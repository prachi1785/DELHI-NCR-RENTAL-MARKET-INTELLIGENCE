import { useState, useMemo } from 'react';
import Sidebar from './components/Sidebar';
import FilterPanel from './components/FilterPanel';
import MarketOverview from './pages/MarketOverview';
import PriceDrivers from './pages/PriceDrivers';
import LocationIntelligence from './pages/LocationIntelligence';
import RenterSegments from './pages/RenterSegments';
import FindYourRental from './pages/FindYourRental';
import LocalityComparison from './pages/LocalityComparison';
import DataTransparency from './pages/DataTransparency';
import type { PropertyListing } from './types';


// Load our converted JSON dataset
import listingsRaw from './data/listings.json';

const listings = listingsRaw as PropertyListing[];

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');

  // Filter States
  const [selectedCity, setSelectedCity] = useState<string>('All');
  const [selectedLocality, setSelectedLocality] = useState<string>('All');
  const [selectedType, setSelectedType] = useState<string>('All');
  const [selectedFurnishing, setSelectedFurnishing] = useState<string>('All');
  const [bedrooms, setBedrooms] = useState<number | 'All'>('All');
  
  const maxRentLimit = useMemo(() => {
    return Math.max(...listings.map((item) => item.monthly_rent), 80000);
  }, []);
  
  const [budgetRange, setBudgetRange] = useState<[number, number]>([5000, maxRentLimit]);

  // Reset Filters
  const resetFilters = () => {
    setSelectedCity('All');
    setSelectedLocality('All');
    setSelectedType('All');
    setSelectedFurnishing('All');
    setBedrooms('All');
    setBudgetRange([5000, maxRentLimit]);
  };

  // Compute filtered dataset
  const filteredData = useMemo(() => {
    return listings.filter((item) => {
      if (selectedCity !== 'All' && item.city !== selectedCity) return false;
      if (selectedLocality !== 'All' && item.locality !== selectedLocality) return false;
      if (selectedType !== 'All' && item.property_type !== selectedType) return false;
      if (selectedFurnishing !== 'All' && item.furnishing_status !== selectedFurnishing) return false;
      if (bedrooms !== 'All' && item.bedrooms !== bedrooms) return false;
      if (item.monthly_rent < budgetRange[0] || item.monthly_rent > budgetRange[1]) return false;
      return true;
    });
  }, [selectedCity, selectedLocality, selectedType, selectedFurnishing, bedrooms, budgetRange]);

  // Render current active tab content
  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <MarketOverview filteredData={filteredData} />;
      case 'drivers':
        return <PriceDrivers filteredData={filteredData} />;
      case 'location':
        return <LocationIntelligence filteredData={listings} />; // Needs full dataset for mapping and custom profiles
      case 'renter':
        return <RenterSegments filteredData={listings} />; // Needs full dataset for segment-wide comparison
      case 'find':
        return <FindYourRental listings={listings} />; // Needs full dataset to run recommendation queries
      case 'compare':
        return <LocalityComparison listings={listings} />; // Needs full dataset to look up chosen localities
      case 'transparency':
        return <DataTransparency />;
      default:
        return <MarketOverview filteredData={filteredData} />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans text-xs">
      {/* Desktop Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} listingsCount={listings.length} />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        {/* Mobile Navbar Header */}
        <header className="bg-slate-900 text-white p-4 flex justify-between items-center md:hidden flex-shrink-0">
          <span className="font-bold text-xs uppercase tracking-wider">Delhi/NCR Rental BI</span>
          <select
            value={activeTab}
            onChange={(e) => setActiveTab(e.target.value)}
            className="bg-slate-800 text-slate-200 text-xs py-1.5 px-3 rounded border border-slate-700 focus:outline-none"
          >
            <option value="overview">Overview</option>
            <option value="drivers">Price Drivers</option>
            <option value="location">Location Intelligence</option>
            <option value="renter">Renter Segments</option>
            <option value="find">Find Your Rental</option>
            <option value="compare">Locality Comparison</option>
            <option value="transparency">Methodology</option>
          </select>
        </header>

        {/* Scrollable Container */}
        <div className="flex-1 p-6 space-y-6 max-w-7xl w-full mx-auto">
          {/* Header Title */}
          <div className="pb-3 border-b border-slate-200">
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              {activeTab === 'overview' && 'Market Overview'}
              {activeTab === 'drivers' && 'What Drives Rental Prices?'}
              {activeTab === 'location' && 'Location Intelligence'}
              {activeTab === 'renter' && 'Renter Segments'}
              {activeTab === 'find' && 'Find Your Rental'}
              {activeTab === 'compare' && 'Locality Comparison'}
              {activeTab === 'transparency' && 'Methodology & Data Parameters'}
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              {activeTab === 'overview' && 'A data-driven view of residential rental prices, property characteristics and affordability.'}
              {activeTab === 'drivers' && 'An analysis of parameters triggering rental premiums, sizing correlations, and transit access.'}
              {activeTab === 'location' && 'Explore spatial rental distributions, property sizes, and coordinate mapping across NCR zones.'}
              {activeTab === 'renter' && 'Contrasting space requirements, budget parameters, and connectivity weights across renter profiles.'}
              {activeTab === 'find' && 'Select your renter profile and preferences to display matched properties sorted by Value Score.'}
              {activeTab === 'compare' && 'Select up to three localities to analyze rent, connectivity, and amenities side-by-side.'}
              {activeTab === 'transparency' && 'Methodology transparency, scoring weight models, data parameters, and analytical limitations.'}
            </p>
          </div>

          {/* Filters Summary (Overview and Price Drivers only) */}
          {(activeTab === 'overview' || activeTab === 'drivers') && (
            <FilterPanel
              listings={listings}
              selectedCity={selectedCity}
              setSelectedCity={setSelectedCity}
              selectedLocality={selectedLocality}
              setSelectedLocality={setSelectedLocality}
              selectedType={selectedType}
              setSelectedType={setSelectedType}
              selectedFurnishing={selectedFurnishing}
              setSelectedFurnishing={setSelectedFurnishing}
              budgetRange={budgetRange}
              setBudgetRange={setBudgetRange}
              bedrooms={bedrooms}
              setBedrooms={setBedrooms}
              resetFilters={resetFilters}
            />
          )}

          {/* Sub-page */}
          <div className="min-h-0">{renderContent()}</div>
        </div>

        {/* Footer */}
        <footer className="bg-white border-t border-slate-200 py-4 text-center text-[10px] text-slate-400 mt-auto">
          <p>© {new Date().getFullYear()} Delhi/NCR Rental Market Intelligence • Internal BI Case Study</p>
        </footer>
      </div>
    </div>
  );
}
