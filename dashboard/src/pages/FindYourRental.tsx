import { useState, useMemo } from 'react';
import type { PropertyListing, RenterSegment } from '../types';
import { formatCurrency, formatDistance } from '../utils/mathUtils';
import { Search, AlertCircle, HelpCircle, MapPin, Award, Shield, Wifi, Snowflake, Info, Compass } from 'lucide-react';

interface FindYourRentalProps {
  listings: PropertyListing[];
}

export default function FindYourRental({ listings }: FindYourRentalProps) {
  // Recommendation States
  const [profile, setProfile] = useState<RenterSegment>('Student');
  const [minRent, setMinRent] = useState<number>(8000);
  const [maxRent, setMaxRent] = useState<number>(30000);
  const [bhkType, setBhkType] = useState<string>('All');
  const [furnishing, setFurnishing] = useState<string>('All');
  const [metroDistLimit, setMetroDistLimit] = useState<string>('All');
  
  // Selected Amenities Checklist
  const [selectedAmenities, setSelectedAmenities] = useState<{ [key: string]: boolean }>({
    ac: false,
    wifi: false,
    parking: false,
    security: false,
    power_backup: false,
    gym: false,
    food: false,
  });

  // Selected Property for detailed modal
  const [detailedProperty, setDetailedProperty] = useState<(PropertyListing & { totalMonthlyCost: number }) | null>(null);

  // Toggle Amenity Checkbox
  const handleAmenityToggle = (amenity: string) => {
    setSelectedAmenities(prev => ({
      ...prev,
      [amenity]: !prev[amenity]
    }));
  };

  // Run matching and recommendation algorithm
  const recommendedProperties = useMemo(() => {
    return listings
      .filter(item => {
        // 1. Budget Filter
        if (item.monthly_rent < minRent || item.monthly_rent > maxRent) return false;
        
        // 2. BHK Type
        if (bhkType !== 'All' && item.property_type !== bhkType) return false;
        
        // 3. Furnishing Status
        if (furnishing !== 'All' && item.furnishing_status !== furnishing) return false;
        
        // 4. Metro Distance
        if (metroDistLimit !== 'All') {
          const dist = item.metro_distance_km;
          if (metroDistLimit === '<500m' && dist > 0.5) return false;
          if (metroDistLimit === '<1km' && dist > 1.0) return false;
          if (metroDistLimit === '<2km' && dist > 2.0) return false;
        }

        // 5. Amenities checklist matching
        if (selectedAmenities.ac && item.ac !== 'Yes') return false;
        if (selectedAmenities.wifi && item.wifi !== 'Yes') return false;
        if (selectedAmenities.parking && item.parking !== 'Yes') return false;
        if (selectedAmenities.security && item.security !== 'Yes') return false;
        if (selectedAmenities.power_backup && item.power_backup !== 'Yes') return false;
        if (selectedAmenities.gym && item.gym !== 'Yes') return false;
        if (selectedAmenities.food && item.food !== 'Yes') return false;

        return true;
      })
      .map(item => {
        // Map target value score column
        const scoreCol = profile === 'Student' ? 'vfm_student'
                        : profile === 'Working Professional' ? 'vfm_professional'
                        : profile === 'Working Bachelor' ? 'vfm_bachelor' : 'vfm_family';
        
        // Calculate Total Monthly Cost
        // Rent + Maintenance + Electricity + internet (₹800 flat)
        const totalMonthlyCost = item.monthly_rent + item.maintenance + item.electricity_estimate + 800;

        return {
          ...item,
          targetScore: item[scoreCol] as number,
          totalMonthlyCost
        };
      })
      .sort((a, b) => b.targetScore - a.targetScore);
  }, [listings, profile, minRent, maxRent, bhkType, furnishing, metroDistLimit, selectedAmenities]);

  // Aggregate matches by locality
  const topLocalities = useMemo(() => {
    const locMap: { [key: string]: { locality: string; city: string; count: number; avgScore: number } } = {};
    recommendedProperties.forEach(item => {
      if (!locMap[item.locality]) {
        locMap[item.locality] = { locality: item.locality, city: item.city, count: 0, avgScore: 0 };
      }
      locMap[item.locality].count += 1;
      locMap[item.locality].avgScore += item.targetScore;
    });

    return Object.values(locMap)
      .map(item => ({
        ...item,
        avgScore: Math.round(item.avgScore / item.count)
      }))
      .sort((a, b) => b.avgScore - a.avgScore)
      .slice(0, 5);
  }, [recommendedProperties]);

  return (
    <div className="space-y-6">
      
      {/* Search Config Panel */}
      <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
        <h3 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-4 pb-2 border-b border-slate-100 flex items-center gap-2">
          <Search className="w-4 h-4 text-slate-550" />
          Your Requirements
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
          {/* Renter Profile Select */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Who are you? (Renter Profile)
            </label>
            <select
              value={profile}
              onChange={(e) => setProfile(e.target.value as RenterSegment)}
              className="w-full text-sm py-2 px-3 border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 font-medium"
            >
              <option value="Student">Student (Colleges, Wifi, Budget)</option>
              <option value="Working Professional">Working Professional (Offices, Commute, Society)</option>
              <option value="Working Bachelor">Working Bachelor (Budget, Connectivity, Flex)</option>
              <option value="Family">Family (Space, Schools, Hospitals, Parking)</option>
            </select>
          </div>

          {/* Budget Min/Max Number inputs */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Rent Budget Range (₹)
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                value={minRent}
                onChange={(e) => setMinRent(Number(e.target.value))}
                placeholder="Min"
                className="w-1/2 text-sm py-2 px-3 border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <span className="text-slate-400 self-center">-</span>
              <input
                type="number"
                value={maxRent}
                onChange={(e) => setMaxRent(Number(e.target.value))}
                placeholder="Max"
                className="w-1/2 text-sm py-2 px-3 border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 font-semibold"
              />
            </div>
          </div>

          {/* BHK Format */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              BHK Format
            </label>
            <select
              value={bhkType}
              onChange={(e) => setBhkType(e.target.value)}
              className="w-full text-sm py-2 px-3 border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="All">Any Layout</option>
              <option value="1RK">1 RK</option>
              <option value="1BHK">1 BHK</option>
              <option value="2BHK">2 BHK</option>
              <option value="3BHK">3 BHK</option>
              <option value="4BHK">4 BHK</option>
            </select>
          </div>

          {/* Furnishing select */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Furnishing
            </label>
            <select
              value={furnishing}
              onChange={(e) => setFurnishing(e.target.value)}
              className="w-full text-sm py-2 px-3 border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 font-semibold"
            >
              <option value="All">Any Furnishing</option>
              <option value="Furnished">Furnished</option>
              <option value="Semi-Furnished">Semi-Furnished</option>
              <option value="Unfurnished">Unfurnished</option>
            </select>
          </div>

          {/* Metro Distance */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Metro Distance
            </label>
            <select
              value={metroDistLimit}
              onChange={(e) => setMetroDistLimit(e.target.value)}
              className="w-full text-sm py-2 px-3 border border-slate-300 rounded-md focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="All">No Proximity Limit</option>
              <option value="<500m">Within 500m (&lt;500m)</option>
              <option value="<1km">Within 1km (&lt;1.0 km)</option>
              <option value="<2km">Within 2km (&lt;2.0 km)</option>
            </select>
          </div>
        </div>

        {/* Amenities Checklist */}
        <div className="mt-6 pt-4 border-t border-slate-100">
          <span className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
            Must-Have Amenities
          </span>
          <div className="flex flex-wrap gap-2.5">
            {[
              { id: 'wifi', label: 'High-speed WiFi', icon: Wifi },
              { id: 'ac', label: 'Air Conditioning', icon: Snowflake },
              { id: 'parking', label: 'Car Parking', icon: Compass },
              { id: 'security', label: 'Security Guard', icon: Shield },
              { id: 'power_backup', label: 'Power Backup', icon: HelpCircle },
              { id: 'gym', label: 'Society Gym', icon: Award },
            ].map(amenity => {
              const Icon = amenity.icon;
              const isSelected = selectedAmenities[amenity.id];
              return (
                <button
                  key={amenity.id}
                  onClick={() => handleAmenityToggle(amenity.id)}
                  className={`inline-flex items-center text-xs py-1.5 px-3.5 rounded-full border transition-all cursor-pointer font-medium gap-1.5 ${
                    isSelected
                      ? 'bg-indigo-600 border-indigo-600 text-white shadow-sm'
                      : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {amenity.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Results grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Recommended Localities Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-4 border border-slate-200 rounded shadow-xs">
            <h4 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider mb-3 flex items-center gap-1.5">
              Top Matching Localities
            </h4>
            
            {topLocalities.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-4">No localities matching active configurations.</p>
            ) : (
              <div className="space-y-3">
                {topLocalities.map((loc, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 border border-slate-150 rounded-md">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="font-semibold text-xs text-slate-700 block">{loc.locality}</span>
                        <span className="text-[10px] text-slate-400">{loc.city}</span>
                      </div>
                      <span className="text-xs font-bold text-indigo-700 bg-white border border-slate-200 px-1.5 py-0.5 rounded">
                        {loc.avgScore} VFM
                      </span>
                    </div>
                    <div className="mt-2 text-[10px] text-slate-400">
                      Found {loc.count} matching options
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded text-[10px] text-slate-500 flex gap-2">
            <AlertCircle className="w-4.5 h-4.5 text-slate-400 flex-shrink-0" />
            <p className="leading-relaxed">
              <strong>Disclaimer:</strong> Matches are computed algorithmically based on analytical utility weighting of property characteristics. This serves as a decision-support model, not personalized financial or commercial advice.
            </p>
          </div>
        </div>

        {/* Recommended Property List */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex justify-between items-center bg-white p-4 border border-slate-200 rounded shadow-xs text-xs">
            <span className="text-slate-600">
              Found <strong className="text-slate-900 font-bold">{recommendedProperties.length}</strong> matching property records
            </span>
            <span className="text-slate-500 font-semibold uppercase tracking-wider text-[9px]">Sorted by Value Score</span>
          </div>

          {recommendedProperties.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-lg p-12 text-center">
              <AlertCircle className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <h5 className="font-semibold text-slate-600 text-sm">No Properties Match Your Query</h5>
              <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">Try widening your rent budget range, allowing a greater metro distance, or checking fewer amenities.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendedProperties.slice(0, 20).map(prop => (
                <div key={prop.property_id} className="bg-white border border-slate-200 hover:border-slate-300 rounded shadow-xs overflow-hidden flex flex-col justify-between transition-colors text-xs">
                  <div className="p-4">
                    {/* Header */}
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-[9px] uppercase font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded inline-block">
                          {prop.property_type} • {prop.furnishing_status}
                        </span>
                        <h4 className="font-bold text-slate-900 text-xs mt-2 leading-snug">{prop.listing_title}</h4>
                        <div className="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          {prop.locality}, {prop.city}
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <span className="text-base font-bold text-slate-800 block">{formatCurrency(prop.monthly_rent)}</span>
                        <span className="text-[9px] text-slate-400 block">/ month</span>
                      </div>
                    </div>

                    {/* Features list */}
                    <div className="mt-4 grid grid-cols-2 gap-y-2 gap-x-1.5 pb-4 border-b border-slate-100 text-xs">
                      <div className="text-slate-500">
                        Size: <strong className="text-slate-700">{prop.area_sqft} sqft</strong>
                      </div>
                      <div className="text-slate-500">
                        Metro Distance: <strong className="text-slate-700">{formatDistance(prop.metro_distance_km)}</strong>
                      </div>
                      <div className="text-slate-500">
                        Rent/Sqft: <strong className="text-slate-700">₹{prop.rent_per_sqft}/sqft</strong>
                      </div>
                      <div className="text-slate-500">
                        Rating: <strong className="text-slate-700">★ {prop.rating}</strong>
                      </div>
                    </div>

                    {/* Key Amenities */}
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {prop.wifi === 'Yes' && <span className="bg-slate-50 text-slate-500 text-[9px] font-medium py-0.5 px-2 rounded-full inline-flex items-center gap-0.5"><Wifi className="w-2.5 h-2.5" /> WiFi</span>}
                      {prop.ac === 'Yes' && <span className="bg-slate-50 text-slate-500 text-[9px] font-medium py-0.5 px-2 rounded-full inline-flex items-center gap-0.5"><Snowflake className="w-2.5 h-2.5" /> AC</span>}
                      {prop.parking === 'Yes' && <span className="bg-slate-50 text-slate-500 text-[9px] font-medium py-0.5 px-2 rounded-full inline-flex items-center gap-0.5"><Compass className="w-2.5 h-2.5" /> Parking</span>}
                      {prop.security === 'Yes' && <span className="bg-slate-50 text-slate-500 text-[9px] font-medium py-0.5 px-2 rounded-full inline-flex items-center gap-0.5"><Shield className="w-2.5 h-2.5" /> Guard</span>}
                    </div>
                  </div>

                  {/* VFM Footer */}
                  <div className="bg-slate-50 p-3.5 border-t border-slate-100 flex justify-between items-center text-xs">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wide">Value Score:</span>
                      <span className="font-bold text-slate-800">{prop.targetScore} <span className="text-[9px] text-slate-450 font-normal">/ 100</span></span>
                    </div>
                    <button
                      onClick={() => setDetailedProperty(prop)}
                      className="text-[11px] text-slate-600 hover:text-slate-900 font-semibold cursor-pointer"
                    >
                      Cost Breakdown →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Modal dialog for Cost breakdown details */}
      {detailedProperty && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-md w-full overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex justify-between items-start">
              <div>
                <span className="text-[9px] font-bold text-indigo-600 uppercase tracking-widest bg-indigo-50 px-2 py-0.5 rounded-full">
                  Cost Breakdown
                </span>
                <h4 className="font-bold text-slate-800 text-base mt-1.5">{detailedProperty.listing_title}</h4>
              </div>
              <button
                onClick={() => setDetailedProperty(null)}
                className="text-slate-400 hover:text-slate-700 text-lg cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="p-5 space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center text-sm py-1 border-b border-slate-50">
                  <span className="text-slate-500">Monthly Rent:</span>
                  <span className="font-bold text-slate-800">{formatCurrency(detailedProperty.monthly_rent)}</span>
                </div>
                <div className="flex justify-between items-center text-sm py-1 border-b border-slate-50">
                  <span className="text-slate-500">Monthly Maintenance:</span>
                  <span className="font-semibold text-slate-700">{formatCurrency(detailedProperty.maintenance)}</span>
                </div>
                <div className="flex justify-between items-center text-sm py-1 border-b border-slate-50">
                  <span className="text-slate-500">Electricity Estimate:</span>
                  <span className="font-semibold text-slate-700">{formatCurrency(detailedProperty.electricity_estimate)}</span>
                </div>
                <div className="flex justify-between items-center text-sm py-1 border-b border-slate-50">
                  <span className="text-slate-500">Internet Connection:</span>
                  <span className="font-semibold text-slate-700">{formatCurrency(800)}</span>
                </div>
                <div className="flex justify-between items-center text-base font-bold text-indigo-700 pt-2 border-t border-slate-200">
                  <span>Total Monthly Housing Cost:</span>
                  <span>{formatCurrency(detailedProperty.totalMonthlyCost)}</span>
                </div>
              </div>

              <div className="bg-slate-50 p-3 rounded-md border border-slate-150 flex gap-2">
                <Info className="w-4 h-4 text-indigo-500 flex-shrink-0 mt-0.5" />
                <div className="text-[10px] text-slate-500 leading-relaxed">
                  <strong>Estimated Security Deposit:</strong> {formatCurrency(detailedProperty.security_deposit)} (ref. {(detailedProperty.security_deposit / detailedProperty.monthly_rent).toFixed(0)}x rent, refundable at lease end).
                </div>
              </div>
            </div>

            <div className="bg-slate-50 p-4 border-t border-slate-100 text-right">
              <button
                onClick={() => setDetailedProperty(null)}
                className="bg-slate-800 text-white text-xs font-semibold py-1.5 px-4 rounded hover:bg-slate-900 transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
