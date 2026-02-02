"""아이템 마스터 조회 모듈 (Supabase 버전)

items 테이블에서 아이템 정보를 조회하고, 사용 가능·여유공간 여부를 판별합니다.
"""

import logging
from typing import Optional, Union

from .supabase_client import get_supabase, TABLE_ITEMS
from .models import ItemInfo

logger = logging.getLogger(__name__)


def _row_to_item_info(row: dict) -> ItemInfo:
    """Supabase 행을 ItemInfo 객체로 변환"""
    name = row.get("name", "").strip()
    if not name:
        raise ValueError("아이템명이 비어 있습니다.")

    # 가격 파싱 ("비매품" 또는 숫자)
    raw_price = row.get("price", "0")
    if raw_price == "비매품":
        price: Union[int, str] = "비매품"
    else:
        try:
            price = int(raw_price) if raw_price else 0
        except (ValueError, TypeError):
            price = 0

    # 부피 파싱 (0 이상)
    raw_size = row.get("size")
    try:
        volume = max(0, int(raw_size) if raw_size is not None else 0)
    except (ValueError, TypeError):
        volume = 0

    return ItemInfo(
        name=name,
        price=price,
        description=str(row.get("description", "") or "").strip(),
        use_message=str(row.get("use_script", "") or "").strip(),
        stat=str(row.get("change_stats", "") or "").strip(),
        value=str(row.get("change_value", "") or "").strip(),
        volume=volume,
    )


def get_item_info(item_name: str) -> Optional[ItemInfo]:
    """아이템 정보 조회 (PK 조회)"""
    if not item_name or not item_name.strip():
        return None

    try:
        supabase = get_supabase()
        response = (
            supabase.table(TABLE_ITEMS)
            .select("*")
            .eq("name", item_name.strip())
            .limit(1)
            .execute()
        )
        if response.data:
            return _row_to_item_info(response.data[0])
        return None
    except Exception as e:
        logger.exception("아이템 조회 실패 (name=%s): %s", item_name, e)
        return None


def get_all_item_infos() -> list[ItemInfo]:
    """전체 아이템 목록 조회"""
    try:
        supabase = get_supabase()
        response = supabase.table(TABLE_ITEMS).select("*").execute()
        result: list[ItemInfo] = []
        for row in response.data:
            try:
                result.append(_row_to_item_info(row))
            except ValueError as e:
                logger.warning("아이템 행 스킵: %s", e)
        return result
    except Exception as e:
        logger.exception("아이템 목록 조회 실패: %s", e)
        return []


def is_usable(item_info: ItemInfo) -> bool:
    """아이템 사용 가능 여부 (사용문구 있음 + 스탯이 '사용 불가' 아님)"""
    msg = (item_info.use_message or "").strip()
    stat = (item_info.stat or "").strip()
    return bool(msg and msg != "-") and stat != "사용 불가"


def is_misc_item(item_info: ItemInfo) -> bool:
    """부피 0 아이템(여유공간) 여부"""
    return (item_info.volume or 0) == 0
