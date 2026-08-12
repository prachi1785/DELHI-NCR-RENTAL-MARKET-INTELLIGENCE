-- Delhi/NCR Rental Market Intelligence Normalized Schema
-- Database: PostgreSQL or MySQL compatible

-- 1. locations Table
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    locality VARCHAR(100) UNIQUE NOT NULL,
    city VARCHAR(50) NOT NULL,
    zone VARCHAR(50) NOT NULL
);

-- 2. properties Table
CREATE TABLE properties (
    property_id VARCHAR(50) PRIMARY KEY,
    location_id INT REFERENCES locations(location_id),
    property_type VARCHAR(10) NOT NULL, -- '1RK', '1BHK', '2BHK', '3BHK', '4BHK'
    bedrooms INT NOT NULL,
    bathrooms INT NOT NULL,
    area_sqft INT NOT NULL,
    furnishing_status VARCHAR(20) NOT NULL, -- 'Furnished', 'Semi-Furnished', 'Unfurnished'
    floor INT NOT NULL,
    total_floors INT NOT NULL,
    property_age INT NOT NULL
);

-- 3. pricing Table
CREATE TABLE pricing (
    property_id VARCHAR(50) PRIMARY KEY REFERENCES properties(property_id),
    monthly_rent INT NOT NULL,
    security_deposit INT NOT NULL,
    maintenance INT NOT NULL,
    electricity_estimate INT NOT NULL
);

-- 4. amenities Table
CREATE TABLE amenities (
    property_id VARCHAR(50) PRIMARY KEY REFERENCES properties(property_id),
    parking VARCHAR(3) NOT NULL, -- 'Yes', 'No'
    balcony VARCHAR(3) NOT NULL,
    lift VARCHAR(3) NOT NULL,
    power_backup VARCHAR(3) NOT NULL,
    water_supply VARCHAR(20) NOT NULL,
    ac VARCHAR(3) NOT NULL,
    wifi VARCHAR(3) NOT NULL,
    food VARCHAR(3) NOT NULL,
    laundry VARCHAR(3) NOT NULL,
    gym VARCHAR(3) NOT NULL,
    cctv VARCHAR(3) NOT NULL,
    security VARCHAR(3) NOT NULL,
    housekeeping VARCHAR(3) NOT NULL
);

-- 5. connectivity Table
CREATE TABLE connectivity (
    property_id VARCHAR(50) PRIMARY KEY REFERENCES properties(property_id),
    metro_station VARCHAR(100) NOT NULL,
    metro_distance_km DECIMAL(4, 2) NOT NULL,
    nearest_college VARCHAR(100) NOT NULL,
    college_distance_km DECIMAL(4, 2) NOT NULL,
    nearest_office_hub VARCHAR(100) NOT NULL,
    office_distance_km DECIMAL(4, 2) NOT NULL,
    school_distance_km DECIMAL(4, 2) NOT NULL,
    hospital_distance_km DECIMAL(4, 2) NOT NULL
);

-- 6. listings Table
CREATE TABLE listings (
    property_id VARCHAR(50) PRIMARY KEY REFERENCES properties(property_id),
    renter_segment VARCHAR(50) NOT NULL, -- 'Student', 'Working Professional', 'Working Bachelor', 'Family'
    rating DECIMAL(2, 1) NOT NULL,
    review_count INT NOT NULL,
    available VARCHAR(3) NOT NULL, -- 'Yes', 'No'
    listing_date DATE NOT NULL,
    source VARCHAR(50) NOT NULL
);
