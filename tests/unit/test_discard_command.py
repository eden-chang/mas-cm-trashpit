"""버리기 명령어 단위 테스트"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.commands import discard
from shared.constants import ErrorMessages


class TestDiscardCommand:
    """[버리기/아이템명] 명령어 테스트"""
    
    @pytest.fixture
    def mock_character(self):
        """테스트용 캐릭터 픽스처"""
        return {
            'name': '테스트캐릭터',
            'mastodon_id': 'test_user',
            'strength': 5,
            'bag': {'사과': 2},
            'misc': {},
            'around': {}
        }
    
    def test_discard_success_from_bag(self, mock_character):
        """가방에서 아이템 버리기 성공"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.discard.find_item_location', return_value='bag'), \
             patch('bot.commands.discard.remove_item', return_value=True):
            
            result = discard.handle("status-1", "test_user", ["사과"])
            
            assert "버렸습니다" in result
            assert "사과" in result
    
    def test_discard_success_from_nearby(self, mock_character):
        """주변에서 아이템 버리기 성공"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.discard.find_item_location', return_value='nearby'), \
             patch('bot.commands.discard.remove_item', return_value=True):
            
            result = discard.handle("status-1", "test_user", ["돌멩이"])
            
            assert "버렸습니다" in result
    
    def test_discard_item_not_in_inventory(self, mock_character):
        """소지하지 않은 아이템 버리기 시도"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.discard.find_item_location', return_value=None):
            
            result = discard.handle("status-1", "test_user", ["칼"])
            
            assert "가지고 있지 않습니다" in result or "소지하고 있지 않습니다" in result
    
    def test_discard_empty_args(self, mock_character):
        """인자 없이 명령어 실행"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = discard.handle("status-1", "test_user", [])
            
            assert "아이템명을 입력해주세요" in result or "사용법" in result
    
    def test_discard_whitespace_item_name(self, mock_character):
        """공백만 있는 아이템명"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = discard.handle("status-1", "test_user", ["   "])
            
            assert "아이템명을 입력해주세요" in result
    
    def test_discard_too_long_item_name(self, mock_character):
        """너무 긴 아이템명"""
        long_name = "x" * 100
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = discard.handle("status-1", "test_user", [long_name])
            
            assert "아이템명이 너무 깁니다" in result
    
    def test_discard_remove_item_failure(self, mock_character):
        """remove_item 실패 시 SYSTEM_ERROR 메시지 반환"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.discard.find_item_location', return_value='bag'), \
             patch('bot.commands.discard.remove_item', return_value=False):
            
            result = discard.handle("status-1", "test_user", ["사과"])
            
            assert result == ErrorMessages.SYSTEM_ERROR.format(user="test_user")
    
    def test_discard_db_error_handling(self, mock_character):
        """DB 오류 발생 시 안전한 처리"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.discard.find_item_location', side_effect=Exception("DB Error")):
            
            result = discard.handle("status-1", "test_user", ["사과"])
            
            assert "오류" in result
