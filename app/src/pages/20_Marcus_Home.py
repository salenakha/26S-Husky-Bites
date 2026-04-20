import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome, {st.session_state.get('first_name', 'Marcus')} 👋")
st.write("### What would you like to analyze today?")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button('Trend Dashboard', 
                 type='primary', 
                 use_container_width=True):
        st.switch_page('pages/21_Trend_Dashboard.py')

with col2:
    if st.button('Sensitivity Analysis', 
                 type='primary', 
                 use_container_width=True):
        st.switch_page('pages/22_Sensitivity_Analysis.py')

with col3:
    if st.button('Export Data', 
                 type='primary', 
                 use_container_width=True):
        st.switch_page('pages/23_Export_Data.py')
