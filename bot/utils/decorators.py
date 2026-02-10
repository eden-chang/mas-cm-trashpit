from functools import wraps
from typing import Callable, Any, List, Dict, Optional
from bot.logger import get_logger

logger = get_logger()

def handle_error(func: Callable) -> Callable:
    """명령어 핸들러용 에러 처리 데코레이터"""
    @wraps(func)
    def wrapper(status_id: str, user: str, args: list[str], *extra_args, **kwargs) -> Any:
        try:
            return func(status_id, user, args, *extra_args, **kwargs)
        except Exception as e:
            logger.error(f"Command Error ({func.__name__}): {e}", exc_info=True)
            reply(status_id, f"@{user} 시스템 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.\n(Error: {str(e)})")
    return wrapper

def validate_args(min_args: int, usage: str) -> Callable:
    """인자 개수 검증 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(status_id: str, user: str, args: list[str], *extra_args, **kwargs) -> Any:
            if not args or len(args) < min_args or not all(arg.strip() for arg in args[:min_args]):
                from bot.mastodon_client import reply
                reply(status_id, f"@{user} 형식이 잘못되었습니다.\n사용법: {usage}")
                return
            return func(status_id, user, args, *extra_args, **kwargs)
        return wrapper
    return decorator


def require_character(func: Callable) -> Callable:
    """캐릭터 조회를 자동으로 수행하는 데코레이터
    
    마스토돈 ID로 캐릭터를 조회하고, 찾지 못하면 에러 메시지를 반환합니다.
    성공 시 character 인자를 추가하여 핸들러 함수를 호출합니다.
    
    Usage:
        @require_character
        def handle(status_id: str, user: str, character: Dict, args: List[str]) -> str:
            char_name = character['name']
            ...
    """
    @wraps(func)
    def wrapper(status_id: str, user: str, args: List[str]) -> str:
        from bot.services.character_service import get_character_by_mastodon_id, CharacterServiceError
        from shared.constants import ErrorMessages

        try:
            character = get_character_by_mastodon_id(user)
            if not character:
                return ErrorMessages.CHARACTER_NOT_FOUND.format(user=user)

            return func(status_id, user, character, args)
        except CharacterServiceError as e:
            logger.command_error(user, func.__name__, f"캐릭터 조회 시스템 오류: {e}")
            return f"@{user} 시스템 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
        except Exception as e:
            logger.command_error(user, func.__name__, f"캐릭터 조회 실패: {e}", exc_info=True)
            return ErrorMessages.DB_ERROR.format(user=user)
    
    return wrapper
