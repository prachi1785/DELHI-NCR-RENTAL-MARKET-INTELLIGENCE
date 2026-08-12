import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts';
import type { PropertyListing } from '../types';
import { getMedian, getMean, formatCurrency, formatCompactCurrency } from '../utils/mathUtils';
import { AlertCircle } from 'lucide-react';

interface MarketOverviewProps {
  filteredData: PropertyListing[];
}

const COLORS = ['#0f172a', '#334155', '#475569', '#64748b', '#94a3b8'];

export default function MarketOverview({ filteredData }: MarketOverviewProps) {
  // Compute KPI values
  const totalListings = filteredData.length;
  const rents = filteredData.map(item => item.monthly_rent);
  const sizes = filteredData.map(item => item.area_sqft);
  const sqftRents = filteredData.map(item => item.rent_per_sqft);
  const deposits = filteredData.map(item => item.security_deposit);

  const medianRent = getMedian(rents);
  const avgRent = getMean(rents);
  const medianSqftRent = getMedian(sqftRents);
  const avgSize = getMean(sizes);
  const medianDeposit = getMedian(deposits);

  // Chart 1: Median Rent by Locality (Top 10)
  const localityMedians = Array.from(new Set(filteredData.map(item => item.locality)))
    .map(loc => {
      const locListings = filteredData.filter(item => item.locality === loc);
      return {
        locality: loc,
        medianRent: getMedian(locListings.map(item => item.monthly_rent)),
        count: locListings.length
      };
    })
    .sort((a, b) => b.medianRent - a.medianRent)
    .slice(0, 10);

  // Chart 2: Rent Distribution (Histogram simulation)
  const bins = [0, 10000, 15000, 20000, 30000, 45000, 60000, 100000, 999999];
  const binLabels = ['<10k', '10k-15k', '15k-20k', '20k-30k', '30k-45k', '45k-60k', '60k-1L', '>1L'];
  const rentDist = binLabels.map((label, idx) => {
    const count = filteredData.filter(item => {
      const rent = item.monthly_rent;
      return rent >= bins[idx] && rent < bins[idx + 1];
    }).length;
    return { name: label, Listings: count };
  });

  // Chart 3: BHK Type Distribution
  const typeCounts = Array.from(new Set(filteredData.map(item => item.property_type)))
    .map(type => ({
      name: type,
      value: filteredData.filter(item => item.property_type === type).length
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  // Chart 4: Furnishing Distribution
  const furnishingCounts = Array.from(new Set(filteredData.map(item => item.furnishing_status)))
    .map(status => ({
      name: status,
      value: filteredData.filter(item => item.furnishing_status === status).length
    }));

  // Chart 5: City Comparisons
  const cityComparisons = Array.from(new Set(filteredData.map(item => item.city)))
    .map(city => {
      const cityListings = filteredData.filter(item => item.city === city);
      return {
        city: city,
        'Median Rent': getMedian(cityListings.map(item => item.monthly_rent)),
        'Avg Size (Sqft)': Math.round(getMean(cityListings.map(item => item.area_sqft)))
      };
    })
    .sort((a, b) => b['Median Rent'] - a['Median Rent']);

  const kpis = [
    { label: 'Total Listings', value: totalListings, subtext: 'Active in dataset' },
    { label: 'Median Monthly Rent', value: formatCurrency(medianRent), subtext: `Avg: ${formatCurrency(avgRent)}` },
    { label: 'Median Rent / Sq.Ft.', value: `₹${medianSqftRent.toFixed(1)}/sqft`, subtext: 'Carpet area basis' },
    { label: 'Average Property Size', value: `${Math.round(avgSize)} sqft`, subtext: 'Floor space average' },
    { label: 'Median Security Deposit', value: formatCurrency(medianDeposit), subtext: `~${(medianDeposit / (medianRent || 1)).toFixed(1)}x monthly rent` },
  ];

  if (totalListings === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 bg-white border border-slate-200 rounded shadow-xs">
        <AlertCircle className="w-8 h-8 text-slate-300 mb-2" />
        <h3 className="font-semibold text-slate-700 text-sm">No Listings Match Your Filters</h3>
        <p className="text-xs text-slate-450 mt-1">Try resetting the controls or broadening your search criteria.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-xs">
      {/* KPI Cards Grid */}
      <div className="bg-white border border-slate-200 rounded grid grid-cols-2 md:grid-cols-5 divide-y md:divide-y-0 md:divide-x divide-slate-200 shadow-xs">
        {kpis.map((kpi, idx) => (
          <div key={idx} className="p-4 flex flex-col justify-between">
            <span className="text-[10px] font-bold text-slate-450 uppercase tracking-wide block">{kpi.label}</span>
            <span className="text-xl font-bold text-slate-800 block mt-1">{kpi.value}</span>
            {kpi.subtext && <span className="text-[10px] text-slate-400 mt-0.5 block">{kpi.subtext}</span>}
          </div>
        ))}
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Locality Rents */}
        <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
          <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-4 border-b border-slate-50 pb-2">Top 10 Localities by Rent (Median)</h4>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={localityMedians} layout="vertical" margin={{ left: 50, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} vertical={true} stroke="#f1f5f9" />
                <XAxis type="number" tickFormatter={(v) => formatCompactCurrency(v)} stroke="#64748b" fontSize={10} />
                <YAxis dataKey="locality" type="category" stroke="#64748b" fontSize={10} width={100} />
                <Tooltip 
                  formatter={(value: any) => [formatCurrency(Number(value)), 'Median Rent']}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                />
                <Bar dataKey="medianRent" fill="#1e293b" radius={[0, 2, 2, 0]} barSize={14} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Rent Distribution */}
        <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
          <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-4 border-b border-slate-50 pb-2">Rent Distribution (Listings count)</h4>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rentDist} margin={{ bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                />
                <Bar dataKey="Listings" fill="#475569" radius={[2, 2, 0, 0]} barSize={26} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Secondary Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* BHK Splits */}
        <div className="bg-white p-5 border border-slate-200 rounded-lg shadow-sm flex flex-col justify-between">
          <h4 className="font-semibold text-slate-800 mb-2">BHK Type Distribution</h4>
          <div className="h-56 relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={typeCounts}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {typeCounts.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any) => [`${value} listings`]} />
              </PieChart>
            </ResponsiveContainer>
            {/* Center Summary */}
            <div className="absolute text-center">
              <span className="text-2xl font-bold text-slate-700">{totalListings}</span>
              <p className="text-[10px] uppercase font-semibold text-slate-400">Listings</p>
            </div>
          </div>
          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 mt-2">
            {typeCounts.map((entry, idx) => (
              <span key={idx} className="text-xs text-slate-600 flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                {entry.name} ({Math.round(entry.value / totalListings * 100)}%)
              </span>
            ))}
          </div>
        </div>

        {/* Furnishing status */}
        <div className="bg-white p-5 border border-slate-200 rounded-lg shadow-sm flex flex-col justify-between">
          <h4 className="font-semibold text-slate-800 mb-2">Furnishing Distribution</h4>
          <div className="h-56 relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={furnishingCounts}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {furnishingCounts.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any) => [`${value} listings`]} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute text-center font-bold text-slate-700 text-sm">
              Status Split
            </div>
          </div>
          <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 mt-2">
            {furnishingCounts.map((entry, idx) => (
              <span key={idx} className="text-xs text-slate-600 flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: COLORS[(idx + 2) % COLORS.length] }}></span>
                {entry.name} ({Math.round(entry.value / totalListings * 100)}%)
              </span>
            ))}
          </div>
        </div>

        {/* Regional Comparisons */}
        <div className="bg-white p-5 border border-slate-200 rounded-lg shadow-sm flex flex-col justify-between">
          <div>
            <h4 className="font-semibold text-slate-800 mb-3">Median Rent by City</h4>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cityComparisons}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="city" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={10} tickFormatter={(v) => formatCompactCurrency(v)} />
                  <Tooltip 
                    formatter={(value: any) => [formatCurrency(Number(value)), 'Median Rent']}
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                  />
                  <Bar dataKey="Median Rent" fill="#475569" radius={[2, 2, 0, 0]} barSize={18} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-100 flex justify-between items-center text-xs text-slate-500">
            <span>Highest: Gurugram</span>
            <span>Lowest: Greater Noida</span>
          </div>
        </div>
      </div>
    </div>
  );
}
