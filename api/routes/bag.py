"""가방 API 엔드포인트"""

from flask import Blueprint, jsonify, request

from api.auth import require_character_token
from api.services.sheet_service import get_character_by_name, update_bag_items, update_inventory
from api.services.inventory_service import enrich_items, calculate_total_volume
from api.services.item_service import get_item_info

bp = Blueprint("bag", __name__, url_prefix="/api")


@bp.route("/bag/<name>")
@require_character_token
def get_bag(name: str):
    """가방 아이템 조회"""
    char = get_character_by_name(name)

    if not char:
        return jsonify({"error": "캐릭터를 찾을 수 없습니다."}), 404

    bag_items_dict = [{"name": i.name, "quantity": i.quantity} for i in char.bag_items]
    used = calculate_total_volume(bag_items_dict)
    available = char.bag_capacity - used

    return jsonify({
        "capacity": char.bag_capacity,
        "used": used,
        "available": available,
        "items": enrich_items(char.bag_items),
        "updated_at": char.updated_at,  # 동기화용 타임스탬프
    })


@bp.route("/bag/<name>", methods=["POST"])
@require_character_token
def update_bag(name: str):
    """가방·주변·여유공간 전체 인벤토리 업데이트 (동기화용)"""
    char = get_character_by_name(name)

    if not char:
        return jsonify({"error": "캐릭터를 찾을 수 없습니다."}), 404

    # 충돌 감지: 클라이언트가 알고 있는 타임스탬프와 서버 타임스탬프 비교
    client_timestamp = request.json.get("last_known_update")
    if client_timestamp and char.updated_at and client_timestamp != char.updated_at:
        return jsonify({
            "success": False,
            "error": "다른 곳에서 변경되었습니다. 새로고침 후 다시 시도하세요.",
            "conflict": True,
            "server_timestamp": char.updated_at,
        }), 409

    items = request.json.get("items", [])
    nearby_items = request.json.get("nearby_items")
    misc_items = request.json.get("misc_items")

    # 하위 호환: items만 오면 가방만 업데이트 (기존 API)
    if nearby_items is None and misc_items is None:
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

        update_bag_items(name, items)
        # 업데이트 후 새 타임스탬프 조회
        updated_char = get_character_by_name(name)
        return jsonify({
            "success": True,
            "used": total_volume,
            "available": char.bag_capacity - total_volume,
            "updated_at": updated_char.updated_at if updated_char else None,
        })

    # 전체 인벤토리 동기화: 가방·주변·여유공간 한 번에 업데이트
    bag_items = [{"name": i["name"], "quantity": i["quantity"]} for i in items]
    nearby_list = [{"name": i["name"], "quantity": i["quantity"]} for i in (nearby_items or [])]
    misc_list = [{"name": i["name"], "quantity": i["quantity"]} for i in (misc_items or [])]
    
    # 배치 정보 처리
    layout = request.json.get("layout")
    bag_layout = None
    if layout is not None:
        bag_layout = [
            {
                "name": l.get("name", ""),
                "row": l.get("row", 0),
                "col": l.get("col", 0),
                "shapeIndex": l.get("shapeIndex", 0),
            }
            for l in layout
        ]

    total_volume = 0
    for item in bag_items:
        info = get_item_info(item["name"])
        volume = info.volume if info else 0
        total_volume += volume * item["quantity"]

    if total_volume > char.bag_capacity:
        return jsonify({
            "success": False,
            "error": f"용량 초과 ({total_volume}/{char.bag_capacity})",
        }), 400

    update_inventory(name, bag_items, nearby_list, misc_list, bag_layout)

    # 업데이트 후 새 타임스탬프 조회
    updated_char = get_character_by_name(name)
    return jsonify({
        "success": True,
        "used": total_volume,
        "available": char.bag_capacity - total_volume,
        "updated_at": updated_char.updated_at if updated_char else None,
    })
