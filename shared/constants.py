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
    BAG = 6         # 가방 (G열)
    MISC = 7        # 여유공간 (H열)
    NEARBY = 8      # 주변 (I열)

# '상점' 시트 컬럼 인덱스
class ShopColumns(IntEnum):
    NAME = 0        # 아이템명
    PRICE = 1       # 가격
    DESC = 2        # 설명
    USE_MSG = 3     # 사용문구
    STAT = 4        # 스탯
    VALUE = 5       # 수치
    VOLUME = 6      # 부피
