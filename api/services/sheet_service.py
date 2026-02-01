"""구글 시트 서비스 (Phase 3.2 + 3.3 캐싱)"""

import time
import logging
from typing import Optional

from gspread.exceptions import APIError

from shared.google_sheets import get_worksheet
from shared.constants import WORKSHEET_MANAGEMENT, ManagementColumns
from shared.models import Character
from shared.parser import parse_inventory, serialize_inventory
from shared.cache import (
    cached,
    invalidate_character_cache,
    CACHE_TTL_CHARACTERS,
)

logger = logging.getLogger(__name__)

# 재시도 설정
MAX_RETRIES = 3
RETRY_DELAY = 1  # 초


def _retry_on_rate_limit(func):
    """Rate limit 시 재시도하는 데코레이터"""
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except APIError as e:
                if e.response.status_code == 429:  # Rate limit
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    logger.warning("Rate limit 도달, %d초 후 재시도 (%d/%d)",
                                   wait_time, attempt + 1, MAX_RETRIES)
                    time.sleep(wait_time)
                else:
                    raise
        # 마지막 시도
        return func(*args, **kwargs)
    return wrapper


@cached(ttl=CACHE_TTL_CHARACTERS)
@_retry_on_rate_limit
def get_all_characters() -> list[Character]:
    """전체 캐릭터 목록 조회 (캐시됨)"""
    ws = get_worksheet(WORKSHEET_MANAGEMENT)
    records = ws.get_all_records()[1:]  # 2행(정보행) 스킵

    characters = []
    for idx, record in enumerate(records):
        char = _record_to_character(record, row_index=idx + 3)
        characters.append(char)

    return characters


@cached(ttl=CACHE_TTL_CHARACTERS)
def get_character_by_name(name: str) -> Optional[Character]:
    """이름으로 캐릭터 조회 (캐시됨). get_all_characters 캐시 활용으로 API 호출 최소화."""
    for char in get_all_characters():
        if char.name == name:
            return char
    return None


@cached(ttl=CACHE_TTL_CHARACTERS)
def get_character_by_mastodon_id(mastodon_id: str) -> Optional[Character]:
    """마스토돈 ID로 캐릭터 조회 (캐시됨). get_all_characters 캐시 활용으로 API 호출 최소화."""
    for char in get_all_characters():
        if char.mastodon_id == mastodon_id:
            return char
    return None


def find_character_row(name: str) -> Optional[int]:
    """캐릭터 이름으로 행 번호 반환 (1-indexed). None이면 미존재."""
    for char in get_all_characters():
        if char.name == name:
            return char.row_index
    return None


def get_character_with_range(name: str) -> Optional[Character]:
    """범위로 한 행만 읽어 단일 캐릭터 조회 (대형 시트용 최적화).
    캐시 미스 시 get_all_characters 대비 2회 API 호출로 단일 행만 로드."""
    ws = get_worksheet(WORKSHEET_MANAGEMENT)
    names_col = ws.col_values(ManagementColumns.NAME + 1)
    for i, n in enumerate(names_col[2:], start=3):  # 2행 스킵
        if n == name:
            row_values = list(ws.row_values(i))
            while len(row_values) < 9:
                row_values.append("")
            return Character(
                name=row_values[0] or "",
                mastodon_id=row_values[1] or "",
                faction=row_values[2] or "",
                health=int(row_values[3] or 0),
                strength=int(row_values[4] or 1),
                luck=int(row_values[5] or 0),
                bag_items=parse_inventory(row_values[6]),
                misc_items=parse_inventory(row_values[7]),
                nearby_items=parse_inventory(row_values[8]),
                row_index=i,
            )
    return None


@_retry_on_rate_limit
def batch_update_cells(updates: list[tuple[int, int, str]]) -> None:
    """여러 셀을 한 번에 업데이트. updates: [(row, col, value), ...] (1-based)."""
    if not updates:
        return
    ws = get_worksheet(WORKSHEET_MANAGEMENT)
    cells = []
    for row, col, value in updates:
        cell = ws.cell(row, col)
        cell.value = value
        cells.append(cell)
    ws.update_cells(cells)


@_retry_on_rate_limit
def update_bag_items(name: str, items: list[dict]) -> bool:
    """가방 아이템 업데이트 + 캐시 무효화"""
    char = get_character_by_name(name)
    if not char:
        return False

    bag_text = serialize_inventory(items)
    batch_update_cells([(char.row_index, ManagementColumns.BAG + 1, bag_text)])

    invalidate_character_cache(name)
    return True


@_retry_on_rate_limit
def update_nearby_items(name: str, items: list[dict]) -> bool:
    """주변 아이템 업데이트 + 캐시 무효화"""
    char = get_character_by_name(name)
    if not char:
        return False

    nearby_text = serialize_inventory(items)
    row, col = char.row_index, ManagementColumns.NEARBY + 1
    batch_update_cells([(row, col, nearby_text)])

    invalidate_character_cache(name)
    return True


@_retry_on_rate_limit
def update_bag_and_nearby_items(
    name: str,
    bag_items: list[dict],
    nearby_items: list[dict],
) -> bool:
    """가방·주변 아이템을 한 번의 API 호출로 배치 업데이트."""
    char = get_character_by_name(name)
    if not char:
        return False

    bag_text = serialize_inventory(bag_items)
    nearby_text = serialize_inventory(nearby_items)
    updates = [
        (char.row_index, ManagementColumns.BAG + 1, bag_text),
        (char.row_index, ManagementColumns.NEARBY + 1, nearby_text),
    ]
    batch_update_cells(updates)

    invalidate_character_cache(name)
    return True


@_retry_on_rate_limit
def update_misc_items(name: str, items: list[dict]) -> bool:
    """여유공간 아이템 업데이트 + 캐시 무효화"""
    char = get_character_by_name(name)
    if not char:
        return False

    misc_text = serialize_inventory(items)
    batch_update_cells([(char.row_index, ManagementColumns.MISC + 1, misc_text)])

    invalidate_character_cache(name)
    return True


def _record_to_character(record: dict, row_index: int) -> Character:
    """시트 레코드를 Character 객체로 변환"""
    return Character(
        name=str(record.get("이름") or ""),
        mastodon_id=str(record.get("아이디") or ""),
        faction=str(record.get("진영", "") or ""),
        health=int(record.get("체력", 0) or 0),
        strength=int(record.get("근력", 1) or 1),
        luck=int(record.get("행운", 0) or 0),
        bag_items=parse_inventory(record.get("가방", "")),
        misc_items=parse_inventory(record.get("여유공간", "")),
        nearby_items=parse_inventory(record.get("주변", "")),
        row_index=row_index,
    )
