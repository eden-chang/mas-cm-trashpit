"""마스토돈 API 클라이언트"""

import time
from mastodon import Mastodon

from .config import MASTODON_API_BASE_URL, BOT_ACCESS_TOKEN
from .logger import get_logger

logger = get_logger()

_client = None


def get_client() -> Mastodon:
    """마스토돈 클라이언트 반환 (싱글톤)"""
    global _client

    if _client is None:
        _client = Mastodon(
            access_token=BOT_ACCESS_TOKEN,
            api_base_url=MASTODON_API_BASE_URL,
        )
        logger.system_event("마스토돈 클라이언트 초기화 완료", "success")

    return _client


def reinit_client():
    """마스토돈 클라이언트 재초기화"""
    global _client
    _client = None
    return get_client()


def reply(status_id: str, message: str, visibility: str = "unlisted"):
    """답글 전송 (재시도 로직 포함)"""
    max_retries = 3
    retry_delays = [10, 30, 60]

    for attempt in range(max_retries):
        try:
            client = get_client()

            # 메시지 길이 제한 (500자)
            if len(message) > 500:
                message = message[:497] + "..."
                logger.warning("메시지가 500자를 초과하여 잘림")

            status = client.status(status_id)
            client.status_reply(
                to_status=status,
                status=message,
                visibility=visibility,
            )
            return

        except Exception as e:
            logger.error(f"답글 전송 실패 (시도 {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                logger.api_retry("마스토돈", delay, attempt + 1)
                time.sleep(delay)
                reinit_client()
            else:
                logger.error(f"답글 전송 최종 실패: {e}")


def send_dm(message: str):
    """DM 전송"""
    try:
        client = get_client()
        client.status_post(message, visibility="direct")
    except Exception as e:
        logger.error(f"DM 전송 실패: {e}")


def get_notifications(since_id=None):
    """멘션 알림 조회 (재시도 로직 포함)"""
    max_retries = 3
    retry_delays = [5, 15, 30]

    for attempt in range(max_retries):
        try:
            client = get_client()
            return client.notifications(
                types=["mention"],
                since_id=since_id,
            )

        except Exception as e:
            logger.error(f"알림 조회 실패 (시도 {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                logger.api_retry("마스토돈", delay, attempt + 1)
                time.sleep(delay)
                reinit_client()
            else:
                logger.error(f"알림 조회 최종 실패: {e}")
                return []

    return []
