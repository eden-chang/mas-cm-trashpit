"""전투 관련 공통 유틸리티 — 진영·근력 기반 데미지 계산"""

import random
from typing import Dict, Literal, Optional, Tuple

FACTION_WEGA = "wega"
FACTION_SKY = "sky"

FACTION_ALIASES: Dict[str, str] = {
    "웨가": FACTION_WEGA,
    "wega": FACTION_WEGA,
    "vega": FACTION_WEGA,
    "베가": FACTION_WEGA,
    "스카이": FACTION_SKY,
    "sky": FACTION_SKY,
}


def normalize_faction(faction: str) -> Optional[str]:
    """진영 문자열을 표준값(wega/sky)으로 정규화."""
    normalized = (faction or "").lower().replace(" ", "")
    return FACTION_ALIASES.get(normalized) if normalized else None


def _parse_int_safe(raw: object, default: int = 0) -> int:
    """원시 값을 안전하게 정수로 파싱. 실패 시 default 반환."""
    if raw is None:
        return default
    try:
        s = str(raw).strip()
        if not s:
            return default
        return max(0, int(float(s)))
    except (ValueError, TypeError):
        return default


def parse_stat(character: dict, key: str, default: int = 0) -> int:
    """
    캐릭터 dict에서 스탯 값을 안전하게 파싱.

    Args:
        character: 캐릭터 딕셔너리
        key: 스탯 키 (strength, health, luck, points, hp 등)
        default: 파싱 실패 시 반환값

    Returns:
        파싱된 정수 (0 이상)
    """
    raw = character.get(key, default) or default
    return _parse_int_safe(raw, default)


def parse_stat_optional(
    character: dict, key: str
) -> Tuple[Optional[int], Optional[str]]:
    """
    필수 스탯 파싱. None/빈값과 파싱 실패를 구분.

    Returns:
        (value, error_type): 성공 시 (int, None), 실패 시 (None, "missing"|"invalid")
    """
    raw = character.get(key)
    if raw is None or str(raw).strip() == "":
        return (None, "missing")
    try:
        return (max(0, int(float(str(raw).strip()))), None)
    except (ValueError, TypeError):
        return (None, "invalid")


def parse_strength(character: dict) -> int:
    """캐릭터 dict에서 근력 값을 안전하게 파싱."""
    return parse_stat(character, "strength", 0)


def compute_damage(
    normalized_faction: str,
    strength: int,
    user_name: str,
    action: Literal["attack", "shoot"],
) -> str:
    """
    진영·근력에 따른 데미지 계산 및 메시지 생성.

    웨가: 근력×10 + 랜덤(40~80)
    스카이: 60 + 랜덤(20~60)
    """
    action_label = "공격" if action == "attack" else "발사"

    if normalized_faction == FACTION_WEGA:
        dice_roll = random.randint(40, 80)
        total_damage = strength * 10 + dice_roll
        return (
            f"웨이스트 가드 {user_name}의 {action_label}\n"
            f"근력[{strength}] × 10 + 랜덤값[{dice_roll}] = 도합 {total_damage} 데미지"
        )
    else:
        dice_roll = random.randint(20, 60)
        total_damage = 60 + dice_roll
        return (
            f"스카이 스크래퍼 {user_name}의 {action_label}\n"
            f"기본값[60] + 랜덤값[{dice_roll}] = 도합 {total_damage} 데미지"
        )
