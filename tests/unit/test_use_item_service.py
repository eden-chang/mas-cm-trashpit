# -*- coding: utf-8 -*-
"""use_item_service 단위 테스트 (location → RPC 매핑 검증)"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.services.use_item_service import use_item, UseItemResult


class TestUseItemServiceLocationMapping:
    """RPC 호출 시 봇 location(nearby) → DB 컬럼명(around) 매핑 검증"""

    def test_use_item_calls_rpc_with_around_when_item_in_nearby(self):
        """find_item_location이 'nearby' 반환 시 use_item_with_transaction에 location='around' 전달"""
        with patch("bot.services.use_item_service.find_item_location", return_value="nearby"), \
             patch("bot.services.use_item_service.get_item_info") as mock_get_item, \
             patch("bot.services.use_item_service.is_transaction_available", return_value=True), \
             patch("bot.services.use_item_service.use_item_with_transaction") as mock_tx:
            mock_get_item.return_value = {
                "name": "회복 물약",
                "stat": "체력",
                "value": "1d6",
                "volume": 1,
            }
            mock_tx.return_value = {"success": True, "removed_quantity": 1, "stat_updated": True}

            with patch("bot.services.use_item_service.roll_dice", return_value=5):
                result = use_item("테스트캐", "회복 물약")

        assert result.success is True
        mock_tx.assert_called_once()
        call_kwargs = mock_tx.call_args[1]
        assert call_kwargs["location"] == "around", (
            "RPC must receive DB column name 'around' when item is in 'nearby'"
        )
        assert call_kwargs["char_name"] == "테스트캐"
        assert call_kwargs["item_name"] == "회복 물약"

    def test_use_item_calls_rpc_with_bag_when_item_in_bag(self):
        """find_item_location이 'bag' 반환 시 use_item_with_transaction에 location='bag' 전달"""
        with patch("bot.services.use_item_service.find_item_location", return_value="bag"), \
             patch("bot.services.use_item_service.get_item_info") as mock_get_item, \
             patch("bot.services.use_item_service.is_transaction_available", return_value=True), \
             patch("bot.services.use_item_service.use_item_with_transaction") as mock_tx:
            mock_get_item.return_value = {
                "name": "물약",
                "stat": "체력",
                "value": "3",
                "volume": 1,
            }
            mock_tx.return_value = {"success": True, "removed_quantity": 1, "stat_updated": True}

            with patch("bot.services.use_item_service.roll_dice", return_value=3):
                result = use_item("캐", "물약")

        assert result.success is True
        mock_tx.assert_called_once()
        call_kwargs = mock_tx.call_args[1]
        assert call_kwargs["location"] == "bag"

    def test_use_item_calls_rpc_with_misc_when_item_in_misc(self):
        """find_item_location이 'misc' 반환 시 use_item_with_transaction에 location='misc' 전달"""
        with patch("bot.services.use_item_service.find_item_location", return_value="misc"), \
             patch("bot.services.use_item_service.get_item_info") as mock_get_item, \
             patch("bot.services.use_item_service.is_transaction_available", return_value=True), \
             patch("bot.services.use_item_service.use_item_with_transaction") as mock_tx:
            mock_get_item.return_value = {
                "name": "과일",
                "stat": "체력",
                "value": "2",
                "volume": 0,
            }
            mock_tx.return_value = {"success": True, "removed_quantity": 1, "stat_updated": True}

            with patch("bot.services.use_item_service.roll_dice", return_value=2):
                result = use_item("캐", "과일")

        assert result.success is True
        mock_tx.assert_called_once()
        call_kwargs = mock_tx.call_args[1]
        assert call_kwargs["location"] == "misc"
