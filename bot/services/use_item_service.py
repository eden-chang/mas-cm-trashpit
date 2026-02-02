"""아이템 사용 비즈니스 로직 서비스"""

import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.constants import ManagementColumns, LOCATION_TO_DB_COLUMN
from bot.services.item_service import get_item_info
from bot.services.inventory_service import (
    remove_item,
    find_item_location,
    get_item_count,
    update_stat,
)
from bot.services.transaction_service import use_item_with_transaction, is_transaction_available
from bot.utils.dice import roll_dice
from bot.logger import get_logger

logger = get_logger()

# 아이템 스탯명 -> 관리 시트 컬럼 인덱스
_STAT_COLUMN = {
    "체력": ManagementColumns.HEALTH,
    "근력": ManagementColumns.STRENGTH,
    "행운": ManagementColumns.LUCK,
}

# 스탯 컬럼명 매핑 (Supabase 컬럼명)
_STAT_TO_DB_COLUMN = {
    ManagementColumns.HEALTH: "con",
    ManagementColumns.STRENGTH: "str",
    ManagementColumns.LUCK: "luck",
}

# 트랜잭션 사용 가능 여부 캐시
_transaction_available: Optional[bool] = None


@dataclass
class UseItemResult:
    """아이템 사용 결과"""
    success: bool
    error_code: Optional[str] = None
    applied_delta: Optional[int] = None
    stat_name: Optional[str] = None
    remaining_count: int = 0
    effect_message: str = ""
    item_name: str = ""


def use_item(char_name: str, item_name: str) -> UseItemResult:
    """아이템 사용 비즈니스 로직
    
    트랜잭션이 사용 가능하면 원자적 처리를 수행하고,
    그렇지 않으면 레거시 방식으로 처리합니다.
    
    Args:
        char_name: 캐릭터 이름
        item_name: 아이템명
        
    Returns:
        UseItemResult: 사용 결과
    """
    global _transaction_available
    
    try:
        # 1. 소지 여부 확인
        location = find_item_location(char_name, item_name)
        if not location:
            return UseItemResult(
                success=False,
                error_code="ITEM_NOT_IN_INVENTORY",
                item_name=item_name
            )
        
        # 2. 아이템 정보 조회
        item_info = get_item_info(item_name)
        if not item_info:
            return UseItemResult(
                success=False,
                error_code="ITEM_INFO_NOT_FOUND",
                item_name=item_name
            )
        
        # 3. 스탯 정보 준비
        stat_col = _STAT_COLUMN.get((item_info.get("stat") or "").strip())
        value_raw = item_info.get("value")
        stat_name = (item_info.get("stat") or "").strip()
        applied_delta: Optional[int] = None
        
        if stat_col is not None and value_raw not in (None, ""):
            try:
                applied_delta = roll_dice(str(value_raw).strip())
            except Exception as e:
                logger.error(f"다이스 굴림 오류: {e}", exc_info=True)
                applied_delta = 0
        
        # 4. 트랜잭션 가능 여부 확인 (첫 호출 시만)
        if _transaction_available is None:
            _transaction_available = is_transaction_available()
            logger.info(f"트랜잭션 사용 가능: {_transaction_available}")
        
        # 5. 트랜잭션 또는 레거시 방식으로 처리
        if _transaction_available and applied_delta is not None and applied_delta != 0:
            # 트랜잭션 방식: 아이템 차감 + 스탯 업데이트를 원자적으로
            # RPC는 DB 컬럼명(bag, misc, around)을 기대하므로 봇 키(nearby 등)를 매핑
            location_for_rpc = LOCATION_TO_DB_COLUMN.get(location, location)
            db_column = _STAT_TO_DB_COLUMN.get(stat_col)
            tx_result = use_item_with_transaction(
                char_name=char_name,
                item_name=item_name,
                location=location_for_rpc,
                stat_column=db_column,
                stat_delta=applied_delta
            )
            
            if not tx_result.get('success'):
                logger.error(f"트랜잭션 실패: {tx_result.get('error')}")
                return UseItemResult(
                    success=False,
                    error_code="TRANSACTION_FAILED",
                    item_name=item_name
                )
        else:
            # 레거시 방식: 순차적 처리
            if not remove_item(char_name, item_name, 1, location):
                logger.error(f"remove_item 실패: {char_name}, {item_name}")
                return UseItemResult(
                    success=False,
                    error_code="REMOVE_ITEM_FAILED",
                    item_name=item_name
                )
            
            # 스탯 업데이트 (있는 경우)
            if stat_col is not None and applied_delta is not None and applied_delta != 0:
                if not update_stat(char_name, stat_col, applied_delta):
                    logger.warning(f"update_stat 실패: {char_name}, {stat_col}, {applied_delta}")
        
        # 6. 남은 수량 확인
        remaining = get_item_count(char_name, item_name)
        
        # 7. 효과 메시지 생성
        if applied_delta is not None and stat_name:
            effect_msg = item_info.get("use_msg") or f"효과: {stat_name} {applied_delta:+d}"
        else:
            effect_msg = item_info.get("use_msg") or f"효과: {stat_name} {item_info.get('value', '')}"
        
        return UseItemResult(
            success=True,
            applied_delta=applied_delta,
            stat_name=stat_name,
            remaining_count=remaining,
            effect_message=effect_msg,
            item_name=item_name
        )
        
    except Exception as e:
        logger.error(f"use_item 예외: {e}", exc_info=True)
        return UseItemResult(
            success=False,
            error_code="UNEXPECTED_ERROR",
            item_name=item_name
        )
