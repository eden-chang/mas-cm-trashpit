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
