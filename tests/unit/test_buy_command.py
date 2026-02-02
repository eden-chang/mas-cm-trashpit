# -*- coding: utf-8 -*-
"""[구매/아이템명] 명령어 핸들러 단위 테스트"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.commands import buy


class TestBuyHandle:
    """buy.handle 단위 테스트"""

    def test_no_args_returns_usage(self) -> None:
        result = buy.handle("status-1", "testuser", [])
        assert result is not None
        assert "사용법" in result
        assert "[구매/아이템명]" in result

    def test_empty_item_name_returns_usage(self) -> None:
        result = buy.handle("status-1", "testuser", ["   "])
        assert result is not None
        assert "사용법" in result

    def test_item_not_found_returns_message(self) -> None:
        with patch("bot.commands.buy.get_item_info", return_value=None):
            result = buy.handle("status-1", "testuser", ["없는아이템"])
            assert result is not None
            assert "아이템을 찾을 수 없습니다" in result
            assert "상점 목록" in result

    def test_bimaejum_returns_message(self) -> None:
        info = {"name": "비밀 아이템", "price": "비매품", "desc": "", "volume": 0}
        with patch("bot.commands.buy.get_item_info", return_value=info):
            result = buy.handle("status-1", "testuser", ["비밀 아이템"])
            assert result is not None
            assert "비매품으로 구매할 수 없습니다" in result

    def test_quantity_zero_returns_message(self) -> None:
        info = {"name": "사과", "price": 10, "desc": "", "volume": 0}
        with patch("bot.commands.buy.get_item_info", return_value=info):
            result = buy.handle("status-1", "testuser", ["사과", "0"])
            assert "구매 개수는 1 이상" in result

    def test_quantity_over_999_returns_message(self) -> None:
        info = {"name": "사과", "price": 10, "desc": "", "volume": 0}
        with patch("bot.commands.buy.get_item_info", return_value=info):
            result = buy.handle("status-1", "testuser", ["사과", "1000"])
            assert "최대 999개" in result

    def test_quantity_empty_string_returns_message(self) -> None:
        """개수 인자가 빈 문자열이면 '개수는 숫자로…' 메시지."""
        info = {"name": "사과", "price": 10, "desc": "", "volume": 0}
        with patch("bot.commands.buy.get_item_info", return_value=info):
            result = buy.handle("status-1", "testuser", ["사과", ""])
            assert result is not None
            assert "개수" in result and ("숫자" in result or "입력" in result)

    def test_no_character_returns_message(self) -> None:
        info = {"name": "사과", "price": 10, "desc": "", "volume": 0}
        with (
            patch("bot.commands.buy.get_item_info", return_value=info),
            patch("bot.commands.buy.get_character_by_mastodon_id", return_value=None),
        ):
            result = buy.handle("status-1", "testuser", ["사과"])
            assert "등록된 캐릭터를 찾을 수 없습니다" in result

    def test_insufficient_points_returns_message(self) -> None:
        info = {"name": "사과", "price": 100, "desc": "", "volume": 0}
        character = {"name": "테스트캐릭터", "points": 5}
        with (
            patch("bot.commands.buy.get_item_info", return_value=info),
            patch("bot.commands.buy.get_character_by_mastodon_id", return_value=character),
        ):
            result = buy.handle("status-1", "testuser", ["사과"])
            assert "포인트가 부족" in result
            assert "5" in result

    def test_update_stat_deduct_fails_returns_message(self) -> None:
        info = {"name": "사과", "price": 10, "desc": "", "volume": 0}
        character = {"name": "테스트캐릭터", "points": 100}
        with (
            patch("bot.commands.buy.get_item_info", return_value=info),
            patch("bot.commands.buy.get_character_by_mastodon_id", return_value=character),
            patch("bot.commands.buy.update_stat", return_value=False),
        ):
            result = buy.handle("status-1", "testuser", ["사과"])
            assert "포인트 차감" in result or "오류" in result

    def test_add_item_fail_rollback_success_returns_message(self) -> None:
        info = {"name": "사과", "price": 10, "desc": "", "volume": 0}
        character = {"name": "테스트캐릭터", "points": 100}
        with (
            patch("bot.commands.buy.get_item_info", return_value=info),
            patch("bot.commands.buy.get_character_by_mastodon_id", return_value=character),
            patch("bot.commands.buy.update_stat", return_value=True),
            patch("bot.commands.buy.add_item", return_value=False),
        ):
            result = buy.handle("status-1", "testuser", ["사과"])
            assert "아이템 추가에 실패" in result
            assert "포인트는 차감되지 않았습니다" in result

    def test_add_item_fail_rollback_fail_returns_admin_message(self) -> None:
        info = {"name": "사과", "price": 10, "desc": "", "volume": 0}
        character = {"name": "테스트캐릭터", "points": 100}
        update_stat_calls = []

        def update_stat_side_effect(char_name: str, stat: str, delta: int) -> bool:
            update_stat_calls.append((char_name, stat, delta))
            if len(update_stat_calls) == 1:
                return True
            return False

        with (
            patch("bot.commands.buy.get_item_info", return_value=info),
            patch("bot.commands.buy.get_character_by_mastodon_id", return_value=character),
            patch("bot.commands.buy.update_stat", side_effect=update_stat_side_effect),
            patch("bot.commands.buy.add_item", return_value=False),
        ):
            result = buy.handle("status-1", "testuser", ["사과"])
            assert "환불 시도 중 오류" in result or "관리자에게 문의" in result

    def test_success_returns_purchase_message_and_balance(self) -> None:
        info = {"name": "사과", "price": 10, "desc": "", "volume": 0}
        character = {"name": "테스트캐릭터", "points": 100}
        with (
            patch("bot.commands.buy.get_item_info", return_value=info),
            patch("bot.commands.buy.get_character_by_mastodon_id", return_value=character),
            patch("bot.commands.buy.update_stat", return_value=True),
            patch("bot.commands.buy.add_item", return_value=True),
        ):
            result = buy.handle("status-1", "testuser", ["사과"])
            assert "구매했습니다" in result
            assert "사과" in result
            assert "-10포인트" in result
            assert "잔액 90포인트" in result

    def test_success_with_quantity_returns_correct_totals(self) -> None:
        info = {"name": "사과", "price": 10, "desc": "", "volume": 0}
        character = {"name": "테스트캐릭터", "points": 100}
        with (
            patch("bot.commands.buy.get_item_info", return_value=info),
            patch("bot.commands.buy.get_character_by_mastodon_id", return_value=character),
            patch("bot.commands.buy.update_stat", return_value=True),
            patch("bot.commands.buy.add_item", return_value=True),
        ):
            result = buy.handle("status-1", "testuser", ["사과", "3"])
            assert "구매했습니다" in result
            assert "-30포인트" in result
            assert "3개 획득" in result
            assert "잔액 70포인트" in result
