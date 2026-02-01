from enum import IntEnum

# 시트 이름 매핑
SHEET_NAMES = {
    "CHARACTERS": "관리",  # 캐릭터 정보 (스탯, 인벤토리)
    "SHOP": "상점",        # 아이템 마스터
    "LOGS": "기록지",      # 로그
    "LIST": "명단",        # 마스토돈 ID 매핑
}

# '관리' 시트 컬럼 인덱스 (0-based for internal use, gspread uses 1-based)
class ManagementColumns(IntEnum):
    NAME = 0        # 이름 (A열)
    MASTODON_ID = 1 # 아이디 (B열)
    FACTION = 2     # 진영 (C열)
    HEALTH = 3      # 체력 (D열)
    STRENGTH = 4    # 근력 (E열)
    LUCK = 5        # 행운 (F열)
    MONEY = 6       # 소지금 (G열) - 포인트
    BAG = 7         # 가방 (H열)
    MISC = 8        # 여유공간 (I열)
    NEARBY = 9      # 주변 (J열)

def get_bag_capacity(strength: int) -> int:
    """근력 기반 가방 용량 (문서 1.3). 1~5: 20, 6~10: 40, 11~15: 60, 16~20: 80."""
    try:
        s = int(strength)
        if 1 <= s <= 5:
            return 20
        if 6 <= s <= 10:
            return 40
        if 11 <= s <= 15:
            return 60
        if 16 <= s <= 20:
            return 80
    except (TypeError, ValueError):
        pass
    return 20


# '상점' 시트 컬럼 인덱스
class ShopColumns(IntEnum):
    NAME = 0        # 아이템명
    PRICE = 1       # 가격
    DESC = 2        # 설명
    USE_MSG = 3     # 사용문구
    STAT = 4        # 스탯
    VALUE = 5       # 수치
    VOLUME = 6      # 부피
