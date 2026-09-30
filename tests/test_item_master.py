"""Phase 1.2 아이템 마스터 단위 테스트"""

import pytest

from shared.models import ItemInfo
from shared.item_master import (
    _row_to_item_info,
    is_usable,
    is_misc_item,
)


def _row(**overrides: object) -> dict:
    row = {
        "name": "반지",
        "price": "70",
        "description": "은반지",
        "use_script": "반지가 빛난다.",
        "change_stats": "근력",
        "change_value": "10",
        "size": 0,
    }
    row.update(overrides)
    return row


class TestRowToItemInfo:
    """items 테이블 행 → ItemInfo 변환 검증"""

    def test_valid_row_returns_item_info(self) -> None:
        info = _row_to_item_info(_row())
        assert info.name == "반지"
        assert info.price == 70
        assert info.use_message == "반지가 빛난다."
        assert info.stat == "근력"
        assert info.value == "10"
        assert info.volume == 0

    def test_empty_name_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="아이템명이 비어 있습니다"):
            _row_to_item_info(_row(name=""))

    def test_whitespace_only_name_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="아이템명이 비어 있습니다"):
            _row_to_item_info(_row(name="   "))

    def test_non_sellable_price(self) -> None:
        info = _row_to_item_info(_row(name="아몬드", price="비매품", change_value="-(1d6+3)"))
        assert info.price == "비매품"
        assert info.value == "-(1d6+3)"

    def test_invalid_price_defaults_to_zero(self) -> None:
        assert _row_to_item_info(_row(price="abc")).price == 0

    def test_negative_volume_clamped_to_zero(self) -> None:
        assert _row_to_item_info(_row(size=-1)).volume == 0

    def test_missing_optional_fields_become_empty(self) -> None:
        info = _row_to_item_info({"name": "돌"})
        assert info.description == ""
        assert info.use_message == ""
        assert info.volume == 0


class TestIsUsable:
    """is_usable 검증 (문서 1.2: 사용문구 있음 + 스탯 != 사용 불가)"""

    def test_usable_when_message_and_stat_ok(self) -> None:
        info = ItemInfo(name="x", use_message="쓴다", stat="체력", value="5")
        assert is_usable(info) is True

    def test_not_usable_when_no_message(self) -> None:
        info = ItemInfo(name="x", use_message="", stat="체력", value="5")
        assert is_usable(info) is False

    def test_not_usable_when_stat_disabled(self) -> None:
        info = ItemInfo(name="x", use_message="쓴다", stat="사용 불가", value="")
        assert is_usable(info) is False

    def test_not_usable_when_message_is_dash(self) -> None:
        info = ItemInfo(name="x", use_message="-", stat="체력", value="1")
        assert is_usable(info) is False


class TestIsMiscItem:
    """is_misc_item 검증 (부피 0 = 여유공간)"""

    def test_volume_zero_is_misc(self) -> None:
        info = ItemInfo(name="x", volume=0)
        assert is_misc_item(info) is True

    def test_volume_nonzero_not_misc(self) -> None:
        info = ItemInfo(name="x", volume=1)
        assert is_misc_item(info) is False
