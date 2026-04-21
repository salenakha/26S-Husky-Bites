import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Husky Leaderboard 🏆')
st.write('Top-ranked restaurants based on student ratings.')

API_URL = 'http://web-api:4000/maya/leaderboard'

try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        results = response.json()
        if results:
            for r in results:
                with st.expander(f"#{r['rank_num']} — {r['name']}  ⭐ {r['score_avg']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"📍 {r['location']}")
                    with col2:
                        st.write(f"💰 Price Range: {'$' * int(r['price_range'])}")
                    with col3:
                        st.write(f"🚶 {r['dist_from_campus']} miles from campus")
                    if r.get('halal_certified'):
                        st.success('✅ Halal Certified')
        else:
            st.info('No leaderboard data available.')
    else:
        st.error('Could not fetch leaderboard from the API.')
except requests.exceptions.RequestException as e:
    st.error(f'Error connecting to API: {str(e)}')
    st.info('Make sure the API server is running.')

if st.button('Back to Home', type='primary'):
    st.switch_page('pages/30_Maya_Home.py')