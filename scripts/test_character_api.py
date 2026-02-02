"""개별 캐릭터 API 응답 테스트"""

import requests
import json


def main():
    base_url = "http://127.0.0.1:5000/api"
    
    # 데이릭 캐릭터 상세 조회
    response = requests.get(f"{base_url}/character/데이릭")
    data = response.json()
    
    print("=== /api/character/데이릭 응답 ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # bag_items 확인
    print("\n=== bag_items 분석 ===")
    if "bag_items" in data:
        print(f"bag_items 개수: {len(data['bag_items'])}")
        for item in data.get("bag_items", []):
            print(f"  - {item}")
    else:
        print("bag_items 필드 없음!")
    
    # bag_layout 확인
    print("\n=== bag_layout 분석 ===")
    if "bag_layout" in data:
        print(f"bag_layout 개수: {len(data['bag_layout'])}")
        for layout in data.get("bag_layout", []):
            print(f"  - {layout}")
    else:
        print("bag_layout 필드 없음!")


if __name__ == "__main__":
    main()
