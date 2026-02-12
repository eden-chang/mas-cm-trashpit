"""관리자 API 엔드포인트 (Phase 3.3)

캐시 관리 및 시스템 상태 확인용.
TODO: 실제 운영 시 인증 추가 필요
"""

import logging

from flask import Blueprint, jsonify

from shared.cache import invalidate_cache, get_cache_stats, cleanup_expired

logger = logging.getLogger(__name__)

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.route("/cache/stats")
def cache_stats():
    """캐시 통계 조회 (Phase 3.3 캐시 모니터링)"""
    stats = get_cache_stats()
    logger.debug("캐시 통계: %s", stats)
    return jsonify(stats)


@bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """전체 캐시 초기화"""
    count = invalidate_cache()
    return jsonify({
        "success": True,
        "message": f"캐시 {count}건 삭제됨",
    })


@bp.route("/cache/cleanup", methods=["POST"])
def cleanup_cache():
    """만료된 캐시 정리"""
    count = cleanup_expired()
    return jsonify({
        "success": True,
        "message": f"만료 캐시 {count}건 정리됨",
    })



@bp.route("/characters/refresh", methods=["POST"])
def refresh_characters():
    """캐릭터 캐시 새로고침. 관리 시트 업데이트 시 호출."""
    try:
        invalidate_cache("get_all_characters")
        invalidate_cache("get_character_by_name")
        invalidate_cache("get_character_by_mastodon_id")
        return jsonify({
            "success": True,
            "message": "캐릭터 캐시 새로고침 완료",
        })
    except Exception as e:
        logger.exception("캐릭터 캐시 새로고침 실패")
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500
