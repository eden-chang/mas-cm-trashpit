#!/usr/bin/env python
"""Supabase ↔ API ↔ 웹 · 봇–Supabase 연동 테스트 러너

이 스크립트는 Phase 4 연동 검증 및 봇–Supabase 연결성 테스트를 실행합니다.

사용법:
    python scripts/run_integration_tests.py             # 읽기 전용 테스트
    python scripts/run_integration_tests.py --write    # 쓰기 포함 테스트
    python scripts/run_integration_tests.py --all       # 전체 테스트 (쓰기 포함)
    python scripts/run_integration_tests.py --bot       # 봇–Supabase(–API) 테스트 추가

환경변수:
    TEST_API_BASE           - API 기본 URL (기본: http://localhost:5000/api)
    TEST_CHARACTER           - 테스트용 캐릭터 이름
    ENABLE_WRITE_TESTS       - 쓰기 테스트 활성화 (true/false)
    ENABLE_BOT_SUPABASE_TESTS - 봇–Supabase 테스트 활성화 (--bot 시 자동 true)
    TEST_MASTODON_ID         - 봇 테스트용 캐릭터의 마스토돈 ID
    TEST_ITEM                - 봇 테스트용 아이템명
    TEST_CHARACTER_RECEIVER  - 봇 양도 테스트용 수신자 캐릭터 (선택)
"""

import os
import sys
import subprocess
import argparse
import time
import requests
from pathlib import Path

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"

# 기본 설정
DEFAULT_API_BASE = "http://localhost:5000/api"


def check_api_server(api_base: str) -> bool:
    """API 서버 상태 확인"""
    health_url = api_base.replace("/api", "") + "/health"
    try:
        resp = requests.get(health_url, timeout=3)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def check_web_server(port: int = 5173) -> bool:
    """웹 개발 서버 상태 확인"""
    try:
        resp = requests.get(f"http://localhost:{port}", timeout=3)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_test_character(api_base: str) -> str | None:
    """테스트용 캐릭터 자동 선택 (첫 번째 캐릭터)"""
    try:
        resp = requests.get(f"{api_base}/characters", timeout=5)
        if resp.status_code == 200:
            chars = resp.json()
            if chars:
                return chars[0]["name"]
    except requests.exceptions.RequestException:
        pass
    return None


def print_header(title: str):
    """섹션 헤더 출력"""
    print()
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_status(label: str, ok: bool, detail: str = ""):
    """상태 출력"""
    status = "✓" if ok else "✗"
    print(f"  {status} {label}{': ' + detail if detail else ''}")


