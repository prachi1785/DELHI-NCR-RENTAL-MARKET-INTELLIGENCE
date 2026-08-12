# Delhi/NCR Rental Market Intelligence — End-to-End Data Analytics Case Study

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](python/)
[![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20MySQL-4169E1?style=flat&logo=postgresql&logoColor=white)](sql/)
[![Dashboard](https://img.shields.io/badge/Dashboard-React%20%2B%20TypeScript-61DAFB?style=flat&logo=react&logoColor=white)](dashboard/)

This portfolio-grade data analytics project examines the residential rental market in the Delhi National Capital Region (Delhi/NCR). It provides a full analyst workflow from generating raw messy data, cleaning it via Python (Pandas/NumPy), storing it in a normalized PostgreSQL database schema, analyzing pricing drivers using SQL, building a customizable multi-attribute decision scoring engine (Value-for-Money Score), and presenting the insights via a highly polished interactive React dashboard.

---

## 1. Core Business Problem

> **What factors influence residential rental prices across Delhi/NCR, and which specific localities offer the best relative value for different target renter demographics?**

Finding a rental property involves balancing multiple trade-offs (rent vs space, distance to transit vs quiet neighborhoods). Crucially, "best value" is subjective and differs by renter profile:
1. **Students** prioritize cheap rents, high-speed WiFi, proximity to college campuses (Delhi University North Campus, Greater Noida Knowledge Parks), and ready-to-move-in furnished rooms.
2. **Working Professionals** prioritize corporate connectivity (Gurugram/Noida Expressway), high-quality societies with power backups, lifts, security, and short commute distances.
3. **Working Bachelors** seek budget efficiency, 1RK/1BHK layouts, and proximity to metro corridors for ease of transit.
4. **Families** demand spacious layouts (2BHK/3BHK), green environments, access to school buses, nearby hospital corridors, and dedicated parking.

This project avoids generic hard-coded findings. All conclusions, pricing premiums, and spatial value scores are computed directly from the dataset.

---

## 2. Tech Stack

- **Python & Jupyter Notebooks:** Pandas (data cleansing, formatting, text mapping), NumPy (mathematical decay functions), Matplotlib & Seaborn (statistical distributions and correlation checks).
- **Relational SQL Database:** PostgreSQL-compatible schema and analytical query scripts for grouping, premium calculation, and in-database VFM scoring.
- **Interactive Dashboard:** React (v18), TypeScript, Vite, Tailwind CSS (v4), and Recharts (data visualizations).

---

## 3. Project Structure

```text
delhi-ncr-rental-market-intelligence/
│
├── data/
│   ├── raw/
│   │   └── rental_listings_raw.csv           # Messy simulated raw CSV dataset
│   ├── processed/
│   │   └── rental_listings_cleaned.csv       # Cleaned, standardized CSV with VFM scores
│   └── README.md                             # Dataset glossary & descriptions
│
├── python/
│   ├── data_cleaning.ipynb                   # Cleansing & normalisation pipeline
│   ├── exploratory_analysis.ipynb            # Descriptive & statistical analysis
│   ├── value_score.ipynb                     # Decision scoring engine configuration
│   ├── generate_raw_data.py                  # Raw CSV generator script
│   ├── run_analysis_and_build_notebooks.py   # Master execution & notebook compiler
│   └── requirements.txt                      # Python dependencies
│
├── sql/
│   ├── schema.sql                            # Relational database table definitions
│   ├── analysis_queries.sql                  # Analytical queries for database insights
│   └── README.md                             # SQL usage instructions & schema mapping
│
├── dashboard/
│   ├── src/                                  # React source components and pages
│   ├── dist/                                 # Built production static assets
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md                             # React app setup instructions
│
├── README.md                                 # Master repository documentation
└── .gitignore
```

---

## 4. Value-For-Money (VFM) Score Methodology

To quantify "value," we normalize property attributes into a unified 0–100 scale:
- **Affordability Score:** `100 - (monthly_rent / max_rent * 100)`. Higher rent translates to a lower affordability index.
- **Metro Proximity:** Exponential decay model `100 * exp(-0.8 * distance_km)`. Properties within 500m score `~100`, while those beyond 2km drop below `20`.
- **Destination Proximity:** Similar exponential decay calculated to colleges, office parks, and schools/hospitals depending on profile.
- **Amenities Score:** Percentage of available key amenities relative to the segment profile's needs.
- **Safety Index:** Combines zone crime-rate indices with CCTV and guard presence.

### Demographic Weight Configurations:

| Component | Students | Working Professionals | Working Bachelors | Families |
| :--- | :---: | :---: | :---: | :---: |
| **Rent Affordability** | **30%** | **20%** | **30%** | **20%** |
| **Metro Connectivity** | **25%** | **25%** | **25%** | **10%** (Shared) |
| **Target Proximity** | **20%** (Colleges) | **25%** (Offices) | **15%** (Offices) | **35%** (Schools/Hospitals) |
| **Amenities** | **15%** | **15%** | **15%** | **15%** |
| **Safety** | **10%** | **15%** | **15%** | **20%** |
| **Space (Sq.Ft.)** | — | — | — | **15%** |

---

## 5. Key Findings from the Dataset

These insights were calculated dynamically from the prototype dataset:
1. **Regional Pricing:** Gurugram leads the region with a median rent of **₹31,000**, followed by Delhi (**₹20,000**), Noida (**₹17,000**), Ghaziabad (**₹15,000**), and Greater Noida (**₹11,500**).
2. **Locality Benchmarks:** The most expensive localities are **Golf Course Road** (Gurugram) at ₹62,500 median rent and **Hauz Khas** (South Delhi) at ₹58,000. The cheapest are **Knowledge Park** (Greater Noida) at ₹9,500 and **Shakarpur** (East Delhi) at ₹11,500.
3. **Amenity Premiums:** Dedicated parking spaces command the highest pricing premium at **90%** (₹28,500 vs. ₹15,000 median), followed by Air Conditioning at **39%** and Power Backups at **22%**.
4. **Metro Distance Impact:** Units directly near a metro station (&lt;500m) command a median rent of **₹25,000** vs. **₹17,500** for remote units (&gt;2km), showing a premium of **42.8%** for public transport access.

---

## 6. How to Run Locally

### Run Python Notebooks & Data Pipeline
1. Navigate to the root directory and install dependencies:
   ```bash
   pip install -r python/requirements.txt
   ```
2. Re-run the data pipeline (generates raw CSV, cleans it, calculates scores, and compiles Jupyter Notebooks):
   ```bash
   python3 python/generate_raw_data.py
   python3 python/run_analysis_and_build_notebooks.py
   ```

### Set Up Dashboard
1. Navigate to the dashboard directory:
   ```bash
   cd dashboard
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Access the dashboard at `http://localhost:5173`.
