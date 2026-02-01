"""아이템 서비스 (상점 시트 - 캐시 적용)

상점 데이터는 자주 변경되지 않으므로 CACHE_TTL(3600초) 캐싱 적용.
"""

import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.google_sheets import get_worksheet
from shared.constants import SHEET_NAMES, ShopColumns
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
    """상점 시트에서 전체 아이템 로드"""
    global _items_cache, _cache_time
    try:
        ws = get_worksheet(SHEET_NAMES['SHOP'])
        records = ws.get_all_records()[1:]  # 2행 정보행 스킵

        _items_cache = {}
        for record in records:
            name = (record.get("아이템명") or "").strip()
            if not name:
                continue

            raw_volume = record.get("부피")
            try:
                volume = int(raw_volume) if raw_volume not in (None, "") else 0
            except (ValueError, TypeError):
                volume = 0

            _items_cache[name] = {
                'name': name,
                'price': record.get("가격", ""),
                'desc': record.get("설명", ""),
                'use_msg': record.get("사용문구", ""),
                'stat': record.get("스탯", ""),
                'value': record.get("수치", ""),
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
