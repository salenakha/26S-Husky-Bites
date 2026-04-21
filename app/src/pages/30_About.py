import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# About this App")

st.markdown(
    """
    This is a demo app for Husky Bites, a restaurant review and exploration app made for SP26 CS3200 Project.  

    The goal of this demo is to provide an overview of our app's features and functionality.

    Stay tuned for more information and features to come!
    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
