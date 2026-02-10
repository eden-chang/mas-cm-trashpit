"""아이템 서비스 (Supabase 버전 - 캐시 적용)

아이템 데이터는 자주 변경되지 않으므로 캐싱 적용.
"""

import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.supabase_client import get_supabase, TABLE_ITEMS
from shared.config import CACHE_TTL
from bot.logger import get_logger

logger = get_logger()

# 캐시에 저장되는 아이템 정보 형태 (price/value는 DB에서 문자열·숫자 혼용)
class ItemInfo(TypedDict, total=False):
    name: str
    price: Any
    desc: str
    use_msg: str
    stat: str
    value: Any
    volume: int


# 캐시 저장소
_items_cache: Dict[str, Dict[str, Any]] = {}
_cache_time: float = 0


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


def _is_cache_valid() -> bool:
    """캐시 유효성 확인 (TTL 기반)"""
    return _cache_time > 0 and (time.time() - _cache_time) < CACHE_TTL


def _load_items_cache() -> None:
    """Supabase에서 전체 아이템 로드"""
    global _items_cache, _cache_time
    try:
        supabase = get_supabase()
        response = supabase.table(TABLE_ITEMS).select("*").execute()

        _items_cache = {}
        for row in response.data:
            name = (row.get("name") or "").strip()
            if not name:
                continue

            raw_size = row.get("size")
            try:
                volume = int(raw_size) if raw_size is not None else 0
            except (ValueError, TypeError):
                volume = 0

            _items_cache[name] = {
                'name': name,
                'price': row.get("price", ""),
                'desc': row.get("description", ""),
                'use_msg': row.get("use_script", ""),
                'stat': row.get("change_stats", ""),
                'value': row.get("change_value", ""),
                'volume': max(0, volume),
            }

        _cache_time = time.time()
        logger.info("아이템 캐시 로드 완료: %d개 아이템", len(_items_cache))
    except Exception as e:
        logger.error("아이템 캐시 로드 실패: %s", e)
        raise


def get_item_info(item_name: str) -> Optional[ItemInfo]:
    """아이템 정보 조회 (캐시 사용). 입력은 strip·공백 정규화 후 정확/정규화 매칭."""
    if not _is_cache_valid():
        _load_items_cache()

    if not item_name or not isinstance(item_name, str):
        return None
    key = item_name.strip()
    if key in _items_cache:
        return _items_cache[key]
    normalized = _normalize_item_name(item_name)
    if not normalized:
        return None
    for name, info in _items_cache.items():
        if _normalize_item_name(name) == normalized:
            return info
    return None


def refresh_cache() -> None:
    """캐시 강제 새로고침"""
    global _cache_time
    _cache_time = 0
    _load_items_cache()


def list_shop_items() -> List[Dict[str, Any]]:
    """구매 가능한 아이템 목록 (price가 숫자이고 양수인 것만, 비매품 제외). 이름 순 정렬."""
    if not _is_cache_valid():
        _load_items_cache()

    result: List[Dict[str, Any]] = []
    for name, info in _items_cache.items():
        p = parse_sellable_price(info.get("price"))
        if p is None:
            continue
        result.append({**info, "price": p})
    return sorted(result, key=lambda x: x.get("name", ""))
