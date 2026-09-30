# -*- coding: utf-8 -*-
"""스탯 변경 명령어 handle 단위 테스트 (mock 사용)"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bot.commands import stat_change


def test_handle_args_too_short_returns_usage():
    """args 부족 시 사용법 메시지 반환"""
    result = stat_change.handle("sid", "user", [])
    assert result is not None
    assert "@user" in result
    assert "사용법" in result
    assert "[스탯명/숫자]" in result

    result = stat_change.handle("sid", "user", ["hp"])
    assert result is not None
    assert "사용법" in result


def test_handle_non_numeric_delta_returns_error():
    """숫자가 아닌 delta 시 '숫자를 입력해 주세요' 반환"""
    result = stat_change.handle("sid", "user", ["hp", "abc"])
    assert result is not None
    assert "@user" in result
    assert "숫자를 입력해 주세요" in result

    result = stat_change.handle("sid", "user", ["체력", "x"])
    assert "숫자를 입력해 주세요" in result


def test_handle_unsupported_stat_returns_error():
    """지원하지 않는 스탯명 시 '지원 스탯: …' 반환"""
    result = stat_change.handle("sid", "user", ["unknown", "5"])
    assert result is not None
    assert "@user" in result
    assert "지원 스탯" in result
    assert "hp" in result and "체력" in result


@patch("bot.commands.stat_change.get_character_by_mastodon_id", return_value=None)
def test_handle_no_character_returns_error(mock_get_char):
    """캐릭터 없음 시 '등록된 캐릭터를 찾을 수 없습니다' 반환"""
    result = stat_change.handle("sid", "user", ["hp", "3"])
    mock_get_char.assert_called_once_with("user")
    assert result is not None
    assert "@user" in result
    assert "등록된 캐릭터를 찾을 수 없습니다" in result


@patch("bot.commands.stat_change.update_stat", return_value=False)
@patch("bot.commands.stat_change.get_character_by_mastodon_id")
def test_handle_update_stat_failure_returns_error(mock_get_char, mock_update):
    """update_stat 실패 시 '스탯 변경에 실패했습니다' 반환"""
    mock_get_char.return_value = {"name": "테스트캐", "hp": 10}
    result = stat_change.handle("sid", "user", ["hp", "3"])
    mock_update.assert_called_once_with("테스트캐", "hp", 3)
    assert result is not None
    assert "@user" in result
    assert "스탯 변경에 실패했습니다" in result


@patch("bot.commands.stat_change.update_stat", return_value=True)
@patch("bot.commands.stat_change.get_character_by_mastodon_id")
def test_handle_success_hp_message(mock_get_char, mock_update):
    """HP 변경 성공 시 'HP이(가) 10 → 13으로 변경되었습니다' 형태"""
    mock_get_char.return_value = {"name": "테스트캐", "hp": 10}
    result = stat_change.handle("sid", "user", ["hp", "3"])
    mock_update.assert_called_once_with("테스트캐", "hp", 3)
    assert result is not None
    assert "@user" in result
    assert "HP" in result
    assert "10" in result and "13" in result
    assert "변경되었습니다" in result


@patch("bot.commands.stat_change.update_stat", return_value=True)
@patch("bot.commands.stat_change.get_character_by_mastodon_id")
def test_handle_success_health_display_name(mock_get_char, mock_update):
    """체력 변경 성공 시 표시명 '체력' 사용"""
    mock_get_char.return_value = {"name": "테스트캐", "health": 5}
    result = stat_change.handle("sid", "user", ["체력", "-2"])
    mock_update.assert_called_once_with("테스트캐", "health", -2)
    assert "체력" in result
    assert "5" in result and "3" in result


@patch("bot.commands.stat_change.update_stat", return_value=True)
@patch("bot.commands.stat_change.get_character_by_mastodon_id")
def test_handle_success_strength_display_name(mock_get_char, mock_update):
    """근력 변경 성공 시 표시명 '근력' 사용"""
    mock_get_char.return_value = {"name": "테스트캐", "strength": 2}
    result = stat_change.handle("sid", "user", ["근력", "1"])
    mock_update.assert_called_once_with("테스트캐", "strength", 1)
    assert "근력" in result
    assert "2" in result and "3" in result


@patch("bot.commands.stat_change.update_stat", return_value=True)
@patch("bot.commands.stat_change.get_character_by_mastodon_id")
def test_handle_success_luck_display_name(mock_get_char, mock_update):
    """행운 변경 성공 시 표시명 '행운' 사용"""
    mock_get_char.return_value = {"name": "테스트캐", "luck": 7}
    result = stat_change.handle("sid", "user", ["행운", "-1"])
    mock_update.assert_called_once_with("테스트캐", "luck", -1)
    assert "행운" in result
    assert "7" in result and "6" in result


@patch("bot.commands.stat_change.update_stat", return_value=True)
@patch("bot.commands.stat_change.get_character_by_mastodon_id")
def test_handle_delta_zero_skips_update(mock_get_char, mock_update):
    """delta가 0인 경우 [hp/0]: 입력 단계에서 거부하고 update_stat을 호출하지 않는다"""
    mock_get_char.return_value = {"name": "테스트캐", "hp": 10}
    result = stat_change.handle("sid", "user", ["hp", "0"])
    mock_update.assert_not_called()
    assert result is not None
    assert "@user" in result
    assert "0이 아닌 숫자" in result
