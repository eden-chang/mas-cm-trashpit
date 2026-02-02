"""[방어] 명령어 핸들러 — 체력 기반 방어력 계산"""

import random
from typing import Any, Dict, Optional

from shared.constants import ErrorMessages
from bot.services.combat_utils import parse_stat_optional
from bot.utils.decorators import require_character


@require_character
def handle(status_id: str, user: str, character: Dict[str, Any], args: list) -> Optional[str]:
    """[방어] — 체력×10 + 랜덤값(1~40) = 총 방어."""
    user_name = (character.get("name") or "").strip() or user
    health, error = parse_stat_optional(character, "health")
    if error == "missing":
        return ErrorMessages.NO_HEALTH.format(user=user, user_name=user_name)
    if error == "invalid":
        health_raw = character.get("health")
        return ErrorMessages.INVALID_HEALTH.format(
            user=user, user_name=user_name, health_raw=health_raw
        )

    assert health is not None
    dice_roll = random.randint(1, 40)
    total_defense = health * 10 + dice_roll

    message = (
        f"{user_name}의 방어\n"
        f"체력[{health}] × 10 + 랜덤값[{dice_roll}] = {total_defense} 방어"
    )
    return message
