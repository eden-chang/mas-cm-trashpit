/**
 * Grid constants and shape patterns for tetris-style inventory
 * 음수 오프셋: 앵커(0,0) 기준 왼쪽/위로 확장 (CSS absolute positioning으로 렌더링)
 */

import type { ShapePattern } from '../types';

export const GRID_COLS = 10;

// Shape patterns for different volumes (relative coordinates from anchor at (0,0))
export const SHAPES: Record<number, ShapePattern[]> = {
  1: [
    [{ row: 0, col: 0 }], // 1칸
  ],
  2: [
    [{ row: 0, col: 0 }, { row: 0, col: 1 }], // 가로 1×2
    [{ row: 0, col: 0 }, { row: 1, col: 0 }], // 세로 2×1
  ],
  3: [
    // 직선 (2가지)
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }], // 가로 1×3
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }], // 세로 3×1
    // L자 4방향 회전
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 0 }], // ┘ (XX / X.)
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 1 }], // └ (XX / .X)
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 1, col: 1 }], // ┐ (X. / XX)
    [{ row: 0, col: 0 }, { row: 1, col: -1 }, { row: 1, col: 0 }], // ┌ (.X / XX)
  ],
  4: [
    // 직선 (2가지)
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }, { row: 0, col: 3 }], // 가로 1×4
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }, { row: 3, col: 0 }], // 세로 4×1
    // 정사각형
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 0 }, { row: 1, col: 1 }], // 2×2
    // L자 4방향 회전
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }, { row: 2, col: 1 }],   // L-0: X./X./XX
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }, { row: 1, col: 0 }],   // L-90: XXX/X..
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 1 }, { row: 2, col: 1 }],   // L-180: XX/.X/.X
    [{ row: 0, col: 0 }, { row: 1, col: -2 }, { row: 1, col: -1 }, { row: 1, col: 0 }], // L-270: ..X/XXX
    // J자 4방향 회전 (L 거울)
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: -1 }, { row: 2, col: 0 }],  // J-0: .X/.X/XX
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 1, col: 1 }, { row: 1, col: 2 }],   // J-90: X../XXX
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 0 }, { row: 2, col: 0 }],   // J-180: XX/X./X.
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }, { row: 1, col: 2 }],   // J-270: XXX/..X
  ],
  6: [
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }, { row: 1, col: 0 }, { row: 1, col: 1 }, { row: 1, col: 2 }], // 2×3
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 1 }, { row: 2, col: 1 }], // 3×2
    [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 }, { row: 0, col: 3 }, { row: 0, col: 4 }, { row: 0, col: 5 }], // 가로 1×6
    [{ row: 0, col: 0 }, { row: 1, col: 0 }, { row: 2, col: 0 }, { row: 3, col: 0 }, { row: 4, col: 0 }, { row: 5, col: 0 }], // 세로 6×1
  ],
};

// 5~20칸: 직사각형 모양 자동 생성
function generateRectShapes(volume: number): ShapePattern[] {
  const shapes: ShapePattern[] = [];
  for (let rows = 1; rows <= volume; rows++) {
    if (volume % rows !== 0) continue;
    const cols = volume / rows;
    const shape: ShapePattern = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        shape.push({ row: r, col: c });
      }
    }
    shapes.push(shape);
  }
  shapes.sort((a, b) => {
    const aR = Math.max(...a.map(p => p.row)) + 1;
    const aC = Math.max(...a.map(p => p.col)) + 1;
    const bR = Math.max(...b.map(p => p.row)) + 1;
    const bC = Math.max(...b.map(p => p.col)) + 1;
    return Math.abs(aR - aC) - Math.abs(bR - bC);
  });
  return shapes;
}

for (let v = 2; v <= 20; v++) {
  if (!SHAPES[v]) {
    SHAPES[v] = generateRectShapes(v);
  }
}

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
