"""[양도/...] 명령어 핸들러

문서 2.4 - 양도 명령어 스펙 기반 구현.
- [양도/아이템명/이름]: 아이템 양도
- [양도/n포인트/이름]: 포인트 양도
"""

import sys

sys.path.insert(0, str(__file__).rsplit("\\", 3)[0])
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from bot.mastodon_client import reply, send_dm
from bot.logger import get_logger
from bot.services.character_service import (
    get_character_by_mastodon_id,
    get_character_by_name,
)
from bot.services.item_service import get_item_info
from bot.services.inventory_service import (
    find_item_location,
    remove_from_location,
    add_to_nearby,
    add_to_bag,
    add_to_misc,
    update_stat,
)
from shared.constants import ManagementColumns
from shared.models import Character

logger = get_logger()


def handle_item(status_id: str, user: str, args: list[str]) -> None:
    """[양도/아이템명/이름] - 아이템을 다른 캐릭터에게 양도합니다.

    처리 흐름 (문서 2.4):
    1. 수신자 캐릭터 확인
    2. 아이템 위치 확인 (발신자)
    3. 아이템 정보 조회
    4. 발신자에서 제거
    5. 수신자 주변(또는 여유공간)에 추가
    6. 양쪽에 알림
    """
    if len(args) < 2:
        reply(status_id, f"@{user} 사용법: [양도/아이템명/캐릭터명]")
        return

    item_name = args[0].strip()
    recipient_name = args[1].strip()
    if not item_name or not recipient_name:
        reply(status_id, f"@{user} 아이템명과 캐릭터명을 입력해주세요. 사용법: [양도/아이템명/캐릭터명]")
        return

    # 1. 발신자/수신자 검증
    validation = _validate_transfer_parties(status_id, user, recipient_name)
    if validation is None:
        return
    sender, recipient = validation
    sender_name = sender.name

    # 2. 아이템 위치 확인
    location = find_item_location(sender_name, item_name)
    if not location:
        reply(status_id, f"@{user} '{item_name}'을(를) 소지하고 있지 않습니다.")
        return

    # 3. 아이템 정보
    item_info = get_item_info(item_name)
    if not item_info:
        reply(status_id, f"@{user} '{item_name}' 정보를 찾을 수 없습니다.")
        return

    # 4. 발신자에서 제거
    removed = remove_from_location(sender_name, item_name, 1, location)
    if not removed:
        reply(status_id, f"@{user} '{item_name}' 양도 처리에 실패했습니다. 나중에 다시 시도해주세요.")
        logger.command_error(user, f"양도/{item_name}/{recipient_name}", "인벤토리 업데이트 실패")
        return

    # 5. 수신자에게 추가 (volume 0 → 여유공간, 그 외 → 주변)
    if item_info.volume == 0:
        added = add_to_misc(recipient_name, item_name, 1)
        dest = "여유공간"
    else:
        added = add_to_nearby(recipient_name, item_name, 1)
        dest = "주변"

    if not added:
        _rollback_add_to_sender(sender_name, item_name, location)
        reply(status_id, f"@{user} '{item_name}' 양도 처리에 실패했습니다. 나중에 다시 시도해주세요.")
        logger.command_error(user, f"양도/{item_name}/{recipient_name}", "인벤토리 업데이트 실패")
        return

    # 6. 응답
    response = f"@{user} {item_name}을(를) {recipient_name}에게 양도했습니다!"
    reply(status_id, response)
    logger.command_response(user, f"양도/{item_name}/{recipient_name}", response)

    _notify_recipient_item(recipient, sender_name, item_name, dest)


def _validate_transfer_parties(
    status_id: str, user: str, recipient_name: str
) -> tuple[Character, Character] | None:
    """발신자·수신자 검증. (sender, recipient) 반환 또는 None."""
    sender = get_character_by_mastodon_id(user)
    if not sender:
        reply(status_id, f"@{user} 등록된 캐릭터를 찾을 수 없습니다.")
        return None

    recipient = get_character_by_name(recipient_name)
    if not recipient:
        reply(status_id, f"@{user} '{recipient_name}' 캐릭터를 찾을 수 없습니다.")
        return None

    if sender.name == recipient_name:
        reply(status_id, f"@{user} 자기 자신에게는 양도할 수 없습니다.")
        return None

    return (sender, recipient)


