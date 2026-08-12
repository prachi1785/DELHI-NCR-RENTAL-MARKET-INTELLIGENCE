import { useState, useMemo } from 'react';
import type { PropertyListing } from '../types';
import { getMedian, getMean, formatCurrency, formatDistance } from '../utils/mathUtils';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Columns } from 'lucide-react';

interface LocalityComparisonProps {
  listings: PropertyListing[];
}

export default function LocalityComparison({ listings }: LocalityComparisonProps) {
  // Get all unique localities
  const localities = Array.from(new Set(listings.map(item => item.locality))).sort();

  // Selected localities state
  const [localityA, setLocalityA] = useState<string>('Dwarka');
  const [localityB, setLocalityB] = useState<string>('Laxmi Nagar');
  const [localityC, setLocalityC] = useState<string>('Noida Sector 62');

  // Compute stats helper
  const getLocalityStats = (locName: string) => {
    const subset = listings.filter(item => item.locality === locName);
    if (subset.length === 0) return null;
    
    const rents = subset.map(item => item.monthly_rent);
    const sizes = subset.map(item => item.area_sqft);
    const sqfts = subset.map(item => item.rent_per_sqft);
    const metros = subset.map(item => item.metro_distance_km);
    const deposits = subset.map(item => item.security_deposit);
    
    // Average scores
    const studentVfm = subset.map(item => item.vfm_student);
    const profVfm = subset.map(item => item.vfm_professional);
    const familyVfm = subset.map(item => item.vfm_family);

    // Percentage offering parking and lift
    const parkingCount = subset.filter(item => item.parking === 'Yes').length;
    const liftCount = subset.filter(item => item.lift === 'Yes').length;
    const powerBackupCount = subset.filter(item => item.power_backup === 'Yes').length;

    return {
      locality: locName,
      city: subset[0].city,
      count: subset.length,
      medianRent: getMedian(rents),
      rentPerSqft: getMedian(sqfts),
      avgSize: Math.round(getMean(sizes)),
      medianMetroDistance: getMedian(metros),
      medianDeposit: getMedian(deposits),
      vfmStudent: Math.round(getMean(studentVfm)),
      vfmProfessional: Math.round(getMean(profVfm)),
      vfmFamily: Math.round(getMean(familyVfm)),
      parkingPct: Math.round(parkingCount / subset.length * 100),
      liftPct: Math.round(liftCount / subset.length * 100),
      powerBackupPct: Math.round(powerBackupCount / subset.length * 100),
    };
  };

  // Compile stats for selections
  const statsA = useMemo(() => getLocalityStats(localityA), [listings, localityA]);
  const statsB = useMemo(() => getLocalityStats(localityB), [listings, localityB]);
  const statsC = useMemo(() => getLocalityStats(localityC), [listings, localityC]);

  const activeStatsList = useMemo(() => {
    const list = [];
    if (statsA) list.push(statsA);
    if (statsB) list.push(statsB);
    if (statsC) list.push(statsC);
    return list;
  }, [statsA, statsB, statsC]);

  // Grouped Bar chart data
  const chartData = useMemo(() => {
    return activeStatsList.map(s => ({
      name: s.locality,
      'Median Rent (₹)': s.medianRent,
      'Avg Size (sqft)': s.avgSize,
      'VFM Student': s.vfmStudent,
      'VFM Family': s.vfmFamily,
    }));
  }, [activeStatsList]);

  return (
    <div className="space-y-6">
      
      {/* Selection row */}
      <div className="bg-white p-5 border border-slate-200 rounded-lg shadow-sm">
        <h3 className="font-bold text-slate-800 flex items-center gap-2 mb-4 pb-2 border-b border-slate-100">
          <Columns className="w-5 h-5 text-indigo-600" />
          Locality Comparison Setup
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Locality A</label>
            <select
              value={localityA}
              onChange={(e) => setLocalityA(e.target.value)}
              className="w-full text-sm py-2 px-3 border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 font-semibold"
            >
              {localities.map(loc => (
                <option key={loc} value={loc} disabled={loc === localityB || loc === localityC}>{loc}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1.5">Locality B</label>
            <select
              value={localityB}
              onChange={(e) => setLocalityB(e.target.value)}
              className="w-full text-xs py-1.5 px-2.5 border border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:border-slate-400"
            >
              {localities.map(loc => (
                <option key={loc} value={loc} disabled={loc === localityA || loc === localityC}>{loc}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1.5">Locality C (Optional)</label>
            <select
              value={localityC}
              onChange={(e) => setLocalityC(e.target.value)}
              className="w-full text-xs py-1.5 px-2.5 border border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:border-slate-400"
            >
              <option value="">-- None Selected --</option>
              {localities.map(loc => (
                <option key={loc} value={loc} disabled={loc === localityA || loc === localityB}>{loc}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Comparisons Grid */}
      <div className="bg-white border border-slate-200 rounded shadow-xs overflow-hidden">
        <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider p-4 border-b border-slate-100">Locality Characteristics Table</h4>
        <div className="overflow-x-auto text-xs">
          <table className="min-w-full text-xs divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-2.5 text-left text-[10px] font-bold text-slate-500 uppercase tracking-wider">Metrics</th>
                {activeStatsList.map(s => (
                  <th key={s.locality} className="px-4 py-2.5 text-left text-[10px] font-bold text-slate-800 uppercase tracking-wider">
                    {s.locality} ({s.city})
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr>
                <td className="px-4 py-2 font-medium text-slate-500">Median Rent</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-4 py-2 font-bold text-slate-800">{formatCurrency(s.medianRent)}</td>
                ))}
              </tr>
              <tr>
                <td className="px-4 py-2 font-medium text-slate-500">Rent per Sq.Ft.</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-4 py-2 text-slate-700">₹{s.rentPerSqft.toFixed(1)}/sqft</td>
                ))}
              </tr>
              <tr>
                <td className="px-4 py-2 font-medium text-slate-500">Average Unit Size</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-4 py-2 text-slate-700">{s.avgSize} sqft</td>
                ))}
              </tr>
              <tr>
                <td className="px-4 py-2 font-medium text-slate-500">Median Metro Distance</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-4 py-2 text-slate-700">{formatDistance(s.medianMetroDistance)}</td>
                ))}
              </tr>
              <tr>
                <td className="px-4 py-2 font-medium text-slate-500">Median Security Deposit</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-4 py-2 text-slate-700">{formatCurrency(s.medianDeposit)}</td>
                ))}
              </tr>
              <tr className="bg-slate-50/40">
                <td className="px-4 py-2 font-bold text-slate-550">VFM Score: Student</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-4 py-2 font-bold text-slate-800">{s.vfmStudent} <span className="text-[10px] font-normal text-slate-400">/ 100</span></td>
                ))}
              </tr>
              <tr className="bg-slate-50/40">
                <td className="px-4 py-2 font-bold text-slate-550">VFM Score: Professional</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-4 py-2 font-bold text-slate-800">{s.vfmProfessional} <span className="text-[10px] font-normal text-slate-400">/ 100</span></td>
                ))}
              </tr>
              <tr className="bg-slate-50/40">
                <td className="px-4 py-2 font-bold text-slate-550">VFM Score: Family</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-4 py-2 font-bold text-slate-800">{s.vfmFamily} <span className="text-[10px] font-normal text-slate-400">/ 100</span></td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-3.5 font-medium text-slate-500">Parking Spot Availability</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-6 py-3.5 text-slate-600">{s.parkingPct}% of listings</td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-3.5 font-medium text-slate-500">Elevator / Lift Presence</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-6 py-3.5 text-slate-600">{s.liftPct}% of listings</td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-3.5 font-medium text-slate-500">Power Backup Presence</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-6 py-3.5 text-slate-600">{s.powerBackupPct}% of listings</td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-3.5 font-medium text-slate-500">Sample Count</td>
                {activeStatsList.map(s => (
                  <td key={s.locality} className="px-6 py-3.5 text-slate-400">{s.count} listings</td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Comparison Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rent Comparisons */}
        <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
          <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-4 border-b border-slate-50 pb-2">Rent & Size Profile side-by-side</h4>
          <div className="h-64 text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} tickFormatter={(v) => formatCurrency(v).replace('₹', '')} />
                <Tooltip />
                <Legend iconSize={8} wrapperStyle={{ fontSize: '10px' }} />
                <Bar dataKey="Median Rent (₹)" fill="#1e293b" radius={[2, 2, 0, 0]} barSize={20} />
                <Bar dataKey="Avg Size (sqft)" fill="#475569" radius={[2, 2, 0, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Score comparison */}
        <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
          <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-4 border-b border-slate-50 pb-2">Value score comparisons</h4>
          <div className="h-64 text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                <YAxis domain={[0, 100]} stroke="#64748b" fontSize={10} />
                <Tooltip />
                <Legend iconSize={8} wrapperStyle={{ fontSize: '10px' }} />
                <Bar dataKey="VFM Student" fill="#334155" radius={[2, 2, 0, 0]} barSize={20} />
                <Bar dataKey="VFM Family" fill="#94a3b8" radius={[2, 2, 0, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

    </div>
  );
}
