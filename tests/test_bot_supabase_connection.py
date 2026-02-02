"""봇 명령 → Supabase 반영 연결성 테스트 (Supabase–웹–봇 계획 3.2, 3.3)

각 마스토돈 봇 명령 실행 후 Supabase에 기대한 대로 반영되는지 검증합니다.
E2E: 봇 명령 후 API 캐시 무효화 → API로 조회해 동일 데이터 확인 (선택).
마스토돈 API 호출(reply)은 mock 처리합니다.

전제 조건 (스킵 시):
- ENABLE_BOT_SUPABASE_TESTS=true
- TEST_CHARACTER: 테스트용 캐릭터 이름 (Supabase characters에 존재)
- TEST_MASTODON_ID: 해당 캐릭터의 마스토돈 계정 ID (id 컬럼)
- TEST_ITEM: items 테이블에 존재하는 테스트용 아이템명
- (양도 수신/지급 수혜자) TEST_CHARACTER_RECEIVER: 다른 캐릭터 이름 (선택)
- E2E: TEST_API_BASE (API 서버 기동 필요)
"""

import os
import sys
from unittest.mock import patch

import pytest
import requests
from dotenv import load_dotenv

# 프로젝트 루트
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)
load_dotenv(os.path.join(_project_root, ".env"))


# ============================================================
# 전제 조건 및 스킵
# ============================================================
ENABLE = os.getenv("ENABLE_BOT_SUPABASE_TESTS", "").lower() == "true"
TEST_CHARACTER = os.getenv("TEST_CHARACTER")
TEST_MASTODON_ID = os.getenv("TEST_MASTODON_ID")
TEST_ITEM = os.getenv("TEST_ITEM")
TEST_CHARACTER_RECEIVER = os.getenv("TEST_CHARACTER_RECEIVER")  # 양도 수신/지급 수혜자


def _bot_tests_configured() -> bool:
    return bool(ENABLE and TEST_CHARACTER and TEST_MASTODON_ID and TEST_ITEM)


requires_bot_supabase = pytest.mark.skipif(
    not _bot_tests_configured(),
    reason=(
        "봇–Supabase 테스트 비활성화. "
        "ENABLE_BOT_SUPABASE_TESTS=true, TEST_CHARACTER, TEST_MASTODON_ID, TEST_ITEM 설정 후 실행."
    ),
)


# ============================================================
# Fixtures: Mastodon mock, character state
# ============================================================
@pytest.fixture(autouse=True)
def mock_mastodon_reply():
    """봇이 reply 호출 시 실제 전송하지 않고 무시."""
    with patch("bot.mastodon_client.reply", lambda status_id, msg, **kw: None), patch(
        "bot.commands.transfer.notify_item_received", lambda *a, **kw: True
    ):
        yield


def _get_character(name: str):
    from bot.services.character_service import get_character
    return get_character(name)


def _count_item(char: dict, item_name: str) -> int:
    """캐릭터 인벤(가방+여유+주변)에서 아이템 수량 합계."""
    if not char:
        return 0
    total = 0
    for key in ("bag", "misc", "around"):
        inv = char.get(key) or {}
        if isinstance(inv, dict):
            total += int(inv.get(item_name, 0) or 0)
    return total


def _get_points(char: dict) -> int:
    if not char:
        return 0
    try:
        return int(char.get("points") or 0)
    except (TypeError, ValueError):
        return 0


# ============================================================
# 1. 획득 [획득/아이템명]
# ============================================================
@requires_bot_supabase
class TestBotAcquire:
    """[획득/아이템명] → Supabase 반영 검증"""

    def test_acquire_success_reflected_in_supabase(self):
        from bot.commands import acquire

        before = _get_character(TEST_CHARACTER)
        count_before = _count_item(before, TEST_ITEM)

        result = acquire.handle("status-1", TEST_MASTODON_ID, [TEST_ITEM])

        assert "등록된 캐릭터를 찾을 수 없습니다" not in result
        assert "존재하지 않는 아이템" not in result
        assert "획득" in result or "실패" not in result

        after = _get_character(TEST_CHARACTER)
        count_after = _count_item(after, TEST_ITEM)
        assert count_after >= count_before + 1, "Supabase에 아이템이 1개 이상 증가해야 함"


# ============================================================
# 2. 버리기 [버리기/아이템명]
# ============================================================
@requires_bot_supabase
class TestBotDiscard:
    """[버리기/아이템명] → Supabase 반영 검증"""

    def test_discard_success_reflected_in_supabase(self):
        from bot.commands import discard
        from bot.services.inventory_service import add_item

        # 소지하지 않으면 버리기 불가이므로, 먼저 1개 추가
        add_item(TEST_CHARACTER, TEST_ITEM, 1, "nearby")
        before = _get_character(TEST_CHARACTER)
        count_before = _count_item(before, TEST_ITEM)
        assert count_before >= 1, "테스트 전 테스트 캐릭터가 해당 아이템을 1개 이상 소지해야 함"

        result = discard.handle("status-1", TEST_MASTODON_ID, [TEST_ITEM])

        assert "가지고 있지 않습니다" not in result
        assert "버렸습니다" in result or "시스템 오류" not in result

        after = _get_character(TEST_CHARACTER)
        count_after = _count_item(after, TEST_ITEM)
        assert count_after == count_before - 1, "Supabase에서 해당 아이템이 1개 감소해야 함"


