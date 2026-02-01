"""인벤토리 파싱 유틸리티 (shared.parser 재수출)

호환성 유지: 기존 api.utils.parser import 경로 그대로 사용 가능.
"""

from shared.parser import parse_inventory, serialize_inventory

__all__ = ["parse_inventory", "serialize_inventory"]
