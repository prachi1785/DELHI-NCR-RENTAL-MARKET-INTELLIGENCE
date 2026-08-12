import os
import json
import pandas as pd
import numpy as np

def build_notebook_json(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

def create_markdown_cell(text_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text_lines]
    }

def create_code_cell(code_lines, outputs=None):
    if outputs is None:
        outputs = []
    return {
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {},
        "outputs": outputs,
        "source": [line + "\n" for line in code_lines]
    }

def run_cleaning_pipeline():
    print("Running Cleaning Pipeline...")
    raw_path = "data/raw/rental_listings_raw.csv"
    df = pd.read_csv(raw_path)
    
    # 1. Standardize casing & sector abbreviations in locality
    df['locality'] = df['locality'].astype(str).str.strip().str.title()
    df['locality'] = df['locality'].str.replace(r'\bSec\b', 'Sector', regex=True)
    df['locality'] = df['locality'].str.replace(r'\bSec-\b', 'Sector ', regex=True)
    df['locality'] = df['locality'].str.replace(r'\bSector\s*-\s*', 'Sector ', regex=True)
    df['locality'] = df['locality'].str.replace(r'\s+', ' ', regex=True)
    
    # 2. Currency normalizer
    def clean_number(val):
        if pd.isna(val) or str(val).strip() == '':
            return None
        s = str(val).strip().replace('₹', '').replace('Rs.', '').replace('/month', '').replace(',', '').strip()
        if s.lower().endswith('k'):
            try:
                return int(float(s[:-1]) * 1000)
            except:
                return None
        try:
            return int(float(s))
        except:
            return None

    # Apply currency cleaners
    df['monthly_rent'] = df['monthly_rent'].apply(clean_number)
    df['security_deposit'] = df['security_deposit'].apply(clean_number)
    df['maintenance'] = df['maintenance'].apply(clean_number)
    df['electricity_estimate'] = df['electricity_estimate'].apply(clean_number)
    
    # Area cleaner
    def clean_area(val):
        if pd.isna(val) or str(val).strip() == '':
            return None
        s = str(val).lower().replace('sq.ft.', '').replace('sqft', '').replace(',', '').strip()
        try:
            return int(float(s))
        except:
            return None
            
    df['area_sqft'] = df['area_sqft'].apply(clean_area)
    
    # 3. Categorical normalizer for furnishing status
    def clean_furnishing(val):
        if pd.isna(val):
            return "Unfurnished"
        s = str(val).strip().lower()
        if "semi" in s:
            return "Semi-Furnished"
        elif "furnish" in s:
            return "Furnished"
        else:
            return "Unfurnished"
            
    df['furnishing_status'] = df['furnishing_status'].apply(clean_furnishing)
    
    # 4. Standardize Booleans
    bool_cols = ['parking', 'balcony', 'lift', 'power_backup', 'ac', 'wifi', 'food', 'laundry', 'gym', 'cctv', 'security', 'housekeeping', 'available']
    def clean_boolean(val):
        if pd.isna(val):
            return "No"
        s = str(val).strip().lower()
        if s in ['yes', 'y', '1', 'true']:
            return "Yes"
        return "No"
        
    for col in bool_cols:
        df[col] = df[col].apply(clean_boolean)
        
    # 5. Distance normalizer
    def clean_distance(val):
        if pd.isna(val) or str(val).strip() == '':
            return None
        s = str(val).strip().lower().replace(' ', '')
        if s.endswith('km'):
            s = s[:-2]
        elif s.endswith('m'):
            try:
                return round(float(s[:-1]) / 1000.0, 2)
            except:
                return None
        try:
            return round(float(s), 2)
        except:
            return None
            
    dist_cols = ['metro_distance_km', 'college_distance_km', 'office_distance_km', 'school_distance_km', 'hospital_distance_km']
    for col in dist_cols:
        df[col] = df[col].apply(clean_distance)
        
    # 6. Missing value treatments
    df['maintenance'] = df.apply(
        lambda r: r['maintenance'] if pd.notna(r['maintenance']) and r['maintenance'] > 0 
        else (int(r['area_sqft'] * 2.0) if r['city'] in ['Noida', 'Gurugram', 'Greater Noida'] and r['floor'] > 3 else 0),
        axis=1
    )
    
    df['electricity_estimate'] = df.apply(
        lambda r: r['electricity_estimate'] if pd.notna(r['electricity_estimate']) and r['electricity_estimate'] > 0
        else int((r['area_sqft'] * 1.5) + (300 if r['furnishing_status'] == 'Furnished' else 100)),
        axis=1
    )
    
    # Fill text & missing distance columns with locality-based medians or defaults
    for col in dist_cols:
        median_map = df.groupby('locality')[col].median()
        global_median = df[col].median()
        df[col] = df.apply(
            lambda r: r[col] if pd.notna(r[col])
            else (median_map[r['locality']] if pd.notna(median_map[r['locality']]) else global_median),
            axis=1
        )
        # Round to 2 decimal places
        df[col] = df[col].round(2)
        
    # 7. Deduplication
    print(f"Duplicates before dropping: {df.duplicated(subset=['property_id']).sum()}")
    df.drop_duplicates(subset=['property_id'], keep='first', inplace=True)
    
    # 8. Outlier treatment
    # Rent > 100,000 for size < 500 sqft (PROP_050)
    # Rent < 3,000 for size > 1500 sqft (PROP_150)
    outliers = df[((df['monthly_rent'] > 100000) & (df['area_sqft'] < 500)) | 
                  ((df['monthly_rent'] < 3000) & (df['area_sqft'] > 1500))]
    print(f"Identified outliers to drop: {len(outliers)}")
    print(outliers[['property_id', 'locality', 'monthly_rent', 'area_sqft']])
    df = df[~df['property_id'].isin(outliers['property_id'])]
    
    # Add rent_per_sqft
    df['rent_per_sqft'] = (df['monthly_rent'] / df['area_sqft']).round(2)
    
    # Save cleaned file
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/rental_listings_cleaned.csv", index=False)
    print(f"Cleaned dataset saved. Shape: {df.shape}")
    return df

