import csv
import random
import os
import datetime

# Seed for reproducibility
random.seed(42)

# Locality Configurations
# locality: (city, zone, rent_per_sqft_range, avg_size_multiplier, metro_station, nearest_college, nearest_office_hub)
LOCALITY_CONFIGS = {
    # North Delhi
    "Mukherjee Nagar": ("Delhi", "North Delhi", (16, 24), 0.8, "GTB Nagar Metro Station", "SGTB Khalsa College", "Connaught Place"),
    "Model Town": ("Delhi", "North Delhi", (28, 38), 1.1, "Model Town Metro Station", "Miranda House", "Connaught Place"),
    "Kamla Nagar": ("Delhi", "North Delhi", (18, 26), 0.85, "Vishwa Vidyalaya Metro Station", "Kirori Mal College", "Connaught Place"),
    "Civil Lines": ("Delhi", "North Delhi", (35, 50), 1.3, "Civil Lines Metro Station", "St. Stephen's College", "Connaught Place"),
    "Rohini": ("Delhi", "North Delhi", (14, 20), 0.9, "Rohini West Metro Station", "Delhi Technological University (DTU)", "Netaji Subhash Place"),
    
    # Central / West Delhi
    "Karol Bagh": ("Delhi", "Central Delhi", (22, 30), 0.85, "Karol Bagh Metro Station", "Sri Guru Nanak Dev Khalsa College", "Connaught Place"),
    "Patel Nagar": ("Delhi", "West Delhi", (20, 28), 0.9, "Patel Nagar Metro Station", "Kalindi College", "Rajendra Place IT Hub"),
    "Rajinder Nagar": ("Delhi", "Central Delhi", (24, 34), 0.9, "Rajendra Place Metro Station", "Venkateshwara College", "Rajendra Place IT Hub"),
    "Janakpuri": ("Delhi", "West Delhi", (18, 26), 1.2, "Janakpuri West Metro Station", "Bhaskaracharya College", "Janakpuri District Centre"),
    
    # East Delhi
    "Laxmi Nagar": ("Delhi", "East Delhi", (12, 18), 0.8, "Laxmi Nagar Metro Station", "Shyam Lal College", "Noida Sector 62 IT Park"),
    "Shakarpur": ("Delhi", "East Delhi", (11, 16), 0.75, "Nirman Vihar Metro Station", "Bhim Rao Ambedkar College", "Noida Sector 62 IT Park"),
    "Preet Vihar": ("Delhi", "East Delhi", (24, 32), 1.2, "Preet Vihar Metro Station", "Vivekananda College", "Noida Sector 62 IT Park"),
    "Mayur Vihar": ("Delhi", "East Delhi", (20, 28), 1.0, "Mayur Vihar 1 Metro Station", "Shaheed Sukhdev College of Business Studies", "Noida Sector 62 IT Park"),
    
    # South Delhi
    "Saket": ("Delhi", "South Delhi", (28, 38), 1.0, "Saket Metro Station", "Gargi College", "Saket District Centre"),
    "Malviya Nagar": ("Delhi", "South Delhi", (26, 36), 0.95, "Malviya Nagar Metro Station", "College of Vocational Studies", "Okhla Industrial Area"),
    "Hauz Khas": ("Delhi", "South Delhi", (40, 60), 1.2, "Hauz Khas Metro Station", "IIT Delhi", "Okhla Industrial Area"),
    "Green Park": ("Delhi", "South Delhi", (38, 55), 1.25, "Green Park Metro Station", "NIFT Delhi", "Bhikaji Cama Place"),
    "Greater Kailash": ("Delhi", "South Delhi", (42, 65), 1.4, "Kailash Colony Metro Station", "Lady Shri Ram College (LSR)", "Nehru Place IT Hub"),
    "Vasant Kunj": ("Delhi", "South Delhi", (35, 50), 1.5, "Chattarpur Metro Station", "Jawaharlal Nehru University (JNU)", "Cyber City Gurugram"),
    
    # Dwarka
    "Dwarka": ("Delhi", "Dwarka", (18, 25), 1.3, "Dwarka Sector 10 Metro Station", "Netaji Subhas University of Technology (NSUT)", "Gurugram Sector 21 IT Park"),
    
    # NCR Noida
    "Noida Sector 62": ("Noida", "Noida", (14, 20), 1.1, "Noida Sector 62 Metro Station", "JSS Academy of Technical Education", "Noida Sector 62 IT Park"),
    "Noida Sector 15": ("Noida", "Noida", (16, 22), 0.9, "Noida Sector 15 Metro Station", "Amity University Noida", "Noida Sector 16 Commercial Hub"),
    "Noida Sector 137": ("Noida", "Noida", (12, 18), 1.2, "Noida Sector 137 Metro Station", "Amity University Noida", "Noida Expressway Offices"),
    
    # NCR Greater Noida
    "Pari Chowk": ("Greater Noida", "Greater Noida", (9, 14), 1.2, "Pari Chowk Metro Station", "Galgotias University", "Greater Noida Industrial Area"),
    "Knowledge Park": ("Greater Noida", "Greater Noida", (8, 13), 1.1, "Knowledge Park II Metro Station", "Sharda University", "Greater Noida Industrial Area"),
    
    # NCR Ghaziabad
    "Indirapuram": ("Ghaziabad", "Ghaziabad", (12, 17), 1.2, "Vaishali Metro Station", "ABES Engineering College", "Noida Sector 62 IT Park"),
    "Vaishali": ("Ghaziabad", "Ghaziabad", (14, 20), 1.1, "Vaishali Metro Station", "Inderprastha Dental College", "Noida Sector 62 IT Park"),
    
    # NCR Gurugram
    "DLF Phase 3": ("Gurugram", "Gurugram", (26, 38), 0.9, "Phase 3 Metro Station", "Dronacharya College of Engineering", "DLF Cyber City"),
    "Gurugram Sector 45": ("Gurugram", "Gurugram", (22, 32), 1.1, "HUDA City Centre Metro Station", "Ansal University", "Golf Course Road Offices"),
    "Gurugram Sector 56": ("Gurugram", "Gurugram", (18, 26), 1.2, "Sector 56 Metro Station", "IILM University", "Golf Course Road Offices"),
    "Golf Course Road": ("Gurugram", "Gurugram", (45, 75), 1.5, "Sector 42-43 Metro Station", "GD Goenka University", "Golf Course Road Offices"),
}

