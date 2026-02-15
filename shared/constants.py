"""상수 정의

Supabase 마이그레이션 완료. 일부 상수는 레거시 호환용으로 유지.
"""

from enum import IntEnum
from typing import Final

# ============================================================
# DEPRECATED: Google Sheets 레거시 상수
# 아래 상수들은 더 이상 사용되지 않습니다.
# ============================================================

# DEPRECATED: 시트 이름 매핑 (Supabase로 마이그레이션됨)
# SHEET_NAMES = {
#     "CHARACTERS": "관리",
#     "SHOP": "상점",
#     "LOGS": "기록지",
#     "LIST": "명단",
# }

# DEPRECATED: 워크시트 이름 상수 (Supabase로 마이그레이션됨)
# WORKSHEET_MANAGEMENT = "관리"
# WORKSHEET_SHOP = "상점"
# WORKSHEET_LOGS = "기록지"
# WORKSHEET_LIST = "명단"

# ============================================================
# characters 테이블 컬럼 매핑 (봇에서 사용)
# Supabase 컬럼명: name, id, side, con, str, luck, hp, points, bag, misc, around, arrange
# ============================================================

class ManagementColumns(IntEnum):
    """characters 테이블 컬럼 인덱스
    
    봇 명령어에서 스탯 업데이트 시 사용됩니다.
    Supabase 컬럼명과의 매핑:
    - NAME (0) → name
    - MASTODON_ID (1) → id
    - FACTION (2) → side
    - HEALTH (3) → con
    - STRENGTH (4) → str
    - LUCK (5) → luck
    - HP (6) → hp
    - MONEY (7) → points
    - BAG (8) → bag
    - MISC (9) → misc
    - NEARBY (10) → around
    - LAYOUT (11) → arrange
    """
    NAME = 0
    MASTODON_ID = 1
    FACTION = 2
    HEALTH = 3
    STRENGTH = 4
    LUCK = 5
    HP = 6
    MONEY = 7
    BAG = 8
    MISC = 9
    NEARBY = 10
    LAYOUT = 11


# ============================================================
# 스탯 명령 매핑 (봇 stat_change / update_stat)
# 봇 내부 키(character dict) ↔ Supabase characters 테이블 컬럼명
# ============================================================

# 사용자 입력(정규식 허용) → 봇 내부 키 (character dict 키와 동일)
STAT_INPUT_TO_KEY: Final[dict[str, str]] = {
    "hp": "hp",
    "체력": "health",
    "근력": "strength",
    "행운": "luck",
}

# 봇 내부 키 → Supabase characters 컬럼명 (con, str, hp, luck, points)
STAT_KEY_TO_DB_COLUMN: Final[dict[str, str]] = {
    "hp": "hp",
    "health": "con",
    "con": "con",
    "strength": "str",
    "str": "str",
    "luck": "luck",
    "points": "points",
}

# 봇 내부 키 → 응답 메시지용 표시명
STAT_KEY_TO_DISPLAY_NAME: Final[dict[str, str]] = {
    "hp": "HP",
    "health": "체력",
    "strength": "근력",
    "luck": "행운",
}


# ============================================================
# 회피(dodge) 성공률 구간
# 행운(luck) 구간별 성공 확률: (luck 임계값, 성공률 %)
# ============================================================

LUCK_RATE_TABLE: Final[list[tuple[int, int]]] = [(4, 30), (8, 50), (12, 65)]
DODGE_MAX_RATE: Final[int] = 80
DODGE_MIN_RATE: Final[int] = 30


# ============================================================
# 가방 용량 계산
# ============================================================

def get_bag_capacity(strength: int) -> int:
    """근력 기반 가방 용량. 1~5: 20, 6~10: 40, 11~49: 60, 50: 200."""
    try:
        s = int(strength)
        if s >= 50:
            return 200
        if 1 <= s <= 5:
            return 20
        if 6 <= s <= 10:
            return 40
        if s >= 11:
            return 60
    except (TypeError, ValueError):
        pass
    return 20


# ============================================================
# items 테이블 컬럼 매핑 (레거시 참조용)
# Supabase 컬럼명: name, price, description, use_script, change_stats, change_value, size
# ============================================================

class ShopColumns(IntEnum):
    """items 테이블 컬럼 인덱스 (레거시 참조용)
    
    Supabase 컬럼명과의 매핑:
    - NAME (0) → name
    - PRICE (1) → price
    - DESC (2) → description
    - USE_MSG (3) → use_script
    - STAT (4) → change_stats
    - VALUE (5) → change_value
    - VOLUME (6) → size
    """
    NAME = 0
    PRICE = 1
    DESC = 2
    USE_MSG = 3
    STAT = 4
    VALUE = 5
    VOLUME = 6


# ============================================================
# 인벤토리 위치 상수
# ============================================================

class InventoryLocation:
    """인벤토리 위치 상수 (오타 방지 및 타입 안정성)"""
    BAG: Final[str] = 'bag'
    MISC: Final[str] = 'misc'
    NEARBY: Final[str] = 'nearby'


# 봇 내부 location 키 → Supabase characters 컬럼명 (RPC use_item_transaction 등에서 사용)
LOCATION_TO_DB_COLUMN: Final[dict[str, str]] = {
    "nearby": "around",
    "bag": "bag",
    "misc": "misc",
}


# ============================================================
# 아이템 관련 상수
# ============================================================

ZERO_VOLUME_THRESHOLD: Final[int] = 0
"""부피 0인 아이템은 여유공간에 자동 보관"""

MAX_ITEM_NAME_LENGTH: Final[int] = 50
"""아이템명 최대 길이 (입력 검증용)"""


# ============================================================
# 에러 메시지 템플릿
# ============================================================

class ErrorMessages:
    """에러 메시지 템플릿 (일관성 유지)"""
    CHARACTER_NOT_FOUND: Final[str] = "@{user} 등록된 캐릭터를 찾을 수 없습니다."
    ITEM_NOT_FOUND: Final[str] = "@{user} '{item_name}' 아이템이 존재하지 않습니다."
    ITEM_NOT_IN_INVENTORY: Final[str] = "@{user} '{item_name}' 아이템을 소지하고 있지 않습니다."
    ITEM_INFO_NOT_FOUND: Final[str] = "@{user} '{item_name}' 정보를 찾을 수 없습니다."
    SYSTEM_ERROR: Final[str] = "@{user} 시스템 오류가 발생했습니다."
    TRANSACTION_ERROR: Final[str] = "@{user} 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
    DB_ERROR: Final[str] = "@{user} 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    INVALID_ITEM_NAME: Final[str] = "@{user} 아이템명을 입력해주세요. 사용법: [{command}/아이템명]"
    ITEM_NAME_TOO_LONG: Final[str] = "@{user} 아이템명이 너무 깁니다. (최대 {max_length}자)"
    NO_FACTION: Final[str] = "@{user} {user_name}의 진영 정보가 없습니다."
    UNKNOWN_FACTION: Final[str] = "@{user} {user_name}의 진영({faction})을 인식할 수 없습니다."
    NO_HEALTH: Final[str] = "@{user} {user_name}의 체력 정보가 없습니다."
    INVALID_HEALTH: Final[str] = "@{user} {user_name}의 체력 값이 올바르지 않습니다: {health_raw}"
