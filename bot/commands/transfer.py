"""[양도/아이템1,아이템2,.../받는사람] 명령어 핸들러 — 다중 아이템, 주변→여유공간→가방 우선 차감."""

from collections import Counter

from bot.services.character_service import get_character_by_mastodon_id, get_character
from bot.services.item_service import get_item_info
from bot.services.inventory_service import (
    add_item,
    remove_item_by_priority,
    update_stat,
)
from bot.notifications import notify_item_received
from bot.logger import get_logger

logger = get_logger()


def handle_item(status_id: str, user: str, args: list) -> str:
    """아이템 양도 (여러 개 가능). [양도/사과, 반지, 사과/아이작] → 사과 2개·반지 1개를 아이작에게."""
    if len(args) < 2:
        msg = f"@{user} 사용법: [양도/아이템명(쉼표로 여러 개)/받는사람이름]"
        logger.command_error(user, "양도", "인자 부족")
        return msg

    item_part = args[0].strip()
    target_name = args[1].strip()
    if not item_part or not target_name:
        msg = f"@{user} 사용법: [양도/아이템명(쉼표로 여러 개)/받는사람이름]"
        logger.command_error(user, "양도", "아이템/대상 비어 있음")
        return msg

    item_names = [s.strip() for s in item_part.split(",") if s.strip()]
    if not item_names:
        msg = f"@{user} 양도할 아이템을 입력해 주세요."
        logger.command_error(user, "양도", "아이템 목록 없음")
        return msg

    request = Counter(item_names)

    sender = get_character_by_mastodon_id(user)
    if not sender:
        msg = f"@{user} 등록된 캐릭터를 찾을 수 없습니다."
        logger.command_error(user, "양도", "등록된 캐릭터 없음")
        return msg
    sender_char_name = sender["name"]

    receiver = get_character(target_name)
    if not receiver:
        msg = f"@{user} 받는 사람 '{target_name}'을(를) 찾을 수 없습니다."
        logger.command_error(user, "양도", f"받는 사람 없음: {target_name}")
        return msg
    if sender_char_name == target_name:
        msg = f"@{user} 자기 자신에게는 양도할 수 없습니다."
        logger.command_error(user, "양도", "자기 자신에게 양도 시도")
        return msg

    success_lines: list[str] = []
    fail_lines: list[str] = []

    for item_name, need_count in request.items():
        item_info = get_item_info(item_name)
        if not item_info:
            fail_lines.append(f"'{item_name}' — 아이템 정보 없음")
            continue

        actual = remove_item_by_priority(sender_char_name, item_name, need_count)
        if actual <= 0:
            fail_lines.append(f"'{item_name}' {need_count}개 — 소지하지 않음")
            continue

        target_loc = "misc" if item_info.get("volume", 0) == 0 else "nearby"
        if not add_item(target_name, item_name, actual, target_loc):
            add_item(sender_char_name, item_name, actual, "nearby")
            fail_lines.append(f"'{item_name}' — 수신자 추가 실패(롤백)")
            continue

        dest_label = "여유공간" if target_loc == "misc" else "주변"
        recipient_id = receiver.get("mastodon_id")
        if recipient_id:
            notify_item_received(
                str(recipient_id), sender_char_name, item_name, actual, dest_label
            )
        if actual == need_count:
            success_lines.append(f"'{item_name}' {actual}개 → {target_name} ({dest_label})")
        else:
            success_lines.append(f"'{item_name}' {actual}개 전달 (요청 {need_count}개 중 부족 {need_count - actual}개)")
            fail_lines.append(f"'{item_name}' — {need_count - actual}개 부족")

    if not success_lines:
        msg = f"@{user} 양도된 아이템이 없습니다.\n" + "\n".join(fail_lines)
        logger.command_error(user, "양도", "양도 성공 없음(소지 부족 등)")
        return msg

    head = f"@{user} {target_name}에게 양도했습니다.\n" + "\n".join(success_lines)
    if fail_lines:
        head += "\n(실패/부족: " + "; ".join(fail_lines) + ")"
    logger.command_response(user, "양도", head)
    return head

def handle_point(status_id: str, user: str, args: list) -> str:
    """포인트(소지금) 양도."""
    if len(args) < 2:
        msg = f"@{user} 사용법: [양도/포인트수/받는사람이름] (예: [양도/10포인트/캐릭터명])"
        logger.command_error(user, "양도(포인트)", "인자 부족")
        return msg
    try:
        amount = int(args[0])
    except ValueError:
        msg = f"@{user} 포인트는 숫자로 입력해 주세요."
        logger.command_error(user, "양도(포인트)", "포인트 비숫자")
        return msg
    recipient_name = args[1].strip()
    if amount <= 0:
        msg = f"@{user} 양도할 포인트는 1 이상이어야 합니다."
        logger.command_error(user, "양도(포인트)", "포인트 0 이하")
        return msg

    sender = get_character_by_mastodon_id(user)
    if not sender:
        msg = f"@{user} 등록된 캐릭터를 찾을 수 없습니다."
        logger.command_error(user, "양도(포인트)", "등록된 캐릭터 없음")
        return msg
    sender_name = sender["name"]
    try:
        sender_points = int(sender.get("points", 0) or 0)
    except (TypeError, ValueError):
        sender_points = 0

    recipient = get_character(recipient_name)
    if not recipient:
        msg = f"@{user} '{recipient_name}' 캐릭터를 찾을 수 없습니다."
        logger.command_error(user, "양도(포인트)", f"받는 사람 없음: {recipient_name}")
        return msg
    if sender_name == recipient_name:
        msg = f"@{user} 자기 자신에게는 양도할 수 없습니다."
        logger.command_error(user, "양도(포인트)", "자기 자신에게 양도 시도")
        return msg

    if sender_points < amount:
        msg = f"@{user} 포인트가 부족합니다. (보유: {sender_points})"
        logger.command_error(user, "양도(포인트)", "포인트 부족")
        return msg

    if not update_stat(sender_name, "points", -amount):
        msg = f"@{user} 포인트 차감 중 오류가 발생했습니다."
        logger.command_error(user, "양도(포인트)", "포인트 차감 실패")
        return msg
    if not update_stat(recipient_name, "points", amount):
        update_stat(sender_name, "points", amount)  # 롤백
        msg = f"@{user} 포인트 지급 중 오류가 발생했습니다."
        logger.command_error(user, "양도(포인트)", "포인트 지급 실패(롤백)")
        return msg

    remaining = sender_points - amount
    response = (
        f"@{user} {amount}포인트를 {recipient_name}에게 양도했습니다!\n"
        f"남은 포인트: {remaining}"
    )
    logger.command_response(user, "양도(포인트)", response)
    return response
