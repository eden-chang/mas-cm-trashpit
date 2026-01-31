"""가방 API 엔드포인트"""

from flask import Blueprint, jsonify, request

from api.services.sheet_service import get_character_by_name, update_bag_items
from api.services.inventory_service import enrich_items, calculate_total_volume
from api.services.item_service import get_item_info

bp = Blueprint("bag", __name__, url_prefix="/api")


@bp.route("/bag/<name>")
def get_bag(name: str):
    """가방 아이템 조회"""
    char = get_character_by_name(name)

    if not char:
        return jsonify({"error": "캐릭터를 찾을 수 없습니다."}), 404

    return jsonify({
        "capacity": char.bag_capacity,
        "used": char.bag_used,
        "available": char.bag_available,
        "items": enrich_items(char.bag_items),
    })


@bp.route("/bag/<name>", methods=["POST"])
def update_bag(name: str):
    """가방 아이템 업데이트"""
    char = get_character_by_name(name)

    if not char:
        return jsonify({"error": "캐릭터를 찾을 수 없습니다."}), 404

    items = request.json.get("items", [])

    # 용량 검증
    total_volume = 0
    for item in items:
        info = get_item_info(item["name"])
        volume = info.volume if info else 0
        total_volume += volume * item["quantity"]

    if total_volume > char.bag_capacity:
        return jsonify({
            "success": False,
            "error": f"용량 초과 ({total_volume}/{char.bag_capacity})",
        }), 400

    # 시트 업데이트
    update_bag_items(name, items)

    return jsonify({
        "success": True,
        "used": total_volume,
        "available": char.bag_capacity - total_volume,
    })
