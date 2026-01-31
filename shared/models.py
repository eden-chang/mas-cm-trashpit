"""데이터 모델 정의"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Item:
    """아이템 정보"""
    name: str
    quantity: int = 1
    volume: int = 0

    @property
    def total_volume(self) -> int:
        return self.volume * self.quantity


@dataclass
class ItemInfo:
    """아이템 마스터 정보 (상점 시트)"""
    name: str
    price: int = 0
    description: str = ""
    use_message: str = ""
    stat: str = ""
    value: int = 0
    volume: int = 0


@dataclass
class Character:
    """캐릭터 정보"""
    name: str
    mastodon_id: str
    health: int = 0
    strength: int = 1
    luck: int = 0
    bag_items: list[Item] = field(default_factory=list)
    misc_items: list[Item] = field(default_factory=list)
    nearby_items: list[Item] = field(default_factory=list)
    row_index: int = 0  # 시트에서의 행 번호

    @property
    def bag_capacity(self) -> int:
        from .constants import get_bag_capacity
        return get_bag_capacity(self.strength)

    @property
    def bag_used(self) -> int:
        return sum(item.total_volume for item in self.bag_items)

    @property
    def bag_available(self) -> int:
        return self.bag_capacity - self.bag_used
