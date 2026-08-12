import { useState, useMemo } from 'react';
import type { PropertyListing, RenterSegment } from '../types';
import { getMedian, getMean, formatCurrency, formatDistance } from '../utils/mathUtils';
import { MapPin, Info, ArrowUpDown } from 'lucide-react';

interface LocationIntelligenceProps {
  filteredData: PropertyListing[];
}

type MapMetric = 'medianRent' | 'rentPerSqft' | 'valueScore' | 'avgSize' | 'medianMetroDistance';

const LOCALITY_COORDS: { [key: string]: { x: number; y: number; zone: string } } = {
  "Mukherjee Nagar": { x: 230, y: 70, zone: "North Delhi" },
  "Model Town": { x: 200, y: 90, zone: "North Delhi" },
  "Kamla Nagar": { x: 220, y: 110, zone: "North Delhi" },
  "Civil Lines": { x: 250, y: 100, zone: "North Delhi" },
  "Rohini": { x: 140, y: 90, zone: "North Delhi" },
  "Karol Bagh": { x: 210, y: 150, zone: "Central Delhi" },
  "Patel Nagar": { x: 180, y: 155, zone: "West Delhi" },
  "Rajinder Nagar": { x: 200, y: 165, zone: "Central Delhi" },
  "Janakpuri": { x: 120, y: 180, zone: "West Delhi" },
  "Laxmi Nagar": { x: 310, y: 160, zone: "East Delhi" },
  "Shakarpur": { x: 300, y: 175, zone: "East Delhi" },
  "Preet Vihar": { x: 330, y: 165, zone: "East Delhi" },
  "Mayur Vihar": { x: 320, y: 210, zone: "East Delhi" },
  "Saket": { x: 230, y: 310, zone: "South Delhi" },
  "Malviya Nagar": { x: 220, y: 285, zone: "South Delhi" },
  "Hauz Khas": { x: 210, y: 260, zone: "South Delhi" },
  "Green Park": { x: 195, y: 250, zone: "South Delhi" },
  "Greater Kailash": { x: 250, y: 275, zone: "South Delhi" },
  "Vasant Kunj": { x: 160, y: 295, zone: "South Delhi" },
  "Dwarka": { x: 90, y: 220, zone: "Dwarka" },
  "Noida Sector 62": { x: 410, y: 190, zone: "Noida" },
  "Noida Sector 15": { x: 350, y: 225, zone: "Noida" },
  "Noida Sector 137": { x: 430, y: 270, zone: "Noida" },
  "Pari Chowk": { x: 500, y: 330, zone: "Greater Noida" },
  "Knowledge Park": { x: 490, y: 305, zone: "Greater Noida" },
  "Indirapuram": { x: 390, y: 155, zone: "Ghaziabad" },
  "Vaishali": { x: 350, y: 145, zone: "Ghaziabad" },
  "DLF Phase 3": { x: 120, y: 320, zone: "Gurugram" },
  "Gurugram Sector 45": { x: 110, y: 350, zone: "Gurugram" },
  "Gurugram Sector 56": { x: 120, y: 380, zone: "Gurugram" },
  "Golf Course Road": { x: 140, y: 360, zone: "Gurugram" },
};

// Regional geographic boundary outlines in SVG (approximate nodes)
const ZONE_PATHS = [
  { name: 'North Delhi', d: 'M 130 50 L 270 50 L 260 120 L 130 120 Z', color: 'fill-slate-100/50' },
  { name: 'West Delhi & Dwarka', d: 'M 70 120 L 200 120 L 170 240 L 70 240 Z', color: 'fill-slate-100/50' },
  { name: 'Central & South Delhi', d: 'M 200 120 L 260 120 L 270 330 L 150 330 Z', color: 'fill-slate-100/50' },
  { name: 'East Delhi & Ghaziabad', d: 'M 270 125 L 430 125 L 370 230 L 270 230 Z', color: 'fill-slate-100/50' },
  { name: 'Noida & Greater Noida', d: 'M 350 230 L 530 230 L 530 350 L 350 350 Z', color: 'fill-slate-100/50' },
  { name: 'Gurugram', d: 'M 100 310 L 160 310 L 160 400 L 100 400 Z', color: 'fill-slate-100/50' },
];

