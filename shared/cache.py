"""캐싱 유틸리티 (Phase 3.3)

공통 캐싱 레이어. 시트 API 호출을 줄이기 위한 TTL 기반 메모리 캐시.
"""

import os
import time
import logging
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# 기본 캐시 TTL (초)
CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))  # 1분
CACHE_TTL_ITEMS = int(os.getenv("CACHE_TTL_ITEMS", "300"))  # 아이템은 5분
CACHE_TTL_CHARACTERS = int(os.getenv("CACHE_TTL_CHARACTERS", "30"))  # 캐릭터는 30초

# 메모리 캐시 저장소
_cache: dict[str, tuple[Any, float]] = {}


def cached(ttl: int = CACHE_TTL) -> Callable:
    """TTL 기반 캐시 데코레이터

    Args:
        ttl: 캐시 유효 시간(초)

    Usage:
        @cached(ttl=60)
        def get_character_by_name(name: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            key = _make_cache_key(func.__name__, args, kwargs)

            # 캐시 히트 확인
            if key in _cache:
                value, timestamp = _cache[key]
                if time.time() - timestamp < ttl:
                    logger.debug("Cache hit: %s", key)
                    return value

            # 캐시 미스 - 실제 함수 호출
            logger.debug("Cache miss: %s", key)
            result = func(*args, **kwargs)
            _cache[key] = (result, time.time())
            return result

        # 캐시 우회 메서드 추가
        wrapper.uncached = func
        wrapper.invalidate = lambda *a, **kw: invalidate_cache(
            _make_cache_key(func.__name__, a, kw)
        )
        return wrapper

    return decorator


def _make_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """캐시 키 생성"""
    # 간단한 문자열 키 생성
    args_str = str(args) if args else ""
    kwargs_str = str(sorted(kwargs.items())) if kwargs else ""
    return f"{func_name}:{args_str}:{kwargs_str}"


def invalidate_cache(pattern: Optional[str] = None) -> int:
    """캐시 무효화

    Args:
        pattern: 삭제할 키 패턴. None이면 전체 삭제.

    Returns:
        삭제된 캐시 항목 수
    """
    global _cache

    if pattern is None:
        count = len(_cache)
        _cache = {}
        logger.info("전체 캐시 무효화: %d건", count)
        return count

    # 패턴 매칭 삭제
    keys_to_delete = [k for k in _cache if pattern in k]
    for key in keys_to_delete:
        del _cache[key]

    if keys_to_delete:
        logger.info("캐시 무효화 (%s): %d건", pattern, len(keys_to_delete))

    return len(keys_to_delete)


def invalidate_character_cache(char_name: str) -> None:
    """특정 캐릭터 관련 캐시 무효화"""
    invalidate_cache(f"get_character_by_name:('{char_name}'")
    invalidate_cache("get_character_by_mastodon_id:")  # ID 캐시도 무효화 (패턴 매칭)
    invalidate_cache("get_all_characters")


def get_cache_stats() -> dict:
    """캐시 통계 반환"""
    now = time.time()
    total = len(_cache)
    expired = sum(1 for _, (_, ts) in _cache.items() if now - ts > CACHE_TTL)

    return {
        "total_entries": total,
        "expired_entries": expired,
        "active_entries": total - expired,
    }


def cleanup_expired() -> int:
    """만료된 캐시 정리

    TODO: 주니어 - 주기적으로 호출하는 백그라운드 태스크 구현
    """
    global _cache
    now = time.time()
    initial_count = len(_cache)

    # TTL이 가장 긴 값 기준으로 정리 (보수적)
    max_ttl = max(CACHE_TTL, CACHE_TTL_ITEMS, CACHE_TTL_CHARACTERS)
    _cache = {k: v for k, v in _cache.items() if now - v[1] < max_ttl}

    cleaned = initial_count - len(_cache)
    if cleaned:
        logger.info("만료 캐시 정리: %d건", cleaned)

    return cleaned
