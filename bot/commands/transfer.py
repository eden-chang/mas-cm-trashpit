"""[양도/아이템명/받는사람] 명령어 핸들러"""

import sys
import os

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from bot.services.character_service import get_character_by_mastodon_id, get_character
from bot.services.item_service import get_item_info
from bot.services.inventory_service import remove_item, add_item, find_item_location

def handle_item(status_id: str, user: str, args: list) -> str:
    """아이템 양도"""
    if len(args) < 2:
        return f"@{user} 사용법: [양도/아이템명/받는사람이름]"

    item_name = args[0].strip()
    target_name = args[1].strip()

    # 1. 보내는 사람 조회
    sender = get_character_by_mastodon_id(user)
    if not sender:
        return f"@{user} 등록된 캐릭터를 찾을 수 없습니다."
    
    sender_char_name = sender['name']

    # 2. 받는 사람 조회
    receiver = get_character(target_name)
    if not receiver:
        return f"@{user} 받는 사람 '{target_name}'을(를) 찾을 수 없습니다."

    # 3. 아이템 소지 확인
    location = find_item_location(sender_char_name, item_name)
    if not location:
        return f"@{user} '{item_name}'을(를) 가지고 있지 않습니다."

    # 4. 아이템 정보 (부피 확인용)
    item_info = get_item_info(item_name)
    if not item_info:
        return f"@{user} 아이템 정보를 찾을 수 없습니다."

    # 5. 이동 (Sender 제거 -> Receiver 추가)
    if remove_item(sender_char_name, item_name, 1, location):
        target_loc = 'misc' if item_info['volume'] == 0 else 'nearby'
        if add_item(target_name, item_name, 1, target_loc):
            return (f"@{user} '{item_name}'을(를) {target_name}에게 보냈습니다.\n"
                    f"(수신자는 '{'여유공간' if target_loc == 'misc' else '주변'}'을 확인하세요)")
        else:
            # 롤백 시도 (보낸 사람에게 다시 추가)
            add_item(sender_char_name, item_name, 1, location)
            return f"@{user} 양도 실패: 수신자에게 아이템을 추가할 수 없습니다."
    else:
        return f"@{user} 양도 실패: 아이템 차감 중 오류 발생."

def handle_point(status_id: str, user: str, args: list) -> str:
    return f"@{user} 포인트 양도 기능은 아직 구현되지 않았습니다."
