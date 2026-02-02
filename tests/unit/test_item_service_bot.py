# -*- coding: utf-8 -*-
"""bot.services.item_service 단위 테스트 (parse_sellable_price, get_item_info 정규화, list_shop_items 정렬)"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.services import item_service


class TestParseSellablePrice:
    """parse_sellable_price 단위 테스트"""

    def test_none_returns_none(self) -> None:
        assert item_service.parse_sellable_price(None) is None

    def test_bimaejum_returns_none(self) -> None:
        assert item_service.parse_sellable_price("비매품") is None
        assert item_service.parse_sellable_price("  비매품  ") is None

    def test_empty_string_returns_none(self) -> None:
        assert item_service.parse_sellable_price("") is None
        assert item_service.parse_sellable_price("   ") is None

    def test_positive_integer_string(self) -> None:
        assert item_service.parse_sellable_price("100") == 100
        assert item_service.parse_sellable_price("  50  ") == 50

    def test_positive_int(self) -> None:
        assert item_service.parse_sellable_price(100) == 100
        assert item_service.parse_sellable_price(1) == 1

    def test_zero_or_negative_returns_none(self) -> None:
        assert item_service.parse_sellable_price(0) is None
        assert item_service.parse_sellable_price(-1) is None
        assert item_service.parse_sellable_price("-5") is None
        assert item_service.parse_sellable_price("0") is None

    def test_float_coerced_to_int(self) -> None:
        assert item_service.parse_sellable_price(99.9) == 99
        assert item_service.parse_sellable_price("99.9") == 99

    def test_invalid_returns_none(self) -> None:
        assert item_service.parse_sellable_price("abc") is None
        assert item_service.parse_sellable_price([]) is None


class TestGetItemInfoNormalization:
    """get_item_info 이름 정규화 동작 테스트 (캐시 mock)"""

    @pytest.fixture
    def mock_cache(self) -> dict:
        return {
            "힐링 포션": {
                "name": "힐링 포션",
                "price": 50,
                "desc": "체력 회복",
                "volume": 1,
            },
            "마나 포션": {
                "name": "마나 포션",
                "price": "비매품",
                "desc": "마나",
                "volume": 0,
            },
        }

    def test_exact_match(self, mock_cache: dict) -> None:
        with (
            patch.object(item_service, "_items_cache", mock_cache),
            patch.object(item_service, "_is_cache_valid", return_value=True),
        ):
            info = item_service.get_item_info("힐링 포션")
            assert info is not None
            assert info["name"] == "힐링 포션"

    def test_normalized_match_extra_spaces(self, mock_cache: dict) -> None:
        with (
            patch.object(item_service, "_items_cache", mock_cache),
            patch.object(item_service, "_is_cache_valid", return_value=True),
        ):
            info = item_service.get_item_info("  힐링  포션  ")
            assert info is not None
            assert info["name"] == "힐링 포션"

    def test_not_found_returns_none(self, mock_cache: dict) -> None:
        with (
            patch.object(item_service, "_items_cache", mock_cache),
            patch.object(item_service, "_is_cache_valid", return_value=True),
        ):
            assert item_service.get_item_info("없는아이템") is None
            assert item_service.get_item_info("") is None


class TestListShopItemsSort:
    """list_shop_items 정렬 및 parse_sellable_price 사용 테스트 (캐시 mock)"""

    @pytest.fixture
    def mock_cache_unsorted(self) -> dict:
        return {
            "바나나": {"name": "바나나", "price": 10, "desc": "", "volume": 0},
            "사과": {"name": "사과", "price": "비매품", "desc": "", "volume": 0},
            "감": {"name": "감", "price": 5, "desc": "", "volume": 0},
        }

    def test_returns_only_sellable_sorted_by_name(self, mock_cache_unsorted: dict) -> None:
        with (
            patch.object(item_service, "_items_cache", mock_cache_unsorted),
            patch.object(item_service, "_is_cache_valid", return_value=True),
        ):
            result = item_service.list_shop_items()
            names = [x["name"] for x in result]
            assert names == ["감", "바나나"]
            assert all(x["price"] == int(x["price"]) and x["price"] > 0 for x in result)
