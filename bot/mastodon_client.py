"""마스토돈 API 클라이언트"""

from mastodon import Mastodon

from .config import MASTODON_API_BASE_URL, BOT_ACCESS_TOKEN

_client = None


def get_client() -> Mastodon:
    """마스토돈 클라이언트 반환 (싱글톤)"""
    global _client

    if _client is None:
        _client = Mastodon(
            access_token=BOT_ACCESS_TOKEN,
            api_base_url=MASTODON_API_BASE_URL,
        )

    return _client


def reply(status_id: str, message: str, visibility: str = "unlisted"):
    """답글 전송"""
    client = get_client()
    status = client.status(status_id)
    client.status_reply(
        to_status=status,
        status=message,
        visibility=visibility,
    )


def get_notifications(since_id=None):
    """멘션 알림 조회"""
    client = get_client()
    return client.notifications(
        types=["mention"],
        since_id=since_id,
    )
