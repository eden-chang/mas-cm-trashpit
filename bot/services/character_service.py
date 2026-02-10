"""캐릭터 서비스 (Supabase 버전)"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.supabase_client import get_supabase, TABLE_CHARACTERS
from shared.parser import parse_json_inventory
from bot.logger import get_logger

logger = get_logger()


class CharacterServiceError(Exception):
    """네트워크/DB 장애 등 시스템 오류. '캐릭터 미존재'(None 반환)와 구분된다."""


def _row_to_dict(row: dict) -> Dict[str, Any]:
    """Supabase 행을 기존 인터페이스 형태로 변환"""
    return {
        'name': row.get('name', ''),
        'mastodon_id': row.get('id', ''),
        'faction': row.get('side', ''),
        'health': row.get('con', 0) or 0,
        'strength': row.get('str', 1) or 1,
        'luck': row.get('luck', 0) or 0,
        'hp': row.get('hp', 0) or 0,
        'points': row.get('points', 0) or 0,
        'bag': row.get('bag') or {},
        'misc': row.get('misc') or {},
        'around': row.get('around') or {},
        'row': 0,  # Supabase에서는 사용하지 않음
        'raw': row,  # 원본 데이터 보관
    }


def get_character(name: str) -> Optional[Dict[str, Any]]:
    """이름으로 캐릭터 조회.

    Returns:
        캐릭터 dict 또는 미존재 시 None.
    Raises:
        CharacterServiceError: 네트워크/DB 장애.
    """
    if not name:
        return None

    try:
        supabase = get_supabase()
        response = (
            supabase.table(TABLE_CHARACTERS)
            .select("*")
            .eq("name", name)
            .limit(1)
            .execute()
        )
        if response.data:
            return _row_to_dict(response.data[0])
        return None
    except Exception as e:
        logger.error("Character Lookup Error: %s", e)
        raise CharacterServiceError(f"캐릭터 조회 중 시스템 오류: {e}") from e


def get_character_by_name(name: str) -> Optional[Dict[str, Any]]:
    """이름으로 캐릭터 조회 (get_character 별칭)."""
    return get_character(name)


def get_character_by_mastodon_id(mastodon_id: str) -> Optional[Dict[str, Any]]:
    """마스토돈 ID로 캐릭터 조회.

    Returns:
        캐릭터 dict 또는 미존재 시 None.
    Raises:
        CharacterServiceError: 네트워크/DB 장애.
    """
    if not mastodon_id:
        return None

    try:
        supabase = get_supabase()
        response = (
            supabase.table(TABLE_CHARACTERS)
            .select("*")
            .eq("id", mastodon_id)
            .limit(1)
            .execute()
        )
        if response.data:
            return _row_to_dict(response.data[0])
        return None
    except Exception as e:
        logger.error("Character Lookup Error (ID): %s", e)
        raise CharacterServiceError(f"캐릭터 조회 중 시스템 오류: {e}") from e
