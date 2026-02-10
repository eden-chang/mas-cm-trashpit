"""[구매/아이템명/n] 명령어 핸들러 — 상점에서 아이템 구매"""

import threading
from typing import Optional

from bot.logger import get_logger
from bot.services.character_service import get_character_by_mastodon_id
from bot.services.item_service import get_item_info, parse_sellable_price
from bot.services.inventory_service import update_stat, add_item
from bot.utils.korean import josa

logger = get_logger()

# 동일 캐릭터에 대한 동시 구매 시 포인트/인벤토리 일관성을 위해 캐릭터별 락 사용
_buy_locks: dict[str, threading.Lock] = {}
_buy_locks_guard = threading.Lock()


def _lock_for_character(char_name: str) -> threading.Lock:
    """캐릭터별 락 반환 (동시 구매 시 경쟁 조건 방지)."""
    with _buy_locks_guard:
        if char_name not in _buy_locks:
            _buy_locks[char_name] = threading.Lock()
        return _buy_locks[char_name]


def handle(status_id: str, user: str, args: list[str]) -> Optional[str]:
    """[구매/아이템명] 또는 [구매/아이템명/n]. args: [item_name] 또는 [item_name, quantity_str].

    처리 순서: 포인트 차감(update_stat) 후 인벤토리 추가(add_item). add_item 실패 시 포인트 환불.
    아이템명에 슬래시(/)는 사용할 수 없으며, 개수는 생략 시 1개.
    """
    if not args or not args[0].strip():
        return f"@{user} 사용법: [구매/아이템명] 또는 [구매/아이템명/개수]"

    item_name = args[0].strip()
    quantity = 1
    if len(args) >= 2 and args[1] is not None and str(args[1]).strip():
        try:
            quantity = int(args[1].strip())
            if quantity <= 0:
                return f"@{user} 구매 개수는 1 이상이어야 합니다."
            if quantity > 999:
                return f"@{user} 한 번에 최대 999개까지만 구매할 수 있습니다."
        except ValueError:
            return f"@{user} 개수는 숫자로 입력해 주세요."

    info = get_item_info(item_name)
    if not info:
        logger.debug(f"구매 조회 실패: 아이템 없음 user={user} item_name={item_name!r}")
        return f"@{user} '{item_name}' 아이템을 찾을 수 없습니다. 상점 목록을 확인해 주세요."

    unit_price = parse_sellable_price(info.get("price"))
    if unit_price is None:
        return f"@{user} {josa(item_name, '은/는')} 비매품으로 구매할 수 없습니다."

    total_cost = unit_price * quantity

    character = get_character_by_mastodon_id(user)
    if not character:
        logger.debug(f"구매 실패: 캐릭터 없음 user={user}")
        return f"@{user} 등록된 캐릭터를 찾을 수 없습니다."

    char_name = character["name"]
    current_points = character.get("points") or 0
    try:
        current_points = int(current_points)
    except (TypeError, ValueError):
        current_points = 0

    if current_points < total_cost:
        return f"@{user} 포인트가 부족합니다. 현재 소지 포인트는 {current_points}입니다."

    lock = _lock_for_character(char_name)
    lock.acquire()
    try:
        if not update_stat(char_name, "points", -total_cost):
            logger.error(
                f"구매 포인트 차감 실패 char_name={char_name!r} item_name={item_name!r} quantity={quantity} total_cost={total_cost}"
            )
            return f"@{user} 포인트 차감 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

        canonical_name = info.get("name", item_name)
        volume = info.get("volume", 0) or 0
        location = "misc" if volume == 0 else "nearby"
        if not add_item(char_name, canonical_name, quantity, location):
            logger.warning(
                f"구매 아이템 추가 실패, 환불 시도 char_name={char_name!r} item_name={item_name!r} quantity={quantity} total_cost={total_cost}"
            )
            if not update_stat(char_name, "points", total_cost):
                logger.error(
                    f"구매 환불 실패 char_name={char_name!r} item_name={item_name!r} total_cost={total_cost}"
                )
                return (
                    f"@{user} 아이템 추가에 실패했으며, 포인트 환불 시도 중 오류가 발생했습니다. "
                    "관리자에게 문의해 주세요."
                )
            return f"@{user} 아이템 추가에 실패했습니다. 포인트는 차감되지 않았습니다."

        remaining = current_points - total_cost
        location_label = "여유공간" if location == "misc" else "주변 공간"
        lines = [
            f"@{user} {josa(canonical_name, '을/를')} 구매했습니다.",
            f"➭ -{total_cost}포인트",
            f"➭ {canonical_name} {quantity}개 획득",
            f"➭ 잔액 {remaining}포인트",
            "",
            "설명을 확인하시려면 [설명/아이템명]을 사용하세요.",
            f"구매한 아이템은 {location_label}에 들어갔으므로, 아이템을 가방에 넣기 위해서는 인벤토리를 편집하시기 바랍니다.",
        ]
        return "\n".join(lines)
    finally:
        lock.release()
