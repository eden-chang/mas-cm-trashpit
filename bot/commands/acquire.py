"""[획득/아이템명] 명령어 핸들러"""

import sys
import os

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

from bot.services.character_service import get_character_by_mastodon_id
from bot.services.item_service import get_item_info
from bot.services.inventory_service import add_item

def handle(status_id: str, user: str, args: list) -> str:
    """
    아이템 획득 처리
    Returns: 응답 메시지 (mocking을 위해 return 처리, 실제 봇은 reply 호출)
    """
    if not args:
        return f"@{user} 사용법: [획득/아이템명]"

    item_name = args[0].strip()
    if not item_name:
        return f"@{user} 아이템명을 입력해주세요. 사용법: [획득/아이템명]"

    # 1. 캐릭터 조회
    character = get_character_by_mastodon_id(user)
    if not character:
        return f"@{user} 등록된 캐릭터를 찾을 수 없습니다."

    char_name = character['name']

    # 2. 아이템 정보 조회
    item_info = get_item_info(item_name)
    if not item_info:
        return f"@{user} '{item_name}'은(는) 존재하지 않는 아이템입니다."

    volume = item_info['volume']

    # 3. 추가 (부피 0 -> 여유공간 / 부피 > 0 -> 주변)
    target_location = 'misc' if volume == 0 else 'nearby'
    
    if add_item(char_name, item_name, 1, target_location):
        if volume == 0:
            return (f"@{user} {item_name}을(를) 획득했습니다! (부피 0)\n"
                    f"자동으로 여유공간에 보관되었습니다.")
        else:
            return (f"@{user} {item_name}을(를) 획득했습니다! (부피: {volume})\n"
                    f"주변에 임시 보관됩니다.")
    else:
        return f"@{user} '{item_name}' 획득 처리에 실패했습니다. (시스템 오류)"
