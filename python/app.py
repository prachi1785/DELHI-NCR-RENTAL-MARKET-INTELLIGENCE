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
    /* Consolidate typography and backgrounds across environments */
    html, body, [class*="css"], .stApp, .stMarkdown, .kpi-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    .stApp { background-color: #f8fafc !important; }
    
    /* Parity for top padding and page spacing */
    .block-container { 
        padding-top: 1.5rem !important; 
        padding-bottom: 2.0rem !important; 
        max-width: 100% !important; 
    }
    
    h1, h2, h3, h4 { 
        color: #0f172a !important; 
        font-weight: 700 !important; 
    }
    
    /* KPI Card styling to match localhost exactly */
    .kpi-container {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        padding: 1rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .kpi-title {
        font-size: 10px;
        font-weight: bold;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 20px;
        font-weight: bold;
        color: #0f172a;
        margin-top: 0.25rem;
    }
    .kpi-subtext {
        font-size: 10px;
        color: #94a3b8;
        margin-top: 0.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper: Load dataset
@st.cache_data
def load_data():
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
    df_raw = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Segment Preference Configurations
WEIGHTS = {
    'Student': {'rent': 0.30, 'metro': 0.25, 'college': 0.20, 'amenities': 0.15, 'safety': 0.10},
    'Working Professional': {'rent': 0.20, 'metro': 0.25, 'office': 0.25, 'amenities': 0.15, 'safety': 0.15},
    'Working Bachelor': {'rent': 0.30, 'metro': 0.25, 'office': 0.15, 'amenities': 0.15, 'safety': 0.15},
    'Family': {'rent': 0.20, 'space': 0.15, 'school': 0.20, 'hospital': 0.15, 'safety': 0.20, 'metro_office': 0.10}
}

# Navigation Menu
st.sidebar.markdown("<h2 style='font-size: 14px; margin-bottom: 1rem; color: white;'>Navigation Controls</h2>", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Select Tab View",
    ["Overview", "Price Drivers", "Renter Segments", "Find Your Rental", "Locality Comparison", "Methodology"],
    label_visibility="collapsed"
)

# Sidebar metadata
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='font-size: 10px; color: #94a3b8; line-height: 1.5;'>
    <strong>Listings Analyzed:</strong> {len(df_raw)}<br>
    <strong>Data Period:</strong> Q3 2026<br>
    <strong>Last Updated:</strong> Aug 2026<br>
    <strong>Data Status:</strong> Simulated Prototype
</div>
""", unsafe_allow_html=True)

# Global Filters only active for Overview and Price Drivers
if page in ["Overview", "Price Drivers"]:
    st.sidebar.markdown("---")
    st.sidebar.markdown("<span style='font-size: 10px; font-weight: bold; text-transform: uppercase; color: #94a3b8;'>Data Scope Filters</span>", unsafe_allow_html=True)
    
    cities = ["All"] + sorted(list(df_raw['city'].unique()))
    selected_city = st.sidebar.selectbox("City", cities)
    
    if selected_city != "All":
        filtered_localities = sorted(list(df_raw[df_raw['city'] == selected_city]['locality'].unique()))
    else:
        filtered_localities = sorted(list(df_raw['locality'].unique()))
    
    selected_locality = st.sidebar.selectbox("Locality", ["All"] + filtered_localities)
    
    property_types = ["All"] + sorted(list(df_raw['property_type'].unique()))
    selected_bhk = st.sidebar.selectbox("BHK Type", property_types)
    
    furnishing = ["All"] + sorted(list(df_raw['furnishing_status'].unique()))
    selected_furnishing = st.sidebar.selectbox("Furnishing Status", furnishing)
    
    max_rent_limit = float(df_raw['monthly_rent'].max())
    selected_budget = st.sidebar.slider("Maximum Budget (₹)", min_value=5000, max_value=int(max_rent_limit), value=int(max_rent_limit), step=2500)
    
    # Filter dataset
    df_filtered = df_raw.copy()
    if selected_city != "All":
        df_filtered = df_filtered[df_filtered['city'] == selected_city]
    if selected_locality != "All":
        df_filtered = df_filtered[df_filtered['locality'] == selected_locality]
    if selected_bhk != "All":
        df_filtered = df_filtered[df_filtered['property_type'] == selected_bhk]
    if selected_furnishing != "All":
        df_filtered = df_filtered[df_filtered['furnishing_status'] == selected_furnishing]
    df_filtered = df_filtered[df_filtered['monthly_rent'] <= selected_budget]
else:
    df_filtered = df_raw.copy()
# System Status Diagnostics (Collapsed)
with st.sidebar.expander("System Diagnostic Check", expanded=False):
    st.markdown(f"""
    <div style='font-size: 10px; color: #64748b; line-height: 1.4;'>
        <strong>Streamlit:</strong> {st.__version__}<br>
        <strong>WD:</strong> {os.getcwd()[:20]}...<br>
        <strong>Config:</strong> {'Found' if os.path.exists('.streamlit/config.toml') else 'Missing'}<br>
        <strong>Clean CSV:</strong> {'Found' if os.path.exists('data/processed/rental_listings_cleaned.csv') else 'Missing'}
    </div>
    """, unsafe_allow_html=True)

# Header title helper
st.markdown(f"<h1 style='font-size: 24px; margin-bottom: 0.2rem;'>{page}</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 12px; color: #64748b; margin-bottom: 1.5rem;'>Delhi/NCR Rental Market Intelligence Internal BI Case Study</p>", unsafe_allow_html=True)

# ----------------- OVERVIEW PAGE -----------------
if page == "Overview":
    if df_filtered.empty:
        st.warning("No listings match your filter selections. Try adjusting the Sidebar sliders.")
        st.stop()
        
    # KPIs Row
    median_rent = df_filtered['monthly_rent'].median()
    avg_rent = df_filtered['monthly_rent'].mean()
    median_sqft = df_filtered['rent_per_sqft'].median()
    avg_size = df_filtered['area_sqft'].mean()
    median_deposit = df_filtered['security_deposit'].median()
    
    cols = st.columns(5)
    with cols[0]:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Total Listings</div><div class='kpi-value'>{len(df_filtered)}</div><div class='kpi-subtext'>Active records</div></div>""", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Median Rent</div><div class='kpi-value'>₹{int(median_rent):,}</div><div class='kpi-subtext'>Avg: ₹{int(avg_rent):,}</div></div>""", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Median Rent / Sq.Ft</div><div class='kpi-value'>₹{int(median_sqft)}</div><div class='kpi-subtext'>Carpet area basis</div></div>""", unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Average Size</div><div class='kpi-value'>{int(avg_size)} sqft</div><div class='kpi-subtext'>Floor space average</div></div>""", unsafe_allow_html=True)
    with cols[4]:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Median Deposit</div><div class='kpi-value'>₹{int(median_deposit):,}</div><div class='kpi-subtext'>~{(median_deposit/median_rent):.1f}x Rent</div></div>""", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Top 10 Localities by Rent (Median)</h4>", unsafe_allow_html=True)
        locality_rents = df_filtered.groupby('locality')['monthly_rent'].median().reset_index().sort_values(by='monthly_rent', ascending=True).tail(10)
        fig_loc = px.bar(
            locality_rents, 
            y='locality', 
            x='monthly_rent', 
            orientation='h',
            labels={'locality': 'Locality', 'monthly_rent': 'Median Monthly Rent (₹)'},
            color_discrete_sequence=['#1e293b']
        )
        fig_loc.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_size=10,
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
        st.plotly_chart(fig_loc, use_container_width=True)
        
    with chart_cols[1]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Rent Distribution Bins</h4>", unsafe_allow_html=True)
        fig_dist = px.histogram(
            df_filtered, 
            x='monthly_rent',
            nbins=12,
            labels={'monthly_rent': 'Monthly Rent (₹)', 'count': 'Listings'},
            color_discrete_sequence=['#475569']
        )
        fig_dist.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_size=10,
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    sub_cols = st.columns(3)
    
    with sub_cols[0]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>BHK Type Distribution</h4>", unsafe_allow_html=True)
        bhk_counts = df_filtered['property_type'].value_counts().reset_index()
        bhk_counts.columns = ['BHK Type', 'Count']
        fig_bhk = px.pie(bhk_counts, values='Count', names='BHK Type', color_discrete_sequence=['#0f172a', '#334155', '#475569', '#64748b', '#cbd5e1'])
        fig_bhk.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=220, font_size=10)
        st.plotly_chart(fig_bhk, use_container_width=True)
        
    with sub_cols[1]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Furnishing Status</h4>", unsafe_allow_html=True)
        furn_counts = df_filtered['furnishing_status'].value_counts().reset_index()
        furn_counts.columns = ['Status', 'Count']
        fig_furn = px.pie(furn_counts, values='Count', names='Status', color_discrete_sequence=['#334155', '#64748b', '#cbd5e1'])
        fig_furn.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=220, font_size=10)
        st.plotly_chart(fig_furn, use_container_width=True)
        
    with sub_cols[2]:
        st.markdown("<h4 style='font-size: 13px; text-transform: uppercase; color: #475569;'>Median Rent by City</h4>", unsafe_allow_html=True)
        city_median = df_filtered.groupby('city')['monthly_rent'].median().reset_index().sort_values(by='monthly_rent', ascending=False)
        fig_city = px.bar(
            city_median, 
            x='city', 
            y='monthly_rent', 
            labels={'city': 'City', 'monthly_rent': 'Rent (₹)'},
            color_discrete_sequence=['#475569']
        )
        fig_city.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=220,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_size=10,
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
        st.plotly_chart(fig_city, use_container_width=True)

# ----------------- PRICE DRIVERS PAGE -----------------
elif page == "Price Drivers":
    if df_filtered.empty:
        st.warning("No listings match your filters. Try adjusting budget sliders.")
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
            color_discrete_sequence=['#0f172a', '#334155', '#475569', '#94a3b8'],
            opacity=0.6,
            hover_data=['locality', 'city', 'furnishing_status']
        )
        fig_scatter.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_size=10,
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
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
                color_discrete_sequence=['#475569']
            )
            fig_metro.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                height=240,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_size=10,
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
            )
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
                color_discrete_sequence=['#334155']
            )
            fig_prem.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                height=240,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_size=10,
                xaxis=dict(showgrid=True, gridcolor='#f1f5f9')
            )
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
            color_discrete_sequence=['#0f172a', '#334155', '#475569', '#94a3b8']
        )
        fig_radar.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=280,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_size=10,
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
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
        # Display top 10 matches in a clean table format
        show_cols = ['listing_title', 'locality', 'city', 'monthly_rent', 'area_sqft', 'metro_distance_km', 'furnishing_status', 'VFM_Score']
        df_show = df_matches[show_cols].head(10).copy()
        df_show.columns = ['Property Details', 'Locality', 'City', 'Rent (₹)', 'Size (sqft)', 'Metro (km)', 'Furnishing', 'VFM Score']
        
        # Render a clean HTML table
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        # Expanders for detailed breakdown
        st.markdown("<span style='font-size: 10px; font-weight: bold; text-transform: uppercase; color: #94a3b8;'>Housing Cost Breakdowns</span>", unsafe_allow_html=True)
        for idx, row in df_matches.head(3).iterrows():
            with st.expander(f"{row['listing_title']} - {row['locality']} (Score: {row['VFM_Score']}/100)"):
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
            color_discrete_sequence=['#1e293b', '#475569', '#94a3b8']
        )
        fig_comp.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=280,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_size=10,
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
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
