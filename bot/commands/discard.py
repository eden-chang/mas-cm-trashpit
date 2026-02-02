"""[버리기/아이템명] 명령어 핸들러"""

import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.services.inventory_service import remove_item, find_item_location
from bot.utils.decorators import require_character
from bot.utils.validation import validate_item_name
from bot.logger import get_logger
from shared.constants import ErrorMessages

logger = get_logger()

try:
    from postgrest.exceptions import APIError as PostgrestAPIError
except ImportError:
    PostgrestAPIError = None  # type: ignore[misc, assignment]

_DISCARD_HANDLED_EXCEPTIONS: tuple = (ConnectionError, OSError)
if PostgrestAPIError is not None:
    _DISCARD_HANDLED_EXCEPTIONS = _DISCARD_HANDLED_EXCEPTIONS + (PostgrestAPIError,)


@require_character
def handle(status_id: str, user: str, character: Dict, args: List[str]) -> str:
    """아이템 버리기
    
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
        return ErrorMessages.INVALID_ITEM_NAME.format(user=user, command="버리기")
    
    item_name = args[0].strip()
    is_valid, error_msg = validate_item_name(item_name)
    if not is_valid:
        return f"@{user} {error_msg}"
    
    char_name = character['name']
    
    try:
        # 2. 소지 확인
        location = find_item_location(char_name, item_name)
        if not location:
            return ErrorMessages.ITEM_NOT_IN_INVENTORY.format(user=user, item_name=item_name)
        
        # 3. 삭제
        if not remove_item(char_name, item_name, 1, location):
            logger.command_error(user, "버리기", f"remove_item 실패: {item_name}")
            return ErrorMessages.SYSTEM_ERROR.format(user=user)
        
        return f"@{user} '{item_name}'을(를) 버렸습니다."
        
    except _DISCARD_HANDLED_EXCEPTIONS as e:
        logger.command_error(user, "버리기", f"예외 발생: {type(e).__name__}: {e}", exc_info=False)
        return ErrorMessages.DB_ERROR.format(user=user)
    except Exception as e:
        logger.command_error(user, "버리기", f"예외 발생: {e}", exc_info=True)
        return ErrorMessages.DB_ERROR.format(user=user)
