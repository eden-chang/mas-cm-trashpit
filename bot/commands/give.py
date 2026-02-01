"""[양도/...] 명령어 핸들러"""

import sys

sys.path.insert(0, str(__file__).rsplit("\\", 3)[0])

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
    add_to_misc,
    update_stat,
)
from shared.constants import ManagementColumns

logger = get_logger()


def handle_item(status_id: str, user: str, args: list):
    """
    아이템 양도 처리

    1. 보내는 캐릭터 조회
    2. 받는 캐릭터 조회
    3. 아이템 보유 확인
    4. 아이템 이동
    5. 결과 응답
    """
    item_name = args[0].strip()
    recipient_name = args[1].strip()

    # 보내는 캐릭터 조회
    sender = get_character_by_mastodon_id(user)
    if not sender:
        reply(status_id, f"@{user} 등록된 캐릭터를 찾을 수 없습니다.")
        return

    sender_name = sender.name

    # 받는 캐릭터 조회
    recipient = get_character_by_name(recipient_name)
    if not recipient:
        reply(status_id, f"@{user} '{recipient_name}' 캐릭터를 찾을 수 없습니다.")
        return

    # 자기 자신에게 양도 방지
    if sender_name == recipient_name:
        reply(status_id, f"@{user} 자기 자신에게는 양도할 수 없습니다.")
        return

    # 아이템 위치 확인
    location = find_item_location(sender_name, item_name)
    if not location:
        reply(status_id, f"@{user} '{item_name}'을(를) 소지하고 있지 않습니다.")
        return

    # 아이템 정보 확인
    item_info = get_item_info(item_name)
    if not item_info:
        reply(status_id, f"@{user} '{item_name}' 정보를 찾을 수 없습니다.")
        return

    # 발신자에서 제거
    if not remove_from_location(sender_name, item_name, 1, location):
        reply(status_id, f"@{user} 아이템 양도 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
        return

    # 수신자에게 추가
    if item_info.volume == 0:
        add_to_misc(recipient_name, item_name, 1)
        dest = "여유공간"
    else:
        add_to_nearby(recipient_name, item_name, 1)
        dest = "주변"

    # 응답
    response = f"@{user} {item_name}을(를) {recipient_name}에게 양도했습니다!"
    reply(status_id, response)
    logger.command_response(user, f"양도/{item_name}/{recipient_name}", response)

    # 수신자에게 알림
    recipient_id = recipient.mastodon_id
    if recipient_id:
        notify_message = (
            f"@{recipient_id} {sender_name}님이 {item_name}을(를) 양도했습니다!\n"
            f"{dest}에서 확인하세요."
        )
        send_dm(notify_message)


def handle_point(status_id: str, user: str, args: list):
    """
    포인트 양도 처리

    1. 보내는 캐릭터 조회
    2. 받는 캐릭터 조회
    3. 포인트 잔액 확인
    4. 포인트 이동
    5. 결과 응답
    """
    amount = int(args[0])
    recipient_name = args[1].strip()

    # 유효성 검사
    if amount <= 0:
        reply(status_id, f"@{user} 양도할 포인트는 1 이상이어야 합니다.")
        return

    # 보내는 캐릭터 조회
    sender = get_character_by_mastodon_id(user)
    if not sender:
        reply(status_id, f"@{user} 등록된 캐릭터를 찾을 수 없습니다.")
        return

    sender_name = sender.name

    # 받는 캐릭터 조회
    recipient = get_character_by_name(recipient_name)
    if not recipient:
        reply(status_id, f"@{user} '{recipient_name}' 캐릭터를 찾을 수 없습니다.")
        return

    # 자기 자신에게 양도 방지
    if sender_name == recipient_name:
        reply(status_id, f"@{user} 자기 자신에게는 양도할 수 없습니다.")
        return

    # 포인트 확인 (행운을 포인트로 사용)
    sender_points = sender.luck
    if sender_points < amount:
        reply(status_id, f"@{user} 포인트가 부족합니다. (보유: {sender_points})")
        return

    # 포인트 이동
    update_stat(sender_name, ManagementColumns.LUCK, -amount)
    update_stat(recipient_name, ManagementColumns.LUCK, amount)

    # 응답
    remaining = sender_points - amount
    response = (
        f"@{user} {amount}포인트를 {recipient_name}에게 양도했습니다!\n"
        f"남은 포인트: {remaining}"
    )
    reply(status_id, response)
    logger.command_response(user, f"양도/{amount}포인트/{recipient_name}", response)

    # 수신자 알림
    recipient_id = recipient.mastodon_id
    if recipient_id:
        notify_message = (
            f"@{recipient_id} {sender_name}님이 {amount}포인트를 양도했습니다!"
        )
        send_dm(notify_message)
