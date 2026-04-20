import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

BASE_URL = 'http://api:4000/jordan'

st.title('Review Moderation')
st.write('---')

# ── FILTER AND VIEW REVIEWS ──────────────────────────────────
st.subheader('Browse Reviews')

status_filter = st.selectbox('Filter by Status', ['all', 'approved', 'removed', 'pending'])

try:
    if status_filter == 'all':
        response = requests.get(f'{BASE_URL}/reviews')
    else:
        response = requests.get(f'{BASE_URL}/reviews', params={'status': status_filter})

    if response.status_code == 200:
        reviews = response.json()
        if reviews:
            st.dataframe(reviews, use_container_width=True)
        else:
            st.info('No reviews found.')
    else:
        st.error('Failed to load reviews.')
except Exception as e:
    st.error(f'Error connecting to API: {e}')

st.write('---')

# ── FLAG / SOFT-REMOVE A REVIEW ──────────────────────────────
st.subheader('Flag or Update Review Status')

with st.form('flag_review_form'):
    flag_id = st.number_input('Review ID to Flag', min_value=1, step=1)
    new_status = st.selectbox('Set Status To', ['removed', 'approved', 'pending'])
    flag_submitted = st.form_submit_button('Update Review Status', type='primary')
    if flag_submitted:
        try:
            r = requests.put(f'{BASE_URL}/reviews/{flag_id}/status',
                             json={'status': new_status})
            if r.status_code == 200:
                st.success(f'Review {flag_id} status updated to "{new_status}".')
                st.rerun()
            else:
                st.error(f'Failed: {r.text}')
        except Exception as e:
            st.error(f'Error: {e}')

st.write('---')

# ── PERMANENTLY DELETE A REVIEW ──────────────────────────────
st.subheader('Permanently Delete a Review')

with st.form('delete_review_form'):
    delete_id = st.number_input('Review ID to Delete', min_value=1, step=1)
    st.warning('This permanently removes the review from the database.')
    delete_submitted = st.form_submit_button('Delete Review', type='primary')
    if delete_submitted:
        try:
            r = requests.delete(f'{BASE_URL}/reviews/{delete_id}')
            if r.status_code == 200:
                st.success(f'Review {delete_id} permanently deleted.')
                st.rerun()
            else:
                st.error(f'Failed: {r.text}')
        except Exception as e:
            st.error(f'Error: {e}')
