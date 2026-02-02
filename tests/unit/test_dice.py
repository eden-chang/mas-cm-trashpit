# -*- coding: utf-8 -*-
"""bot.utils.dice (is_dice_expression, roll_dice) 단위 테스트"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from bot.utils.dice import is_dice_expression, roll_dice


class TestIsDiceExpression:
    """is_dice_expression 경계 케이스"""

    @pytest.mark.parametrize("value", ["1d6", "2d6+3", "1d10-2", "-(1d6+3)", "2D6+1"])
    def test_valid_dice_expressions(self, value: str) -> None:
        assert is_dice_expression(value) is True

    @pytest.mark.parametrize("value", ["1d", "d6", "1d6+", "x1d6", "", "   ", "5"])
    def test_invalid_or_non_dice(self, value: str) -> None:
        assert is_dice_expression(value) is False

    def test_none_returns_false(self) -> None:
        assert is_dice_expression(None) is False  # type: ignore[arg-type]
