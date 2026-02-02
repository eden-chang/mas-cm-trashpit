# -*- coding: utf-8 -*-
"""[설명/아이템명] 명령어 핸들러 단위 테스트"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.commands import item_description


class TestItemDescriptionHandle:
    """item_description.handle 단위 테스트"""

    def test_no_args_returns_usage(self) -> None:
        result = item_description.handle("status-1", "testuser", [])
        assert result is not None
        assert "사용법" in result
        assert "[설명/아이템명]" in result

    def test_empty_item_name_returns_usage(self) -> None:
        result = item_description.handle("status-1", "testuser", ["   "])
        assert result is not None
        assert "사용법" in result

    def test_item_not_found_returns_message(self) -> None:
        with patch("bot.commands.item_description.get_item_info", return_value=None):
            result = item_description.handle("status-1", "testuser", ["없는아이템"])
            assert result is not None
            assert "아이템을 찾을 수 없습니다" in result
            assert "없는아이템" in result

    def test_bimaejum_display(self) -> None:
        info = {"name": "비밀 아이템", "price": "비매품", "desc": "설명", "stat": "", "value": None}
        with patch("bot.commands.item_description.get_item_info", return_value=info):
            result = item_description.handle("status-1", "testuser", ["비밀 아이템"])
            assert "비매품" in result
            assert "비밀 아이템" in result
            assert "설명" in result

    def test_numeric_price_display(self) -> None:
        info = {"name": "힐링 포션", "price": 50, "desc": "체력 회복", "stat": "", "value": None}
        with patch("bot.commands.item_description.get_item_info", return_value=info):
            result = item_description.handle("status-1", "testuser", ["힐링 포션"])
            assert "50" in result
            assert "포인트" in result
            assert "체력 회복" in result

    def test_stat_value_number(self) -> None:
        info = {"name": "물약", "price": 10, "desc": "설명", "stat": "체력", "value": "5"}
        with patch("bot.commands.item_description.get_item_info", return_value=info):
            result = item_description.handle("status-1", "testuser", ["물약"])
            assert "[사용 시 체력 +5]" in result or "체력 +5" in result

    def test_stat_value_dice(self) -> None:
        info = {"name": "물약", "price": 10, "desc": "설명", "stat": "체력", "value": "1d6+2"}
        with patch("bot.commands.item_description.get_item_info", return_value=info):
            result = item_description.handle("status-1", "testuser", ["물약"])
            assert "1d6+2" in result
            assert "사용 시" in result

    def test_price_zero_or_empty_displays_bimaejum(self) -> None:
        """가격이 0이거나 빈 문자열이면 비매품으로 표시."""
        for price in (0, "", "   "):
            info = {"name": "특별 아이템", "price": price, "desc": "설명", "stat": "", "value": None}
            with patch("bot.commands.item_description.get_item_info", return_value=info):
                result = item_description.handle("status-1", "testuser", ["특별 아이템"])
                assert result is not None
                assert "비매품" in result
                assert "특별 아이템" in result

    def test_stat_value_negative_displays_minus(self) -> None:
        """value가 '-5' 등 음수일 때 [사용 시 체력 -5] 형태로 표시."""
        info = {"name": "저주 물약", "price": 10, "desc": "설명", "stat": "체력", "value": "-5"}
        with patch("bot.commands.item_description.get_item_info", return_value=info):
            result = item_description.handle("status-1", "testuser", ["저주 물약"])
            assert result is not None
            assert "[사용 시 체력 -5]" in result or "체력 -5" in result
