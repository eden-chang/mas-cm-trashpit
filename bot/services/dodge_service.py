"""회피 문구 조회 서비스 (Supabase dodge 테이블)"""

import random
from pathlib import Path
from typing import List

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.supabase_client import get_supabase, TABLE_DODGE
from bot.logger import get_logger

logger = get_logger()

DEFAULT_SUCCESS_MESSAGES = ["회피에 성공했습니다!"]
DEFAULT_FAILURE_MESSAGES = ["회피에 실패했습니다..."]


def get_dodge_texts(success: bool) -> List[str]:
    """
    dodge 테이블에서 success 여부에 맞는 text 목록 반환.

    Args:
        success: True면 성공 문구, False면 실패 문구.

    Returns:
        비어 있지 않으면 선택 가능한 문구 목록 (빈 문자열 제외).
    """
    try:
        supabase = get_supabase()
        response = (
            supabase.table(TABLE_DODGE)
            .select("text")
            .eq("success", success)
            .execute()
        )
        texts = [
            str(row.get("text", "")).strip()
            for row in (response.data or [])
            if row.get("text")
        ]
        return [t for t in texts if t]
    except (ConnectionError, TimeoutError, OSError, RuntimeError, ValueError, KeyError) as e:
        logger.warning("dodge 테이블 조회 실패: %s. 기본 문구 사용.", e)
        return []
    except Exception as e:
        logger.warning("dodge 테이블 조회 중 예기치 않은 오류: %s. 기본 문구 사용.", e)
        return []


def pick_dodge_message(success: bool) -> str:
    """
    성공/실패에 맞는 회피 문구 하나를 랜덤 선택.
    dodge 테이블에 없으면 기본 문구 반환.
    """
    texts = get_dodge_texts(success)
    if texts:
        return random.choice(texts)
    if success:
        return random.choice(DEFAULT_SUCCESS_MESSAGES)
    return random.choice(DEFAULT_FAILURE_MESSAGES)
