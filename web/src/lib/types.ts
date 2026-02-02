/**
 * API·UI 공통 타입 정의
 */

/** 캐릭터 목록 항목 (GET /api/characters) */
export interface CharacterSummary {
  name: string;
  bag_capacity: number;
  bag_used: number;
  nearby_count?: number;
  health?: number;
  hp: number;
  max_hp: number;
}

/** API 배치 항목 */
export interface ApiLayoutItem {
  name: string;
  row: number;
  col: number;
  shapeIndex: number;
  id?: string;
}

/** API 가방/주변 아이템 (enrich_items 응답) */
export interface ApiItemEnriched {
  name: string;
  quantity: number;
  volume: number;
  total_volume: number;
}

/** API 여유공간 아이템 */
export interface ApiMiscItem {
  name: string;
  quantity: number;
}

/** 캐릭터 상세 (GET /api/character/:name) */
export interface ApiCharacter {
  name: string;
  mastodon_id?: string;
  faction?: string;
  health?: number;
  strength?: number;
  luck?: number;
  hp: number;
  max_hp: number;
  bag_capacity: number;
  bag_used: number;
  bag_available?: number;
  bag_items: ApiItemEnriched[];
  misc_items: ApiMiscItem[];
  nearby_items: ApiItemEnriched[];
  bag_layout: ApiLayoutItem[];
  updated_at?: string | null;
}

/** UI 그리드 아이템 */
export interface Item {
  id: string;
  name: string;
  count: number;
  volume: number;
  gridPosition?: { row: number; col: number };
  shapeIndex?: number;
  icon?: string;
  type?: 'consumable' | 'equipment';
  color?: string;
}

/** UI 주변 아이템 */
export interface NearbyItem {
  id: string;
  name: string;
  volume: number;
  icon?: string;
  count?: number;
  ids?: string[];
}

/** UI 여유공간 아이템 (부피 0) */
export interface FreeItem extends Item {
  volume: 0;
}
