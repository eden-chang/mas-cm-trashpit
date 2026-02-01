#!/usr/bin/env python
"""API 엔드포인트 빠른 테스트

각 엔드포인트를 호출하고 결과를 출력합니다.

사용법:
    python scripts/test_api_endpoints.py
    python scripts/test_api_endpoints.py --character 캐릭터명
"""

import sys
import json
import argparse
import requests
from typing import Any

API_BASE = "http://localhost:5000"


def colored(text: str, color: str) -> str:
    """ANSI 색상 (Windows 터미널 지원)"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def test_endpoint(method: str, path: str, json_data: dict = None) -> tuple[bool, Any]:
    """엔드포인트 테스트"""
    url = f"{API_BASE}{path}"
    try:
        if method == "GET":
            resp = requests.get(url, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=json_data, timeout=10)
        else:
            return False, f"지원하지 않는 메서드: {method}"

        data = resp.json() if resp.content else {}
        return resp.status_code < 400, {
            "status": resp.status_code,
            "data": data,
        }
    except requests.exceptions.ConnectionError:
        return False, "연결 실패 - API 서버가 실행 중인지 확인하세요"
    except Exception as e:
        return False, str(e)


def print_result(name: str, success: bool, result: Any):
    """결과 출력"""
    status = colored("✓ PASS", "green") if success else colored("✗ FAIL", "red")
    print(f"\n{status} {name}")

    if isinstance(result, dict):
        print(f"  Status: {result.get('status', 'N/A')}")
        data = result.get("data", {})
        if isinstance(data, list):
            print(f"  Items: {len(data)}")
            if data:
                print(f"  First: {json.dumps(data[0], ensure_ascii=False)[:100]}...")
        elif isinstance(data, dict):
            preview = json.dumps(data, ensure_ascii=False)[:200]
            print(f"  Data: {preview}...")
    else:
        print(f"  {result}")


def main():
    parser = argparse.ArgumentParser(description="API 엔드포인트 테스트")
    parser.add_argument("--character", "-c", help="테스트할 캐릭터 이름")
    args = parser.parse_args()

    print("=" * 60)
    print(" API 엔드포인트 테스트")
    print("=" * 60)

    # 1. 기본 엔드포인트
    print(colored("\n[기본 엔드포인트]", "blue"))

    success, result = test_endpoint("GET", "/health")
    print_result("GET /health", success, result)

    success, result = test_endpoint("GET", "/")
    print_result("GET /", success, result)

    # 2. 캐릭터 API
    print(colored("\n[캐릭터 API]", "blue"))

    success, result = test_endpoint("GET", "/api/characters")
    print_result("GET /api/characters", success, result)

    # 테스트 캐릭터 결정
    test_char = args.character
    if not test_char and success and result.get("data"):
        test_char = result["data"][0].get("name")
        print(f"  → 테스트 캐릭터 자동 선택: {test_char}")

    if test_char:
        success, result = test_endpoint("GET", f"/api/character/{test_char}")
        print_result(f"GET /api/character/{test_char}", success, result)

        # 3. 가방 API
        print(colored("\n[가방 API]", "blue"))

        success, result = test_endpoint("GET", f"/api/bag/{test_char}")
        print_result(f"GET /api/bag/{test_char}", success, result)

        # 4. 주변 API
        print(colored("\n[주변 API]", "blue"))

        success, result = test_endpoint("GET", f"/api/nearby/{test_char}")
        print_result(f"GET /api/nearby/{test_char}", success, result)

    # 5. 아이템 API
    print(colored("\n[아이템 API]", "blue"))

    success, result = test_endpoint("GET", "/api/items")
    print_result("GET /api/items", success, result)

    # 6. 관리자 API
    print(colored("\n[관리자 API]", "blue"))

    success, result = test_endpoint("GET", "/api/admin/cache/stats")
    print_result("GET /api/admin/cache/stats", success, result)

    # 7. 존재하지 않는 캐릭터 (에러 처리 확인)
    print(colored("\n[에러 처리]", "blue"))

    success, result = test_endpoint("GET", "/api/character/__nonexistent__")
    # 404는 정상 동작
    is_404 = result.get("status") == 404 if isinstance(result, dict) else False
    print_result(
        "GET /api/character/__nonexistent__ (404 예상)",
        is_404,
        result
    )

    # 완료
    print("\n" + "=" * 60)
    print(" 테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    # Windows 콘솔 ANSI 색상 지원
    import os
    os.system("")  # ANSI 이스케이프 시퀀스 활성화

    main()
