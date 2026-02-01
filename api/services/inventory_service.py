"""인벤토리 관련 서비스"""

from shared.models import Character, Item
from api.services.item_service import get_item_info
from api.services.sheet_service import update_bag_items, update_nearby_items


def enrich_items(items: list[Item]) -> list[dict]:
    """아이템에 부피 정보 추가"""
    result = []
    for item in items:
        info = get_item_info(item.name)
        volume = info.volume if info else 0
        result.append({
            "name": item.name,
            "quantity": item.quantity,
            "volume": volume,
            "total_volume": volume * item.quantity,
        })
    return result


def calculate_total_volume(items: list[dict]) -> int:
    """아이템 리스트의 총 부피 계산"""
    total = 0
    for item in items:
        info = get_item_info(item["name"])
        volume = info.volume if info else 0
        total += volume * item.get("quantity", 1)
    return total


def move_nearby_to_bag(char: Character, item_name: str, quantity: int = 1) -> dict:
    """주변 아이템을 가방으로 이동"""
    nearby_item = next(
        (item for item in char.nearby_items if item.name == item_name),
        None,
    )

    if not nearby_item:
        return {"success": False, "error": f"주변에 '{item_name}'이(가) 없습니다."}

    if nearby_item.quantity < quantity:
        return {"success": False, "error": f"수량이 부족합니다. (보유: {nearby_item.quantity})"}

    info = get_item_info(item_name)
    volume = info.volume if info else 0
    required_space = volume * quantity

    bag_items_dict = [{"name": i.name, "quantity": i.quantity} for i in char.bag_items]
    bag_used = calculate_total_volume(bag_items_dict)
    bag_available = char.bag_capacity - bag_used

    if required_space > bag_available:
        return {
            "success": False,
            "error": f"가방 공간이 부족합니다. (필요: {required_space}, 남음: {bag_available})",
        }

    # 주변에서 제거
    if nearby_item.quantity == quantity:
        char.nearby_items.remove(nearby_item)
    else:
        nearby_item.quantity -= quantity

    # 가방에 추가
    bag_item = None
    for item in char.bag_items:
        if item.name == item_name:
            bag_item = item
            break

    if bag_item:
        bag_item.quantity += quantity
    else:
        char.bag_items.append(Item(name=item_name, quantity=quantity, volume=volume))

    # 시트 업데이트
    update_bag_items(char.name, [{"name": i.name, "quantity": i.quantity} for i in char.bag_items])
    update_nearby_items(char.name, [{"name": i.name, "quantity": i.quantity} for i in char.nearby_items])

    return {"success": True, "message": f"{item_name}을(를) 가방에 넣었습니다."}
