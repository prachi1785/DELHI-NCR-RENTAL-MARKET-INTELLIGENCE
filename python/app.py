import streamlit as st
import streamlit.components.v1 as components
import os
import re

# Set page config
st.set_page_config(
    page_title="Delhi/NCR Rental Market Intelligence",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS to hide all Streamlit elements and make the iframe fullscreen
st.markdown("""
<style>
    /* Hide Streamlit headers and footers */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide Streamlit sidebar if it exists */
    div[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Remove padding and margins */
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    iframe {
        width: 100% !important;
        height: 100vh !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
        background-color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# Build directories
dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard', 'dist')
index_path = os.path.join(dist_dir, 'index.html')

if not os.path.exists(index_path):
    st.error("Compiled React index.html not found! Run npm run build.")
    st.stop()

# Load index.html
with open(index_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Inline JS and CSS dynamically by matching files in dist/assets
assets_dir = os.path.join(dist_dir, 'assets')
js_file = ""
css_file = ""

if os.path.exists(assets_dir):
    for f_name in os.listdir(assets_dir):
        if f_name.endswith('.js'):
            js_file = f_name
        elif f_name.endswith('.css'):
            css_file = f_name

if js_file and css_file:
    # Read JS and CSS content
    with open(os.path.join(assets_dir, js_file), 'r', encoding='utf-8') as f:
        js_content = f.read()
    with open(os.path.join(assets_dir, css_file), 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Inline them by replacing script and link tags literally to avoid PatternError from backslashes
    css_match = re.search(r'<link rel="stylesheet"[^>]*href="/assets/[^"]*"[^>]*>', html_content)
    if css_match:
        html_content = html_content.replace(css_match.group(0), f'<style>\n{css_content}\n</style>')

    js_match = re.search(r'<script type="module"[^>]*src="/assets/[^"]*"[^>]*><\/script>', html_content)
    if js_match:
        html_content = html_content.replace(js_match.group(0), f'<script type="module">\n{js_content}\n</script>')
else:
    st.error("Vite build assets not found! Check dashboard/dist/assets.")
    st.stop()

# Render full viewport iframe
components.html(html_content, height=1000, scrolling=True)
