"""[지급/아이템1,아이템2,.../캐릭터1,캐릭터2,...] 명령어 핸들러 — 운영진 전용, 다중 아이템·다중 수혜자"""

import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.mastodon_client import reply
from bot.logger import get_logger
from bot.config import SYSTEM_ADMIN_IDS
from bot.services.character_service import get_character_by_name
from bot.services.item_service import get_item_info
from bot.services.inventory_service import add_item, get_available_space

logger = get_logger()


def handle(status_id: str, user: str, args: list[str]) -> None:
    """
    운영진 전용 아이템 지급 (다중 아이템·다중 수혜자).

    [지급/사과/아이작, 엘렌] → 아이작·엘렌 주변에 사과 1개씩
    [지급/사과, 사과, 사과/아이작] → 아이작 주변에 사과 3개
    [지급/사과, 사과, 반지, 사과/아이작, 엘렌] → 각자 주변에 사과 3개, 반지 1개
    """
    if user not in SYSTEM_ADMIN_IDS:
        reply(status_id, f"@{user} 이 명령은 운영진만 사용할 수 있습니다.")
        logger.command_error(user, "지급", "권한 없음")
        return

    if len(args) < 2:
        reply(status_id, f"@{user} 사용법: [지급/아이템(쉼표로 여러 개)/캐릭터(쉼표로 여러 명)]")
        return

    items_str = args[0].strip()
    recipients_str = args[1].strip()
    if not items_str or not recipients_str:
        reply(status_id, f"@{user} 아이템과 캐릭터를 입력해주세요. [지급/아이템1,아이템2/캐릭터1,캐릭터2]")
        return

    item_names = [s.strip() for s in items_str.split(",") if s.strip()]
    recipient_names = [s.strip() for s in recipients_str.split(",") if s.strip()]
    if not item_names or not recipient_names:
        reply(status_id, f"@{user} 아이템과 캐릭터를 각각 1개 이상 입력해주세요.")
        return

    request = Counter(item_names)

    unknown_items: list[str] = []
    for item_name in request:
        if not get_item_info(item_name):
            unknown_items.append(item_name)
    if unknown_items:
        reply(status_id, f"@{user} 존재하지 않는 아이템: {', '.join(unknown_items)}")
        return

    success_by_char: list[str] = []
    not_found: list[str] = []

    for target_name in recipient_names:
        character = get_character_by_name(target_name)
        if not character:
            not_found.append(target_name)
            continue
        char_name = character["name"]
        added_parts: list[str] = []
        for item_name, count in request.items():
            item_info = get_item_info(item_name)
            loc = "misc" if (item_info and item_info.get("volume", 0) == 0) else "nearby"
            if add_item(char_name, item_name, count, loc):
                added_parts.append(f"{item_name} {count}개")
            else:
                added_parts.append(f"{item_name} 지급 실패")
        success_by_char.append(f"{target_name}: {', '.join(added_parts)}")

    if not success_by_char:
        reply(status_id, f"@{user} 지급된 캐릭터가 없습니다. 찾을 수 없음: {', '.join(not_found)}")
        return

    response = f"@{user} 지급 완료.\n" + "\n".join(success_by_char)
    if not_found:
        response += f"\n(캐릭터 없음: {', '.join(not_found)})"
    reply(status_id, response)
    logger.command_response(user, "지급", response)