# ============================================================
# 3. 사용 [사용/아이템명]
# ============================================================
@requires_bot_supabase
class TestBotUse:
    """[사용/아이템명] → Supabase 반영 검증 (아이템 차감)"""

    def test_use_success_reflected_in_supabase(self):
        from bot.commands import use
        from bot.services.inventory_service import add_item

        add_item(TEST_CHARACTER, TEST_ITEM, 1, "nearby")
        before = _get_character(TEST_CHARACTER)
        count_before = _count_item(before, TEST_ITEM)
        assert count_before >= 1

        result = use.handle("status-1", TEST_MASTODON_ID, [TEST_ITEM])

        assert "소지하고 있지 않습니다" not in result
        assert "사용했습니다" in result or "실패" not in result

        after = _get_character(TEST_CHARACTER)
        count_after = _count_item(after, TEST_ITEM)
        assert count_after == count_before - 1, "Supabase에서 아이템 1개 차감 반영"


# ============================================================
# 4. 양도(아이템) [양도/아이템/받는사람]
# ============================================================
@requires_bot_supabase
@pytest.mark.skipif(
    not TEST_CHARACTER_RECEIVER,
    reason="TEST_CHARACTER_RECEIVER가 필요합니다 (양도 수신자).",
)
class TestBotTransferItem:
    """[양도/아이템/받는사람] → Supabase 반영 검증"""

    def test_transfer_item_success_reflected_in_supabase(self):
        from bot.commands import transfer
        from bot.services.inventory_service import add_item

        add_item(TEST_CHARACTER, TEST_ITEM, 1, "nearby")
        sender_before = _count_item(_get_character(TEST_CHARACTER), TEST_ITEM)
        receiver_before = _count_item(_get_character(TEST_CHARACTER_RECEIVER), TEST_ITEM)
        assert sender_before >= 1

        result = transfer.handle_item(
            "status-1", TEST_MASTODON_ID, [TEST_ITEM, TEST_CHARACTER_RECEIVER]
        )

        assert "찾을 수 없습니다" not in result
        assert "양도했습니다" in result or "전달" in result

        sender_after = _count_item(_get_character(TEST_CHARACTER), TEST_ITEM)
        receiver_after = _count_item(_get_character(TEST_CHARACTER_RECEIVER), TEST_ITEM)
        assert sender_after == sender_before - 1
        assert receiver_after == receiver_before + 1


# ============================================================
# 5. 양도(포인트) [양도/n포인트/받는사람]
# ============================================================
@requires_bot_supabase
@pytest.mark.skipif(
    not TEST_CHARACTER_RECEIVER,
    reason="TEST_CHARACTER_RECEIVER가 필요합니다 (포인트 수신자).",
)
class TestBotTransferPoint:
    """[양도/n포인트/받는사람] → Supabase 반영 검증"""

    def test_transfer_point_success_reflected_in_supabase(self):
        from bot.commands import transfer
        from bot.services.character_service import get_character

        sender_before = _get_character(TEST_CHARACTER)
        receiver_before = _get_character(TEST_CHARACTER_RECEIVER)
        points_sender_before = _get_points(sender_before)
        points_receiver_before = _get_points(receiver_before)

        amount = 1
        if points_sender_before < amount:
            pytest.skip(
                f"테스트 캐릭터({TEST_CHARACTER})의 포인트가 {amount} 이상이어야 합니다."
            )

        result = transfer.handle_point(
            "status-1", TEST_MASTODON_ID, [str(amount), TEST_CHARACTER_RECEIVER]
        )

        assert "포인트가 부족합니다" not in result
        assert "양도했습니다" in result or "포인트" in result

        sender_after = _get_character(TEST_CHARACTER)
        receiver_after = _get_character(TEST_CHARACTER_RECEIVER)
        assert _get_points(sender_after) == points_sender_before - amount
        assert _get_points(receiver_after) == points_receiver_before + amount


