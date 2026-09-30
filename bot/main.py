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
from mastodon import CallbackStreamListener
from bot.mastodon_client import get_notifications, reply, get_client, reinit_client
from bot.commands import (
    use,
    transfer,
    discard,
    acquire,
    grant,
    points_admin,
    stat_change,
    shop,
    item_description,
    buy,
    peek_status,
    attack,
    defense,
    shoot,
    dodge,
    bag_link,
)
from bot.scheduler import start_scheduler, stop_scheduler
from bot.logger import get_logger

logger = get_logger()

try:
    from postgrest.exceptions import APIError as PostgrestAPIError
except ImportError:
    PostgrestAPIError = None  # type: ignore[misc, assignment]

# 핸들러 실행 시 구체적으로 처리할 예외 (네트워크/DB 등)
_HANDLER_IO_EXCEPTIONS: tuple = (ConnectionError, OSError)
if PostgrestAPIError is not None:
    _HANDLER_IO_EXCEPTIONS = _HANDLER_IO_EXCEPTIONS + (PostgrestAPIError,)

# 디버그 모드 설정
if DEBUG_MODE:
    os.environ["DEBUG"] = "true"

# 허용 명령어 접두사 (화이트리스트)
ALLOWED_PREFIXES = frozenset({
    "획득", "버리기", "사용", "양도", "지급",
    "포인트 추가", "포인트추가", "포인트 차감", "포인트차감",
    "hp", "체력", "근력", "행운",
    "상점", "설명", "구매", "상태 확인", "상태확인",
    "발사", "공격", "방어", "회피",
    "가방 링크", "가방링크",
})

# 응답에 개인 자격 증명이 포함되므로 요청 공개 범위와 관계없이 DM으로만 답하는 명령어
DIRECT_REPLY_COMMANDS = frozenset({"bag_link"})

# 명령어 패턴 (give_point는 give_item보다 먼저 — 더 구체적인 패턴 우선)
PATTERNS = {
    "use": re.compile(r"\[사용/([^\]]+)\]"),
    "give_point": re.compile(r"\[양도/(\d+)포인트/([^\]]+)\]"),
    "give_item": re.compile(r"\[양도/([^\]/]+)/([^\]]+)\]"),
    "discard": re.compile(r"\[버리기/([^\]]+)\]"),
    "acquire": re.compile(r"\[획득/([^\]]+)\]"),
    "grant_item": re.compile(r"\[지급/([^\]/]+)/([^\]]+)\]"),
    "point_add": re.compile(r"\[포인트 추가/([^/]+)/([^\]]+)\]"),
    "point_add_nospace": re.compile(r"\[포인트추가/([^/]+)/([^\]]+)\]"),
    "point_deduct": re.compile(r"\[포인트 차감/([^/]+)/([^\]]+)\]"),
    "point_deduct_nospace": re.compile(r"\[포인트차감/([^/]+)/([^\]]+)\]"),
    "stat_change": re.compile(r"\[(hp|체력|근력|행운)/([+-]?\d+)\]"),
    "shop": re.compile(r"\[상점\]"),
    "item_description": re.compile(r"\[설명/([^\]]+)\]"),
    # [구매/아이템명] 또는 [구매/아이템명/개수]. 아이템명에 슬래시(/) 미지원.
    "buy": re.compile(r"\[구매/([^/]+)(?:/(\d+))?\]"),
    "peek_status": re.compile(r"\[상태 확인\]"),
    "peek_status_nospace": re.compile(r"\[상태확인\]"),
    "attack": re.compile(r"\[공격\]"),
    "defense": re.compile(r"\[방어\]"),
    "shoot": re.compile(r"\[발사\]"),
    "dodge": re.compile(r"\[회피\]"),
    "bag_link": re.compile(r"\[가방 ?링크\]"),
}

# 명령어 핸들러 매핑
HANDLERS = {
    "use": use.handle,
    "give_item": transfer.handle_item,
    "give_point": transfer.handle_point,
    "discard": discard.handle,
    "acquire": acquire.handle,
    "grant_item": grant.handle,
    "point_add": points_admin.handle_add,
    "point_add_nospace": points_admin.handle_add,
    "point_deduct": points_admin.handle_deduct,
    "point_deduct_nospace": points_admin.handle_deduct,
    "stat_change": stat_change.handle,
    "shop": shop.handle,
    "item_description": item_description.handle,
    "buy": buy.handle,
    "peek_status": peek_status.handle,
    "peek_status_nospace": peek_status.handle,
    "attack": attack.handle,
    "defense": defense.handle,
    "shoot": shoot.handle,
    "dodge": dodge.handle,
    "bag_link": bag_link.handle,
}


def _extract_prefix(matched_text: str) -> str:
    """매칭된 [명령어/인자] 또는 [명령어]에서 접두사 추출."""
    inner = matched_text[1:-1]
    return inner.split("/")[0].strip()


def _resolve_reply_visibility(user_visibility: str) -> str:
    """봇 답변은 unlisted/private/direct만 허용. public은 unlisted로 다운그레이드."""
    if user_visibility in ("unlisted", "private", "direct"):
        return user_visibility
    return "unlisted"


