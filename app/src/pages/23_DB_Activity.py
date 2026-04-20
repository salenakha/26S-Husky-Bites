import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

BASE_URL = 'http://api:4000/jordan'

st.title('Database Activity Dashboard')
st.write('Monitor system growth over time — reviews, users, and restaurants.')
st.write('---')

try:
    response = requests.get(f'{BASE_URL}/analytics/activity-metrics')
    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            df['metric_date'] = pd.to_datetime(df['metric_date'])
            df = df.sort_values('metric_date')

            # ── KPI SUMMARY CARDS ────────────────────────────
            latest = df.iloc[-1]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('Total Reviews', int(latest['reviews_count']))
            with col2:
                st.metric('Active Users', int(latest['active_users_count']))
            with col3:
                st.metric('Total Restaurants', int(latest['restaurant_count']))

            st.write('---')

            # ── REVIEWS OVER TIME ────────────────────────────
            st.subheader('Reviews Over Time')
            st.line_chart(df.set_index('metric_date')['reviews_count'])

            # ── ACTIVE USERS OVER TIME ───────────────────────
            st.subheader('Active Users Over Time')
            st.line_chart(df.set_index('metric_date')['active_users_count'])

            # ── RESTAURANT COUNT OVER TIME ───────────────────
            st.subheader('Restaurant Count Over Time')
            st.line_chart(df.set_index('metric_date')['restaurant_count'])

            st.write('---')

            # ── RAW DATA TABLE ───────────────────────────────
            st.subheader('Raw Activity Data')
            st.dataframe(df, use_container_width=True)

        else:
            st.info('No activity metrics found in the database.')
    else:
        st.error('Failed to load activity metrics.')
except Exception as e:
    st.error(f'Error connecting to API: {e}')
