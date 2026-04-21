import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Between-Class Meal Finder')
st.write('Find the fastest meal option near you based on walk time + wait time.')

API_URL = 'http://web-api:4000/maya/restaurants/between-class'

try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        results = response.json()
        if results:
            st.success(f'Found {len(results)} fast options near you!')
            for i, r in enumerate(results, 1):
                # Ensure numeric types
                r['estimated_total_minutes'] = float(r['estimated_total_minutes'])
                r['dist_from_campus'] = float(r['dist_from_campus'])
                r['wait_minutes'] = int(r['wait_minutes'])
                r['avg_rating'] = float(r['avg_rating'])
                
                with st.expander(f"#{i} — {r['name']} (~{round(r['estimated_total_minutes'], 1)} min total)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Walk Time", f"{round(r['dist_from_campus'] * 12)} min")
                    with col2:
                        st.metric("Wait Time", f"{r['wait_minutes']} min")
                    with col3:
                        st.metric("Avg Rating", f"⭐ {r['avg_rating']}")
                    st.write(f"📍 {r['location']}")
                    if r.get('halal_certified'):
                        st.success('✅ Halal Certified')
        else:
            st.info('No results found right now.')
    else:
        st.error('Could not fetch data from the API.')
except requests.exceptions.RequestException as e:
    st.error(f'Error connecting to API: {str(e)}')
    st.info('Make sure the API server is running.')

if st.button('Back to Home', type='primary'):
    st.switch_page('pages/30_Maya_Home.py')