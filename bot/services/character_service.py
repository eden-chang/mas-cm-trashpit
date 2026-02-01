"""캐릭터 서비스"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.google_sheets import get_worksheet
from shared.constants import SHEET_NAMES, ManagementColumns
from bot.logger import get_logger

logger = get_logger()


def get_character(name: str) -> Optional[Dict[str, Any]]:
    """이름으로 캐릭터 조회"""
    try:
        ws = get_worksheet(SHEET_NAMES['CHARACTERS'])
        cell = ws.find(name)
        if not cell:
            return None
            
        row_values = ws.row_values(cell.row)
        
        return {
            'name': name,
            'row': cell.row,
            'raw': row_values,
            'mastodon_id': row_values[ManagementColumns.MASTODON_ID] if len(row_values) > ManagementColumns.MASTODON_ID else None
        }
    except Exception as e:
        logger.error("Character Lookup Error: %s", e)
        return None


def get_character_by_name(name: str) -> Optional[Dict[str, Any]]:
    """이름으로 캐릭터 조회 (get_character 별칭)."""
    return get_character(name)


def get_character_by_mastodon_id(mastodon_id: str) -> Optional[Dict[str, Any]]:
    """마스토돈 ID로 캐릭터 조회"""
    try:
        ws = get_worksheet(SHEET_NAMES['CHARACTERS'])
        cell = ws.find(mastodon_id)
        if not cell:
            return None
            
        row_values = ws.row_values(cell.row)
        
        return {
            'name': row_values[ManagementColumns.NAME],
            'row': cell.row,
            'raw': row_values,
            'mastodon_id': mastodon_id
        }
    except Exception as e:
        logger.error("Character Lookup Error (ID): %s", e)
        return None
