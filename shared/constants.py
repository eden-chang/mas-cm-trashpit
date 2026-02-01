"""공용 상수 정의"""

# 구글 시트 ID
SHEET_ID = "1JrUVHRj7fKpvX-cP98J13Asx6h-FEydAPCm0q7l1exk"

# 워크시트 이름
WORKSHEET_MANAGEMENT = "관리"
WORKSHEET_SHOP = "상점"

# 근력에 따른 가방 용량 (문서 1.3)
CAPACITY_RULES = {
    (1, 5): 20,
    (6, 10): 40,
    (11, 15): 60,
    (16, 20): 80,
}

def get_bag_capacity(strength: int) -> int:
    """근력에 따른 가방 용량 계산"""
    for (min_str, max_str), capacity in CAPACITY_RULES.items():
        if min_str <= strength <= max_str:
            return capacity
    return 20  # 기본값


# 진영 정보 (Phase 1.1)
FACTION_WEGA = "웨가"
FACTION_SKY = "스카이"


# 시트 컬럼 인덱스 (0부터 시작)
# 순서: 이름, 아이디, 진영, 체력, 근력, 행운, 가방, 여유공간, 주변
class ManagementColumns:
    NAME = 0        # 이름
    MASTODON_ID = 1 # 아이디
    FACTION = 2     # 진영 (웨가/스카이)
    HEALTH = 3      # 체력
    STRENGTH = 4    # 근력
    LUCK = 5        # 행운
    BAG = 6         # 가방
    MISC = 7        # 여유공간
    NEARBY = 8      # 주변


class ShopColumns:
    ITEM_NAME = 0   # 아이템명
    PRICE = 1       # 가격
    DESCRIPTION = 2 # 설명
    USE_MESSAGE = 3 # 사용문구
    STAT = 4        # 스탯
    VALUE = 5       # 수치
    VOLUME = 6      # 부피
