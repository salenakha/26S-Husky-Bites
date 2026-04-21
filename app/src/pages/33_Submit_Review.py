import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Submit a Review ✍️')
st.write('Rate your meal and help other Huskies find great food!')

API_URL = 'http://web-api:4000/maya/reviews'

with st.form('submit_review_form'):
    restaurant_id = st.number_input('Restaurant ID', min_value=1, step=1)
    rating = st.slider('Rating (1-5)', min_value=1, max_value=5, value=5)
    review_text = st.text_area('Your Review (keep it short!)', max_chars=300,
                               placeholder='Fast service, great halal options...')
    submitted = st.form_submit_button('Submit Review')

    if submitted:
        if not review_text.strip():
            st.error('Please write a short review before submitting.')
        else:
            payload = {
                'user_id': st.session_state.get('user_id', 42),
                'restaurant_id': int(restaurant_id),
                'rating': float(rating),
                'review_text': review_text
            }
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 201:
                    st.success('Review submitted! Thanks for helping fellow Huskies 🐾')
                else:
                    st.error(f"Failed to submit: {response.json().get('error', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f'Error connecting to API: {str(e)}')
                st.info('Make sure the API server is running.')

if st.button('Back to Home', type='primary'):
    st.switch_page('pages/30_Maya_Home.py')