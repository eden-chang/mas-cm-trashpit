"""[설명/아이템명] 명령어 핸들러 — 아이템 설명 출력"""

from typing import Optional

from bot.logger import get_logger
from bot.services.item_service import get_item_info, format_price_display
from bot.utils.dice import is_dice_expression

logger = get_logger()


def handle(status_id: str, user: str, args: list[str]) -> Optional[str]:
    """[설명/아이템명] — args: [item_name]. name (price 포인트) : description, 스탯 변화 시 [사용 시 스탯 ±값]."""
    if not args or not args[0].strip():
        return f"@{user} 사용법: [설명/아이템명]"

    item_name = args[0].strip()
    info = get_item_info(item_name)
    if not info:
        logger.debug(f"설명 조회 실패: 아이템 없음 user={user} item_name={item_name!r}")
        return f"@{user} '{item_name}' 아이템을 찾을 수 없습니다."

    name = info.get("name", item_name)
    price_str = format_price_display(info.get("price"))
    desc = (info.get("desc") or "").strip() or "설명 없음"
    stat = (info.get("stat") or "").strip()
    value_raw = info.get("value")

    base = f"{name}({price_str}): {desc}" if price_str == "비매품" else f"{name} ({price_str}) : {desc}"

    # 사용 불가 아이템
    if stat == "사용 불가":
        return f"@{user} {base} [명령어 사용 불가]"

    if stat and value_raw is not None and str(value_raw).strip():
        value_str = str(value_raw).strip()
        if is_dice_expression(value_str):
            base += f" [사용 시 {stat} {value_str}]"
        else:
            try:
                v = int(float(value_str))
                base += f" [사용 시 {stat} {v:+d}]" if v != 0 else ""
            except (ValueError, TypeError):
                base += f" [사용 시 {stat} {value_str}]"

    return f"@{user} {base}"
