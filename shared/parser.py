"""인벤토리 텍스트 파싱/직렬화 (문서 1.1 - Phase 1.1 통합)

단일 소스: api, bot, shared 모듈 모두 이 모듈 사용.
형식: "아이템명: 수량, 아이템명: 수량, ..." (콜론 뒤 공백, 콤마+공백 구분)
"""

import re
from typing import Union

from .models import Item


def parse_inventory(text: str) -> list[Item]:
    """인벤토리 텍스트를 Item 리스트로 파싱

    지원 형식:
    - "아이템명: 수량" (Phase 1.1 표준)
    - "아이템명 수량개", "아이템명x3"
    - 수량 없이 아이템명만 (수량 1)
    """
    if not text or not text.strip():
        return []

    items: list[Item] = []
    parts = re.split(r"[,\n]", text.strip())

    for part in parts:
        part = part.strip()
        if not part:
            continue

        match = re.match(r"(.+?):\s*(\d+)$", part)
        if match:
            items.append(Item(name=match.group(1).strip(), quantity=int(match.group(2))))
            continue

        if ":" in part:
            name, _ = part.split(":", 1)
            if name.strip():
                items.append(Item(name=name.strip(), quantity=1))
                continue

        match = re.match(r"(.+?)\s*(\d+)개", part)
        if match:
            items.append(Item(name=match.group(1).strip(), quantity=int(match.group(2))))
            continue

        match = re.match(r"(.+?)\s*[xX×]\s*(\d+)", part)
        if match:
            items.append(Item(name=match.group(1).strip(), quantity=int(match.group(2))))
            continue

        if part:
            items.append(Item(name=part, quantity=1))

    return items


def serialize_inventory(items: Union[list[dict], list[Item]]) -> str:
    """아이템 리스트를 시트 저장용 텍스트로 직렬화

    dict 또는 Item 객체 모두 지원 (duck typing).
    Phase 1.1 형식: "아이템명: 수량, 아이템명: 수량, ..."
    """
    if not items:
        return ""

    parts = []
    for item in items:
        name = (item.get("name", "") or "") if isinstance(item, dict) else (item.name or "")
        qty = item.get("quantity", 1) if isinstance(item, dict) else item.quantity
        if name:
            parts.append(f"{name}: {qty}")

    return ", ".join(parts)
