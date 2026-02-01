"""[버리기/아이템명] 명령어 핸들러"""

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from bot.mastodon_client import reply
from bot.logger import get_logger
from bot.services.character_service import get_character_by_mastodon_id
from bot.services.inventory_service import (
    find_item_location,
    remove_from_location,
)

logger = get_logger()

LOCATION_NAMES = {
    "nearby": "주변",
    "bag": "가방",
    "misc": "여유공간",
}


def handle(status_id: str, user: str, args: list[str]) -> None:
    """
    아이템 버리기 처리

    1. 캐릭터 조회
    2. 아이템 위치 확인 (주변 -> 가방 -> 여유공간)
    3. 해당 위치에서 삭제
    4. 결과 응답
    """
    if not args:
        reply(status_id, f"@{user} 사용법: [버리기/아이템명]")
        return

    item_name = args[0].strip()
    if not item_name:
        reply(status_id, f"@{user} 아이템명을 입력해주세요. 사용법: [버리기/아이템명]")
        return

    # 캐릭터 조회
    character = get_character_by_mastodon_id(user)
    if not character:
        reply(status_id, f"@{user} 등록된 캐릭터를 찾을 수 없습니다.")
        return

    char_name = character.name

    # 아이템 위치 확인
    location = find_item_location(char_name, item_name)
    if not location:
        reply(status_id, f"@{user} '{item_name}'을(를) 소지하고 있지 않습니다.")
        return

    # 삭제 처리
    removed = remove_from_location(char_name, item_name, 1, location)
    if not removed:
        reply(status_id, f"@{user} '{item_name}' 버리기에 실패했습니다. 나중에 다시 시도해주세요.")
        logger.command_error(user, f"버리기/{item_name}", "인벤토리 업데이트 실패")
        return

    location_name = LOCATION_NAMES.get(location, location)
    response = f"@{user} {item_name}을(를) 버렸습니다. ({location_name}에서)"

    reply(status_id, response)
    logger.command_response(user, f"버리기/{item_name}", response)
