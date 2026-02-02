"""Supabase 캐릭터 서비스 (구 sheet_service)

구글 시트 → Supabase PostgreSQL 마이그레이션 완료.
기존 인터페이스 유지하여 호환성 보장.
"""

import logging
from typing import Optional

from shared.supabase_client import get_supabase, TABLE_CHARACTERS
from shared.models import Character
from shared.parser import parse_json_inventory, serialize_json_inventory, parse_json_layout, serialize_json_layout
from shared.cache import (
    cached,
    invalidate_character_cache,
    CACHE_TTL_CHARACTERS,
)

logger = logging.getLogger(__name__)


def _row_to_character(row: dict) -> Character:
    """Supabase 행을 Character 객체로 변환"""
    return Character(
        name=row.get("name", ""),
        mastodon_id=row.get("id", ""),
        faction=row.get("side", ""),
        health=row.get("con", 0) or 0,
        strength=row.get("str", 1) or 1,
        luck=row.get("luck", 0) or 0,
        hp=row.get("hp", 0) or 0,
        points=row.get("points", 0) or 0,
        bag_items=parse_json_inventory(row.get("bag")),
        misc_items=parse_json_inventory(row.get("misc")),
        nearby_items=parse_json_inventory(row.get("around")),
        bag_layout=parse_json_layout(row.get("arrange")),
        row_index=0,  # Supabase에서는 사용하지 않음
        updated_at=row.get("updated_at"),  # 마지막 수정 시각
    )


@cached(ttl=CACHE_TTL_CHARACTERS)
def get_all_characters() -> list[Character]:
    """전체 캐릭터 목록 조회 (캐시됨, 이름순 정렬)"""
    try:
        supabase = get_supabase()
        response = supabase.table(TABLE_CHARACTERS).select("*").order("name").execute()
        return [_row_to_character(row) for row in response.data]
    except Exception as e:
        logger.exception("캐릭터 목록 조회 실패: %s", e)
        return []


@cached(ttl=CACHE_TTL_CHARACTERS)
def get_character_by_name(name: str) -> Optional[Character]:
    """이름으로 캐릭터 조회 (캐시됨, PK 조회)"""
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
            return _row_to_character(response.data[0])
        return None
    except Exception as e:
        logger.exception("캐릭터 조회 실패 (name=%s): %s", name, e)
        return None


@cached(ttl=CACHE_TTL_CHARACTERS)
def get_character_by_mastodon_id(mastodon_id: str) -> Optional[Character]:
    """마스토돈 ID로 캐릭터 조회 (캐시됨)"""
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
            return _row_to_character(response.data[0])
        return None
    except Exception as e:
        logger.exception("캐릭터 조회 실패 (mastodon_id=%s): %s", mastodon_id, e)
        return None


def find_character_row(name: str) -> Optional[int]:
    """호환성 유지용 - Supabase에서는 의미 없음, 항상 0 반환"""
    char = get_character_by_name(name)
    return 0 if char else None


def update_bag_items(name: str, items: list[dict]) -> bool:
    """가방 아이템 업데이트"""
    try:
        supabase = get_supabase()
        bag_data = serialize_json_inventory(items)
        response = (
            supabase.table(TABLE_CHARACTERS)
            .update({"bag": bag_data})
            .eq("name", name)
            .execute()
        )
        if response.data:
            invalidate_character_cache(name)
            return True
        return False
    except Exception as e:
        logger.exception("가방 업데이트 실패 (name=%s): %s", name, e)
        return False


def update_nearby_items(name: str, items: list[dict]) -> bool:
    """주변 아이템 업데이트 (around 컬럼)"""
    try:
        supabase = get_supabase()
        around_data = serialize_json_inventory(items)
        response = (
            supabase.table(TABLE_CHARACTERS)
            .update({"around": around_data})
            .eq("name", name)
            .execute()
        )
        if response.data:
            invalidate_character_cache(name)
            return True
        return False
    except Exception as e:
        logger.exception("주변 업데이트 실패 (name=%s): %s", name, e)
        return False


def update_misc_items(name: str, items: list[dict]) -> bool:
    """여유공간 아이템 업데이트"""
    try:
        supabase = get_supabase()
        misc_data = serialize_json_inventory(items)
        response = (
            supabase.table(TABLE_CHARACTERS)
            .update({"misc": misc_data})
            .eq("name", name)
            .execute()
        )
        if response.data:
            invalidate_character_cache(name)
            return True
        return False
    except Exception as e:
        logger.exception("여유공간 업데이트 실패 (name=%s): %s", name, e)
        return False


def update_bag_and_nearby_items(
    name: str,
    bag_items: list[dict],
    nearby_items: list[dict],
) -> bool:
    """가방·주변 아이템 한 번에 업데이트"""
    try:
        supabase = get_supabase()
        response = (
            supabase.table(TABLE_CHARACTERS)
            .update({
                "bag": serialize_json_inventory(bag_items),
                "around": serialize_json_inventory(nearby_items),
            })
            .eq("name", name)
            .execute()
        )
        if response.data:
            invalidate_character_cache(name)
            return True
        return False
    except Exception as e:
        logger.exception("가방+주변 업데이트 실패 (name=%s): %s", name, e)
        return False


def update_inventory(
    name: str,
    bag_items: list[dict],
    nearby_items: list[dict],
    misc_items: list[dict],
    bag_layout: Optional[list[dict]] = None,
) -> bool:
    """가방·주변·여유공간 아이템 한 번에 업데이트
    
    bag_layout이 제공되면 배치 정보(arrange 컬럼)도 함께 저장합니다.
    """
    try:
        supabase = get_supabase()
        update_data = {
            "bag": serialize_json_inventory(bag_items),
            "misc": serialize_json_inventory(misc_items),
            "around": serialize_json_inventory(nearby_items),
        }
        
        # 배치 정보가 제공되면 함께 저장
        if bag_layout is not None:
            update_data["arrange"] = serialize_json_layout(bag_layout)
        
        response = (
            supabase.table(TABLE_CHARACTERS)
            .update(update_data)
            .eq("name", name)
            .execute()
        )
        if response.data:
            invalidate_character_cache(name)
            return True
        return False
    except Exception as e:
        logger.exception("인벤토리 업데이트 실패 (name=%s): %s", name, e)
        return False
