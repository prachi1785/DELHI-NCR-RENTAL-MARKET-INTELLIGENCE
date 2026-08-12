import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, Cell } from 'recharts';
import type { PropertyListing } from '../types';
import { getMedian, formatCurrency, getPremiumPct } from '../utils/mathUtils';
import { Zap, HelpCircle, Sparkles, Navigation, Award } from 'lucide-react';

interface PriceDriversProps {
  filteredData: PropertyListing[];
}

export default function PriceDrivers({ filteredData }: PriceDriversProps) {
  // Compute premiums dynamically
  const acPremium = getPremiumPct(filteredData, 'ac');
  const parkingPremium = getPremiumPct(filteredData, 'parking');
  const wifiPremium = getPremiumPct(filteredData, 'wifi');
  const powerBackupPremium = getPremiumPct(filteredData, 'power_backup');
  
  // Furnishing Premium: Semi vs Unfurnished, Furnished vs Unfurnished
  const unfurnishedRents = filteredData.filter(i => i.furnishing_status === 'Unfurnished').map(i => i.monthly_rent);
  const semiRents = filteredData.filter(i => i.furnishing_status === 'Semi-Furnished').map(i => i.monthly_rent);
  const furnishedRents = filteredData.filter(i => i.furnishing_status === 'Furnished').map(i => i.monthly_rent);
  
  const medianUnfurnished = getMedian(unfurnishedRents);
  const medianSemi = getMedian(semiRents);
  const medianFurnished = getMedian(furnishedRents);
  
  const semiPremiumPct = medianUnfurnished > 0 ? ((medianSemi - medianUnfurnished) / medianUnfurnished * 100) : 0;
  const furnishedPremiumPct = medianUnfurnished > 0 ? ((medianFurnished - medianUnfurnished) / medianUnfurnished * 100) : 0;

  // Scatter plot data
  const scatterData = filteredData.map(item => ({
    x: item.area_sqft,
    y: item.monthly_rent,
    name: item.listing_title,
    locality: item.locality,
    bhk: item.property_type
  }));

  // Distances breakdown
  const metroBuckets = [
    { name: '< 500m', rent: getMedian(filteredData.filter(i => i.metro_distance_km <= 0.5).map(i => i.monthly_rent)) },
    { name: '500m - 1km', rent: getMedian(filteredData.filter(i => i.metro_distance_km > 0.5 && i.metro_distance_km <= 1.0).map(i => i.monthly_rent)) },
    { name: '1km - 2km', rent: getMedian(filteredData.filter(i => i.metro_distance_km > 1.0 && i.metro_distance_km <= 2.0).map(i => i.monthly_rent)) },
    { name: '> 2km', rent: getMedian(filteredData.filter(i => i.metro_distance_km > 2.0).map(i => i.monthly_rent)) },
  ].filter(b => b.rent > 0);

  // Office proximity breakdown (not visualized in charts, removed)

  // Generate dynamic insights
  const insights = [];
  if (filteredData.length > 0) {
    if (parkingPremium > 0) {
      insights.push({
        title: 'Parking Rental Premium',
        desc: `Properties offering dedicated parking spots command a median rent premium of ${parkingPremium.toFixed(1)}% compared to those without.`,
        icon: Award,
        color: 'border-emerald-200 bg-emerald-50 text-emerald-800'
      });
    }
    if (acPremium > 0) {
      insights.push({
        title: 'AC Premium',
        desc: `Air conditioning availability is associated with a ${acPremium.toFixed(1)}% premium in monthly rent, reflecting high summer demand in the NCR region.`,
        icon: Zap,
        color: 'border-indigo-200 bg-indigo-50 text-indigo-800'
      });
    }
    if (furnishedPremiumPct > 0) {
      insights.push({
        title: 'Furnishing Upgrade Value',
        desc: `Fully Furnished flats carry a ${furnishedPremiumPct.toFixed(1)}% markup over Unfurnished units, while Semi-Furnished properties carry a ${semiPremiumPct.toFixed(1)}% markup.`,
        icon: Sparkles,
        color: 'border-amber-200 bg-amber-50 text-amber-800'
      });
    }
    if (metroBuckets.length >= 2) {
      const nearMetro = metroBuckets[0].rent;
      const farMetro = metroBuckets[metroBuckets.length - 1].rent;
      const diffPct = ((nearMetro - farMetro) / farMetro * 100);
      if (diffPct > 0) {
        insights.push({
          title: 'Metro Proximity Impact',
          desc: `Properties within 500m of a metro station command ${diffPct.toFixed(1)}% higher median rent compared to properties located more than 2km away.`,
          icon: Navigation,
          color: 'border-rose-200 bg-rose-50 text-rose-800'
        });
      }
    }
  }

  // Premium metrics graph data
  const premiumChartData = [
    { name: 'Parking Premium', value: Math.round(parkingPremium) },
    { name: 'AC Premium', value: Math.round(acPremium) },
    { name: 'Power Backup', value: Math.round(powerBackupPremium) },
    { name: 'WiFi Premium', value: Math.round(wifiPremium) },
  ].filter(p => p.value !== 0);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
      {/* Left Columns - Charts */}
      <div className="xl:col-span-3 space-y-6">
        
        {/* Rent vs Area Size */}
        <div className="bg-white p-5 border border-slate-200 rounded-lg shadow-sm">
          <h4 className="font-semibold text-slate-800 mb-2">Rent vs. Property Size (Carpet Area)</h4>
          <p className="text-xs text-slate-500 mb-4">Each point represents a listing. Rents increase with size, showing a strong positive correlation.</p>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" dataKey="x" name="Area" unit=" sqft" stroke="#64748b" fontSize={11} />
                <YAxis type="number" dataKey="y" name="Rent" unit=" ₹" stroke="#64748b" fontSize={11} tickFormatter={(v) => formatCurrency(v).replace('₹', '')} />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white p-3 border border-slate-200 rounded shadow-xs text-xs">
                          <p className="font-semibold text-slate-850">{data.name}</p>
                          <p className="text-slate-500 mt-1">Locality: {data.locality}</p>
                          <p className="text-slate-850 font-semibold">Rent: {formatCurrency(data.y)}</p>
                          <p className="text-slate-600">Size: {data.x} sqft</p>
                          <p className="text-slate-600">Type: {data.bhk}</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter name="Properties" data={scatterData} fill="#334155" opacity={0.5} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Proximity and Amenity row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Proximity charts */}
          <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
            <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-4 border-b border-slate-50 pb-2">Rent by Metro Distance (Median)</h4>
            <div className="h-64 text-xs">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metroBuckets}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={10} tickFormatter={(v) => formatCurrency(v).replace('₹', '')} />
                  <Tooltip formatter={(value: any) => [formatCurrency(Number(value)), 'Median Rent']} />
                  <Bar dataKey="rent" fill="#475569" radius={[2, 2, 0, 0]} barSize={26} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Premium values */}
          <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
            <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-4 border-b border-slate-50 pb-2">Amenity Rental Premiums (%)</h4>
            <div className="h-64 text-xs">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={premiumChartData} layout="vertical" margin={{ left: 30 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} vertical={true} stroke="#f1f5f9" />
                  <XAxis type="number" unit="%" stroke="#64748b" fontSize={10} />
                  <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={10} width={90} />
                  <Tooltip formatter={(value: any) => [`${value}%`, 'Rent Premium']} />
                  <Bar dataKey="value" fill="#334155" radius={[0, 2, 2, 0]} barSize={12}>
                    {premiumChartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill="#334155" opacity={1 - index * 0.15} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>

      </div>

      {/* Right Column - Insights Sidebar */}
      <div className="xl:col-span-1 space-y-6">
        <div className="bg-white p-4 border border-slate-200 rounded shadow-xs h-full flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-slate-150">
              <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider">Dynamic Insights</h3>
            </div>
            
            {insights.length === 0 ? (
              <div className="text-center py-10 text-xs">
                <HelpCircle className="w-6 h-6 text-slate-300 mx-auto mb-2" />
                <p className="text-slate-500">Not enough data to calculate pricing premiums under current filters.</p>
              </div>
            ) : (
              <div className="space-y-4 text-xs">
                {insights.map((insight, idx) => {
                  const Icon = insight.icon;
                  return (
                    <div key={idx} className="p-3.5 border border-slate-200 rounded bg-slate-50/50 flex gap-3">
                      <Icon className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
                      <div>
                        <h5 className="font-bold text-slate-800 text-xs">{insight.title}</h5>
                        <p className="text-[11px] text-slate-550 mt-1 leading-relaxed">{insight.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
          
          <div className="mt-6 pt-4 border-t border-slate-100 text-[10px] text-slate-400 leading-normal">
            *Premium estimates calculated via median rents of filtered populations. Standard deviations apply. Correlation does not imply direct causality.
          </div>
        </div>
      </div>
    </div>
  );
}
