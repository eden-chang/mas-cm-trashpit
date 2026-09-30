"""주변 아이템 API 엔드포인트"""

from flask import Blueprint, jsonify, request

from api.auth import require_character_token
from api.services.sheet_service import get_character_by_name
from api.services.inventory_service import enrich_items, move_nearby_to_bag

bp = Blueprint("nearby", __name__, url_prefix="/api")


@bp.route("/nearby/<name>")
@require_character_token
def get_nearby(name: str):
    """주변 아이템 조회"""
    char = get_character_by_name(name)

    if not char:
        return jsonify({"error": "캐릭터를 찾을 수 없습니다."}), 404

    return jsonify({
        "items": enrich_items(char.nearby_items),
    })


@bp.route("/nearby/<name>/move", methods=["POST"])
@require_character_token
def move_to_bag(name: str):
    """주변 아이템을 가방으로 이동"""
    char = get_character_by_name(name)

    if not char:
        return jsonify({"error": "캐릭터를 찾을 수 없습니다."}), 404

    item_name = request.json.get("item_name")
    quantity = request.json.get("quantity", 1)

    result = move_nearby_to_bag(char, item_name, quantity)

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)
