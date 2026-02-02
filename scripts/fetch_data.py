"""API를 통해 characters와 items 데이터를 조회하는 스크립트"""

import requests
import json


def main():
    base_url = "http://127.0.0.1:5000/api"
    
    # Characters 조회
    chars_response = requests.get(f"{base_url}/characters")
    chars = chars_response.json()
    
    # Items 조회  
    items_response = requests.get(f"{base_url}/items")
    items = items_response.json()
    
    # JSON 파일로 저장
    with open("characters_data.json", "w", encoding="utf-8") as f:
        json.dump(chars, f, indent=2, ensure_ascii=False)
    
    with open("items_data.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    
    print(f"Characters: {len(chars)} records saved to characters_data.json")
    print(f"Items: {len(items)} records saved to items_data.json")


if __name__ == "__main__":
    main()
