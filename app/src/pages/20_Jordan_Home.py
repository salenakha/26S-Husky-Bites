import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome, {st.session_state.get('first_name', 'Jordan')} 👋")
st.write("### What would you like to manage today?")

if st.button('Manage Restaurants',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/21_Manage_Restaurants.py')

if st.button('Review Moderation',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/22_Review_Moderation.py')

if st.button('Database Activity Dashboard',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/23_DB_Activity.py')
