"""마스토돈 알림 시스템

Phase 5.3 문서에 따른 알림 템플릿 및 전송 함수
"""

from .mastodon_client import get_client
from .logger import get_logger

logger = get_logger()

# 마스토돈 메시지 길이 제한
MAX_MESSAGE_LENGTH = 500
# 멘션 + 줄바꿈을 위한 여유 공간 (@username\n 최대 ~30자)
MENTION_RESERVE = 35


class NotificationTemplates:
    """알림 메시지 템플릿"""

    @staticmethod
    def item_received(sender_name: str, item_name: str, quantity: int, location: str) -> str:
        """아이템 양도 수신 알림"""
        qty_str = f" x{quantity}" if quantity > 1 else ""
        return (
            f"📦 {sender_name}님이 {item_name}{qty_str}을(를) 양도했습니다!\n"
            f"{location}에서 확인하세요."
        )

    @staticmethod
    def bag_full(item_name: str, volume: int, available: int) -> str:
        """가방 공간 부족 알림"""
        return (
            f"⚠️ 가방 공간이 부족합니다!\n"
            f"아이템: {item_name} (부피: {volume}칸)\n"
            f"남은 공간: {available}칸\n\n"
            f"주변에 임시 보관됩니다."
        )

    @staticmethod
    def cleanup_warning(items: list[dict]) -> str:
        """삭제 1시간 전 경고 알림

        Args:
            items: [{"name": str, "quantity": int}, ...]
        """
        if not items:
            return ""

        item_list = ", ".join(item["name"] for item in items[:3])
        if len(items) > 3:
            item_list += f" 외 {len(items) - 3}개"

        return (
            f"⏰ 1시간 후 주변 아이템이 삭제됩니다!\n"
            f"아이템: {item_list}\n"
            f"지금 가방에 넣으세요!"
        )

    @staticmethod
    def cleanup_done(items: list[dict]) -> str:
        """자동 삭제 완료 알림

        Args:
            items: [{"name": str, "quantity": int}, ...]
        """
        if not items:
            return ""

        item_list = "\n".join(
            f"- {item['name']} x{item['quantity']}" for item in items
        )

        return (
            f"⚠️ 주변 아이템이 자동 삭제되었습니다:\n"
            f"{item_list}\n\n"
            f"다음부터는 빨리 가방에 넣으세요!"
        )

    @staticmethod
    def item_used(item_name: str, effect: str, remaining: int) -> str:
        """아이템 사용 알림"""
        msg = f"✨ {item_name}을(를) 사용했습니다!\n{effect}"
        if remaining > 0:
            msg += f"\n남은 수량: {remaining}개"
        else:
            msg += f"\n(마지막 {item_name})"
        return msg


def send_notification(
    recipient_id: str,
    message: str,
    visibility: str = "direct",
) -> bool:
    """마스토돈 알림 전송

    Args:
        recipient_id: 수신자 마스토돈 ID (@ 없이)
        message: 메시지 내용 (@멘션 제외)
        visibility: 공개 범위 (direct, unlisted, public)

    Returns:
        성공 여부
    """
    if not recipient_id or not message:
        return False

    try:
        client = get_client()
        mention = f"@{recipient_id}\n"
        mention_len = len(mention)

        # 멘션이 잘리지 않도록 본문만 잘라냄
        max_body_len = MAX_MESSAGE_LENGTH - mention_len - 3  # "..." 여유
        if len(message) > max_body_len:
            message = message[:max_body_len] + "..."
            logger.warning("알림 메시지가 길이 제한으로 잘림 (멘션 보존)")

        full_message = mention + message

        client.status_post(full_message, visibility=visibility)
        logger.info(f"알림 전송 성공: @{recipient_id}")
        return True
    except Exception as e:
        logger.error(f"알림 전송 실패 (@{recipient_id}): {e}")
        return False


def notify_item_received(
    recipient_id: str,
    sender_name: str,
    item_name: str,
    quantity: int = 1,
    location: str = "주변",
) -> bool:
    """아이템 양도 수신 알림 전송"""
    message = NotificationTemplates.item_received(sender_name, item_name, quantity, location)
    return send_notification(recipient_id, message)


def notify_bag_full(
    recipient_id: str,
    item_name: str,
    volume: int,
    available: int,
) -> bool:
    """가방 공간 부족 알림 전송"""
    message = NotificationTemplates.bag_full(item_name, volume, available)
    return send_notification(recipient_id, message)


def notify_cleanup_warning(
    recipient_id: str,
    items: list[dict],
) -> bool:
    """삭제 경고 알림 전송"""
    message = NotificationTemplates.cleanup_warning(items)
    if not message:
        return False
    return send_notification(recipient_id, message)


def notify_cleanup_done(
    recipient_id: str,
    items: list[dict],
) -> bool:
    """삭제 완료 알림 전송"""
    message = NotificationTemplates.cleanup_done(items)
    if not message:
        return False
    return send_notification(recipient_id, message)