# ============================================================
# 6. 포인트 추가/차감 [포인트 추가/금액/대상], [포인트 차감/금액/대상] (운영진 전용)
# ============================================================
@requires_bot_supabase
class TestPointsAdmin:
    """[포인트 추가/금액/대상], [포인트 차감/금액/대상] → Supabase 반영 검증 (SYSTEM_ADMIN_IDS mock)"""

    def test_point_add_success_reflected_in_supabase(self):
        from bot.commands import points_admin

        with patch("bot.commands.points_admin.SYSTEM_ADMIN_IDS", [TEST_MASTODON_ID]):
            before = _get_character(TEST_CHARACTER)
            points_before = _get_points(before)

            result = points_admin.handle_add(
                "status-1", TEST_MASTODON_ID, ["10", TEST_CHARACTER]
            )

            assert "포인트 추가 완료" in result
            assert "성공: 1명" in result

            after = _get_character(TEST_CHARACTER)
            points_after = _get_points(after)
            assert points_after == points_before + 10

    def test_point_deduct_success_reflected_in_supabase(self):
        from bot.commands import points_admin

        before = _get_character(TEST_CHARACTER)
        points_before = _get_points(before)
        if points_before < 5:
            pytest.skip(
                f"테스트 캐릭터({TEST_CHARACTER})의 포인트가 5 이상이어야 합니다."
            )

        with patch("bot.commands.points_admin.SYSTEM_ADMIN_IDS", [TEST_MASTODON_ID]):
            result = points_admin.handle_deduct(
                "status-1", TEST_MASTODON_ID, ["5", TEST_CHARACTER]
            )

            assert "포인트 차감 완료" in result
            assert "성공: 1명" in result

            after = _get_character(TEST_CHARACTER)
            points_after = _get_points(after)
            assert points_after == points_before - 5
            assert points_after >= 0

    def test_point_deduct_clamps_to_zero_reflected_in_supabase(self):
        """차감량이 현재 포인트 초과 시 0으로 클램프되고 DB에 반영되는지 검증."""
        from bot.commands import points_admin

        with patch("bot.commands.points_admin.SYSTEM_ADMIN_IDS", [TEST_MASTODON_ID]):
            points_admin.handle_add("status-1", TEST_MASTODON_ID, ["10", TEST_CHARACTER])

        with patch("bot.commands.points_admin.SYSTEM_ADMIN_IDS", [TEST_MASTODON_ID]):
            result = points_admin.handle_deduct(
                "status-1", TEST_MASTODON_ID, ["9999", TEST_CHARACTER]
            )

        assert "포인트 차감 완료" in result
        assert "성공: 1명" in result
        assert "→ 0" in result
        after = _get_character(TEST_CHARACTER)
        assert _get_points(after) == 0


# ============================================================
# 7. 지급 [지급/캐릭터/아이템] (운영진 전용)
# ============================================================
@requires_bot_supabase
class TestBotGrant:
    """[지급/캐릭터/아이템] → Supabase 반영 검증 (SYSTEM_ADMIN_IDS mock)"""

    def test_grant_success_reflected_in_supabase(self):
        from bot.commands import grant

        with patch("bot.commands.grant.SYSTEM_ADMIN_IDS", [TEST_MASTODON_ID]):
            before = _get_character(TEST_CHARACTER)
            count_before = _count_item(before, TEST_ITEM)

            grant.handle("status-1", TEST_MASTODON_ID, [TEST_CHARACTER, TEST_ITEM])

            after = _get_character(TEST_CHARACTER)
            count_after = _count_item(after, TEST_ITEM)
            assert count_after >= count_before + 1, "지급 후 수혜자 인벤에 아이템이 추가되어야 함"


# ============================================================
# E2E: 봇 → Supabase → API (캐시 무효화 후 API 조회)
# ============================================================
API_BASE = os.getenv("TEST_API_BASE", "http://localhost:5000/api")


def _api_available() -> bool:
    try:
        resp = requests.get(API_BASE.replace("/api", "") + "/health", timeout=2)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def _api_invalidate_character_cache() -> None:
    """API 서버의 캐릭터 캐시 무효화 (admin 엔드포인트 호출)."""
    base = API_BASE.replace("/api", "")
    resp = requests.post(base + "/api/admin/characters/refresh", timeout=5)
    if resp.status_code != 200:
        raise RuntimeError(f"캐시 무효화 실패: {resp.status_code} {resp.text}")


def _api_get_character_count_item(name: str, item_name: str) -> int:
    """API GET /character/{name} 응답에서 해당 아이템 수량 합계."""
    resp = requests.get(f"{API_BASE}/character/{name}", timeout=5)
    if resp.status_code != 200:
        raise RuntimeError(f"캐릭터 조회 실패: {resp.status_code}")
    data = resp.json()
    total = 0
    for key in ("bag_items", "misc_items", "nearby_items"):
        for entry in data.get(key) or []:
            if entry.get("name") == item_name:
                total += int(entry.get("quantity") or 0)
    return total


@requires_bot_supabase
@pytest.mark.skipif(
    not _api_available(),
    reason="E2E: API 서버가 실행 중이지 않습니다. TEST_API_BASE 확인.",
)
class TestBotSupabaseApiE2E:
    """봇 명령 → Supabase 반영 → API 조회 시 동일 데이터 확인 (캐시 무효화 후)."""

    def test_acquire_then_api_reflects_same_data(self):
        from bot.commands import acquire

        result = acquire.handle("status-e2e", TEST_MASTODON_ID, [TEST_ITEM])
        assert "등록된 캐릭터를 찾을 수 없습니다" not in result
        assert "존재하지 않는 아이템" not in result

        _api_invalidate_character_cache()
        count_via_api = _api_get_character_count_item(TEST_CHARACTER, TEST_ITEM)
        count_via_db = _count_item(_get_character(TEST_CHARACTER), TEST_ITEM)
        assert count_via_api == count_via_db, (
            f"봇 반영 후 API 조회와 DB 직접 조회가 일치해야 함 "
            f"(API={count_via_api}, DB={count_via_db})"
        )
