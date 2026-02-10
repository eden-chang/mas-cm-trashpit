"""[상점] 명령어 핸들러 — 구매 가능한 아이템 목록 출력"""

from typing import Optional, Tuple, Type

from bot.logger import get_logger
from bot.services.item_service import list_shop_items

logger = get_logger()

MAX_SHOP_DISPLAY = 50

# list_shop_items()에서 발생 가능: ConnectionError, OSError, PostgrestAPIError
try:
    from postgrest.exceptions import APIError as PostgrestAPIError
except ImportError:
    PostgrestAPIError = None  # type: ignore[misc, assignment]

_SHOP_HANDLED_EXCEPTIONS: Tuple[Type[BaseException], ...] = (
    ConnectionError,
    OSError,
)
if PostgrestAPIError is not None:
    _SHOP_HANDLED_EXCEPTIONS = _SHOP_HANDLED_EXCEPTIONS + (PostgrestAPIError,)


def handle(status_id: str, user: str, args: list[str]) -> Optional[str]:
    """[상점] — args 없음. items 테이블에서 price가 숫자인 아이템만 멘션으로 출력.

    status_id는 다른 핸들러와 시그니처 통일을 위해 받으나 본 명령에서는 미사용.
    """
    try:
        items = list_shop_items()
    except _SHOP_HANDLED_EXCEPTIONS as e:
        logger.error(f"상점 조회 실패 (네트워크/API): {e}")
        return f"@{user} 상점 조회 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
    except Exception as e:
        logger.error(f"상점 조회 중 예상치 못한 오류: {e}")
        return f"@{user} 상점 조회 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

    if not items:
        return f"@{user} 현재 구매 가능한 아이템이 없습니다."

    lines = [f"@{user} 구매 가능한 아이템 목록", ""]
    for item in items[:MAX_SHOP_DISPLAY]:
        name = item.get("name", "알 수 없음")
        price = item.get("price", 0)
        desc = (item.get("desc") or "").strip() or "설명 없음"
        try:
            price_str = f"{int(price):,}포인트"
        except (TypeError, ValueError):
            price_str = f"{price}포인트"
        lines.append(f"- {name} ({price_str}) : {desc}")
    if len(items) > MAX_SHOP_DISPLAY:
        lines.append(f"... 외 {len(items) - MAX_SHOP_DISPLAY}개")

    return "\n".join(lines)
