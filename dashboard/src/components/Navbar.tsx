import { Home, TrendingUp, Map, Users, Search, Columns, Info } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function Navbar({ activeTab, setActiveTab }: NavbarProps) {
  const navItems = [
    { id: 'overview', name: 'Market Overview', icon: Home },
    { id: 'drivers', name: 'Price Drivers', icon: TrendingUp },
    { id: 'location', name: 'Location Intelligence', icon: Map },
    { id: 'renter', name: 'Renter Segments', icon: Users },
    { id: 'find', name: 'Find Your Rental', icon: Search },
    { id: 'compare', name: 'Compare Localities', icon: Columns },
    { id: 'transparency', name: 'Data & Methodology', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
                <span className="h-6 w-1.5 rounded-full bg-indigo-600 inline-block"></span>
                Delhi/NCR Rental Intelligence
              </span>
            </div>
            <nav className="hidden md:ml-8 md:flex md:space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150 whitespace-nowrap gap-2 ${
                      isActive
                        ? 'bg-slate-100 text-indigo-700 font-semibold'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                    {item.name}
                  </button>
                );
              })}
            </nav>
          </div>
          
          <div className="flex items-center md:hidden">
            {/* Mobile Nav Select */}
            <select
              value={activeTab}
              onChange={(e) => setActiveTab(e.target.value)}
              className="block w-full py-1.5 pl-3 pr-10 text-sm border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {navItems.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </header>
  );
}
