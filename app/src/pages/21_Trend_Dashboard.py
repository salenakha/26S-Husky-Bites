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
    # Fetching the list of restaurants for selection
    res = requests.get('http://web-api:4000/jordan/restaurants')
    restaurants = res.json() if res.status_code == 200 else []
    
    # Use name and ID to ensure uniqueness in the dropdown
    restaurant_options = {f"{r['name']} (ID: {r['restaurant_id']})": r['restaurant_id'] for r in restaurants}
    
    selected_option = st.selectbox("Select Restaurant to Analyze", 
                                  options=["All Restaurants"] + list(restaurant_options.keys()))
    
    url = 'http://web-api:4000/marcus/trends'
    if selected_option != "All Restaurants":
        url += f"?restaurant_id={restaurant_options[selected_option]}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        
        if not df.empty:
            try:
                # Fix potential type issues by converting to numeric
                df['avg_rating'] = pd.to_numeric(df['avg_rating'], errors='coerce')
                df['total_reviews'] = pd.to_numeric(df['total_reviews'], errors='coerce')
                
                df['review_date'] = pd.to_datetime(df['review_date'])
                df = df.sort_values('review_date')
            except Exception as e:
                st.error(f"Pandas processing error: {e}")
                st.write("Data types in DataFrame:")
                st.write(df.dtypes)
                st.stop()
            
            # Line chart for average rating
            st.subheader(f"Average Rating Over Time for {selected_option}")
            st.line_chart(df.set_index('review_date')['avg_rating'])
            
            # Area chart for review count
            st.subheader(f"Total Review Activity for {selected_option}")
            st.area_chart(df.set_index('review_date')['total_reviews'])
            
            # Show the raw data table
            with st.expander("View Raw Data"):
                st.dataframe(df)
        else:
            st.info(f"No rating trend data found for {selected_option}.")
    else:
        st.error(f"Error fetching data from API: {response.status_code}")
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
