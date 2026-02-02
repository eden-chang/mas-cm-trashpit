"""캐릭터에게 아이템 지급 스크립트

각 캐릭터의 around(주변)에 테스트용 아이템을 지급합니다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase, TABLE_CHARACTERS, TABLE_ITEMS

supabase = get_supabase()


def grant_items():
    """각 캐릭터에게 아이템 지급"""
    
    # 먼저 실제 캐릭터 이름과 아이템 이름 조회
    chars_response = supabase.table(TABLE_CHARACTERS).select("name").execute()
    items_response = supabase.table(TABLE_ITEMS).select("name, size").execute()
    
    char_names = [c["name"] for c in chars_response.data]
    item_names = {i["name"]: i.get("size", 0) for i in items_response.data}
    
    print(f"Found {len(char_names)} characters: {char_names}")
    print(f"Found {len(item_names)} items")
    print()
    
    # 아이템 분류 (부피별)
    volume_0_items = [name for name, size in item_names.items() if size == 0]
    volume_1_items = [name for name, size in item_names.items() if size == 1]
    volume_2_items = [name for name, size in item_names.items() if size == 2]
    volume_large_items = [name for name, size in item_names.items() if size >= 3]
    
    print(f"Volume 0 items (misc): {volume_0_items}")
    print(f"Volume 1 items: {volume_1_items}")
    print(f"Volume 2 items: {volume_2_items}")
    print(f"Volume 3+ items: {volume_large_items}")
    print()
    
    # 캐릭터별로 다양한 아이템 배분
    if len(char_names) >= 4:
        grants = []
        
        # 첫 번째 캐릭터 - 다양한 부피
        all_items = list(item_names.keys())
        grants.append({
            "name": char_names[0],
            "items": {
                all_items[0]: 2,  # 콜라
                all_items[4]: 3,  # 테스트 물약
                all_items[9]: 2,  # 붕대
                all_items[5]: 1,  # 녹슨 칼
                all_items[13]: 1, # 철제 방패
            }
        })
        
        # 두 번째 캐릭터 - 여유공간 아이템 포함
        grants.append({
            "name": char_names[1],
            "items": {
                all_items[1]: 3,  # 사이다
                all_items[6]: 2,  # 에너지 드링크
                all_items[7]: 2,  # 행운의 동전 (부피 0)
                all_items[12]: 1, # 부적 (부피 0)
            }
        })
        
        # 세 번째 캐릭터 - 큰 부피 아이템
        grants.append({
            "name": char_names[2],
            "items": {
                all_items[2]: 2,  # 성인 잡지
                all_items[8]: 1,  # 낡은 배낭
                all_items[10]: 2, # 손전등
                all_items[11]: 3, # 비상식량
            }
        })
        
        # 네 번째 캐릭터 - 혼합
        grants.append({
            "name": char_names[3],
            "items": {
                all_items[0]: 1,  # 콜라
                all_items[1]: 1,  # 사이다
                all_items[4]: 2,  # 테스트 물약
                all_items[3]: 1,  # 청년가담 (부피 0)
                all_items[9]: 4,  # 붕대
            }
        })
        
        print("Granting items...")
        print()
        
        for grant in grants:
            char_name = grant["name"]
            items = grant["items"]
            
            try:
                response = (
                    supabase.table(TABLE_CHARACTERS)
                    .update({"around": items})
                    .eq("name", char_name)
                    .execute()
                )
                
                if response.data:
                    total_items = sum(items.values())
                    print(f"[OK] {char_name}: {total_items} items granted")
                    for item_name, qty in items.items():
                        size = item_names.get(item_name, 0)
                        print(f"     - {item_name} x{qty} (size: {size})")
                else:
                    print(f"[FAIL] {char_name}: update failed")
            except Exception as e:
                print(f"[FAIL] {char_name}: {e}")
            
            print()
    
    print("Done!")


if __name__ == "__main__":
    grant_items()
