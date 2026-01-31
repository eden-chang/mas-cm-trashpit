"""아이템 API 엔드포인트"""

from flask import Blueprint, jsonify

from api.services.item_service import get_item_info, get_all_items

bp = Blueprint("items", __name__, url_prefix="/api")


@bp.route("/items")
def list_items():
    """전체 아이템 목록 조회"""
    items = get_all_items()

    return jsonify([
        {
            "name": item.name,
            "price": item.price,
            "description": item.description,
            "volume": item.volume,
        }
        for item in items
    ])


@bp.route("/item/<name>")
def get_item(name: str):
    """아이템 정보 조회"""
    item = get_item_info(name)

    if not item:
        return jsonify({"error": "아이템을 찾을 수 없습니다."}), 404

    return jsonify({
        "name": item.name,
        "price": item.price,
        "description": item.description,
        "use_message": item.use_message,
        "stat": item.stat,
        "value": item.value,
        "volume": item.volume,
    })
