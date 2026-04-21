import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title("📥 Export Restaurant Data")
st.write("Download anonymized review data for external analysis.")

st.subheader("Filter Export Settings")

try:
    # Optional filter: Get all restaurants for a dropdown
    response = requests.get('http://web-api:4000/jordan/restaurants')
    restaurants = response.json() if response.status_code == 200 else []
    
    # Use name and ID to ensure uniqueness in the dropdown
    restaurant_options = {f"{r['name']} (ID: {r['restaurant_id']})": r['restaurant_id'] for r in restaurants}
    
    selected_option = st.selectbox("Select Restaurant (optional)", 
                                  options=["All Restaurants"] + list(restaurant_options.keys()))
    
    # Trigger the export when a button is clicked
    if st.button("Generate Export Data", type="primary"):
        url = 'http://web-api:4000/marcus/export'
        if selected_option != "All Restaurants":
            url += f"?restaurant_id={restaurant_options[selected_option]}"
            
        # Fetching the export data from the API
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            
            if not df.empty:
                # Ensure numeric types
                if 'rating' in df.columns:
                    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
                
                st.success(f"Generated data for {len(df)} reviews.")
                st.dataframe(df.head(20))
                
                # Convert to CSV for download
                csv = df.to_csv(index=False).encode('utf-8')
                
                # Use a download button for the CSV
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"restaurant_export_{selected_option.replace(' ', '_')}.csv",
                    mime='text/csv'
                )
            else:
                st.info(f"No data found for {selected_option}.")
        else:
            st.error(f"Error generating export data: {response.status_code}")
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
