# -*- coding: utf-8 -*-
"""포인트 추가/차감 명령어 유닛 테스트"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bot.commands import points_admin


# ============================================================
# _parse_amount
# ============================================================
class TestParseAmount:
    def test_none_returns_none(self):
        assert points_admin._parse_amount(None) is None

    def test_empty_string_returns_none(self):
        assert points_admin._parse_amount("") is None

    def test_whitespace_only_returns_none(self):
        assert points_admin._parse_amount("   ") is None

    def test_plain_number(self):
        assert points_admin._parse_amount("10") == 10

    def test_number_with_suffix(self):
        assert points_admin._parse_amount("10포인트") == 10

    def test_whitespace_around_number(self):
        assert points_admin._parse_amount(" 5 ") == 5

    def test_comma_separated_number_parsed_as_integer(self):
        assert points_admin._parse_amount("100,000") == 100_000

    def test_negative_returns_none(self):
        assert points_admin._parse_amount("-5") is None

    def test_no_digit_returns_none(self):
        assert points_admin._parse_amount("abc") is None


# ============================================================
# _resolve_targets
# ============================================================
class TestResolveTargets:
    def test_empty_string_returns_empty_list(self):
        assert points_admin._resolve_targets("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert points_admin._resolve_targets("   ") == []

    def test_single_target(self):
        assert points_admin._resolve_targets("A") == ["A"]

    def test_two_targets_comma_separated(self):
        assert points_admin._resolve_targets("A,B") == ["A", "B"]

    def test_targets_with_whitespace(self):
        assert points_admin._resolve_targets(" A , B ") == ["A", "B"]

    def test_duplicate_targets_preserved_in_resolve(self):
        """_resolve_targets returns list as-is; dedupe happens in _run_operation."""
        assert points_admin._resolve_targets("A,A") == ["A", "A"]


# ============================================================
# handle_add / handle_deduct (authorization, args, mocks)
# ============================================================
@patch("bot.commands.points_admin.SYSTEM_ADMIN_IDS", ["admin_user"])
class TestHandleAddDeductAuthorization:
    def test_handle_add_unauthorized_user(self):
        out = points_admin.handle_add("status-1", "normal_user", ["10", "Char"])
        assert "운영진만 사용할 수 있습니다" in out

    def test_handle_deduct_unauthorized_user(self):
        out = points_admin.handle_deduct("status-1", "normal_user", ["5", "Char"])
        assert "운영진만 사용할 수 있습니다" in out


@patch("bot.commands.points_admin.SYSTEM_ADMIN_IDS", ["admin_user"])
class TestHandleAddDeductArgsValidation:
    def test_handle_add_args_too_short(self):
        out = points_admin.handle_add("status-1", "admin_user", ["10"])
        assert "사용법" in out and "포인트 추가" in out

    def test_handle_deduct_args_too_short(self):
        out = points_admin.handle_deduct("status-1", "admin_user", [])
        assert "사용법" in out

    def test_handle_add_amount_zero(self):
        out = points_admin.handle_add("status-1", "admin_user", ["0", "Char"])
        assert "양의 정수" in out

    def test_handle_add_amount_no_digit_returns_validation_message(self):
        out = points_admin.handle_add("status-1", "admin_user", ["-", "Char"])
        assert "양의 정수" in out or "금액" in out

    def test_handle_add_amount_non_numeric(self):
        out = points_admin.handle_add("status-1", "admin_user", ["abc", "Char"])
        assert "양의 정수" in out

    def test_handle_add_empty_targets(self):
        out = points_admin.handle_add("status-1", "admin_user", ["10", "  "])
        assert "대상 캐릭터를 입력해 주세요" in out

    def test_handle_add_amount_exceeds_cap(self):
        out = points_admin.handle_add(
            "status-1", "admin_user", ["2000000", "Char"]
        )
        assert "허용 상한" in out or "1,000,000" in out

    def test_handle_add_negative_amount_rejected(self):
        out = points_admin.handle_add("status-1", "admin_user", ["-5", "Char"])
        assert "양의 정수" in out


@patch("bot.commands.points_admin.update_stat")
@patch("bot.commands.points_admin.get_character")
@patch("bot.commands.points_admin.SYSTEM_ADMIN_IDS", ["admin_user"])
class TestHandleAddWithMocks:
    def test_add_success_single_target(self, mock_get_character, mock_update_stat):
        mock_get_character.return_value = {"points": 100}
        mock_update_stat.return_value = True

        out = points_admin.handle_add("status-1", "admin_user", ["10", "CharA"])

        assert "포인트 추가 완료" in out
        assert "성공: 1명" in out
        assert "CharA" in out
        assert "100 → 110" in out
        mock_get_character.assert_called_once_with("CharA")
        mock_update_stat.assert_called_once_with("CharA", "points", 10)

    def test_add_character_not_found(self, mock_get_character, mock_update_stat):
        mock_get_character.return_value = None

        out = points_admin.handle_add("status-1", "admin_user", ["10", "Unknown"])

        assert "실패: 1명" in out
        assert "캐릭터를 찾을 수 없습니다" in out
        mock_update_stat.assert_not_called()

    def test_add_update_stat_fails(self, mock_get_character, mock_update_stat):
        mock_get_character.return_value = {"points": 50}
        mock_update_stat.return_value = False

        out = points_admin.handle_add("status-1", "admin_user", ["10", "CharA"])

        assert "실패: 1명" in out
        assert "업데이트 실패" in out

    def test_add_duplicate_targets_applied_once(self, mock_get_character, mock_update_stat):
        mock_get_character.return_value = {"points": 100}
        mock_update_stat.return_value = True

        out = points_admin.handle_add("status-1", "admin_user", ["10", "CharA,CharA"])

        assert "포인트 추가 완료" in out
        assert "동일 대상 중복은 한 번만 적용했습니다" in out
        assert "성공: 1명" in out
        mock_get_character.assert_called_once_with("CharA")
        mock_update_stat.assert_called_once_with("CharA", "points", 10)


@patch("bot.commands.points_admin.update_stat")
@patch("bot.commands.points_admin.get_character")
@patch("bot.commands.points_admin.SYSTEM_ADMIN_IDS", ["admin_user"])
class TestHandleDeductWithMocks:
    def test_deduct_success_single_target(self, mock_get_character, mock_update_stat):
        mock_get_character.return_value = {"points": 100}
        mock_update_stat.return_value = True

        out = points_admin.handle_deduct("status-1", "admin_user", ["30", "CharA"])

        assert "포인트 차감 완료" in out
        assert "성공: 1명" in out
        assert "CharA" in out
        assert "100 → 70" in out
        mock_update_stat.assert_called_once_with("CharA", "points", -30)

    def test_deduct_clamps_to_zero(self, mock_get_character, mock_update_stat):
        mock_get_character.return_value = {"points": 10}
        mock_update_stat.return_value = True

        out = points_admin.handle_deduct("status-1", "admin_user", ["50", "CharA"])

        assert "10 → 0" in out
        mock_update_stat.assert_called_once_with("CharA", "points", -10)

    def test_deduct_character_not_found(self, mock_get_character, mock_update_stat):
        mock_get_character.return_value = None

        out = points_admin.handle_deduct("status-1", "admin_user", ["5", "Unknown"])

        assert "실패: 1명" in out
        assert "캐릭터를 찾을 수 없습니다" in out
