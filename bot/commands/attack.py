"""[공격] 명령어 핸들러 — 진영·근력 기반 데미지 계산"""

from typing import Any, Dict, Literal, Optional

from shared.constants import ErrorMessages
from bot.services.combat_utils import (
    compute_damage,
    normalize_faction,
    parse_strength,
)
from bot.utils.decorators import require_character


def handle_combat_damage(
    status_id: str,
    user: str,
    character: Dict[str, Any],
    args: list,
    action: Literal["attack", "shoot"],
) -> str:
    """공격/발사 공통 핸들러 — 진영·근력 기반 데미지 계산. (character는 require_character로 주입)"""
    user_name = (character.get("name") or "").strip() or user
    faction_raw = (character.get("faction") or "").strip()
    if not faction_raw:
        return ErrorMessages.NO_FACTION.format(user=user, user_name=user_name)

    normalized_faction = normalize_faction(faction_raw)
    if normalized_faction is None:
        return ErrorMessages.UNKNOWN_FACTION.format(
            user=user, user_name=user_name, faction=faction_raw
        )

    strength = parse_strength(character)
    return compute_damage(normalized_faction, strength, user_name, action)


@require_character
def handle(status_id: str, user: str, character: Dict[str, Any], args: list) -> str:
    """[공격] — 진영별 데미지 (웨가: 근력×10+랜덤40~80, 스카이: 60+랜덤20~60)."""
    return handle_combat_damage(status_id, user, character, args, "attack")
