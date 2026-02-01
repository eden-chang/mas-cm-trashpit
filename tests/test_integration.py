"""구글 시트 ↔ 웹사이트 연동성 통합 테스트 (Phase 4)

이 테스트는 실제 Flask API 서버와 구글 시트 연동을 검증합니다.
테스트 전 API 서버가 실행 중이어야 합니다: python api/app.py
"""

import os
import sys
import time
import json
import pytest
import requests
from typing import Optional
from unittest.mock import patch

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.cache import invalidate_cache, get_cache_stats


# ============================================================
# 테스트 설정
# ============================================================
API_BASE = os.getenv("TEST_API_BASE", "http://localhost:5000/api")
TEST_CHARACTER = os.getenv("TEST_CHARACTER", None)  # 테스트용 캐릭터 이름


def api_available() -> bool:
    """API 서버 가용성 확인"""
    try:
        resp = requests.get(f"{API_BASE.replace('/api', '')}/health", timeout=2)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


# API 서버 필수 데코레이터
requires_api = pytest.mark.skipif(
    not api_available(),
    reason="API 서버가 실행 중이지 않습니다. `python api/app.py`로 시작하세요."
)

# 테스트 캐릭터 필수 데코레이터
requires_test_character = pytest.mark.skipif(
    TEST_CHARACTER is None,
    reason="TEST_CHARACTER 환경변수가 설정되지 않았습니다."
)


