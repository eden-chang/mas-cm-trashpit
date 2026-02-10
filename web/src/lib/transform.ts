/**
 * API ↔ UI 데이터 변환
 */

import type { Item, NearbyItem, FreeItem } from '@/lib/types';
import type { ApiItemEnriched, ApiMiscItem, ApiLayoutItem } from '@/lib/types';

/** 캐릭터 데이터 변환 (필요 시 확장용) */
export function transformCharacterData<T>(data: T): T {
  return data;
}

/** UI 그리드 아이템 → API items (저장 요청, 같은 이름 아이템 수량 합산) */
export function gridItemsToApiItems(items: Item[]): Array<{ name: string; quantity: number }> {
  const aggregated = new Map<string, number>();
  for (const item of items) {
    aggregated.set(item.name, (aggregated.get(item.name) ?? 0) + item.count);
  }
  return Array.from(aggregated, ([name, quantity]) => ({ name, quantity }));
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

/** UI 주변 아이템 → API nearby_items (같은 이름 아이템 수량 합산) */
export function nearbyItemsToApiItems(
  items: NearbyItem[]
): Array<{ name: string; quantity: number }> {
  const aggregated = new Map<string, number>();
  for (const item of items) {
    aggregated.set(item.name, (aggregated.get(item.name) ?? 0) + (item.count ?? 1));
  }
  return Array.from(aggregated, ([name, quantity]) => ({ name, quantity }));
}

/** UI 여유공간 아이템 → API misc_items (같은 이름 아이템 수량 합산) */
export function freeItemsToApiItems(
  items: FreeItem[]
): Array<{ name: string; quantity: number }> {
  const aggregated = new Map<string, number>();
  for (const item of items) {
    aggregated.set(item.name, (aggregated.get(item.name) ?? 0) + item.count);
  }
  return Array.from(aggregated, ([name, quantity]) => ({ name, quantity }));
}

/**
 * API bag_items + bag_layout → UI 그리드 아이템
 * quantity > 1인 아이템은 개별 Item(count: 1)으로 확장하여
 * 각각 고유한 그리드 위치를 가지도록 함
 */
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

  const result: Item[] = [];
  let idCounter = 0;
  const usedByName = new Map<string, number>();

  for (const item of bagItems) {
    const layouts = layoutByName.get(item.name) ?? [];

    // 부피 있는 아이템: 개별 인스턴스로 확장 (각각 독립적인 그리드 위치)
    if (item.volume > 0 && item.quantity > 1) {
      for (let i = 0; i < item.quantity; i++) {
        const used = usedByName.get(item.name) ?? 0;
        const layout = layouts[used];
        if (layout) usedByName.set(item.name, used + 1);

        result.push({
          id: `i-${Date.now()}-${idCounter++}`,
          name: item.name,
          count: 1,
          volume: item.volume,
          gridPosition: layout ? { row: layout.row, col: layout.col } : undefined,
          shapeIndex: layout?.shapeIndex ?? 0,
        });
      }
    } else {
      // 부피 0 또는 수량 1: 기존 방식
      const used = usedByName.get(item.name) ?? 0;
      const layout = layouts[used];
      if (layout) usedByName.set(item.name, used + 1);

      result.push({
        id: `i-${Date.now()}-${idCounter++}`,
        name: item.name,
        count: item.quantity,
        volume: item.volume,
        gridPosition: layout ? { row: layout.row, col: layout.col } : undefined,
        shapeIndex: layout?.shapeIndex ?? 0,
      });
    }
  }

  return result;
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
