import { useState, useEffect, useCallback, memo } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Coins, FileText, Paperclip, AlertCircle } from 'lucide-react';
import type { ApiCharacter } from '@/lib/types';
import { QuantityDialog } from '@/app/components/bag/dialogs';
import type { QuantityDialogState } from '@/app/components/bag/types';
import { apiBagToGridItems, apiNearbyToItems, apiMiscToItems } from '@/lib/transform';

interface Item {
  id: string;
  name: string;
  count: number;
  volume: number;
  gridPosition?: { row: number; col: number };
  shapeIndex?: number; // 현재 선택된 모양 인덱스
  icon?: string;
  type?: 'consumable' | 'equipment'; // 아이템 타입
  color?: string; // 아이템 고유 색상
}

interface NearbyItem {
  id: string;
  name: string;
  volume: number;
  icon?: string;
  count?: number; // 그룹화된 수량 정보 추가
  ids?: string[]; // 그룹화된 아이템 ID들
}

// 부피별 가능한 모양들 (상대 좌표, 첫 번째 셀이 (0,0) 앵커)
// 음수 오프셋: 앵커 기준 왼쪽/위로 확장 (CSS absolute positioning으로 렌더링)
type ShapePattern = Array<{ row: number; col: number }>;

const SHAPES: Record<number, ShapePattern[]> = {
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

/**
 * 5칸 이상: 최대한 박스(직사각형) 형태로 자동 생성
 * 정사각형에 가까운 순서대로 정렬
 */
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
  // 정사각형에 가까운 순서대로 정렬
  shapes.sort((a, b) => {
    const aR = Math.max(...a.map(p => p.row)) + 1;
    const aC = Math.max(...a.map(p => p.col)) + 1;
    const bR = Math.max(...b.map(p => p.row)) + 1;
    const bC = Math.max(...b.map(p => p.col)) + 1;
    return Math.abs(aR - aC) - Math.abs(bR - bC);
  });
  return shapes;
}

// 5~20칸: 직사각형 모양 자동 생성
for (let v = 2; v <= 20; v++) {
  if (!SHAPES[v]) {
    SHAPES[v] = generateRectShapes(v);
  }
}

// ============================================================
// 랜덤 색상 생성 함수
// ============================================================

/**
 * 아이템별 랜덤 색상 생성
 * 색상 범위: #c7baa7 (밝음) ~ #846539 (어두움)
 */
function generateRandomItemColor(): string {
  // #c7baa7 = RGB(199, 186, 167)
  // #846539 = RGB(132, 101, 57)
  const r = Math.floor(132 + Math.random() * (199 - 132));
  const g = Math.floor(101 + Math.random() * (186 - 101));
  const b = Math.floor(57 + Math.random() * (167 - 57));
  return `rgb(${r}, ${g}, ${b})`;
}

// ============================================================
// 자동 배치 헬퍼 함수들
// ============================================================

/**
 * 특정 위치에 아이템을 배치할 수 있는지 확인
 */
function canPlaceAtPosition(
  shape: ShapePattern,
  startRow: number,
  startCol: number,
  occupiedCells: Set<string>,
  gridRows: number,
  gridCols: number
): boolean {
  for (const pos of shape) {
    const row = startRow + pos.row;
    const col = startCol + pos.col;
    
    // 그리드 범위 체크
    if (row < 0 || row >= gridRows || col < 0 || col >= gridCols) {
      return false;
    }
    
    // 이미 점유된 셀 체크
    if (occupiedCells.has(`${row},${col}`)) {
      return false;
    }
  }
  return true;
}

/**
 * 아이템을 배치할 수 있는 다음 빈 위치 찾기 (좌상단부터 순회)
 */
function findNextAvailablePosition(
  volume: number,
  shapeIndex: number,
  occupiedCells: Set<string>,
  gridRows: number,
  gridCols: number
): { row: number; col: number } | null {
  const shape = SHAPES[volume]?.[shapeIndex] || SHAPES[1][0];
  
  for (let row = 0; row < gridRows; row++) {
    for (let col = 0; col < gridCols; col++) {
      if (canPlaceAtPosition(shape, row, col, occupiedCells, gridRows, gridCols)) {
        return { row, col };
      }
    }
  }
  return null;
}

/**
 * 아이템이 차지하는 셀들을 점유 상태로 기록
 */
function markOccupied(
  volume: number,
  shapeIndex: number,
  gridPosition: { row: number; col: number },
  occupiedCells: Set<string>
): void {
  const shape = SHAPES[volume]?.[shapeIndex] || SHAPES[1][0];
  
  for (const pos of shape) {
    const row = gridPosition.row + pos.row;
    const col = gridPosition.col + pos.col;
    occupiedCells.add(`${row},${col}`);
  }
}

interface GridCellProps {
  rowIndex: number;
  colIndex: number;
  cellData: { item: Item | null; isFirst: boolean };
  onDrop: (item: Item | NearbyItem, row: number, col: number) => void;
  onItemClick: (item: Item) => void;
  onDragStart?: (item: Item | NearbyItem) => void;
  onDragEnd?: () => void;
  onHover?: (row: number, col: number) => void;
  draggedItem?: (Item | NearbyItem) | null;
  hoverPosition?: { row: number; col: number } | null;
  isValidDrop?: boolean;
  isInDropZone?: boolean;
  isMobile?: boolean;
  gapSize: number;
}

// 셀 크기 상수 - 모바일 터치 UX 개선을 위해 크기 증가
const CELL_SIZE = {
  mobile: 36,  // 28px → 36px (터치 친화적)
  desktop: 48,
  gap: {
    mobile: 2,
    desktop: 4,
  }
};

