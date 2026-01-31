"""캐릭터 API 엔드포인트"""

from flask import Blueprint, jsonify

from api.services.sheet_service import get_character_by_name
from api.services.inventory_service import enrich_items

bp = Blueprint("character", __name__, url_prefix="/api")


@bp.route("/character/<name>")
def get_character(name: str):
    """캐릭터 전체 정보 조회"""
    char = get_character_by_name(name)

    if not char:
        return jsonify({"error": "캐릭터를 찾을 수 없습니다."}), 404

    return jsonify({
        "name": char.name,
        "mastodon_id": char.mastodon_id,
        "health": char.health,
        "strength": char.strength,
        "luck": char.luck,
        "bag_capacity": char.bag_capacity,
        "bag_used": char.bag_used,
        "bag_available": char.bag_available,
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
