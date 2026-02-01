"""캐릭터 API 엔드포인트"""

from flask import Blueprint, jsonify

from api.services.sheet_service import get_character_by_name
from api.services.inventory_service import enrich_items, calculate_total_volume

bp = Blueprint("character", __name__, url_prefix="/api")


def _bag_stats(char):
    """가방 사용량/가용량 (아이템 마스터 부피 기준)"""
    bag_items_dict = [{"name": i.name, "quantity": i.quantity} for i in char.bag_items]
    used = calculate_total_volume(bag_items_dict)
    return used, char.bag_capacity - used


@bp.route("/character/<name>")
def get_character(name: str):
    """캐릭터 전체 정보 조회"""
    char = get_character_by_name(name)

    if not char:
        return jsonify({"error": "캐릭터를 찾을 수 없습니다."}), 404

    bag_used, bag_available = _bag_stats(char)

    return jsonify({
        "name": char.name,
        "mastodon_id": char.mastodon_id,
        "faction": char.faction,
        "health": char.health,
        "strength": char.strength,
        "luck": char.luck,
        "bag_capacity": char.bag_capacity,
        "bag_used": bag_used,
        "bag_available": bag_available,
        "bag_items": enrich_items(char.bag_items),
        "misc_items": [{"name": i.name, "quantity": i.quantity} for i in char.misc_items],
        "nearby_items": enrich_items(char.nearby_items),
    })


@bp.route("/characters")
def list_characters():
    """전체 캐릭터 목록 조회"""
    from api.services.sheet_service import get_all_characters

    characters = get_all_characters()

    return jsonify([
        {
            "name": char.name,
            "bag_capacity": char.bag_capacity,
            "bag_used": char.bag_used,
            "nearby_count": len(char.nearby_items),
        }
        for char in characters
    ])
