"""구글 시트 서비스"""

from typing import Optional

from shared.google_sheets import get_worksheet
from shared.constants import WORKSHEET_MANAGEMENT
from shared.models import Character, Item
from api.utils.parser import parse_inventory, serialize_inventory


def get_all_characters() -> list[Character]:
    """전체 캐릭터 목록 조회"""
    ws = get_worksheet(WORKSHEET_MANAGEMENT)
    records = ws.get_all_records()[1:]  # 2행(정보행) 스킵

    characters = []
    for idx, record in enumerate(records):
        char = _record_to_character(record, row_index=idx + 3)
        characters.append(char)

    return characters


def get_character_by_name(name: str) -> Optional[Character]:
    """이름으로 캐릭터 조회"""
    ws = get_worksheet(WORKSHEET_MANAGEMENT)
    records = ws.get_all_records()[1:]

    for idx, record in enumerate(records):
        if record["이름"] == name:
            return _record_to_character(record, row_index=idx + 3)

    return None


def get_character_by_mastodon_id(mastodon_id: str) -> Optional[Character]:
    """마스토돈 ID로 캐릭터 조회"""
    ws = get_worksheet(WORKSHEET_MANAGEMENT)
    records = ws.get_all_records()[1:]

    for idx, record in enumerate(records):
        if record["아이디"] == mastodon_id:
            return _record_to_character(record, row_index=idx + 3)

    return None


def update_bag_items(name: str, items: list[dict]):
    """가방 아이템 업데이트"""
    char = get_character_by_name(name)
    if not char:
        return False

    ws = get_worksheet(WORKSHEET_MANAGEMENT)
    bag_text = serialize_inventory(items)

    # 가방 컬럼 (F열 = 6)
    ws.update_cell(char.row_index, 6, bag_text)
    return True


def update_nearby_items(name: str, items: list[dict]):
    """주변 아이템 업데이트"""
    char = get_character_by_name(name)
    if not char:
        return False

    ws = get_worksheet(WORKSHEET_MANAGEMENT)
    nearby_text = serialize_inventory(items)

    # 주변 컬럼 (H열 = 8)
    ws.update_cell(char.row_index, 8, nearby_text)
    return True


def _record_to_character(record: dict, row_index: int) -> Character:
    """시트 레코드를 Character 객체로 변환"""
    return Character(
        name=record["이름"],
        mastodon_id=record["아이디"],
        health=int(record.get("체력", 0) or 0),
        strength=int(record.get("근력", 1) or 1),
        luck=int(record.get("행운", 0) or 0),
        bag_items=parse_inventory(record.get("가방", "")),
        misc_items=parse_inventory(record.get("여유공간", "")),
        nearby_items=parse_inventory(record.get("주변", "")),
        row_index=row_index,
    )
