-- Delhi/NCR Rental Market Intelligence - Analytical Queries

-- 1. Median/Average Rent and Size by Locality
-- Calculates the statistical summary of rent and square footage for each locality
SELECT 
    l.locality,
    l.city,
    COUNT(p.property_id) AS total_listings,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_monthly_rent,
    ROUND(AVG(p.area_sqft), 0) AS avg_area_sqft,
    ROUND(AVG(pr.monthly_rent::decimal / p.area_sqft), 2) AS avg_rent_per_sqft
FROM properties p
JOIN locations l ON p.location_id = l.location_id
JOIN pricing pr ON p.property_id = pr.property_id
GROUP BY l.locality, l.city
ORDER BY avg_monthly_rent DESC;


-- 2. Top 5 Most Expensive Localities (by Average Rent)
SELECT 
    l.locality,
    l.city,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_rent
FROM properties p
JOIN locations l ON p.location_id = l.location_id
JOIN pricing pr ON p.property_id = pr.property_id
GROUP BY l.locality, l.city
ORDER BY avg_rent DESC
LIMIT 5;


-- 3. Top 5 Cheapest Localities (by Average Rent)
SELECT 
    l.locality,
    l.city,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_rent
FROM properties p
JOIN locations l ON p.location_id = l.location_id
JOIN pricing pr ON p.property_id = pr.property_id
GROUP BY l.locality, l.city
ORDER BY avg_rent ASC
LIMIT 5;


-- 4. Rent per Sq.Ft. by Locality and City
SELECT 
    l.city,
    l.locality,
    ROUND(AVG(pr.monthly_rent::decimal / p.area_sqft), 2) AS rent_per_sqft
FROM properties p
JOIN locations l ON p.location_id = l.location_id
JOIN pricing pr ON p.property_id = pr.property_id
GROUP BY l.city, l.locality
ORDER BY l.city, rent_per_sqft DESC;


-- 5. Rent by Property Type (1RK, 1BHK, 2BHK, 3BHK, 4BHK)
SELECT 
    p.property_type,
    COUNT(p.property_id) AS total_listings,
    ROUND(MIN(pr.monthly_rent), 0) AS min_rent,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_rent,
    ROUND(MAX(pr.monthly_rent), 0) AS max_rent
FROM properties p
JOIN pricing pr ON p.property_id = pr.property_id
GROUP BY p.property_type
ORDER BY avg_rent ASC;


-- 6. Rent by Furnishing Status (Premium Analysis)
-- Shows how much extra landlords charge for furnished properties
SELECT 
    p.furnishing_status,
    COUNT(p.property_id) AS total_listings,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_rent,
    ROUND(AVG(pr.monthly_rent::decimal / p.area_sqft), 2) AS rent_per_sqft
FROM properties p
JOIN pricing pr ON p.property_id = pr.property_id
GROUP BY p.furnishing_status
ORDER BY avg_rent DESC;


-- 7. Amenity Rental Premiums
-- Calculates the price premium for key amenities: AC, Parking, Gym, and Power Backup
SELECT 
    'AC' AS amenity_name,
    a.ac AS amenity_present,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_rent,
    ROUND(AVG(pr.monthly_rent) - LAG(ROUND(AVG(pr.monthly_rent), 0)) OVER (ORDER BY a.ac), 0) AS premium
FROM amenities a
JOIN pricing pr ON a.property_id = pr.property_id
GROUP BY a.ac

UNION ALL

SELECT 
    'Parking' AS amenity_name,
    a.parking AS amenity_present,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_rent,
    ROUND(AVG(pr.monthly_rent) - LAG(ROUND(AVG(pr.monthly_rent), 0)) OVER (ORDER BY a.parking), 0) AS premium
FROM amenities a
JOIN pricing pr ON a.property_id = pr.property_id
GROUP BY a.parking;


-- 8. Average Rent by Targeted Renter Segment
SELECT 
    li.renter_segment,
    COUNT(p.property_id) AS total_listings,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_rent,
    ROUND(AVG(p.area_sqft), 0) AS avg_size_sqft
FROM properties p
JOIN pricing pr ON p.property_id = pr.property_id
JOIN listings li ON p.property_id = li.property_id
GROUP BY li.renter_segment
ORDER BY avg_rent DESC;


