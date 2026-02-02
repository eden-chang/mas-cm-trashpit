"""테스트용 스크립트: Supabase 연결 및 데이터 조회 확인"""

import sys
import os

# 상위 디렉토리 import
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from shared.supabase_client import get_supabase, TABLE_CHARACTERS, TABLE_ITEMS
from shared.config import SUPABASE_URL


def test_connection():
    print(f"[INFO] Connecting to Supabase: {SUPABASE_URL}...")
    try:
        supabase = get_supabase()
        print("[OK] Connected!")

        # 'characters' 테이블 조회 테스트
        print("\n[INFO] Checking 'characters' Table...")
        response = supabase.table(TABLE_CHARACTERS).select("*").limit(3).execute()
        print(f"  Found {len(response.data)} characters")
        if response.data:
            sample = response.data[0]
            print(f"  Sample: {sample.get('name')} ({sample.get('id')})")

        # 'items' 테이블 조회 테스트
        print("\n[INFO] Checking 'items' Table...")
        response = supabase.table(TABLE_ITEMS).select("*").limit(3).execute()
        print(f"  Found {len(response.data)} items")
        if response.data:
            sample = response.data[0]
            print(f"  Sample: {sample.get('name')} (price: {sample.get('price')}, size: {sample.get('size')})")

        print("\n[SUCCESS] Connection Test Passed!")

    except Exception as e:
        print(f"\n[ERROR] Connection Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
