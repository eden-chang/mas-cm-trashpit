"""아이템 서비스 (Supabase 버전 - 캐시 적용)

아이템 데이터는 자주 변경되지 않으므로 캐싱 적용.
"""

import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.supabase_client import get_supabase, TABLE_ITEMS
from shared.config import CACHE_TTL
from bot.logger import get_logger

logger = get_logger()

# 캐시 저장소
_items_cache: Dict[str, Dict[str, Any]] = {}
_cache_time: float = 0


def _is_cache_valid() -> bool:
    """캐시 유효성 확인 (TTL 기반)"""
    return _cache_time > 0 and (time.time() - _cache_time) < CACHE_TTL


def _load_items_cache() -> None:
    """Supabase에서 전체 아이템 로드"""
    global _items_cache, _cache_time
    try:
        supabase = get_supabase()
        response = supabase.table(TABLE_ITEMS).select("*").execute()

        _items_cache = {}
        for row in response.data:
            name = (row.get("name") or "").strip()
            if not name:
                continue

            raw_size = row.get("size")
            try:
                volume = int(raw_size) if raw_size is not None else 0
            except (ValueError, TypeError):
                volume = 0

            _items_cache[name] = {
                'name': name,
                'price': row.get("price", ""),
                'desc': row.get("description", ""),
                'use_msg': row.get("use_script", ""),
                'stat': row.get("change_stats", ""),
                'value': row.get("change_value", ""),
                'volume': max(0, volume),
            }

        _cache_time = time.time()
        logger.info("아이템 캐시 로드 완료: %d개 아이템", len(_items_cache))
    except Exception as e:
        logger.error("아이템 캐시 로드 실패: %s", e)
        raise


def get_item_info(item_name: str) -> Optional[Dict[str, Any]]:
    """아이템 정보 조회 (캐시 사용)"""
    if not _is_cache_valid():
        _load_items_cache()

    return _items_cache.get(item_name)


def refresh_cache() -> None:
    """캐시 강제 새로고침"""
    global _cache_time
    _cache_time = 0
    _load_items_cache()
