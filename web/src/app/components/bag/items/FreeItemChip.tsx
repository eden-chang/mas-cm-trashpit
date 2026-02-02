import { useDrag } from 'react-dnd';
import { Coins, FileText, Paperclip } from 'lucide-react';
import type { Item } from '../types';

interface FreeItemChipProps {
  item: Item;
}

function getIcon(iconName?: string) {
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
}

export function FreeItemChip({ item }: FreeItemChipProps) {
  const [{ isDragging }, drag] = useDrag({
    type: 'freeitem',
    item: item,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  return (
    <div
      ref={drag}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-[var(--color-bg-light)]/50 border border-[var(--color-misc)]/25 rounded-lg text-xs text-[var(--color-text-primary)] cursor-move hover:border-[var(--color-misc)]/60 transition-all font-medium ${
        isDragging ? 'opacity-30' : 'opacity-100'
      }`}
    >
      {getIcon(item.icon)}
      <span>{item.name}</span>
      <span className="text-[var(--color-misc)] text-[10px]">×{item.count}</span>
    </div>
  );
}