PROPERTY_TYPES_CONFIG = {
    "1RK": (1, 1, (250, 450)),
    "1BHK": (1, 1, (400, 650)),
    "2BHK": (2, 2, (750, 1100)),
    "3BHK": (3, 2, (1200, 1800)),
    "4BHK": (4, 4, (1800, 2600))
}

FURNISHING_FORMATS = ["Furnished", "fully-furnished", "Semi-Furnished", "semi-furnished", "unfurnished", "Unfurnished"]
YES_NO_FORMATS = [("Yes", "No"), ("yes", "no"), ("Y", "N"), ("1", "0")]

def get_messy_boolean(val):
    fmt = random.choice(YES_NO_FORMATS)
    return fmt[0] if val else fmt[1]

def get_messy_distance(dist_km):
    if random.random() < 0.15:
        return ""
    r = random.random()
    if r < 0.3:
        return f"{dist_km} km"
    elif r < 0.6 and dist_km < 1.0:
        return f"{int(dist_km * 1000)}m"
    elif r < 0.8:
        return f"{dist_km}km"
    else:
        return str(dist_km)

def get_messy_rent(rent):
    r = random.random()
    if r < 0.25:
        return f"₹{rent:,}"
    elif r < 0.50:
        return f"{rent // 1000}k"
    elif r < 0.75:
        return f"Rs. {rent:,}/month"
    else:
        return str(rent)

