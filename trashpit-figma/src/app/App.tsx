import BagTab from '@/app/components/BagTab';
import { RefreshCw, Cloud, AlertCircle, Package, Menu, X, Search } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function App() {
  const [selectedCharacter, setSelectedCharacter] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(31522); // 08:45:22 in seconds
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(true); // 예시로 true로 설정
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setTimeRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // 예시 캐릭터 데이터 (20명)
  const characters = [
    { name: '전사', capacity: 15, maxCapacity: 60, gridSize: 60, strength: 6, hp: 85, maxHp: 100 },
    { name: '마법사', capacity: 8, maxCapacity: 20, gridSize: 20, strength: 2, hp: 45, maxHp: 60 },
    { name: '도적', capacity: 12, maxCapacity: 40, gridSize: 40, strength: 4, hp: 70, maxHp: 80 },
    { name: '성기사', capacity: 18, maxCapacity: 60, gridSize: 60, strength: 7, hp: 95, maxHp: 100 },
    { name: '암살자', capacity: 10, maxCapacity: 40, gridSize: 40, strength: 5, hp: 60, maxHp: 70 },
    { name: '사냥꾼', capacity: 14, maxCapacity: 50, gridSize: 50, strength: 5, hp: 75, maxHp: 90 },
    { name: '드루이드', capacity: 6, maxCapacity: 30, gridSize: 30, strength: 3, hp: 50, maxHp: 70 },
    { name: '바드', capacity: 5, maxCapacity: 25, gridSize: 25, strength: 2, hp: 40, maxHp: 50 },
    { name: '광전사', capacity: 20, maxCapacity: 60, gridSize: 60, strength: 8, hp: 90, maxHp: 95 },
    { name: '흑마법사', capacity: 7, maxCapacity: 20, gridSize: 20, strength: 2, hp: 35, maxHp: 50 },
    { name: '수도승', capacity: 11, maxCapacity: 35, gridSize: 35, strength: 4, hp: 70, maxHp: 80 },
    { name: '네크로맨서', capacity: 9, maxCapacity: 25, gridSize: 25, strength: 3, hp: 40, maxHp: 60 },
    { name: '레인저', capacity: 13, maxCapacity: 45, gridSize: 45, strength: 5, hp: 65, maxHp: 75 },
    { name: '소서러', capacity: 6, maxCapacity: 20, gridSize: 20, strength: 2, hp: 38, maxHp: 55 },
    { name: '워록', capacity: 8, maxCapacity: 25, gridSize: 25, strength: 3, hp: 48, maxHp: 65 },
    { name: '클레릭', capacity: 10, maxCapacity: 40, gridSize: 40, strength: 4, hp: 70, maxHp: 85 },
    { name: '샤먼', capacity: 9, maxCapacity: 30, gridSize: 30, strength: 3, hp: 55, maxHp: 70 },
    { name: '검사', capacity: 16, maxCapacity: 55, gridSize: 55, strength: 6, hp: 80, maxHp: 90 },
    { name: '궁수', capacity: 12, maxCapacity: 45, gridSize: 45, strength: 4, hp: 60, maxHp: 70 },
    { name: '연금술사', capacity: 7, maxCapacity: 30, gridSize: 30, strength: 2, hp: 45, maxHp: 60 },
  ];

  const currentCharacter = characters[selectedCharacter];

  // 검색 필터링
  const filteredCharacters = characters.filter(char =>
    char.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="size-full flex flex-col bg-bg-base">
      {/* 헤더 */}
      <header className="h-14 md:h-16 border-b border-border flex items-center justify-between px-3 md:px-6 bg-bg-raised/50 backdrop-blur-sm shrink-0">
        <h1 className="text-base md:text-xl font-bold bg-gradient-to-r from-cyan to-purple bg-clip-text text-transparent tracking-wide">
          TRPG INVENTORY
        </h1>
        <div className="flex items-center gap-2 md:gap-4">
          <div className="text-xs md:text-sm text-text-secondary font-mono">
            {currentCharacter.name} | STR: {currentCharacter.strength}
          </div>
          {/* 햄버거 버튼 (모바일용) */}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="md:hidden p-2 rounded-lg bg-bg-overlay border border-cyan/30 text-cyan hover:border-cyan hover:shadow-[0_0_15px_rgba(var(--color-primary-rgb),0.3)] transition-all"
          >
            {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* 메인 콘텐츠 영역 */}
        <main className="flex-1 flex flex-col bg-bg-base overflow-y-auto">
          <div className="p-3 md:p-6">
            <BagTab gridSize={currentCharacter.gridSize} timeRemaining={timeRemaining} formatTime={formatTime} />
          </div>
        </main>

        {/* 오버레이 (모바일에서 사이드바 열렸을 때) */}
        {isSidebarOpen && (
          <div
            className="md:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}
        
        {/* 오른쪽 사이드바 */}
        <aside className={`
          w-full sm:w-96 md:w-80 border-l border-border bg-bg-raised/30 backdrop-blur-md flex flex-col
          fixed md:relative right-0 top-14 md:top-16 bottom-0 z-50
          transform transition-transform duration-300
          ${isSidebarOpen ? 'translate-x-0' : 'translate-x-full md:translate-x-0'}
        `}>
          <div className="p-3 md:p-3 pt-3 md:pt-3 border-b border-border flex items-center justify-between shrink-0">
            <h2 className="text-sm font-semibold text-cyan tracking-wider uppercase">Characters</h2>
            <button
              onClick={() => setIsSidebarOpen(false)}
              className="md:hidden p-1 rounded text-text-secondary hover:text-cyan transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          {/* 검색창 */}
          <div className="p-3 border-b border-border shrink-0">
            <div className="relative">
              <Search className="absolute top-2.5 left-3 w-4 h-4 text-text-secondary pointer-events-none" />
              <input
                type="text"
                placeholder="Search characters..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full py-2 pl-10 pr-3 rounded-lg bg-bg-base/50 border border-border text-sm text-text-primary placeholder-text-secondary focus:border-cyan/50 focus:shadow-[0_0_15px_rgba(var(--color-primary-rgb),0.2)] focus:outline-none transition-all"
              />
            </div>
          </div>
          
          {/* 캐릭터 리스트 */}
          <div className="flex-1 overflow-y-auto p-2 md:p-3 space-y-2 md:space-y-3">
            {filteredCharacters.map((character, index) => {
              const isActive = selectedCharacter === characters.indexOf(character);
              const hpPercent = (character.hp / character.maxHp) * 100;
              const capacityPercent = (character.capacity / character.gridSize) * 100;
              
              return (
                <button
                  key={index}
                  onClick={() => {
                    setSelectedCharacter(characters.indexOf(character));
                    setIsSidebarOpen(false); // 모바일에서 선택 후 닫기
                  }}
                  className={`w-full text-left p-2 md:p-3 rounded-lg transition-all relative overflow-hidden group ${
                    isActive
                      ? 'bg-bg-overlay border-2 border-cyan shadow-[0_0_25px_rgba(var(--color-primary-rgb),0.5)]'
                      : 'bg-bg-base/50 border border-border hover:border-purple/50 hover:shadow-[0_0_15px_rgba(var(--color-secondary-rgb),0.2)]'
                  }`}
                >
                  {/* Glassmorphism overlay */}
                  <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
                  
                  <div className="relative flex items-center gap-2 md:gap-3">
                    {/* 아바타 */}
                    <div className={`w-9 h-9 md:w-10 md:h-10 rounded-full flex items-center justify-center text-sm md:text-base font-bold transition-all shrink-0 ${
                      isActive 
                        ? 'bg-gradient-to-br from-cyan to-purple text-black shadow-[0_0_15px_rgba(var(--color-primary-rgb),0.5)]' 
                        : 'bg-bg-overlay text-text-secondary group-hover:bg-purple/20'
                    }`}>
                      {character.name[0]}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      {/* 이름과 STR을 같은 줄에 */}
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="text-xs md:text-sm font-semibold text-text-primary">{character.name}</div>
                        <div className="flex items-center gap-1 text-[9px] md:text-[10px] text-text-secondary">
                          <span className="font-mono font-bold">STR</span>
                          <span className="font-mono text-purple font-bold">{character.strength}</span>
                        </div>
                      </div>
                      
                      {/* HP와 가방 용량을 한 줄에 나란히 */}
                      <div className="flex gap-2 md:gap-3">
                        {/* HP 바 */}
                        <div className="flex-1">
                          <div className="flex items-center justify-between text-[9px] md:text-[10px] text-text-secondary mb-0.5 font-mono">
                            <span className="font-bold">HP</span>
                            <span className="font-bold text-danger">{character.hp}/{character.maxHp}</span>
                          </div>
                          <div className="h-1.5 md:h-2 bg-bg-base/80 rounded-full overflow-hidden border border-border">
                            <div 
                              className="h-full bg-danger rounded-full transition-all duration-300 shadow-[0_0_8px_rgba(var(--color-danger-rgb),0.6)]"
                              style={{ width: `${hpPercent}%` }}
                            />
                          </div>
                        </div>
                        
                        {/* 가방 용량 바 */}
                        <div className="flex-1">
                          <div className="flex items-center justify-between text-[9px] md:text-[10px] text-text-secondary mb-0.5 font-mono">
                            <span className="font-bold flex items-center gap-0.5">
                              <Package className="w-2 h-2 md:w-2.5 md:h-2.5" />
                              BAG
                            </span>
                            <span className={`font-bold ${
                              capacityPercent > 80
                                ? 'text-danger'
                                : capacityPercent > 60
                                ? 'text-warning'
                                : 'text-success'
                            }`}>{character.capacity}/{character.gridSize}</span>
                          </div>
                          <div className="h-1.5 md:h-2 bg-bg-base/80 rounded-full overflow-hidden border border-border">
                            <div 
                              className={`h-full rounded-full transition-all duration-300 ${
                                capacityPercent > 80
                                  ? 'bg-danger shadow-[0_0_8px_rgba(var(--color-danger-rgb),0.6)]'
                                  : capacityPercent > 60
                                  ? 'bg-warning shadow-[0_0_8px_rgba(var(--color-warning-rgb),0.6)]'
                                  : 'bg-gradient-to-r from-success to-cyan shadow-[0_0_8px_rgba(var(--color-success-rgb),0.6)]'
                              }`}
                              style={{ width: `${capacityPercent}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="p-3 md:p-4 border-t border-border space-y-2 shrink-0">
            {/* Sync to Cloud 버튼 */}
            <button 
              className="w-full flex items-center justify-center gap-2 px-3 md:px-4 py-2 md:py-2.5 text-sm md:text-base rounded-lg bg-success/20 border border-success/50 text-success hover:border-success hover:shadow-[0_0_20px_rgba(var(--color-success-rgb),0.4)] transition-all font-bold relative overflow-hidden group"
              onClick={() => setHasUnsavedChanges(false)}
            >
              <div className="absolute inset-0 bg-success/10 opacity-0 group-hover:opacity-100 transition-opacity" />
              <Cloud className="w-4 h-4 relative z-10" />
              <span className="relative z-10">SYNC TO CLOUD</span>
              {hasUnsavedChanges && (
                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 md:w-3 md:h-3 bg-warning rounded-full animate-pulse shadow-[0_0_10px_rgba(var(--color-warning-rgb),0.8)]" />
              )}
            </button>
            
            {/* Unsaved Changes 인디케이터 */}
            {hasUnsavedChanges && (
              <div className="flex items-center gap-2 px-2 md:px-3 py-1.5 md:py-2 bg-warning/10 border border-warning/30 rounded-lg">
                <div className="w-1.5 h-1.5 md:w-2 md:h-2 bg-warning rounded-full animate-pulse" />
                <span className="text-[10px] md:text-xs text-warning font-mono">Unsaved Changes</span>
              </div>
            )}
            
            {/* Refresh Data 버튼 */}
            <button className="w-full flex items-center justify-center gap-2 px-3 md:px-4 py-2 md:py-2.5 text-sm md:text-base rounded-lg bg-gradient-to-r from-cyan/10 to-purple/10 border border-cyan/30 text-cyan hover:border-cyan hover:shadow-[0_0_15px_rgba(var(--color-primary-rgb),0.3)] transition-all font-medium">
              <RefreshCw className="w-3.5 h-3.5 md:w-4 md:h-4" />
              Refresh Data
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}