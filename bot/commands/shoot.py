"""[발사] 명령어 핸들러 — 진영·근력 기반 발사 데미지 계산"""

from typing import Any, Dict

from bot.commands.attack import handle_combat_damage
from bot.utils.decorators import require_character


@require_character
def handle(status_id: str, user: str, character: Dict[str, Any], args: list) -> str:
    """[발사] — 진영별 발사 데미지 (웨가: 근력×10+랜덤40~80, 스카이: 60+랜덤20~60)."""
    return handle_combat_damage(status_id, user, character, args, "shoot")
