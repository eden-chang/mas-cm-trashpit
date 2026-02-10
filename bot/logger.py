"""
트래시핏 봇 로깅 유틸리티

구조화되고 가독성 높은 로깅 시스템을 제공합니다.
한국 시간(KST)으로 타임스탬프를 표시합니다.
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional


class KSTFormatter(logging.Formatter):
    """한국 시간(KST) 기준으로 포맷하는 로깅 포매터"""

    def formatTime(self, record, datefmt=None):
        """타임스탬프를 KST로 변환"""
        dt = datetime.fromtimestamp(record.created, tz=ZoneInfo("Asia/Seoul"))
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S KST")


class BotLogger:
    """봇 전용 로거 래퍼 클래스"""

    def __init__(self, name: str = "TrashpitBot"):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """로거 초기 설정"""
        if self.logger.handlers:
            return

        self.logger.setLevel(logging.INFO)

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 포맷 설정
        formatter = KSTFormatter(
            fmt="%(asctime)s | %(levelname)-7s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S KST",
        )
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def command_received(self, username: str, command: str, args: list = None):
        """명령어 수신 로그"""
        args_str = f" args={args}" if args else ""
        self.logger.info(f"[명령어 수신] @{username} | [{command}]{args_str}")

    def command_response(self, username: str, command: str, response_preview: str):
        """명령어 응답 로그"""
        preview = response_preview.replace("\n", " ")[:50]
        if len(response_preview) > 50:
            preview += "..."
        self.logger.info(f"[응답 전송] @{username} | [{command}] | {preview}")

    def command_error(self, username: str, command: str, error: str, exc_info: bool = False):
        """명령어 오류 로그
        
        Args:
            username: 사용자명
            command: 명령어
            error: 에러 메시지
            exc_info: True이면 스택 트레이스 포함
        """
        self.logger.error(f"[명령어 오류] @{username} | [{command}] | {error}", exc_info=exc_info)

    def sheet_access(self, operation: str, target: str, success: bool = True):
        """시트 접근 로그"""
        status = "성공" if success else "실패"
        self.logger.info(f"[시트 {operation}] {target} | {status}")

    def api_retry(self, service: str, delay: int, attempt: int):
        """API 재시도 로그"""
        self.logger.warning(f"[재시도] {service} | 대기 {delay}초 | 시도 #{attempt}")

    def system_event(self, message: str, event_type: str = "info"):
        """시스템 이벤트 로그"""
        prefix_map = {
            "start": "[시작]",
            "stop": "[종료]",
            "success": "[성공]",
            "error": "[오류]",
            "warning": "[경고]",
            "info": "[정보]",
        }
        prefix = prefix_map.get(event_type, "[정보]")

        if event_type == "error":
            self.logger.error(f"{prefix} {message}")
        elif event_type == "warning":
            self.logger.warning(f"{prefix} {message}")
        else:
            self.logger.info(f"{prefix} {message}")

    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        self.logger.exception(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)


# 싱글톤 인스턴스
_logger_instance = None


def get_logger() -> BotLogger:
    """로거 싱글톤 인스턴스 반환"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = BotLogger()
    return _logger_instance
