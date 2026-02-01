"""[사용/아이템명] 명령어 핸들러"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.constants import ManagementColumns
from bot.services.character_service import get_character_by_mastodon_id
from bot.services.item_service import get_item_info
from bot.services.inventory_service import (
    remove_item,
    find_item_location,
    get_item_count,
    update_stat,
)
from bot.utils.dice import roll_dice

# 아이템 스탯명 -> 관리 시트 컬럼 인덱스
_STAT_COLUMN = {
    "체력": ManagementColumns.HEALTH,
    "근력": ManagementColumns.STRENGTH,
    "행운": ManagementColumns.LUCK,
}

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

    # 4. 사용 (차감 후 효과 적용, 다이스 표현식 지원)
    if remove_item(char_name, item_name, 1, location):
        applied_delta: Optional[int] = None
        stat_col = _STAT_COLUMN.get((item_info.get("stat") or "").strip())
        value_raw = item_info.get("value")
        if stat_col is not None and value_raw not in (None, ""):
            delta = roll_dice(str(value_raw).strip())
            if delta != 0:
                update_stat(char_name, stat_col, delta)
                applied_delta = delta
        remaining = get_item_count(char_name, item_name)
        stat_name = (item_info.get("stat") or "").strip()
        if applied_delta is not None and stat_name:
            effect_msg = item_info.get("use_msg") or f"효과: {stat_name} {applied_delta:+d}"
        else:
            effect_msg = item_info.get("use_msg") or f"효과: {stat_name} {item_info.get('value', '')}"
        msg = f"@{user} {item_name}을(를) 사용했습니다!\n{effect_msg}"
        if remaining > 0:
            msg += f"\n(남은 수량: {remaining})"
        return msg
    else:
        return f"@{user} 사용 처리에 실패했습니다."
