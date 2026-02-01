"""테스트용 스크립트: 인벤토리 파서 확인"""

import sys
import os

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from shared.inventory_parser import parse_inventory_str, to_inventory_str

def test_parser():
    print("🧪 Inventory Parser Test")
    
    cases = [
        ("사과: 1, 바나나: 3", {'사과': 1, '바나나': 3}),
        ("사과:1,바나나:3", {'사과': 1, '바나나': 3}),
        ("검: 1\n방패: 1", {'검': 1, '방패': 1}),
        ("돌멩이", {'돌멩이': 1}),
        ("", {}),
        ("  ", {}),
        ("사과: 0, 바나나: 2", {'바나나': 2}), # to_string 변환 시 0 제거 확인용
    ]
    
    for input_str, expected in cases:
        print(f"\nInput: '{input_str}'")
        parsed = parse_inventory_str(input_str)
        print(f"Parsed: {parsed}")
        
        # 0 이하 수량은 parse 단계에서는 유지하고 to_string에서 거름?
        # 아니면 parse 로직에 따라 다름. 현재 로직: parse는 그대로, to_str에서 필터링
        
        serialized = to_inventory_str(parsed)
        print(f"Serialized: '{serialized}'")
        
        # 검증 (순서 무관 비교를 위해 dict 재파싱)
        re_parsed = parse_inventory_str(serialized)
        
        # 0인 항목 제외하고 비교
        expected_filtered = {k: v for k, v in expected.items() if v > 0}
        parsed_filtered = {k: v for k, v in parsed.items() if v > 0}
        
        if parsed_filtered == expected_filtered:
             print("✅ Pass")
        else:
             print(f"❌ Fail (Expected: {expected_filtered}, Got: {parsed_filtered})")

if __name__ == "__main__":
    test_parser()
