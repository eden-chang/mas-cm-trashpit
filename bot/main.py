#!/usr/bin/env python3
"""
트래시핏 마스토돈 봇 메인 실행 파일

사용법:
    python main.py                # 일반 실행
    python main.py --debug        # 디버그 모드
    python main.py --test         # 테스트 모드
"""

import os
import re
import sys
import argparse
import signal
import time
from pathlib import Path

# 상위 디렉토리 import를 위한 경로 추가 (프로젝트 루트)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from shared.config import POLLING_INTERVAL, DEBUG_MODE
from bot.mastodon_client import get_notifications, reply
from bot.commands import use, transfer, discard, acquire, grant
from bot.logger import get_logger

logger = get_logger()

# 디버그 모드 설정
if DEBUG_MODE:
    os.environ["DEBUG"] = "true"

# 명령어 패턴
PATTERNS = {
    "use": re.compile(r"\[사용/([^\]]+)\]"),
    "give_item": re.compile(r"\[양도/([^\]/]+)/([^\]]+)\]"),
    "give_point": re.compile(r"\[양도/(\d+)포인트/([^\]]+)\]"),
    "discard": re.compile(r"\[버리기/([^\]]+)\]"),
    "acquire": re.compile(r"\[획득/([^\]]+)\]"),
    "grant_item": re.compile(r"\[지급/([^\]/]+)/([^\]]+)\]"),
}

# 명령어 핸들러 매핑
HANDLERS = {
    "use": use.handle,
    "give_item": transfer.handle_item,
    "give_point": transfer.handle_point,
    "discard": discard.handle,
    "acquire": acquire.handle,
    "grant_item": grant.handle,
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
    logger.command_received(user, cmd_type, args)

    # 핸들러 실행 (반환값이 있으면 reply로 전송)
    handler = HANDLERS.get(cmd_type)
    if handler:
        try:
            result = handler(status_id, user, args)
            if result is not None:
                reply(status_id, result)
        except Exception as e:
            logger.command_error(user, cmd_type, str(e))
            reply(status_id, f"@{user} 오류가 발생했습니다: {e}")


def signal_handler(signum, frame):
    """시그널 핸들러 - Ctrl+C 등으로 봇을 안전하게 종료"""
    logger.system_event(f"봇 종료 신호를 받았습니다 (시그널: {signum})", "stop")
    sys.exit(0)


def run_test_mode():
    """테스트 모드 실행"""
    logger.system_event("테스트 모드로 실행합니다", "info")

    test_cases = [
        ("testuser", "[획득/사과]"),
        ("testuser", "[사용/사과]"),
        ("testuser", "[버리기/사과]"),
    ]

    for username, command in test_cases:
        logger.info(f"테스트: {username} -> {command}")
        result = parse_command(command)
        if result:
            cmd_type, args = result
            logger.info(f"파싱 결과: cmd_type={cmd_type}, args={args}")
        else:
            logger.info("파싱 실패: 명령어를 찾을 수 없음")
        logger.info("-" * 50)


def run_polling_loop():
    """폴링 루프 실행"""
    consecutive_failures = 0
    max_consecutive_failures = 5
    last_id = None

    while True:
        try:
            notifications = get_notifications(since_id=last_id)

            for notif in reversed(notifications):
                on_notification(notif)
                last_id = notif["id"]

            consecutive_failures = 0

        except KeyboardInterrupt:
            logger.system_event("사용자가 봇을 종료했습니다", "stop")
            break

        except Exception as e:
            consecutive_failures += 1
            logger.error(f"폴링 오류 (연속 실패 {consecutive_failures}회): {e}")

            if consecutive_failures >= max_consecutive_failures:
                logger.error(
                    f"연속 {max_consecutive_failures}회 실패. 프로그램을 종료합니다."
                )
                raise

            # 지수 백오프 대기
            delay = min(60 * consecutive_failures, 300)
            logger.warning(f"재시도 대기 중... ({delay}초)")
            time.sleep(delay)

        time.sleep(POLLING_INTERVAL)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="트래시핏 마스토돈 봇")
    parser.add_argument("--debug", action="store_true", help="디버그 모드로 실행")
    parser.add_argument("--test", action="store_true", help="테스트 모드로 실행")

    args = parser.parse_args()

    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("=" * 60)
    logger.info("트래시핏 마스토돈 봇")
    logger.info("=" * 60)

    try:
        if args.test:
            run_test_mode()
        else:
            if args.debug:
                os.environ["DEBUG"] = "true"
                logger.system_event("디버그 모드로 실행합니다", "info")

            logger.system_event("봇을 시작합니다", "start")
            logger.info(f"폴링 간격: {POLLING_INTERVAL}초")
            logger.info("Ctrl+C를 눌러 종료할 수 있습니다.")

            run_polling_loop()

    except Exception as e:
        logger.error(f"예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)

    logger.system_event("봇이 종료되었습니다", "stop")


if __name__ == "__main__":
    main()
