import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

# ── Page header ───────────────────────────────────────────────────────────────
st.title("Student Recommendations")
st.write("Restaurants reviewed and rated by fellow Northeastern students — no tourists, no noise.")
st.divider()

# ── Fetch data from Flask API ─────────────────────────────────────────────────
API_URL = "http://web-api:4000/olivia/restaurants/recommendations"

try:
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()

        if not data:
            st.info("No student-reviewed restaurants found right now. Check back soon!")
        else:
            # Convert to DataFrame for easy display
            df = pd.DataFrame(data)

            # ── Summary metric ────────────────────────────────────────────────
            st.metric("Restaurants found", len(df))
            st.write("")

            # ── Display each restaurant as a card ─────────────────────────────
            for _, row in df.iterrows():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.write(f"**{row['name']}**")
                        st.write(f"📍 {row['location']}")
                        if row.get('review_text'):
                            st.caption(f"💬 \"{row['review_text']}\"")

                    with col2:
                        st.metric("Rating", f"⭐ {row['rating']}")

                    with col3:
                        dist = row.get('dist_from_campus', 'N/A')
                        st.metric("Distance", f"{dist} mi" if dist != 'N/A' else 'N/A')

    else:
        st.error(f"Could not load recommendations. API returned status {response.status_code}.")

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the API: {str(e)}")
    st.info("Make sure the API container is running on http://web-api:4000")

# ── Navigation ────────────────────────────────────────────────────────────────
st.divider()
if st.button("← Back to Home", use_container_width=False):
    st.switch_page("pages/00_Olivia_Home.py")
