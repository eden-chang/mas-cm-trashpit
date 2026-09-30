"""캐릭터 API 엔드포인트"""

from flask import Blueprint, jsonify

from api.auth import require_character_token
from api.services.sheet_service import get_character_by_name
from api.services.inventory_service import enrich_items, calculate_total_volume

bp = Blueprint("character", __name__, url_prefix="/api")


def _bag_stats(char):
    """가방 사용량/가용량 (아이템 마스터 부피 기준)"""
    bag_items_dict = [{"name": i.name, "quantity": i.quantity} for i in char.bag_items]
    used = calculate_total_volume(bag_items_dict)
    return used, char.bag_capacity - used


@bp.route("/character/<name>")
@require_character_token
def get_character(name: str):
    """캐릭터 전체 정보 조회"""
    char = get_character_by_name(name)

    if not char:
        return jsonify({"error": "캐릭터를 찾을 수 없습니다."}), 404

    bag_used, bag_available = _bag_stats(char)

    # 배치 정보 변환
    bag_layout = [
        {
            "name": l.name,
            "row": l.row,
            "col": l.col,
            "shapeIndex": l.shapeIndex,
        }
        for l in char.bag_layout
    ]

    return jsonify({
        "name": char.name,
        "mastodon_id": char.mastodon_id,
        "faction": char.faction,
        "health": char.health,
        "strength": char.strength,
        "luck": char.luck,
        "hp": char.hp,
        "max_hp": char.max_hp,
        "bag_capacity": char.bag_capacity,
        "bag_used": bag_used,
        "bag_available": bag_available,
        "bag_items": enrich_items(char.bag_items),
        "misc_items": [{"name": i.name, "quantity": i.quantity} for i in char.misc_items],
        "nearby_items": enrich_items(char.nearby_items),
        "bag_layout": bag_layout,
    })


@bp.route("/characters")
def list_characters():
    """전체 캐릭터 목록 조회 (이름순 정렬)"""
    from api.services.sheet_service import get_all_characters

    characters = get_all_characters()

    # 명시적으로 딕셔너리 생성
    result = []
    for char in characters:
        # bag_used 계산: 아이템 마스터에서 부피 정보를 가져와서 계산
        bag_items_dict = [{"name": i.name, "quantity": i.quantity} for i in char.bag_items]
        bag_used = calculate_total_volume(bag_items_dict)
        
        result.append({
            "name": str(char.name),
            "bag_capacity": int(char.bag_capacity),
            "bag_used": int(bag_used),
            "nearby_count": int(len(char.nearby_items)),
            "health": int(char.health),
            "hp": int(char.hp),
            "max_hp": int(char.max_hp),
        })
    
    return jsonify(result)
