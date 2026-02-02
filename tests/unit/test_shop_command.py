# -*- coding: utf-8 -*-
"""[상점] 명령어 핸들러 단위 테스트"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.commands import shop


class TestShopHandle:
    """shop.handle 단위 테스트"""

    def test_empty_list_returns_no_items_message(self) -> None:
        with patch("bot.commands.shop.list_shop_items", return_value=[]):
            result = shop.handle("status-1", "testuser", [])
            assert result is not None
            assert "구매 가능한 아이템이 없습니다" in result
            assert "@testuser" in result

    def test_one_item_displays_list(self) -> None:
        items = [
            {"name": "힐링 포션", "price": 50, "desc": "체력 회복"},
        ]
        with patch("bot.commands.shop.list_shop_items", return_value=items):
            result = shop.handle("status-1", "testuser", [])
            assert "구매 가능한 아이템 목록" in result
            assert "힐링 포션" in result
            assert "50포인트" in result
            assert "체력 회복" in result
            assert "... 외" not in result

    def test_fifty_items_no_overflow_message(self) -> None:
        items = [{"name": f"아이템{i}", "price": 10, "desc": ""} for i in range(50)]
        with patch("bot.commands.shop.list_shop_items", return_value=items):
            result = shop.handle("status-1", "testuser", [])
            assert "구매 가능한 아이템 목록" in result
            assert "... 외" not in result

    def test_fifty_one_items_shows_overflow(self) -> None:
        items = [{"name": f"아이템{i}", "price": 10, "desc": ""} for i in range(51)]
        with patch("bot.commands.shop.list_shop_items", return_value=items):
            result = shop.handle("status-1", "testuser", [])
            assert "... 외 1개" in result

    def test_list_shop_items_exception_returns_domain_message(self) -> None:
        with patch("bot.commands.shop.list_shop_items", side_effect=RuntimeError("db error")):
            result = shop.handle("status-1", "testuser", [])
            assert result is not None
            assert "상점 조회" in result
            assert "오류" in result
            assert "@testuser" in result
