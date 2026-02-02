"""API 테스트 스크립트"""

import urllib.request
import json

# 캐릭터 목록 조회
print("=== 캐릭터 목록 (/api/characters) ===")
with urllib.request.urlopen("http://127.0.0.1:5000/api/characters") as response:
    data = json.loads(response.read().decode())
    for char in data:
        print(f"  {char['name']}: bag_used={char['bag_used']}/{char['bag_capacity']}")

# 데이릭 캐릭터 상세
print("\n=== 데이릭 상세 (/api/character/데이릭) ===")
with urllib.request.urlopen("http://127.0.0.1:5000/api/character/데이릭") as response:
    data = json.loads(response.read().decode())
    print(f"  name: {data['name']}")
    print(f"  bag_used: {data['bag_used']}/{data['bag_capacity']}")
    print(f"  bag_items: {json.dumps(data['bag_items'], ensure_ascii=False, indent=4)}")
    print(f"  misc_items: {json.dumps(data['misc_items'], ensure_ascii=False, indent=4)}")
    print(f"  nearby_items: {json.dumps(data['nearby_items'], ensure_ascii=False, indent=4)}")
