import { useDrag } from 'react-dnd';
import type { NearbyItem } from '../types';

interface NearbyItemChipProps {
  item: NearbyItem;
  count?: number;
}

export function NearbyItemChip({ item, count = 1 }: NearbyItemChipProps) {
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