def parse_command(content: str) -> tuple[str, list] | None:
    """명령어 파싱 (허용 접두사 화이트리스트 검증 포함)"""
    content = re.sub(r"<[^>]+>", "", content)

    for cmd_type, pattern in PATTERNS.items():
        match = pattern.search(content)
        if match:
            prefix = _extract_prefix(match.group(0))
            if prefix in ALLOWED_PREFIXES:
                return (cmd_type, list(match.groups()))
            return None

    return None


def on_notification(notification: dict):
    """멘션 알림 처리"""
    if notification["type"] != "mention":
        return

    status = notification["status"]
    content = status["content"]
    user = notification["account"]["acct"]
    status_id = status["id"]
    visibility = _resolve_reply_visibility(status.get("visibility", "unlisted"))

    # 명령어 파싱
    result = parse_command(content)
    if not result:
        return

    cmd_type, args = result
    logger.command_received(user, cmd_type, args)
    if cmd_type in DIRECT_REPLY_COMMANDS:
        visibility = "direct"

    # 핸들러 실행 (반환값이 있으면 reply로 전송)
    handler = HANDLERS.get(cmd_type)
    if handler:
        try:
            result = handler(status_id, user, args)
            if result is not None:
                # 핸들러가 붙인 @user 접두사 제거 (status_reply가 자동 추가)
                if result.startswith(f"@{user}"):
                    result = result[len(f"@{user}"):].lstrip()
                reply(status_id, result, visibility=visibility)
        except _HANDLER_IO_EXCEPTIONS as e:
            logger.command_error(user, cmd_type, str(e), exc_info=False)
            reply(status_id, "시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요.", visibility=visibility)
        except Exception as e:
            logger.command_error(user, cmd_type, str(e), exc_info=True)
            reply(status_id, "시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요.", visibility=visibility)


def signal_handler(signum, frame):
    """시그널 핸들러 - Ctrl+C 등으로 봇을 안전하게 종료"""
    logger.system_event(f"봇 종료 신호를 받았습니다 (시그널: {signum})", "stop")
    stop_scheduler()
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


def _skip_existing_notifications() -> None:
    """시작 시 기존 알림을 조회만 하여 건너뛴다."""
    try:
        existing = get_notifications(since_id=None)
        if existing:
            logger.info(f"기존 알림 {len(existing)}개 건너뜀")
        else:
            logger.info("기존 알림 없음")
    except Exception as e:
        logger.warning(f"초기 알림 조회 실패: {e}")


def run_streaming_loop():
    """스트리밍으로 실시간 알림 처리 (연결 끊김 시 자동 재연결)"""
    _skip_existing_notifications()

    listener = CallbackStreamListener(notification_handler=on_notification)
    consecutive_failures = 0
    max_consecutive_failures = 5

    while True:
        try:
            client = get_client()
            logger.system_event("스트리밍 연결 시작", "info")
            client.stream_user(listener)
            # stream_user가 정상 종료되면 재연결
            consecutive_failures = 0
        except KeyboardInterrupt:
            logger.system_event("사용자가 봇을 종료했습니다", "stop")
            break
        except Exception as e:
            consecutive_failures += 1
            logger.warning(
                f"스트리밍 연결 끊김 (연속 실패 {consecutive_failures}회): {e}"
            )

            if consecutive_failures >= max_consecutive_failures:
                logger.error(
                    f"스트리밍 연속 {max_consecutive_failures}회 실패, 폴링으로 전환합니다."
                )
                raise

            delay = min(5 * consecutive_failures, 30)
            logger.info(f"스트리밍 재연결 대기 중... ({delay}초)")
            time.sleep(delay)
            reinit_client()


def run_polling_loop():
    """폴링 루프 실행 (스트리밍 실패 시 fallback)"""
    consecutive_failures = 0
    max_consecutive_failures = 5

    # 시작 시 기존 알림을 모두 건너뛰고, 이후 새 알림만 처리
    try:
        existing = get_notifications(since_id=None)
        if existing:
            last_id = existing[0]["id"]  # 가장 최신 알림 ID
            logger.info(f"기존 알림 {len(existing)}개 건너뜀 (last_id={last_id})")
        else:
            last_id = None
            logger.info("기존 알림 없음, 처음부터 폴링 시작")
    except Exception as e:
        logger.warning(f"초기 알림 조회 실패, last_id=None으로 시작: {e}")
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

            logger.system_event("봇을 시작합니다 (스트리밍 모드)", "start")
            logger.info("Ctrl+C를 눌러 종료할 수 있습니다.")

            # 스케줄러 시작 (주변 아이템 자동 삭제)
            start_scheduler()

            try:
                run_streaming_loop()
            except Exception:
                logger.warning("스트리밍 실패, 폴링 모드로 전환합니다.")
                logger.info(f"폴링 간격: {POLLING_INTERVAL}초")
                run_polling_loop()

    except Exception as e:
        logger.error(f"예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)

    logger.system_event("봇이 종료되었습니다", "stop")


if __name__ == "__main__":
    main()
