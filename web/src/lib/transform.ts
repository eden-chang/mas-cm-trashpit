/**
 * API ↔ UI 데이터 변환
 */

import type { Item, NearbyItem, FreeItem } from '@/lib/types';
import type { ApiItemEnriched, ApiMiscItem, ApiLayoutItem } from '@/lib/types';

/** 캐릭터 데이터 변환 (필요 시 확장용) */
export function transformCharacterData<T>(data: T): T {
  return data;
}

/** UI 그리드 아이템 → API items (저장 요청) */
export function gridItemsToApiItems(items: Item[]): Array<{ name: string; quantity: number }> {
  return items.map((item) => ({ name: item.name, quantity: item.count }));
}

/** UI 그리드 아이템 → API layout (저장 요청) */
export function gridItemsToApiLayout(
  items: Item[]
): Array<{ name: string; row: number; col: number; shapeIndex: number }> {
  return items
    .filter((item) => item.gridPosition != null && item.volume > 0)
    .map((item) => ({
      name: item.name,
      row: item.gridPosition!.row,
      col: item.gridPosition!.col,
      shapeIndex: item.shapeIndex ?? 0,
    }));
}

/** UI 주변 아이템 → API nearby_items */
export function nearbyItemsToApiItems(
  items: NearbyItem[]
): Array<{ name: string; quantity: number }> {
  return items.map((item) => ({ name: item.name, quantity: item.count ?? 1 }));
}

/** UI 여유공간 아이템 → API misc_items */
export function freeItemsToApiItems(
  items: FreeItem[]
): Array<{ name: string; quantity: number }> {
  return items.map((item) => ({ name: item.name, quantity: item.count }));
}

/** API bag_items + bag_layout → UI 그리드 아이템 */
export function apiBagToGridItems(
  bagItems: ApiItemEnriched[],
  bagLayout: ApiLayoutItem[]
): Item[] {
  const layoutByName = new Map<string, ApiLayoutItem[]>();
  for (const l of bagLayout) {
    const list = layoutByName.get(l.name) ?? [];
    list.push(l);
    layoutByName.set(l.name, list);
  }
  const usedByName = new Map<string, number>();
  return bagItems.map((item, idx) => {
    const layouts = layoutByName.get(item.name) ?? [];
    const used = usedByName.get(item.name) ?? 0;
    const first = layouts[used];
    if (first) usedByName.set(item.name, used + 1);
    return {
      id: `i-${Date.now()}-${idx}`,
      name: item.name,
      count: item.quantity,
      volume: item.volume,
      gridPosition: first ? { row: first.row, col: first.col } : undefined,
      shapeIndex: first?.shapeIndex ?? 0,
    };
  });
}

/** API nearby_items → UI NearbyItem[] */
export function apiNearbyToItems(nearbyItems: ApiItemEnriched[]): NearbyItem[] {
  const out: NearbyItem[] = [];
  nearbyItems.forEach((item, groupIndex) => {
    for (let i = 0; i < item.quantity; i++) {
      out.push({
        id: `n-${Date.now()}-${groupIndex}-${i}`,
        name: item.name,
        volume: item.volume,
        count: 1,
      });
    }
  });
  return out;
}

/** API misc_items → UI FreeItem[] */
export function apiMiscToItems(miscItems: ApiMiscItem[]): Item[] {
  return miscItems.map((item, index) => ({
    id: `f-${Date.now()}-${index}`,
    name: item.name,
    count: item.quantity,
    volume: 0,
  }));
}
