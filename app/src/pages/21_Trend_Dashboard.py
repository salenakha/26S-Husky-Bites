import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title("📈 Restaurant Rating Trends")
st.write("Visualizing how restaurant quality has evolved over time.")

try:
    # Use the service name defined in docker-compose.yaml (web-api)
    # The API is mapped to port 4000
    response = requests.get('http://web-api:4000/marcus/trends')
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        
        if not df.empty:
            df['review_date'] = pd.to_datetime(df['review_date'])
            df = df.sort_values('review_date')
            
            # Line chart for average rating
            st.subheader("Average Rating Over Time")
            st.line_chart(df.set_index('review_date')['avg_rating'])
            
            # Area chart for review count
            st.subheader("Total Review Activity")
            st.area_chart(df.set_index('review_date')['total_reviews'])
            
            # Show the raw data table
            with st.expander("View Raw Data"):
                st.dataframe(df)
        else:
            st.info("No rating trend data found.")
    else:
        st.error(f"Error fetching data from API: {response.status_code}")
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
