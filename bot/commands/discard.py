"""[버리기/아이템명] 명령어 핸들러"""

import sys
import os

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from bot.services.character_service import get_character_by_mastodon_id
from bot.services.inventory_service import remove_item, find_item_location

def handle(status_id: str, user: str, args: list) -> str:
    """아이템 버리기"""
    if not args:
        return f"@{user} 사용법: [버리기/아이템명]"

    item_name = args[0].strip()

    # 1. 캐릭터 조회
    character = get_character_by_mastodon_id(user)
    if not character:
        return f"@{user} 등록된 캐릭터를 찾을 수 없습니다."
    
    char_name = character['name']

    # 2. 소지 확인
    location = find_item_location(char_name, item_name)
    if not location:
        return f"@{user} '{item_name}'을(를) 가지고 있지 않습니다."

    # 3. 삭제
    if remove_item(char_name, item_name, 1, location):
        return f"@{user} '{item_name}'을(를) 버렸습니다."
    else:
        return f"@{user} 버리기 실패 (시스템 오류)"
