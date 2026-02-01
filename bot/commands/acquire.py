"""[획득/아이템명] 명령어 핸들러"""

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from bot.mastodon_client import reply
from bot.logger import get_logger
from bot.services.character_service import get_character_by_mastodon_id
from bot.services.item_service import get_item_info
from bot.services.inventory_service import add_to_nearby, add_to_misc, get_available_space

logger = get_logger()


def handle(status_id: str, user: str, args: list) -> None:
    """
    아이템 획득 처리

    1. 캐릭터 조회
    2. 아이템 정보 조회
    3. 부피에 따라 주변 또는 여유공간에 추가
    4. 결과 응답
    """
    if not args:
        reply(status_id, f"@{user} 사용법: [획득/아이템명]")
        return

    item_name = args[0].strip()
    if not item_name:
        reply(status_id, f"@{user} 아이템명을 입력해주세요. 사용법: [획득/아이템명]")
        return

    character = get_character_by_mastodon_id(user)
    if not character:
        reply(status_id, f"@{user} 등록된 캐릭터를 찾을 수 없습니다.")
        return

    char_name = character.name

    item_info = get_item_info(item_name)
    if not item_info:
        reply(status_id, f"@{user} '{item_name}'은(는) 존재하지 않는 아이템입니다.")
        return

    volume = item_info.volume

    if volume == 0:
        added = add_to_misc(char_name, item_name, 1)
    else:
        added = add_to_nearby(char_name, item_name, 1)

    if not added:
        reply(
            status_id,
            f"@{user} '{item_name}' 획득 처리에 실패했습니다. 나중에 다시 시도해주세요.",
        )
        logger.command_error(user, f"획득/{item_name}", "인벤토리 업데이트 실패")
        return

    if volume == 0:
        response = (
            f"@{user} {item_name}을(를) 획득했습니다! (부피 0)\n"
            f"자동으로 여유공간에 보관되었습니다."
        )
    else:
        available = get_available_space(char_name)
        if volume <= available:
            response = (
                f"@{user} {item_name}을(를) 획득했습니다! (부피: {volume})\n"
                f"가방 남은 공간: {available}칸\n"
                f"웹에서 가방에 넣으세요."
            )
        else:
            response = (
                f"@{user} {item_name}을(를) 획득했습니다! (부피: {volume})\n"
                f"⚠️ 가방 공간이 부족합니다! (남은 공간: {available}칸)\n"
                f"주변에 임시 보관됩니다. (자동 삭제 주의)"
            )

    reply(status_id, response)
    logger.command_response(user, f"획득/{item_name}", response)
