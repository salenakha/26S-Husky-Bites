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

try:
    response = requests.get('http://web-api:4000/marcus/waittime-ratings')
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Correlation analysis
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
                             title="Wait Time vs. Rating (size by review count)")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top restaurants for efficiency
            st.subheader("Top Performers (Highest Rating, Lowest Wait)")
            df['score'] = df['avg_rating'] / (df['avg_wait_minutes'] + 1)
            top_performers = df.sort_values('score', ascending=False).head(5)
            st.table(top_performers[['name', 'avg_rating', 'avg_wait_minutes']])
            
            with st.expander("View Full Data Table"):
                st.dataframe(df)
        else:
            st.info("No data found for wait time analysis.")
    else:
        st.error(f"Error fetching data from API: {response.status_code}")
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
