"""Phase 1.2 아이템 마스터 단위 테스트"""

import pytest

from shared.models import ItemInfo
from shared.item_master import (
    record_to_item_info,
    is_usable,
    is_misc_item,
)


class TestRecordToItemInfo:
    """record_to_item_info 검증"""

    def test_valid_record_returns_item_info(self) -> None:
        record = {
            "아이템명": "반지",
            "가격": 70,
            "설명": "은반지",
            "사용문구": "반지가 빛난다.",
            "스탯": "근력",
            "수치": "10",
            "부피": "0",
        }
        info = record_to_item_info(record)
        assert info.name == "반지"
        assert info.price == 70
        assert info.volume == 0

    def test_empty_name_raises_value_error(self) -> None:
        record = {"아이템명": "", "가격": 0, "설명": "", "사용문구": "", "스탯": "", "수치": "", "부피": "0"}
        with pytest.raises(ValueError, match="아이템명이 없습니다"):
            record_to_item_info(record)

    def test_whitespace_only_name_raises_value_error(self) -> None:
        record = {"아이템명": "   ", "가격": 0, "설명": "", "사용문구": "", "스탯": "", "수치": "", "부피": "1"}
        with pytest.raises(ValueError, match="아이템명이 없습니다"):
            record_to_item_info(record)

    def test_non_sellable_price(self) -> None:
        record = {
            "아이템명": "아몬드",
            "가격": "비매품",
            "설명": "",
            "사용문구": "먹는다",
            "스탯": "체력",
            "수치": "-(1d6+3)",
            "부피": "0",
        }
        info = record_to_item_info(record)
        assert info.price == "비매품"
        assert info.value == "-(1d6+3)"
        assert info.volume == 0

    def test_negative_volume_clamped_to_zero(self) -> None:
        record = {
            "아이템명": "버그아이템",
            "가격": 0,
            "설명": "",
            "사용문구": "",
            "스탯": "사용 불가",
            "수치": "",
            "부피": "-1",
        }
        info = record_to_item_info(record)
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
