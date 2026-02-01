/**
 * Types for the Bag/Inventory components
 */

export interface Item {
  id: string;
  name: string;
  count: number;
  volume: number;
  gridPosition?: { row: number; col: number };
  shapeIndex?: number;
  icon?: string;
  type?: 'consumable' | 'equipment';
}

export interface NearbyItem {
  id: string;
  name: string;
  volume: number;
  icon?: string;
  count?: number;
  ids?: string[];
}

export interface FreeItem extends Item {
  volume: 0;
}

export interface GridPosition {
  row: number;
  col: number;
}

export type ShapePattern = Array<GridPosition>;

export interface CellData {
  item: Item | null;
  isFirst: boolean;
}

export interface QuantityDialogState {
  isOpen: boolean;
  item: Item | NearbyItem | null;
  maxQuantity: number;
  selectedQuantity: number;
  action: 'toNearby' | 'toMisc' | null;
}
