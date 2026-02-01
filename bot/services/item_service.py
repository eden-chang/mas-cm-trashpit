"""아이템 정보 조회 서비스 (문서 1.2 기반, shared.item_master + 캐시)"""

import sys
from typing import Optional

sys.path.insert(0, str(__file__).rsplit("\\", 3)[0])

from shared.models import ItemInfo
from shared.item_master import (
    get_item_info as _get_item_info,
    get_all_item_infos,
    is_usable as _is_usable,
    is_misc_item as _is_misc_item,
)
from bot.logger import get_logger

logger = get_logger()

_item_cache: dict[str, ItemInfo] = {}


def get_item_info(item_name: str) -> Optional[ItemInfo]:
    """아이템 정보 조회 (캐시 우선, 없으면 상점 시트)"""
    if item_name in _item_cache:
        return _item_cache[item_name]
    try:
        info = _get_item_info(item_name)
        if info:
            _item_cache[item_name] = info
        return info
    except Exception as e:
        logger.error(f"아이템 조회 오류: {e}")
        return None


def is_usable(item_info: ItemInfo) -> bool:
    """아이템 사용 가능 여부 (문서 1.2: 사용문구 있음 + 스탯 != 사용 불가)"""
    return _is_usable(item_info)


def is_misc_item(item_info: ItemInfo) -> bool:
    """부피 0 아이템(여유공간) 여부"""
    return _is_misc_item(item_info)


def clear_item_cache() -> None:
    """아이템 캐시 초기화"""
    global _item_cache
    _item_cache = {}


def refresh_item_cache() -> None:
    """아이템 캐시 전체 새로고침 (shared.get_all_item_infos 1회 호출)"""
    global _item_cache
    _item_cache = {}
    try:
        infos = get_all_item_infos()
        _item_cache = {info.name: info for info in infos}
        logger.info("아이템 캐시 갱신 완료: %d개", len(_item_cache))
    except Exception as e:
        logger.exception("아이템 캐시 갱신 오류: %s", e)
