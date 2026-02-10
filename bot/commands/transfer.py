"""[양도/아이템1,아이템2,.../받는사람] 명령어 핸들러 — 다중 아이템, 주변→여유공간→가방 우선 차감."""

from collections import Counter

from bot.services.character_service import get_character_by_mastodon_id, get_character, CharacterServiceError
from bot.services.item_service import get_item_info
from bot.services.inventory_service import (
    add_item,
    remove_item_by_priority_detailed,
    update_stat,
)
from bot.notifications import notify_item_received
from bot.utils.korean import josa
from bot.utils.locking import get_character_lock
from bot.utils.validation import validate_item_name
from bot.logger import get_logger

logger = get_logger()

_SYSTEM_ERROR = "시스템 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."


def _acquire_dual_locks(name_a: str, name_b: str):
    """두 캐릭터 락을 이름 사전순으로 획득 (데드락 방지). context manager로 사용."""
    import contextlib

    first, second = sorted([name_a, name_b])

    @contextlib.contextmanager
    def _dual():
        lock1 = get_character_lock(first)
        lock2 = get_character_lock(second)
        lock1.acquire()
        try:
            lock2.acquire()
            try:
                yield
            finally:
                lock2.release()
        finally:
            lock1.release()

    return _dual()


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

    for name in item_names:
        is_valid, error_msg = validate_item_name(name)
        if not is_valid:
            return f"@{user} {error_msg}"

    request = Counter(item_names)

    try:
        sender = get_character_by_mastodon_id(user)
    except CharacterServiceError:
        return f"@{user} {_SYSTEM_ERROR}"
    if not sender:
        msg = f"@{user} 등록된 캐릭터를 찾을 수 없습니다."
        logger.command_error(user, "양도", "등록된 캐릭터 없음")
        return msg
    sender_char_name = sender["name"]

    try:
        receiver = get_character(target_name)
    except CharacterServiceError:
        return f"@{user} {_SYSTEM_ERROR}"
    if not receiver:
        msg = f"@{user} '{target_name}' 캐릭터를 찾을 수 없습니다. 명단에 등록되어 있는지 확인해 주세요."
        logger.command_error(user, "양도", f"받는 사람 없음: {target_name}")
        return msg
    if sender_char_name == target_name:
        msg = f"@{user} 자기 자신에게는 양도할 수 없습니다."
        logger.command_error(user, "양도", "자기 자신에게 양도 시도")
        return msg

    # 두 캐릭터 락을 사전순으로 획득 (데드락 방지)
    with _acquire_dual_locks(sender_char_name, target_name):
        success_lines: list[str] = []
        fail_lines: list[str] = []

        for item_name, need_count in request.items():
            item_info = get_item_info(item_name)
            if not item_info:
                fail_lines.append(f"'{item_name}' — 아이템 정보 없음")
                continue

            actual, removed_locations = remove_item_by_priority_detailed(
                sender_char_name, item_name, need_count
            )
            if actual <= 0:
                fail_lines.append(f"'{item_name}' {need_count}개 — 소지하지 않음")
                continue

            target_loc = "misc" if item_info.get("volume", 0) == 0 else "nearby"
            if not add_item(target_name, item_name, actual, target_loc):
                # 롤백: 원래 위치로 복원
                for rb_loc, rb_qty in removed_locations:
                    if not add_item(sender_char_name, item_name, rb_qty, rb_loc):
                        logger.error(
                            "양도 롤백 실패: sender=%s item=%s loc=%s qty=%d",
                            sender_char_name, item_name, rb_loc, rb_qty,
                        )
                fail_lines.append(f"'{item_name}' — 수신자 추가 실패(롤백)")
                continue

            dest_label = "여유공간" if target_loc == "misc" else "주변"
            recipient_id = receiver.get("mastodon_id")
            if recipient_id:
                notify_item_received(
                    str(recipient_id), sender_char_name, item_name, actual, dest_label
                )
            if actual == need_count:
                success_lines.append(f"- {item_name} {actual}개 ({dest_label})")
            else:
                success_lines.append(f"- {item_name} {actual}개 ({dest_label}) (요청 {need_count}개 중 {need_count - actual}개 부족)")
                fail_lines.append(f"'{item_name}' — {need_count - actual}개 부족")

    if not success_lines:
        msg = f"@{user} 양도된 아이템이 없습니다.\n" + "\n".join(fail_lines)
        logger.command_error(user, "양도", "양도 성공 없음(소지 부족 등)")
        return msg

    # 단일 아이템: "{아이템}을/를 {대상}에게 양도했습니다."
    if len(request) == 1:
        only_name = next(iter(request))
        head = f"@{user} {josa(only_name, '을/를')} {target_name}에게 양도했습니다."
    else:
        head = f"@{user} {target_name}에게 양도했습니다."
        head += "\n" + "\n".join(success_lines)
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

    try:
        sender = get_character_by_mastodon_id(user)
    except CharacterServiceError:
        return f"@{user} {_SYSTEM_ERROR}"
    if not sender:
        msg = f"@{user} 등록된 캐릭터를 찾을 수 없습니다."
        logger.command_error(user, "양도(포인트)", "등록된 캐릭터 없음")
        return msg
    sender_name = sender["name"]

    try:
        recipient = get_character(recipient_name)
    except CharacterServiceError:
        return f"@{user} {_SYSTEM_ERROR}"
    if not recipient:
        msg = f"@{user} '{recipient_name}' 캐릭터를 찾을 수 없습니다. 명단에 등록되어 있는지 확인해 주세요."
        logger.command_error(user, "양도(포인트)", f"받는 사람 없음: {recipient_name}")
        return msg
    if sender_name == recipient_name:
        msg = f"@{user} 자기 자신에게는 양도할 수 없습니다."
        logger.command_error(user, "양도(포인트)", "자기 자신에게 양도 시도")
        return msg

    # 두 캐릭터 락을 사전순으로 획득 (데드락 방지)
    with _acquire_dual_locks(sender_name, recipient_name):
        # 락 내에서 sender 포인트 재조회 (TOCTOU 방지)
        try:
            sender = get_character_by_mastodon_id(user)
        except CharacterServiceError:
            return f"@{user} {_SYSTEM_ERROR}"
        try:
            sender_points = int(sender.get("points", 0) or 0) if sender else 0
        except (TypeError, ValueError):
            sender_points = 0

        if sender_points < amount:
            msg = f"@{user} 소지금이 부족합니다. 현재 보유: {sender_points:,}포인트"
            logger.command_error(user, "양도(포인트)", "포인트 부족")
            return msg

        if not update_stat(sender_name, "points", -amount):
            msg = f"@{user} 포인트 차감 중 오류가 발생했습니다."
            logger.command_error(user, "양도(포인트)", "포인트 차감 실패")
            return msg
        if not update_stat(recipient_name, "points", amount):
            if not update_stat(sender_name, "points", amount):  # 롤백 실패
                logger.error(f"포인트 양도 롤백 실패: sender={sender_name} amount={amount}")
                msg = f"@{user} 포인트 지급 중 오류가 발생했으며, 환불도 실패했습니다. 관리자에게 문의해 주세요."
            else:
                msg = f"@{user} 포인트 지급 중 오류가 발생했습니다."
            logger.command_error(user, "양도(포인트)", "포인트 지급 실패(롤백)")
            return msg

        remaining = sender_points - amount

    response = (
        f"@{user} {amount:,} 포인트를 {recipient_name}에게 양도했습니다. "
        f"현재 소지금은 {remaining:,} 포인트입니다."
    )
    logger.command_response(user, "양도(포인트)", response)
    return response
