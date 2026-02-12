"""아이템 정보 서비스 (문서 1.2 기반, shared.item_master 직접 조회)"""

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


def get_item_info(name: str) -> Optional[ItemInfo]:
    """아이템 정보 조회 (매번 DB에서 직접 조회)"""
    return _get_item_info(name)


def get_all_items() -> list[ItemInfo]:
    """전체 아이템 목록 조회 (매번 DB에서 직접 조회)"""
    return get_all_item_infos()


def is_usable(item_info: ItemInfo) -> bool:
    """아이템 사용 가능 여부 (문서 1.2)"""
    return is_usable_item(item_info)


def is_misc_item(item_info: ItemInfo) -> bool:
    """부피 0 아이템(여유공간) 여부"""
    return is_misc_item_info(item_info)
