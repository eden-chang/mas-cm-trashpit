"""인벤토리 관리 서비스 (Supabase 버전)"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.supabase_client import get_supabase, TABLE_CHARACTERS
from shared.constants import get_bag_capacity, STAT_KEY_TO_DB_COLUMN
from bot.services.character_service import get_character
from bot.services.item_service import get_item_info
from bot.logger import get_logger

logger = get_logger()

try:
    from postgrest.exceptions import APIError as PostgrestAPIError
except ImportError:
    PostgrestAPIError = None  # type: ignore[misc, assignment]

# 인벤토리 위치 → Supabase 컬럼 매핑
_LOC_TO_COLUMN = {
    'bag': 'bag',
    'misc': 'misc',
    'nearby': 'around',
}

# 양도 시 수집 우선순위: 주변 -> 여유공간 -> 가방
TRANSFER_PRIORITY = ("nearby", "misc", "bag")


# ============================================================
# Core Logic
# ============================================================

def get_inventory_dict(char_name: str, location: str) -> dict[str, int]:
    """특정 위치의 인벤토리를 딕셔너리로 반환"""
    char = get_character(char_name)
    if not char:
        return {}

    column = _LOC_TO_COLUMN.get(location)
    if not column:
        return {}

    inv_data = char.get(column) or {}
    if not isinstance(inv_data, dict):
        return {}

    result: dict[str, int] = {}
    for k, v in inv_data.items():
        try:
            qty = int(v)
        except (TypeError, ValueError):
            logger.warning("get_inventory_dict: 비숫자 값 무시 char=%s loc=%s key=%s val=%r", char_name, location, k, v)
            continue
        if qty > 0:
            result[str(k)] = qty
    return result


def update_inventory_location(char_name: str, location: str, items: dict[str, int]) -> bool:
    """특정 위치의 인벤토리 업데이트"""
    column = _LOC_TO_COLUMN.get(location)
    if not column:
        return False

    # 수량이 0 이하인 아이템 제거
    clean_items = {k: v for k, v in items.items() if v > 0}
    data = clean_items if clean_items else None

    try:
        supabase = get_supabase()
        response = (
            supabase.table(TABLE_CHARACTERS)
            .update({column: data})
            .eq("name", char_name)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        logger.error("Inventory Update Error: %s", e)
        return False


# ============================================================
# High Level Operations
# ============================================================

def add_item(char_name: str, item_name: str, quantity: int, location: str = 'nearby') -> bool:
    """아이템 추가"""
    if location not in _LOC_TO_COLUMN:
        return False

    items = get_inventory_dict(char_name, location)
    items[item_name] = items.get(item_name, 0) + quantity

    return update_inventory_location(char_name, location, items)


def remove_item(char_name: str, item_name: str, quantity: int, location: str) -> bool:
    """아이템 제거"""
    if location not in _LOC_TO_COLUMN:
        return False

    items = get_inventory_dict(char_name, location)

    if item_name not in items:
        return False

    items[item_name] -= quantity
    if items[item_name] <= 0:
        del items[item_name]

    return update_inventory_location(char_name, location, items)


def find_item_location(char_name: str, item_name: str) -> Optional[str]:
    """아이템 위치 찾기 (주변 -> 가방 -> 여유공간 순)"""
    if item_name in get_inventory_dict(char_name, 'nearby'):
        return 'nearby'
    if item_name in get_inventory_dict(char_name, 'bag'):
        return 'bag'
    if item_name in get_inventory_dict(char_name, 'misc'):
        return 'misc'
    return None


def get_item_count(char_name: str, item_name: str) -> int:
    """전체 소지 수량 확인"""
    total = 0
    for location in ['nearby', 'bag', 'misc']:
        items = get_inventory_dict(char_name, location)
        total += items.get(item_name, 0)
    return total


def get_item_counts_by_location(char_name: str, item_name: str) -> dict[str, int]:
    """아이템의 위치별 수량 반환 (주변, 여유공간, 가방 순)."""
    return {
        loc: get_inventory_dict(char_name, loc).get(item_name, 0)
        for loc in TRANSFER_PRIORITY
    }


def remove_item_by_priority(char_name: str, item_name: str, quantity: int) -> int:
    """우선순위(주변 -> 여유공간 -> 가방)대로 아이템을 차감하고, 실제 차감된 수량을 반환."""
    total, _ = remove_item_by_priority_detailed(char_name, item_name, quantity)
    return total


def remove_item_by_priority_detailed(
    char_name: str, item_name: str, quantity: int
) -> tuple[int, list[tuple[str, int]]]:
    """우선순위대로 아이템을 차감하고, (총 차감 수량, [(위치, 수량), ...])를 반환.

    실패 시 이미 제거된 아이템을 add_item으로 롤백한다.
    """
    if quantity <= 0:
        return 0, []
    by_loc = get_item_counts_by_location(char_name, item_name)
    remaining = quantity
    removed: list[tuple[str, int]] = []

    for loc in TRANSFER_PRIORITY:
        if remaining <= 0:
            break
        take = min(remaining, by_loc[loc])
        if take <= 0:
            continue
        if remove_item(char_name, item_name, take, loc):
            removed.append((loc, take))
            remaining -= take
        else:
            # 실패 → 이전에 제거된 아이템을 원래 위치로 복원
            logger.warning(
                "remove_item_by_priority: %s에서 제거 실패, 롤백 시작 char=%s item=%s",
                loc, char_name, item_name,
            )
            for rb_loc, rb_qty in removed:
                if not add_item(char_name, item_name, rb_qty, rb_loc):
                    logger.error(
                        "remove_item_by_priority: 롤백 실패 char=%s item=%s loc=%s qty=%d",
                        char_name, item_name, rb_loc, rb_qty,
                    )
            return 0, []

    removed_total = sum(q for _, q in removed)
    return removed_total, removed


def add_to_nearby(char_name: str, item_name: str, quantity: int) -> bool:
    """주변에 아이템 추가 (add_item wrapper)."""
    return add_item(char_name, item_name, quantity, "nearby")


def add_to_misc(char_name: str, item_name: str, quantity: int) -> bool:
    """여유공간에 아이템 추가 (add_item wrapper)."""
    return add_item(char_name, item_name, quantity, "misc")


def remove_from_location(
    char_name: str, item_name: str, quantity: int, location: str
) -> bool:
    """지정 위치에서 아이템 제거 (remove_item wrapper)."""
    return remove_item(char_name, item_name, quantity, location)


def get_available_space(char_name: str) -> int:
    """가방 남은 공간 (용량 - 사용량). 문서 1.3 근력별 용량 기준."""
    char = get_character(char_name)
    if not char:
        return 0

    strength = char.get("strength", 1) or 1
    capacity = get_bag_capacity(strength)

    bag_items = get_inventory_dict(char_name, 'bag')
    used = 0
    for item_name, qty in bag_items.items():
        info = get_item_info(item_name)
        if info:
            used += info.get("volume", 0) * qty

    return max(0, capacity - used)


def update_stat(char_name: str, stat_name: str, delta: int) -> bool:
    """캐릭터 스탯 업데이트 (hp, luck 등).

    stat_name은 character dict 키(health, strength, luck, hp, points)와 동일해야 하며,
    stat_change 명령과 inventory_service 간 계약이다.
    HP 업데이트 시 최대 HP(체력 * 10) 이상으로 올라가지 않도록 클램프한다.
    """
    char = get_character(char_name)
    if not char:
        return False

    column = STAT_KEY_TO_DB_COLUMN.get(stat_name.lower())
    if not column:
        logger.error(f"Unknown stat: {stat_name}")
        return False

    raw_current = char.get(stat_name, 0) or 0
    try:
        current = int(raw_current)
    except (TypeError, ValueError):
        current = 0
    new_value = current + delta
    if stat_name.lower() == "points":
        new_value = max(0, new_value)

    # HP 상한 클램프: 최대 HP = 체력(health/con) * 10
    if stat_name.lower() == "hp" and delta > 0:
        health_raw = char.get("health", 0) or 0
        try:
            max_hp = max(0, int(health_raw) * 10)
        except (TypeError, ValueError):
            max_hp = 0
        if max_hp > 0 and new_value > max_hp:
            new_value = max_hp

    try:
        supabase = get_supabase()
        response = (
            supabase.table(TABLE_CHARACTERS)
            .update({column: new_value})
            .eq("name", char_name)
            .execute()
        )
        return bool(response.data)
    except (OSError, ConnectionError) as e:
        logger.error(
            "update_stat failed (network) char_name=%s stat_name=%s delta=%s: %s: %s",
            char_name, stat_name, delta, type(e).__name__, e,
        )
        return False
    except Exception as e:
        if PostgrestAPIError is not None and isinstance(e, PostgrestAPIError):
            logger.error(
                "update_stat failed (API) char_name=%s stat_name=%s delta=%s: %s: %s",
                char_name, stat_name, delta, type(e).__name__, e,
            )
            return False
        logger.exception(
            "update_stat unexpected error char_name=%s stat_name=%s delta=%s",
            char_name, stat_name, delta,
        )
        raise
