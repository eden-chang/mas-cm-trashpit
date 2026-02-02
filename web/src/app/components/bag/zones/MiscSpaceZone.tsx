import { useDrop } from 'react-dnd';
import type { NearbyItem } from '../types';

interface MiscSpaceZoneProps {
  onDrop: (item: NearbyItem) => void;
  children: React.ReactNode;
}

export function MiscSpaceZone({ onDrop, children }: MiscSpaceZoneProps) {
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
      className={`bg-[var(--color-bg-mid)]/50 border p-3 md:p-4 rounded-lg min-h-[100px] md:min-h-[120px] transition-all ${
        isOver && canDrop
          ? 'border-[var(--color-misc)]'
          : 'border-[var(--color-misc)]/20'
      }`}
    >
      <div className="relative">
        {children}
      </div>
    </div>
  );
}
