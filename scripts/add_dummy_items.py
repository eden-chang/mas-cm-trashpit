"""더미 아이템 추가 스크립트

items 테이블에 테스트용 더미 아이템을 추가합니다.
"""

import sys
from pathlib import Path

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase, TABLE_ITEMS


def add_dummy_items():
    """더미 아이템 10개 추가"""
    
    dummy_items = [
        {
            "name": "테스트 물약",
            "price": "100",
            "description": "테스트용 회복 물약입니다.",
            "use_script": "물약을 마셨다. 기분이 좋아졌다!",
            "change_stats": "체력",
            "change_value": "5",
            "size": 1,
        },
        {
            "name": "녹슨 칼",
            "price": "50",
            "description": "녹이 슨 낡은 칼. 그래도 쓸만하다.",
            "use_script": "",
            "change_stats": "사용 불가",
            "change_value": "",
            "size": 2,
        },
        {
            "name": "에너지 드링크",
            "price": "150",
            "description": "카페인이 듬뿍 든 에너지 음료.",
            "use_script": "에너지 드링크를 벌컥벌컥 마셨다!",
            "change_stats": "근력",
            "change_value": "1d6",
            "size": 1,
        },
        {
            "name": "행운의 동전",
            "price": "비매품",
            "description": "행운을 가져다준다는 동전.",
            "use_script": "동전을 던져보았다. 앞면이 나왔다!",
            "change_stats": "행운",
            "change_value": "3",
            "size": 0,  # 여유공간 아이템
        },
        {
            "name": "낡은 배낭",
            "price": "200",
            "description": "수납공간이 있는 배낭.",
            "use_script": "",
            "change_stats": "사용 불가",
            "change_value": "",
            "size": 4,
        },
        {
            "name": "붕대",
            "price": "30",
            "description": "상처를 치료할 수 있는 붕대.",
            "use_script": "붕대로 상처를 감았다.",
            "change_stats": "체력",
            "change_value": "2",
            "size": 1,
        },
        {
            "name": "손전등",
            "price": "80",
            "description": "어둠을 밝히는 손전등.",
            "use_script": "",
            "change_stats": "사용 불가",
            "change_value": "",
            "size": 2,
        },
        {
            "name": "비상식량",
            "price": "60",
            "description": "오래 보관할 수 있는 비상식량.",
            "use_script": "비상식량을 먹었다. 맛은 그저 그렇다.",
            "change_stats": "체력",
            "change_value": "1d6+2",
            "size": 1,
        },
        {
            "name": "부적",
            "price": "비매품",
            "description": "신비로운 힘이 깃든 부적.",
            "use_script": "부적의 힘을 느꼈다!",
            "change_stats": "행운",
            "change_value": "1d6",
            "size": 0,  # 여유공간 아이템
        },
        {
            "name": "철제 방패",
            "price": "300",
            "description": "튼튼한 철제 방패.",
            "use_script": "",
            "change_stats": "사용 불가",
            "change_value": "",
            "size": 6,
        },
    ]
    
    supabase = get_supabase()
    
    print(f"Adding {len(dummy_items)} dummy items...")
    
    success_count = 0
    for item in dummy_items:
        try:
            # upsert로 이미 있으면 업데이트
            response = supabase.table(TABLE_ITEMS).upsert(item).execute()
            if response.data:
                print(f"  [OK] '{item['name']}' added (size: {item['size']})")
                success_count += 1
            else:
                print(f"  [FAIL] '{item['name']}' failed")
        except Exception as e:
            print(f"  [FAIL] '{item['name']}' error: {e}")
    
    print(f"\nDone: {success_count}/{len(dummy_items)} items added")
    return success_count


if __name__ == "__main__":
    add_dummy_items()
