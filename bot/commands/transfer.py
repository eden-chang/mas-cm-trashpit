"""[양도/아이템1,아이템2,.../받는사람] 명령어 핸들러 — 다중 아이템, 주변→여유공간→가방 우선 차감."""

import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.constants import ManagementColumns
from bot.services.character_service import get_character_by_mastodon_id, get_character
from bot.services.item_service import get_item_info
from bot.services.inventory_service import (
    add_item,
    remove_item_by_priority,
    update_stat,
)

def handle_item(status_id: str, user: str, args: list) -> str:
    """아이템 양도 (여러 개 가능). [양도/사과, 반지, 사과/아이작] → 사과 2개·반지 1개를 아이작에게."""
    if len(args) < 2:
        return f"@{user} 사용법: [양도/아이템명(쉼표로 여러 개)/받는사람이름]"

    item_part = args[0].strip()
    target_name = args[1].strip()
    if not item_part or not target_name:
        return f"@{user} 사용법: [양도/아이템명(쉼표로 여러 개)/받는사람이름]"

    item_names = [s.strip() for s in item_part.split(",") if s.strip()]
    if not item_names:
        return f"@{user} 양도할 아이템을 입력해 주세요."

    request = Counter(item_names)

    sender = get_character_by_mastodon_id(user)
    if not sender:
        return f"@{user} 등록된 캐릭터를 찾을 수 없습니다."
    sender_char_name = sender["name"]

    receiver = get_character(target_name)
    if not receiver:
        return f"@{user} 받는 사람 '{target_name}'을(를) 찾을 수 없습니다."
    if sender_char_name == target_name:
        return f"@{user} 자기 자신에게는 양도할 수 없습니다."

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
        if actual == need_count:
            success_lines.append(f"'{item_name}' {actual}개 → {target_name} ({dest_label})")
        else:
            success_lines.append(f"'{item_name}' {actual}개 전달 (요청 {need_count}개 중 부족 {need_count - actual}개)")
            fail_lines.append(f"'{item_name}' — {need_count - actual}개 부족")

    if not success_lines:
        return f"@{user} 양도된 아이템이 없습니다.\n" + "\n".join(fail_lines)

    head = f"@{user} {target_name}에게 양도했습니다.\n" + "\n".join(success_lines)
    if fail_lines:
        head += "\n(실패/부족: " + "; ".join(fail_lines) + ")"
    return head

def handle_point(status_id: str, user: str, args: list) -> str:
    """포인트(소지금) 양도."""
    if len(args) < 2:
        return f"@{user} 사용법: [양도/포인트수/받는사람이름] (예: [양도/10포인트/캐릭터명])"
    try:
        amount = int(args[0])
    except ValueError:
        return f"@{user} 포인트는 숫자로 입력해 주세요."
    recipient_name = args[1].strip()
    if amount <= 0:
        return f"@{user} 양도할 포인트는 1 이상이어야 합니다."

    sender = get_character_by_mastodon_id(user)
    if not sender:
        return f"@{user} 등록된 캐릭터를 찾을 수 없습니다."
    sender_name = sender["name"]
    raw = sender.get("raw") or []
    try:
        sender_points = int(raw[ManagementColumns.MONEY]) if len(raw) > ManagementColumns.MONEY and raw[ManagementColumns.MONEY] not in (None, "") else 0
    except (TypeError, ValueError):
        sender_points = 0

    recipient = get_character(recipient_name)
    if not recipient:
        return f"@{user} '{recipient_name}' 캐릭터를 찾을 수 없습니다."
    if sender_name == recipient_name:
        return f"@{user} 자기 자신에게는 양도할 수 없습니다."

    if sender_points < amount:
        return f"@{user} 포인트가 부족합니다. (보유: {sender_points})"

    if not update_stat(sender_name, ManagementColumns.MONEY, -amount):
        return f"@{user} 포인트 차감 중 오류가 발생했습니다."
    if not update_stat(recipient_name, ManagementColumns.MONEY, amount):
        update_stat(sender_name, ManagementColumns.MONEY, amount)  # 롤백
        return f"@{user} 포인트 지급 중 오류가 발생했습니다."

    remaining = sender_points - amount
    return (
        f"@{user} {amount}포인트를 {recipient_name}에게 양도했습니다!\n"
        f"남은 포인트: {remaining}"
    )
