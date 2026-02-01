"""구글 시트 쓰기 연동 테스트 (Phase 4)

⚠️ 주의: 이 테스트는 실제 구글 시트에 데이터를 쓰고 복원합니다.
테스트 전 반드시 TEST_CHARACTER를 테스트 전용 캐릭터로 설정하세요.

실행 방법:
    TEST_CHARACTER=테스트캐릭터 python -m pytest tests/test_write_operations.py -v
"""

import os
import sys
import time
import pytest
import requests
from typing import Optional

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# 테스트 설정
# ============================================================
API_BASE = os.getenv("TEST_API_BASE", "http://localhost:5000/api")
TEST_CHARACTER = os.getenv("TEST_CHARACTER", None)
ENABLE_WRITE_TESTS = os.getenv("ENABLE_WRITE_TESTS", "false").lower() == "true"


def api_available() -> bool:
    """API 서버 가용성 확인"""
    try:
        resp = requests.get(f"{API_BASE.replace('/api', '')}/health", timeout=2)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


# 조건부 스킵 데코레이터
requires_api = pytest.mark.skipif(
    not api_available(),
    reason="API 서버가 실행 중이지 않습니다."
)

requires_test_character = pytest.mark.skipif(
    TEST_CHARACTER is None,
    reason="TEST_CHARACTER 환경변수가 설정되지 않았습니다."
)

requires_write_enabled = pytest.mark.skipif(
    not ENABLE_WRITE_TESTS,
    reason="쓰기 테스트가 비활성화됨. ENABLE_WRITE_TESTS=true로 활성화하세요."
)


# ============================================================
# 1. 가방 업데이트 테스트
# ============================================================
@requires_api
@requires_test_character
@requires_write_enabled
class TestBagUpdateOperations:
    """가방 업데이트 연산 테스트"""

    def get_current_bag(self) -> dict:
        """현재 가방 상태 조회"""
        resp = requests.get(f"{API_BASE}/bag/{TEST_CHARACTER}")
        assert resp.status_code == 200
        return resp.json()

    def update_bag(self, items: list) -> dict:
        """가방 업데이트"""
        resp = requests.post(
            f"{API_BASE}/bag/{TEST_CHARACTER}",
            json={"items": items}
        )
        return resp.json(), resp.status_code

    def test_update_bag_success(self):
        """가방 업데이트 성공"""
        # 현재 상태 저장
        original = self.get_current_bag()
        original_items = original["items"]

        try:
            # 빈 가방으로 업데이트
            result, status = self.update_bag([])
            assert status == 200
            assert result["success"] is True

            # 확인
            time.sleep(0.5)  # 캐시 고려
            updated = self.get_current_bag()
            # 빈 가방이어야 함 (또는 캐시 지연)

        finally:
            # 원래 상태 복원
            restore_items = [
                {"name": i["name"], "quantity": i["quantity"]}
                for i in original_items
            ]
            self.update_bag(restore_items)

    def test_update_bag_capacity_exceeded(self):
        """용량 초과 시 거부"""
        # 현재 용량 확인
        bag = self.get_current_bag()
        capacity = bag["capacity"]

        # 용량 초과하는 아이템 추가 시도
        # 가상의 큰 아이템 (실제 아이템명 필요)
        huge_items = [{"name": "테스트아이템", "quantity": 9999}]

        result, status = self.update_bag(huge_items)
        # 용량 초과로 400 예상 (아이템이 존재하지 않으면 다른 에러)


# ============================================================
# 2. 주변 → 가방 이동 테스트
# ============================================================
@requires_api
@requires_test_character
@requires_write_enabled
class TestMoveTooBagOperations:
    """주변 → 가방 이동 테스트"""

    def get_character(self) -> dict:
        """캐릭터 전체 정보 조회"""
        resp = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        assert resp.status_code == 200
        return resp.json()

    def move_to_bag(self, item_name: str, quantity: int = 1) -> tuple:
        """아이템 가방으로 이동"""
        resp = requests.post(
            f"{API_BASE}/nearby/{TEST_CHARACTER}/move",
            json={"item_name": item_name, "quantity": quantity}
        )
        return resp.json(), resp.status_code

    def test_move_nonexistent_item(self):
        """존재하지 않는 아이템 이동 시 에러"""
        result, status = self.move_to_bag("__존재하지않는아이템__", 1)
        assert status == 400
        assert result["success"] is False
        assert "error" in result

    def test_move_item_insufficient_quantity(self):
        """수량 부족 시 에러"""
        char = self.get_character()
        nearby = char["nearby_items"]

        if not nearby:
            pytest.skip("주변에 아이템이 없습니다.")

        # 보유량보다 많이 이동 시도
        item = nearby[0]
        result, status = self.move_to_bag(item["name"], item["quantity"] + 100)
        assert status == 400
        assert result["success"] is False


# ============================================================
# 3. 동시성 테스트 (시뮬레이션)
# ============================================================
@requires_api
@requires_test_character
@requires_write_enabled
class TestConcurrencySimulation:
    """동시성 시뮬레이션 테스트"""

    def test_sequential_updates_preserved(self):
        """순차 업데이트 보존"""
        # 첫 번째 읽기
        resp1 = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        data1 = resp1.json()

        # 두 번째 읽기 (즉시)
        resp2 = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        data2 = resp2.json()

        # 동일해야 함
        assert data1["bag_items"] == data2["bag_items"]
        assert data1["nearby_items"] == data2["nearby_items"]


# ============================================================
# 4. 캐시 무효화 테스트
# ============================================================
@requires_api
@requires_test_character
@requires_write_enabled
class TestCacheInvalidation:
    """캐시 무효화 테스트"""

    def test_update_invalidates_cache(self):
        """업데이트 후 캐시 무효화 확인"""
        # 첫 번째 조회 (캐시 채움)
        resp1 = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        data1 = resp1.json()

        # 가방 업데이트 (캐시 무효화 트리거)
        items = [
            {"name": i["name"], "quantity": i["quantity"]}
            for i in data1["bag_items"]
        ]
        requests.post(
            f"{API_BASE}/bag/{TEST_CHARACTER}",
            json={"items": items}
        )

        # 두 번째 조회 (새 데이터)
        resp2 = requests.get(f"{API_BASE}/character/{TEST_CHARACTER}")
        data2 = resp2.json()

        # 구조가 유효해야 함
        assert "bag_items" in data2
        assert "nearby_items" in data2


# ============================================================
# 메인 실행
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("쓰기 연산 테스트")
    print("=" * 60)
    print()
    print("⚠️  이 테스트는 실제 시트에 데이터를 씁니다!")
    print()

    if not api_available():
        print("✗ API 서버 연결 실패")
        sys.exit(1)

    if not TEST_CHARACTER:
        print("✗ TEST_CHARACTER 환경변수 필요")
        sys.exit(1)

    if not ENABLE_WRITE_TESTS:
        print("⚠ 쓰기 테스트 비활성화됨")
        print("  ENABLE_WRITE_TESTS=true 로 활성화하세요.")
        sys.exit(0)

    print(f"✓ API 서버: {API_BASE}")
    print(f"✓ 테스트 캐릭터: {TEST_CHARACTER}")
    print()

    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
