"""Phase 3.3 캐시 동작 테스트"""

import time
import pytest
from unittest.mock import patch

from shared.cache import (
    cached,
    invalidate_cache,
    invalidate_character_cache,
    get_cache_stats,
    cleanup_expired,
    _make_cache_key,
)


def _clear_cache() -> None:
    """테스트 간 캐시 초기화"""
    invalidate_cache()


class TestCachedDecorator:
    """TTL 기반 캐시 데코레이터"""

    def setup_method(self) -> None:
        _clear_cache()

    def test_cache_hit_returns_cached_value(self) -> None:
        call_count = 0

        @cached(ttl=60)
        def get_value(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        assert get_value(5) == 10
        assert get_value(5) == 10
        assert call_count == 1

    def test_cache_miss_calls_function(self) -> None:
        call_count = 0

        @cached(ttl=60)
        def get_value(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        assert get_value(1) == 1
        assert get_value(2) == 2
        assert call_count == 2

    def test_ttl_expiration(self) -> None:
        call_count = 0

        @cached(ttl=1)
        def get_value() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        assert get_value() == 1
        assert get_value() == 1
        time.sleep(1.1)
        assert get_value() == 2

    def test_uncached_bypasses_cache(self) -> None:
        call_count = 0

        @cached(ttl=60)
        def get_value() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        assert get_value() == 1
        assert get_value() == 1
        assert get_value.uncached() == 2
        assert get_value.uncached() == 3


class TestInvalidateCache:
    """캐시 무효화"""

    def setup_method(self) -> None:
        _clear_cache()

    def test_invalidate_all_clears_cache(self) -> None:
        @cached(ttl=60)
        def get_value() -> int:
            return 42

        get_value()
        stats = get_cache_stats()
        assert stats["total_entries"] == 1

        count = invalidate_cache()
        assert count == 1

        stats = get_cache_stats()
        assert stats["total_entries"] == 0

    def test_invalidate_pattern_removes_matching_keys(self) -> None:
        @cached(ttl=60)
        def get_a() -> int:
            return 1

        @cached(ttl=60)
        def get_b() -> int:
            return 2

        get_a()
        get_b()

        count = invalidate_cache("get_a")
        assert count == 1

        assert get_a.uncached() == 1
        stats = get_cache_stats()
        assert stats["total_entries"] == 1


class TestInvalidateCharacterCache:
    """캐릭터 관련 캐시 무효화"""

    def setup_method(self) -> None:
        _clear_cache()

    def test_invalidate_character_removes_related_entries(self) -> None:
        @cached(ttl=60)
        def get_character_by_name(name: str) -> str:
            return f"char_{name}"

        get_character_by_name("발트")
        get_character_by_name("스카이")

        invalidate_character_cache("발트")

        stats = get_cache_stats()
        assert "get_character_by_name:('발트'" not in str(stats)


class TestGetCacheStats:
    """캐시 통계"""

    def setup_method(self) -> None:
        _clear_cache()

    def test_empty_cache_stats(self) -> None:
        stats = get_cache_stats()
        assert stats["total_entries"] == 0
        assert stats["active_entries"] == 0

    def test_stats_reflect_cached_entries(self) -> None:
        @cached(ttl=60)
        def get_value() -> int:
            return 1

        get_value()
        get_value()

        stats = get_cache_stats()
        assert stats["total_entries"] == 1


class TestCleanupExpired:
    """만료 캐시 정리"""

    def setup_method(self) -> None:
        _clear_cache()

    def test_cleanup_removes_expired_entries(self) -> None:
        """cleanup_expired는 max_ttl 기준으로 만료 항목 제거. TTL=1인 항목은 1초 후 만료."""
        with patch("shared.cache.CACHE_TTL", 1), patch(
            "shared.cache.CACHE_TTL_ITEMS", 1
        ), patch("shared.cache.CACHE_TTL_CHARACTERS", 1):
            @cached(ttl=1)
            def get_value() -> int:
                return 1

            get_value()
            time.sleep(1.1)

            cleaned = cleanup_expired()
            assert cleaned >= 1


class TestMakeCacheKey:
    """캐시 키 생성"""

    def test_key_includes_func_name_and_args(self) -> None:
        key = _make_cache_key("get_char", ("발트",), {})
        assert "get_char" in key
        assert "발트" in key
