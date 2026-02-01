"""인벤토리 문자열 파서

형식: "아이템: 수량, 아이템2: 수량" (공백/콤마 허용)
예: "사과: 1, 바나나: 3"
"""

import re

def parse_inventory_str(inv_str: str) -> dict[str, int]:
    """
    인벤토리 문자열을 딕셔너리로 파싱
    "사과: 1, 바나나: 3" -> {'사과': 1, '바나나': 3}
    """
    if not inv_str or inv_str.strip() == "":
        return {}

    items = {}
    # 콤마 또는 줄바꿈으로 분리
    parts = re.split(r'[,|\n]', inv_str)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # "아이템: 수량" 형식
        if ':' in part:
            name, qty_str = part.rsplit(':', 1)
            name = name.strip()
            try:
                qty = int(qty_str.strip())
                # 중복 아이템이 있다면 합산
                items[name] = items.get(name, 0) + qty
            except ValueError:
                continue # 수량이 숫자가 아니면 무시
        else:
            # 수량 없이 아이템 이름만 있는 경우 (1개로 간주)
            name = part.strip()
            items[name] = items.get(name, 0) + 1
            
    return items

def to_inventory_str(items: dict[str, int]) -> str:
    """
    딕셔너리를 인벤토리 문자열로 변환
    {'사과': 1, '바나나': 3} -> "사과: 1, 바나나: 3"
    수량이 0 이하인 아이템은 제외
    """
    parts = []
    for name, qty in items.items():
        if qty > 0:
            parts.append(f"{name}: {qty}")
    
    return ", ".join(parts)
