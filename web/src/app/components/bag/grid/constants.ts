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
 * Get item colors - 통일된 검정 배경 (아이템 내부 비텍스트는 검정)
 * 텍스트 색상만 구분용으로 사용
 */
export function getItemColors(_type?: 'consumable' | 'equipment') {
  return {
    fill: 'var(--color-item-fill)',
    border: 'var(--color-item-border)',
    textColor: 'var(--color-item-placed)',
  };
}
