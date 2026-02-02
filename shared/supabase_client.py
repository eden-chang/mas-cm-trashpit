"""Supabase 클라이언트 싱글톤 모듈"""

import logging
from typing import Optional

from supabase import create_client, Client

from . import config

logger = logging.getLogger(__name__)

_client: Optional[Client] = None


def get_supabase() -> Client:
    """Supabase 클라이언트 반환 (싱글톤)"""
    global _client

    if _client is None:
        try:
            _client = create_client(
                config.SUPABASE_URL,
                config.SUPABASE_SERVICE_KEY
            )
            logger.info("Supabase 클라이언트 초기화 완료")
        except Exception as e:
            logger.error("Supabase 클라이언트 초기화 실패: %s", e)
            raise

    return _client


# 테이블 이름 상수
TABLE_CHARACTERS = "characters"
TABLE_ITEMS = "items"
TABLE_DODGE = "dodge"
