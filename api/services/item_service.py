"""아이템 정보 서비스"""

from typing import Optional

from shared.google_sheets import get_worksheet
from shared.constants import WORKSHEET_SHOP
from shared.models import ItemInfo

# 캐시
_items_cache: dict[str, ItemInfo] = {}
_cache_loaded = False


def _load_items_cache():
    """아이템 캐시 로드"""
    global _items_cache, _cache_loaded

    ws = get_worksheet(WORKSHEET_SHOP)
    records = ws.get_all_records()

    _items_cache = {}
    for record in records:
        name = record.get("아이템명", "")
        if name:
            _items_cache[name] = ItemInfo(
                name=name,
                price=int(record.get("가격", 0) or 0),
                description=str(record.get("설명", "")),
                use_message=str(record.get("사용문구", "")),
                stat=str(record.get("스탯", "")),
                value=int(record.get("수치", 0) or 0),
                volume=int(record.get("부피", 0) or 0),
            )

    _cache_loaded = True


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


def refresh_cache():
    """캐시 새로고침"""
    global _cache_loaded
    _cache_loaded = False
    _load_items_cache()
