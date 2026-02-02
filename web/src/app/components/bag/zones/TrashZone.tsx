import { useDrop } from 'react-dnd';
import type { Item, NearbyItem } from '../types';

interface TrashZoneProps {
  onDrop: (item: Item | NearbyItem) => void;
}

export function TrashZone({ onDrop }: TrashZoneProps) {
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
          ? 'border-[var(--color-trash-border-hover)] bg-[var(--color-trash-bg-hover)]'
          : 'border-[var(--color-trash-border)] bg-[var(--color-trash-bg)]'
      }`}
    >
      <div className="text-xs text-[var(--color-trash-text)]">이곳에 아이템을 끌어다 버릴 수 있어요</div>
    </div>
  );
}
