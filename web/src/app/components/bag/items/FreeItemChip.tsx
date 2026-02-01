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
