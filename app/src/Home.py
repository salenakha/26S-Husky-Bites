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
    st.session_state['user_id'] = 42
    logger.info("Logging in as Olivia — International Student")
    st.switch_page('pages/00_Olivia_Home.py')

if st.button("Olivia: International Student",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'pol_strat_advisor'
    st.session_state['first_name'] = 'John'
    logger.info("Logging in as Political Strategy Advisor Persona")
    st.switch_page('pages/00_Pol_Strat_Home.py')

if st.button("Jordan: System Administrator",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'administrator'
    st.session_state['first_name'] = 'Jordan'
    logger.info("Logging in as Jordan (System Admin)")
    st.switch_page('pages/10_Jordan_Home.py')

if st.button("Marcus: Data Analyst",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'analyst'
    st.session_state['first_name'] = 'Marcus'
    logger.info("Logging in as Marcus (Data Analyst)")
    st.switch_page('pages/20_Marcus_Home.py')

if st.button("Maya: Pre-Med Student",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'student_premed'
    st.session_state['first_name'] = 'Maya'
    logger.info("Logging in as Maya (Pre-Med Student)")
    st.switch_page('pages/30_Maya_Home.py')