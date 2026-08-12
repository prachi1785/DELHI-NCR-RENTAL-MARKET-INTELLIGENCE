import { HelpCircle, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function DataTransparency() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Transparency Banner */}
      <div className="bg-slate-100 border border-slate-250 rounded p-4 flex gap-4 text-slate-800 shadow-xs">
        <AlertTriangle className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-xs uppercase tracking-wide">Prototype Dataset Notice</h4>
          <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">
            This prototype application utilizes a programmatically simulated dataset of 839 records covering major Delhi/NCR rental hubs. The distributions are designed to accurately mirror real-world rental patterns (e.g. higher rents in South Delhi and Cyber Gurugram, student hubs in North/East Delhi). For production deployment, you can import public listing feeds into the matching PostgreSQL schema.
          </p>
        </div>
      </div>

      {/* Methodology Section */}
      <div className="bg-white p-4 border border-slate-200 rounded shadow-xs space-y-6">
        <div>
          <h3 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider pb-2 border-b border-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-slate-500" />
            Value-for-Money (VFM) Scoring Framework
          </h3>
          <p className="text-xs text-slate-500 mt-2 leading-relaxed">
            The Value-for-Money index determines how much practical benefit a property offers relative to its financial cost. Instead of a single static score, the engine computes four separate indexes tailored to specific renter demographics by weighting standardized (0–100) parameters.
          </p>
        </div>

        {/* Weights table */}
        <div className="overflow-x-auto">
          <table className="min-w-full text-xs text-slate-700 divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-2 text-left font-bold text-slate-500 uppercase tracking-wider text-[9px]">Scoring Parameter</th>
                <th className="px-4 py-2 text-left font-bold text-slate-700 uppercase tracking-wider text-[9px]">Students</th>
                <th className="px-4 py-2 text-left font-bold text-slate-700 uppercase tracking-wider text-[9px]">Professionals</th>
                <th className="px-4 py-2 text-left font-bold text-slate-700 uppercase tracking-wider text-[9px]">Bachelors</th>
                <th className="px-4 py-2 text-left font-bold text-slate-700 uppercase tracking-wider text-[9px]">Families</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              <tr>
                <td className="px-4 py-2.5 font-bold">Rent Affordability</td>
                <td className="px-4 py-2.5">30%</td>
                <td className="px-4 py-2.5">20%</td>
                <td className="px-4 py-2.5">30%</td>
                <td className="px-4 py-2.5">20%</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 font-bold">Metro Connectivity</td>
                <td className="px-4 py-2.5">25%</td>
                <td className="px-4 py-2.5">25%</td>
                <td className="px-4 py-2.5">25%</td>
                <td className="px-4 py-2.5">10% (Shared)</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 font-bold">Destination Proximity</td>
                <td className="px-4 py-2.5">20% (Colleges)</td>
                <td className="px-4 py-2.5">25% (Offices)</td>
                <td className="px-4 py-2.5">15% (Offices)</td>
                <td className="px-4 py-2.5">35% (Schools/Hospitals)</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 font-bold">Amenities Score</td>
                <td className="px-4 py-2.5">15%</td>
                <td className="px-4 py-2.5">15%</td>
                <td className="px-4 py-2.5">15%</td>
                <td className="px-4 py-2.5">15%</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 font-bold">Safety Index</td>
                <td className="px-4 py-2.5">10%</td>
                <td className="px-4 py-2.5">15%</td>
                <td className="px-4 py-2.5">15%</td>
                <td className="px-4 py-2.5">20%</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Formulas */}
        <div className="space-y-3 pt-3 border-t border-slate-100">
          <h4 className="font-bold text-slate-800 text-sm">Parameter Normalization Formulas</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-600">
            <div className="p-3 bg-slate-50 rounded border border-slate-100">
              <span className="font-semibold block text-slate-800">Rent Affordability Score</span>
              <code className="block mt-1 font-mono text-[10px] bg-slate-200/50 p-1 rounded">100 - (monthly_rent / max_rent * 100)</code>
              <p className="mt-1 leading-normal text-[10px]">Capped globally. Higher rents receive lower affordability index.</p>
            </div>
            <div className="p-3 bg-slate-50 rounded border border-slate-100">
              <span className="font-semibold block text-slate-800">Metro Proximity Score</span>
              <code className="block mt-1 font-mono text-[10px] bg-slate-200/50 p-1 rounded">100 * exp(-0.8 * distance_km)</code>
              <p className="mt-1 leading-normal text-[10px]">Exponential decay. Properties directly beside the metro score ~100. Over 2km drops to &lt;20.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Limitations Section */}
      <div className="bg-white p-4 border border-slate-200 rounded shadow-xs space-y-4">
        <h3 className="font-bold text-slate-800 text-[10px] uppercase tracking-wider pb-2 border-b border-slate-100 flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-slate-500" />
          Analytical Limitations
        </h3>
        <ul className="list-disc list-inside text-xs text-slate-600 space-y-2 leading-relaxed">
          <li>
            <strong>Missing Qualitative Variables:</strong> Factors such as landlord behavior, structural construction quality, natural ventilation, and neighbor quality are not captured in public metadata feeds.
          </li>
          <li>
            <strong>Static Commute Proxies:</strong> Distance is modeled as straight-line proximity to nearest station coordinates. It does not account for peak-hour road congestion or public transport frequencies.
          </li>
          <li>
            <strong>Dynamic Seasonality:</strong> Rents vary depending on the calendar month (e.g. North Campus rents surge in July/August during DU admissions). The dataset reflects a standardized snapshot.
          </li>
        </ul>
      </div>

    </div>
  );
}
