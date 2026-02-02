"""[회피] 명령어 핸들러 — 행운 기반 회피 성공/실패 판정, dodge 테이블 문구"""

import random
from typing import Any, Dict

from shared.constants import (
    DODGE_MAX_RATE,
    DODGE_MIN_RATE,
    LUCK_RATE_TABLE,
)
from bot.services.combat_utils import parse_stat
from bot.services.dodge_service import pick_dodge_message
from bot.utils.decorators import require_character


def _success_rate(luck: int) -> int:
    if luck <= 0:
        return DODGE_MIN_RATE
    for threshold, rate in LUCK_RATE_TABLE:
        if luck <= threshold:
            return rate
    return DODGE_MAX_RATE


@require_character
def handle(status_id: str, user: str, character: Dict[str, Any], args: list) -> str:
    """[회피] — 행운별 성공 확률로 1d100 판정 후 dodge 테이블 문구 반환."""
    user_name = (character.get("name") or "").strip() or user
    luck = parse_stat(character, "luck", 0)

    success_rate = _success_rate(luck)
    roll = random.randint(1, 100)
    is_success = roll <= success_rate

    dodge_text = pick_dodge_message(is_success)
    return f"{user_name}의 회피 — 주사위 {roll} (성공률 {success_rate}%)\n{dodge_text}"