def generate_dataset():
    listings = []
    
    for i in range(1, 851):
        prop_id = f"PROP_{i:03d}"
        locality = random.choice(list(LOCALITY_CONFIGS.keys()))
        city, zone, rent_sqft_range, size_mult, metro, college, office = LOCALITY_CONFIGS[locality]
        
        # Inconsistent Locality Cases
        loc_mess = locality
        r_case = random.random()
        if r_case < 0.15:
            loc_mess = locality.lower()
        elif r_case < 0.3:
            loc_mess = locality.upper()
        elif "Sector" in locality and random.random() < 0.4:
            loc_mess = locality.replace("Sector", "Sec")
        elif "Sector" in locality and random.random() < 0.4:
            loc_mess = locality.replace("Sector ", "Sec-")
            
        prop_type = random.choices(["1RK", "1BHK", "2BHK", "3BHK", "4BHK"], weights=[15, 25, 35, 20, 5], k=1)[0]
        bedrooms, bathrooms, size_range = PROPERTY_TYPES_CONFIG[prop_type]
        
        min_size, max_size = size_range
        area = int(random.uniform(min_size, max_size) * size_mult)
        
        base_rent_rate = random.uniform(rent_sqft_range[0], rent_sqft_range[1])
        rent = int(area * base_rent_rate)
        
        furnishing = random.choice(FURNISHING_FORMATS)
        is_furnished = "furnish" in furnishing.lower() and "semi" not in furnishing.lower()
        is_semi = "semi" in furnishing.lower()
        
        if is_furnished:
            rent = int(rent * 1.25)
        elif is_semi:
            rent = int(rent * 1.1)
            
        rent = (rent // 500) * 500
        if rent < 5000:
            rent = 5000
            
        security_multiplier = random.choices([1, 2, 3], weights=[15, 75, 10], k=1)[0]
        security_deposit = rent * security_multiplier
        
        maintenance = 0
        if random.random() < 0.7:
            maintenance = int(area * random.uniform(1.5, 3.5))
            maintenance = (maintenance // 100) * 100
            
        electricity = int((area * random.uniform(1.2, 2.2)) + (300 if is_furnished else 100))
        electricity = (electricity // 100) * 100
        
        total_floors = random.choice([3, 4, 5, 8, 12, 15, 20, 24])
        floor = random.randint(0, total_floors)
        age = random.randint(0, 15)
        
        parking = get_messy_boolean(random.choices([True, False], weights=[60, 40], k=1)[0] if prop_type not in ["1RK", "1BHK"] else random.choices([True, False], weights=[20, 80], k=1)[0])
        balcony = get_messy_boolean(random.random() < 0.75)
        lift = get_messy_boolean(total_floors > 4 and random.random() < 0.95)
        power_backup = get_messy_boolean(random.random() < 0.6)
        water_supply = random.choice(["24 Hours", "12 Hours", "4 Hours"])
        ac = get_messy_boolean(is_furnished or random.random() < 0.4)
        wifi = get_messy_boolean(random.random() < 0.5)
        food = get_messy_boolean(random.random() < 0.15)
        laundry = get_messy_boolean(random.random() < 0.2)
        gym = get_messy_boolean(total_floors > 8 and random.random() < 0.4)
        cctv = get_messy_boolean(random.random() < 0.65)
        security = get_messy_boolean(random.random() < 0.7)
        housekeeping = get_messy_boolean(random.random() < 0.3)
        
        metro_dist = round(random.uniform(0.1, 4.5), 2)
        college_dist = round(random.uniform(0.3, 10.0), 2)
        office_dist = round(random.uniform(0.5, 15.0), 2)
        school_dist = round(random.uniform(0.2, 5.0), 2)
        hospital_dist = round(random.uniform(0.3, 6.0), 2)
        
        if prop_type in ["1RK", "1BHK"] and (wifi == "Yes" or ac == "Yes" or wifi == "Y" or ac == "Y" or wifi == "1" or ac == "1") and rent <= 15000:
            segment = "Student"
        elif prop_type in ["1BHK", "2BHK"] and metro_dist <= 1.5 and rent <= 25000:
            segment = "Working Bachelor"
        elif prop_type in ["2BHK", "3BHK"] and metro_dist <= 2.0 and office_dist <= 8.0:
            segment = "Working Professional"
        else:
            segment = "Family"
            
        rating = round(random.uniform(3.2, 4.9), 1)
        reviews = random.randint(0, 85)
        available = get_messy_boolean(random.random() < 0.85)
        
        days_ago = random.randint(0, 45)
        listing_date = (datetime.date.today() - datetime.timedelta(days=days_ago)).isoformat()
        source = random.choice(["MagicBricks", "NoBroker", "99acres", "Housing.com"])
        
        title = f"{prop_type} Apartment in {locality}"
        if is_furnished:
            title = f"Fully Furnished {title}"
        elif is_semi:
            title = f"Semi-Furnished {title}"
            
        is_dup = i in [10, 55, 110, 220, 330, 440, 550, 660, 770, 810]
        
        record = {
            "property_id": prop_id if not is_dup else f"PROP_{i-1:03d}",
            "property_type": prop_type,
            "listing_title": title,
            "locality": loc_mess,
            "city": city,
            "zone": zone,
            "renter_segment": segment,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "floor": floor,
            "total_floors": total_floors,
            "property_age": age,
            "monthly_rent": get_messy_rent(rent) if not is_dup else get_messy_rent(rent),
            "security_deposit": get_messy_rent(security_deposit) if random.random() < 0.9 else str(security_deposit),
            "maintenance": get_messy_rent(maintenance) if maintenance > 0 and random.random() < 0.8 else ("" if random.random() < 0.5 else "0"),
            "electricity_estimate": str(electricity) if random.random() < 0.8 else "",
            "area_sqft": str(area) if random.random() < 0.9 else f"{area} sq.ft.",
            "furnishing_status": furnishing,
            "parking": parking,
            "balcony": balcony,
            "lift": lift,
            "power_backup": power_backup,
            "water_supply": water_supply,
            "ac": ac,
            "wifi": wifi,
            "food": food,
            "laundry": laundry,
            "gym": gym,
            "cctv": cctv,
            "security": security,
            "housekeeping": housekeeping,
            "metro_station": metro,
            "metro_distance_km": get_messy_distance(metro_dist),
            "nearest_college": college,
            "college_distance_km": get_messy_distance(college_dist),
            "nearest_office_hub": office,
            "office_distance_km": get_messy_distance(office_dist),
            "school_distance_km": get_messy_distance(school_dist),
            "hospital_distance_km": get_messy_distance(hospital_dist),
            "rating": str(rating),
            "review_count": str(reviews),
            "available": available,
            "listing_date": listing_date,
            "source": source
        }
        
        if i == 50:
            record["monthly_rent"] = "₹1,50,000"
            record["listing_title"] = "Super Premium 1RK (Outlier)"
        elif i == 150:
            record["monthly_rent"] = "1.2k"
            record["listing_title"] = "Huge 4BHK for dirt cheap"
        
        listings.append(record)

    return listings

def save_raw_csv(listings):
    os.makedirs("/Users/prachichauhan/.gemini/antigravity/scratch/delhi-ncr-rental-market-intelligence/data/raw", exist_ok=True)
    filepath = "/Users/prachichauhan/.gemini/antigravity/scratch/delhi-ncr-rental-market-intelligence/data/raw/rental_listings_raw.csv"
    
    keys = listings[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(listings)
    print(f"Generated raw dataset with {len(listings)} rows at {filepath}")

if __name__ == "__main__":
    listings = generate_dataset()
    save_raw_csv(listings)
