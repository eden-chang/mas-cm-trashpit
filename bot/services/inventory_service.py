"""인벤토리 관리 서비스"""

import os
import sys
from typing import Optional

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from shared.google_sheets import get_worksheet
from shared.models import Character, Item
from shared.constants import ManagementColumns, WORKSHEET_MANAGEMENT, get_bag_capacity
from shared.parser import serialize_inventory
from bot.logger import get_logger
from bot.services.item_service import get_item_info
from bot.services.character_service import get_character_by_name

logger = get_logger()


def find_item_location(char_name: str, item_name: str) -> Optional[str]:
    """아이템 위치 찾기 (주변 -> 가방 -> 여유공간 순)"""
    char = get_character_by_name(char_name)
    if not char:
        return None

    # 주변 확인
    for item in char.nearby_items:
        if item.name == item_name:
            return "nearby"

    # 가방 확인
    for item in char.bag_items:
        if item.name == item_name:
            return "bag"

    # 여유공간 확인
    for item in char.misc_items:
        if item.name == item_name:
            return "misc"

    return None


def get_available_space(char_name: str) -> int:
    """남은 가방 공간 계산 (아이템 마스터 부피 기준)"""
    char = get_character_by_name(char_name)
    if not char:
        return 0

    capacity = get_bag_capacity(char.strength)
    used = 0
    for item in char.bag_items:
        info = get_item_info(item.name)
        volume = info.volume if info else 0
        used += volume * item.quantity
    return max(0, capacity - used)


def can_add_item(char_name: str, item_name: str, quantity: int = 1) -> bool:
    """아이템 추가 가능 여부 (문서 1.3)

    부피 0 아이템은 여유공간으로 가므로 항상 True.
    """
    item_info = get_item_info(item_name)
    if not item_info:
        return False

    if item_info.volume == 0:
        return True

    needed = item_info.volume * quantity
    available = get_available_space(char_name)
    return needed <= available


def add_item_to_character(char_name: str, item_name: str, quantity: int = 1) -> bool:
    """아이템 추가 - 자동 분류 (문서 1.3)

    부피 0: 여유공간(misc)에 추가
    부피 1+: 주변(nearby)에 추가 (가방은 웹에서 정리)
    """
    item_info = get_item_info(item_name)
    if not item_info:
        return False

    if item_info.volume == 0:
        return add_to_misc(char_name, item_name, quantity)
    return add_to_nearby(char_name, item_name, quantity)


def get_item_count(char_name: str, item_name: str) -> int:
    """캐릭터가 소지한 아이템 총 수량"""
    char = get_character_by_name(char_name)
    if not char:
        return 0

    total = 0
    for item_list in [char.nearby_items, char.bag_items, char.misc_items]:
        for item in item_list:
            if item.name == item_name:
                total += item.quantity

    return total


def update_inventory_column(
    char_name: str, column: str, item_name: str, delta: int
) -> bool:
    """인벤토리 컬럼 업데이트"""
    try:
        char = get_character_by_name(char_name)
        if not char:
            logger.error(f"캐릭터를 찾을 수 없음: {char_name}")
            return False

        # 컬럼 매핑
        column_map = {
            "nearby": (ManagementColumns.NEARBY, char.nearby_items),
            "bag": (ManagementColumns.BAG, char.bag_items),
            "misc": (ManagementColumns.MISC, char.misc_items),
        }

        if column not in column_map:
            logger.error(f"잘못된 컬럼: {column}")
            return False

        col_idx, items = column_map[column]

        # 아이템 업데이트
        updated = False
        for item in items:
            if item.name == item_name:
                item.quantity += delta
                updated = True
                break

        if not updated and delta > 0:
            items.append(Item(name=item_name, quantity=delta))

        # 수량 0 이하 제거
        items = [item for item in items if item.quantity > 0]

        # 시트 업데이트
        ws = get_worksheet(WORKSHEET_MANAGEMENT)
        new_value = serialize_inventory(items)
        ws.update_cell(char.row_index, col_idx + 1, new_value)

        logger.sheet_access("업데이트", f"{char_name}/{column}/{item_name}", True)
        return True

    except Exception as e:
        logger.error(f"인벤토리 업데이트 오류: {e}")
        return False


def add_to_nearby(char_name: str, item_name: str, quantity: int = 1) -> bool:
    """주변에 아이템 추가"""
    return update_inventory_column(char_name, "nearby", item_name, quantity)


def add_to_bag(char_name: str, item_name: str, quantity: int = 1) -> bool:
    """가방에 아이템 추가"""
    return update_inventory_column(char_name, "bag", item_name, quantity)


def add_to_misc(char_name: str, item_name: str, quantity: int = 1) -> bool:
    """여유공간에 아이템 추가"""
    return update_inventory_column(char_name, "misc", item_name, quantity)


def remove_from_nearby(char_name: str, item_name: str, quantity: int = 1) -> bool:
    """주변에서 아이템 제거"""
    return update_inventory_column(char_name, "nearby", item_name, -quantity)


def remove_from_bag(char_name: str, item_name: str, quantity: int = 1) -> bool:
    """가방에서 아이템 제거"""
    return update_inventory_column(char_name, "bag", item_name, -quantity)


def remove_from_misc(char_name: str, item_name: str, quantity: int = 1) -> bool:
    """여유공간에서 아이템 제거"""
    return update_inventory_column(char_name, "misc", item_name, -quantity)


def remove_from_location(
    char_name: str, item_name: str, quantity: int, location: str
) -> bool:
    """위치별 아이템 제거 (find_item_location 반환값과 호환)

    Args:
        char_name: 캐릭터 이름
        item_name: 아이템명
        quantity: 제거 수량
        location: 'nearby' | 'bag' | 'misc'

    Returns:
        제거 성공 여부
    """
    removers = {
        "nearby": remove_from_nearby,
        "bag": remove_from_bag,
        "misc": remove_from_misc,
    }
    remover = removers.get(location)
    if not remover:
        logger.error(f"잘못된 위치: {location}")
        return False
    return remover(char_name, item_name, quantity)


def update_stat(char_name: str, stat_column: int, delta: int) -> bool:
    """캐릭터 스탯 업데이트"""
    try:
        char = get_character_by_name(char_name)
        if not char:
            return False

        ws = get_worksheet(WORKSHEET_MANAGEMENT)
        current = int(ws.cell(char.row_index, stat_column + 1).value or 0)
        new_value = current + delta

        ws.update_cell(char.row_index, stat_column + 1, new_value)
        logger.sheet_access("스탯 업데이트", f"{char_name}/{stat_column}/{delta}", True)
        return True

    except Exception as e:
        logger.error(f"스탯 업데이트 오류: {e}")
        return False