def _rollback_add_to_sender(
    sender_name: str, item_name: str, location: str
) -> None:
    """수신자 추가 실패 시 발신자 인벤토리 롤백"""
    adders = {"nearby": add_to_nearby, "bag": add_to_bag, "misc": add_to_misc}
    adder = adders.get(location, add_to_nearby)
    adder(sender_name, item_name, 1)


def handle_point(status_id: str, user: str, args: list[str]) -> None:
    """[양도/n포인트/이름] - 포인트를 다른 캐릭터에게 양도합니다.

    처리 흐름 (문서 2.4):
    1. 수신자 캐릭터 확인
    2. 발신자 포인트 확인
    3. 포인트 차감/추가
    4. 양쪽에 알림

    Note: trashpit은 행운(LUCK) 컬럼을 포인트로 사용합니다.
    """
    if len(args) < 2:
        reply(status_id, f"@{user} 사용법: [양도/n포인트/캐릭터명]")
        return

    try:
        amount = int(args[0])
    except (ValueError, TypeError):
        reply(status_id, f"@{user} 양도할 포인트는 숫자로 입력해주세요. (예: [양도/100포인트/캐릭터명])")
        return

    recipient_name = args[1].strip()
    if not recipient_name:
        reply(status_id, f"@{user} 캐릭터명을 입력해주세요. 사용법: [양도/n포인트/캐릭터명]")
        return

    if amount <= 0:
        reply(status_id, f"@{user} 양도할 포인트는 1 이상이어야 합니다.")
        return

    # 1. 발신자/수신자 검증
    validation = _validate_transfer_parties(status_id, user, recipient_name)
    if validation is None:
        return
    sender, recipient = validation
    sender_name = sender.name

    # 2. 포인트 확인 (행운 컬럼 = 포인트)
    sender_points = sender.luck
    if sender_points < amount:
        reply(status_id, f"@{user} 포인트가 부족합니다. (보유: {sender_points})")
        return

    # 3. 포인트 이동
    sender_ok = update_stat(sender_name, ManagementColumns.LUCK, -amount)
    if not sender_ok:
        reply(status_id, f"@{user} 포인트 양도 처리에 실패했습니다. 나중에 다시 시도해주세요.")
        logger.command_error(
            user, f"양도/{amount}포인트/{recipient_name}", "스탯 업데이트 실패"
        )
        return

    recipient_ok = update_stat(recipient_name, ManagementColumns.LUCK, amount)
    if not recipient_ok:
        update_stat(sender_name, ManagementColumns.LUCK, amount)  # 롤백
        reply(status_id, f"@{user} 포인트 양도 처리에 실패했습니다. 나중에 다시 시도해주세요.")
        logger.command_error(
            user, f"양도/{amount}포인트/{recipient_name}", "스탯 업데이트 실패"
        )
        return

    # 4. 응답
    remaining = sender_points - amount
    response = (
        f"@{user} {amount}포인트를 {recipient_name}에게 양도했습니다!\n"
        f"남은 포인트: {remaining}"
    )
    reply(status_id, response)
    logger.command_response(
        user, f"양도/{amount}포인트/{recipient_name}", response
    )

    # 수신자 알림
    _notify_recipient_point(recipient, sender_name, amount)


def get_character_points(char_name: str) -> int:
    """캐릭터 포인트(행운) 조회.

    trashpit은 행운(LUCK)을 포인트로 사용합니다.
    """
    char = get_character_by_name(char_name)
    return int(char.luck) if char else 0


def _notify_recipient_item(
    recipient: Character, sender_name: str, item_name: str, dest: str
) -> None:
    """수신자에게 아이템 양도 알림 DM 전송"""
    recipient_id = recipient.mastodon_id
    if not recipient_id:
        return

    message = (
        f"@{recipient_id} {sender_name}님이 {item_name}을(를) 양도했습니다!\n"
        f"{dest}에서 확인하세요."
    )
    send_dm(message)


def _notify_recipient_point(
    recipient: Character, sender_name: str, amount: int
) -> None:
    """수신자에게 포인트 양도 알림 DM 전송"""
    recipient_id = recipient.mastodon_id
    if not recipient_id:
        return

    message = (
        f"@{recipient_id} {sender_name}님이 {amount}포인트를 양도했습니다!"
    )
    send_dm(message)
