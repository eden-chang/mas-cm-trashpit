"""마스토돈 봇 메인 진입점"""

import re
import sys
import time
import logging

# 상위 디렉토리 import를 위한 경로 추가
sys.path.insert(0, str(__file__).rsplit("\\", 2)[0])

from bot.config import POLLING_INTERVAL
from bot.mastodon_client import get_notifications, reply
from bot.commands import use, give, discard, acquire

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 명령어 패턴
PATTERNS = {
    "use": re.compile(r"\[사용/([^\]]+)\]"),
    "give_item": re.compile(r"\[양도/([^\]/]+)/([^\]]+)\]"),
    "give_point": re.compile(r"\[양도/(\d+)포인트/([^\]]+)\]"),
    "discard": re.compile(r"\[버리기/([^\]]+)\]"),
    "acquire": re.compile(r"\[획득/([^\]]+)\]"),
}

# 명령어 핸들러 매핑
HANDLERS = {
    "use": use.handle,
    "give_item": give.handle_item,
    "give_point": give.handle_point,
    "discard": discard.handle,
    "acquire": acquire.handle,
}


def parse_command(content: str) -> tuple[str, list] | None:
    """명령어 파싱"""
    # HTML 태그 제거
    content = re.sub(r"<[^>]+>", "", content)

    for cmd_type, pattern in PATTERNS.items():
        match = pattern.search(content)
        if match:
            return (cmd_type, list(match.groups()))

    return None


def on_notification(notification: dict):
    """멘션 알림 처리"""
    if notification["type"] != "mention":
        return

    status = notification["status"]
    content = status["content"]
    user = notification["account"]["acct"]
    status_id = status["id"]

    # 명령어 파싱
    result = parse_command(content)
    if not result:
        return

    cmd_type, args = result
    logger.info(f"명령어 감지: {cmd_type} from @{user}, args={args}")

    # 핸들러 실행
    handler = HANDLERS.get(cmd_type)
    if handler:
        try:
            handler(status_id, user, args)
        except Exception as e:
            logger.error(f"명령어 처리 오류: {e}")
            reply(status_id, f"@{user} 오류가 발생했습니다: {e}")


def main():
    """메인 폴링 루프"""
    logger.info("봇 시작...")
    last_id = None

    while True:
        try:
            notifications = get_notifications(since_id=last_id)

            for notif in reversed(notifications):
                on_notification(notif)
                last_id = notif["id"]

        except Exception as e:
            logger.error(f"폴링 오류: {e}")

        time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    main()
