"""용량 계산 규칙 (문서 1.3 - 용량 계산 규칙)

근력 스탯에 따른 가방 용량 계산 및 가방 사용량 계산.
"""

from .constants import get_bag_capacity
from .parser import parse_inventory


def calculate_capacity(strength: int) -> int:
    """근력 기반 가방 용량 계산

    근력 1~5: 20, 6~10: 40, 11~49: 60, 50 이상: 200, 그 외: 20(기본값)
    """
    return get_bag_capacity(strength)


def calculate_used_volume(inventory_str: str) -> int:
    """가방 사용량 계산 (아이템 마스터 부피 기준)"""
    from .item_master import get_item_info

    items = parse_inventory(inventory_str)
    total = 0

    for item in items:
        item_info = get_item_info(item.name)
        volume = item_info.volume if item_info else 0
        total += volume * item.quantity

    return total
