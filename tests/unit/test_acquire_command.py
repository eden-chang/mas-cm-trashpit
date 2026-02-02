"""획득 명령어 단위 테스트"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.commands import acquire


class TestAcquireCommand:
    """[획득/아이템명] 명령어 테스트"""
    
    @pytest.fixture
    def mock_character(self):
        """테스트용 캐릭터 픽스처"""
        return {
            'name': '테스트캐릭터',
            'mastodon_id': 'test_user',
            'strength': 5,
            'health': 10,
            'luck': 3,
            'hp': 100,
            'points': 50,
            'bag': {},
            'misc': {},
            'around': {}
        }
    
    @pytest.fixture
    def mock_item_zero_volume(self):
        """부피 0 아이템 픽스처"""
        return {
            'name': '사과',
            'volume': 0,
            'stat': '체력',
            'value': '5',
            'use_msg': '사과를 먹었다!'
        }
    
    @pytest.fixture
    def mock_item_normal(self):
        """일반 아이템 픽스처"""
        return {
            'name': '로프',
            'volume': 2,
            'stat': '',
            'value': '',
            'use_msg': ''
        }
    
    def test_acquire_zero_volume_item_success(self, mock_character, mock_item_zero_volume):
        """부피 0 아이템 획득 시 여유공간에 추가"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=mock_item_zero_volume), \
             patch('bot.commands.acquire.add_item', return_value=True), \
             patch('bot.commands.acquire.get_available_space', return_value=20):
            
            result = acquire.handle("status-1", "test_user", ["사과"])
            
            assert "획득했습니다" in result
            assert "부피 0" in result
            assert "여유공간에 보관" in result
            assert "가방 남은 공간: 20칸" in result
    
    def test_acquire_normal_item_success(self, mock_character, mock_item_normal):
        """일반 아이템 획득 시 주변에 추가"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=mock_item_normal), \
             patch('bot.commands.acquire.add_item', return_value=True), \
             patch('bot.commands.acquire.get_available_space', return_value=18):
            
            result = acquire.handle("status-1", "test_user", ["로프"])
            
            assert "획득했습니다" in result
            assert "부피: 2" in result
            assert "가방 남은 공간: 18칸" in result
            assert "웹에서 가방에 넣으세요" in result
    
    def test_acquire_nonexistent_item_error(self, mock_character):
        """존재하지 않는 아이템 획득 시도"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=None):
            
            result = acquire.handle("status-1", "test_user", ["이상한물건"])
            
            assert "존재하지 않는 아이템" in result
    
    def test_acquire_empty_item_name_error(self, mock_character):
        """빈 아이템명 입력"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = acquire.handle("status-1", "test_user", [])
            
            assert "아이템명을 입력해주세요" in result or "사용법" in result
    
    def test_acquire_whitespace_item_name_error(self, mock_character):
        """공백만 있는 아이템명 입력"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = acquire.handle("status-1", "test_user", ["   "])
            
            assert "아이템명을 입력해주세요" in result
    
    def test_acquire_too_long_item_name_error(self, mock_character):
        """너무 긴 아이템명 입력"""
        long_name = "a" * 100
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = acquire.handle("status-1", "test_user", [long_name])
            
            assert "아이템명이 너무 깁니다" in result
    
    def test_acquire_add_item_failure(self, mock_character, mock_item_normal):
        """add_item 실패 시 시스템 오류 반환"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=mock_item_normal), \
             patch('bot.commands.acquire.add_item', return_value=False):
            
            result = acquire.handle("status-1", "test_user", ["로프"])
            
            assert "시스템 오류" in result or "실패" in result
    
    def test_acquire_db_error_handling(self, mock_character):
        """DB 오류 발생 시 안전한 처리"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', side_effect=Exception("DB Error")):
            
            result = acquire.handle("status-1", "test_user", ["사과"])
            
            assert "오류" in result
            assert "@test_user" in result
