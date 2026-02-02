"""입력 검증 유틸리티

명령어 인자의 유효성을 검증하는 함수들을 제공합니다.
"""

from typing import Tuple, Optional
from shared.constants import MAX_ITEM_NAME_LENGTH


def validate_item_name(item_name: str) -> Tuple[bool, Optional[str]]:
    """아이템명 검증
    
    Args:
        item_name: 검증할 아이템명
        
    Returns:
        (유효 여부, 에러 메시지)
        유효하면 (True, None), 무효하면 (False, "에러 메시지")
    """
    if not item_name or not item_name.strip():
        return False, "아이템명을 입력해주세요."
    
    if len(item_name) > MAX_ITEM_NAME_LENGTH:
        return False, f"아이템명이 너무 깁니다. (최대 {MAX_ITEM_NAME_LENGTH}자)"
    
    return True, None


def validate_args_not_empty(args: list, min_length: int = 1) -> Tuple[bool, Optional[str]]:
    """명령어 인자가 비어있지 않은지 검증
    
    Args:
        args: 명령어 인자 리스트
        min_length: 최소 인자 개수
        
    Returns:
        (유효 여부, 에러 메시지)
    """
    if not args or len(args) < min_length:
        return False, f"인자가 부족합니다. (최소 {min_length}개 필요)"
    
    return True, None
