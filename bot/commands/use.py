"""[사용/아이템명] 명령어 핸들러"""

import sys
import os

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from bot.services.character_service import get_character_by_mastodon_id
from bot.services.item_service import get_item_info
from bot.services.inventory_service import remove_item, find_item_location, get_item_count

def handle(status_id: str, user: str, args: list) -> str:
    """아이템 사용 처리"""
    if not args:
        return f"@{user} 사용법: [사용/아이템명]"

    item_name = args[0].strip()
    
    # 1. 캐릭터 조회
    character = get_character_by_mastodon_id(user)
    if not character:
        return f"@{user} 등록된 캐릭터를 찾을 수 없습니다."
    
    char_name = character['name']

    # 2. 소지 여부 확인
    location = find_item_location(char_name, item_name)
    if not location:
        return f"@{user} '{item_name}'을(를) 소지하고 있지 않습니다."

    # 3. 아이템 정보 조회
    item_info = get_item_info(item_name)
    if not item_info:
        return f"@{user} '{item_name}' 정보를 찾을 수 없습니다."

    # 4. 사용 (차감)
    # TODO: 효과 적용 로직은 아직 구현 안 됨 (Phase 2 범위 밖일 수도 있음, 일단 차감만)
    if remove_item(char_name, item_name, 1, location):
        remaining = get_item_count(char_name, item_name)
        effect_msg = item_info['use_msg'] or f"효과: {item_info['stat']} {item_info['value']}"
        
        msg = f"@{user} {item_name}을(를) 사용했습니다!\n{effect_msg}"
        if remaining > 0:
            msg += f"\n(남은 수량: {remaining})"
        return msg
    else:
        return f"@{user} 사용 처리에 실패했습니다."
