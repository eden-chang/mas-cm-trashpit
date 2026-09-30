# -*- coding: utf-8 -*-
"""bot.services.item_service 단위 테스트 (parse_sellable_price, get_item_info 정규화, list_shop_items 정렬)"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def _items_to_rows(items: dict) -> list[dict]:
    """item_service 딕셔너리 형태를 Supabase items 행 형태로 변환"""
    return [
        {
            "name": info["name"],
            "price": info["price"],
            "description": info.get("desc", ""),
            "size": info.get("volume", 0),
        }
        for info in items.values()
    ]


class _FakeQuery:
    """supabase.table(...).select(...).eq(...).limit(...).execute() 체인 흉내"""

    def __init__(self, rows: list[dict]) -> None:
        self._rows = rows

    def select(self, *_args: object) -> "_FakeQuery":
        return self

    def eq(self, column: str, value: object) -> "_FakeQuery":
        return _FakeQuery([r for r in self._rows if r.get(column) == value])

    def limit(self, count: int) -> "_FakeQuery":
        return _FakeQuery(self._rows[:count])

    def execute(self) -> MagicMock:
        return MagicMock(data=self._rows)


def _fake_supabase(items: dict) -> MagicMock:
    client = MagicMock()
    client.table.side_effect = lambda _name: _FakeQuery(_items_to_rows(items))
    return client


class TestGetItemInfoNormalization:
    """get_item_info 이름 정규화 동작 테스트 (Supabase mock)"""

    @pytest.fixture
    def items(self) -> dict:
        return {
            "힐링 포션": {"name": "힐링 포션", "price": 50, "desc": "체력 회복", "volume": 1},
            "마나 포션": {"name": "마나 포션", "price": "비매품", "desc": "마나", "volume": 0},
        }

    def test_exact_match(self, items: dict) -> None:
        with patch.object(item_service, "get_supabase", return_value=_fake_supabase(items)):
            info = item_service.get_item_info("힐링 포션")
            assert info is not None
            assert info["name"] == "힐링 포션"
            assert info["volume"] == 1

    def test_normalized_match_extra_spaces(self, items: dict) -> None:
        with patch.object(item_service, "get_supabase", return_value=_fake_supabase(items)):
            info = item_service.get_item_info("  힐링  포션  ")
            assert info is not None
            assert info["name"] == "힐링 포션"

    def test_not_found_returns_none(self, items: dict) -> None:
        with patch.object(item_service, "get_supabase", return_value=_fake_supabase(items)):
            assert item_service.get_item_info("없는아이템") is None
            assert item_service.get_item_info("") is None

    def test_db_error_returns_none(self) -> None:
        with patch.object(item_service, "get_supabase", side_effect=RuntimeError("down")):
            assert item_service.get_item_info("힐링 포션") is None


class TestListShopItemsSort:
    """list_shop_items 정렬 및 parse_sellable_price 사용 테스트 (Supabase mock)"""

    @pytest.fixture
    def items_unsorted(self) -> dict:
        return {
            "바나나": {"name": "바나나", "price": 10, "desc": "", "volume": 0},
            "사과": {"name": "사과", "price": "비매품", "desc": "", "volume": 0},
            "감": {"name": "감", "price": 5, "desc": "", "volume": 0},
        }

    def test_returns_only_sellable_sorted_by_name(self, items_unsorted: dict) -> None:
        with patch.object(item_service, "get_supabase", return_value=_fake_supabase(items_unsorted)):
            result = item_service.list_shop_items()
            names = [x["name"] for x in result]
            assert names == ["감", "바나나"]
            assert all(x["price"] == int(x["price"]) and x["price"] > 0 for x in result)
