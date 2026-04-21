import logging
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')
SideBarLinks()

st.title("⚖️ Wait Time vs. Rating Sensitivity Analysis")
st.write("Exploring the correlation between wait times and restaurant ratings.")

# Fetching the list of restaurants for selection
try:
    res = requests.get('http://web-api:4000/jordan/restaurants')
    restaurants = res.json() if res.status_code == 200 else []
    
    # Use name and ID to ensure uniqueness in the dropdown
    restaurant_options = {f"{r['name']} (ID: {r['restaurant_id']})": r['restaurant_id'] for r in restaurants}
    
    selected_option = st.selectbox("Select Restaurant to Analyze", 
                                  options=["All Restaurants"] + list(restaurant_options.keys()))
    
    url = 'http://web-api:4000/marcus/waittime-ratings'
    if selected_option != "All Restaurants":
        url += f"?restaurant_id={restaurant_options[selected_option]}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Fix potential type issues by converting to numeric
            df['avg_wait_minutes'] = pd.to_numeric(df['avg_wait_minutes'], errors='coerce')
            df['avg_rating'] = pd.to_numeric(df['avg_rating'], errors='coerce')
            df['total_reviews'] = pd.to_numeric(df['total_reviews'], errors='coerce')
            
            # Drop rows with NaN if any were created during conversion
            df = df.dropna(subset=['avg_wait_minutes', 'avg_rating'])

            # Correlation analysis
            if len(df) > 1:
                correlation = df['avg_wait_minutes'].corr(df['avg_rating'])
                st.metric("Correlation Coefficient", round(correlation, 3), 
                          delta_color="normal", help="Wait time vs. Rating")
            
            # Scatter plot using Plotly Express
            fig = px.scatter(df, x="avg_wait_minutes", y="avg_rating", 
                             size="total_reviews", color="avg_rating",
                             hover_name="name",
                             labels={
                                 "avg_wait_minutes": "Average Wait Time (mins)",
                                 "avg_rating": "Average Rating",
                                 "total_reviews": "Total Reviews"
                             },
                             title=f"Wait Time vs. Rating for {selected_option}")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top restaurants for efficiency
            st.subheader("Top Performers (Highest Rating, Lowest Wait)")
            # Adding a small constant to avoid division by zero
            df['score'] = df['avg_rating'] / (df['avg_wait_minutes'] + 1)
            top_performers = df.sort_values('score', ascending=False).head(5)
            st.table(top_performers[['name', 'avg_rating', 'avg_wait_minutes']])
            
            with st.expander("View Full Data Table"):
                st.dataframe(df)
        else:
            st.info(f"No data found for {selected_option}.")
    else:
        st.error(f"Error fetching data from API: {response.status_code}")
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
