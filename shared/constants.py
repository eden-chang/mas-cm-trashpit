"""상수 정의

Supabase 마이그레이션 완료. 일부 상수는 레거시 호환용으로 유지.
"""

from enum import IntEnum

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
# 가방 용량 계산
# ============================================================

def get_bag_capacity(strength: int) -> int:
    """근력 기반 가방 용량. 1~5: 20, 6~10: 40, 11+: 60."""
    try:
        s = int(strength)
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
