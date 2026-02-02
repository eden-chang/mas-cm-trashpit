"""Supabase 데이터 확인 스크립트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from shared.supabase_client import get_supabase, TABLE_CHARACTERS

supabase = get_supabase()
response = supabase.table(TABLE_CHARACTERS).select("name, bag, misc, around, arrange").order("name").execute()

for row in response.data:
    print(f"Character: {row.get('name')}")
    print(f"  bag: {json.dumps(row.get('bag'), ensure_ascii=False)}")
    print(f"  misc: {json.dumps(row.get('misc'), ensure_ascii=False)}")
    print(f"  around: {json.dumps(row.get('around'), ensure_ascii=False)}")
    print(f"  arrange: {json.dumps(row.get('arrange'), ensure_ascii=False)}")
    print()
