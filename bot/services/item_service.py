"""아이템 서비스 (Supabase 버전 - 매 조회 시 DB 직접 조회)"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.supabase_client import get_supabase, TABLE_ITEMS
from bot.logger import get_logger

logger = get_logger()

# 아이템 정보 형태 (price/value는 DB에서 문자열·숫자 혼용)
class ItemInfo(TypedDict, total=False):
    name: str
    price: Any
    desc: str
    use_msg: str
    stat: str
    value: Any
    volume: int


def _normalize_item_name(name: str) -> str:
    """앞뒤 공백 제거 후 연속 공백을 하나로 합침."""
    if not name or not isinstance(name, str):
        return ""
    return re.sub(r"\s+", " ", name.strip())


def parse_sellable_price(price: Any) -> Optional[int]:
    """가격이 매매 가능한 양수 정수면 반환, 그 외 None.
    None, '비매품', 비숫자, 0 이하 → None.
    """
    if price is None:
        return None
    if isinstance(price, str):
        s = price.strip()
        if s == "비매품" or not s:
            return None
        try:
            p = int(float(s))
        except (ValueError, TypeError):
            return None
    else:
        try:
            p = int(price)
        except (ValueError, TypeError):
            return None
    return p if p > 0 else None


def format_price_display(price: Any) -> str:
    """가격을 설명/상점 표시용 문자열로 반환. '비매품' 또는 'N포인트'."""
    if price is None:
        return "비매품"
    if isinstance(price, str):
        s = price.strip()
        if s == "비매품" or not s:
            return "비매품"
        try:
            p = int(float(s))
            return f"{p:,}포인트" if p > 0 else "비매품"
        except (ValueError, TypeError):
            return "비매품"
    try:
        p = int(price)
        return f"{p:,}포인트" if p > 0 else "비매품"
    except (ValueError, TypeError):
        return "비매품"


def _row_to_item_dict(row: dict) -> Optional[Dict[str, Any]]:
    """Supabase 행을 아이템 딕셔너리로 변환"""
    name = (row.get("name") or "").strip()
    if not name:
        return None

    raw_size = row.get("size")
    try:
        volume = int(raw_size) if raw_size is not None else 0
    except (ValueError, TypeError):
        volume = 0

    return {
        'name': name,
        'price': row.get("price", ""),
        'desc': row.get("description", ""),
        'use_msg': row.get("use_script", ""),
        'stat': row.get("change_stats", ""),
        'value': row.get("change_value", ""),
        'volume': max(0, volume),
    }


def _fetch_all_items() -> Dict[str, Dict[str, Any]]:
    """Supabase에서 전체 아이템 로드 (매번 직접 조회)"""
    try:
        supabase = get_supabase()
        response = supabase.table(TABLE_ITEMS).select("*").execute()

        result: Dict[str, Dict[str, Any]] = {}
        for row in response.data:
            item = _row_to_item_dict(row)
            if item:
                result[item['name']] = item
        return result
    except Exception as e:
        logger.error("아이템 목록 조회 실패: %s", e)
        raise


def get_item_info(item_name: str) -> Optional[ItemInfo]:
    """아이템 정보 조회 (매번 DB에서 직접 조회)"""
    if not item_name or not isinstance(item_name, str):
        return None

    try:
        supabase = get_supabase()
        key = item_name.strip()
        response = (
            supabase.table(TABLE_ITEMS)
            .select("*")
            .eq("name", key)
            .limit(1)
            .execute()
        )
        if response.data:
            return _row_to_item_dict(response.data[0])

        # 정규화 매칭 시도 (전체 조회 필요)
        normalized = _normalize_item_name(item_name)
        if not normalized:
            return None
        all_items = _fetch_all_items()
        for name, info in all_items.items():
            if _normalize_item_name(name) == normalized:
                return info
        return None
    except Exception as e:
        logger.error("아이템 조회 실패 (name=%s): %s", item_name, e)
        return None


def list_shop_items() -> List[Dict[str, Any]]:
    """구매 가능한 아이템 목록 (매번 DB에서 직접 조회)"""
    all_items = _fetch_all_items()

    result: List[Dict[str, Any]] = []
    for name, info in all_items.items():
        p = parse_sellable_price(info.get("price"))
        if p is None:
            continue
        result.append({**info, "price": p})
    return sorted(result, key=lambda x: x.get("name", ""))
