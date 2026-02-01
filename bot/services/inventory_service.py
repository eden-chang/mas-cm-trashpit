"""인벤토리 관리 서비스"""

import sys
import os
from typing import Optional

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from shared.google_sheets import get_worksheet
from shared.constants import ManagementColumns, SHEET_NAMES
from shared.inventory_parser import parse_inventory_str, to_inventory_str
from bot.services.character_service import get_character
from bot.services.item_service import get_item_info

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
        print(f"❌ Inventory Update Error: {e}")
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
