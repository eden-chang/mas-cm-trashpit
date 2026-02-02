"""[지급/캐릭터1,캐릭터2,.../아이템1,아이템2,...] 명령어 핸들러 — 운영진 전용, 다중 캐릭터·다중 아이템"""

from collections import Counter

from bot.logger import get_logger
from bot.config import SYSTEM_ADMIN_IDS
from bot.services.character_service import get_character_by_name
from bot.services.item_service import get_item_info
from bot.services.inventory_service import add_item

logger = get_logger()


def handle(status_id: str, user: str, args: list[str]) -> str | None:
    """
    운영진 전용 아이템 지급 (다중 캐릭터·다중 아이템).
    [지급/캐릭터명/아이템명] — 문서·사용자 기대 순서.

    [지급/아이작, 엘렌/사과] → 아이작·엘렌 주변에 사과 1개씩
    [지급/아이작/사과, 사과, 사과] → 아이작 주변에 사과 3개
    [지급/아이작, 엘렌/사과, 사과, 반지, 사과] → 각자 주변에 사과 3개, 반지 1개
    """
    if user not in SYSTEM_ADMIN_IDS:
        logger.command_error(user, "지급", "권한 없음")
        return f"@{user} 이 명령은 운영진만 사용할 수 있습니다."

    if len(args) < 2:
        return f"@{user} 사용법: [지급/캐릭터(쉼표로 여러 명)/아이템(쉼표로 여러 개)]"

    recipients_str = args[0].strip()
    items_str = args[1].strip()
    if not recipients_str or not items_str:
        return f"@{user} 캐릭터와 아이템을 입력해주세요. [지급/캐릭터1,캐릭터2/아이템1,아이템2]"

    recipient_names = [s.strip() for s in recipients_str.split(",") if s.strip()]
    item_names = [s.strip() for s in items_str.split(",") if s.strip()]
    if not item_names or not recipient_names:
        return f"@{user} 캐릭터와 아이템을 각각 1개 이상 입력해주세요."

    request = Counter(item_names)

    unknown_items: list[str] = []
    for item_name in request:
        if not get_item_info(item_name):
            unknown_items.append(item_name)
    if unknown_items:
        return f"@{user} 존재하지 않는 아이템: {', '.join(unknown_items)}"

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
        return f"@{user} 지급된 캐릭터가 없습니다. 찾을 수 없습니다: {', '.join(not_found)}"

    response = f"@{user} 지급 완료.\n" + "\n".join(success_by_char)
    if not_found:
        response += f"\n(캐릭터를 찾을 수 없습니다: {', '.join(not_found)})"
    logger.command_response(user, "지급", response)
    return response
