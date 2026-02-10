"""한국어 조사 자동 처리 유틸리티"""


def has_batchim(word: str) -> bool:
    """마지막 글자에 받침이 있는지 판단.

    한글 유니코드: (code - 0xAC00) % 28 != 0 이면 받침 있음.
    숫자로 끝나는 경우: 0,1,3,6,7,8 → 받침 있음.
    영문/기타: 받침 없는 것으로 간주.
    """
    if not word:
        return False

    last = word.rstrip()[-1]

    # 한글 완성형 (가 ~ 힣)
    if '\uAC00' <= last <= '\uD7A3':
        return (ord(last) - 0xAC00) % 28 != 0

    # 숫자
    if last.isdigit():
        return last in ('0', '1', '3', '6', '7', '8')

    # 영문/기타 → 받침 없음으로 간주
    return False


def josa(word: str, particles: str) -> str:
    """word에 맞는 조사를 붙여 반환.

    particles: 슬래시로 구분된 두 형태.
      - 받침 있을 때 / 받침 없을 때 순서.
      - 예: "을/를", "이/가", "은/는", "과/와"

    Examples:
        josa("사과", "을/를") → "사과를"
        josa("사이다", "을/를") → "사이다를"
        josa("빵", "이/가") → "빵이"
        josa("사과", "이/가") → "사과가"
    """
    parts = particles.split("/")
    if len(parts) != 2:
        return word + particles

    with_batchim, without_batchim = parts
    suffix = with_batchim if has_batchim(word) else without_batchim
    return word + suffix
