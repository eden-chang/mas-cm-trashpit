"""[사용/아이템명] 명령어 핸들러

문서 2.3 - 사용 명령어 스펙 기반 구현.
처리 흐름: 아이템 위치 확인 → 정보 조회 → 사용 가능 확인 → 효과 적용 → 차감 → 응답
"""

import sys
from typing import TYPE_CHECKING

sys.path.insert(0, str(__file__).rsplit("\\", 3)[0])

from bot.mastodon_client import reply
from bot.logger import get_logger
from bot.utils.dice import roll_dice
from bot.services.character_service import get_character_by_mastodon_id
from bot.services.item_service import get_item_info, is_usable
from bot.services.inventory_service import (
    find_item_location,
    get_item_count,
    remove_from_location,
    update_stat,
)
from shared.constants import ManagementColumns

if TYPE_CHECKING:
    from shared.models import ItemInfo

logger = get_logger()

# 스탯명 → 시트 컬럼 인덱스 매핑 (문서 2.3)
_STAT_COLUMNS = {
    "체력": ManagementColumns.HEALTH,
    "근력": ManagementColumns.STRENGTH,
    "행운": ManagementColumns.LUCK,
}


def handle(status_id: str, user: str, args: list[str]) -> None:
    """
    아이템 사용 처리

    1. 캐릭터 조회 (마스토돈 ID로)
    2. 아이템 위치 확인 (주변 → 가방 → 여유공간)
    3. 아이템 정보 조회 (상점)
    4. 사용 가능 여부 확인
    5. 효과 적용 (스탯 변경, 다이스 굴림 포함)
    6. 아이템 소모
    7. 결과 응답
    """
    if not args or not args[0].strip():
        reply(status_id, f"@{user} 사용할 아이템명을 입력해 주세요. 사용법: [사용/아이템명]")
        return

    item_name = args[0].strip()

    # 1. 캐릭터 조회
    character = get_character_by_mastodon_id(user)
    if not character:
        reply(status_id, f"@{user} 등록된 캐릭터를 찾을 수 없습니다.")
        return

    char_name = character.name

    # 2. 아이템 위치 확인
    location = find_item_location(char_name, item_name)
    if not location:
        reply(status_id, f"@{user} '{item_name}'을(를) 소지하고 있지 않습니다.")
        return

    # 3. 아이템 정보 조회
    item_info = get_item_info(item_name)
    if not item_info:
        reply(status_id, f"@{user} '{item_name}' 정보를 찾을 수 없습니다.")
        return

    # 4. 사용 가능 여부 확인
    if not is_usable(item_info):
        reply(status_id, f"@{user} '{item_name}'은(는) 사용할 수 없는 아이템입니다.")
        return

    # 5. 효과 적용 (다이스 굴림 포함) - 문서 2.3 순서
    actual_value, effect_ok = _apply_effect(char_name, item_info)
    if effect_ok is False:
        reply(
            status_id,
            f"@{user} 스탯 적용 중 오류가 발생했습니다. 아이템은 소모되지 않았습니다. 잠시 후 다시 시도해 주세요.",
        )
        return

    # 6. 아이템 소모
    if not remove_from_location(char_name, item_name, 1, location):
        reply(
            status_id,
            f"@{user} 아이템 차감 중 오류가 발생했습니다. 효과는 적용되었을 수 있으니 "
            "다시 사용하지 마세요. 문제가 계속되면 운영진에게 문의해 주세요.",
        )
        return

    # 7. 응답
    remaining = get_item_count(char_name, item_name)
    use_message = (item_info.use_message or "").strip() or f"{item_name}을(를) 사용했다."
    response = f"@{user} {use_message}"

    effect_text = _format_effect(item_info.stat, actual_value)
    if effect_text:
        response += f"\n{effect_text}"

    if remaining > 0:
        response += f"\n남은 {item_name}: {remaining}개"
    else:
        response += f"\n(마지막 {item_name}을(를) 사용했습니다)"

    reply(status_id, response)
    logger.command_response(user, f"사용/{item_name}", response)


def _apply_effect(char_name: str, item_info: "ItemInfo") -> tuple[int, bool | None]:
    """아이템 효과 적용 (스탯 변경).

    Returns:
        (적용된 수치, 성공 여부)
        - 효과가 없으면 (0, None) - 실패가 아님
        - 스탯 업데이트 실패 시 (0, False)
    """
    stat = (item_info.stat or "").strip()
    value_str = (item_info.value or "").strip()

    if not stat or stat == "사용 불가" or not value_str:
        return 0, None

    column = _STAT_COLUMNS.get(stat)
    if column is None:
        return 0, None

    actual_value = roll_dice(value_str)
    if not update_stat(char_name, column, actual_value):
        logger.error(f"스탯 업데이트 실패: {char_name}/{stat}/{actual_value}")
        return 0, False
    return actual_value, True


def _format_effect(stat: str, value: int) -> str:
    """효과 텍스트 포맷 (문서 2.3)"""
    if not stat or stat == "사용 불가" or value == 0:
        return ""
    sign = "+" if value > 0 else ""
    return f"효과: {stat} {sign}{value}"
