import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

# ── Page header ───────────────────────────────────────────────────────────────
st.title("🔍 Filter Restaurants")
st.write("Narrow down your options by cuisine, price, and atmosphere.")
st.divider()

# ── Filter controls ───────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    cuisine = st.selectbox(
        "Cuisine type",
        options=["Any", "Vietnamese", "Mexican", "Italian", "Japanese",
                 "American", "Chinese", "Indian", "Thai", "Mediterranean",
                 "Korean", "Vegan", "Café"],
        index=0
    )

with col2:
    max_price = st.selectbox(
        "Max price range",
        options=["Any", "1 ($)", "2 ($$)", "3 ($$$)"],
        index=0
    )

with col3:
    atmosphere = st.selectbox(
        "Atmosphere",
        options=["Any", "casual", "upscale", "fast-casual", "cozy", "lively"],
        index=0
    )

# ── Build query params ────────────────────────────────────────────────────────
params = {}
if cuisine != "Any":
    params["cuisine"] = cuisine
if max_price != "Any":
    params["price_range"] = max_price.split(" ")[0]   # extract just the number
if atmosphere != "Any":
    params["atmosphere"] = atmosphere

# ── Fetch button ──────────────────────────────────────────────────────────────
if st.button("Search", type="primary", use_container_width=False):
    st.session_state["filter_results"] = None   # reset previous results

    API_URL = "http://web-api:4000/olivia/restaurants/filter"

    try:
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            st.session_state["filter_results"] = response.json()
        else:
            st.error(f"API error: {response.status_code}")

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the API: {str(e)}")
        st.info("Make sure the API container is running on http://web-api:4000")

# ── Also load all restaurants on page load ────────────────────────────────────
if "filter_results" not in st.session_state:
    try:
        response = requests.get("http://web-api:4000/olivia/restaurants/filter")
        if response.status_code == 200:
            st.session_state["filter_results"] = response.json()
    except:
        st.session_state["filter_results"] = []

# ── Display results ───────────────────────────────────────────────────────────
st.divider()
results = st.session_state.get("filter_results", [])

if results is not None:
    if len(results) == 0:
        st.info("No restaurants matched your filters. Try broadening your search.")
    else:
        st.write(f"**{len(results)} restaurant(s) found**")
        st.write("")

        # Compare toggle
        compare_mode = st.toggle("Compare mode — sort by rating, price, and distance")

        if compare_mode:
            # Show as a sortable table
            df = pd.DataFrame(results)
            display_cols = [c for c in ['name', 'cuisine_name', 'location',
                                        'avg_rating', 'price_range', 'atmosphere']
                            if c in df.columns]
            df_display = df[display_cols].rename(columns={
                'name': 'Restaurant',
                'cuisine_name': 'Cuisine',
                'location': 'Location',
                'avg_rating': 'Rating',
                'price_range': 'Price',
                'atmosphere': 'Atmosphere'
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)

        else:
            # Show as cards
            for row in results:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.write(f"**{row['name']}**")
                        st.write(f"📍 {row.get('location', '')}  |  "
                                 f"🍴 {row.get('cuisine_name', '')}  |  "
                                 f"✨ {row.get('atmosphere', '')}")
                    with c2:
                        rating = row.get('avg_rating', 'N/A')
                        st.metric("Rating", f"⭐ {rating}" if rating != 'N/A' else 'N/A')
                    with c3:
                        price = row.get('price_range', 'N/A')
                        price_display = '$' * int(price) if price and price != 'N/A' else 'N/A'
                        st.metric("Price", price_display)

# ── Navigation ────────────────────────────────────────────────────────────────
st.divider()
if st.button("← Back to Home", use_container_width=False):
    st.switch_page("pages/00_Olivia_Home.py")
