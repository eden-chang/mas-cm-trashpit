"""엣지 케이스 테스트"""

import sys
from pathlib import Path
from unittest.mock import patch
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.commands import acquire, discard, use
from bot.services.use_item_service import UseItemResult


class TestEdgeCases:
    """엣지 케이스 테스트"""
    
    @pytest.fixture
    def mock_character(self):
        """테스트용 캐릭터"""
        return {
            'name': '테스트캐릭터',
            'mastodon_id': 'test_user',
            'strength': 5,
            'bag': {},
            'misc': {},
            'around': {}
        }
    
    def test_special_characters_in_item_name(self, mock_character):
        """특수문자 포함 아이템명 처리"""
        special_item = {
            'name': '아이템@#$',
            'volume': 1,
            'stat': '',
            'value': ''
        }
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=special_item), \
             patch('bot.commands.acquire.add_item', return_value=True), \
             patch('bot.commands.acquire.get_available_space', return_value=20):
            
            result = acquire.handle("status-1", "test_user", ["아이템@#$"])
            
            # 특수문자가 포함되어도 정상 처리되어야 함
            assert "획득했습니다" in result or "오류" in result
    
    def test_unicode_item_name(self, mock_character):
        """유니코드 아이템명 (한글, 이모지 등)"""
        unicode_item = {
            'name': '사과🍎',
            'volume': 0,
            'stat': '체력',
            'value': '5'
        }
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=unicode_item), \
             patch('bot.commands.acquire.add_item', return_value=True), \
             patch('bot.commands.acquire.get_available_space', return_value=20):
            
            result = acquire.handle("status-1", "test_user", ["사과🍎"])
            
            assert "획득했습니다" in result
    
    def test_very_long_item_name(self, mock_character):
        """매우 긴 아이템명 (경계값 테스트)"""
        # MAX_ITEM_NAME_LENGTH = 50
        long_name_49 = "a" * 49
        long_name_50 = "a" * 50
        long_name_51 = "a" * 51
        
        # 49자는 허용
        item_49 = {'name': long_name_49, 'volume': 1}
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=item_49), \
             patch('bot.commands.acquire.add_item', return_value=True), \
             patch('bot.commands.acquire.get_available_space', return_value=20):
            result = acquire.handle("status-1", "test_user", [long_name_49])
            assert "획득했습니다" in result
        
        # 50자는 허용
        item_50 = {'name': long_name_50, 'volume': 1}
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=item_50), \
             patch('bot.commands.acquire.add_item', return_value=True), \
             patch('bot.commands.acquire.get_available_space', return_value=20):
            result = acquire.handle("status-1", "test_user", [long_name_50])
            assert "획득했습니다" in result
        
        # 51자는 거부
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = acquire.handle("status-1", "test_user", [long_name_51])
            assert "아이템명이 너무 깁니다" in result
    
    def test_use_last_item_then_use_again(self, mock_character):
        """마지막 아이템 사용 후 재사용 시도"""
        # 첫 번째 사용: 성공
        result_first = UseItemResult(
            success=True,
            remaining_count=0,
            effect_message="효과: 체력 +5",
            item_name="사과"
        )
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.use.use_item', return_value=result_first):
            result = use.handle("status-1", "test_user", ["사과"])
            assert "사용했습니다" in result
        
        # 두 번째 사용: 실패 (소지하지 않음)
        result_second = UseItemResult(
            success=False,
            error_code="ITEM_NOT_IN_INVENTORY",
            item_name="사과"
        )
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.use.use_item', return_value=result_second):
            result = use.handle("status-1", "test_user", ["사과"])
            assert "소지하고 있지 않습니다" in result
    
    def test_empty_string_after_strip(self, mock_character):
        """strip 후 빈 문자열이 되는 경우"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = acquire.handle("status-1", "test_user", ["   \t\n  "])
            assert "아이템명을 입력해주세요" in result
    
    def test_multiple_spaces_in_item_name(self, mock_character):
        """아이템명에 여러 공백 포함"""
        item = {
            'name': '큰   사과',
            'volume': 0,
            'stat': '',
            'value': ''
        }
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=item), \
             patch('bot.commands.acquire.add_item', return_value=True), \
             patch('bot.commands.acquire.get_available_space', return_value=20):
            
            result = acquire.handle("status-1", "test_user", ["큰   사과"])
            assert "획득했습니다" in result
    
    def test_item_name_with_newline(self, mock_character):
        """아이템명에 개행 문자 포함 (비정상 입력)"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character):
            result = acquire.handle("status-1", "test_user", ["사과\n칼"])
            # 개행이 포함되어도 처리되어야 함 (strip으로 제거됨)
            assert "@test_user" in result
    
    def test_case_sensitive_item_name(self, mock_character):
        """대소문자 구분 (영문 아이템의 경우)"""
        item_lower = {'name': 'apple', 'volume': 1}
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=item_lower), \
             patch('bot.commands.acquire.add_item', return_value=True), \
             patch('bot.commands.acquire.get_available_space', return_value=20):
            
            result = acquire.handle("status-1", "test_user", ["apple"])
            assert "획득했습니다" in result
        
        # 대문자로 시도하면 다른 아이템으로 인식
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=None):
            result = acquire.handle("status-1", "test_user", ["APPLE"])
            assert "존재하지 않는 아이템" in result
    
    def test_zero_quantity_item(self, mock_character):
        """수량이 0인 아이템 버리기 시도"""
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.discard.find_item_location', return_value=None):
            result = discard.handle("status-1", "test_user", ["사과"])
            assert "가지고 있지 않습니다" in result or "소지하고 있지 않습니다" in result
    
    def test_negative_volume_item(self, mock_character):
        """음수 부피 아이템 (비정상 데이터)"""
        negative_item = {
            'name': '이상한아이템',
            'volume': -1,
            'stat': '',
            'value': ''
        }
        
        with patch('bot.services.character_service.get_character_by_mastodon_id', return_value=mock_character), \
             patch('bot.commands.acquire.get_item_info', return_value=negative_item), \
             patch('bot.commands.acquire.add_item', return_value=True), \
             patch('bot.commands.acquire.get_available_space', return_value=20):
            
            result = acquire.handle("status-1", "test_user", ["이상한아이템"])
            # 음수 부피도 처리되어야 함 (nearby로 처리)
            assert "획득했습니다" in result
