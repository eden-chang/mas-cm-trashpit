/**
 * Grid constants and shape patterns for tetris-style inventory
 */

import type { ShapePattern } from '../types';

export const GRID_COLS = 10;

// Shape patterns for different volumes (relative coordinates from top-left)
export const SHAPES: Record<number, ShapePattern[]> = {
  1: [
    [{ row: 0, col: 0 }], // 1칸
  ],
  2: [
    [{ row: 0, col: 0 }, { row: 0, col: 1 }], // 가로 1×2
    [{ row: 0, col: 0 }, { row: 1, col: 0 }], // 세로 2×1
  ],
  3: [
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }], // 가로 1×3
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }], // 세로 3×1
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 0, col: 1 }], // L자
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 1 }], // ㄱ자
  ],
  4: [
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }, { row: 0, col: 3 }], // 가로 1×4
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }, { row: 3, col: 0 }], // 세로 4×1
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 0 }, { row: 1, col: 1 }], // 정사각형 2×2
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }, { row: 2, col: 1 }], // L자
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 1 }, { row: 2, col: 1 }], // ㄴ자
  ],
  6: [
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }, { row: 0, col: 3 }, { row: 0, col: 4 }, { row: 0, col: 5 }], // 가로 1×6
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }, { row: 3, col: 0 }, { row: 4, col: 0 }, { row: 5, col: 0 }], // 세로 6×1
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }, { row: 1, col: 0 }, { row: 1, col: 1 }, { row: 1, col: 2 }], // 2×3
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 1 }, { row: 2, col: 1 }], // 3×2
  ],
};

/**
 * Get shape pattern for a given volume and shape index
 */
export function getShape(volume: number, shapeIndex: number): ShapePattern {
  const shapes = SHAPES[volume] || SHAPES[1];
  return shapes[shapeIndex % shapes.length];
}

/**
 * Get item colors based on type
 */
export function getItemColors(type?: 'consumable' | 'equipment') {
  if (type === 'consumable') {
    return { border: '#00F3FF', glow: 'rgba(0, 243, 255, 0.4)', bg: 'rgba(0, 243, 255, 0.15)' };
  }
  if (type === 'equipment') {
    return { border: '#FFB020', glow: 'rgba(255, 176, 32, 0.4)', bg: 'rgba(255, 176, 32, 0.15)' };
  }
  return { border: '#BF5AF2', glow: 'rgba(191, 90, 242, 0.4)', bg: 'rgba(191, 90, 242, 0.15)' };
}
