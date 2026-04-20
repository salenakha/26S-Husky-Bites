import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Welcome to HuskyBites, {st.session_state['first_name']}! 🐾")
st.write("### What would you like to do today?")
st.write("Discover great restaurants near Northeastern, curated by fellow Huskies.")

st.divider()

if st.button('🍽️  Browse Student Recommendations',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/01_Recommendations.py')

if st.button('🔍  Filter Restaurants',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/02_Filter_Restaurants.py')

if st.button('❤️  My Saved Favorites',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/03_My_Favorites.py')
