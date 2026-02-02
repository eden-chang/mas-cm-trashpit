"""Supabase에서 characters와 items 테이블의 모든 데이터를 조회하는 스크립트"""

import sys
sys.path.insert(0, ".")

import json
from shared.supabase_client import get_supabase, TABLE_CHARACTERS, TABLE_ITEMS


def main():
    supabase = get_supabase()
    
    # Characters 테이블 전체 조회
    chars_response = supabase.table(TABLE_CHARACTERS).select("*").execute()
    characters = chars_response.data
    
    # Items 테이블 전체 조회
    items_response = supabase.table(TABLE_ITEMS).select("*").execute()
    items = items_response.data
    
    # JSON 파일로 저장
    with open("characters_full_data.json", "w", encoding="utf-8") as f:
        json.dump(characters, f, indent=2, ensure_ascii=False)
    
    with open("items_full_data.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    print(f"=== Characters 테이블 ({len(characters)}건) ===")
    if characters:
        print(f"컬럼: {list(characters[0].keys())}")
    
    print(f"\n=== Items 테이블 ({len(items)}건) ===")
    if items:
        print(f"컬럼: {list(items[0].keys())}")
    
    print("\n파일 저장 완료:")
    print("- characters_full_data.json")
    print("- items_full_data.json")


if __name__ == "__main__":
    main()
