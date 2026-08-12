import { Home, TrendingUp, Map, Users, Search, Columns, Info } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  listingsCount: number;
}

export default function Sidebar({ activeTab, setActiveTab, listingsCount }: SidebarProps) {
  const navItems = [
    { id: 'overview', name: 'Overview', icon: Home },
    { id: 'drivers', name: 'Price Drivers', icon: TrendingUp },
    { id: 'location', name: 'Location Intelligence', icon: Map },
    { id: 'renter', name: 'Renter Segments', icon: Users },
    { id: 'find', name: 'Find Your Rental', icon: Search },
    { id: 'compare', name: 'Locality Comparison', icon: Columns },
    { id: 'transparency', name: 'Methodology', icon: Info },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 flex-shrink-0 hidden md:flex">
      {/* Brand Label */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-2.5">
        <span className="h-5 w-1 bg-indigo-500 rounded-sm"></span>
        <div className="flex flex-col">
          <span className="font-bold text-sm text-white tracking-wide uppercase">Delhi/NCR Rental</span>
          <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Market Intelligence</span>
        </div>
      </div>

      {/* Nav List */}
      <nav className="flex-1 py-4 px-4 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center px-3.5 py-2.5 text-xs font-medium rounded transition-colors duration-150 gap-2.5 cursor-pointer ${
                isActive
                  ? 'bg-slate-800 text-white font-semibold'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
              {item.name}
            </button>
          );
        })}
      </nav>

      {/* Metadata Bottom panel */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-[10px] text-slate-500 space-y-1.5">
        <div className="flex justify-between">
          <span>Listings Analyzed:</span>
          <span className="font-bold text-slate-350">{listingsCount}</span>
        </div>
        <div className="flex justify-between">
          <span>Data Period:</span>
          <span className="text-slate-450 font-medium">Q3 2026</span>
        </div>
        <div className="flex justify-between">
          <span>Last Updated:</span>
          <span className="text-slate-450">Aug 2026</span>
        </div>
      </div>
    </aside>
  );
}
