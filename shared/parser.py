"""인벤토리 파싱/직렬화 모듈

지원 형식:
1. 텍스트 (레거시): "아이템명: 수량, 아이템명: 수량, ..."
2. JSON 객체 (Supabase): {"아이템명": 수량, "아이템명": 수량}
"""

import json
import logging
import re
from typing import Optional, Union

from .models import Item, LayoutItem

logger = logging.getLogger(__name__)


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
    """아이템 리스트를 시트 저장용 텍스트로 직렬화 (레거시)

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


# ============================================================
# Supabase JSON 형식 파싱/직렬화
# ============================================================

def parse_json_inventory(data: Optional[dict]) -> list[Item]:
    """Supabase JSON 객체를 Item 리스트로 변환

    Supabase 형식: {"콜라": 1, "사이다": 3}
    반환: [Item(name="콜라", quantity=1), Item(name="사이다", quantity=3)]
    """
    if not data or not isinstance(data, dict):
        return []

    items: list[Item] = []
    for name, quantity in data.items():
        if not name:
            continue
        try:
            qty = int(quantity) if quantity else 0
            if qty > 0:
                items.append(Item(name=str(name), quantity=qty))
        except (ValueError, TypeError):
            logger.warning("인벤토리 수량 파싱 실패: %s=%s", name, quantity)
            continue

    return items


def serialize_json_inventory(items: Union[list[dict], list[Item]]) -> Optional[dict]:
    """Item 리스트를 Supabase JSON 객체로 직렬화

    반환: {"콜라": 1, "사이다": 3} 또는 None (빈 경우)
    """
    if not items:
        return None

    result: dict[str, int] = {}
    for item in items:
        if isinstance(item, dict):
            name = item.get("name", "")
            qty = item.get("quantity", 1)
        else:
            name = item.name
            qty = item.quantity

        if name and qty > 0:
            result[name] = qty

    return result if result else None


def parse_layout(json_str: str) -> list[LayoutItem]:
    """배치 JSON 문자열을 LayoutItem 리스트로 파싱

    JSON 형식:
    [
      {"id": "i-123-0", "name": "생수", "row": 0, "col": 0, "shapeIndex": 0},
      {"id": "i-123-1", "name": "붕대", "row": 1, "col": 0, "shapeIndex": 1}
    ]
    
    id 필드는 선택적이며, 같은 이름의 아이템이 여러 위치에 있을 때 구분용.
    """
    if not json_str or not json_str.strip():
        return []

    try:
        data = json.loads(json_str)
        if not isinstance(data, list):
            return []

        result: list[LayoutItem] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name", "")
            if not name:
                continue
            result.append(LayoutItem(
                name=str(name),
                row=int(item.get("row", 0)),
                col=int(item.get("col", 0)),
                shapeIndex=int(item.get("shapeIndex", 0)),
                id=item.get("id"),  # 인스턴스 ID (선택적)
            ))
        return result
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.warning("배치 JSON 파싱 실패: %s", e)
        return []


def serialize_layout(layout: Union[list[dict], list[LayoutItem]]) -> str:
    """배치 리스트를 JSON 문자열로 직렬화

    dict 또는 LayoutItem 객체 모두 지원.
    id 필드가 있으면 포함됨.
    """
    if not layout:
        return ""

    result = []
    for item in layout:
        if isinstance(item, dict):
            entry = {
                "name": item.get("name", ""),
                "row": item.get("row", 0),
                "col": item.get("col", 0),
                "shapeIndex": item.get("shapeIndex", 0),
            }
            if item.get("id"):
                entry["id"] = item["id"]
            result.append(entry)
        else:
            entry = {
                "name": item.name,
                "row": item.row,
                "col": item.col,
                "shapeIndex": item.shapeIndex,
            }
            if item.id:
                entry["id"] = item.id
            result.append(entry)

    return json.dumps(result, ensure_ascii=False)


# ============================================================
# Supabase JSON 형식 배치 파싱/직렬화
# ============================================================

def parse_json_layout(data: Optional[list]) -> list[LayoutItem]:
    """Supabase JSON 배열을 LayoutItem 리스트로 변환

    Supabase 형식 (arrange 컬럼):
    [
      {"id": "i-123-0", "name": "생수", "row": 0, "col": 0, "shapeIndex": 0},
      {"id": "i-123-1", "name": "붕대", "row": 1, "col": 0, "shapeIndex": 1}
    ]
    
    id 필드는 선택적이며, 같은 이름의 아이템이 여러 위치에 있을 때 구분용.
    """
    if not data or not isinstance(data, list):
        return []

    result: list[LayoutItem] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name", "")
        if not name:
            continue
        try:
            result.append(LayoutItem(
                name=str(name),
                row=int(item.get("row", 0)),
                col=int(item.get("col", 0)),
                shapeIndex=int(item.get("shapeIndex", 0)),
                id=item.get("id"),  # 인스턴스 ID (선택적)
            ))
        except (ValueError, TypeError) as e:
            logger.warning("배치 항목 파싱 실패: %s, %s", item, e)
            continue

    return result


def serialize_json_layout(layout: Optional[Union[list[dict], list[LayoutItem]]]) -> Optional[list]:
    """배치 리스트를 Supabase JSON 배열로 직렬화

    반환: [{"id": "i-123-0", "name": "생수", "row": 0, "col": 0, "shapeIndex": 0}, ...] 또는 None
    id 필드는 존재할 경우에만 포함됨.
    """
    if not layout:
        return None

    result = []
    for item in layout:
        if isinstance(item, dict):
            entry = {
                "name": item.get("name", ""),
                "row": item.get("row", 0),
                "col": item.get("col", 0),
                "shapeIndex": item.get("shapeIndex", 0),
            }
            # id 필드가 있으면 포함
            if item.get("id"):
                entry["id"] = item["id"]
            result.append(entry)
        else:
            entry = {
                "name": item.name,
                "row": item.row,
                "col": item.col,
                "shapeIndex": item.shapeIndex,
            }
            # id 필드가 있으면 포함
            if item.id:
                entry["id"] = item.id
            result.append(entry)

    return result if result else None
