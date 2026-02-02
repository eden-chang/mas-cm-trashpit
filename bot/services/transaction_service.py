"""트랜잭션 처리 서비스

Supabase RPC를 사용하여 원자적 트랜잭션을 처리합니다.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.supabase_client import get_supabase
from bot.logger import get_logger

logger = get_logger()


def use_item_with_transaction(
    char_name: str,
    item_name: str,
    location: str,
    stat_column: Optional[str] = None,
    stat_delta: Optional[int] = None
) -> Dict[str, Any]:
    """아이템 사용을 트랜잭션으로 처리
    
    아이템 차감과 스탯 업데이트를 원자적으로 수행합니다.
    
    Args:
        char_name: 캐릭터 이름
        item_name: 아이템명
        location: 인벤토리 위치 ('bag', 'misc', 'around')
        stat_column: 업데이트할 스탯 컬럼 ('con', 'str', 'luck', 'hp')
        stat_delta: 스탯 변화량
        
    Returns:
        트랜잭션 결과 딕셔너리
        {
            'success': bool,
            'error': str (실패 시),
            'removed_quantity': int (성공 시),
            'stat_updated': bool (성공 시)
        }
    """
    try:
        supabase = get_supabase()
        
        # Supabase RPC 함수 호출
        result = supabase.rpc(
            'use_item_transaction',
            {
                'p_char_name': char_name,
                'p_item_name': item_name,
                'p_location': location,
                'p_stat_column': stat_column,
                'p_stat_delta': stat_delta
            }
        ).execute()
        
        if result.data:
            return result.data
        else:
            logger.error(f"트랜잭션 RPC 호출 결과 없음: {char_name}, {item_name}")
            return {
                'success': False,
                'error': 'NO_RESULT'
            }
            
    except Exception as e:
        logger.error(f"트랜잭션 처리 중 예외: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'EXCEPTION',
            'message': str(e)
        }


def is_transaction_available() -> bool:
    """트랜잭션 RPC 함수가 사용 가능한지 확인
    
    Returns:
        사용 가능 여부
    """
    try:
        supabase = get_supabase()
        # 테스트 호출 (존재하지 않는 캐릭터로)
        result = supabase.rpc(
            'use_item_transaction',
            {
                'p_char_name': '__test__',
                'p_item_name': '__test__',
                'p_location': 'bag',
                'p_stat_column': None,
                'p_stat_delta': None
            }
        ).execute()
        
        # 함수가 존재하면 호출은 성공 (결과는 실패일 수 있음)
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        if 'function' in error_msg and 'does not exist' in error_msg:
            logger.warning("트랜잭션 RPC 함수가 아직 생성되지 않았습니다. 레거시 방식을 사용합니다.")
            return False
        else:
            logger.error(f"트랜잭션 가용성 확인 중 오류: {e}")
            return False
