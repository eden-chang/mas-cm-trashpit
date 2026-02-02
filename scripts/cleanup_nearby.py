"""
주변 아이템 자동 삭제 스크립트

매일 0시에 실행되도록 cron에 등록하거나,
수동 실행 시 모든 캐릭터의 'around' 컬럼(주변 아이템)을 비웁니다.

사용 예:
    # 프로젝트 루트에서 실행
    python scripts/cleanup_nearby.py
    # 또는 --dry-run으로 실제 변경 없이 시뮬레이션
    python scripts/cleanup_nearby.py --dry-run
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

from dotenv import load_dotenv

load_dotenv()

from api.services.sheet_service import get_all_characters, update_nearby_items

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def cleanup_nearby_items(dry_run: bool = False) -> int:
    """
    모든 캐릭터의 주변 아이템을 비웁니다.

    Args:
        dry_run: True면 실제 변경 없이 시뮬레이션만 수행

    Returns:
        삭제된 캐릭터 수
    """
    characters = get_all_characters()
    cleared_count = 0

    for char in characters:
        if not char.nearby_items:
            continue

        item_count = sum(i.quantity for i in char.nearby_items)
        logger.info(
            "[%s] 주변 아이템 %d개 발견: %s",
            char.name,
            item_count,
            ", ".join(f"{i.name}x{i.quantity}" for i in char.nearby_items),
        )

        if not dry_run:
            success = update_nearby_items(char.name, [])
            if success:
                cleared_count += 1
                logger.info("[%s] 주변 아이템 삭제 완료", char.name)
            else:
                logger.error("[%s] 주변 아이템 삭제 실패", char.name)
        else:
            cleared_count += 1

    return cleared_count


def main() -> None:
    parser = argparse.ArgumentParser(description="주변 아이템 자동 삭제")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 변경 없이 시뮬레이션만 수행",
    )
    args = parser.parse_args()

    logger.info(
        "[%s] 주변 아이템 자동 삭제 시작 (dry_run=%s)",
        datetime.now().isoformat(),
        args.dry_run,
    )

    try:
        cleared = cleanup_nearby_items(dry_run=args.dry_run)
        logger.info(
            "[%s] 완료. 삭제된 캐릭터: %d명",
            datetime.now().isoformat(),
            cleared,
        )
    except Exception as e:
        logger.exception("주변 아이템 삭제 중 오류 발생: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
