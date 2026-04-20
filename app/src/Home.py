import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

st.session_state['authenticated'] = False

SideBarLinks(show_home=True)

logger.info("Loading the Home page of the app")
st.title('HuskyBites 🐾')
st.write('#### Hi! As which user would you like to log in?')

if st.button("Act as Olivia, an International Student",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'olivia'
    st.session_state['first_name'] = 'Olivia'
    st.switch_page('pages/00_Olivia_Home.py')

if st.button('Act as Jordan, a System Administrator',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'jordan'
    st.session_state['first_name'] = 'Jordan'
    st.switch_page('pages/10_Jordan_Home.py')

if st.button('Act as Marcus, a Data Analyst',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'marcus'
    st.session_state['first_name'] = 'Marcus'
    st.switch_page('pages/20_Marcus_Home.py')

if st.button('Act as Maya, a Pre-Med Student',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'maya'
    st.session_state['first_name'] = 'Maya'
    st.switch_page('pages/30_Maya_Home.py')