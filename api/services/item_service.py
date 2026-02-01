"""아이템 정보 서비스 (문서 1.2 기반, shared.item_master + 캐시)"""

import logging
from typing import Optional

from shared.models import ItemInfo
from shared.item_master import (
    get_item_info as _get_item_info,
    get_all_item_infos,
    is_usable as is_usable_item,
    is_misc_item as is_misc_item_info,
)

logger = logging.getLogger(__name__)

_items_cache: dict[str, ItemInfo] = {}
_cache_loaded = False


def _load_items_cache() -> None:
    """아이템 캐시 로드 (shared.get_all_item_infos 1회 호출). 실패 시 예외 전파."""
    global _items_cache, _cache_loaded
    try:
        infos = get_all_item_infos()
        _items_cache = {info.name: info for info in infos}
        _cache_loaded = True
    except Exception as e:
        logger.exception("아이템 캐시 로드 실패: %s", e)
        raise


def get_item_info(name: str) -> Optional[ItemInfo]:
    """아이템 정보 조회"""
    global _cache_loaded
    if not _cache_loaded:
        _load_items_cache()
    return _items_cache.get(name)


def get_all_items() -> list[ItemInfo]:
    """전체 아이템 목록 조회"""
    global _cache_loaded
    if not _cache_loaded:
        _load_items_cache()
    return list(_items_cache.values())


def is_usable(item_info: ItemInfo) -> bool:
    """아이템 사용 가능 여부 (문서 1.2)"""
    return is_usable_item(item_info)


def is_misc_item(item_info: ItemInfo) -> bool:
    """부피 0 아이템(여유공간) 여부"""
    return is_misc_item_info(item_info)


def refresh_cache() -> None:
    """캐시 새로고침"""
    global _cache_loaded
    _cache_loaded = False
    _load_items_cache()
