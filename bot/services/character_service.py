"""캐릭터 조회 및 관리 서비스"""

import os
import sys
from typing import Optional

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from shared.google_sheets import get_worksheet
from shared.models import Character
from shared.constants import WORKSHEET_MANAGEMENT, ManagementColumns
from shared.parser import parse_inventory
from bot.logger import get_logger

logger = get_logger()


def get_character_by_mastodon_id(mastodon_id: str) -> Optional[Character]:
    """마스토돈 ID로 캐릭터 조회"""
    try:
        ws = get_worksheet(WORKSHEET_MANAGEMENT)
        all_values = ws.get_all_values()

        # 첫 2행은 헤더이므로 스킵
        for row_idx, row in enumerate(all_values[2:], start=3):
            if len(row) > ManagementColumns.MASTODON_ID:
                if row[ManagementColumns.MASTODON_ID].strip() == mastodon_id:
                    return _parse_character_row(row, row_idx)

        return None

    except Exception as e:
        logger.error(f"캐릭터 조회 오류: {e}")
        return None


def get_character_by_name(name: str) -> Optional[Character]:
    """캐릭터 이름으로 조회"""
    try:
        ws = get_worksheet(WORKSHEET_MANAGEMENT)
        all_values = ws.get_all_values()

        for row_idx, row in enumerate(all_values[2:], start=3):
            if len(row) > ManagementColumns.NAME:
                if row[ManagementColumns.NAME].strip() == name:
                    return _parse_character_row(row, row_idx)

        return None

    except Exception as e:
        logger.error(f"캐릭터 조회 오류: {e}")
        return None


def _parse_character_row(row: list, row_idx: int) -> Character:
    """시트 행을 Character 객체로 변환"""

    def safe_int(value: str, default: int = 0) -> int:
        try:
            return int(value) if value else default
        except ValueError:
            return default

    def safe_str(idx: int) -> str:
        return row[idx].strip() if len(row) > idx else ""

    return Character(
        name=safe_str(ManagementColumns.NAME),
        mastodon_id=safe_str(ManagementColumns.MASTODON_ID),
        faction=safe_str(ManagementColumns.FACTION),
        health=safe_int(safe_str(ManagementColumns.HEALTH)),
        strength=safe_int(safe_str(ManagementColumns.STRENGTH), default=1),
        luck=safe_int(safe_str(ManagementColumns.LUCK)),
        bag_items=parse_inventory(safe_str(ManagementColumns.BAG)),
        misc_items=parse_inventory(safe_str(ManagementColumns.MISC)),
        nearby_items=parse_inventory(safe_str(ManagementColumns.NEARBY)),
        row_index=row_idx,
    )


def find_character_row(char_name: str) -> Optional[int]:
    """캐릭터 이름으로 시트 행 번호 찾기"""
    char = get_character_by_name(char_name)
    return char.row_index if char else None
