"""스케줄러 모듈

Phase 5.1 문서에 따른 주변 아이템 자동 삭제 스케줄러
- 매일 0시: 주변 아이템 삭제 + 알림
- 매일 23시: 삭제 1시간 전 경고 알림
"""

import sys
from pathlib import Path
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# 한국 시간대 (KST = UTC+9)
try:
    from zoneinfo import ZoneInfo
    KST = ZoneInfo("Asia/Seoul")
except ImportError:
    # Python 3.8 이하 호환
    import pytz
    KST = pytz.timezone("Asia/Seoul")

# 프로젝트 루트를 PYTHONPATH에 추가
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

from api.services.sheet_service import get_all_characters, update_nearby_items
from bot.notifications import notify_cleanup_warning, notify_cleanup_done
from bot.logger import get_logger

logger = get_logger()

_scheduler = None


def _format_items(items: list[dict]) -> str:
    """아이템 목록을 문자열로 포맷"""
    return ", ".join(f"{item['name']}x{item['quantity']}" for item in items)


def cleanup_nearby_items():
    """주변 아이템 자동 삭제 (매일 0시 KST 실행)"""
    logger.info("[%s] 주변 아이템 자동 삭제 시작", datetime.now().isoformat())

    try:
        characters = get_all_characters()
        deleted_count = 0

        for char in characters:
            if not char.nearby_items:
                continue

            # 삭제할 아이템 기록
            items = [{"name": i.name, "quantity": i.quantity} for i in char.nearby_items]
            item_count = sum(item["quantity"] for item in items)

            logger.info(
                "[%s] 주변 아이템 %d개 삭제: %s",
                char.name, item_count, _format_items(items)
            )

            # 먼저 삭제 실행
            success = update_nearby_items(char.name, [])
            if success:
                deleted_count += 1
                # 삭제 성공 후 알림 전송 (알림 실패해도 삭제는 완료됨)
                notify_cleanup_done(char.mastodon_id, items)
            else:
                logger.error("[%s] 주변 아이템 삭제 실패", char.name)

        logger.info("[%s] 완료. 삭제된 캐릭터: %d명", datetime.now().isoformat(), deleted_count)

    except Exception as e:
        logger.exception("주변 아이템 삭제 중 오류: %s", e)


def warn_before_cleanup():
    """삭제 1시간 전 경고 알림 (매일 23시 KST 실행)"""
    logger.info("[%s] 주변 아이템 삭제 경고 시작", datetime.now().isoformat())

    try:
        characters = get_all_characters()
        warned_count = 0

        for char in characters:
            if not char.nearby_items:
                continue

            items = [{"name": i.name, "quantity": i.quantity} for i in char.nearby_items]

            logger.info("[%s] 삭제 경고: %s", char.name, _format_items(items))

            # 경고 알림 전송
            if notify_cleanup_warning(char.mastodon_id, items):
                warned_count += 1

        logger.info("[%s] 완료. 경고 전송: %d명", datetime.now().isoformat(), warned_count)

    except Exception as e:
        logger.exception("삭제 경고 전송 중 오류: %s", e)


def get_scheduler() -> BackgroundScheduler:
    """스케줄러 인스턴스 반환 (싱글톤)"""
    global _scheduler

    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone=KST)

        # 매일 0시 KST: 주변 아이템 삭제
        _scheduler.add_job(
            cleanup_nearby_items,
            CronTrigger(hour=0, minute=0, timezone=KST),
            id="cleanup_nearby",
            replace_existing=True,
        )

        # 매일 23시 KST: 삭제 경고
        _scheduler.add_job(
            warn_before_cleanup,
            CronTrigger(hour=23, minute=0, timezone=KST),
            id="warn_cleanup",
            replace_existing=True,
        )

        logger.info("스케줄러 작업 등록 완료 (KST 기준)")
        logger.info("  - cleanup_nearby: 매일 0시 KST")
        logger.info("  - warn_cleanup: 매일 23시 KST")

    return _scheduler


def start_scheduler():
    """스케줄러 시작"""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.system_event("스케줄러 시작", "start")


def stop_scheduler():
    """스케줄러 중지"""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        logger.system_event("스케줄러 중지", "stop")
        _scheduler = None