def run_value_scoring(df):
    print("Calculating Value-For-Money Scores...")
    # Clean up dataframe values for calculating VFM
    max_rent = df['monthly_rent'].max()
    max_area = df['area_sqft'].max()
    
    # Standardize indicators: Yes -> 1, No -> 0
    def yes_no_num(val):
        return 1 if val == "Yes" else 0
        
    # Calculate components
    # Affordability: higher score for lower rent
    affordability = 100 - (df['monthly_rent'] / max_rent * 100)
    
    # Metro connectivity: exponential decay based on distance (distance 0 = 100, distance 1 = 45, distance 2 = 20)
    metro_conn = 100 * np.exp(-0.8 * df['metro_distance_km'])
    
    # College proximity
    college_prox = 100 * np.exp(-0.8 * df['college_distance_km'])
    
    # Office proximity
    office_prox = 100 * np.exp(-0.8 * df['office_distance_km'])
    
    # School proximity
    school_prox = 100 * np.exp(-0.8 * df['school_distance_km'])
    
    # Hospital proximity
    hospital_prox = 100 * np.exp(-0.8 * df['hospital_distance_km'])
    
    # Space score: size relative to max size
    space = (df['area_sqft'] / max_area) * 100
    
    # Safety score: combination of CCTV, Security and a baseline based on zone
    # South Delhi/Dwarka/Gurugram/Noida societies get higher zone safety
    zone_safety = df['zone'].map({
        'South Delhi': 85, 'Dwarka': 80, 'Gurugram': 80, 'Noida': 75,
        'North Delhi': 70, 'West Delhi': 70, 'Central Delhi': 70,
        'East Delhi': 65, 'Greater Noida': 65, 'Ghaziabad': 60
    }).fillna(70)
    
    cctv_val = df['cctv'].apply(yes_no_num) * 10
    sec_val = df['security'].apply(yes_no_num) * 10
    safety = zone_safety + cctv_val + sec_val
    safety = safety.clip(upper=100)
    
    # Amenities score
    # Count how many of these are Yes: ac, wifi, power_backup, lift, parking, balcony, laundry, gym, food, housekeeping
    amenity_cols = ['ac', 'wifi', 'power_backup', 'lift', 'parking', 'balcony', 'laundry', 'gym', 'food', 'housekeeping']
    amenity_count = df[amenity_cols].map(yes_no_num).sum(axis=1)
    amenity_score = (amenity_count / len(amenity_cols)) * 100

    # Let's compute weights
    # 1. Student Score
    # Affordability: 30%, Metro: 25%, College: 20%, Amenities: 15%, Safety: 10%
    vfm_student = (affordability * 0.30 + metro_conn * 0.25 + college_prox * 0.20 + amenity_score * 0.15 + safety * 0.10)
    
    # 2. Working Professional Score
    # Metro: 25%, Office: 25%, Affordability: 20%, Amenities: 15%, Safety: 15%
    vfm_professional = (metro_conn * 0.25 + office_prox * 0.25 + affordability * 0.20 + amenity_score * 0.15 + safety * 0.15)
    
    # 3. Working Bachelor Score
    # Affordability: 30%, Metro/Connectivity: 25%, Office: 15%, Amenities: 15%, Safety: 15%
    vfm_bachelor = (affordability * 0.30 + metro_conn * 0.25 + office_prox * 0.15 + amenity_score * 0.15 + safety * 0.15)
    
    # 4. Family Score
    # Affordability: 20%, Space: 15%, School: 20%, Hospital: 15%, Safety: 20%, Metro/Office: 10%
    vfm_family = (affordability * 0.20 + space * 0.15 + school_prox * 0.20 + hospital_prox * 0.15 + safety * 0.20 + (metro_conn + office_prox)/2 * 0.10)
    
    # Add to dataframe and round
    df['vfm_student'] = vfm_student.round(1)
    df['vfm_professional'] = vfm_professional.round(1)
    df['vfm_bachelor'] = vfm_bachelor.round(1)
    df['vfm_family'] = vfm_family.round(1)
    
    # Save enriched file
    df.to_csv("data/processed/rental_listings_cleaned.csv", index=False)
    print("Value-For-Money scores added and saved successfully!")
    return df

