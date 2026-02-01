import { useState, useEffect } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Coins, FileText, Paperclip, Clock, AlertCircle, X } from 'lucide-react';

interface Item {
  id: string;
  name: string;
  count: number;
  volume: number;
  gridPosition?: { row: number; col: number };
  shapeIndex?: number; // 현재 선택된 모양 인덱스
  icon?: string;
  type?: 'consumable' | 'equipment'; // 아이템 타입
}

interface NearbyItem {
  id: string;
  name: string;
  volume: number;
  icon?: string;
  count?: number; // 그룹화된 수량 정보 추가
  ids?: string[]; // 그룹화된 아이템 ID들
}

// 부피별 가능한 모양들 (상대 좌표)
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
}

function GridCell({ rowIndex, colIndex, cellData, onDrop, onItemClick, onDragStart, onDragEnd, onHover, draggedItem, hoverPosition, isValidDrop, isInDropZone, isMobile = false }: GridCellProps) {
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
    item: item && isFirst ? item : null,
    canDrag: () => !!(item && isFirst),
    collect: (monitor) => {
      const isDragging = monitor.isDragging();
      if (isDragging && item && isFirst && onDragStart) {
        onDragStart(item);
      }
      return {
        isDragging,
      };
    },
  });

  const ref = (node: HTMLDivElement | null) => {
    if (isFirst) {
      drag(node);
    }
    drop(node);
  };

  // 5칸 단위 굵은 선 체크
  const isThickBorderRight = (colIndex + 1) % 5 === 0;
  const isThickBorderBottom = (rowIndex + 1) % 5 === 0;

  // 빈 셀 - 더 밝은 그리드 라인으로 가시성 향상
  if (!item) {
    // 고스트 프리뷰 표시 여부 체크
    const showGhost = draggedItem && hoverPosition && 
      hoverPosition.row === rowIndex && hoverPosition.col === colIndex;
    
    return (
      <div
        ref={drop}
        className={`w-7 h-7 md:w-12 md:h-12 transition-all ${
          isOver && canDrop
            ? 'bg-[#00F3FF]/15 border-[#00F3FF]/60 shadow-[inset_0_0_15px_rgba(0,243,255,0.3)]'
            : showGhost
            ? 'bg-[#00F3FF]/10 border-[#00F3FF]/40'
            : isInDropZone && isValidDrop
            ? 'bg-[#00FF88]/20 border-[#00FF88]/60'
            : isInDropZone && !isValidDrop
            ? 'bg-[#FF4757]/20 border-[#FF4757]/60'
            : 'bg-transparent hover:border-[#00F3FF]/40'
        }`}
        style={{
          borderWidth: '1px',
          borderRightWidth: isThickBorderRight ? '2px' : '1px',
          borderBottomWidth: isThickBorderBottom ? '2px' : '1px',
          borderColor: isOver && canDrop 
            ? 'rgba(0, 243, 255, 0.6)' 
            : showGhost 
            ? 'rgba(0, 243, 255, 0.4)'
            : isInDropZone && isValidDrop
            ? 'rgba(0, 255, 136, 0.6)'
            : isInDropZone && !isValidDrop
            ? 'rgba(255, 71, 87, 0.6)'
            : 'rgba(42, 47, 58, 0.8)',
        }}
      />
    );
  }

  // 아이템이 있는 셀
  if (!isFirst) {
    // 첫 칸이 아니면 완전 투명 (병합된 셀의 일부 - 그리드 라인 완전 제거)
    return <div className="w-7 h-7 md:w-12 md:h-12 bg-transparent border-0" />;
  }

  // 첫 칸 - 진짜 병합된 하나의 블록으로 렌더링
  const shapeIndex = item.shapeIndex || 0;
  const shape = SHAPES[item.volume]?.[shapeIndex] || SHAPES[1][0];

  // 타입별 색상 설정
  const itemColors = item.type === 'consumable' 
    ? { border: '#00F3FF', glow: 'rgba(0, 243, 255, 0.4)', bg: 'rgba(0, 243, 255, 0.15)' }
    : item.type === 'equipment'
    ? { border: '#FFB020', glow: 'rgba(255, 176, 32, 0.4)', bg: 'rgba(255, 176, 32, 0.15)' }
    : { border: '#BF5AF2', glow: 'rgba(191, 90, 242, 0.4)', bg: 'rgba(191, 90, 242, 0.15)' };

  return (
    <div className="w-7 h-7 md:w-12 md:h-12 relative">
      {/* 각 셀을 절대 위치로 독립 렌더링 - 경계 박스 없이 */}
      {shape.map((pos, idx) => {
        // 모바일과 데스크톱에서 다른 크기 사용
        const cellSize = isMobile ? 28 : 48;
        const gapSize = isMobile ? 1 : 4;
        const totalCellSize = cellSize + gapSize;
        
        return (
          <div
            key={idx}
            ref={idx === 0 ? ref : undefined}
            className={`absolute cursor-move transition-all group ${
              isDragging ? 'opacity-40' : 'opacity-100'
            }`}
            style={{
              left: `${pos.col * totalCellSize}px`,
              top: `${pos.row * totalCellSize}px`,
              width: `${cellSize}px`,
              height: `${cellSize}px`,
              zIndex: 10,
            }}
            onClick={(e) => {
              e.stopPropagation();
              if (item) onItemClick(item);
            }}
          >
            <div 
              className="absolute inset-0 rounded-md md:rounded-lg overflow-hidden transition-all duration-200 group-hover:scale-105"
              style={{
                background: `linear-gradient(135deg, ${itemColors.bg} 0%, ${itemColors.bg.replace('0.15', '0.25')} 100%)`,
                backdropFilter: 'blur(10px)',
                border: `1.5px solid ${itemColors.border}`,
                boxShadow: `0 0 12px ${itemColors.glow}, inset 0 0 12px ${itemColors.glow.replace('0.4', '0.1')}`,
              }}
            >
              {/* Inner glow effect */}
              <div 
                className="absolute inset-0" 
                style={{
                  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
                }}
              />
            </div>
            
            {/* 호버시 추가 글로우 */}
            <div 
              className="absolute inset-0 rounded-md md:rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" 
              style={{ 
                boxShadow: `0 0 20px ${itemColors.glow.replace('0.4', '1')}, inset 0 0 20px ${itemColors.glow}` 
              }} 
            />
            
            {/* 부피 표시 - 첫 번째 셀에만 */}
            {idx === 0 && (
              <div 
                className="absolute px-1 py-0.5 rounded text-[7px] md:text-[9px] font-bold font-mono pointer-events-none z-10"
                style={{
                  top: '2px',
                  left: '2px',
                  backgroundColor: itemColors.glow.replace('0.4', '0.8'),
                  color: '#000',
                  textShadow: 'none',
                  border: `1px solid ${itemColors.border}`,
                }}
              >
                {item.volume}
              </div>
            )}
            
            {/* 아이템 라벨 - 첫 번째 셀에만 */}
            {idx === 0 && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none p-0.5 md:p-1 z-10">
                <div 
                  className="text-[8px] md:text-sm font-bold text-center leading-tight font-mono"
                  style={{ 
                    color: itemColors.border,
                    textShadow: '0 1px 4px rgba(0, 0, 0, 1), 0 0 4px rgba(0, 0, 0, 0.9)',
                    letterSpacing: '0.3px',
                    filter: `drop-shadow(0 0 2px ${itemColors.glow})`,
                    fontSize: item.volume === 1 ? '7px' : '8px',
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
        );
      })}
    </div>
  );
}

interface TrashZoneProps {
  onDrop: (item: Item | NearbyItem) => void;
}

function TrashZone({ onDrop }: TrashZoneProps) {
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
      className={`p-4 border-2 border-dashed rounded-lg text-center transition-all ${
        isOver && canDrop
          ? 'border-[#999999] bg-[#F5F5F5]'
          : 'border-[#BBBBBB] bg-[#F0F0F0]'
      }`}
    >
      <div className="text-xs text-[#666666]">여기에 끌어다 놓으면 버려요</div>
    </div>
  );
}

interface NearbyZoneProps {
  onDrop: (item: Item) => void;
  children: React.ReactNode;
}

function NearbyZone({ onDrop, children }: NearbyZoneProps) {
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
      className={`bg-[#1A0F0F] backdrop-blur-sm border rounded-lg p-4 min-h-[120px] transition-all relative overflow-hidden shadow-[0_4px_16px_rgba(255,71,87,0.2)] ${
        isOver && canDrop 
          ? 'border-[#FF4757] shadow-[0_0_30px_rgba(255,71,87,0.6)]' 
          : 'border-[#FF4757]/40 shadow-[0_0_20px_rgba(255,71,87,0.3)]'
      }`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-[#FF4757]/10 to-transparent pointer-events-none animate-pulse" />
      <div className="relative">
        {children}
      </div>
    </div>
  );
}

interface MiscSpaceZoneProps {
  onDrop: (item: NearbyItem) => void;
  children: React.ReactNode;
}

function MiscSpaceZone({ onDrop, children }: MiscSpaceZoneProps) {
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
      className={`bg-[#161922]/50 backdrop-blur-sm border p-3 md:p-4 rounded-lg min-h-[100px] md:min-h-[120px] relative overflow-hidden transition-all ${
        isOver && canDrop 
          ? 'border-[#BF5AF2] shadow-[0_0_30px_rgba(191,90,242,0.4)]' 
          : 'border-[#BF5AF2]/20 shadow-[0_4px_16px_rgba(191,90,242,0.1)]'
      }`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-[#BF5AF2]/5 to-transparent pointer-events-none" />
      <div className="relative">
        {children}
      </div>
    </div>
  );
}

interface FreeItemChipProps {
  item: Item;
}

function FreeItemChip({ item }: FreeItemChipProps) {
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
      className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-[#2A2F3A]/50 backdrop-blur-sm border border-[#BF5AF2]/30 rounded-lg text-xs text-[#E8EAED] cursor-move hover:bg-[#BF5AF2]/20 hover:border-[#BF5AF2] hover:shadow-[0_0_10px_rgba(191,90,242,0.4)] transition-all font-medium ${
        isDragging ? 'opacity-30' : 'opacity-100'
      }`}
    >
      {getIcon(item.icon)}
      <span>{item.name}</span>
      <span className="text-[#BF5AF2] font-mono text-[10px]">×{item.count}</span>
    </div>
  );
}

interface NearbyItemChipProps {
  item: NearbyItem;
  count?: number;
}

function NearbyItemChip({ item, count = 1 }: NearbyItemChipProps) {
  const [{ isDragging }, drag] = useDrag({
    type: 'nearby',
    item: item,
    collect: (monitor) => {
      const isDragging = monitor.isDragging();
      return {
        isDragging,
      };
    },
  });

  return (
    <div
      ref={drag}
      className={`inline-flex items-center gap-2 px-3 py-2 bg-[#2A2F3A]/50 backdrop-blur-sm border rounded-lg text-xs text-[#E8EAED] cursor-move hover:bg-[#FF4757]/20 hover:border-[#FF4757] hover:shadow-[0_0_15px_rgba(255,71,87,0.5)] transition-all font-medium relative ${
        isDragging ? 'opacity-30' : 'opacity-100'
      }`}
      style={{
        borderColor: 'rgba(255, 71, 87, 0.5)',
        animation: 'flicker 2s ease-in-out infinite',
      }}
    >
      {count > 1 && (
        <span className="absolute -top-2 -right-2 px-1.5 py-0.5 bg-[#FF4757] text-white rounded-full text-[10px] font-mono font-bold border-2 border-[#0B0E14]">
          ×{count}
        </span>
      )}
      <span>{item.name}</span>
      <span className="px-1.5 py-0.5 bg-[#FF4757]/20 text-[#FF4757] rounded text-[10px] font-mono border border-[#FF4757]/30 font-bold">
        {item.volume}
      </span>
    </div>
  );
}

interface BagTabProps {
  gridSize: number;
  timeRemaining: number;
  formatTime: (time: number) => string;
}

function BagTabContent({ gridSize, timeRemaining, formatTime }: BagTabProps) {
  const gridCols = 10;
  const gridRows = Math.ceil(gridSize / gridCols);

  const [items, setItems] = useState<Item[]>([
    { id: '1', name: '사과', count: 1, volume: 1, gridPosition: { row: 0, col: 0 }, shapeIndex: 0 },
    { id: '2', name: '물병', count: 1, volume: 1, gridPosition: { row: 0, col: 1 }, shapeIndex: 0 },
    { id: '3', name: '빵', count: 1, volume: 2, gridPosition: { row: 0, col: 2 }, shapeIndex: 0 },
    { id: '4', name: '철 광석', count: 1, volume: 4, gridPosition: { row: 0, col: 4 }, shapeIndex: 0 },
    { id: '5', name: '검', count: 1, volume: 4, gridPosition: { row: 0, col: 8 }, shapeIndex: 0 },
  ]);

  const [freeItems, setFreeItems] = useState<Item[]>([
    { id: 'f1', name: '클립', count: 5, volume: 0, icon: 'paperclip' },
    { id: 'f2', name: '메모지', count: 12, volume: 0, icon: 'file' },
    { id: 'f3', name: '동전', count: 8, volume: 0, icon: 'coins' },
  ]);

  const [nearbyItems, setNearbyItems] = useState<NearbyItem[]>([
    { id: 'n1', name: '포션', volume: 1 },
    { id: 'n2', name: '포션', volume: 1 },
    { id: 'n3', name: '포션', volume: 1 },
    { id: 'n4', name: '붕대', volume: 2 },
    { id: 'n5', name: '붕대', volume: 2 },
    { id: 'n6', name: '소독약', volume: 2 },
    { id: 'n7', name: '소독약', volume: 2 },
    { id: 'n8', name: '잡지', volume: 3 },
    { id: 'n9', name: '잡지', volume: 3 },
    { id: 'n10', name: '빵', volume: 2 },
    { id: 'n11', name: '영수증', volume: 0, icon: 'file' },
    { id: 'n12', name: '영수증', volume: 0, icon: 'file' },
    { id: 'n13', name: '영수증', volume: 0, icon: 'file' },
  ]);

  const [draggedItem, setDraggedItem] = useState<(Item | NearbyItem) | null>(null);
  const [hoverPosition, setHoverPosition] = useState<{ row: number; col: number } | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  
  // 수량 선택 다이얼로그 상태
  const [quantityDialog, setQuantityDialog] = useState<{
    isOpen: boolean;
    item: Item | NearbyItem | null;
    maxQuantity: number;
    selectedQuantity: number;
    action: 'toNearby' | 'toMisc' | null;
  }>({ isOpen: false, item: null, maxQuantity: 1, selectedQuantity: 1, action: null });

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
      if (draggedItem.volume === 0) {
        // 부피 0 아이템은 misc space로
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
        setNearbyItems((prev) => prev.filter((i) => i.id !== draggedItem.id));
      } else {
        // 일반 아이템은 가방으로
        const newItem: Item = {
          id: draggedItem.id,
          name: draggedItem.name,
          count: 1,
          volume: draggedItem.volume,
          gridPosition: { row, col },
          shapeIndex: 0,
          icon: draggedItem.icon,
        };
        
        if (canPlaceItem(newItem, row, col, 0)) {
          setItems((prev) => [...prev, newItem]);
          setNearbyItems((prev) => prev.filter((i) => i.id !== draggedItem.id));
        }
      }
    }
    setDraggedItem(null);
    setHoverPosition(null);
  };

  const handleItemClick = (item: Item) => {
    const shapeCount = SHAPES[item.volume]?.length || 1;
    const nextShapeIndex = ((item.shapeIndex || 0) + 1) % shapeCount;
    
    // 새 모양으로 배치 가능한지 확인
    if (item.gridPosition && canPlaceItem(item, item.gridPosition.row, item.gridPosition.col, nextShapeIndex)) {
      setItems((prev) =>
        prev.map((i) =>
          i.id === item.id ? { ...i, shapeIndex: nextShapeIndex } : i
        )
      );
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
      // 가방 아이템을 주변으로
      const nearbyItem: NearbyItem = {
        id: draggedItem.id,
        name: draggedItem.name,
        volume: draggedItem.volume,
        icon: draggedItem.icon,
      };
      setNearbyItems((prev) => [...prev, nearbyItem]);
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

    // 그룹화된 아이템인 경우 (count와 ids가 있음)
    if (draggedItem.count && draggedItem.count > 1 && draggedItem.ids) {
      // 수량이 2개 이상이면 다이얼로그 표시
      setQuantityDialog({
        isOpen: true,
        item: draggedItem,
        maxQuantity: draggedItem.count,
        selectedQuantity: 1,
        action: 'toMisc',
      });
    } else {
      // 단일 아이템이면 바로 이동
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
      
      // Nearby에서 해당 아이템 제거
      if (draggedItem.ids) {
        // 그룹화된 아이템에서 하나만 제거
        const removeId = draggedItem.ids[0];
        setNearbyItems((prev) => prev.filter((i) => i.id !== removeId));
      } else {
        setNearbyItems((prev) => prev.filter((i) => i.id !== draggedItem.id));
      }
    }
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
      if (item.ids) {
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

  return (
    <div className="flex flex-col gap-4 md:gap-6 h-full">
      {/* 수량 선택 다이얼로그 */}
      {quantityDialog.isOpen && quantityDialog.item && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(11, 14, 20, 0.9)' }}>
          <div className="bg-[#1C2128] border-2 border-[#BF5AF2] rounded-xl p-6 max-w-sm w-full shadow-[0_0_40px_rgba(191,90,242,0.5)] relative">
            {/* Glassmorphism effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-[#BF5AF2]/10 to-transparent rounded-xl pointer-events-none" />
            
            <div className="relative space-y-4">
              {/* 헤더 */}
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-[#BF5AF2] uppercase tracking-wider">수량 선택</h3>
                <button
                  onClick={() => setQuantityDialog({ isOpen: false, item: null, maxQuantity: 1, selectedQuantity: 1, action: null })}
                  className="text-[#8B92A0] hover:text-[#BF5AF2] transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* 아이템 정보 */}
              <div className="bg-[#0B0E14]/50 border border-[#BF5AF2]/30 rounded-lg p-4">
                <div className="text-sm text-[#E8EAED] font-medium mb-2">{quantityDialog.item.name}</div>
                <div className="text-xs text-[#8B92A0] font-mono">보유 수량: {quantityDialog.maxQuantity}개</div>
              </div>

              {/* 수량 선택 */}
              <div className="space-y-2">
                <label className="text-sm text-[#E8EAED] font-medium">이동할 수량</label>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setQuantityDialog(prev => ({ ...prev, selectedQuantity: Math.max(1, prev.selectedQuantity - 1) }))}
                    className="px-4 py-2 bg-[#2A2F3A] border border-[#BF5AF2]/30 rounded-lg text-[#BF5AF2] font-bold hover:bg-[#BF5AF2]/20 hover:border-[#BF5AF2] transition-all"
                  >
                    -
                  </button>
                  <input
                    type="number"
                    min="1"
                    max={quantityDialog.maxQuantity}
                    value={quantityDialog.selectedQuantity}
                    onChange={(e) => {
                      const value = Math.min(quantityDialog.maxQuantity, Math.max(1, parseInt(e.target.value) || 1));
                      setQuantityDialog(prev => ({ ...prev, selectedQuantity: value }));
                    }}
                    className="flex-1 px-4 py-2 bg-[#0B0E14] border border-[#BF5AF2]/30 rounded-lg text-center text-[#E8EAED] font-mono font-bold focus:border-[#BF5AF2] focus:outline-none"
                  />
                  <button
                    onClick={() => setQuantityDialog(prev => ({ ...prev, selectedQuantity: Math.min(prev.maxQuantity, prev.selectedQuantity + 1) }))}
                    className="px-4 py-2 bg-[#2A2F3A] border border-[#BF5AF2]/30 rounded-lg text-[#BF5AF2] font-bold hover:bg-[#BF5AF2]/20 hover:border-[#BF5AF2] transition-all"
                  >
                    +
                  </button>
                </div>
                <button
                  onClick={() => setQuantityDialog(prev => ({ ...prev, selectedQuantity: prev.maxQuantity }))}
                  className="w-full py-1.5 text-xs text-[#8B92A0] hover:text-[#BF5AF2] transition-colors font-mono"
                >
                  전체 선택
                </button>
              </div>

              {/* 버튼 */}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setQuantityDialog({ isOpen: false, item: null, maxQuantity: 1, selectedQuantity: 1, action: null })}
                  className="flex-1 px-4 py-2.5 bg-[#2A2F3A] border border-[#8B92A0]/30 rounded-lg text-[#8B92A0] font-bold hover:bg-[#8B92A0]/20 hover:border-[#8B92A0] transition-all"
                >
                  취소
                </button>
                <button
                  onClick={handleQuantityConfirm}
                  className="flex-1 px-4 py-2.5 bg-[#BF5AF2]/20 border border-[#BF5AF2] rounded-lg text-[#BF5AF2] font-bold hover:bg-[#BF5AF2]/30 hover:shadow-[0_0_20px_rgba(191,90,242,0.6)] transition-all"
                >
                  확인
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 상단: 가방 영역 (메인) */}
      <div className="flex-1 space-y-2 md:space-y-3">
        {/* 헤더 및 용량 정보 */}
        <div className="flex items-end justify-between flex-wrap gap-2">
          <h3 className="text-sm md:text-base font-bold text-[#00F3FF] tracking-wider uppercase" style={{ fontFamily: 'Inter, sans-serif' }}>Inventory Bag</h3>
          {/* 대형 용량 수치 + 경고 */}
          <div className="flex items-center gap-2 md:gap-3">
            {isCriticalCapacity && (
              <div className="flex items-center gap-1 md:gap-1.5 px-1.5 md:px-2 py-0.5 md:py-1 bg-[#FF4757]/10 border border-[#FF4757]/30 rounded-lg animate-pulse">
                <AlertCircle className="w-3 h-3 md:w-3.5 md:h-3.5 text-[#FF4757]" />
                <span className="text-[10px] md:text-xs text-[#FF4757] font-mono font-bold">CRITICAL</span>
              </div>
            )}
            <div className={`text-xl md:text-2xl font-bold font-mono transition-all ${
              usedCapacity / maxCapacity > 0.8
                ? 'text-[#FF4757]'
                : usedCapacity / maxCapacity > 0.6
                ? 'text-[#FFB020]'
                : 'text-[#00FF88]'
            }`}>
              {usedCapacity} <span className="text-base md:text-lg text-[#8B92A0]">/</span> {maxCapacity}
            </div>
          </div>
        </div>
        
        {/* Capacity Gauge */}
        <div className="space-y-1 md:space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] md:text-xs text-[#8B92A0] font-mono uppercase tracking-wider font-bold">CAPACITY</span>
            <span className={`text-[10px] md:text-xs font-mono font-bold ${
              usedCapacity / maxCapacity > 0.8
                ? 'text-[#FF4757]'
                : usedCapacity / maxCapacity > 0.6
                ? 'text-[#FFB020]'
                : 'text-[#00FF88]'
            }`}>
              {Math.round((usedCapacity / maxCapacity) * 100)}%
            </span>
          </div>
          <div className="relative h-4 md:h-6 bg-[#0B0E14]/80 rounded-full overflow-hidden border border-white/10 md:border-2">
            <div 
              className={`h-full transition-all duration-500 ${
                usedCapacity / maxCapacity > 0.8
                  ? 'bg-gradient-to-r from-[#FF4757] to-[#FF6B9D] shadow-[0_0_20px_rgba(255,71,87,0.8)]'
                  : usedCapacity / maxCapacity > 0.6
                  ? 'bg-gradient-to-r from-[#FFB020] to-[#FFC837] shadow-[0_0_20px_rgba(255,176,32,0.8)]'
                  : 'bg-gradient-to-r from-[#00FF88] to-[#00F3FF] shadow-[0_0_20px_rgba(0,255,136,0.8)]'
              }`}
              style={{ width: `${(usedCapacity / maxCapacity) * 100}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-white/30 to-transparent animate-pulse" />
            </div>
          </div>
        </div>
        
        <div className="bg-[#1C2128]/60 backdrop-blur-sm border border-white/10 p-3 md:p-6 rounded-xl relative overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.4)] overflow-x-auto">
          {/* Glassmorphism effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
          
          <div className="relative mx-auto" style={{ width: 'fit-content', minWidth: '280px' }}>
            {gridCells.map((row, rowIndex) => (
              <div key={rowIndex} className="flex gap-1">
                {row.map((cellData, colIndex) => {
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
                    />
                  );
                })}
              </div>
            ))}
            
            {/* 그리드 밖으로 나가는 경우 빨간색 오버레이 표시 */}
            {draggedItem && hoverPosition && !isValidDropPosition && (() => {
              const volume = 'volume' in draggedItem ? draggedItem.volume : 0;
              const shapeIndex = 'shapeIndex' in draggedItem ? (draggedItem.shapeIndex || 0) : 0;
              const shape = SHAPES[volume]?.[shapeIndex] || SHAPES[1][0];
              
              // 모바일과 데스크톱에서 다른 크기 사용
              const cellSize = isMobile ? 28 : 48;
              const gapSize = isMobile ? 1 : 4;
              const totalCellSize = cellSize + gapSize;
              
              const blockWidth = (Math.max(...shape.map(p => p.col)) + 1) * cellSize + Math.max(...shape.map(p => p.col)) * gapSize;
              const blockHeight = (Math.max(...shape.map(p => p.row)) + 1) * cellSize + Math.max(...shape.map(p => p.row)) * gapSize;
              
              const left = hoverPosition.col * totalCellSize;
              const top = hoverPosition.row * totalCellSize;
              
              return (
                <div
                  className="absolute pointer-events-none"
                  style={{
                    left: `${left}px`,
                    top: `${top}px`,
                    width: `${blockWidth}px`,
                    height: `${blockHeight}px`,
                  }}
                >
                  <div 
                    className="absolute inset-0 rounded-md md:rounded-lg border-2 border-[#FF4757] bg-[#FF4757]/10"
                    style={{
                      boxShadow: '0 0 15px rgba(255, 71, 87, 0.5)',
                    }}
                  />
                </div>
              );
            })()}
          </div>
        </div>
      </div>

      {/* 하단: 여유공간 + 주변 (보조) - 모바일에서는 세로로 배치 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        {/* 여유공간 - 미세하게 다른 배경 */}
        <div className="space-y-2 md:space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs md:text-sm font-bold text-[#BF5AF2] tracking-wider uppercase" style={{ fontFamily: 'Inter, sans-serif' }}>MISC SPACE</h3>
            <div className="text-[10px] md:text-xs text-[#8B92A0] font-mono font-bold">WEIGHTLESS</div>
          </div>
          <MiscSpaceZone onDrop={handleMiscDrop}>
            {freeItems.length > 0 ? (
              <div className="relative flex flex-wrap gap-2 overflow-x-auto">
                {freeItems.map((item) => (
                  <FreeItemChip key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-[100px] md:h-[120px] text-[10px] md:text-xs text-[#8B92A0]/50 font-mono">
                No weightless items
              </div>
            )}
          </MiscSpaceZone>
        </div>

        {/* 주변 - 강조된 경고 배경 */}
        <div className="space-y-2 md:space-y-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h3 className="text-xs md:text-sm font-bold text-[#FF4757] tracking-wider uppercase" style={{ fontFamily: 'Inter, sans-serif' }}>NEARBY ITEMS</h3>
            <div className="flex items-center gap-1 md:gap-2 px-1.5 md:px-2 py-0.5 md:py-1 bg-[#FF4757]/10 border border-[#FF4757]/30 rounded-lg">
              <AlertCircle className="w-3 h-3 md:w-3.5 md:h-3.5 text-[#FF4757] animate-pulse" />
              <span className="text-[10px] md:text-xs text-[#FF4757] font-mono font-bold">DELETE IN {formatTime(timeRemaining)}</span>
            </div>
          </div>
          <NearbyZone onDrop={handleNearbyDrop}>
            {nearbyItemsGrouped.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {nearbyItemsGrouped.map((item) => (
                  <NearbyItemChip key={item.ids[0]} item={item} count={item.count} />
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-[100px] md:h-[120px] text-[10px] md:text-xs text-[#8B92A0]/50 font-mono">
                No nearby items
              </div>
            )}
          </NearbyZone>
        </div>
      </div>
    </div>
  );
}

export default function BagTab({ gridSize, timeRemaining, formatTime }: BagTabProps) {
  return (
    <DndProvider backend={HTML5Backend}>
      <BagTabContent gridSize={gridSize} timeRemaining={timeRemaining} formatTime={formatTime} />
      <style>{`
        @keyframes flicker {
          0%, 100% { 
            border-color: rgba(255, 71, 87, 0.4);
            box-shadow: 0 0 10px rgba(255, 71, 87, 0.2);
          }
          50% { 
            border-color: rgba(255, 71, 87, 0.8);
            box-shadow: 0 0 20px rgba(255, 71, 87, 0.4);
          }
        }
      `}</style>
    </DndProvider>
  );
}