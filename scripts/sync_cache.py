"""
캐시 동기화/프리로드 스크립트

API 서버나 봇이 메모리 캐시를 사용하는 경우,
Supabase 데이터를 미리 로드하여 캐시를 워밍업합니다.

사용 예:
    python scripts/sync_cache.py
"""

import logging
import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def preload_data() -> dict:
    """
    Supabase 데이터를 프리로드하고 아이템 캐시를 새로고침합니다.

    Returns:
        로드된 데이터 요약
    """
    from api.services.sheet_service import get_all_characters
    from api.services.item_service import get_all_items, refresh_cache

    refresh_cache()
    characters = get_all_characters()
    items = get_all_items()

    summary = {
        "characters": len(characters),
        "items": len(items),
    }

    logger.info("프리로드 완료: 캐릭터 %d명, 아이템 %d개", summary["characters"], summary["items"])
    return summary


def main() -> None:
    logger.info("캐시 동기화 시작")

    try:
        preload_data()
        logger.info("캐시 동기화 완료")
    except Exception as e:
        logger.exception("캐시 동기화 중 오류 발생: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
