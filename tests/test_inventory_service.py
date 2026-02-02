# -*- coding: utf-8 -*-
"""인벤토리 서비스 update_stat 단위 테스트 (mock 사용)"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bot.services import inventory_service


def test_update_stat_returns_false_when_character_not_found():
    """캐릭터 없음 시 False 반환"""
    with patch("bot.services.inventory_service.get_character", return_value=None):
        result = inventory_service.update_stat("없는캐", "hp", 5)
    assert result is False


def test_update_stat_returns_false_for_unknown_stat_name():
    """알 수 없는 stat_name 시 False 반환"""
    with patch("bot.services.inventory_service.get_character") as mock_get:
        mock_get.return_value = {"name": "테스트캐", "hp": 10}
        result = inventory_service.update_stat("테스트캐", "unknown_stat", 1)
    assert result is False


def test_update_stat_coerces_string_current_to_int_and_updates():
    """char 스탯이 문자열 '7'인 경우 int 변환 후 7 + delta로 DB에 전달"""
    with patch("bot.services.inventory_service.get_supabase") as mock_supabase:
        mock_execute = MagicMock(return_value=MagicMock(data=[{}]))
        mock_eq = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_update = MagicMock(return_value=MagicMock(eq=mock_eq))
        mock_table = MagicMock(return_value=MagicMock(update=mock_update))
        mock_supabase.return_value = MagicMock(table=mock_table)

        with patch("bot.services.inventory_service.get_character") as mock_get:
            mock_get.return_value = {"name": "테스트캐", "hp": "7"}
            result = inventory_service.update_stat("테스트캐", "hp", 3)

    assert result is True
    mock_update.assert_called_once()
    payload = mock_update.call_args[0][0]
    assert payload == {"hp": 10}


def test_update_stat_success_calls_update_with_correct_column_and_value():
    """정상 stat_name·숫자 시 update 호출 인자 및 True 반환"""
    with patch("bot.services.inventory_service.get_supabase") as mock_supabase:
        mock_execute = MagicMock(return_value=MagicMock(data=[{}]))
        mock_eq = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_update = MagicMock(return_value=MagicMock(eq=mock_eq))
        mock_table = MagicMock(return_value=MagicMock(update=mock_update))
        mock_supabase.return_value = MagicMock(table=mock_table)

        with patch("bot.services.inventory_service.get_character") as mock_get:
            mock_get.return_value = {"name": "테스트캐", "health": 5}
            result = inventory_service.update_stat("테스트캐", "health", -2)

    assert result is True
    mock_update.assert_called_once_with({"con": 3})
    mock_eq.assert_called_once_with("name", "테스트캐")


def test_update_stat_health_column_mapping():
    """health → con 컬럼 매핑 확인"""
    with patch("bot.services.inventory_service.get_supabase") as mock_supabase:
        mock_execute = MagicMock(return_value=MagicMock(data=[{}]))
        mock_eq = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_update = MagicMock(return_value=MagicMock(eq=mock_eq))
        mock_table = MagicMock(return_value=MagicMock(update=mock_update))
        mock_supabase.return_value = MagicMock(table=mock_table)

        with patch("bot.services.inventory_service.get_character") as mock_get:
            mock_get.return_value = {"name": "캐", "health": 1}
            inventory_service.update_stat("캐", "health", 0)

    payload = mock_update.call_args[0][0]
    assert "con" in payload
    assert payload["con"] == 1


def test_update_stat_points_clamped_to_zero():
    """points인 경우 new_value < 0이면 0으로 clamp 후 update 호출"""
    with patch("bot.services.inventory_service.get_supabase") as mock_supabase:
        mock_execute = MagicMock(return_value=MagicMock(data=[{}]))
        mock_eq = MagicMock(return_value=MagicMock(execute=mock_execute))
        mock_update = MagicMock(return_value=MagicMock(eq=mock_eq))
        mock_table = MagicMock(return_value=MagicMock(update=mock_update))
        mock_supabase.return_value = MagicMock(table=mock_table)

        with patch("bot.services.inventory_service.get_character") as mock_get:
            mock_get.return_value = {"name": "캐", "points": 3}
            result = inventory_service.update_stat("캐", "points", -10)

    assert result is True
    mock_update.assert_called_once_with({"points": 0})
    mock_eq.assert_called_once_with("name", "캐")
