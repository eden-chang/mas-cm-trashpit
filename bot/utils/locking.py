"""캐릭터별 공유 락 유틸리티 — 모든 명령(구매/양도/사용)이 동일 Lock 인스턴스를 공유."""

import threading

_character_locks: dict[str, threading.Lock] = {}
_character_locks_guard = threading.Lock()


def get_character_lock(char_name: str) -> threading.Lock:
    """캐릭터 이름에 해당하는 Lock을 반환한다.

    동일 캐릭터에 대해 항상 같은 Lock 인스턴스를 반환하므로,
    buy / transfer / use 등 여러 명령 간 경쟁 조건을 방지할 수 있다.
    """
    with _character_locks_guard:
        if char_name not in _character_locks:
            _character_locks[char_name] = threading.Lock()
        return _character_locks[char_name]
