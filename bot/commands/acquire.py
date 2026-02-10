"""[획득/아이템명] 명령어 핸들러"""

import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.services.item_service import get_item_info
from bot.services.inventory_service import add_item, get_available_space
from bot.utils.decorators import require_character
from bot.utils.validation import validate_item_name
from bot.utils.korean import josa
from bot.logger import get_logger
from shared.constants import (
    InventoryLocation,
    ZERO_VOLUME_THRESHOLD,
    ErrorMessages,
)

logger = get_logger()

try:
    from postgrest.exceptions import APIError as PostgrestAPIError
except ImportError:
    PostgrestAPIError = None  # type: ignore[misc, assignment]

_ACQUIRE_HANDLED_EXCEPTIONS: tuple = (ConnectionError, OSError)
if PostgrestAPIError is not None:
    _ACQUIRE_HANDLED_EXCEPTIONS = _ACQUIRE_HANDLED_EXCEPTIONS + (PostgrestAPIError,)


@require_character
def handle(status_id: str, user: str, character: Dict, args: List[str]) -> str:
    """아이템 획득 처리
    
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
        return ErrorMessages.INVALID_ITEM_NAME.format(user=user, command="획득")
    
    item_name = args[0].strip()
    is_valid, error_msg = validate_item_name(item_name)
    if not is_valid:
        return f"@{user} {error_msg}"
    
    char_name = character['name']
    
    try:
        # 2. 아이템 정보 조회
        item_info = get_item_info(item_name)
        if not item_info:
            return ErrorMessages.ITEM_NOT_FOUND.format(user=user, item_name=item_name)
        
        volume = item_info['volume']
        
        # 3. 추가 (부피 0 -> 여유공간 / 부피 > 0 -> 주변)
        target_location = (
            InventoryLocation.MISC 
            if volume == ZERO_VOLUME_THRESHOLD 
            else InventoryLocation.NEARBY
        )
        
        # 4. 인벤토리에 추가
        if not add_item(char_name, item_name, 1, target_location):
            logger.command_error(user, "획득", f"add_item 실패: {item_name}")
            return ErrorMessages.SYSTEM_ERROR.format(user=user)
        
        # 5. 성공 응답 생성
        available = get_available_space(char_name)
        
        if volume == ZERO_VOLUME_THRESHOLD:
            return (
                f"@{user} {josa(item_name, '을/를')} 획득했습니다! (부피 0)\n"
                f"자동으로 여유공간에 보관되었습니다.\n"
                f"가방 남은 공간: {available}칸"
            )

        return (
            f"@{user} {josa(item_name, '을/를')} 획득했습니다! (부피: {volume})\n"
            f"가방 남은 공간: {available}칸\n"
            f"웹에서 가방에 넣으세요."
        )
        
    except _ACQUIRE_HANDLED_EXCEPTIONS as e:
        logger.command_error(user, "획득", f"예외 발생: {type(e).__name__}: {e}", exc_info=False)
        return ErrorMessages.DB_ERROR.format(user=user)
    except Exception as e:
        logger.command_error(user, "획득", f"예외 발생: {e}", exc_info=True)
        return ErrorMessages.DB_ERROR.format(user=user)
