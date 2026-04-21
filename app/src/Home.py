import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

st.session_state['authenticated'] = False

SideBarLinks(show_home=True)

logger.info("Loading the Home page of the app")

# add logo here
with open("assets/logo.svg", "r") as f:
    svg = f.read()
st.markdown(svg, unsafe_allow_html=True)

st.write("## Welcome to HuskyBites")
st.write("#### The restaurant discovery app built for Northeastern students.")
st.write("---")
st.write("#### Who are you today?")

if st.button("Olivia: International Student",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'olivia'
    st.session_state['first_name'] = 'Olivia'
    st.session_state['user_id'] = 1 # gmeriot0, int_student
    logger.info("Logging in as Olivia (International Student)")
    st.switch_page('pages/00_Olivia_Home.py')

if st.button("Jordan: System Administrator",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'jordan'
    st.session_state['first_name'] = 'Jordan'
    st.session_state['user_id'] = 10 # tgreenman9, admin
    logger.info("Logging in as Jordan (System Admin)")
    st.switch_page('pages/20_Jordan_Home.py')

if st.button("Marcus: Data Analyst",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'marcus'
    st.session_state['first_name'] = 'Marcus'
    st.session_state['user_id'] = 2 # aclaybourne1, analyst
    logger.info("Logging in as Marcus (Data Analyst)")
    st.switch_page('pages/20_Marcus_Home.py')

if st.button("Maya: Pre-Med Student",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'maya'
    st.session_state['first_name'] = 'Maya'
    st.session_state['user_id'] = 5 # jcurran4, pre_med_student
    logger.info("Logging in as Maya (Pre-Med Student)")
    st.switch_page('pages/30_Maya_Home.py')
