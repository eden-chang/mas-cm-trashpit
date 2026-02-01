"""[지급/캐릭터명/아이템명] 명령어 핸들러 — 운영진 전용 아이템 지급"""

import sys

sys.path.insert(0, str(__file__).rsplit("\\", 3)[0])
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from bot.mastodon_client import reply
from bot.logger import get_logger
from bot.config import SYSTEM_ADMIN_IDS
from bot.services.character_service import get_character_by_name
from bot.services.item_service import get_item_info
from bot.services.inventory_service import (
    add_to_nearby,
    add_to_misc,
    get_available_space,
)

logger = get_logger()


def handle(status_id: str, user: str, args: list[str]) -> None:
    """
    운영진 전용 아이템 지급 처리

    1. 운영진 권한 확인
    2. 대상 캐릭터 조회
    3. 아이템 정보 조회
    4. 부피에 따라 주변 또는 여유공간에 추가
    5. 결과 응답
    """
    if user not in SYSTEM_ADMIN_IDS:
        reply(status_id, f"@{user} 이 명령은 운영진만 사용할 수 있습니다.")
        logger.command_error(user, "지급", "권한 없음")
        return

    if len(args) < 2:
        reply(status_id, f"@{user} 사용법: [지급/캐릭터명/아이템명]")
        return

    target_name = args[0].strip()
    item_name = args[1].strip()
    if not target_name or not item_name:
        reply(status_id, f"@{user} 캐릭터명과 아이템명을 입력해주세요. 사용법: [지급/캐릭터명/아이템명]")
        return

    character = get_character_by_name(target_name)
    if not character:
        reply(status_id, f"@{user} '{target_name}' 캐릭터를 찾을 수 없습니다.")
        return

    item_info = get_item_info(item_name)
    if not item_info:
        reply(status_id, f"@{user} '{item_name}'은(는) 존재하지 않는 아이템입니다.")
        return

    char_name = character.name
    volume = item_info.volume

    if volume == 0:
        added = add_to_misc(char_name, item_name, 1)
    else:
        added = add_to_nearby(char_name, item_name, 1)

    if not added:
        reply(
            status_id,
            f"@{user} '{item_name}' 지급 처리에 실패했습니다. 나중에 다시 시도해주세요.",
        )
        logger.command_error(user, f"지급/{target_name}/{item_name}", "인벤토리 업데이트 실패")
        return

    if volume == 0:
        response = (
            f"@{user} {target_name}에게 {item_name}을(를) 지급했습니다. (부피 0)\n"
            f"자동으로 여유공간에 보관되었습니다."
        )
    else:
        available = get_available_space(char_name)
        if volume <= available:
            response = (
                f"@{user} {target_name}에게 {item_name}을(를) 지급했습니다. (부피: {volume})\n"
                f"가방 남은 공간: {available}칸\n"
                f"웹에서 가방에 넣으세요."
            )
        else:
            response = (
                f"@{user} {target_name}에게 {item_name}을(를) 지급했습니다. (부피: {volume})\n"
                f"가방 공간이 부족합니다! (남은 공간: {available}칸)\n"
                f"주변에 임시 보관됩니다. (자동 삭제 주의)"
            )

    reply(status_id, response)
    logger.command_response(user, f"지급/{target_name}/{item_name}", response)
