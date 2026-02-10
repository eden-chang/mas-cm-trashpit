"""[상태 확인] 명령어 핸들러 — 본인 스탯·포인트·HP·가방 출력"""

from typing import Any, Dict

from shared.constants import get_bag_capacity
from bot.services.item_service import get_item_info
from bot.services.combat_utils import parse_stat
from bot.utils.decorators import require_character
from bot.logger import get_logger

logger = get_logger()


@require_character
def handle(status_id: str, user: str, character: Dict[str, Any], args: list[str]) -> str:
    """[상태 확인] — 근력, 체력, 행운, 포인트, HP, 가방 사용/용량 출력."""
    strength = parse_stat(character, "strength", 0)
    health = parse_stat(character, "health", 0)
    luck = parse_stat(character, "luck", 0)
    points = parse_stat(character, "points", 0)
    hp = parse_stat(character, "hp", 0)

    max_hp = health * 10
    capacity = get_bag_capacity(strength)
    bag_data = character.get("bag") or {}
    if not isinstance(bag_data, dict):
        bag_data = {}
    used = 0
    for item_name, qty in bag_data.items():
        try:
            q = int(qty)
        except (TypeError, ValueError):
            continue
        if q <= 0:
            continue
        info = get_item_info(item_name)
        if not info:
            logger.warning("상태 확인: 미등록 아이템 '%s' (캐릭터: %s)", item_name, character.get("name", "?"))
        vol = (info.get("volume", 0) or 0) if info else 0
        used += vol * q

    lines = [
        "상태 확인",
        "",
        f"근력 {strength}",
        f"체력 {health}",
        f"행운 {luck}",
        "",
        f"{points:,} 포인트 소지",
        "",
        f"HP {hp}/{max_hp}",
        f"가방 {used}/{capacity}",
    ]
    return "\n".join(lines)