def run_tests(test_file: str, extra_args: list = None) -> int:
    """pytest 실행"""
    cmd = [
        sys.executable, "-m", "pytest",
        str(TESTS_DIR / test_file),
        "-v", "--tb=short"
    ]
    if extra_args:
        cmd.extend(extra_args)

    return subprocess.call(cmd, cwd=str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(description="연동 테스트 러너")
    parser.add_argument("--write", action="store_true", help="쓰기 테스트 포함")
    parser.add_argument("--all", action="store_true", help="전체 테스트 (쓰기 포함)")
    parser.add_argument("--api-base", default=None, help="API 기본 URL")
    parser.add_argument("--character", default=None, help="테스트 캐릭터 이름")
    parser.add_argument("--skip-checks", action="store_true", help="사전 검사 스킵")
    parser.add_argument("--bot", action="store_true", help="봇–Supabase(–API) 연결성 테스트 포함")
    args = parser.parse_args()

    # 환경 설정
    api_base = args.api_base or os.getenv("TEST_API_BASE", DEFAULT_API_BASE)
    test_character = args.character or os.getenv("TEST_CHARACTER")
    enable_write = args.write or args.all
    enable_bot = args.bot

    if enable_bot:
        os.environ["ENABLE_BOT_SUPABASE_TESTS"] = "true"
        if test_character:
            os.environ["TEST_CHARACTER"] = test_character

    print_header("Supabase ↔ API ↔ 웹 · 봇 연동 테스트")
    print()
    print("  Phase 4 연동 검증 테스트를 실행합니다.")
    print()

    # ========================================
    # 1. 사전 검사
    # ========================================
    if not args.skip_checks:
        print_header("1. 사전 검사")

        # API 서버 확인
        api_ok = check_api_server(api_base)
        print_status("API 서버", api_ok, api_base)

        if not api_ok:
            print()
            print("  ⚠ API 서버가 실행 중이지 않습니다.")
            print("  → 다음 명령으로 시작하세요:")
            print("    python api/app.py")
            print()
            return 1

        # 테스트 캐릭터 확인 또는 자동 선택
        if not test_character:
            test_character = get_test_character(api_base)
            if test_character:
                print_status("테스트 캐릭터 (자동 선택)", True, test_character)
            else:
                print_status("테스트 캐릭터", False, "자동 선택 실패")
                print()
                print("  ⚠ TEST_CHARACTER 환경변수를 설정하거나 --character 옵션을 사용하세요.")
        else:
            print_status("테스트 캐릭터", True, test_character)

        # 웹 서버 확인 (선택)
        web_ok = check_web_server()
        print_status("웹 개발 서버", web_ok, "http://localhost:5173" if web_ok else "미실행")

        # 환경변수 설정
        os.environ["TEST_API_BASE"] = api_base
        if test_character:
            os.environ["TEST_CHARACTER"] = test_character
        if enable_write:
            os.environ["ENABLE_WRITE_TESTS"] = "true"

    # ========================================
    # 2. 읽기 전용 테스트
    # ========================================
    print_header("2. 읽기 전용 테스트")
    print()
    print("  API 연결, 캐릭터 조회, 가방/주변 조회 테스트...")
    print()

    read_result = run_tests("test_integration.py")

    if read_result != 0:
        print()
        print("  ⚠ 일부 읽기 테스트 실패")

    # ========================================
    # 3. 쓰기 테스트 (옵션)
    # ========================================
    if enable_write:
        print_header("3. 쓰기 테스트")
        print()
        print("  ⚠ 실제 구글 시트에 데이터를 씁니다!")
        print()

        if not test_character:
            print("  ✗ TEST_CHARACTER가 필요합니다.")
            return 1

        write_result = run_tests("test_write_operations.py")

        if write_result != 0:
            print()
            print("  ⚠ 일부 쓰기 테스트 실패")

    # ========================================
    # 4. 캐시 테스트
    # ========================================
    print_header("4. 캐시 동작 테스트")
    print()
    print("  TTL 기반 캐시, 무효화 테스트...")
    print()

    cache_result = run_tests("test_cache.py")

    # ========================================
    # 5. 봇–Supabase(–API) 테스트 (옵션)
    # ========================================
    bot_result = 0
    if enable_bot:
        print_header("5. 봇–Supabase(–API) 연결성 테스트")
        print()
        print("  봇 명령 반영 → Supabase 확인, E2E 시 API 조회 일치 확인...")
        print("  (TEST_MASTODON_ID, TEST_ITEM 등 미설정 시 해당 테스트 스킵)")
        print()

        bot_result = run_tests("test_bot_supabase_connection.py")

        if bot_result != 0:
            print()
            print("  ⚠ 일부 봇–Supabase 테스트 실패")

    # ========================================
    # 결과 요약
    # ========================================
    print_header("테스트 결과 요약")

    all_passed = read_result == 0 and cache_result == 0
    if enable_write:
        all_passed = all_passed and write_result == 0
    if enable_bot:
        all_passed = all_passed and bot_result == 0

    print_status("읽기 테스트", read_result == 0)
    print_status("캐시 테스트", cache_result == 0)
    if enable_write:
        print_status("쓰기 테스트", write_result == 0)
    if enable_bot:
        print_status("봇–Supabase 테스트", bot_result == 0)

    print()
    if all_passed:
        print("  ✓ 모든 테스트 통과!")
    else:
        print("  ✗ 일부 테스트 실패. 위 로그를 확인하세요.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
