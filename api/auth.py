"""API 인증: 캐릭터별 서명 링크 토큰과 관리자 Bearer 토큰 검증."""

import hmac
import logging
from functools import wraps
from typing import Callable

from flask import jsonify, request

from api import config
from shared.access_token import is_valid_secret, verify_token

logger = logging.getLogger(__name__)

CHARACTER_TOKEN_HEADER = "X-Character-Token"


def require_character_token(view: Callable) -> Callable:
    """URL의 <name>과 서명 토큰의 캐릭터가 일치할 때만 요청을 허용한다."""

    @wraps(view)
    def wrapper(name: str, *args, **kwargs):
        if not is_valid_secret(config.INVENTORY_LINK_SECRET):
            logger.error("INVENTORY_LINK_SECRET이 설정되지 않아 캐릭터 API 요청을 거부함")
            return jsonify({"error": "서버 인증 설정이 완료되지 않았습니다."}), 503

        token_name = verify_token(request.headers.get(CHARACTER_TOKEN_HEADER), config.INVENTORY_LINK_SECRET)
        if token_name is None:
            return jsonify({
                "error": "유효하지 않거나 만료된 링크입니다. 봇에게 [가방 링크]를 다시 요청해 주세요.",
            }), 401
        if token_name != name:
            logger.warning("캐릭터 토큰 불일치: 토큰=%s, 요청=%s", token_name, name)
            return jsonify({"error": "이 캐릭터에 접근할 권한이 없습니다."}), 403

        return view(name, *args, **kwargs)

    return wrapper


def check_admin_token():
    """관리자 API용 before_request 훅. 통과하면 None, 실패하면 오류 응답을 반환한다."""
    if not is_valid_secret(config.ADMIN_API_TOKEN):
        return jsonify({"error": "관리자 API가 비활성화되어 있습니다."}), 503

    header = request.headers.get("Authorization", "")
    scheme, _, provided = header.partition(" ")
    if scheme != "Bearer" or not hmac.compare_digest(provided.encode(), config.ADMIN_API_TOKEN.encode()):
        return jsonify({"error": "관리자 인증이 필요합니다."}), 401

    return None
