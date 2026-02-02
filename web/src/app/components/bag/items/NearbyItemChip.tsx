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
      className={`inline-flex items-center gap-2 px-3 py-2 bg-[var(--color-bg-light)]/50 border rounded-lg text-xs text-[var(--color-text-primary)] cursor-move hover:border-[var(--color-nearby)] transition-all font-medium relative ${
        isDragging ? 'opacity-30' : 'opacity-100'
      }`}
      style={{
        borderColor: 'var(--color-nearby)',
      }}
    >
      {count > 1 && (
        <span className="absolute -top-2 -right-2 px-1.5 py-0.5 bg-[var(--color-nearby)] text-white rounded-full text-[10px] font-bold border-2 border-[var(--color-bg-dark)]">
          ×{count}
        </span>
      )}
      <span>{item.name}</span>
      <span className="px-1.5 py-0.5 bg-[var(--color-nearby)]/20 text-[var(--color-nearby)] rounded text-[10px] border border-[var(--color-nearby)]/30 font-bold">
        {item.volume}
      </span>
    </div>
  );
}
