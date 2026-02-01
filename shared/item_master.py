"""아이템 마스터 조회 (문서 1.2 - 아이템 마스터)

상점 워크시트에서 아이템 정보를 조회하고, 사용 가능·여유공간 여부를 판별합니다.
"""

import logging
from typing import Optional, Union

from .constants import WORKSHEET_SHOP
from .google_sheets import get_worksheet
from .models import ItemInfo

logger = logging.getLogger(__name__)


def record_to_item_info(record: dict) -> ItemInfo:
    """상점 시트 레코드 한 행을 ItemInfo로 변환 (가격·수치·부피 파싱).

    Raises:
        ValueError: 아이템명이 비어 있을 때.
    """
    name = (record.get("아이템명") or "").strip()
    if not name:
        raise ValueError("아이템 마스터 레코드에 아이템명이 없습니다.")
    raw_price = record.get("가격")
    if raw_price == "비매품" or (isinstance(raw_price, str) and raw_price.strip() == "비매품"):
        price: Union[int, str] = "비매품"
    else:
        try:
            price = int(raw_price) if raw_price is not None and str(raw_price).strip() else 0
        except (ValueError, TypeError):
            price = 0
    raw_volume = record.get("부피")
    try:
        vol = int(raw_volume) if raw_volume is not None and str(raw_volume).strip() else 0
    except (ValueError, TypeError):
        vol = 0
    volume = max(0, vol)  # 문서 1.2: 부피는 0 이상

    return ItemInfo(
        name=name,
        price=price,
        description=str(record.get("설명") or "").strip(),
        use_message=str(record.get("사용문구") or "").strip(),
        stat=str(record.get("스탯") or "").strip(),
        value=str(record.get("수치") or "").strip(),
        volume=volume,
    )


def get_item_info(item_name: str) -> Optional[ItemInfo]:
    """상점에서 아이템 정보 조회 (2행 정보행 스킵). 시트 접근 실패 시 None 반환."""
    if not (item_name and item_name.strip()):
        return None
    try:
        ws = get_worksheet(WORKSHEET_SHOP)
        records = ws.get_all_records()[1:]  # 2행 스킵 (문서 1.1)
        key = item_name.strip()
        for record in records:
            name = (record.get("아이템명") or "").strip()
            if name == key:
                return record_to_item_info(record)
        return None
    except Exception as e:
        logger.exception("상점 시트 아이템 조회 실패: %s", e)
        return None


def get_all_item_infos() -> list[ItemInfo]:
    """상점 시트에서 전체 아이템 목록 조회 (2행 스킵). 시트 1회 읽기.

    Returns:
        아이템명이 있는 행만 포함. 시트 접근 실패 시 예외 전파.
    """
    ws = get_worksheet(WORKSHEET_SHOP)
    records = ws.get_all_records()[1:]
    result: list[ItemInfo] = []
    for record in records:
        name = (record.get("아이템명") or "").strip()
        if not name:
            continue
        try:
            result.append(record_to_item_info(record))
        except ValueError:
            logger.warning("아이템 마스터 행 스킵(아이템명 없음): %s", record)
    return result


def is_usable(item_info: ItemInfo) -> bool:
    """아이템 사용 가능 여부 (사용문구 있음 + 스탯이 '사용 불가' 아님)"""
    msg = (item_info.use_message or "").strip()
    stat = (item_info.stat or "").strip()
    return bool(msg and msg != "-") and stat != "사용 불가"


def is_misc_item(item_info: ItemInfo) -> bool:
    """부피 0 아이템(여유공간) 여부"""
    return (item_info.volume or 0) == 0
