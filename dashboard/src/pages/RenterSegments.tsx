import { useMemo } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import type { PropertyListing } from '../types';
import { getMedian, getMean, formatCurrency } from '../utils/mathUtils';
import { GraduationCap, Briefcase, User, Users } from 'lucide-react';

interface RenterSegmentsProps {
  filteredData: PropertyListing[];
}

export default function RenterSegments({ filteredData }: RenterSegmentsProps) {
  // Extract and summarize statistics for each segment
  const segmentSummaries = useMemo(() => {
    const segments = ['Student', 'Working Professional', 'Working Bachelor', 'Family'];
    return segments.map(seg => {
      // Find listings belonging to this segment
      const subset = filteredData.filter(item => item.renter_segment === seg);
      const rents = subset.map(item => item.monthly_rent);
      const sizes = subset.map(item => item.area_sqft);
      const metros = subset.map(item => item.metro_distance_km);
      
      const vfmCol = seg === 'Student' ? 'vfm_student' 
                     : seg === 'Working Professional' ? 'vfm_professional'
                     : seg === 'Working Bachelor' ? 'vfm_bachelor' : 'vfm_family';
      const vfmScores = subset.map(item => item[vfmCol] as number);

      // Find typical property layout
      const types = subset.map(item => item.property_type);
      const typicalType = types.length > 0 
        ? types.reduce((a, b, _, arr) => arr.filter(v => v === a).length >= arr.filter(v => v === b).length ? a : b)
        : 'N/A';

      // Find typical furnishing status
      const furnishing = subset.map(item => item.furnishing_status);
      const typicalFurnishing = furnishing.length > 0
        ? furnishing.reduce((a, b, _, arr) => arr.filter(v => v === a).length >= arr.filter(v => v === b).length ? a : b)
        : 'N/A';

      return {
        segment: seg,
        listingsCount: subset.length,
        medianRent: getMedian(rents),
        avgSize: Math.round(getMean(sizes)),
        medianMetroDistance: getMedian(metros),
        avgValueScore: Math.round(getMean(vfmScores)),
        typicalType,
        typicalFurnishing
      };
    });
  }, [filteredData]);

  // Data for Grouped Bar Charts
  const chartData = segmentSummaries.map(s => ({
    name: s.segment,
    'Median Rent': s.medianRent,
    'Avg Size (sqft)': s.avgSize,
    'Avg Value Score': s.avgValueScore,
  }));

  // Weights breakdown for Radar chart comparison
  // Showcases the decision framework of each segment
  const radarData = [
    { subject: 'Affordability', Student: 30, Professional: 20, Bachelor: 30, Family: 20 },
    { subject: 'Metro Proximity', Student: 25, Professional: 25, Bachelor: 25, Family: 10 },
    { subject: 'Dest Proximity', Student: 20, Professional: 25, Bachelor: 15, Family: 35 }, // College/Office/School+Hospital
    { subject: 'Amenities', Student: 15, Professional: 15, Bachelor: 15, Family: 15 },
    { subject: 'Safety', Student: 10, Professional: 15, Bachelor: 15, Family: 20 },
  ];

  // Helper icons for segment summaries
  const segmentMetadata: { [key: string]: { icon: any; color: string; desc: string } } = {
    'Student': {
      icon: GraduationCap,
      color: 'bg-indigo-50 border-indigo-100 text-indigo-700',
      desc: 'Prioritize affordability, high speed WiFi, proximity to North Campus or Knowledge Parks, and ready-to-move-in furnished rooms.'
    },
    'Working Professional': {
      icon: Briefcase,
      color: 'bg-emerald-50 border-emerald-100 text-emerald-700',
      desc: 'Focus on office connectivity (Gurugram/Noida Expressway), high-quality societies, power backup, lifts, and security.'
    },
    'Working Bachelor': {
      icon: User,
      color: 'bg-amber-50 border-amber-100 text-amber-700',
      desc: 'Seek affordable, flexible layouts (1RK/1BHK), proximity to metro routes, and bachelor-friendly rental terms.'
    },
    'Family': {
      icon: Users,
      color: 'bg-pink-50 border-pink-100 text-pink-700',
      desc: 'Demand spacious layout (2BHK/3BHK), green environments, access to school buses, nearby hospital corridors, and dedicated parking.'
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Comparative Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {segmentSummaries.map(summary => {
          const meta = segmentMetadata[summary.segment];
          const Icon = meta.icon;

          return (
            <div key={summary.segment} className="bg-white border border-slate-200 rounded-lg shadow-sm p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <span className="font-bold text-slate-800 text-base">{summary.segment}</span>
                  <span className={`p-2 rounded-lg border ${meta.color}`}>
                    <Icon className="w-5 h-5" />
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed h-12 overflow-hidden">{meta.desc}</p>
                
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Median Rent:</span>
                    <span className="font-bold text-slate-700">{formatCurrency(summary.medianRent)}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Typical Layout:</span>
                    <span className="font-bold text-indigo-600">{summary.typicalType}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Avg Area Size:</span>
                    <span className="font-bold text-slate-700">{summary.avgSize} sqft</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Typical Furnishing:</span>
                    <span className="font-bold text-slate-700">{summary.typicalFurnishing}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Metro distance:</span>
                    <span className="font-bold text-slate-700">{summary.medianMetroDistance.toFixed(2)} km</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center bg-slate-50 p-2.5 rounded-md">
                <span className="text-[10px] uppercase font-bold text-slate-400">Average Value Score</span>
                <span className="font-bold text-indigo-700 text-sm">{summary.avgValueScore || 0} / 100</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Segment charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Median Rent and Size comparisons */}
        <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
          <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-4 border-b border-slate-50 pb-2">Renter Segment Rental Comparisons</h4>
          <div className="h-80 text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} tickFormatter={(v) => formatCurrency(v).replace('₹', '')} />
                <Tooltip formatter={(value: any) => [formatCurrency(Number(value)), 'Median Rent']} />
                <Bar dataKey="Median Rent" fill="#1e293b" radius={[2, 2, 0, 0]} barSize={26} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Radar Charts of Weights */}
        <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
          <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-2 border-b border-slate-50 pb-2">Weight Framework Comparison (%)</h4>
          <p className="text-[10px] text-slate-400 mb-4">Illustrates how parameters are weighted in scoring value-for-money across profiles.</p>
          <div className="h-80 flex items-center justify-center text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="subject" stroke="#64748b" fontSize={10} />
                <PolarRadiusAxis angle={30} domain={[0, 40]} stroke="#cbd5e1" fontSize={8} />
                <Radar name="Student" dataKey="Student" stroke="#0f172a" fill="#0f172a" fillOpacity={0.05} />
                <Radar name="Professional" dataKey="Professional" stroke="#334155" fill="#334155" fillOpacity={0.05} />
                <Radar name="Bachelor" dataKey="Bachelor" stroke="#475569" fill="#475569" fillOpacity={0.05} />
                <Radar name="Family" dataKey="Family" stroke="#94a3b8" fill="#94a3b8" fillOpacity={0.05} />
                <Legend iconSize={8} wrapperStyle={{ fontSize: '10px' }} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

    </div>
  );
}
