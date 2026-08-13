import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# Page Configurations
st.set_page_config(
    page_title="Delhi/NCR Rental Market Intelligence",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Slate UI CSS Overrides
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    /* Consolidate typography and backgrounds across environments */
    html, body, [class*="css"], .stApp, .stMarkdown, .kpi-container, .stSelectbox, .stNumberInput, .stRadio, .stSlider {
        font-family: 'Manrope', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    .stApp { 
        background-color: #f8fafc !important; 
    }
    
    /* Parity for top padding and page spacing */
    .block-container { 
        padding-top: 1.5rem !important; 
        padding-bottom: 2.0rem !important; 
        max-width: 1200px !important; 
        margin: 0 auto !important;
    }
    
    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Manrope', sans-serif !important;
        color: #0f172a !important; 
        font-weight: 700 !important; 
        letter-spacing: -0.02em !important;
    }

    /* Sidebar controls and navigation tweaks */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
        width: 270px !important;
        min-width: 270px !important;
        max-width: 270px !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 270px !important;
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Hide the radio dot circles completely */
    div[role="radiogroup"] label span[data-baseweb="radio"],
    div[role="radiogroup"] label div[data-checked],
    div[role="radiogroup"] label div:first-child:not([data-testid="stMarkdownContainer"]),
    div[role="radiogroup"] label svg {
        display: none !important;
    }
    
    /* Style label text for horizontal filters block to match React uppercase styling */
    [data-testid="stHorizontalBlock"] label p {
        font-size: 10px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #475569 !important;
    }
    
    /* Sidebar radio buttons styling */
    div[role="radiogroup"] label {
        background-color: transparent !important;
        padding: 0.6rem 0.8rem !important;
        border-radius: 4px !important;
        margin-bottom: 0.25rem !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    div[role="radiogroup"] label:has(div[data-checked="true"]) {
        background-color: #1e293b !important; /* Active slate-navy background */
    }
    div[role="radiogroup"] label:has(div[data-checked="true"]) p,
    div[role="radiogroup"] label:has(div[data-checked="true"]) div {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    div[role="radiogroup"] label p, div[role="radiogroup"] label div {
        color: #94a3b8 !important;
        font-size: 13px !important;
        transition: color 0.15s ease !important;
        margin: 0 !important;
    }
    div[role="radiogroup"] label:hover p, div[role="radiogroup"] label:hover div {
        color: #ffffff !important;
    }
    
    /* Vector Line Icons via SVG background injection */
    div[role="radiogroup"] label p::before {
        content: "";
        display: inline-block;
        width: 14px;
        height: 14px;
        margin-right: 10px;
        vertical-align: -2px;
        background-repeat: no-repeat;
        background-size: contain;
    }
    /* Inactive States */
    div[role="radiogroup"] label:nth-child(1) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%2394a3b8%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpath d=%27m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z%27/%3E%3Cpolyline points=%279 22 9 12 15 12 15 22%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:nth-child(2) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%2394a3b8%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpolyline points=%2722 7 13.5 15.5 8.5 10.5 2 17%27/%3E%3Cpolyline points=%2716 7 22 7 22 13%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:nth-child(3) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%2394a3b8%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpolygon points=%273 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21%27/%3E%3Cline x1=%279%27 x2=%279%27 y1=%273%27 y2=%2718%27/%3E%3Cline x1=%2715%27 x2=%2715%27 y1=%276%27 y2=%2721%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:nth-child(4) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%2394a3b8%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpath d=%27M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2%27/%3E%3Ccircle cx=%279%27 cy=%277%27 r=%274%27/%3E%3Cpath d=%27M22 21v-2a4 4 0 0 0-3-3.87%27/%3E%3Cpath d=%27M16 3.13a4 4 0 0 1 0 7.75%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:nth-child(5) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%2394a3b8%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Ccircle cx=%2711%27 cy=%2711%27 r=%278%27/%3E%3Cline x1=%2721%27 x2=%2716.65%27 y1=%2721%27 y2=%2716.65%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:nth-child(6) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%2394a3b8%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Crect width=%2718%27 height=%2718%27 x=%273%27 y=%273%27 rx=%272%27/%3E%3Cline x1=%2712%27 x2=%2712%27 y1=%273%27 y2=%2721%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:nth-child(7) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%2394a3b8%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Ccircle cx=%2712%27 cy=%2712%27 r=%2710%27/%3E%3Cline x1=%2712%27 x2=%2712%27 y1=%2716%27 y2=%2712%27/%3E%3Cline x1=%2712%27 x2=%2712.01%27 y1=%278%27 y2=%278%27/%3E%3C/svg%3E");
    }
    /* Active States */
    div[role="radiogroup"] label:has(div[data-checked="true"]):nth-child(1) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%23ffffff%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpath d=%27m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z%27/%3E%3Cpolyline points=%279 22 9 12 15 12 15 22%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:has(div[data-checked="true"]):nth-child(2) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%23ffffff%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpolyline points=%2722 7 13.5 15.5 8.5 10.5 2 17%27/%3E%3Cpolyline points=%2716 7 22 7 22 13%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:has(div[data-checked="true"]):nth-child(3) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%23ffffff%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpolygon points=%273 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21%27/%3E%3Cline x1=%279%27 x2=%279%27 y1=%273%27 y2=%2718%27/%3E%3Cline x1=%2715%27 x2=%2715%27 y1=%276%27 y2=%2721%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:has(div[data-checked="true"]):nth-child(4) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%23ffffff%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Cpath d=%27M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2%27/%3E%3Ccircle cx=%279%27 cy=%277%27 r=%274%27/%3E%3Cpath d=%27M22 21v-2a4 4 0 0 0-3-3.87%27/%3E%3Cpath d=%27M16 3.13a4 4 0 0 1 0 7.75%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:has(div[data-checked="true"]):nth-child(5) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%23ffffff%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Ccircle cx=%2711%27 cy=%2711%27 r=%278%27/%3E%3Cline x1=%2721%27 x2=%2716.65%27 y1=%2721%27 y2=%2716.65%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:has(div[data-checked="true"]):nth-child(6) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%23ffffff%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Crect width=%2718%27 height=%2718%27 x=%273%27 y=%273%27 rx=%272%27/%3E%3Cline x1=%2712%27 x2=%2712%27 y1=%273%27 y2=%2721%27/%3E%3C/svg%3E");
    }
    div[role="radiogroup"] label:has(div[data-checked="true"]):nth-child(7) p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%23ffffff%27 stroke-width=%272%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3E%3Ccircle cx=%2712%27 cy=%2712%27 r=%2710%27/%3E%3Cline x1=%2712%27 x2=%2712%27 y1=%2716%27 y2=%2712%27/%3E%3Cline x1=%2712%27 x2=%2712.01%27 y1=%278%27 y2=%278%27/%3E%3C/svg%3E");
    }
    
    /* KPI Card styling to match React dashboard visual hierarchy */
    .kpi-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.1rem 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        font-family: 'Manrope', sans-serif;
    }
    .kpi-title {
        font-size: 10px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #1e3a8a; /* Indigo primary accent */
        margin-top: 0.25rem;
        line-height: 1.1;
    }
    .kpi-subtext {
        font-size: 10px;
        color: #64748b;
        margin-top: 0.2rem;
    }

    /* Property Suggestion cards styling */
    .property-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 0.5rem;
        margin-top: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        font-family: 'Manrope', sans-serif;
    }
    .property-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .property-title {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
    }
    .property-rent {
        font-size: 16px;
        font-weight: 700;
        color: #2563eb;
    }
    .property-meta {
        font-size: 12px;
        color: #475569;
        margin-bottom: 0.75rem;
    }
    .property-badge {
        background-color: #f1f5f9;
        color: #334155;
        font-size: 10px;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        margin-right: 0.25rem;
        display: inline-block;
    }
    .property-score-badge {
        background-color: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        font-size: 11px;
        font-weight: 700;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Helper: Load dataset
@st.cache_data
def load_cleaned_dataset():
    # Detect running path relative to app.py location
    possible_paths = [
        "data/processed/rental_listings_cleaned.csv",
        "../data/processed/rental_listings_cleaned.csv",
        os.path.join(os.path.dirname(__file__), "../data/processed/rental_listings_cleaned.csv")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Ensure correct types
            df['monthly_rent'] = df['monthly_rent'].astype(float)
            df['area_sqft'] = df['area_sqft'].astype(float)
            df['rent_per_sqft'] = df['rent_per_sqft'].astype(float)
            df['security_deposit'] = df['security_deposit'].astype(float)
            df['metro_distance_km'] = df['metro_distance_km'].astype(float)
            df['office_distance_km'] = df['office_distance_km'].astype(float)
            df['college_distance_km'] = df['college_distance_km'].astype(float)
            return df
    raise FileNotFoundError("Could not find rental_listings_cleaned.csv dataset.")

try:
    df_raw = load_cleaned_dataset()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Helper: Style Plotly figures to use Manrope typography and clean backgrounds
def style_plotly_fig(fig, height=300):
    fig.update_layout(
        font_family="Manrope, Inter, -apple-system, sans-serif",
        font_color="#334155",
        legend_title_font_family="Manrope, sans-serif",
        legend_font_family="Manrope, sans-serif",
        legend_font_size=9,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=height
    )
    fig.update_xaxes(title=None, showgrid=False, linecolor='#cbd5e1', gridcolor='#f1f5f9', tickfont=dict(family="Manrope, sans-serif", size=9))
    fig.update_yaxes(title=None, showgrid=True, linecolor='#cbd5e1', gridcolor='#f1f5f9', tickfont=dict(family="Manrope, sans-serif", size=9))
    return fig

# Segment Preference Configurations
WEIGHTS = {
    'Student': {'rent': 0.30, 'metro': 0.25, 'college': 0.20, 'amenities': 0.15, 'safety': 0.10},
    'Working Professional': {'rent': 0.20, 'metro': 0.25, 'office': 0.25, 'amenities': 0.15, 'safety': 0.15},
    'Working Bachelor': {'rent': 0.30, 'metro': 0.25, 'office': 0.15, 'amenities': 0.15, 'safety': 0.15},
    'Family': {'rent': 0.20, 'space': 0.15, 'school': 0.20, 'hospital': 0.15, 'safety': 0.20, 'metro_office': 0.10}
}

# Sidebar Brand Header
st.sidebar.markdown("""
<div style="display: flex; align-items: center; padding: 0.5rem 0; margin-bottom: 1rem; gap: 10px;">
    <span style="height: 20px; width: 4px; background-color: #6366f1; border-radius: 2px; display: inline-block;"></span>
    <div style="display: flex; flex-direction: column; line-height: 1.2;">
        <span style="font-weight: 700; font-size: 13px; color: #ffffff; letter-spacing: 0.05em; text-transform: uppercase;">Delhi/NCR Rental</span>
        <span style="font-size: 9px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">Market Intelligence</span>
    </div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Select Tab View",
    [
        "Overview",
        "Price Drivers",
        "Location Intelligence",
        "Renter Segments",
        "Find Your Rental",
        "Locality Comparison",
        "Methodology"
    ],
    label_visibility="collapsed"
)

# Sidebar metadata
st.sidebar.markdown(f"""
<div style='margin-top: 2rem; border-top: 1px solid #1e293b; padding-top: 1rem; font-size: 10px; color: #94a3b8; line-height: 1.8;'>
    <div style='display: flex; justify-content: space-between;'>
        <span>Listings Analyzed:</span>
        <span style='font-weight: 700; color: #ffffff;'>{len(df_raw)}</span>
    </div>
    <div style='display: flex; justify-content: space-between;'>
        <span>Data Period:</span>
        <span style='color: #ffffff; font-weight: 500;'>Q3 2026</span>
    </div>
    <div style='display: flex; justify-content: space-between; margin-bottom: 0.75rem;'>
        <span>Last Updated:</span>
        <span style='color: #ffffff;'>Aug 2026</span>
    </div>
    <div style='color: #64748b; font-size: 9px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; border-top: 1px solid #1e293b; padding-top: 0.5rem;'>
        Data Status: Simulated Prototype
    </div>
</div>
""", unsafe_allow_html=True)

# Header title helper and PAGE_INFO
PAGE_INFO = {
    "Overview": {
        "title": "Market Overview",
        "subtitle": "A data-driven view of residential rental prices, property characteristics and affordability."
    },
    "Price Drivers": {
        "title": "What Drives Rental Prices?",
        "subtitle": "An analysis of parameters triggering rental premiums, sizing correlations, and transit access."
    },
    "Location Intelligence": {
        "title": "Location Intelligence",
        "subtitle": "Explore spatial rental distributions, property sizes, and coordinate mapping across NCR zones."
    },
    "Renter Segments": {
        "title": "Renter Segments",
        "subtitle": "Contrasting space requirements, budget parameters, and connectivity weights across renter profiles."
    },
    "Find Your Rental": {
        "title": "Find Your Rental",
        "subtitle": "Select your renter profile and preferences to display matched properties sorted by Value Score."
    },
    "Locality Comparison": {
        "title": "Locality Comparison",
        "subtitle": "Select up to three localities to analyze rent, connectivity, and amenities side-by-side."
    },
    "Methodology": {
        "title": "Methodology & Data Parameters",
        "subtitle": "Methodology transparency, scoring weight models, data parameters, and analytical limitations."
    }
}
info = PAGE_INFO.get(page, PAGE_INFO["Overview"])
st.markdown(f"<h1 style='font-size: 28px; font-weight: 700; color: #0f172a; margin-bottom: 0.15rem; font-family: Manrope, sans-serif;'>{info['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 13px; font-weight: 500; color: #64748b; margin-bottom: 1.25rem; font-family: Manrope, sans-serif; letter-spacing: 0.01em;'>{info['subtitle']}</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 0; margin-bottom: 1.5rem; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# Helper: Filter values
selected_city = "All"
selected_locality = "All"
selected_bhk = "All"
selected_bedrooms = "All"
selected_furnishing = "All"
selected_budget = int(df_raw['monthly_rent'].max())

# Horizontal Analysis Controls for Overview and Price Drivers (renders BELOW title/subtitle/divider)
if page in ["Overview", "Price Drivers"]:
    with st.container(border=True):
        st.markdown("<div style='font-size: 11px; font-weight: 700; color: #0f172a; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>Analysis Controls</div>", unsafe_allow_html=True)
        f_cols = st.columns(6)
        with f_cols[0]:
            cities = ["All"] + sorted(list(df_raw['city'].unique()))
            selected_city = st.selectbox("CITY", cities)
        with f_cols[1]:
            if selected_city != "All":
                filtered_localities = sorted(list(df_raw[df_raw['city'] == selected_city]['locality'].unique()))
            else:
                filtered_localities = sorted(list(df_raw['locality'].unique()))
            selected_locality = st.selectbox("LOCALITY", ["All"] + filtered_localities)
        with f_cols[2]:
            property_types = ["All"] + sorted(list(df_raw['property_type'].unique()))
            selected_bhk = st.selectbox("BHK TYPE", property_types)
        with f_cols[3]:
            bedrooms_list = ["All"] + sorted([str(int(x)) for x in df_raw['bedrooms'].dropna().unique()])
            selected_bedrooms = st.selectbox("BEDROOMS", bedrooms_list)
        with f_cols[4]:
            furnishing = ["All"] + sorted(list(df_raw['furnishing_status'].unique()))
            selected_furnishing = st.selectbox("FURNISHING", furnishing)
        with f_cols[5]:
            max_rent_limit = int(df_raw['monthly_rent'].max())
            # Define specific select options for the budget slider
            budget_options = [5000, 7500, 10000, 12500, 15000, 17500, 20000, 22500, 25000, 30000, 35000, 40000, 45000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000, 175000, 200000, 250000, 300000]
            budget_options = [x for x in budget_options if x < max_rent_limit]
            budget_options.append(max_rent_limit)
            
            slider_options = budget_options + ["No Limit"]
            
            def format_budget(val):
                if val == "No Limit":
                    return "No Limit"
                return f"₹{val:,}"
            
            selected_val = st.select_slider(
                "MAX BUDGET",
                options=slider_options,
                value="No Limit",
                format_func=format_budget
            )
            selected_budget = max_rent_limit if selected_val == "No Limit" else selected_val

# Filter dataset based on selections
df_filtered = df_raw.copy()
if selected_city != "All":
    df_filtered = df_filtered[df_filtered['city'] == selected_city]
if selected_locality != "All":
    df_filtered = df_filtered[df_filtered['locality'] == selected_locality]
if selected_bhk != "All":
    df_filtered = df_filtered[df_filtered['property_type'] == selected_bhk]
if selected_bedrooms != "All":
    df_filtered = df_filtered[df_filtered['bedrooms'] == int(selected_bedrooms)]
if selected_furnishing != "All":
    df_filtered = df_filtered[df_filtered['furnishing_status'] == selected_furnishing]
df_filtered = df_filtered[df_filtered['monthly_rent'] <= selected_budget]

# ----------------- OVERVIEW PAGE -----------------
if page == "Overview":
    if df_filtered.empty:
        st.warning("No listings match your filter selections. Try adjusting the budget or location filters in the Analysis Controls panel.")
        st.stop()
        
    # KPIs Row
    median_rent = df_filtered['monthly_rent'].median()
    avg_rent = df_filtered['monthly_rent'].mean()
    median_sqft = df_filtered['rent_per_sqft'].median()
    avg_size = df_filtered['area_sqft'].mean()
    median_deposit = df_filtered['security_deposit'].median()
    
    deposit_ratio = (median_deposit / median_rent) if median_rent > 0 else 0
    
    st.markdown(f"""
    <style>
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 1rem;
        }}
        @media (max-width: 768px) {{
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr) !important;
            }}
        }}
    </style>
    <div class='kpi-grid'>
        <div class='kpi-container'>
            <div class='kpi-title'>TOTAL LISTINGS</div>
            <div class='kpi-value'>{len(df_filtered)}</div>
            <div class='kpi-subtext'>Active in dataset</div>
        </div>
        <div class='kpi-container'>
            <div class='kpi-title'>MEDIAN MONTHLY RENT</div>
            <div class='kpi-value'>₹{int(median_rent):,}</div>
            <div class='kpi-subtext'>Avg: ₹{int(avg_rent):,}</div>
        </div>
        <div class='kpi-container'>
            <div class='kpi-title'>MEDIAN RENT / SQ.FT.</div>
            <div class='kpi-value'>₹{median_sqft:.1f}/sqft</div>
            <div class='kpi-subtext'>Carpet area basis</div>
        </div>
        <div class='kpi-container'>
            <div class='kpi-title'>AVERAGE PROPERTY SIZE</div>
            <div class='kpi-value'>{int(avg_size)} sqft</div>
            <div class='kpi-subtext'>Floor space average</div>
        </div>
        <div class='kpi-container'>
            <div class='kpi-title'>MEDIAN SECURITY DEPOSIT</div>
            <div class='kpi-value'>₹{int(median_deposit):,}</div>
            <div class='kpi-subtext'>~{deposit_ratio:.1f}x monthly rent</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        st.markdown("<h4 style='font-size: 11px; font-weight: 700; text-transform: uppercase; color: #0f172a; letter-spacing: 0.05em;'>TOP 10 LOCALITIES BY RENT (MEDIAN)</h4>", unsafe_allow_html=True)
        locality_rents = df_filtered.groupby('locality')['monthly_rent'].median().reset_index().sort_values(by='monthly_rent', ascending=True).tail(10)
        fig_loc = px.bar(
            locality_rents, 
            y='locality', 
            x='monthly_rent', 
            orientation='h',
            labels={'locality': 'Locality', 'monthly_rent': 'Median Monthly Rent (₹)'},
            color_discrete_sequence=['#334155']
        )
        fig_loc = style_plotly_fig(fig_loc, height=260)
        st.plotly_chart(fig_loc, use_container_width=True)
        
    with chart_cols[1]:
        st.markdown("<h4 style='font-size: 11px; font-weight: 700; text-transform: uppercase; color: #0f172a; letter-spacing: 0.05em;'>RENT DISTRIBUTION (LISTINGS COUNT)</h4>", unsafe_allow_html=True)
        
        def get_rent_bin(rent):
            if rent < 10000:
                return '<10k'
            elif rent < 15000:
                return '10k–15k'
            elif rent < 20000:
                return '15k–20k'
            elif rent < 30000:
                return '20k–30k'
            elif rent < 45000:
                return '30k–45k'
            elif rent < 60000:
                return '45k–60k'
            elif rent <= 100000:
                return '60k–1L'
            else:
                return '>1L'
                
        bins_order = ['<10k', '10k–15k', '15k–20k', '20k–30k', '30k–45k', '45k–60k', '60k–1L', '>1L']
        df_bins = df_filtered['monthly_rent'].apply(get_rent_bin).value_counts().reindex(bins_order, fill_value=0).reset_index()
        df_bins.columns = ['Rent Range', 'Listings']
        
        fig_dist = px.bar(
            df_bins, 
            x='Rent Range',
            y='Listings',
            color_discrete_sequence=['#475569']
        )
        fig_dist = style_plotly_fig(fig_dist, height=260)
        st.plotly_chart(fig_dist, use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    sub_cols = st.columns(3)
    
    with sub_cols[0]:
        st.markdown("<h4 style='font-size: 11px; font-weight: 700; text-transform: uppercase; color: #0f172a; letter-spacing: 0.05em;'>BHK TYPE DISTRIBUTION</h4>", unsafe_allow_html=True)
        bhk_counts = df_filtered['property_type'].value_counts().reset_index()
        bhk_counts.columns = ['BHK Type', 'Count']
        fig_bhk = px.pie(bhk_counts, values='Count', names='BHK Type', color_discrete_sequence=['#0f172a', '#334155', '#475569', '#64748b', '#cbd5e1'])
        fig_bhk = style_plotly_fig(fig_bhk, height=200)
        st.plotly_chart(fig_bhk, use_container_width=True)
        
    with sub_cols[1]:
        st.markdown("<h4 style='font-size: 11px; font-weight: 700; text-transform: uppercase; color: #0f172a; letter-spacing: 0.05em;'>FURNISHING DISTRIBUTION</h4>", unsafe_allow_html=True)
        furn_counts = df_filtered['furnishing_status'].value_counts().reset_index()
        furn_counts.columns = ['Status', 'Count']
        fig_furn = px.pie(furn_counts, values='Count', names='Status', color_discrete_sequence=['#0f172a', '#475569', '#94a3b8'])
        fig_furn = style_plotly_fig(fig_furn, height=200)
        st.plotly_chart(fig_furn, use_container_width=True)
        
    with sub_cols[2]:
        st.markdown("<h4 style='font-size: 11px; font-weight: 700; text-transform: uppercase; color: #0f172a; letter-spacing: 0.05em;'>MEDIAN RENT BY CITY</h4>", unsafe_allow_html=True)
        city_median = df_filtered.groupby('city')['monthly_rent'].median().reset_index().sort_values(by='monthly_rent', ascending=False)
        fig_city = px.bar(
            city_median, 
            x='city', 
            y='monthly_rent', 
            labels={'city': 'City', 'monthly_rent': 'Rent (₹)'},
            color_discrete_sequence=['#334155']
        )
        fig_city = style_plotly_fig(fig_city, height=200)
        st.plotly_chart(fig_city, use_container_width=True)

# ----------------- PRICE DRIVERS PAGE -----------------
elif page == "Price Drivers":
    if df_filtered.empty:
        st.warning("No listings match your filter selections. Try adjusting the budget or location filters in the Analysis Controls panel.")
        st.stop()
        
    # Premiums Calculation
    med_rent_all = df_filtered['monthly_rent'].median()
    
    # Parking premium
    with_p = df_filtered[df_filtered['parking'] == 'Yes']['monthly_rent'].median()
    no_p = df_filtered[df_filtered['parking'] == 'No']['monthly_rent'].median()
    parking_prem = ((with_p - no_p)/no_p * 100) if no_p > 0 else 0
    
    # AC Premium
    with_ac = df_filtered[df_filtered['ac'] == 'Yes']['monthly_rent'].median()
    no_ac = df_filtered[df_filtered['ac'] == 'No']['monthly_rent'].median()
    ac_prem = ((with_ac - no_ac)/no_ac * 100) if no_ac > 0 else 0
    
    # Backup Premium
    with_b = df_filtered[df_filtered['power_backup'] == 'Yes']['monthly_rent'].median()
    no_b = df_filtered[df_filtered['power_backup'] == 'No']['monthly_rent'].median()
    backup_prem = ((with_b - no_b)/no_b * 100) if no_b > 0 else 0
    
    # WiFi Premium
    with_w = df_filtered[df_filtered['wifi'] == 'Yes']['monthly_rent'].median()
    no_w = df_filtered[df_filtered['wifi'] == 'No']['monthly_rent'].median()
    wifi_prem = ((with_w - no_w)/no_w * 100) if no_w > 0 else 0
    
    chart_cols = st.columns([3, 1])
    
    with chart_cols[0]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Rent vs. Property Size (Carpet Area)</h4>", unsafe_allow_html=True)
        fig_scatter = px.scatter(
            df_filtered, 
            x='area_sqft', 
            y='monthly_rent',
            color='property_type',
            labels={'area_sqft': 'Carpet Area (sqft)', 'monthly_rent': 'Monthly Rent (₹)', 'property_type': 'Layout'},
            color_discrete_sequence=['#1e3a8a', '#2563eb', '#3b82f6', '#94a3b8'],
            opacity=0.6,
            hover_data=['locality', 'city', 'furnishing_status']
        )
        fig_scatter = style_plotly_fig(fig_scatter, height=320)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Sub charts row
        sub_chart_cols = st.columns(2)
        with sub_chart_cols[0]:
            st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Rent by Metro Proximity (Median)</h4>", unsafe_allow_html=True)
            
            # Bucket metro distance
            df_metro = df_filtered.copy()
            df_metro['metro_bucket'] = pd.cut(
                df_metro['metro_distance_km'], 
                bins=[0, 0.5, 1.0, 2.0, 100.0],
                labels=['< 500m', '500m - 1km', '1km - 2km', '> 2km']
            )
            metro_median = df_metro.groupby('metro_bucket')['monthly_rent'].median().reset_index()
            metro_median = metro_median.dropna()
            
            fig_metro = px.bar(
                metro_median,
                x='metro_bucket',
                y='monthly_rent',
                labels={'metro_bucket': 'Metro Distance', 'monthly_rent': 'Median Rent (₹)'},
                color_discrete_sequence=['#1e3a8a']
            )
            fig_metro = style_plotly_fig(fig_metro, height=240)
            st.plotly_chart(fig_metro, use_container_width=True)
            
        with sub_chart_cols[1]:
            st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Amenity Rental Premiums (%)</h4>", unsafe_allow_html=True)
            premiums = pd.DataFrame({
                'Amenity': ['Parking', 'Air Cond.', 'Power Backup', 'WiFi'],
                'Premium (%)': [parking_prem, ac_prem, backup_prem, wifi_prem]
            })
            premiums = premiums[premiums['Premium (%)'] > 0]
            
            fig_prem = px.bar(
                premiums,
                y='Amenity',
                x='Premium (%)',
                orientation='h',
                color_discrete_sequence=['#3b82f6']
            )
            fig_prem = style_plotly_fig(fig_prem, height=240)
            st.plotly_chart(fig_prem, use_container_width=True)
            
    with chart_cols[1]:
        st.markdown("<h4 style='font-size: 10px; font-weight: bold; text-transform: uppercase; color: #64748b; border-b: 1px solid #e2e8f0; padding-bottom: 0.5rem;'>Dynamic Insights</h4>", unsafe_allow_html=True)
        
        # Statically calculate findings from filtered data
        insights = []
        if len(df_filtered) > 0:
            if parking_prem > 0:
                insights.append(f"**Parking Premium:** Staging dedicated parking spaces is associated with a **{int(parking_prem)}%** rent premium (₹{int(with_p):,} vs. ₹{int(no_p):,}).")
            if ac_prem > 0:
                insights.append(f"**Climate Control Impact:** Air Conditioning presence increases median listings by **{int(ac_prem)}%** across current selection criteria.")
            
            # Metro proximity delta
            close_metro = df_filtered[df_filtered['metro_distance_km'] <= 0.5]['monthly_rent'].median()
            far_metro = df_filtered[df_filtered['metro_distance_km'] > 2.0]['monthly_rent'].median()
            if not np.isnan(close_metro) and not np.isnan(far_metro) and far_metro > 0:
                metro_delta = ((close_metro - far_metro)/far_metro) * 100
                insights.append(f"**Transit Proximity:** Properties within 500m of the Delhi metro corridor command a **{int(metro_delta)}%** pricing margin over remote options (>2km).")
        
        if not insights:
            st.markdown("<p style='font-size: 11px; color: #94a3b8;'>Adjust filters to compute dynamic observations.</p>", unsafe_allow_html=True)
        else:
            for inst in insights:
                st.markdown(f"""
                <div style='background: white; border: 1px solid #e2e8f0; border-radius: 4px; padding: 0.75rem; margin-bottom: 0.75rem; font-size: 11px; line-height: 1.5;'>
                    {inst}
                </div>
                """, unsafe_allow_html=True)

# ----------------- LOCATION INTELLIGENCE PAGE -----------------
elif page == "Location Intelligence":
    # 1. Metric selector
    m_cols = st.columns([3, 1])
    with m_cols[0]:
        metric_opts = {
            'Median Rent': 'Median Rent (₹)',
            'Rent per Sq.Ft.': 'Rent per Sq.Ft. (₹)',
            'Value Score': 'Value Score',
            'Average Size': 'Average Size (sqft)',
            'Metro Proximity': 'Metro Proximity (km)'
        }
        selected_metric_label = st.radio(
            "Visualize Metric:",
            list(metric_opts.keys()),
            horizontal=True
        )
        selected_metric = selected_metric_label # mapping key
    
    selected_profile = "Student"
    with m_cols[1]:
        if selected_metric == 'Value Score':
            selected_profile = st.selectbox(
                "Renter Profile:",
                ["Student", "Working Professional", "Working Bachelor", "Family"]
            )
            
    # Compute locality summarized statistics
    LOCALITY_COORDS = {
      "Mukherjee Nagar": { "x": 230, "y": 70, "zone": "North Delhi" },
      "Model Town": { "x": 200, "y": 90, "zone": "North Delhi" },
      "Kamla Nagar": { "x": 220, "y": 110, "zone": "North Delhi" },
      "Civil Lines": { "x": 250, "y": 100, "zone": "North Delhi" },
      "Rohini": { "x": 140, "y": 90, "zone": "North Delhi" },
      "Karol Bagh": { "x": 210, "y": 150, "zone": "Central Delhi" },
      "Patel Nagar": { "x": 180, "y": 155, "zone": "West Delhi" },
      "Rajinder Nagar": { "x": 200, "y": 165, "zone": "Central Delhi" },
      "Janakpuri": { "x": 120, "y": 180, "zone": "West Delhi" },
      "Laxmi Nagar": { "x": 310, "y": 160, "zone": "East Delhi" },
      "Shakarpur": { "x": 300, "y": 175, "zone": "East Delhi" },
      "Preet Vihar": { "x": 330, "y": 165, "zone": "East Delhi" },
      "Mayur Vihar": { "x": 320, "y": 210, "zone": "East Delhi" },
      "Saket": { "x": 230, "y": 310, "zone": "South Delhi" },
      "Malviya Nagar": { "x": 220, "y": 285, "zone": "South Delhi" },
      "Hauz Khas": { "x": 210, "y": 260, "zone": "South Delhi" },
      "Green Park": { "x": 195, "y": 250, "zone": "South Delhi" },
      "Greater Kailash": { "x": 250, "y": 275, "zone": "South Delhi" },
      "Vasant Kunj": { "x": 160, "y": 295, "zone": "South Delhi" },
      "Dwarka": { "x": 90, "y": 220, "zone": "Dwarka" },
      "Noida Sector 62": { "x": 410, "y": 190, "zone": "Noida" },
      "Noida Sector 15": { "x": 350, "y": 225, "zone": "Noida" },
      "Noida Sector 137": { "x": 430, "y": 270, "zone": "Noida" },
      "Pari Chowk": { "x": 500, "y": 330, "zone": "Greater Noida" },
      "Knowledge Park": { "x": 490, "y": 305, "zone": "Greater Noida" },
      "Indirapuram": { "x": 390, "y": 155, "zone": "Ghaziabad" },
      "Vaishali": { "x": 350, "y": 145, "zone": "Ghaziabad" },
      "DLF Phase 3": { "x": 120, "y": 320, "zone": "Gurugram" },
      "Gurugram Sector 45": { "x": 110, "y": 350, "zone": "Gurugram" },
      "Gurugram Sector 56": { "x": 120, "y": 380, "zone": "Gurugram" },
      "Golf Course Road": { "x": 140, "y": 360, "zone": "Gurugram" }
    }
    
    stats = []
    locality_groups = df_raw.groupby('locality')
    for loc, group in locality_groups:
        coords = LOCALITY_COORDS.get(loc)
        if not coords:
            continue
        
        # VFM Score mapping
        vfm_col = ('vfm_student' if selected_profile == 'Student'
                   else 'vfm_professional' if selected_profile == 'Working Professional'
                   else 'vfm_bachelor' if selected_profile == 'Working Bachelor'
                   else 'vfm_family')
        
        stats.append({
            'Locality': loc,
            'City': group['city'].iloc[0],
            'Zone': coords['zone'],
            'x': coords['x'],
            'y': coords['y'],
            'Listings': len(group),
            'Median Rent (₹)': group['monthly_rent'].median(),
            'Rent per Sq.Ft. (₹)': group['rent_per_sqft'].median(),
            'Value Score': int(group[vfm_col].mean()),
            'Average Size (sqft)': int(group['area_sqft'].mean()),
            'Metro Proximity (km)': group['metro_distance_km'].median()
        })
        
    df_map = pd.DataFrame(stats)
    
    # 2. Main layout grid: Map (70%) and Info Card (30%)
    layout_cols = st.columns([5, 2])
    
    with layout_cols[0]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Delhi/NCR Regional Coordinate Plot</h4>", unsafe_allow_html=True)
        
        # We plot coordinates. The sizes and colors are scaled based on selected metric.
        metric_col_mapping = {
            'Median Rent': 'Median Rent (₹)',
            'Rent per Sq.Ft.': 'Rent per Sq.Ft. (₹)',
            'Value Score': 'Value Score',
            'Average Size': 'Average Size (sqft)',
            'Metro Proximity': 'Metro Proximity (km)'
        }
        
        target_col = metric_col_mapping[selected_metric]
        
        # Scale sizes: min size 8, max size 24
        val_min = df_map[target_col].min()
        val_max = df_map[target_col].max()
        val_range = val_max - val_min if val_max != val_min else 1
        
        # Apply scaling logic
        if selected_metric == 'Metro Proximity':
            # For metro proximity, smaller distance = closer = higher proximity bubble size!
            df_map['bubble_size'] = 8 + (1.0 - (df_map[target_col] - val_min)/val_range) * 16
        else:
            df_map['bubble_size'] = 8 + ((df_map[target_col] - val_min)/val_range) * 16
            
        # Select color scale:
        if selected_metric == 'Value Score':
            # green, amber, red scale
            colorscale = ['#dc2626', '#d97706', '#16a34a']
        else:
            # neutral slate scale
            colorscale = ['#cbd5e1', '#64748b', '#0f172a']
            
        fig_map = px.scatter(
            df_map,
            x='x',
            y='y',
            size='bubble_size',
            color=target_col,
            hover_name='Locality',
            hover_data={
                'x': False,
                'y': False,
                'bubble_size': False,
                'City': True,
                'Zone': True,
                'Listings': True,
                'Median Rent (₹)': ':,.0f',
                'Rent per Sq.Ft. (₹)': ':,.1f',
                'Value Score': True,
                'Average Size (sqft)': ':,.0f',
                'Metro Proximity (km)': ':.2f'
            },
            color_continuous_scale=colorscale,
            size_max=24
        )
        
        # Add Yamuna River coordinates line to Plotly
        yamuna_x = [330, 330, 290, 340, 370, 400]
        yamuna_y = [0, 100, 200, 300, 380, 420]
        
        fig_map.add_scatter(
            x=yamuna_x,
            y=yamuna_y,
            mode='lines',
            line=dict(color='#bae6fd', width=6, dash='dash'),
            name='Yamuna River',
            hoverinfo='skip',
            showlegend=False
        )
        
        # Add Yamuna text label
        fig_map.add_annotation(
            x=320,
            y=230,
            text="Yamuna River",
            font=dict(color="#38bdf8", size=8, family="Manrope"),
            showarrow=False,
            textangle=-45
        )
        
        # Invert Y to match SVG top-left origin coordinates
        fig_map.update_yaxes(autorange="reversed", range=[430, -10], showticklabels=False, showgrid=False, zeroline=False)
        fig_map.update_xaxes(range=[-10, 610], showticklabels=False, showgrid=False, zeroline=False)
        
        fig_map = style_plotly_fig(fig_map, height=380)
        fig_map.update_layout(coloraxis_showscale=True, coloraxis_colorbar=dict(thickness=10, title="Scale"))
        st.plotly_chart(fig_map, use_container_width=True)
        
    with layout_cols[1]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Locality Details</h4>", unsafe_allow_html=True)
        
        selected_inspected_locality = st.selectbox(
            "Select Locality to Inspect:",
            df_map['Locality'].tolist()
        )
        
        loc_row = df_map[df_map['Locality'] == selected_inspected_locality].iloc[0]
        
        st.markdown(f"""
        <div style='background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.25rem; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.05); font-family: Manrope, sans-serif;'>
            <span style='background-color: #eff6ff; color: #1e40af; font-size: 10px; font-weight: 700; padding: 0.25rem 0.5rem; border-radius: 4px; text-transform: uppercase;'>
                {loc_row['Zone']}
            </span>
            <h3 style='margin: 0.5rem 0 0.2rem 0; font-size: 18px; font-weight: 700; color: #0f172a;'>
                {loc_row['Locality']}
            </h3>
            <p style='margin: 0 0 1rem 0; font-size: 12px; color: #64748b;'>
                {loc_row['City']}
            </p>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; border-top: 1px solid #f1f5f9; padding-top: 1rem;'>
                <div>
                    <span style='font-size: 9px; font-weight: bold; color: #94a3b8; text-transform: uppercase; tracking-wider;'>Median Rent</span>
                    <p style='font-weight: 700; font-size: 13px; color: #0f172a; margin: 0;'>₹{int(loc_row['Median Rent (₹)']):,}</p>
                </div>
                <div>
                    <span style='font-size: 9px; font-weight: bold; color: #94a3b8; text-transform: uppercase; tracking-wider;'>Rent / Sq.Ft</span>
                    <p style='font-weight: 700; font-size: 13px; color: #0f172a; margin: 0;'>₹{loc_row['Rent per Sq.Ft. (₹)']:.1f}</p>
                </div>
                <div>
                    <span style='font-size: 9px; font-weight: bold; color: #94a3b8; text-transform: uppercase; tracking-wider;'>Value Score</span>
                    <p style='font-weight: 700; font-size: 13px; color: #16a34a; margin: 0;'>{loc_row['Value Score']} / 100</p>
                </div>
                <div>
                    <span style='font-size: 9px; font-weight: bold; color: #94a3b8; text-transform: uppercase; tracking-wider;'>Average Size</span>
                    <p style='font-weight: 700; font-size: 13px; color: #0f172a; margin: 0;'>{loc_row['Average Size (sqft)']} sqft</p>
                </div>
                <div style='grid-column: span 2;'>
                    <span style='font-size: 9px; font-weight: bold; color: #94a3b8; text-transform: uppercase; tracking-wider;'>Median Metro Distance</span>
                    <p style='font-weight: 700; font-size: 13px; color: #0f172a; margin: 0;'>{loc_row['Metro Proximity (km)']:.2f} km</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Locality Metrics Matrix</h4>", unsafe_allow_html=True)
    
    # Render table sorted by metric
    df_matrix_show = df_map[['Locality', 'City', 'Zone', 'Listings', 'Median Rent (₹)', 'Rent per Sq.Ft. (₹)', 'Value Score', 'Average Size (sqft)', 'Metro Proximity (km)']].copy()
    df_matrix_show = df_matrix_show.sort_values(by=target_col, ascending=(selected_metric == 'Metro Proximity'))
    st.dataframe(df_matrix_show, use_container_width=True, hide_index=True)

# ----------------- RENTER SEGMENTS PAGE -----------------
elif page == "Renter Segments":
    st.markdown("<p style='font-size: 12px; color: #475569; margin-bottom: 1.5rem;'>Contrasting space requirements, budget parameters, and transit connectivity weights across renter demographics.</p>", unsafe_allow_html=True)
    
    # Construct weights dataframe for comparison
    subjects = ['Rent Affordability', 'Metro Proximity', 'Target Destination', 'Amenities Score', 'Safety Index', 'Carpet Area']
    radar_data = []
    
    # Map weights
    for sub in subjects:
        row = {'subject': sub}
        if sub == 'Rent Affordability':
            row['Student'] = 30
            row['Professional'] = 20
            row['Bachelor'] = 30
            row['Family'] = 20
        elif sub == 'Metro Proximity':
            row['Student'] = 25
            row['Professional'] = 25
            row['Bachelor'] = 25
            row['Family'] = 5 # Shared
        elif sub == 'Target Destination':
            row['Student'] = 20 # College
            row['Professional'] = 25 # Office
            row['Bachelor'] = 15 # Office
            row['Family'] = 35 # School/Hosp
        elif sub == 'Amenities Score':
            row['Student'] = 15
            row['Professional'] = 15
            row['Bachelor'] = 15
            row['Family'] = 15
        elif sub == 'Safety Index':
            row['Student'] = 10
            row['Professional'] = 15
            row['Bachelor'] = 15
            row['Family'] = 20
        elif sub == 'Carpet Area':
            row['Student'] = 0
            row['Professional'] = 0
            row['Bachelor'] = 0
            row['Family'] = 15
        radar_data.append(row)
        
    df_radar = pd.DataFrame(radar_data)
    
    cols = st.columns([1, 1])
    
    with cols[0]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Value Scoring Weight Matrix (%)</h4>", unsafe_allow_html=True)
        # Display as a clean table
        df_radar_show = df_radar.copy()
        df_radar_show.columns = ['Preference Metric', 'Students (%)', 'Working Professionals (%)', 'Working Bachelors (%)', 'Families (%)']
        st.dataframe(df_radar_show, use_container_width=True, hide_index=True)
        
    with cols[1]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Scoring Weight Comparison</h4>", unsafe_allow_html=True)
        # Melt dataframe for bar charting
        df_melted = df_radar.melt(id_vars='subject', var_name='Renter Segment', value_name='Weight (%)')
        fig_radar = px.bar(
            df_melted,
            x='subject',
            y='Weight (%)',
            color='Renter Segment',
            barmode='group',
            color_discrete_sequence=['#1e3a8a', '#2563eb', '#3b82f6', '#94a3b8']
        )
        fig_radar = style_plotly_fig(fig_radar, height=280)
        st.plotly_chart(fig_radar, use_container_width=True)
# ----------------- FIND YOUR RENTAL PAGE -----------------
elif page == "Find Your Rental":
    st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569; border-b: 1px solid #e2e8f0; padding-bottom: 0.5rem;'>Your Requirements</h4>", unsafe_allow_html=True)
    
    setup_cols = st.columns(4)
    with setup_cols[0]:
        renter_type = st.selectbox("Renter Segment Profile", ["Student", "Working Professional", "Working Bachelor", "Family"])
    with setup_cols[1]:
        max_budget = st.number_input("Maximum Rent (₹)", min_value=5000, value=30000, step=2500)
    with setup_cols[2]:
        furnishing_req = st.selectbox("Furnishing Requirement", ["Any", "Furnished", "Semi-Furnished", "Unfurnished"])
    with setup_cols[3]:
        max_metro = st.selectbox("Max Metro Distance", ["No Limit", "Within 500m", "Within 1km", "Within 2km"])
        
    st.markdown("<span style='font-size: 10px; font-weight: bold; text-transform: uppercase; color: #94a3b8;'>Key Amenities Needed</span>", unsafe_allow_html=True)
    amenity_cols = st.columns(4)
    with amenity_cols[0]:
        need_ac = st.checkbox("Air Conditioning (AC)")
    with amenity_cols[1]:
        need_parking = st.checkbox("Dedicated Parking")
    with amenity_cols[2]:
        need_backup = st.checkbox("Power Backup")
    with amenity_cols[3]:
        need_wifi = st.checkbox("High-Speed WiFi")
        
    # Map pre-calculated Value Scores directly from dataset
    score_col = (
        'vfm_student' if renter_type == 'Student'
        else 'vfm_professional' if renter_type == 'Working Professional'
        else 'vfm_bachelor' if renter_type == 'Working Bachelor'
        else 'vfm_family'
    )
    df_calc = df_raw.copy()
    df_calc['VFM_Score'] = df_calc[score_col].round().astype(int)
    
    # Filter final suggestions
    df_matches = df_calc.copy()
    df_matches = df_matches[df_matches['monthly_rent'] <= max_budget]
    if furnishing_req != "Any":
        df_matches = df_matches[df_matches['furnishing_status'] == furnishing_req]
        
    if max_metro == "Within 500m":
        df_matches = df_matches[df_matches['metro_distance_km'] <= 0.5]
    elif max_metro == "Within 1km":
        df_matches = df_matches[df_matches['metro_distance_km'] <= 1.0]
    elif max_metro == "Within 2km":
        df_matches = df_matches[df_matches['metro_distance_km'] <= 2.0]
        
    if need_ac:
        df_matches = df_matches[df_matches['ac'] == 'Yes']
    if need_parking:
        df_matches = df_matches[df_matches['parking'] == 'Yes']
    if need_backup:
        df_matches = df_matches[df_matches['power_backup'] == 'Yes']
    if need_wifi:
        df_matches = df_matches[df_matches['wifi'] == 'Yes']
        
    df_matches = df_matches.sort_values(by='VFM_Score', ascending=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Suggested Matches ({len(df_matches)} found)</h4>", unsafe_allow_html=True)
    
    if df_matches.empty:
        st.info("No properties match all current requirements. Try loosening filters (e.g. increase max budget or untick AC/parking).")
    else:
        # Render cards for top 3 matches and expanders below them
        for idx, row in df_matches.head(3).iterrows():
            # Format amenities
            amenity_badges = ""
            for col, label in [('ac', 'AC'), ('parking', 'Parking'), ('wifi', 'WiFi'), ('power_backup', 'Power Backup')]:
                if row[col] == 'Yes':
                    amenity_badges += f"<span class='property-badge'>{label}</span>"
            
            # Render property card
            st.markdown(f"""
            <div class='property-card'>
                <div class='property-header'>
                    <div class='property-title'>{row['listing_title']}</div>
                    <div class='property-score-badge'>{row['VFM_Score']} / 100 Value Score</div>
                </div>
                <div class='property-meta'>
                    <strong>{row['locality']}, {row['city']}</strong> &bull; 
                    {row['property_type']} &bull; 
                    {int(row['area_sqft'])} sq.ft. &bull; 
                    {row['metro_distance_km']:.2f} km from metro
                </div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        {amenity_badges}
                    </div>
                    <div class='property-rent'>₹{int(row['monthly_rent']):,}/month</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"Detailed Monthly Budget Breakdown &bull; {row['listing_title']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Locality:** {row['locality']}, {row['city']}")
                    st.write(f"**BHK Layout:** {row['property_type']} ({int(row['area_sqft'])} sqft)")
                    st.write(f"**Proximity:** Metro: {row['metro_distance_km']} km | Offices: {row['office_distance_km']} km")
                    st.write(f"**Amenities:** AC: {row['ac']} | Parking: {row['parking']} | WiFi: {row['wifi']}")
                with c2:
                    rent = row['monthly_rent']
                    maint = row['maintenance']
                    elec = row['electricity_estimate']
                    total = rent + maint + elec + 800  # flat internet
                    
                    st.write(f"**Base monthly rent:** ₹{int(rent):,}")
                    st.write(f"**Monthly Maintenance:** ₹{int(maint):,}")
                    st.write(f"**Electricity (Estimated):** ₹{int(elec):,}")
                    st.write(f"**Internet (Standard flat):** ₹800")
                    st.write(f"---")
                    st.write(f"**Total Estimated Housing Cost:** **₹{int(total):,}/month**")

# ----------------- LOCALITY COMPARISON PAGE -----------------
elif page == "Locality Comparison":
    st.markdown("<p style='font-size: 12px; color: #475569; margin-bottom: 1.5rem;'>Select up to three localities to compare rents, connectivity parameters, and Value Scores side-by-side.</p>", unsafe_allow_html=True)
    
    localities = sorted(list(df_raw['locality'].unique()))
    
    select_cols = st.columns(3)
    with select_cols[0]:
        locA = st.selectbox("Locality A", localities, index=0)
    with select_cols[1]:
        locB = st.selectbox("Locality B", localities, index=1)
    with select_cols[2]:
        locC = st.selectbox("Locality C (Optional)", ["None"] + localities, index=0)
        
    compare_locs = [locA, locB]
    if locC != "None":
        compare_locs.append(locC)
        
    # Calculate stats for chosen
    stats = []
    for loc in compare_locs:
        df_l = df_raw[df_raw['locality'] == loc]
        if not df_l.empty:
            stats.append({
                'Locality': loc,
                'City': df_l['city'].iloc[0],
                'Median Rent (₹)': int(df_l['monthly_rent'].median()),
                'Rent/Sq.Ft. (₹)': int(df_l['rent_per_sqft'].median()),
                'Avg Size (sqft)': int(df_l['area_sqft'].mean()),
                'Metro (km)': f"{df_l['metro_distance_km'].median():.2f} km",
                'Safety Index': int(((df_l['cctv'] == 'Yes').mean() * 100 + (df_l['security'] == 'Yes').mean() * 100) / 2),
                'Parking Spot (%)': f"{int((df_l['parking'] == 'Yes').mean() * 100)}%",
                'Backup Power (%)': f"{int((df_l['power_backup'] == 'Yes').mean() * 100)}%"
            })
            
    df_compare = pd.DataFrame(stats)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Comparison Matrix</h4>", unsafe_allow_html=True)
    st.dataframe(df_compare, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chart comparison
    if len(df_compare) > 0:
        fig_comp = px.bar(
            df_compare,
            x='Locality',
            y='Median Rent (₹)',
            color='Locality',
            color_discrete_sequence=['#1e3a8a', '#3b82f6', '#94a3b8']
        )
        fig_comp = style_plotly_fig(fig_comp, height=280)
        st.plotly_chart(fig_comp, use_container_width=True)

# ----------------- METHODOLOGY PAGE -----------------
elif page == "Methodology":
    st.markdown("""
    <div style='background: white; border: 1px solid #e2e8f0; border-radius: 4px; padding: 1.5rem; space-y: 1.5rem;'>
        <h4 style='font-size: 13px; text-transform: uppercase; color: #0f172a; margin-top: 0;'>Prototype Dataset Notice</h4>
        <p style='font-size: 12px; color: #475569; line-height: 1.6;'>
            This prototype application utilizes a programmatically simulated dataset of 839 records covering major Delhi/NCR rental hubs. The distributions are designed to accurately mirror real-world rental patterns (e.g. higher rents in South Delhi and Cyber Gurugram, student hubs in North/East Delhi). For production deployment, you can import public listing feeds into the matching PostgreSQL schema.
        </p>
        
        <h4 style='font-size: 13px; text-transform: uppercase; color: #0f172a; margin-top: 1.5rem;'>Parameter Normalization Formulas</h4>
        <div style='font-size: 12px; color: #475569; line-height: 1.6;'>
            <ul>
                <li><strong>Rent Affordability Score:</strong> <code>100 - (monthly_rent / max_rent * 100)</code> (Capped globally. Higher rents receive lower affordability index).</li>
                <li><strong>Metro Proximity Score:</strong> <code>100 * exp(-0.8 * distance_km)</code> (Exponential decay. Properties directly beside the metro score ~100. Over 2km drops to &lt;20).</li>
            </ul>
        </div>
        
        <h4 style='font-size: 13px; text-transform: uppercase; color: #0f172a; margin-top: 1.5rem;'>Analytical Limitations</h4>
        <ul style='font-size: 12px; color: #475569; line-height: 1.6;'>
            <li><strong>Missing Qualitative Variables:</strong> Factors such as landlord behavior, structural construction quality, natural ventilation, and neighbor quality are not captured in public metadata feeds.</li>
            <li><strong>Static Commute Proxies:</strong> Distance is modeled as straight-line proximity to nearest station coordinates. It does not account for peak-hour road congestion or public transport frequencies.</li>
            <li><strong>Dynamic Seasonality:</strong> Rents vary depending on the calendar month (e.g. North Campus rents surge in July/August during DU admissions). The dataset reflects a standardized snapshot.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
