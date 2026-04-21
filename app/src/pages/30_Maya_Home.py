import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}! 👋")
st.write('### What would you like to do today?')

if st.button('Between-Class Meal Finder',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/31_Between_Class.py')

if st.button('Husky Leaderboard',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/32_Leaderboard.py')

if st.button('Submit a Review',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/33_Submit_Review.py')
