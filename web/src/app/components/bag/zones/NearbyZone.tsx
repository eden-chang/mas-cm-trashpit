import { useDrop } from 'react-dnd';
import type { Item } from '../types';

interface NearbyZoneProps {
  onDrop: (item: Item) => void;
  children: React.ReactNode;
}

export function NearbyZone({ onDrop, children }: NearbyZoneProps) {
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
      className={`bg-[var(--color-bg-dark)] border rounded-lg p-4 min-h-[120px] transition-all ${
        isOver && canDrop
          ? 'border-[var(--color-nearby)]'
          : 'border-[var(--color-nearby)]/30'
      }`}
    >
      <div className="relative">
        {children}
      </div>
    </div>
  );
}
