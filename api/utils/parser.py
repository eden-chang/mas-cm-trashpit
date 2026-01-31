"""인벤토리 텍스트 파싱 유틸리티"""

import re
from shared.models import Item


def parse_inventory(text: str) -> list[Item]:
    """
    인벤토리 텍스트를 파싱하여 아이템 리스트로 변환

    형식 예시:
    - "사과: 3, 물병: 2"
    - "사과 3개, 물병 2개"
    - "사과x3, 물병x2"
    """
    if not text or not text.strip():
        return []

    items = []
    text = text.strip()

    # 쉼표 또는 줄바꿈으로 분리
    parts = re.split(r"[,\n]", text)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # 패턴 1: "아이템명: 수량"
        match = re.match(r"(.+?):\s*(\d+)", part)
        if match:
            items.append(Item(name=match.group(1).strip(), quantity=int(match.group(2))))
            continue

        # 패턴 2: "아이템명 수량개"
        match = re.match(r"(.+?)\s*(\d+)개", part)
        if match:
            items.append(Item(name=match.group(1).strip(), quantity=int(match.group(2))))
            continue

        # 패턴 3: "아이템명x수량" 또는 "아이템명 x 수량"
        match = re.match(r"(.+?)\s*[xX×]\s*(\d+)", part)
        if match:
            items.append(Item(name=match.group(1).strip(), quantity=int(match.group(2))))
            continue

        # 패턴 4: 수량 없이 아이템명만 (수량 1로 처리)
        if part:
            items.append(Item(name=part, quantity=1))

    return items


def serialize_inventory(items: list[dict]) -> str:
    """
    아이템 리스트를 시트 저장용 텍스트로 변환

    형식: "아이템명: 수량, 아이템명: 수량, ..."
    """
    if not items:
        return ""

    parts = []
    for item in items:
        name = item.get("name", "")
        quantity = item.get("quantity", 1)
        if name:
            parts.append(f"{name}: {quantity}")

    return ", ".join(parts)
