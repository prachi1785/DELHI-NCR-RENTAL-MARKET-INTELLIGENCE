# Dataset Documentation

This directory contains the raw and cleaned datasets for the Delhi/NCR Rental Market Intelligence project.

## Dataset Structure

- **`raw/rental_listings_raw.csv`**: The raw, uncleaned prototype dataset. It contains intentionally introduced duplicates, inconsistent locality names, varied formats for pricing (e.g. `₹15,000`, `15k`, `Rs. 12,000/month`), mixed boolean representation, string-based distances with units (`500m`, `1.2 km`), and missing values.
- **`processed/rental_listings_cleaned.csv`**: The clean, structured, and validated analytical dataset. It includes standardized column types, normalized text values, and pre-calculated Value-for-Money (VFM) scores for the four target renter profiles (Student, Working Professional, Working Bachelor, Family).

## Data Glossary

| Column Name | Type | Description | Sample Value (Raw) | Standardized Value |
| :--- | :--- | :--- | :--- | :--- |
| **`property_id`** | String | Unique identifier for each listing | `PROP_001` | `PROP_001` |
| **`property_type`** | Categorical | The layout configuration of the flat | `1BHK`, `2BHK`, `3BHK`, `1RK` | `1BHK` |
| **`listing_title`** | String | Public listing headline | `"1 BHK in Saket"` | `"Semi-Furnished 1 BHK in Saket"` |
| **`locality`** | Categorical | Sub-area name in Delhi/NCR | `saket`, `Saket` | `Saket` |
| **`city`** | Categorical | City name | `Delhi` | `Delhi` |
| **`zone`** | Categorical | Regional division | `South Delhi` | `South Delhi` |
| **`bedrooms`** | Integer | Number of bedrooms | `1` | `1` |
| **`bathrooms`** | Integer | Number of bathrooms | `1` | `1` |
| **`floor`** | Integer | Floor number of the flat | `2` | `2` |
| **`total_floors`** | Integer | Total floors in the building | `4` | `4` |
| **`property_age`** | Integer | Property age in years | `5` | `5` |
| **`monthly_rent`** | Integer | Core monthly rent in INR (₹) | `₹15,000`, `15k` | `15000` |
| **`security_deposit`**| Integer | Security deposit in INR (₹) | `30000` | `30000` |
| **`maintenance`** | Integer | Monthly society maintenance fees in INR (₹)| `1200` | `1200` |
| **`electricity_estimate`**| Integer | Estimated monthly electricity cost | `""` | `1850` (imputed) |
| **`area_sqft`** | Integer | Carpet area in square feet | `650 sq.ft.` | `650` |
| **`furnishing_status`**| Categorical | Furnishing condition | `fully-furnished` | `Furnished` |
| **`parking`** | Boolean (Y/N)| Presence of dedicated parking spot | `Y`, `1`, `yes` | `Yes` |
| **`balcony`** | Boolean (Y/N)| Presence of a balcony | `N`, `0`, `no` | `No` |
| **`lift`** | Boolean (Y/N)| Elevator accessibility | `Yes` | `Yes` |
| **`power_backup`** | Boolean (Y/N)| Uninterrupted power supply availability | `Yes` | `Yes` |
| **`water_supply`** | Categorical | Daily availability duration of fresh water | `24 Hours` | `24 Hours` |
| **`ac`** | Boolean (Y/N)| Air conditioning installed | `Yes` | `Yes` |
| **`wifi`** | Boolean (Y/N)| High-speed internet setup | `Yes` | `Yes` |
| **`food`** | Boolean (Y/N)| Meals/Tiffin services included | `No` | `No` |
| **`laundry`** | Boolean (Y/N)| Laundry/Washing machine access | `No` | `No` |
| **`gym`** | Boolean (Y/N)| Society gym access | `No` | `No` |
| **`cctv`** | Boolean (Y/N)| Closed-circuit camera security | `Yes` | `Yes` |
| **`security`** | Boolean (Y/N)| Physical guard presence | `Yes` | `Yes` |
| **`housekeeping`** | Boolean (Y/N)| Housekeeping/Cleaning services | `No` | `No` |
| **`metro_station`** | String | Name of the nearest Delhi Metro station | `Saket Metro Station` | `Saket Metro Station` |
| **`metro_distance_km`**| Float | Distance to the metro station in kilometers | `500m` | `0.50` |
| **`nearest_college`** | String | Nearest educational institution name | `Gargi College` | `Gargi College` |
| **`college_distance_km`**| Float | Distance to the college in kilometers | `1.2 km` | `1.20` |
| **`nearest_office_hub`**| String | Nearest commercial employment hub name | `Saket District Centre`| `Saket District Centre`|
| **`office_distance_km`**| Float | Distance to the office hub in kilometers | `1.5` | `1.50` |
| **`school_distance_km`**| Float | Distance to nearest school in km | `0.4` | `0.40` |
| **`hospital_distance_km`**| Float | Distance to nearest hospital in km | `0.6` | `0.60` |
| **`rating`** | Float | Renter rating (1.0 to 5.0) | `4.2` | `4.2` |
| **`review_count`** | Integer | Total reviews written | `18` | `18` |
| **`available`** | Boolean (Y/N)| Availability status of the listing | `Yes` | `Yes` |
| **`listing_date`** | Date | Date when listing was added (YYYY-MM-DD) | `2026-08-10` | `2026-08-10` |
| **`source`** | String | Original platform source | `NoBroker` | `NoBroker` |
| **`vfm_student`** | Float | Value Score (0-100) for Students | *(new column)* | `68.2` |
| **`vfm_professional`**| Float | Value Score (0-100) for Professionals | *(new column)* | `72.1` |
| **`vfm_bachelor`** | Float | Value Score (0-100) for Bachelors | *(new column)* | `65.8` |
| **`vfm_family`** | Float | Value Score (0-100) for Families | *(new column)* | `70.4` |

## Data Collection & Sampling Methodology

- **Sampling:** 31 localities across Delhi/NCR were chosen to represent diverse rental sub-markets: student hubs (North Delhi/East Delhi), tech-centric clusters (Gurugram/Noida), residential planned hubs (Dwarka/Ghaziabad), and premium residential markets (South Delhi).
- **Listing Source Mix:** Modeled on real listings distributed across major rental portals (NoBroker, MagicBricks, Housing.com, 99acres).
- **Proximity:** Distances were calculated using real geographical station nodes to major hubs (e.g. Cyber City, Rajendra Place, Delhi University).
