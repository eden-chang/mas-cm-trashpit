"""테스트용 스크립트: 실제 인벤토리 조작 테스트"""

import sys
import os

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from bot.services.inventory_service import add_item, remove_item, get_item_count, get_inventory_dict
from bot.services.character_service import get_character
from shared.constants import ManagementColumns

# 테스트용 캐릭터 이름 (시트에 실제 존재하는 이름 필요)
TEST_CHAR = "데이릭 워드"

def test_inventory_ops():
    print(f"🧪 Testing Inventory Ops for '{TEST_CHAR}'...")
    
    # 1. 캐릭터 존재 확인
    char = get_character(TEST_CHAR)
    if not char:
        print(f"❌ Character '{TEST_CHAR}' not found in sheet!")
        # 실제 존재하는 캐릭터 목록 출력해서 힌트 얻기
        from shared.google_sheets import get_worksheet
        ws = get_worksheet("관리")
        names = ws.col_values(1) # A열
        print(f"ℹ️ Available Characters: {names[:5]}...") # 상위 5명만
        return

    print(f"✅ Found Character: {char['name']} (Row {char['row']})")

    # 2. 초기 상태 확인
    initial_count = get_item_count(TEST_CHAR, "테스트사과")
    print(f"🍎 Initial '테스트사과': {initial_count}")

    # 3. 아이템 추가 (주변)
    print("➕ Adding '테스트사과' x2 to Nearby...")
    if add_item(TEST_CHAR, "테스트사과", 2, "nearby"):
        print("✅ Added successfully")
    else:
        print("❌ Failed to add")

    # 4. 추가 후 확인
    new_count = get_item_count(TEST_CHAR, "테스트사과")
    print(f"🍎 New Count: {new_count}")
    
    # 5. 아이템 제거 (청소)
    print("➖ Removing '테스트사과' x2...")
    if remove_item(TEST_CHAR, "테스트사과", 2, "nearby"):
        print("✅ Removed successfully")
    else:
        print("❌ Failed to remove")

    # 6. 최종 확인
    final_count = get_item_count(TEST_CHAR, "테스트사과")
    print(f"🍎 Final Count: {final_count}")
    
    if initial_count == final_count:
        print("\n🎉 Inventory Test Passed! (Clean State)")
    else:
        print("\n⚠️ State Mismatch! (Manual Cleanup Required)")

if __name__ == "__main__":
    test_inventory_ops()
