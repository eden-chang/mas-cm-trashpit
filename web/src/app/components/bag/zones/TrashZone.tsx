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
          ? 'border-[#999999] bg-[#F5F5F5]'
          : 'border-[#BBBBBB] bg-[#F0F0F0]'
      }`}
    >
      <div className="text-xs text-[#666666]">여기에 끌어다 놓으면 버려요</div>
    </div>
  );
}
