"""[포인트 추가/금액/대상], [포인트 차감/금액/대상] 명령어 핸들러 — 운영진 전용"""

import re
from typing import Any

from bot.config import SYSTEM_ADMIN_IDS
from bot.logger import get_logger
from bot.services.character_service import get_character, CharacterServiceError
from bot.services.inventory_service import update_stat

logger = get_logger()

# 운영진 포인트 추가/차감 시 허용 금액 상한 (실수·오타 방지)
POINTS_ADMIN_AMOUNT_CAP = 1_000_000


def _parse_amount(amount_str: str | None) -> int | None:
    """금액 문자열에서 숫자만 추출 (10, 10포인트, 100,000 -> 10 / 10 / 100000). 음수는 None."""
    if amount_str is None or not amount_str.strip():
        return None
    s = amount_str.strip()
    if s.startswith("-"):
        return None
    s = s.replace(",", "")
    if s.isdigit():
        return int(s)
    match = re.search(r"\d+", s)
    if not match:
        return None
    try:
        return int(match.group())
    except ValueError:
        return None


def _resolve_targets(targets_str: str) -> list[str]:
    """대상 문자열을 캐릭터 이름 목록으로 변환 (쉼표 구분)."""
    if not targets_str or not targets_str.strip():
        return []
    return [p.strip() for p in targets_str.split(",") if p.strip()]


def _run_operation(user: str, args: list[str], operation: str) -> str:
    """포인트 추가 또는 차감 실행. operation은 '추가' 또는 '차감'.

    표시되는 변경 전/후 수치는 참고용이며, 동시 수정 시 실제 DB와 다를 수 있습니다.
    """
    if user not in SYSTEM_ADMIN_IDS:
        logger.warning(
            f"points_admin unauthorized attempt: user={user} operation={operation} args_count={len(args)}"
        )
        return f"@{user} 이 명령은 운영진만 사용할 수 있습니다."

    if len(args) < 2:
        return f"@{user} 사용법: [포인트 추가/금액/대상] 또는 [포인트 차감/금액/대상]"

    amount = _parse_amount(args[0])
    if amount is None or amount <= 0:
        return f"@{user} 금액은 양의 정수로 입력해 주세요."
    if amount > POINTS_ADMIN_AMOUNT_CAP:
        return f"@{user} 금액이 허용 상한({POINTS_ADMIN_AMOUNT_CAP:,} 포인트)을 초과합니다."

    raw_targets = _resolve_targets(args[1])
    if not raw_targets:
        return f"@{user} 대상 캐릭터를 입력해 주세요."

    targets = list(dict.fromkeys(raw_targets))
    had_duplicates = len(targets) < len(raw_targets)

    results: list[dict[str, Any]] = []

    for char_name in targets:
        try:
            character = get_character(char_name)
        except CharacterServiceError:
            results.append({"character": char_name, "success": False, "error": "시스템 오류"})
            continue
        if not character:
            results.append({"character": char_name, "success": False, "error": "캐릭터를 찾을 수 없습니다"})
            continue

        current_points = character.get("points") or 0
        try:
            current_points = int(current_points)
        except (TypeError, ValueError):
            current_points = 0

        if operation == "추가":
            delta = amount
            new_points = current_points + delta
        else:
            delta = -min(amount, current_points)
            new_points = max(0, current_points - amount)

        if not update_stat(char_name, "points", delta):
            results.append({"character": char_name, "success": False, "error": "업데이트 실패"})
            continue
        results.append({
            "character": char_name,
            "success": True,
            "old_points": current_points,
            "new_points": new_points,
            "change": new_points - current_points,
        })

    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    logger.info(
        f"points_admin {operation}: amount={amount} targets={len(targets)} success={len(successful)} failed={len(failed)}"
    )

    lines = [
        f"포인트 {operation} 완료",
        f"변경 금액: {amount:,} 포인트",
        "",
    ]
    if had_duplicates:
        lines.append("동일 대상 중복은 한 번만 적용했습니다.")
        lines.append("")
    if successful:
        lines.append(f"성공: {len(successful)}명")
        for r in successful[:30]:
            lines.append(f"• {r['character']}: {r['old_points']:,} → {r['new_points']:,}")
        if len(successful) > 30:
            lines.append(f"• ... 외 {len(successful) - 30}명")
        lines.append("")
    if failed:
        lines.append(f"실패: {len(failed)}명")
        for r in failed[:5]:
            lines.append(f"• {r['character']}: {r.get('error', '알 수 없는 오류')}")
        if len(failed) > 5:
            lines.append(f"• ... 외 {len(failed) - 5}명")

    return "\n".join(lines)


def handle_add(status_id: str, user: str, args: list[str]) -> str:
    """[포인트 추가/금액/대상]"""
    return _run_operation(user, args, "추가")


def handle_deduct(status_id: str, user: str, args: list[str]) -> str:
    """[포인트 차감/금액/대상]"""
    return _run_operation(user, args, "차감")
