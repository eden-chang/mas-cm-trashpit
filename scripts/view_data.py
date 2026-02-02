"""데이터 조회 스크립트"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase, TABLE_ITEMS, TABLE_CHARACTERS

supabase = get_supabase()

# Items 조회
print("=" * 70)
print("ITEMS TABLE")
print("=" * 70)
items = supabase.table(TABLE_ITEMS).select("*").execute()
for item in items.data:
    name = item.get("name", "")
    size = item.get("size", 0)
    price = item.get("price", "")
    stats = item.get("change_stats", "-")
    print(f"  {name:20} | size: {size:2} | price: {str(price):10} | stats: {stats}")

# Characters 조회
print()
print("=" * 70)
print("CHARACTERS TABLE")
print("=" * 70)
chars = supabase.table(TABLE_CHARACTERS).select("name, str, around, bag, misc").execute()
for char in chars.data:
    name = char.get("name", "")
    strength = char.get("str", 0)
    around = char.get("around")
    bag = char.get("bag")
    misc = char.get("misc")
    print(f"  {name:15} | STR: {strength:2}")
    print(f"      around: {around}")
    print(f"      bag: {bag}")
    print(f"      misc: {misc}")
    print()