export default function LocationIntelligence({ filteredData }: LocationIntelligenceProps) {
  const [selectedMetric, setSelectedMetric] = useState<MapMetric>('medianRent');
  const [selectedProfile, setSelectedProfile] = useState<RenterSegment>('Student');
  const [hoveredLocality, setHoveredLocality] = useState<string | null>(null);
  const [clickedLocality, setClickedLocality] = useState<string | null>(null);
  
  // Table sorting
  const [sortField, setSortField] = useState<string>('locality');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Compute locality summarized statistics
  const localityStats = useMemo(() => {
    const uniqueLocalities = Array.from(new Set(filteredData.map(item => item.locality)));
    return uniqueLocalities.map(loc => {
      const subset = filteredData.filter(item => item.locality === loc);
      const rents = subset.map(item => item.monthly_rent);
      const sizes = subset.map(item => item.area_sqft);
      const sqfts = subset.map(item => item.rent_per_sqft);
      const metros = subset.map(item => item.metro_distance_km);
      
      const vfmCol = selectedProfile === 'Student' ? 'vfm_student' 
                     : selectedProfile === 'Working Professional' ? 'vfm_professional'
                     : selectedProfile === 'Working Bachelor' ? 'vfm_bachelor' : 'vfm_family';
      const vfmScores = subset.map(item => item[vfmCol] as number);

      return {
        locality: loc,
        city: subset[0].city,
        zone: subset[0].zone,
        count: subset.length,
        medianRent: getMedian(rents),
        rentPerSqft: getMedian(sqfts),
        valueScore: Math.round(getMean(vfmScores)),
        avgSize: Math.round(getMean(sizes)),
        medianMetroDistance: getMedian(metros),
      };
    });
  }, [filteredData, selectedProfile]);

  // Handle table sorting
  const handleSort = (field: string) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const sortedLocalityStats = useMemo(() => {
    const sorted = [...localityStats];
    sorted.sort((a: any, b: any) => {
      let valA = a[sortField];
      let valB = b[sortField];
      
      if (typeof valA === 'string') {
        return sortDirection === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return sortDirection === 'asc' ? valA - valB : valB - valA;
    });
    return sorted;
  }, [localityStats, sortField, sortDirection]);

  // Map ranges for sizing and coloring bubbles
  const metricRanges = useMemo(() => {
    const values = localityStats.map(stat => stat[selectedMetric]);
    if (values.length === 0) return { min: 0, max: 1 };
    return {
      min: Math.min(...values),
      max: Math.max(...values)
    };
  }, [localityStats, selectedMetric]);

  // Helper to compute bubble styling (radius and color)
  const getBubbleProps = (val: number) => {
    const { min, max } = metricRanges;
    const diff = max - min || 1;
    const ratio = (val - min) / diff; // 0 to 1
    
    // Scale radius: 6px to 22px
    const radius = 6 + ratio * 14;
    
    // Scale color (gradient from slate-300 to slate-800, or emerald/amber/rose for value scores)
    let fill = '#475569'; // default slate
    if (selectedMetric === 'valueScore') {
      // Muted green/amber/red for scores
      fill = val >= 70 ? '#16a34a' : val >= 55 ? '#d97706' : '#dc2626';
    } else {
      // Slate scale: higher is dark charcoal, lower is light gray
      fill = ratio > 0.75 ? '#0f172a' : ratio > 0.5 ? '#334155' : ratio > 0.25 ? '#475569' : '#94a3b8';
    }
    
    return { radius, fill };
  };

  // Currently focused locality info card
  const focusedLocalityName = clickedLocality || hoveredLocality;
  const focusedLocalityData = useMemo(() => {
    if (!focusedLocalityName) return null;
    return localityStats.find(item => item.locality === focusedLocalityName);
  }, [focusedLocalityName, localityStats]);

  return (
    <div className="space-y-6">
      
      {/* Metrics Selector Row */}
      <div className="bg-white p-4 border border-slate-200 rounded-lg shadow-sm flex flex-wrap justify-between items-center gap-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mr-2">Visualize Metric:</span>
          {[
            { id: 'medianRent', label: 'Median Rent' },
            { id: 'rentPerSqft', label: 'Rent per Sq.Ft.' },
            { id: 'valueScore', label: 'Value Score' },
            { id: 'avgSize', label: 'Average Size' },
            { id: 'medianMetroDistance', label: 'Metro Proximity' },
          ].map(btn => (
            <button
              key={btn.id}
              onClick={() => setSelectedMetric(btn.id as MapMetric)}
              className={`text-xs px-3 py-1.5 rounded-md font-medium border transition-colors cursor-pointer ${
                selectedMetric === btn.id
                  ? 'bg-slate-900 border-slate-900 text-white'
                  : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {btn.label}
            </button>
          ))}
        </div>

        {selectedMetric === 'valueScore' && (
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Renter Profile:</span>
            <select
              value={selectedProfile}
              onChange={(e) => setSelectedProfile(e.target.value as RenterSegment)}
              className="text-xs py-1 px-3 border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="Student">Student</option>
              <option value="Working Professional">Working Professional</option>
              <option value="Working Bachelor">Working Bachelor</option>
              <option value="Family">Family</option>
            </select>
          </div>
        )}
      </div>

      {/* Main Map & Detail Panel Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Map Canvas */}
        <div className="lg:col-span-3 bg-white p-5 border border-slate-200 rounded-lg shadow-sm flex flex-col justify-between">
          <div>
            <h4 className="font-semibold text-slate-800 flex items-center gap-1.5">
              <MapPin className="w-4.5 h-4.5 text-indigo-600" />
              Delhi/NCR Regional Coordinate Plot
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">Hover or click locality bubbles to view statistics. Click map areas to filter locality list.</p>
          </div>

          <div className="relative border border-slate-100 rounded-lg bg-slate-50 mt-4 overflow-hidden flex items-center justify-center p-2">
            {/* SVG Interactive Canvas */}
            <svg 
              viewBox="0 0 600 420" 
              className="w-full max-w-2xl h-auto select-none"
            >
              {/* Regional Yamuna river graphic */}
              <path d="M 330 0 C 330 100 290 200 340 300 C 350 320 370 380 400 420" fill="none" stroke="#e0f2fe" strokeWidth="16" />
              <path d="M 330 0 C 330 100 290 200 340 300 C 350 320 370 380 400 420" fill="none" stroke="#bae6fd" strokeWidth="2" strokeDasharray="4 4" />

              {/* Draw Region Polygons */}
              {ZONE_PATHS.map((path, idx) => (
                <path
                  key={idx}
                  d={path.d}
                  className={`${path.color} stroke-slate-200 stroke-1 hover:fill-indigo-50/30 transition-all duration-200`}
                />
              ))}

              {/* Render Labels for Major Zones */}
              <text x="140" y="45" className="fill-slate-400 font-bold text-[9px] uppercase tracking-widest">North Delhi</text>
              <text x="75" y="145" className="fill-slate-400 font-bold text-[9px] uppercase tracking-widest">West/Dwarka</text>
              <text x="210" y="345" className="fill-slate-400 font-bold text-[9px] uppercase tracking-widest">South Delhi</text>
              <text x="315" y="120" className="fill-slate-400 font-bold text-[9px] uppercase tracking-widest">East/Ghaziabad</text>
              <text x="440" y="220" className="fill-slate-400 font-bold text-[9px] uppercase tracking-widest">Noida</text>
              <text x="440" y="360" className="fill-slate-400 font-bold text-[9px] uppercase tracking-widest">Greater Noida</text>
              <text x="75" y="385" className="fill-slate-400 font-bold text-[9px] uppercase tracking-widest">Gurugram</text>

              {/* Render Locality bubbles */}
              {localityStats.map((stat) => {
                const coord = LOCALITY_COORDS[stat.locality];
                if (!coord) return null;
                const { radius, fill } = getBubbleProps(stat[selectedMetric]);
                const isHovered = hoveredLocality === stat.locality;
                const isClicked = clickedLocality === stat.locality;

                return (
                  <g key={stat.locality}>
                    <circle
                      cx={coord.x}
                      cy={coord.y}
                      r={radius + 4}
                      className="fill-transparent stroke-transparent hover:stroke-indigo-400/30 hover:stroke-[8px] transition-all cursor-pointer"
                      onMouseEnter={() => setHoveredLocality(stat.locality)}
                      onMouseLeave={() => setHoveredLocality(null)}
                      onClick={() => setClickedLocality(isClicked ? null : stat.locality)}
                    />
                    <circle
                      cx={coord.x}
                      cy={coord.y}
                      r={radius}
                      fill={fill}
                      stroke={isClicked ? '#0f172a' : isHovered ? '#6366f1' : '#fff'}
                      strokeWidth={isClicked ? 2.5 : isHovered ? 2 : 1}
                      className="transition-all pointer-events-none shadow-sm"
                    />
                  </g>
                );
              })}
            </svg>
            
            {/* Map Legend */}
            <div className="absolute bottom-2 left-2 bg-white/95 backdrop-blur-sm border border-slate-200 rounded-md p-2 text-[10px] space-y-1">
              <span className="font-semibold block text-slate-700">Legend</span>
              <div className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full inline-block bg-indigo-200"></span>
                <span>Lower Values</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full inline-block bg-indigo-700"></span>
                <span>Higher Values</span>
              </div>
            </div>
          </div>
        </div>

        {/* Selected/Hovered Locality Info Card */}
        <div className="lg:col-span-1">
          {focusedLocalityData ? (
            <div className="bg-white p-5 border border-slate-200 rounded-lg shadow-sm h-full flex flex-col justify-between">
              <div>
                <div className="pb-3 border-b border-slate-100">
                  <span className="text-[10px] uppercase font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full inline-block">
                    {focusedLocalityData.zone}
                  </span>
                  <h4 className="font-bold text-slate-800 text-lg mt-1">{focusedLocalityData.locality}</h4>
                  <p className="text-xs text-slate-400">{focusedLocalityData.city}</p>
                </div>

                <div className="mt-4 space-y-3.5">
                  <div>
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block">Median rent</span>
                    <span className="text-xl font-bold text-slate-800">{formatCurrency(focusedLocalityData.medianRent)}</span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block">Rent per sqft</span>
                    <span className="text-sm font-semibold text-slate-700">₹{focusedLocalityData.rentPerSqft.toFixed(1)}/sqft</span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block">Average area size</span>
                    <span className="text-sm font-semibold text-slate-700">{focusedLocalityData.avgSize} sqft</span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block">Median metro distance</span>
                    <span className="text-sm font-semibold text-slate-700">{formatDistance(focusedLocalityData.medianMetroDistance)}</span>
                  </div>
                  <div className="p-3 bg-slate-50 border border-slate-150 rounded-md">
                    <span className="text-[10px] uppercase font-semibold text-slate-500 block">
                      VFM Value Score ({selectedProfile})
                    </span>
                    <span className="text-lg font-bold text-indigo-700 mt-0.5 block">
                      {focusedLocalityData.valueScore} <span className="text-xs font-normal text-slate-500">/ 100</span>
                    </span>
                  </div>
                </div>
              </div>

              <div className="text-[10px] text-slate-400 mt-4 leading-normal">
                Based on {focusedLocalityData.count} property listings in this locality.
              </div>
            </div>
          ) : (
            <div className="bg-slate-50 border border-dashed border-slate-300 rounded-lg p-6 h-full flex flex-col justify-center items-center text-center">
              <Info className="w-8 h-8 text-slate-400 mb-2" />
              <h5 className="font-semibold text-slate-700 text-sm">No Locality Selected</h5>
              <p className="text-xs text-slate-400 mt-1 max-w-[180px]">Hover or click a locality bubble on the map to display localized intelligence.</p>
            </div>
          )}
        </div>

      </div>

      {/* Comparison Grid Table */}
      <div className="bg-white p-5 border border-slate-200 rounded-lg shadow-sm">
        <h4 className="font-semibold text-slate-800 mb-4">Locality Metric Comparison Table</h4>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                {[
                  { field: 'locality', label: 'Locality' },
                  { field: 'city', label: 'City' },
                  { field: 'medianRent', label: 'Median Rent' },
                  { field: 'rentPerSqft', label: 'Rent/Sqft' },
                  { field: 'avgSize', label: 'Avg Size' },
                  { field: 'medianMetroDistance', label: 'Metro Dist' },
                  { field: 'valueScore', label: 'Value Score' },
                ].map(col => (
                  <th
                    key={col.field}
                    onClick={() => handleSort(col.field)}
                    className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100 transition-colors"
                  >
                    <div className="flex items-center gap-1">
                      {col.label}
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sortedLocalityStats.map(stat => (
                <tr
                  key={stat.locality}
                  onClick={() => setClickedLocality(clickedLocality === stat.locality ? null : stat.locality)}
                  className={`hover:bg-slate-50/80 cursor-pointer transition-colors ${
                    clickedLocality === stat.locality ? 'bg-indigo-50/40' : ''
                  }`}
                >
                  <td className="px-4 py-3 font-medium text-slate-800">{stat.locality}</td>
                  <td className="px-4 py-3 text-slate-500">{stat.city}</td>
                  <td className="px-4 py-3 font-semibold text-slate-700">{formatCurrency(stat.medianRent)}</td>
                  <td className="px-4 py-3 text-slate-600">₹{stat.rentPerSqft.toFixed(1)}/sqft</td>
                  <td className="px-4 py-3 text-slate-600">{stat.avgSize} sqft</td>
                  <td className="px-4 py-3 text-slate-600">{formatDistance(stat.medianMetroDistance)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                      stat.valueScore >= 70 ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' :
                      stat.valueScore >= 55 ? 'bg-amber-50 text-amber-700 border border-amber-100' :
                      'bg-rose-50 text-rose-700 border border-rose-100'
                    }`}>
                      {stat.valueScore}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