const GridCell = memo(function GridCell({ rowIndex, colIndex, cellData, onDrop, onItemClick, onDragStart, onDragEnd, onHover, draggedItem, hoverPosition, isValidDrop, isInDropZone, isMobile = false, gapSize }: GridCellProps) {
  const { item, isFirst } = cellData;
  
  const [{ isOver, canDrop }, drop] = useDrop({
    accept: ['item', 'nearby'],
    drop: (draggedItem: Item | NearbyItem) => {
      onDrop(draggedItem, rowIndex, colIndex);
      if (onDragEnd) onDragEnd();
    },
    canDrop: () => !item,
    hover: () => {
      if (onHover) onHover(rowIndex, colIndex);
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  });

  const [{ isDragging }, drag] = useDrag({
    type: 'item',
    item: () => {
      if (!item || !isFirst) return null;
      if (onDragStart) onDragStart(item);
      return item;
    },
    canDrag: () => !!(item && isFirst),
    end: () => {
      if (onDragEnd) onDragEnd();
    },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const ref = (node: HTMLDivElement | null) => {
    if (isFirst) {
      drag(node);
    }
    drop(node);
  };

  const cellSize = isMobile ? CELL_SIZE.mobile : CELL_SIZE.desktop;
  // CSS Grid gap과 동기화된 아이템 위치 계산
  const totalCellSize = cellSize + gapSize;

  // 빈 셀
  if (!item) {
    const showGhost = draggedItem && hoverPosition &&
      hoverPosition.row === rowIndex && hoverPosition.col === colIndex;

    // 색상 결정
    let borderColor = 'var(--bg-light)';
    let bgColor = 'transparent';
    
    if (isOver && canDrop) {
      borderColor = 'var(--blue)';
      bgColor = 'rgba(59, 130, 246, 0.1)';
    } else if (showGhost) {
      borderColor = 'var(--blue)';
      bgColor = 'rgba(59, 130, 246, 0.05)';
    } else if (isInDropZone && isValidDrop) {
      borderColor = 'var(--success)';
      bgColor = 'rgba(34, 197, 94, 0.1)';
    } else if (isInDropZone && !isValidDrop) {
      borderColor = 'var(--danger)';
      bgColor = 'rgba(255, 71, 87, 0.1)';
    }

    return (
      <div
        ref={drop}
        style={{
          width: `${cellSize}px`,
          height: `${cellSize}px`,
          boxSizing: 'border-box',
          border: `1px solid ${borderColor}`,
          backgroundColor: bgColor,
        }}
        role="gridcell"
        aria-label={`셀 ${rowIndex + 1}행 ${colIndex + 1}열, 비어있음`}
      />
    );
  }

  // 아이템이 있는 셀
  if (!isFirst) {
    // 첫 칸이 아니면 완전 투명 (병합된 셀의 일부 - 그리드 라인 완전 제거)
    return <div style={{ width: `${cellSize}px`, height: `${cellSize}px`, boxSizing: 'border-box' }} className="bg-transparent border-0" />;
  }

  // 첫 칸 - 진짜 병합된 하나의 블록으로 렌더링 (아이템 내부 비텍스트 = 검정)
  const shapeIndex = item.shapeIndex || 0;
  const shape = SHAPES[item.volume]?.[shapeIndex] || SHAPES[1][0];

  return (
    <div style={{ width: `${cellSize}px`, height: `${cellSize}px` }} className="relative">
      {shape.map((pos, idx) => (
        <div
          key={idx}
          ref={idx === 0 ? ref : undefined}
          className="absolute cursor-move"
          title={item.name}
          style={{
            left: `${pos.col * totalCellSize}px`,
            top: `${pos.row * totalCellSize}px`,
            width: `${cellSize}px`,
            height: `${cellSize}px`,
            zIndex: 10,
            opacity: isDragging ? 0.4 : 1,
          }}
          onClick={(e) => {
            e.stopPropagation();
            if (item) onItemClick(item);
          }}
          role="button"
          aria-label={`${item.name}, 부피 ${item.volume}, 클릭하여 모양 변경`}
          tabIndex={idx === 0 ? 0 : -1}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              if (item) onItemClick(item);
            }
          }}
        >
          {/* 아이템 배경 */}
          <div
            className="absolute inset-0 rounded"
            style={{
              backgroundColor: item.color || 'var(--item)',
              border: `2px solid ${item.color || 'var(--item)'}`,
            }}
          />

          {/* 부피 표시 - 첫 번째 셀에만 */}
          {idx === 0 && (
            <div
              className="absolute font-bold pointer-events-none z-10"
              style={{ 
                top: '2px', 
                left: '4px',
                fontSize: isMobile ? '8px' : '9px',
                color: 'var(--text)',
              }}
            >
              {item.volume}
            </div>
          )}

          {/* 아이템 라벨 - 첫 번째 셀에만 (1칸/2칸 이상 동일 폰트 크기) */}
          {idx === 0 && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none p-1 z-10">
              <div
                className="font-bold text-center leading-tight"
                style={{
                  fontSize: isMobile ? '9px' : '11px',
                  color: 'white',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {item.name}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
});

interface TrashZoneProps {
  onDrop: (item: Item | NearbyItem) => void;
}

const TrashZone = memo(function TrashZone({ onDrop }: TrashZoneProps) {
  const [{ isOver, canDrop }, drop] = useDrop({
    accept: ['item', 'nearby', 'freeitem'],
    drop: (item: Item | NearbyItem) => {
      onDrop(item);
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  });

  return (
    <div
      ref={drop}
      className="p-4 border-2 border-dashed rounded-lg text-center transition-colors"
      style={{
        borderColor: isOver && canDrop ? 'var(--trash)' : 'var(--bg-light)',
        backgroundColor: isOver && canDrop ? 'rgba(153, 153, 153, 0.1)' : 'transparent',
      }}
      role="region"
      aria-label="아이템을 여기에 드롭하면 삭제됩니다"
    >
      <div 
        className="text-sm font-medium"
        style={{ color: isOver && canDrop ? 'var(--trash)' : 'var(--text-muted)' }}
      >
        이곳에 아이템을 끌어다 버릴 수 있어요
      </div>
    </div>
  );
});

interface NearbyZoneProps {
  onDrop: (item: Item) => void;
  children: React.ReactNode;
  /** 가방·버리기 사이 공간을 채우도록 높이 확장 */
  fillHeight?: boolean;
}

const NearbyZone = memo(function NearbyZone({ onDrop, children, fillHeight }: NearbyZoneProps) {
  const [{ isOver, canDrop }, drop] = useDrop({
    accept: ['item', 'freeitem'],
    drop: (item: Item) => {
      onDrop(item);
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  });

  return (
    <div
      ref={drop}
      className={`border rounded-lg p-4 ${fillHeight ? 'flex-1 min-h-0 flex flex-col' : 'min-h-[120px]'}`}
      style={{
        backgroundColor: 'var(--bg)',
        borderColor: isOver && canDrop ? 'var(--danger)' : 'rgba(255, 71, 87, 0.3)',
        borderWidth: isOver && canDrop ? '2px' : '1px',
      }}
      role="region"
      aria-label="주변 아이템 영역"
    >
      {fillHeight ? <div className="overflow-auto flex-1 min-h-0 pt-2">{children}</div> : children}
    </div>
  );
});

interface MiscSpaceZoneProps {
  onDrop: (item: NearbyItem) => void;
  children: React.ReactNode;
  /** 가방·버리기 사이 공간을 채우도록 높이 확장 */
  fillHeight?: boolean;
}

const MiscSpaceZone = memo(function MiscSpaceZone({ onDrop, children, fillHeight }: MiscSpaceZoneProps) {
  const [{ isOver, canDrop }, drop] = useDrop({
    accept: ['nearby'],
    drop: (item: NearbyItem) => {
      onDrop(item);
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  });

  return (
    <div
      ref={drop}
      className={`border rounded-lg p-4 ${fillHeight ? 'flex-1 min-h-0 flex flex-col' : 'min-h-[120px]'}`}
      style={{
        backgroundColor: 'var(--bg)',
        borderColor: isOver && canDrop ? 'var(--misc)' : 'rgba(249, 115, 22, 0.3)',
        borderWidth: isOver && canDrop ? '2px' : '1px',
      }}
      role="region"
      aria-label="여유공간 영역 (무게 없는 아이템)"
    >
      {fillHeight ? <div className="overflow-auto flex-1 min-h-0 pt-2">{children}</div> : children}
    </div>
  );
});

interface FreeItemChipProps {
  item: Item;
}

const FreeItemChip = memo(function FreeItemChip({ item }: FreeItemChipProps) {
  const [{ isDragging }, drag] = useDrag({
    type: 'freeitem',
    item: item,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const getIcon = (iconName?: string) => {
    switch (iconName) {
      case 'coins':
        return <Coins className="w-3 h-3" />;
      case 'file':
        return <FileText className="w-3 h-3" />;
      case 'paperclip':
        return <Paperclip className="w-3 h-3" />;
      default:
        return null;
    }
  };

  return (
    <div
      ref={drag}
      className="inline-flex items-center gap-2 px-2.5 py-1.5 rounded-lg cursor-move text-sm font-medium"
      style={{
        backgroundColor: 'var(--bg-light)',
        border: '1px solid var(--misc)',
        color: 'var(--text)',
        opacity: isDragging ? 0.3 : 1,
      }}
      role="button"
      aria-label={`${item.name}, 수량 ${item.count}개, 드래그하여 이동`}
      tabIndex={0}
    >
      {getIcon(item.icon)}
      <span>{item.name}</span>
      <span 
        className="text-xs font-bold px-1.5 py-0.5 rounded"
        style={{ backgroundColor: 'rgba(249, 115, 22, 0.2)', color: 'var(--misc)' }}
      >
        ×{item.count}
      </span>
    </div>
  );
});

interface NearbyItemChipProps {
  item: NearbyItem;
  count?: number;
}

const NearbyItemChip = memo(function NearbyItemChip({ item, count = 1 }: NearbyItemChipProps) {
  const [{ isDragging }, drag] = useDrag({
    type: 'nearby',
    item: item,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  return (
    <div
      ref={drag}
      className="inline-flex items-center gap-2 px-2.5 py-1.5 rounded-lg cursor-move text-sm font-medium relative"
      style={{
        backgroundColor: 'var(--bg-light)',
        border: '1px solid var(--danger)',
        color: 'var(--text)',
        opacity: isDragging ? 0.3 : 1,
      }}
      role="button"
      aria-label={`${item.name}, 부피 ${item.volume}${count > 1 ? `, ${count}개` : ''}, 드래그하여 가방에 넣기`}
      tabIndex={0}
    >
      {count > 1 && (
        <span 
          className="absolute -top-2 -right-2 px-1.5 py-0.5 rounded-full text-[10px] font-bold"
          style={{ backgroundColor: 'var(--danger)', color: 'white' }}
        >
          ×{count}
        </span>
      )}
      <span>{item.name}</span>
      <span 
        className="px-1.5 py-0.5 rounded text-xs font-bold"
        style={{ backgroundColor: 'rgba(255, 71, 87, 0.2)', color: 'var(--danger)' }}
      >
        {item.volume}
      </span>
    </div>
  );
});

export interface InventoryState {
  items: Item[];
  nearbyItems: NearbyItem[];
  freeItems: Item[];
}

interface BagTabProps {
  gridSize: number;
  timeRemaining: number;
  formatTime: (time: number) => string;
  /** 타이머가 API가 아닌 데모용일 때 표시할 라벨 (예: "데모") */
  timerLabel?: string;
  characterData?: ApiCharacter;
  onInventoryChange?: (state: InventoryState) => void;
  onRefresh?: () => void;
}

function BagTabContent({ gridSize, timeRemaining, formatTime, timerLabel, characterData, onInventoryChange, onRefresh }: BagTabProps) {
  const gridCols = 10;
  const gridRows = Math.ceil(gridSize / gridCols);

  // Initialize items from API data
  const getInitialItems = useCallback((): Item[] => {
    if (characterData?.bag_items && characterData.bag_items.length > 0) {
      // bag_layout이 있으면 저장된 배치 정보 적용
      const transformed = apiBagToGridItems(characterData.bag_items, characterData.bag_layout || []);
      
      // 점유 셀 추적용 Set
      const occupiedCells = new Set<string>();
      
      // 먼저 이미 배치된 아이템들의 점유 셀 기록
      transformed.forEach(item => {
        if (item.gridPosition && item.volume > 0) {
          markOccupied(item.volume, item.shapeIndex || 0, item.gridPosition, occupiedCells);
        }
      });
      
      // 아이템 변환 및 자동 배치 적용
      return transformed.map(item => {
        let gridPosition = item.gridPosition;
        let shapeIndex = item.shapeIndex || 0;
        
        // gridPosition이 없고 부피가 있는 아이템은 자동 배치
        if (!gridPosition && item.volume > 0) {
          // 모든 가능한 모양에 대해 배치 시도
          const shapes = SHAPES[item.volume] || SHAPES[1];
          for (let si = 0; si < shapes.length; si++) {
            const position = findNextAvailablePosition(item.volume, si, occupiedCells, gridRows, gridCols);
            if (position) {
              gridPosition = position;
              shapeIndex = si;
              // 점유 셀 기록
              markOccupied(item.volume, shapeIndex, gridPosition, occupiedCells);
              break;
            }
          }
        }
        
        return {
          id: item.id,
          name: item.name,
          count: item.count,
          volume: item.volume,
          gridPosition,
          shapeIndex,
          color: generateRandomItemColor(),
        };
      });
    }
    // No items - return empty array
    return [];
  }, [characterData, gridRows, gridCols]);

  const getInitialFreeItems = useCallback((): Item[] => {
    if (characterData?.misc_items && characterData.misc_items.length > 0) {
      return characterData.misc_items.map((item, index) => ({
        id: `f-${Date.now()}-${index}`,
        name: item.name,
        count: item.quantity,
        volume: 0,
      }));
    }
    // No items - return empty array
    return [];
  }, [characterData]);

  const getInitialNearbyItems = useCallback((): NearbyItem[] => {
    if (characterData?.nearby_items && characterData.nearby_items.length > 0) {
      const items: NearbyItem[] = [];
      characterData.nearby_items.forEach((item, groupIndex) => {
        // 각 아이템 인스턴스를 개별적으로 생성하되 count: 1을 명시적으로 설정
        for (let i = 0; i < item.quantity; i++) {
          items.push({
            id: `n-${Date.now()}-${groupIndex}-${i}`,
            name: item.name,
            volume: item.volume,
            count: 1,  // 명시적으로 count 설정 (수량 합산 시 필요)
          });
        }
      });
      return items;
    }
    // No items - return empty array
    return [];
  }, [characterData]);

  const [items, setItems] = useState<Item[]>(getInitialItems);
  const [freeItems, setFreeItems] = useState<Item[]>(getInitialFreeItems);
  const [nearbyItems, setNearbyItems] = useState<NearbyItem[]>(getInitialNearbyItems);

  // Re-initialize when characterData changes
  useEffect(() => {
    setItems(getInitialItems());
    setFreeItems(getInitialFreeItems());
    setNearbyItems(getInitialNearbyItems());
  }, [characterData, getInitialItems, getInitialFreeItems, getInitialNearbyItems]);

  // Notify parent when full inventory changes (for sync - bag, nearby, misc)
  useEffect(() => {
    if (onInventoryChange) {
      onInventoryChange({
        items,
        nearbyItems,
        freeItems,
      });
    }
  }, [items, nearbyItems, freeItems, onInventoryChange]);

  const [draggedItem, setDraggedItem] = useState<(Item | NearbyItem) | null>(null);
  const [hoverPosition, setHoverPosition] = useState<{ row: number; col: number } | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  
  // 수량 선택 다이얼로그 상태 (QuantityDialog 컴포넌트와 통일)
  const [quantityDialog, setQuantityDialog] = useState<QuantityDialogState>({
    isOpen: false,
    item: null,
    maxQuantity: 1,
    selectedQuantity: 1,
    action: null,
  });

  // 화면 크기 감지
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // 그리드 셀 데이터 생성 (먼저 생성해야 다른 계산에서 사용 가능)
  const gridCells: Array<Array<{ item: Item | null; isFirst: boolean }>> = Array(gridRows)
    .fill(null)
    .map(() => Array(gridCols).fill(null).map(() => ({ item: null, isFirst: false })));

  items.forEach((item) => {
    if (item.gridPosition) {
      const shapeIndex = item.shapeIndex || 0;
      const shape = SHAPES[item.volume]?.[shapeIndex] || SHAPES[1][0];
      
      shape.forEach((pos, idx) => {
        const row = item.gridPosition!.row + pos.row;
        const col = item.gridPosition!.col + pos.col;
        
        if (row >= 0 && row < gridRows && col >= 0 && col < gridCols) {
          gridCells[row][col] = {
            item: item,
            isFirst: idx === 0,
          };
        }
      });
    }
  });

  // 드래그된 아이템이 차지할 셀 계산
  const getDropZoneCells = (): Set<string> => {
    if (!draggedItem || !hoverPosition) return new Set();
    
    const volume = 'volume' in draggedItem ? draggedItem.volume : 0;
    const shapeIndex = 'shapeIndex' in draggedItem ? (draggedItem.shapeIndex || 0) : 0;
    const shape = SHAPES[volume]?.[shapeIndex] || SHAPES[1][0];
    
    const cells = new Set<string>();
    shape.forEach((pos) => {
      const row = hoverPosition.row + pos.row;
      const col = hoverPosition.col + pos.col;
      cells.add(`${row}-${col}`);
    });
    
    return cells;
  };

  const dropZoneCells = getDropZoneCells();
  
  // 배치 가능 여부 체크
  const isValidDropPosition = hoverPosition && draggedItem ? (() => {
    const volume = 'volume' in draggedItem ? draggedItem.volume : 0;
    const shapeIndex = 'shapeIndex' in draggedItem ? (draggedItem.shapeIndex || 0) : 0;
    const shape = SHAPES[volume]?.[shapeIndex] || SHAPES[1][0];
    
    // 드래그 중인 아이템의 ID (자기 자신과의 충돌은 무시)
    const draggedItemId = 'id' in draggedItem ? draggedItem.id : null;
    
    for (const pos of shape) {
      const row = hoverPosition.row + pos.row;
      const col = hoverPosition.col + pos.col;
      
      // 그리드 범위 체크
      if (row < 0 || row >= gridRows || col < 0 || col >= gridCols) return false;
      
      const cell = gridCells[row]?.[col];
      // 다른 아이템이 있는 경우만 false (자기 자신은 OK)
      if (cell && cell.item && cell.item.id !== draggedItemId) {
        return false;
      }
    }
    return true;
  })() : true;

  const canPlaceItem = (item: Item, startRow: number, startCol: number, shapeIndex: number): boolean => {
    if (startRow < 0 || startCol < 0) return false;
    
    const shape = SHAPES[item.volume]?.[shapeIndex] || SHAPES[1][0];
    
    for (const pos of shape) {
      const row = startRow + pos.row;
      const col = startCol + pos.col;
      
      // 그리드 범위 체크
      if (row < 0 || row >= gridRows || col < 0 || col >= gridCols) return false;
      
      const cell = gridCells[row][col];
      // 다른 아이템이 있는 경우만 false (자기 자신은 OK)
      if (cell.item && cell.item.id !== item.id) {
        return false;
      }
    }
    return true;
  };

  const handleGridDrop = (draggedItem: Item | NearbyItem, row: number, col: number) => {
    // 부피 0인 아이템은 가방에 들어갈 수 없음
    if (draggedItem.volume === 0) {
      return;
    }
    
    if ('gridPosition' in draggedItem) {
      // 기존 아이템 이동
      const shapeIndex = draggedItem.shapeIndex || 0;
      if (canPlaceItem(draggedItem, row, col, shapeIndex)) {
        setItems((prev) =>
          prev.map((i) =>
            i.id === draggedItem.id ? { ...i, gridPosition: { row, col } } : i
          )
        );
      }
    } else {
      // 주변 아이템을 가방 또는 misc space에 추가
      // 그룹화된 아이템이라도 한 번에 1개씩만 이동
      const isGrouped = 'ids' in draggedItem && draggedItem.ids && draggedItem.ids.length > 0;
      // 항상 1개만 이동
      const idToRemove = isGrouped ? draggedItem.ids![0] : draggedItem.id;
      
      if (draggedItem.volume === 0) {
        // 부피 0 아이템은 misc space로
        const newItem: Item = {
          id: `f-${Date.now()}`,
          name: draggedItem.name,
          count: 1,  // 항상 1개만 이동
          volume: 0,
          icon: draggedItem.icon,
        };
        setFreeItems((prev) => {
          const existing = prev.find((i) => i.name === newItem.name && i.volume === 0);
          if (existing) {
            return prev.map((i) =>
              i.id === existing.id ? { ...i, count: i.count + 1 } : i
            );
          }
          return [...prev, newItem];
        });
        // 1개만 제거
        setNearbyItems((prev) => prev.filter((i) => i.id !== idToRemove));
      } else {
        // 일반 아이템은 가방으로
        const newItem: Item = {
          id: `i-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
          name: draggedItem.name,
          count: 1,  // 항상 1개만 이동
          volume: draggedItem.volume,
          gridPosition: { row, col },
          shapeIndex: 0,
          icon: draggedItem.icon,
          color: generateRandomItemColor(),
        };
        
        if (canPlaceItem(newItem, row, col, 0)) {
          setItems((prev) => [...prev, newItem]);
          // 1개만 제거
          setNearbyItems((prev) => prev.filter((i) => i.id !== idToRemove));
        }
      }
    }
    setDraggedItem(null);
    setHoverPosition(null);
  };

  const handleItemClick = (item: Item) => {
    const shapeCount = SHAPES[item.volume]?.length || 1;
    if (shapeCount <= 1) return; // 회전 불가

    const currentIndex = item.shapeIndex || 0;

    // 다음 맞는 모양 찾기 (현재 위치에 배치 가능한 모양으로 순환)
    for (let i = 1; i < shapeCount; i++) {
      const nextIndex = (currentIndex + i) % shapeCount;
      if (item.gridPosition && canPlaceItem(item, item.gridPosition.row, item.gridPosition.col, nextIndex)) {
        setItems((prev) =>
          prev.map((it) =>
            it.id === item.id ? { ...it, shapeIndex: nextIndex } : it
          )
        );
        return;
      }
    }
  };

  const handleTrashDrop = (draggedItem: Item | NearbyItem) => {
    if ('gridPosition' in draggedItem) {
      setItems((prev) => prev.filter((i) => i.id !== draggedItem.id));
    } else if ('count' in draggedItem && draggedItem.volume === 0) {
      // 여유공간 아이템
      setFreeItems((prev) => prev.filter((i) => i.id !== draggedItem.id));
    } else {
      // 주변 아이템
      setNearbyItems((prev) => prev.filter((i) => i.id !== draggedItem.id));
    }
  };

  const handleNearbyDrop = (draggedItem: Item) => {
    if ('gridPosition' in draggedItem) {
      // 가방 아이템을 주변으로 - count만큼 개별 NearbyItem 생성
      const itemCount = draggedItem.count || 1;
      const newNearbyItems: NearbyItem[] = [];
      for (let i = 0; i < itemCount; i++) {
        newNearbyItems.push({
          id: `n-${Date.now()}-${i}`,
          name: draggedItem.name,
          volume: draggedItem.volume,
          icon: draggedItem.icon,
          count: 1,  // 개별 아이템은 count: 1
        });
      }
      setNearbyItems((prev) => [...prev, ...newNearbyItems]);
      setItems((prev) => prev.filter((i) => i.id !== draggedItem.id));
    } else if ('count' in draggedItem && draggedItem.volume === 0) {
      // 여유공간 아이템을 주변으로
      if (draggedItem.count > 1) {
        // 수량이 2개 이상이면 다이얼로그 표시
        setQuantityDialog({
          isOpen: true,
          item: draggedItem,
          maxQuantity: draggedItem.count,
          selectedQuantity: 1,
          action: 'toNearby',
        });
      } else {
        // 수량이 1개면 바로 이동
        const nearbyItem: NearbyItem = {
          id: `n-${Date.now()}`,
          name: draggedItem.name,
          volume: 0,
          icon: draggedItem.icon,
          count: 1,  // 명시적으로 count 설정
        };
        setNearbyItems((prev) => [...prev, nearbyItem]);
        setFreeItems((prev) => prev.filter((i) => i.id !== draggedItem.id));
      }
    }
  };

  // Misc Space로 드롭
  const handleMiscDrop = (draggedItem: NearbyItem) => {
    // 부피 0이 아닌 아이템은 Misc Space에 들어갈 수 없음
    if (draggedItem.volume !== 0) {
      return;
    }

    // 그룹화 여부와 관계없이 항상 1개씩만 이동
    const isGrouped = 'ids' in draggedItem && draggedItem.ids && draggedItem.ids.length > 0;
    const idToRemove = isGrouped ? draggedItem.ids![0] : draggedItem.id;
    
    const newItem: Item = {
      id: `f-${Date.now()}`,
      name: draggedItem.name,
      count: 1,
      volume: 0,
      icon: draggedItem.icon,
    };
    setFreeItems((prev) => {
      const existing = prev.find((i) => i.name === newItem.name && i.volume === 0);
      if (existing) {
        return prev.map((i) =>
          i.id === existing.id ? { ...i, count: i.count + 1 } : i
        );
      }
      return [...prev, newItem];
    });
    
    // 1개만 제거
    setNearbyItems((prev) => prev.filter((i) => i.id !== idToRemove));
  };

  // 수량 선택 다이얼로그 확인
  const handleQuantityConfirm = () => {
    if (!quantityDialog.item || !quantityDialog.action) return;

    const { item, selectedQuantity, action } = quantityDialog;

    if (action === 'toNearby') {
      // Misc Space에서 Nearby로 이동
      const newNearbyItems: NearbyItem[] = [];
      for (let i = 0; i < selectedQuantity; i++) {
        newNearbyItems.push({
          id: `n-${Date.now()}-${i}`,
          name: item.name,
          volume: 0,
          icon: item.icon,
          count: 1,  // 명시적으로 count 설정
        });
      }
      setNearbyItems((prev) => [...prev, ...newNearbyItems]);
      
      setFreeItems((prev) =>
        prev.map((i) =>
          i.id === item.id
            ? { ...i, count: i.count - selectedQuantity }
            : i
        ).filter((i) => i.count > 0)
      );
    } else if (action === 'toMisc') {
      // Nearby에서 Misc Space로 이동
      const newItem: Item = {
        id: `f-${Date.now()}`,
        name: item.name,
        count: selectedQuantity,
        volume: 0,
        icon: item.icon,
      };
      setFreeItems((prev) => {
        const existing = prev.find((i) => i.name === newItem.name && i.volume === 0);
        if (existing) {
          return prev.map((i) =>
            i.id === existing.id ? { ...i, count: i.count + selectedQuantity } : i
          );
        }
        return [...prev, newItem];
      });
      
      // Nearby에서 해당 아이템 제거
      if ('ids' in item && item.ids) {
        // 그룹화된 아이템에서 선택한 수량 제거
        const removeIds = item.ids.slice(0, selectedQuantity);
        setNearbyItems((prev) => prev.filter((i) => !removeIds.includes(i.id)));
      } else {
        setNearbyItems((prev) => prev.filter((i) => i.id !== item.id));
      }
    }

    // 다이얼로그 닫기
    setQuantityDialog({
      isOpen: false,
      item: null,
      maxQuantity: 1,
      selectedQuantity: 1,
      action: null,
    });
  };

  const usedCapacity = items
    .filter((item) => item.gridPosition !== undefined)
    .reduce((sum, item) => sum + item.volume, 0);
  const maxCapacity = gridSize;
  
  // 빈 공간 부족 경고
  const isCriticalCapacity = usedCapacity / maxCapacity > 0.9;

  // Nearby 아이템 수량 합산
  const groupedNearbyItems = nearbyItems.reduce((acc, item) => {
    const key = `${item.name}-${item.volume}`;
    if (!acc[key]) {
      acc[key] = { ...item, count: 0, ids: [] };
    }
    acc[key].count += 1;
    acc[key].ids.push(item.id);
    return acc;
  }, {} as Record<string, NearbyItem & { count: number; ids: string[] }>);
  
  const nearbyItemsGrouped = Object.values(groupedNearbyItems);

  const cellSize = isMobile ? CELL_SIZE.mobile : CELL_SIZE.desktop;
  const gapSize = isMobile ? CELL_SIZE.gap.mobile : CELL_SIZE.gap.desktop;

  const closeQuantityDialog = () => {
    setQuantityDialog({ isOpen: false, item: null, maxQuantity: 1, selectedQuantity: 1, action: null });
  };

  return (
    <div className="flex flex-col gap-4 md:gap-5 h-full min-h-0 relative">
      {/* 배경 이미지 레이어 */}
      <div 
        className="absolute inset-0 pointer-events-none z-0"
        style={{
          backgroundImage: 'url(/image/bg.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          opacity: 0.15,
        }}
        aria-hidden="true"
      />
      <QuantityDialog
        state={quantityDialog}
        onClose={closeQuantityDialog}
        onQuantityChange={(q) => setQuantityDialog((prev) => ({ ...prev, selectedQuantity: q }))}
        onConfirm={handleQuantityConfirm}
      />

      {/* 상단: 가방 영역 */}
      <section className="space-y-3 shrink-0 relative z-10" aria-labelledby="inventory-heading">
        {/* 캐릭터 기본 정보 */}
        <div 
          className="rounded-lg p-3 md:p-4"
          style={{ backgroundColor: 'var(--bg-mid)', border: '1px solid var(--bg-light)' }}
        >
          <div className="flex items-center justify-between gap-4">
            {/* 왼쪽: 캐릭터 이름 */}
            <h3 className="text-base md:text-lg font-bold tracking-wide" style={{ color: 'var(--blue)' }}>
              {characterData?.name ?? '-'}
            </h3>
            
            {/* 오른쪽: 스탯 정보 */}
            <div className="flex flex-wrap items-center justify-end gap-x-4 gap-y-2 md:gap-x-5">
              <div className="flex items-center gap-1.5">
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>체력</span>
                <span className="text-sm font-bold" style={{ color: 'var(--text)' }}>{characterData?.health ?? '-'}</span>
              </div>
              
              <div className="flex items-center gap-1.5">
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>근력</span>
                <span className="text-sm font-bold" style={{ color: 'var(--text)' }}>{characterData?.strength ?? '-'}</span>
              </div>
              
              <div className="flex items-center gap-1.5">
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>행운</span>
                <span className="text-sm font-bold" style={{ color: 'var(--text)' }}>{characterData?.luck ?? '-'}</span>
              </div>
              
              <div className="flex items-center gap-1.5">
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>HP</span>
                <span className="text-sm font-bold" style={{ color: 'var(--text)' }}>{characterData?.hp ?? '-'}</span>
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>/{characterData?.max_hp ?? '-'}</span>
              </div>
              
              <div className="flex items-center gap-1.5">
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>가방</span>
                <span 
                  className="text-sm font-bold"
                  style={{ 
                    color: usedCapacity / maxCapacity > 0.8 ? 'var(--danger)' 
                      : usedCapacity / maxCapacity > 0.6 ? 'var(--warn)' 
                      : 'var(--text)' 
                  }}
                >
                  {usedCapacity}
                </span>
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>/{maxCapacity}</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* 그리드 컨테이너 */}
        <div 
          className="rounded-lg p-3 md:p-4 overflow-x-auto"
          style={{ backgroundColor: 'var(--bg-mid)', border: '1px solid var(--bg-light)' }}
        >
          <div 
            className="mx-auto relative" 
            style={{ 
              display: 'grid',
              gridTemplateColumns: `repeat(${gridCols}, ${cellSize}px)`,
              gridTemplateRows: `repeat(${gridRows}, ${cellSize}px)`,
              gap: `${gapSize}px`,
              width: 'fit-content',
            }}
            role="grid"
            aria-label="인벤토리 그리드"
          >
            {gridCells.flat().map((cellData, idx) => {
              const rowIndex = Math.floor(idx / gridCols);
              const colIndex = idx % gridCols;
              const cellKey = `${rowIndex}-${colIndex}`;
              const isInDropZone = dropZoneCells.has(cellKey);
              
              return (
                <GridCell
                  key={cellKey}
                  rowIndex={rowIndex}
                  colIndex={colIndex}
                  cellData={cellData}
                  onDrop={handleGridDrop}
                  onItemClick={handleItemClick}
                  onDragStart={setDraggedItem}
                  onDragEnd={() => {
                    setDraggedItem(null);
                    setHoverPosition(null);
                  }}
                  onHover={(row, col) => setHoverPosition({ row, col })}
                  draggedItem={draggedItem}
                  hoverPosition={hoverPosition}
                  isValidDrop={isValidDropPosition}
                  isInDropZone={isInDropZone}
                  isMobile={isMobile}
                  gapSize={gapSize}
                />
              );
            })}
            
            {/* 그리드 밖으로 나가는 경우 빨간색 오버레이 표시 */}
            {draggedItem && hoverPosition && !isValidDropPosition && (() => {
              const volume = 'volume' in draggedItem ? draggedItem.volume : 0;
              const shapeIndex = 'shapeIndex' in draggedItem ? (draggedItem.shapeIndex || 0) : 0;
              const shape = SHAPES[volume]?.[shapeIndex] || SHAPES[1][0];
              
              const totalCellSize = cellSize + gapSize;
              
              const minCol = Math.min(...shape.map(p => p.col));
              const maxCol = Math.max(...shape.map(p => p.col));
              const minRow = Math.min(...shape.map(p => p.row));
              const maxRow = Math.max(...shape.map(p => p.row));

              const blockWidth = (maxCol - minCol + 1) * cellSize + (maxCol - minCol) * gapSize;
              const blockHeight = (maxRow - minRow + 1) * cellSize + (maxRow - minRow) * gapSize;

              const left = (hoverPosition.col + minCol) * totalCellSize;
              const top = (hoverPosition.row + minRow) * totalCellSize;
              
              return (
                <div
                  className="absolute pointer-events-none z-20"
                  style={{
                    left: `${left}px`,
                    top: `${top}px`,
                    width: `${blockWidth}px`,
                    height: `${blockHeight}px`,
                  }}
                  aria-hidden="true"
                >
                  <div 
                    className="absolute inset-0 rounded border-2"
                    style={{ borderColor: 'var(--danger)', backgroundColor: 'rgba(255, 71, 87, 0.1)' }}
                  />
                </div>
              );
            })()}
          </div>
        </div>
      </section>

      {/* 중간: 여유공간 + 주변 (가방과 버리기 사이 공간 채움) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 min-h-0 overflow-hidden relative z-10">
        {/* 여유공간 */}
        <section className="flex flex-col min-h-0 space-y-2" aria-labelledby="misc-heading">
          <div className="flex items-center justify-between shrink-0">
            <h3 id="misc-heading" className="text-xs font-bold tracking-wider uppercase" style={{ color: 'var(--misc)' }}>
              여유 공간
            </h3>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{ backgroundColor: 'var(--bg-light)', color: 'var(--text-muted)' }}>
              WEIGHTLESS
            </span>
          </div>
          <MiscSpaceZone onDrop={handleMiscDrop} fillHeight>
            {freeItems.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {freeItems.map((item) => (
                  <FreeItemChip key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center flex-1 min-h-[80px] text-xs gap-1" style={{ color: 'var(--text-muted)', opacity: 0.8 }}>
                <span>무게 없는 아이템 없음</span>
                <span className="opacity-70">주변에서 끌어다 놓으면 여기로 옮겨져요</span>
              </div>
            )}
          </MiscSpaceZone>
        </section>

        {/* 주변 아이템 */}
        <section className="flex flex-col min-h-0 space-y-2" aria-labelledby="nearby-heading">
          <div className="flex items-center justify-between flex-wrap gap-2 shrink-0">
            <h3 id="nearby-heading" className="text-xs font-bold tracking-wider uppercase" style={{ color: 'var(--danger)' }}>
              주변
            </h3>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded" style={{ backgroundColor: 'rgba(255, 71, 87, 0.15)', border: '1px solid var(--danger)' }}>
              <AlertCircle className="w-3 h-3" style={{ color: 'var(--danger)' }} />
              <span className="text-[10px] font-bold" style={{ color: 'var(--danger)' }}>
                {timerLabel ? `${timerLabel} · ` : ''}{formatTime(timeRemaining)} 후 자동 삭제
              </span>
            </div>
          </div>
          <NearbyZone onDrop={handleNearbyDrop} fillHeight>
            {nearbyItemsGrouped.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {nearbyItemsGrouped.map((item) => (
                  <NearbyItemChip key={item.ids[0]} item={item} count={item.count} />
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center flex-1 min-h-[80px] text-xs gap-1" style={{ color: 'var(--text-muted)', opacity: 0.8 }}>
                <span>주변 아이템 없음</span>
                <span className="opacity-70">가방에서 끌어다 놓으면 여기로 옮겨져요</span>
              </div>
            )}
          </NearbyZone>
        </section>
      </div>

      {/* 하단: 버리기 영역 (sticky: 드래그 중에도 항상 보이도록) */}
      <section
        className="shrink-0 relative z-20 sticky bottom-0 pb-1"
        style={{ backgroundColor: 'var(--bg)' }}
        aria-label="버리기"
      >
        <TrashZone onDrop={handleTrashDrop} />
      </section>
    </div>
  );
}

export default function BagTab({ gridSize, timeRemaining, formatTime, timerLabel, characterData, onInventoryChange, onRefresh }: BagTabProps) {
  return (
    <DndProvider backend={HTML5Backend}>
      <BagTabContent
        gridSize={gridSize}
        timeRemaining={timeRemaining}
        formatTime={formatTime}
        timerLabel={timerLabel}
        characterData={characterData}
        onInventoryChange={onInventoryChange}
        onRefresh={onRefresh}
      />
    </DndProvider>
  );
}