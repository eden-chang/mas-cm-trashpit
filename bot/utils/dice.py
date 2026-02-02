"""다이스 굴림 유틸리티

문서 2.3 - 사용 명령어 스펙에 따른 다이스 표기법 처리.
지원 형식: 정수, ndm, ndm+k, ndm-k, -(ndm+k)
"""

import random
import re


def is_dice_expression(value_str: str) -> bool:
    """주사위 표현식 여부 (1d6, 2d6+3, -(1d6+3) 등)."""
    if not value_str or not isinstance(value_str, str):
        return False
    value_str = value_str.strip()
    if value_str.startswith("-(") and value_str.endswith(")"):
        inner = value_str[2:-1]
        return bool(re.match(r"^\d+[dD]\d+([+\-]\d+)?$", inner))
    return bool(re.match(r"^\d+[dD]\d+([+\-]\d+)?$", value_str))


def roll_dice(dice_str: str) -> int:
    """다이스 표기법 처리

    지원 형식:
    - 정수: '10', '-5'
    - ndm: '1d6', '2d10'
    - ndm+k: '1d6+3', '2d6-2'
    - -(ndm+k): '-(1d6+3)', '-2d6'

    Args:
        dice_str: 다이스 표현식 또는 정수 문자열

    Returns:
        굴림 결과 (정수)
    """
    if not dice_str or not str(dice_str).strip():
        return 0

    dice_str = str(dice_str).strip()

    # 정수인 경우
    try:
        return int(dice_str)
    except ValueError:
        pass

    # 음수 다이스: -(ndm+k) 형태
    negative = False
    if dice_str.startswith("-(") and dice_str.endswith(")"):
        negative = True
        dice_str = dice_str[2:-1].strip()
    elif dice_str.startswith("-") and not dice_str[1:2].isdigit():
        negative = True
        dice_str = dice_str[1:].strip()

    # ndm+k 또는 ndm-k 파싱
    match = re.match(r"(\d+)d(\d+)([+-]\d+)?", dice_str, re.IGNORECASE)
    if match:
        n = int(match.group(1))
        m = int(match.group(2))
        k = int(match.group(3) or 0)
        total = sum(random.randint(1, m) for _ in range(n)) + k
        return -total if negative else total

    return 0
