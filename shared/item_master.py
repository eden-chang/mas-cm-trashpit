"""아이템 마스터 조회 모듈 (Supabase 버전)

items 테이블에서 아이템 정보를 조회하고, 사용 가능·여유공간 여부를 판별합니다.
전체 아이템을 메모리에 캐시하여 DB 호출을 최소화합니다.
"""

import os
import time
import logging
from typing import Optional, Union

from .supabase_client import get_supabase, TABLE_ITEMS
from .models import ItemInfo

logger = logging.getLogger(__name__)

# 아이템 마스터 캐시 TTL (초) — 아이템은 거의 변경되지 않으므로 5분
_ITEM_CACHE_TTL = int(os.getenv("CACHE_TTL_ITEMS", "300"))

# 캐시 저장소
_item_cache: dict[str, ItemInfo] = {}
_cache_loaded_at: float = 0.0


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


def _ensure_cache() -> None:
    """캐시가 없거나 만료되었으면 전체 아이템을 로드"""
    global _item_cache, _cache_loaded_at

    now = time.time()
    if _item_cache and (now - _cache_loaded_at) < _ITEM_CACHE_TTL:
        return

    try:
        supabase = get_supabase()
        response = supabase.table(TABLE_ITEMS).select("*").execute()
        new_cache: dict[str, ItemInfo] = {}
        for row in response.data:
            try:
                info = _row_to_item_info(row)
                new_cache[info.name] = info
            except ValueError as e:
                logger.warning("아이템 행 스킵: %s", e)

        _item_cache = new_cache
        _cache_loaded_at = now
        logger.debug("아이템 마스터 캐시 로드 완료: %d건", len(_item_cache))
    except Exception as e:
        logger.exception("아이템 마스터 캐시 로드 실패: %s", e)
        # 기존 캐시가 있으면 만료되더라도 계속 사용 (stale-while-error)
        if not _item_cache:
            raise


def invalidate_item_cache() -> None:
    """아이템 마스터 캐시 수동 무효화"""
    global _item_cache, _cache_loaded_at
    _item_cache = {}
    _cache_loaded_at = 0.0
    logger.info("아이템 마스터 캐시 무효화")


def get_item_info(item_name: str) -> Optional[ItemInfo]:
    """아이템 정보 조회 (캐시에서 조회, 없으면 전체 로드)"""
    if not item_name or not item_name.strip():
        return None

    _ensure_cache()
    return _item_cache.get(item_name.strip())


def get_all_item_infos() -> list[ItemInfo]:
    """전체 아이템 목록 조회 (캐시에서 반환)"""
    _ensure_cache()
    return list(_item_cache.values())


def is_usable(item_info: ItemInfo) -> bool:
    """아이템 사용 가능 여부 (사용문구 있음 + 스탯이 '사용 불가' 아님)"""
    msg = (item_info.use_message or "").strip()
    stat = (item_info.stat or "").strip()
    return bool(msg and msg != "-") and stat != "사용 불가"


def is_misc_item(item_info: ItemInfo) -> bool:
    """부피 0 아이템(여유공간) 여부"""
    return (item_info.volume or 0) == 0