-- 9. Metro Proximity vs Monthly Rent
-- Group properties by distance to the nearest metro station to understand proximity pricing
SELECT 
    CASE 
        WHEN c.metro_distance_km <= 0.5 THEN '1. Near (<500m)'
        WHEN c.metro_distance_km <= 1.0 THEN '2. Moderate (500m-1km)'
        WHEN c.metro_distance_km <= 2.0 THEN '3. Distant (1km-2km)'
        ELSE '4. Remote (>2km)'
    END AS metro_proximity,
    COUNT(p.property_id) AS total_listings,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_rent,
    ROUND(AVG(pr.monthly_rent::decimal / p.area_sqft), 2) AS rent_per_sqft
FROM properties p
JOIN connectivity c ON p.property_id = c.property_id
JOIN pricing pr ON p.property_id = pr.property_id
GROUP BY metro_proximity
ORDER BY metro_proximity;


-- 10. Regional Comparison: Delhi vs Noida vs Gurugram vs Ghaziabad vs Greater Noida
SELECT 
    l.city,
    COUNT(p.property_id) AS total_listings,
    ROUND(AVG(pr.monthly_rent), 0) AS avg_rent,
    ROUND(AVG(pr.monthly_rent::decimal / p.area_sqft), 2) AS avg_rent_per_sqft,
    ROUND(AVG(p.area_sqft), 0) AS avg_area_sqft,
    ROUND(AVG(c.metro_distance_km), 2) AS avg_metro_distance_km
FROM properties p
JOIN locations l ON p.location_id = l.location_id
JOIN pricing pr ON p.property_id = pr.property_id
JOIN connectivity c ON p.property_id = c.property_id
GROUP BY l.city
ORDER BY avg_rent DESC;


-- 11. Complex Value-For-Money Score Calculator in SQL (Student Profile Example)
-- We calculate a customized VFM Score (0-100) using weights:
-- Affordability (30%), Metro Proximity (25%), College Proximity (20%), Amenities (15%), Safety (10%)
WITH score_components AS (
    SELECT 
        p.property_id,
        l.locality,
        pr.monthly_rent,
        -- Affordability: higher score for lower rent
        (100.0 - (pr.monthly_rent::decimal / (SELECT MAX(monthly_rent) FROM pricing) * 100.0)) AS score_affordability,
        -- Metro Proximity: exponential decay based on distance (0km = 100, 1.25km = 36, etc.)
        (100.0 * EXP(-0.8 * c.metro_distance_km)) AS score_metro,
        -- College Proximity
        (100.0 * EXP(-0.8 * c.college_distance_km)) AS score_college,
        -- Amenities: percentage of present standard student amenities (wifi, ac, power_backup, laundry, cctv)
        ((
            CASE WHEN a.wifi = 'Yes' THEN 1 ELSE 0 END +
            CASE WHEN a.ac = 'Yes' THEN 1 ELSE 0 END +
            CASE WHEN a.power_backup = 'Yes' THEN 1 ELSE 0 END +
            CASE WHEN a.laundry = 'Yes' THEN 1 ELSE 0 END +
            CASE WHEN a.cctv = 'Yes' THEN 1 ELSE 0 END
        )::decimal / 5.0 * 100.0) AS score_amenities,
        -- Safety: combined zone score and security measures
        (
            CASE 
                WHEN l.zone = 'South Delhi' THEN 85
                WHEN l.zone = 'Dwarka' THEN 80
                WHEN l.zone = 'Gurugram' THEN 80
                WHEN l.zone = 'Noida' THEN 75
                WHEN l.zone = 'North Delhi' THEN 70
                WHEN l.zone = 'West Delhi' THEN 70
                WHEN l.zone = 'Central Delhi' THEN 70
                ELSE 65
            END + 
            CASE WHEN a.cctv = 'Yes' THEN 10 ELSE 0 END + 
            CASE WHEN a.security = 'Yes' THEN 10 ELSE 0 END
        ) AS score_safety
    FROM properties p
    JOIN locations l ON p.location_id = l.location_id
    JOIN pricing pr ON p.property_id = pr.property_id
    JOIN connectivity c ON p.property_id = c.property_id
    JOIN amenities a ON p.property_id = a.property_id
)
SELECT 
    property_id,
    locality,
    monthly_rent,
    ROUND(score_affordability, 1) AS affordability_idx,
    ROUND(score_metro, 1) AS metro_idx,
    ROUND(score_college, 1) AS college_idx,
    ROUND((
        score_affordability * 0.30 + 
        score_metro * 0.25 + 
        score_college * 0.20 + 
        score_amenities * 0.15 + 
        LEAST(score_safety, 100.0) * 0.10
    )::decimal, 1) AS student_vfm_score
FROM score_components
ORDER BY student_vfm_score DESC
LIMIT 10;