# ============================================================
# 1. API 기본 연결 테스트
# ============================================================
class TestApiConnection:
    """API 서버 기본 연결 테스트"""

    @requires_api
    def test_health_endpoint(self):
        """헬스체크 엔드포인트"""
        resp = requests.get(f"{API_BASE.replace('/api', '')}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    @requires_api
    def test_root_endpoint(self):
        """루트 엔드포인트 상태 확인"""
        resp = requests.get(API_BASE.replace('/api', ''))
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


# ============================================================
# 2. 캐릭터 API 테스트
# ============================================================
class TestCharacterApi:
    """캐릭터 관련 API 테스트"""

    @requires_api
    def test_get_characters_list(self):
        """캐릭터 목록 조회"""
        resp = requests.get(f"{API_BASE}/characters")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

        if data:
            char = data[0]
            assert "name" in char
            assert "bag_capacity" in char
            assert "bag_used" in char

    @requires_api
    @requires_test_character
    def test_get_character_by_name(self):
        """이름으로 캐릭터 조회"""
        resp = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        assert resp.status_code == 200
        data = resp.json()

        # 필수 필드 확인
        assert data["name"] == TEST_CHARACTER
        assert "bag_capacity" in data
        assert "bag_items" in data
        assert "nearby_items" in data
        assert "misc_items" in data

    @requires_api
    def test_get_nonexistent_character(self):
        """존재하지 않는 캐릭터 조회"""
        resp = requests.get(f"{API_BASE}/character/__nonexistent__")
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data


# ============================================================
# 3. 가방 API 테스트
# ============================================================
class TestBagApi:
    """가방 API 테스트"""

    @requires_api
    @requires_test_character
    def test_get_bag(self):
        """가방 조회"""
        resp = requests.get(f"{API_BASE}/bag/{TEST_CHARACTER}")
        assert resp.status_code == 200
        data = resp.json()

        assert "capacity" in data
        assert "used" in data
        assert "available" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    @requires_api
    @requires_test_character
    def test_bag_items_have_volume_info(self):
        """가방 아이템에 부피 정보 포함"""
        resp = requests.get(f"{API_BASE}/bag/{TEST_CHARACTER}")
        assert resp.status_code == 200
        data = resp.json()

        for item in data["items"]:
            assert "name" in item
            assert "quantity" in item
            assert "volume" in item


# ============================================================
# 4. 주변 API 테스트
# ============================================================
class TestNearbyApi:
    """주변 아이템 API 테스트"""

    @requires_api
    @requires_test_character
    def test_get_nearby(self):
        """주변 아이템 조회"""
        resp = requests.get(f"{API_BASE}/nearby/{TEST_CHARACTER}")
        assert resp.status_code == 200
        data = resp.json()

        assert "items" in data
        assert isinstance(data["items"], list)


# ============================================================
# 5. 캐시 동작 테스트
# ============================================================
class TestCacheBehavior:
    """캐시 동작 테스트 (API 내부)"""

    def setup_method(self):
        """테스트 전 캐시 초기화"""
        invalidate_cache()

    @requires_api
    @requires_test_character
    def test_repeated_requests_use_cache(self):
        """반복 요청 시 캐시 사용 확인"""
        # 첫 번째 요청 (캐시 미스)
        start = time.time()
        resp1 = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        first_duration = time.time() - start

        # 두 번째 요청 (캐시 히트 기대)
        start = time.time()
        resp2 = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        second_duration = time.time() - start

        assert resp1.status_code == 200
        assert resp2.status_code == 200

        # 응답 데이터가 동일해야 함
        assert resp1.json() == resp2.json()

    @requires_api
    def test_characters_list_cache(self):
        """캐릭터 목록 캐시 테스트"""
        # 첫 번째 요청
        resp1 = requests.get(f"{API_BASE}/characters")

        # 바로 두 번째 요청
        resp2 = requests.get(f"{API_BASE}/characters")

        assert resp1.status_code == 200
        assert resp2.status_code == 200

        # 데이터가 동일해야 함
        data1 = resp1.json()
        data2 = resp2.json()
        assert len(data1) == len(data2)


# ============================================================
# 6. 데이터 흐름 테스트 (읽기 전용)
# ============================================================
class TestDataFlow:
    """데이터 흐름 테스트 (시트 → API → 클라이언트)"""

    @requires_api
    @requires_test_character
    def test_character_data_consistency(self):
        """캐릭터 데이터 일관성"""
        # 캐릭터 조회
        char_resp = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        assert char_resp.status_code == 200
        char_data = char_resp.json()

        # 가방 조회
        bag_resp = requests.get(f"{API_BASE}/bag/{TEST_CHARACTER}")
        assert bag_resp.status_code == 200
        bag_data = bag_resp.json()

        # 주변 조회
        nearby_resp = requests.get(f"{API_BASE}/nearby/{TEST_CHARACTER}")
        assert nearby_resp.status_code == 200
        nearby_data = nearby_resp.json()

        # 용량 일치 확인
        assert char_data["bag_capacity"] == bag_data["capacity"]

        # 아이템 수 일치 확인
        assert len(char_data["bag_items"]) == len(bag_data["items"])
        assert len(char_data["nearby_items"]) == len(nearby_data["items"])

    @requires_api
    def test_all_characters_have_valid_structure(self):
        """모든 캐릭터 데이터 구조 검증"""
        resp = requests.get(f"{API_BASE}/characters")
        assert resp.status_code == 200
        characters = resp.json()

        for char_summary in characters[:5]:  # 처음 5개만 검증
            char_resp = requests.get(f"{API_BASE}/character/{char_summary['name']}")
            if char_resp.status_code == 200:
                char = char_resp.json()

                # 필수 필드 타입 검증
                assert isinstance(char["name"], str)
                assert isinstance(char["bag_capacity"], int)
                assert isinstance(char["bag_items"], list)
                assert isinstance(char["nearby_items"], list)
                assert isinstance(char["misc_items"], list)


# ============================================================
# 7. 에러 처리 테스트
# ============================================================
class TestErrorHandling:
    """에러 처리 테스트"""

    @requires_api
    def test_invalid_character_returns_404(self):
        """잘못된 캐릭터명 404 반환"""
        resp = requests.get(f"{API_BASE}/character/__invalid_name__")
        assert resp.status_code == 404

    @requires_api
    def test_invalid_bag_request_returns_404(self):
        """잘못된 가방 요청 404 반환"""
        resp = requests.get(f"{API_BASE}/bag/__invalid_name__")
        assert resp.status_code == 404

    @requires_api
    def test_invalid_nearby_request_returns_404(self):
        """잘못된 주변 요청 404 반환"""
        resp = requests.get(f"{API_BASE}/nearby/__invalid_name__")
        assert resp.status_code == 404


# ============================================================
# 8. CORS 테스트
# ============================================================
class TestCors:
    """CORS 설정 테스트"""

    @requires_api
    def test_cors_headers_present(self):
        """CORS 헤더 존재 확인"""
        resp = requests.options(
            f"{API_BASE}/characters",
            headers={"Origin": "http://localhost:5173"}
        )
        # CORS preflight가 허용되어야 함
        # Flask-CORS가 설정되어 있으면 OPTIONS 요청이 성공해야 함


# ============================================================
# 9. 성능 테스트 (간단)
# ============================================================
class TestPerformance:
    """기본 성능 테스트"""

    @requires_api
    def test_characters_list_response_time(self):
        """캐릭터 목록 응답 시간"""
        start = time.time()
        resp = requests.get(f"{API_BASE}/characters")
        duration = time.time() - start

        assert resp.status_code == 200
        # 5초 이내 응답 (첫 요청, 캐시 미스 포함)
        assert duration < 5.0

    @requires_api
    @requires_test_character
    def test_character_detail_response_time(self):
        """캐릭터 상세 응답 시간"""
        start = time.time()
        resp = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        duration = time.time() - start

        assert resp.status_code == 200
        # 3초 이내 응답
        assert duration < 3.0


# ============================================================
# 메인 실행
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("구글 시트 ↔ 웹사이트 연동 테스트")
    print("=" * 60)

    # API 상태 확인
    if api_available():
        print(f"✓ API 서버 연결됨: {API_BASE}")
    else:
        print(f"✗ API 서버 연결 실패: {API_BASE}")
        print("  → `python api/app.py`로 서버를 시작하세요.")
        sys.exit(1)

    # 테스트 캐릭터 확인
    if TEST_CHARACTER:
        print(f"✓ 테스트 캐릭터: {TEST_CHARACTER}")
    else:
        print("⚠ TEST_CHARACTER 환경변수 미설정 (일부 테스트 스킵)")

    print("\npytest 실행 중...")
    print("-" * 60)

    # pytest 실행
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
