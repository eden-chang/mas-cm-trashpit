"""아이템 서비스"""

import sys
from typing import Optional, Dict, Any

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from shared.google_sheets import get_worksheet
from shared.constants import SHEET_NAMES, ShopColumns

def get_item_info(item_name: str) -> Optional[Dict[str, Any]]:
    """아이템 정보 조회"""
    try:
        ws = get_worksheet(SHEET_NAMES['SHOP'])
        cell = ws.find(item_name)
        if not cell:
            return None
            
        row_values = ws.row_values(cell.row)
        
        # 안전한 인덱스 접근
        def safe_get(idx, default=''):
            return row_values[idx] if len(row_values) > idx else default

        return {
            'name': safe_get(ShopColumns.NAME),
            'price': safe_get(ShopColumns.PRICE),
            'desc': safe_get(ShopColumns.DESC),
            'use_msg': safe_get(ShopColumns.USE_MSG),
            'stat': safe_get(ShopColumns.STAT),
            'value': safe_get(ShopColumns.VALUE),
            'volume': int(safe_get(ShopColumns.VOLUME, 0))
        }
    except Exception as e:
        print(f"❌ Item Lookup Error: {e}")
        return None
