"""인벤토리 관리 서비스"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.google_sheets import get_worksheet
from shared.constants import ManagementColumns, SHEET_NAMES, get_bag_capacity
from shared.inventory_parser import parse_inventory_str, to_inventory_str
from bot.services.character_service import get_character
from bot.services.item_service import get_item_info
from bot.logger import get_logger

logger = get_logger()

# ============================================================
# Core Logic
# ============================================================

def get_inventory_dict(char_name: str, column_idx: int) -> dict[str, int]:
    """특정 컬럼의 인벤토리를 파싱하여 반환"""
    char = get_character(char_name)
    if not char:
        return {}
    
    # 0-based index to sheet values
    # char['raw'] contains row values
    try:
        raw_str = char['raw'][column_idx]
        return parse_inventory_str(raw_str)
    except IndexError:
        return {}

def update_inventory_cell(char_name: str, column_idx: int, items: dict[str, int]) -> bool:
    """인벤토리 셀 업데이트"""
    char = get_character(char_name)
    if not char:
        return False
    
    new_str = to_inventory_str(items)
    
    try:
        ws = get_worksheet(SHEET_NAMES['CHARACTERS'])
        # gspread uses 1-based index
        ws.update_cell(char['row'], column_idx + 1, new_str)
        return True
    except Exception as e:
        logger.error("Inventory Update Error: %s", e)
        return False

# ============================================================
# High Level Operations
# ============================================================

def add_item(char_name: str, item_name: str, quantity: int, location: str = 'nearby') -> bool:
    """아이템 추가"""
    col_map = {
        'bag': ManagementColumns.BAG,
        'misc': ManagementColumns.MISC,
        'nearby': ManagementColumns.NEARBY
    }
    
    if location not in col_map:
        return False
        
    col = col_map[location]
    items = get_inventory_dict(char_name, col)
    
    items[item_name] = items.get(item_name, 0) + quantity
    
    return update_inventory_cell(char_name, col, items)

def remove_item(char_name: str, item_name: str, quantity: int, location: str) -> bool:
    """아이템 제거"""
    col_map = {
        'bag': ManagementColumns.BAG,
        'misc': ManagementColumns.MISC,
        'nearby': ManagementColumns.NEARBY
    }
    
    if location not in col_map:
        return False
        
    col = col_map[location]
    items = get_inventory_dict(char_name, col)
    
    if item_name not in items:
        return False
        
    items[item_name] -= quantity
    if items[item_name] <= 0:
        del items[item_name]
        
    return update_inventory_cell(char_name, col, items)

def find_item_location(char_name: str, item_name: str) -> Optional[str]:
    """아이템 위치 찾기 (주변 -> 가방 -> 여유공간 순)"""
    # 주변
    if item_name in get_inventory_dict(char_name, ManagementColumns.NEARBY):
        return 'nearby'
    # 가방
    if item_name in get_inventory_dict(char_name, ManagementColumns.BAG):
        return 'bag'
    # 여유공간
    if item_name in get_inventory_dict(char_name, ManagementColumns.MISC):
        return 'misc'
        
    return None

def get_item_count(char_name: str, item_name: str) -> int:
    """전체 소지 수량 확인"""
    total = 0
    for col in [ManagementColumns.NEARBY, ManagementColumns.BAG, ManagementColumns.MISC]:
        items = get_inventory_dict(char_name, col)
        total += items.get(item_name, 0)
    return total


# 양도 시 수집 우선순위: 주변 -> 여유공간 -> 가방
TRANSFER_PRIORITY = ("nearby", "misc", "bag")
_COL_BY_LOC = {
    "nearby": ManagementColumns.NEARBY,
    "misc": ManagementColumns.MISC,
    "bag": ManagementColumns.BAG,
}


def get_item_counts_by_location(char_name: str, item_name: str) -> dict[str, int]:
    """아이템의 위치별 수량 반환 (주변, 여유공간, 가방 순)."""
    return {
        loc: get_inventory_dict(char_name, _COL_BY_LOC[loc]).get(item_name, 0)
        for loc in TRANSFER_PRIORITY
    }


def remove_item_by_priority(char_name: str, item_name: str, quantity: int) -> int:
    """우선순위(주변 -> 여유공간 -> 가방)대로 아이템을 차감하고, 실제 차감된 수량을 반환."""
    if quantity <= 0:
        return 0
    by_loc = get_item_counts_by_location(char_name, item_name)
    remaining = quantity
    removed_total = 0
    for loc in TRANSFER_PRIORITY:
        if remaining <= 0:
            break
        take = min(remaining, by_loc[loc])
        if take > 0 and remove_item(char_name, item_name, take, loc):
            removed_total += take
            remaining -= take
        elif take > 0:
            break
    return removed_total


def add_to_nearby(char_name: str, item_name: str, quantity: int) -> bool:
    """주변에 아이템 추가 (add_item wrapper)."""
    return add_item(char_name, item_name, quantity, "nearby")


def add_to_misc(char_name: str, item_name: str, quantity: int) -> bool:
    """여유공간에 아이템 추가 (add_item wrapper)."""
    return add_item(char_name, item_name, quantity, "misc")


def remove_from_location(
    char_name: str, item_name: str, quantity: int, location: str
) -> bool:
    """지정 위치에서 아이템 제거 (remove_item wrapper)."""
    return remove_item(char_name, item_name, quantity, location)


def get_available_space(char_name: str) -> int:
    """가방 남은 공간 (용량 - 사용량). 문서 1.3 근력별 용량 기준."""
    char = get_character(char_name)
    if not char or not char.get("raw"):
        return 0
    raw = char["raw"]
    try:
        strength_val = raw[ManagementColumns.STRENGTH] if len(raw) > ManagementColumns.STRENGTH else 1
        strength = int(strength_val) if strength_val not in (None, "") else 1
    except (TypeError, ValueError):
        strength = 1
    capacity = get_bag_capacity(strength)
    bag_items = get_inventory_dict(char_name, ManagementColumns.BAG)
    used = 0
    for item_name, qty in bag_items.items():
        info = get_item_info(item_name)
        if info:
            used += info.get("volume", 0) * qty
    return max(0, capacity - used)


def update_stat(char_name: str, stat_col: int, delta: int) -> bool:
    """관리 시트 스탯 컬럼 값에 delta를 더해 갱신 (1-based 컬럼)."""
    char = get_character(char_name)
    if not char:
        return False
    row = char["row"]
    raw = char.get("raw") or []
    try:
        current = int(raw[stat_col]) if len(raw) > stat_col and raw[stat_col] not in (None, "") else 0
    except (TypeError, ValueError):
        current = 0
    new_value = current + delta
    try:
        ws = get_worksheet(SHEET_NAMES["CHARACTERS"])
        ws.update_cell(row, stat_col + 1, new_value)
        return True
    except Exception as e:
        logger.error("update_stat Error: %s", e)
        return False
