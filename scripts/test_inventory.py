"""테스트용 스크립트: 실제 인벤토리 조작 테스트 (Supabase 버전)"""

import sys
import os

# 상위 디렉토리 import
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from bot.services.inventory_service import add_item, remove_item, get_item_count, get_inventory_dict
from bot.services.character_service import get_character
from shared.supabase_client import get_supabase, TABLE_CHARACTERS

# 테스트용 캐릭터 이름 (Supabase에 실제 존재하는 이름 필요)
TEST_CHAR = "다이먼"


def test_inventory_ops():
    print(f"[TEST] Testing Inventory Ops for '{TEST_CHAR}'...")

    # 1. 캐릭터 존재 확인
    char = get_character(TEST_CHAR)
    if not char:
        print(f"[ERROR] Character '{TEST_CHAR}' not found!")
        # 실제 존재하는 캐릭터 목록 출력
        supabase = get_supabase()
        response = supabase.table(TABLE_CHARACTERS).select("name").execute()
        names = [r.get("name") for r in response.data]
        print(f"[INFO] Available Characters: {names[:5]}...")
        return

    print(f"[OK] Found Character: {char['name']}")

    # 2. 초기 상태 확인
    initial_count = get_item_count(TEST_CHAR, "testapple")
    print(f"[INFO] Initial 'testapple': {initial_count}")

    # 3. 아이템 추가 (주변)
    print("[INFO] Adding 'testapple' x2 to Nearby...")
    if add_item(TEST_CHAR, "testapple", 2, "nearby"):
        print("[OK] Added successfully")
    else:
        print("[ERROR] Failed to add")

    # 4. 추가 후 확인
    new_count = get_item_count(TEST_CHAR, "testapple")
    print(f"[INFO] New Count: {new_count}")

    # 5. 아이템 제거 (청소)
    print("[INFO] Removing 'testapple' x2...")
    if remove_item(TEST_CHAR, "testapple", 2, "nearby"):
        print("[OK] Removed successfully")
    else:
        print("[ERROR] Failed to remove")

    # 6. 최종 확인
    final_count = get_item_count(TEST_CHAR, "testapple")
    print(f"[INFO] Final Count: {final_count}")

    if initial_count == final_count:
        print("\n[SUCCESS] Inventory Test Passed! (Clean State)")
    else:
        print("\n[WARNING] State Mismatch! (Manual Cleanup Required)")


if __name__ == "__main__":
    test_inventory_ops()
