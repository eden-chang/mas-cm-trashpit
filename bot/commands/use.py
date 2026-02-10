"""[사용/아이템명] 명령어 핸들러"""

import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.constants import ErrorMessages
from bot.services.use_item_service import use_item
from bot.utils.decorators import require_character
from bot.utils.locking import get_character_lock
from bot.utils.validation import validate_item_name
from bot.utils.korean import josa
from bot.logger import get_logger

logger = get_logger()


@require_character
def handle(status_id: str, user: str, character: Dict, args: List[str]) -> str:
    """아이템 사용 처리
    
    Args:
        status_id: 마스토돈 상태 ID
        user: 마스토돈 사용자 ID
        character: 캐릭터 정보 (데코레이터가 자동 주입)
        args: 명령어 인자 [아이템명]
        
    Returns:
        응답 메시지
    """
    # 1. 인자 검증
    if not args:
        return ErrorMessages.INVALID_ITEM_NAME.format(user=user, command="사용")
    
    item_name = args[0].strip()
    is_valid, error_msg = validate_item_name(item_name)
    if not is_valid:
        return f"@{user} {error_msg}"
    
    char_name = character['name']

    # 2. 비즈니스 로직 실행 (서비스 레이어) — 동시성 보호
    with get_character_lock(char_name):
        result = use_item(char_name, item_name)
    
    # 3. 결과에 따른 응답 메시지 반환
    if not result.success:
        if result.error_code == "ITEM_NOT_IN_INVENTORY":
            return ErrorMessages.ITEM_NOT_IN_INVENTORY.format(user=user, item_name=item_name)
        elif result.error_code == "ITEM_INFO_NOT_FOUND":
            return ErrorMessages.ITEM_INFO_NOT_FOUND.format(user=user, item_name=item_name)
        elif result.error_code == "ITEM_NOT_USABLE":
            return f"@{user} '{item_name}' 아이템은 명령어로 사용할 수 없습니다."
        elif result.error_code == "REMOVE_ITEM_FAILED":
            return ErrorMessages.SYSTEM_ERROR.format(user=user)
        elif result.error_code == "TRANSACTION_FAILED":
            return ErrorMessages.TRANSACTION_ERROR.format(user=user)
        elif result.error_code == "UNEXPECTED_ERROR":
            return ErrorMessages.DB_ERROR.format(user=user)
        else:
            return ErrorMessages.DB_ERROR.format(user=user)
    
    # 4. 성공 응답 메시지 생성
    if result.effect_message:
        lines = [result.effect_message]
    else:
        lines = [f"{josa(item_name, '을/를')} 사용했습니다."]

    lines.append("")
    lines.append(f"- {item_name} 사용")

    if result.applied_delta is not None and result.stat_display:
        sign = "+" if result.applied_delta >= 0 else ""
        lines.append(f"- {result.stat_display} {result.dice_expression} = {sign}{result.applied_delta}")
        if result.new_stat_value is not None:
            lines.append(f"- 현재 {result.stat_display} {result.new_stat_value}")

    if result.remaining_count > 0:
        lines.append(f"- 남은 수량 {result.remaining_count}개")

    return "\n".join(lines)
