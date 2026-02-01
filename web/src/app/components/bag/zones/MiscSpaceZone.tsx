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
