from functools import wraps
from typing import Callable, Any
from bot.mastodon_client import reply
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
            reply(status_id, f"@{user} 🚫 시스템 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.\n(Error: {str(e)})")
    return wrapper

def validate_args(min_args: int, usage: str) -> Callable:
    """인자 개수 검증 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(status_id: str, user: str, args: list[str], *extra_args, **kwargs) -> Any:
            if not args or len(args) < min_args or not all(arg.strip() for arg in args[:min_args]):
                reply(status_id, f"@{user} ❌ 형식이 잘못되었습니다.\n사용법: {usage}")
                return
            return func(status_id, user, args, *extra_args, **kwargs)
        return wrapper
    return decorator
