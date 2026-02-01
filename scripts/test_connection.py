"""테스트용 스크립트: 시트 연결 및 데이터 조회 확인"""

import sys
import os

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from shared.google_sheets import get_spreadsheet, get_worksheet
from shared.config import SHEET_ID

def test_connection():
    print(f"🔌 Connecting to Sheet ID: {SHEET_ID}...")
    try:
        sh = get_spreadsheet()
        print(f"✅ Connected! Title: {sh.title}")
        
        # 워크시트 목록 확인
        worksheets = sh.worksheets()
        print(f"📂 Worksheets ({len(worksheets)}):")
        for ws in worksheets:
            print(f"  - {ws.title}")
            
        # '관리' 시트 조회 테스트
        print("\n🔍 Checking '관리' Sheet...")
        manage_sheet = get_worksheet("관리")
        headers = manage_sheet.row_values(1)
        print(f"  Headers: {headers}")
        sample = manage_sheet.row_values(2)
        print(f"  Sample Row: {sample}")

        # '상점' 시트 조회 테스트
        print("\n🔍 Checking '상점' Sheet...")
        shop_sheet = get_worksheet("상점")
        headers = shop_sheet.row_values(1)
        print(f"  Headers: {headers}")
        
        print("\n🎉 Connection Test Passed!")
        
    except Exception as e:
        print(f"\n❌ Connection Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
