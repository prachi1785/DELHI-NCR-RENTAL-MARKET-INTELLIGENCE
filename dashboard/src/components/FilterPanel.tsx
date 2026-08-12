import { X, RotateCcw } from 'lucide-react';
import type { PropertyListing } from '../types';

interface FilterPanelProps {
  listings: PropertyListing[];
  selectedCity: string;
  setSelectedCity: (city: string) => void;
  selectedLocality: string;
  setSelectedLocality: (locality: string) => void;
  selectedType: string;
  setSelectedType: (type: string) => void;
  selectedFurnishing: string;
  setSelectedFurnishing: (furnishing: string) => void;
  budgetRange: [number, number];
  setBudgetRange: (range: [number, number]) => void;
  bedrooms: number | 'All';
  setBedrooms: (beds: number | 'All') => void;
  resetFilters: () => void;
}

export default function FilterPanel({
  listings,
  selectedCity,
  setSelectedCity,
  selectedLocality,
  setSelectedLocality,
  selectedType,
  setSelectedType,
  selectedFurnishing,
  setSelectedFurnishing,
  budgetRange,
  setBudgetRange,
  bedrooms,
  setBedrooms,
  resetFilters,
}: FilterPanelProps) {
  // Cities
  const cities = Array.from(new Set(listings.map((item) => item.city))).sort();

  // Localities filtered by city
  const filteredLocalities = Array.from(
    new Set(
      listings
        .filter((item) => selectedCity === 'All' || item.city === selectedCity)
        .map((item) => item.locality)
    )
  ).sort();

  const maxRentLimit = Math.max(...listings.map((item) => item.monthly_rent), 80000);

  // Determine active filters for summary pills
  const activeFilters = [];
  if (selectedCity !== 'All') {
    activeFilters.push({ id: 'city', label: `City: ${selectedCity}`, clear: () => { setSelectedCity('All'); setSelectedLocality('All'); } });
  }
  if (selectedLocality !== 'All') {
    activeFilters.push({ id: 'locality', label: `Locality: ${selectedLocality}`, clear: () => setSelectedLocality('All') });
  }
  if (selectedType !== 'All') {
    activeFilters.push({ id: 'type', label: `BHK: ${selectedType}`, clear: () => setSelectedType('All') });
  }
  if (bedrooms !== 'All') {
    activeFilters.push({ id: 'bedrooms', label: `Bedrooms: ${bedrooms}`, clear: () => setBedrooms('All') });
  }
  if (selectedFurnishing !== 'All') {
    activeFilters.push({ id: 'furnishing', label: `Furnishing: ${selectedFurnishing}`, clear: () => setSelectedFurnishing('All') });
  }
  if (budgetRange[1] < maxRentLimit) {
    activeFilters.push({ id: 'budget', label: `Max Rent: ₹${budgetRange[1].toLocaleString('en-IN')}`, clear: () => setBudgetRange([budgetRange[0], maxRentLimit]) });
  }

  return (
    <div className="bg-white border border-slate-200 rounded p-4 space-y-4">
      {/* Filters Title Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">Analysis Controls</span>
        {activeFilters.length > 0 && (
          <button
            onClick={resetFilters}
            className="text-[10px] text-slate-500 hover:text-slate-900 font-semibold flex items-center gap-1 cursor-pointer"
          >
            <RotateCcw className="w-3 h-3" />
            Clear All
          </button>
        )}
      </div>

      {/* Grid Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 text-xs">
        {/* City Filter */}
        <div>
          <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1">City</label>
          <select
            value={selectedCity}
            onChange={(e) => {
              setSelectedCity(e.target.value);
              setSelectedLocality('All');
            }}
            className="w-full py-1.5 px-2.5 border border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:border-slate-400"
          >
            <option value="All">All Cities</option>
            {cities.map((city) => (
              <option key={city} value={city}>{city}</option>
            ))}
          </select>
        </div>

        {/* Locality Filter */}
        <div>
          <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1">Locality</label>
          <select
            value={selectedLocality}
            onChange={(e) => setSelectedLocality(e.target.value)}
            className="w-full py-1.5 px-2.5 border border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:border-slate-400"
          >
            <option value="All">All Localities</option>
            {filteredLocalities.map((loc) => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
        </div>

        {/* Property Type Filter */}
        <div>
          <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1">BHK Type</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="w-full py-1.5 px-2.5 border border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:border-slate-400"
          >
            <option value="All">All BHKs</option>
            <option value="1RK">1 RK</option>
            <option value="1BHK">1 BHK</option>
            <option value="2BHK">2 BHK</option>
            <option value="3BHK">3 BHK</option>
            <option value="4BHK">4 BHK</option>
          </select>
        </div>

        {/* Bedrooms Filter */}
        <div>
          <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1">Bedrooms</label>
          <select
            value={bedrooms}
            onChange={(e) => setBedrooms(e.target.value === 'All' ? 'All' : Number(e.target.value))}
            className="w-full py-1.5 px-2.5 border border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:border-slate-400"
          >
            <option value="All">Any Bedrooms</option>
            <option value="1">1 Bed</option>
            <option value="2">2 Beds</option>
            <option value="3">3 Beds</option>
            <option value="4">4 Beds</option>
          </select>
        </div>

        {/* Furnishing Filter */}
        <div>
          <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1">Furnishing</label>
          <select
            value={selectedFurnishing}
            onChange={(e) => setSelectedFurnishing(e.target.value)}
            className="w-full py-1.5 px-2.5 border border-slate-200 rounded bg-white text-slate-700 focus:outline-none focus:border-slate-400"
          >
            <option value="All">Any Furnishing</option>
            <option value="Furnished">Furnished</option>
            <option value="Semi-Furnished">Semi-Furnished</option>
            <option value="Unfurnished">Unfurnished</option>
          </select>
        </div>

        {/* Budget Filter */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Max Budget</label>
            <span className="font-bold text-slate-700">
              {budgetRange[1] >= maxRentLimit ? 'No Limit' : `₹${budgetRange[1].toLocaleString('en-IN')}`}
            </span>
          </div>
          <input
            type="range"
            min={5000}
            max={maxRentLimit}
            step={2500}
            value={budgetRange[1]}
            onChange={(e) => setBudgetRange([budgetRange[0], Number(e.target.value)])}
            className="w-full h-1 bg-slate-200 rounded appearance-none cursor-pointer accent-slate-700 focus:outline-none"
          />
        </div>
      </div>

      {/* Active Summary Pills */}
      {activeFilters.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100 text-[10px]">
          <span className="text-slate-400 font-bold uppercase tracking-wider mr-1">Active:</span>
          {activeFilters.map((pill) => (
            <span
              key={pill.id}
              className="inline-flex items-center bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200 gap-1 font-medium"
            >
              {pill.label}
              <button onClick={pill.clear} className="text-slate-400 hover:text-slate-600 cursor-pointer">
                <X className="w-2.5 h-2.5" />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
