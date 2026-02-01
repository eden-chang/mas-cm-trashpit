"""Phase 1.3 용량 계산 규칙 테스트"""

import pytest
from unittest.mock import patch

from shared.capacity import (
    calculate_capacity,
    parse_inventory,
    calculate_used_volume,
)
from shared.constants import get_bag_capacity
from shared.models import Item


class TestCalculateCapacity:
    """근력별 용량 계산"""

    @pytest.mark.parametrize(
        "strength,expected",
        [
            (1, 20),
            (3, 20),
            (5, 20),
            (6, 40),
            (8, 40),
            (10, 40),
            (11, 60),
            (13, 60),
            (15, 60),
            (16, 80),
            (18, 80),
            (20, 80),
        ],
    )
    def test_valid_strength_ranges(self, strength: int, expected: int) -> None:
        assert calculate_capacity(strength) == expected
        assert get_bag_capacity(strength) == expected

    def test_default_for_out_of_range(self) -> None:
        assert calculate_capacity(0) == 20
        assert calculate_capacity(21) == 20
        assert calculate_capacity(100) == 20


class TestParseInventory:
    """인벤토리 문자열 파싱"""

    def test_empty_string(self) -> None:
        assert parse_inventory("") == []
        assert parse_inventory("   ") == []
        assert parse_inventory("\n") == []

    def test_basic_format(self) -> None:
        result = parse_inventory("사과: 3, 물병: 2")
        assert result == [
            Item(name="사과", quantity=3),
            Item(name="물병", quantity=2),
        ]

    def test_no_spaces(self) -> None:
        result = parse_inventory("사과:3,물병:2")
        assert result == [
            Item(name="사과", quantity=3),
            Item(name="물병", quantity=2),
        ]

    def test_single_item(self) -> None:
        result = parse_inventory("손전등: 1")
        assert result == [Item(name="손전등", quantity=1)]

    def test_item_without_quantity(self) -> None:
        result = parse_inventory("반지")
        assert result == [Item(name="반지", quantity=1)]

    def test_invalid_quantity_falls_back_to_one(self) -> None:
        result = parse_inventory("아이템: abc")
        assert result == [Item(name="아이템", quantity=1)]


class TestCalculateUsedVolume:
    """가방 사용량 계산"""

    @patch("shared.item_master.get_item_info")
    def test_single_item(self, mock_get_item_info: object) -> None:
        item_info = type("ItemInfo", (), {"volume": 3})()
        mock_get_item_info.return_value = item_info

        result = calculate_used_volume("손전등: 1")
        assert result == 3

    @patch("shared.item_master.get_item_info")
    def test_multiple_items(self, mock_get_item_info: object) -> None:
        def get_vol(name: str):
            vols = {"사과": 1, "물병": 2, "손전등": 3}
            info = type("ItemInfo", (), {"volume": vols.get(name, 0)})()
            return info

        mock_get_item_info.side_effect = get_vol

        result = calculate_used_volume("사과: 3, 물병: 2, 손전등: 1")
        assert result == (1 * 3) + (2 * 2) + (3 * 1)  # 3 + 4 + 3 = 10

    @patch("shared.item_master.get_item_info")
    def test_unknown_item_treated_as_zero_volume(self, mock_get_item_info: object) -> None:
        mock_get_item_info.return_value = None

        result = calculate_used_volume("미지의아이템: 5")
        assert result == 0

    @patch("shared.item_master.get_item_info")
    def test_empty_inventory(self, mock_get_item_info: object) -> None:
        result = calculate_used_volume("")
        assert result == 0
        mock_get_item_info.assert_not_called()
