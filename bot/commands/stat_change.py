"""[hp/3], [체력/-5], [근력/-1], [행운/3] 본인 스탯 변경 명령어 핸들러"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.constants import STAT_INPUT_TO_KEY, STAT_KEY_TO_DISPLAY_NAME
from bot.utils.korean import josa
from bot.logger import get_logger
from bot.services.character_service import get_character_by_mastodon_id
from bot.services.inventory_service import update_stat

logger = get_logger()


def handle(status_id: str, user: str, args: list[str]) -> str | None:
    """
    본인 스탯 변경. args: [stat_name, delta_str] (예: ["체력", "-5"])
    """
    if len(args) < 2:
        logger.debug(f"stat_change: args 부족 user={user} args={args}")
        return f"@{user} 사용법: [스탯명/숫자] (예: [hp/3], [체력/-5], [근력/-1], [행운/3])"

    stat_input = args[0].strip().lower()
    try:
        delta = int(args[1].strip())
    except (ValueError, TypeError):
        logger.warning(f"stat_change: 숫자 아님 user={user} args={args}")
        return f"@{user} 숫자를 입력해 주세요. (예: [체력/-5])"

    stat_key = STAT_INPUT_TO_KEY.get(stat_input)
    if not stat_key:
        logger.warning(f"stat_change: 지원하지 않는 스탯 user={user} stat_input={stat_input}")
        return f"@{user} 지원 스탯: hp, 체력, 근력, 행운"

    character = get_character_by_mastodon_id(user)
    if not character:
        logger.info(f"stat_change: 캐릭터 없음 user={user}")
        return f"@{user} 등록된 캐릭터를 찾을 수 없습니다."

    char_name = character["name"]
    current = character.get(stat_key, 0) or 0
    try:
        current = int(current)
    except (TypeError, ValueError):
        current = 0

    if not update_stat(char_name, stat_key, delta):
        logger.error(f"stat_change: update_stat 실패 user={user} char={char_name} stat={stat_key} delta={delta}")
        return f"@{user} 스탯 변경에 실패했습니다."

    new_value = current + delta
    display = STAT_KEY_TO_DISPLAY_NAME.get(stat_key, stat_key)
    logger.info(f"stat_change: 성공 user={user} char={char_name} {display} {current}→{new_value}")
    return f"@{user} {josa(display, '이/가')} {current} → {new_value}로 변경되었습니다."
