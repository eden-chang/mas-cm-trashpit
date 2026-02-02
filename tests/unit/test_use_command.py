"""사용 명령어 단위 테스트"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.commands import use
from bot.services.use_item_service import UseItemResult
from shared.constants import ErrorMessages


class TestUseCommand:
    """[사용/아이템명] 명령어 테스트"""
    
    @pytest.fixture
    def mock_character(self):
        """테스트용 캐릭터 픽스처"""
        return {
            'name': '테스트캐릭터',
            'mastodon_id': 'test_user',
            'strength': 5,
            'health': 10,
            'hp': 100,
            'bag': {'회복 물약': 3},
            'misc': {},
            'around': {}
        }
    
    def test_use_item_success_with_effect(self, mock_character):
        """아이템 사용 성공 (효과 있음)"""
        result_obj = UseItemResult(
            success=True,
            applied_delta=7,
            stat_name="체력",
            remaining_count=2,
            effect_message="효과: 체력 +7",
            item_name="회복 물약"
        )
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.use.use_item', return_value=result_obj):
            result = use.handle("status-1", "test_user", ["회복 물약"])
            
            assert "사용했습니다" in result
            assert "회복 물약" in result
            assert "남은 수량: 2" in result
    
    def test_use_item_success_last_item(self, mock_character):
        """마지막 아이템 사용"""
        result_obj = UseItemResult(
            success=True,
            applied_delta=5,
            stat_name="체력",
            remaining_count=0,
            effect_message="효과: 체력 +5",
            item_name="사과"
        )
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.use.use_item', return_value=result_obj):
            result = use.handle("status-1", "test_user", ["사과"])
            
            assert "사용했습니다" in result
            assert "남은 수량" not in result or "0" not in result
    
    def test_use_item_not_in_inventory(self, mock_character):
        """소지하지 않은 아이템 사용 시도"""
        result_obj = UseItemResult(
            success=False,
            error_code="ITEM_NOT_IN_INVENTORY",
            item_name="칼"
        )
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.use.use_item', return_value=result_obj):
            result = use.handle("status-1", "test_user", ["칼"])
            
            assert "소지하고 있지 않습니다" in result
    
    def test_use_item_info_not_found(self, mock_character):
        """아이템 정보를 찾을 수 없음"""
        result_obj = UseItemResult(
            success=False,
            error_code="ITEM_INFO_NOT_FOUND",
            item_name="이상한물건"
        )
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.use.use_item', return_value=result_obj):
            result = use.handle("status-1", "test_user", ["이상한물건"])
            
            assert "정보를 찾을 수 없습니다" in result
    
    def test_use_empty_args(self, mock_character):
        """인자 없이 명령어 실행"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = use.handle("status-1", "test_user", [])
            
            assert "아이템명을 입력해주세요" in result or "사용법" in result
    
    def test_use_whitespace_item_name(self, mock_character):
        """공백만 있는 아이템명"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = use.handle("status-1", "test_user", ["   "])
            
            assert "아이템명을 입력해주세요" in result
    
    def test_use_too_long_item_name(self, mock_character):
        """너무 긴 아이템명"""
        long_name = "y" * 100
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = use.handle("status-1", "test_user", [long_name])
            
            assert "아이템명이 너무 깁니다" in result
    
    def test_use_system_error(self, mock_character):
        """시스템 오류 발생"""
        result_obj = UseItemResult(
            success=False,
            error_code="REMOVE_ITEM_FAILED",
            item_name="사과"
        )
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.use.use_item', return_value=result_obj):
            result = use.handle("status-1", "test_user", ["사과"])
            
            assert result == ErrorMessages.SYSTEM_ERROR.format(user="test_user")
    
    def test_use_transaction_failed_returns_transaction_error_message(self, mock_character):
        """TRANSACTION_FAILED 시 TRANSACTION_ERROR 메시지 반환"""
        result_obj = UseItemResult(
            success=False,
            error_code="TRANSACTION_FAILED",
            item_name="물약"
        )
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.use.use_item', return_value=result_obj):
            result = use.handle("status-1", "test_user", ["물약"])
            
            assert result == ErrorMessages.TRANSACTION_ERROR.format(user="test_user")
    
    def test_use_unexpected_error(self, mock_character):
        """예상치 못한 오류 시 DB_ERROR 메시지 반환"""
        result_obj = UseItemResult(
            success=False,
            error_code="UNEXPECTED_ERROR",
            item_name="사과"
        )
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.use.use_item', return_value=result_obj):
            result = use.handle("status-1", "test_user", ["사과"])
            
            assert result == ErrorMessages.DB_ERROR.format(user="test_user")
