"""[가방 링크] 명령어 핸들러 — 본인 캐릭터 전용 인벤토리 웹 링크를 DM으로 발급"""

from typing import Any, Dict
from urllib.parse import urlencode

from shared import config
from shared.access_token import is_valid_secret, issue_token
from bot.utils.decorators import require_character
from bot.logger import get_logger

logger = get_logger()

SECONDS_PER_DAY = 86_400


@require_character
def handle(status_id: str, user: str, character: Dict[str, Any], args: list[str]) -> str:
    """요청한 계정의 캐릭터에 대해서만 서명된 링크를 만든다 (응답은 항상 DM)."""
    if not is_valid_secret(config.INVENTORY_LINK_SECRET) or not config.INVENTORY_WEB_URL:
        logger.error("가방 링크: INVENTORY_LINK_SECRET 또는 INVENTORY_WEB_URL 미설정")
        return "인벤토리 링크 기능이 아직 설정되지 않았습니다. 관리자에게 문의해 주세요."

    ttl_days = max(1, config.INVENTORY_LINK_TTL_DAYS)
    token = issue_token(character["name"], config.INVENTORY_LINK_SECRET, ttl_days * SECONDS_PER_DAY)
    # 프래그먼트(#)는 서버로 전송되지 않으므로 웹 호스팅 로그에 토큰이 남지 않는다
    link = f"{config.INVENTORY_WEB_URL.rstrip('/')}/#{urlencode({'token': token})}"

    return "\n".join([
        f"{character['name']}의 개인 인벤토리 링크입니다.",
        f"유효기간 {ttl_days}일 · 다른 사람과 공유하지 마세요.",
        "",
        link,
    ])