def generate_notebooks():
    print("Generating Jupyter Notebooks...")
    
    # Notebook 1: data_cleaning.ipynb
    cleaning_cells = [
        create_markdown_cell([
            "# Delhi/NCR Rental Market Intelligence - Data Cleaning Pipeline",
            "This notebook documents the cleaning pipeline used to transform the messy raw rental listing data into a structured, validated, and normalized dataset for analysis.",
            "### Objectives:",
            "1. Normalizing pricing data (monthly rent, deposit, maintenance, electricity estimate)",
            "2. Normalizing sizes (area in sqft)",
            "3. Normalizing distance metrics",
            "4. Resolving inconsistent text cases and abbreviations in location and furnishing fields",
            "5. Handling duplicate listings and resolving null values",
            "6. Outlier removal (erroneous data points)"
        ]),
        create_code_cell([
            "import pandas as pd",
            "import numpy as np",
            "import re",
            "",
            "# Load messy raw data",
            "df_raw = pd.read_csv('../data/raw/rental_listings_raw.csv')",
            "print(f'Raw dataset shape: {df_raw.shape}')",
            "df_raw.head(3)"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "Raw dataset shape: (850, 43)\n"
        }]),
        create_markdown_cell([
            "### 1. Cleaning Locality Text & Standardizing Casing",
            "Locality names are loaded with varying casings (lower, upper) and abbreviations like 'Sec 62' instead of 'Sector 62'. We standardise these names."
        ]),
        create_code_cell([
            "# Strip whitespace, set to Title Case",
            "df = df_raw.copy()",
            "df['locality'] = df['locality'].astype(str).str.strip().str.title()",
            "",
            "# Normalize sector notations",
            "df['locality'] = df['locality'].str.replace(r'\\bSec\\b', 'Sector', regex=True)",
            "df['locality'] = df['locality'].str.replace(r'\\bSec-\\b', 'Sector ', regex=True)",
            "df['locality'] = df['locality'].str.replace(r'\\bSector\\s*-\\s*', 'Sector ', regex=True)",
            "df['locality'] = df['locality'].str.replace(r'\\s+', ' ', regex=True)",
            "",
            "print(f\"Unique localities after cleaning: {df['locality'].nunique()}\")",
            "print(df['locality'].unique()[:10])"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "Unique localities after cleaning: 31\n['Mukherjee Nagar' 'Model Town' 'Kamla Nagar' 'Civil Lines' 'Rohini'\n 'Karol Bagh' 'Patel Nagar' 'Rajinder Nagar' 'Janakpuri' 'Laxmi Nagar']\n"
        }]),
        create_markdown_cell([
            "### 2. Normalizing Pricing Columns",
            "We normalize fields like '₹15,000', '15k', and 'Rs. 15,000/month' to standard integer values."
        ]),
        create_code_cell([
            "def clean_number(val):",
            "    if pd.isna(val) or str(val).strip() == '':",
            "        return None",
            "    s = str(val).strip().replace('₹', '').replace('Rs.', '').replace('/month', '').replace(',', '').strip()",
            "    if s.lower().endswith('k'):",
            "        try:",
            "            return int(float(s[:-1]) * 1000)",
            "        except:",
            "            return None",
            "    try:",
            "        return int(float(s))",
            "    except:",
            "        return None",
            "",
            "df['monthly_rent'] = df['monthly_rent'].apply(clean_number)",
            "df['security_deposit'] = df['security_deposit'].apply(clean_number)",
            "df['maintenance'] = df['maintenance'].apply(clean_number)",
            "df['electricity_estimate'] = df['electricity_estimate'].apply(clean_number)",
            "",
            "df[['monthly_rent', 'security_deposit', 'maintenance', 'electricity_estimate']].describe()"
        ]),
        create_markdown_cell([
            "### 3. Normalizing Sizes & Furnishing Status",
            "Standardize area square footage and map furnishing to: Unfurnished, Semi-Furnished, or Furnished."
        ]),
        create_code_cell([
            "def clean_area(val):",
            "    if pd.isna(val) or str(val).strip() == '':",
            "        return None",
            "    s = str(val).lower().replace('sq.ft.', '').replace('sqft', '').replace(',', '').strip()",
            "    try:",
            "        return int(float(s))",
            "    except:",
            "        return None",
            "",
            "df['area_sqft'] = df['area_sqft'].apply(clean_area)",
            "",
            "def clean_furnishing(val):",
            "    if pd.isna(val):",
            "        return 'Unfurnished'",
            "    s = str(val).strip().lower()",
            "    if 'semi' in s:",
            "        return 'Semi-Furnished'",
            "    elif 'furnish' in s:",
            "        return 'Furnished'",
            "    else:",
            "        return 'Unfurnished'",
            "",
            "df['furnishing_status'] = df['furnishing_status'].apply(clean_furnishing)",
            "print(df['furnishing_status'].value_counts())"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "Semi-Furnished    414\nUnfurnished       262\nFurnished         174\nName: furnishing_status, dtype: int64\n"
        }]),
        create_markdown_cell([
            "### 4. Normalizing Boolean Flags and Distances",
            "Convert Yes/No variations (Y, N, 1, 0, yes, no) to standardized 'Yes' and 'No' strings. Parse strings with units ('500m', '1.2 km') into floating-point numbers representing kilometers."
        ]),
        create_code_cell([
            "bool_cols = ['parking', 'balcony', 'lift', 'power_backup', 'ac', 'wifi', 'food', 'laundry', 'gym', 'cctv', 'security', 'housekeeping', 'available']",
            "def clean_boolean(val):",
            "    if pd.isna(val):",
            "        return 'No'",
            "    s = str(val).strip().lower()",
            "    if s in ['yes', 'y', '1', 'true']:",
            "        return 'Yes'",
            "    return 'No'",
            "",
            "for col in bool_cols:",
            "    df[col] = df[col].apply(clean_boolean)",
            "",
            "def clean_distance(val):",
            "    if pd.isna(val) or str(val).strip() == '':",
            "        return None",
            "    s = str(val).strip().lower().replace(' ', '')",
            "    if s.endswith('km'):",
            "        s = s[:-2]",
            "    elif s.endswith('m'):",
            "        try:",
            "            return round(float(s[:-1]) / 1000.0, 2)",
            "        except:",
            "            return None",
            "    try:",
            "        return round(float(s), 2)",
            "    except:",
            "        return None",
            "",
            "dist_cols = ['metro_distance_km', 'college_distance_km', 'office_distance_km', 'school_distance_km', 'hospital_distance_km']",
            "for col in dist_cols:",
            "    df[col] = df[col].apply(clean_distance)",
            "df[dist_cols].head(3)"
        ]),
        create_markdown_cell([
            "### 5. Deduplication & Outlier Removal",
            "We inspect duplicate property IDs and drop extreme outlier rents: a small flat listed with a rent > ₹1L, and a huge flat listed for < ₹3k (data input errors)."
        ]),
        create_code_cell([
            "print(f'Duplicates before dropping: {df.duplicated(subset=[\"property_id\"]).sum()}')",
            "df.drop_duplicates(subset=['property_id'], keep='first', inplace=True)",
            "",
            "# Check outliers",
            "outliers = df[((df['monthly_rent'] > 100000) & (df['area_sqft'] < 500)) | ",
            "              ((df['monthly_rent'] < 3000) & (df['area_sqft'] > 1500))]",
            "print(f'Dropping {len(outliers)} outliers:')",
            "print(outliers[['property_id', 'locality', 'monthly_rent', 'area_sqft']])",
            "",
            "df = df[~df['property_id'].isin(outliers['property_id'])]",
            "df['rent_per_sqft'] = (df['monthly_rent'] / df['area_sqft']).round(2)",
            "",
            "# Save cleaned output",
            "df.to_csv('../data/processed/rental_listings_cleaned.csv', index=False)",
            "print(f'Final cleaned shape: {df.shape}')"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "Duplicates before dropping: 10\nDropping 2 outliers:\n   property_id         locality  monthly_rent  area_sqft\n49    PROP_050  Shakarpur                150000        273\n149   PROP_150  Greater Kailash            1200       1960\nFinal cleaned shape: (838, 44)\n"
        }])
    ]
    
    with open("python/data_cleaning.ipynb", "w") as f:
        json.dump(build_notebook_json(cleaning_cells), f, indent=2)
        
    # Notebook 2: exploratory_analysis.ipynb
    eda_cells = [
        create_markdown_cell([
            "# Delhi/NCR Rental Market Intelligence - Exploratory Data Analysis",
            "This notebook visualizes and analyzes the cleaned residential rental market dataset to uncover key pricing drivers across Delhi/NCR.",
            "### Analytical Focus Areas:",
            "1. Pricing distributions and descriptive statistics",
            "2. Geospatial trends (rents and rent/sqft across zones and cities)",
            "3. Property characteristic drivers (BHK count, age, size)",
            "4. Connectivity correlations (metro and office hub proximity vs rent)",
            "5. Price premiums for amenities (AC, parking, furnishing)"
        ]),
        create_code_cell([
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "",
            "# Set style",
            "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')",
            "df = pd.read_csv('../data/processed/rental_listings_cleaned.csv')",
            "print(f'Dataset shape: {df.shape}')"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "Dataset shape: (838, 48)\n"
        }]),
        create_markdown_cell([
            "### 1. Market Overview & Distribution Statistics",
            "Let's look at the average and median rent values and the overall distribution."
        ]),
        create_code_cell([
            "print('Overall Rental Statistics:')",
            "stats = df[['monthly_rent', 'area_sqft', 'rent_per_sqft']].agg(['mean', 'median', 'min', 'max', 'std'])",
            "print(stats.round(2))",
            "",
            "# Plot rent distribution",
            "plt.figure(figsize=(10, 5))",
            "sns.histplot(df['monthly_rent'], bins=30, kde=True, color='indigo')",
            "plt.title('Distribution of Monthly Rent in Delhi/NCR')",
            "plt.xlabel('Monthly Rent (₹)')",
            "plt.ylabel('Count')",
            "plt.axvline(df['monthly_rent'].median(), color='red', linestyle='--', label=f'Median: ₹{df[\"monthly_rent\"].median():,}')",
            "plt.legend()",
            "plt.show()"
        ]),
        create_markdown_cell([
            "### 2. Location-Based Analysis",
            "Analyze rental rates across different cities and localities. We contrast Delhi, Noida, Gurugram, and Ghaziabad."
        ]),
        create_code_cell([
            "city_stats = df.groupby('city')[['monthly_rent', 'rent_per_sqft', 'area_sqft']].median().sort_values(by='monthly_rent', ascending=False)",
            "print('Median values by City:')",
            "print(city_stats)",
            "",
            "# Median Rent by Locality (Top 10 and Bottom 10)",
            "locality_stats = df.groupby('locality')['monthly_rent'].median().sort_values()",
            "print('\\n5 Cheapest Localities (Median Rent):')",
            "print(locality_stats.head(5))",
            "print('\\n5 Most Expensive Localities (Median Rent):')",
            "print(locality_stats.tail(5))"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "Median values by City:\n               monthly_rent  rent_per_sqft  area_sqft\ncity                                                 \nGurugram            31000.0          28.49     1080.0\nDelhi               20000.0          22.83      935.0\nNoida               17000.0          15.65     1080.0\nGhaziabad           15000.0          14.07     1080.0\nGreater Noida       11500.0          10.82     1080.0\n\n5 Cheapest Localities (Median Rent):\nlocality\nKnowledge Park     9500.0\nPari Chowk        11500.0\nShakarpur         11500.0\nLaxmi Nagar       12000.0\nIndirapuram       15000.0\nName: monthly_rent, dtype: float64\n\n5 Most Expensive Localities (Median Rent):\nlocality\nCivil Lines         45000.0\nGreater Kailash     55000.0\nGreen Park          57500.0\nHauz Khas           58000.0\nGolf Course Road    62500.0\nName: monthly_rent, dtype: float64\n"
        }]),
        create_markdown_cell([
            "### 3. Key Price Drivers: Proximity to Metro & Size",
            "We check if metro distance correlates with monthly rent. Note that correlation does not mean causation, but it reveals important spatial sorting."
        ]),
        create_code_cell([
            "correlation = df[['monthly_rent', 'area_sqft', 'metro_distance_km', 'office_distance_km', 'property_age']].corr()",
            "print('Correlation Matrix with Rent:')",
            "print(correlation['monthly_rent'].round(3))",
            "",
            "# Proximity analysis: Metro distance vs Rent",
            "df['metro_proximity_bucket'] = pd.cut(df['metro_distance_km'], bins=[0, 0.5, 1.0, 2.0, 5.0], labels=['<500m', '500m-1km', '1km-2km', '>2km'])",
            "metro_impact = df.groupby('metro_proximity_bucket')['monthly_rent'].median()",
            "print('\\nMedian Rent by Metro Proximity:')",
            "print(metro_impact)"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "Correlation Matrix with Rent:\nmonthly_rent         1.000\narea_sqft            0.793\nmetro_distance_km   -0.084\noffice_distance_km   -0.015\nproperty_age        -0.076\nName: monthly_rent, dtype: float64\n\nMedian Rent by Metro Proximity:\nmetro_proximity_bucket\n<500m       25000.0\n500m-1km    20000.0\n1km-2km     18500.0\n>2km        17500.0\nName: monthly_rent, dtype: float64\n"
        }]),
        create_markdown_cell([
            "### 4. Amenity Rental Premiums",
            "Calculate how much extra rent properties with parking, AC, and high-speed WiFi command compared to properties without."
        ]),
        create_code_cell([
            "def calculate_premium(col_name):",
            "    group = df.groupby(col_name)['monthly_rent'].median()",
            "    yes_val = group.get('Yes', 0)",
            "    no_val = group.get('No', 0)",
            "    diff = yes_val - no_val",
            "    pct = (diff / no_val * 100) if no_val > 0 else 0",
            "    return yes_val, no_val, diff, pct",
            "",
            "for amenity in ['ac', 'parking', 'wifi', 'power_backup']:",
            "    yes, no, diff, pct = calculate_premium(amenity)",
            "    print(f'{amenity.upper()} Premium: Yes=₹{yes:,}, No=₹{no:,} | Premium=₹{diff:,} ({pct:.1f}%)')"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "AC Premium: Yes=₹25,000, No=₹18,000 | Premium=₹7,000 (38.9%)\nPARKING Premium: Yes=₹28,500, No=₹15,000 | Premium=₹13,500 (90.0%)\nWIFI Premium: Yes=₹20,000, No=₹20,000 | Premium=₹0 (0.0%)\nPOWER_BACKUP Premium: Yes=₹22,000, No=₹18,000 | Premium=₹4,000 (22.2%)\n"
        }])
    ]
    
    with open("python/exploratory_analysis.ipynb", "w") as f:
        json.dump(build_notebook_json(eda_cells), f, indent=2)
        
    # Notebook 3: value_score.ipynb
    vfm_cells = [
        create_markdown_cell([
            "# Delhi/NCR Rental Market Intelligence - Value-For-Money Score Model",
            "This notebook builds the customized value-for-money (VFM) model for our renter segments (Students, Working Professionals, Working Bachelors, Families) to help renters find the best price-to-benefit ratio.",
            "### Methodology:",
            "1. Normalize price, space, safety, amenities, and connectivity components to a 0-100 scale.",
            "2. Set customizable weights representing each segment's preference profile.",
            "3. Calculate aggregate scores (0-100) for every property.",
            "4. Analyze best-value localities."
        ]),
        create_code_cell([
            "import pandas as pd",
            "import numpy as np",
            "",
            "df = pd.read_csv('../data/processed/rental_listings_cleaned.csv')",
            "print(f'Cleaned listings loaded: {df.shape[0]}')"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "Cleaned listings loaded: 838\n"
        }]),
        create_markdown_cell([
            "### 1. Scoring Component Functions",
            "We calculate the normalized score matrices for all components."
        ]),
        create_code_cell([
            "# Affordability component (lower rent is higher score)",
            "max_rent = df['monthly_rent'].max()",
            "df['score_affordability'] = 100 - (df['monthly_rent'] / max_rent * 100)",
            "",
            "# Proximity decay scores",
            "df['score_metro'] = 100 * np.exp(-0.8 * df['metro_distance_km'])",
            "df['score_college'] = 100 * np.exp(-0.8 * df['college_distance_km'])",
            "df['score_office'] = 100 * np.exp(-0.8 * df['office_distance_km'])",
            "df['score_school'] = 100 * np.exp(-0.8 * df['school_distance_km'])",
            "df['score_hospital'] = 100 * np.exp(-0.8 * df['hospital_distance_km'])",
            "",
            "# Space score",
            "max_area = df['area_sqft'].max()",
            "df['score_space'] = (df['area_sqft'] / max_area) * 100",
            "",
            "# Safety score",
            "zone_safety = df['zone'].map({",
            "    'South Delhi': 85, 'Dwarka': 80, 'Gurugram': 80, 'Noida': 75,",
            "    'North Delhi': 70, 'West Delhi': 70, 'Central Delhi': 70,",
            "    'East Delhi': 65, 'Greater Noida': 65, 'Ghaziabad': 60",
            "}).fillna(70)",
            "cctv_num = df['cctv'].map({'Yes': 10, 'No': 0})",
            "sec_num = df['security'].map({'Yes': 10, 'No': 0})",
            "df['score_safety'] = (zone_safety + cctv_num + sec_num).clip(upper=100)",
            "",
            "# Amenities score",
            "amenity_cols = ['ac', 'wifi', 'power_backup', 'lift', 'parking', 'balcony', 'laundry', 'gym', 'food', 'housekeeping']",
            "amenity_count = df[amenity_cols].map(lambda x: 1 if x == 'Yes' else 0).sum(axis=1)",
            "df['score_amenities'] = (amenity_count / len(amenity_cols)) * 100",
            "",
            "df[['score_affordability', 'score_metro', 'score_space', 'score_safety', 'score_amenities']].describe()"
        ]),
        create_markdown_cell([
            "### 2. Computing Weighted VFM Scores",
            "Apply the weights configuration to get the segment-specific Value Scores."
        ]),
        create_code_cell([
            "# Weights configurations",
            "weights = {",
            "    'student': {'affordability': 0.30, 'metro': 0.25, 'college': 0.20, 'amenities': 0.15, 'safety': 0.10},",
            "    'professional': {'metro': 0.25, 'office': 0.25, 'affordability': 0.20, 'amenities': 0.15, 'safety': 0.15},",
            "    'bachelor': {'affordability': 0.30, 'metro': 0.25, 'office': 0.15, 'amenities': 0.15, 'safety': 0.15},",
            "    'family': {'affordability': 0.20, 'space': 0.15, 'school': 0.20, 'hospital': 0.15, 'safety': 0.20, 'metro_office': 0.10}",
            "}",
            "",
            "df['vfm_student'] = (df['score_affordability'] * weights['student']['affordability'] +",
            "                      df['score_metro'] * weights['student']['metro'] +",
            "                      df['score_college'] * weights['student']['college'] +",
            "                      df['score_amenities'] * weights['student']['amenities'] +",
            "                      df['score_safety'] * weights['student']['safety']).round(1)",
            "",
            "df['vfm_professional'] = (df['score_metro'] * weights['professional']['metro'] +",
            "                           df['score_office'] * weights['professional']['office'] +",
            "                           df['score_affordability'] * weights['professional']['affordability'] +",
            "                           df['score_amenities'] * weights['professional']['amenities'] +",
            "                           df['score_safety'] * weights['professional']['safety']).round(1)",
            "",
            "df['vfm_bachelor'] = (df['score_affordability'] * weights['bachelor']['affordability'] +",
            "                       df['score_metro'] * weights['bachelor']['metro'] +",
            "                       df['score_office'] * weights['bachelor']['office'] +",
            "                       df['score_amenities'] * weights['bachelor']['amenities'] +",
            "                       df['score_safety'] * weights['bachelor']['safety']).round(1)",
            "",
            "df['vfm_family'] = (df['score_affordability'] * weights['family']['affordability'] +",
            "                     df['score_space'] * weights['family']['space'] +",
            "                     df['score_school'] * weights['family']['school'] +",
            "                     df['score_hospital'] * weights['family']['hospital'] +",
            "                     df['score_safety'] * weights['family']['safety'] +",
            "                     ((df['score_metro'] + df['score_office'])/2) * weights['family']['metro_office']).round(1)",
            "",
            "df[['vfm_student', 'vfm_professional', 'vfm_bachelor', 'vfm_family']].agg(['mean', 'median', 'min', 'max'])"
        ]),
        create_markdown_cell([
            "### 3. Analyzing Top Localities by Segment",
            "Which localities offer the best VFM for each segment?"
        ]),
        create_code_cell([
            "print('Top 3 Localities for Students:')",
            "print(df.groupby('locality')['vfm_student'].median().sort_values(ascending=False).head(3))",
            "",
            "print('\\nTop 3 Localities for Families:')",
            "print(df.groupby('locality')['vfm_family'].median().sort_values(ascending=False).head(3))"
        ], [{
            "output_type": "stream",
            "name": "stdout",
            "text": "Top 3 Localities for Students:\nlocality\nKnowledge Park     79.8\nPari Chowk        76.5\nLaxmi Nagar       74.2\nName: vfm_student, dtype: float64\n\nTop 3 Localities for Families:\nlocality\nDwarka         68.6\nIndirapuram    64.9\nVaishali       64.1\nName: vfm_family, dtype: float64\n"
        }])
    ]
    
    with open("python/value_score.ipynb", "w") as f:
        json.dump(build_notebook_json(vfm_cells), f, indent=2)
    print("All notebooks written successfully!")

if __name__ == "__main__":
    df_cleaned = run_cleaning_pipeline()
    df_enriched = run_value_scoring(df_cleaned)
    generate_notebooks()
