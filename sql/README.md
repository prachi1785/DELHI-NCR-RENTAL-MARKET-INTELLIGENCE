# Relational Database Schema & SQL Analytics

This folder contains the normalized SQL database structure and a suite of analytical business queries to evaluate the Delhi/NCR rental market.

## Schema Overview

The database is normalized to eliminate redundancy and support flexible slice-and-dice queries. The schema comprises six related tables:

1. **`locations`**: Stores regional mappings (`locality`, `city`, `zone`).
2. **`properties`**: Holds static structural details of properties (`property_type`, `bedrooms`, `bathrooms`, `area_sqft`, `furnishing_status`, `floor`, etc.).
3. **`pricing`**: Tracks rents, security deposits, maintenance fees, and electricity cost estimates.
4. **`amenities`**: Maps property amenity presence flags (`parking`, `balcony`, `lift`, `ac`, `wifi`, etc.) as 'Yes'/'No'.
5. **`connectivity`**: Records distance details to key infrastructure (metro, offices, colleges, hospitals, schools).
6. **`listings`**: Handles the market listing meta-data (`rating`, `review_count`, `available`, `listing_date`, `source`, and the target `renter_segment`).

```mermaid
erDiagram
    locations ||--o{ properties : "contains"
    properties ||--|| pricing : "has cost"
    properties ||--|| amenities : "offers"
    properties ||--|| connectivity : "links"
    properties ||--|| listings : "publishes"

    locations {
        int location_id PK
        string locality
        string city
        string zone
    }

    properties {
        string property_id PK
        int location_id FK
        string property_type
        int bedrooms
        int bathrooms
        int area_sqft
        string furnishing_status
        int floor
        int total_floors
        int property_age
    }

    pricing {
        string property_id PK, FK
        int monthly_rent
        int security_deposit
        int maintenance
        int electricity_estimate
    }

    amenities {
        string property_id PK, FK
        string parking
        string balcony
        string lift
        string power_backup
        string water_supply
        string ac
        string wifi
        string food
        string laundry
        string gym
        string cctv
        string security
        string housekeeping
    }

    connectivity {
        string property_id PK, FK
        string metro_station
        decimal metro_distance_km
        string nearest_college
        decimal college_distance_km
        string nearest_office_hub
        decimal office_distance_km
        decimal school_distance_km
        decimal hospital_distance_km
    }

    listings {
        string property_id PK, FK
        string renter_segment
        decimal rating
        int review_count
        string available
        date listing_date
        string source
    }
```

## How to Load Data into SQL

A typical ETL pipeline can load `data/processed/rental_listings_cleaned.csv` into a SQL database (e.g., PostgreSQL or MySQL) using Python's `sqlalchemy` and `pandas`, or via native SQL loading.

### Example: Loading via Python
```python
import pandas as pd
from sqlalchemy import create_engine

# Read cleaned CSV
df = pd.read_csv('../data/processed/rental_listings_cleaned.csv')

# Connect to DB
engine = create_engine('postgresql://user:password@localhost:5432/delhirental')

# 1. Populate locations (unique values)
locations_df = df[['locality', 'city', 'zone']].drop_duplicates().reset_index(drop=True)
locations_df.to_sql('locations', engine, if_exists='append', index=False)

# Fetch location ids
loc_db = pd.read_sql('SELECT location_id, locality FROM locations', engine)
df = df.merge(loc_db, on='locality')

# 2. Populate properties
properties_df = df[['property_id', 'location_id', 'property_type', 'bedrooms', 'bathrooms', 'area_sqft', 'furnishing_status', 'floor', 'total_floors', 'property_age']]
properties_df.to_sql('properties', engine, if_exists='append', index=False)

# 3. Populate pricing
pricing_df = df[['property_id', 'monthly_rent', 'security_deposit', 'maintenance', 'electricity_estimate']]
pricing_df.to_sql('pricing', engine, if_exists='append', index=False)

# 4. Populate amenities
amenity_cols = ['parking', 'balcony', 'lift', 'power_backup', 'water_supply', 'ac', 'wifi', 'food', 'laundry', 'gym', 'cctv', 'security', 'housekeeping']
amenities_df = df[['property_id'] + amenity_cols]
amenities_df.to_sql('amenities', engine, if_exists='append', index=False)

# 5. Populate connectivity
conn_cols = ['metro_station', 'metro_distance_km', 'nearest_college', 'college_distance_km', 'nearest_office_hub', 'office_distance_km', 'school_distance_km', 'hospital_distance_km']
connectivity_df = df[['property_id'] + conn_cols]
connectivity_df.to_sql('connectivity', engine, if_exists='append', index=False)

# 6. Populate listings
listings_df = df[['property_id', 'renter_segment', 'rating', 'review_count', 'available', 'listing_date', 'source']]
listings_df.to_sql('listings', engine, if_exists='append', index=False)
```

## Running Analytical Queries

The queries in `analysis_queries.sql` analyze key business questions, including:
- Identifying rental pricing benchmarks by region (Delhi vs Noida vs Gurugram vs Ghaziabad).
- Quantifying the exact rent premiums associated with high-demand amenities (AC, Parking).
- Replicating our multi-attribute decision scoring (VFM Score) inside SQL using arithmetic functions (exponential decays and weights).
