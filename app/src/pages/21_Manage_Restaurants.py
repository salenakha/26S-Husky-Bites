import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

BASE_URL = 'http://api:4000/jordan'

st.title('Manage Restaurants')
st.write('---')

# ── VIEW ALL RESTAURANTS ─────────────────────────────────────
st.subheader('All Restaurants')

try:
    response = requests.get(f'{BASE_URL}/restaurants')
    if response.status_code == 200:
        restaurants = response.json()
        if restaurants:
            st.dataframe(restaurants, use_container_width=True)
        else:
            st.info('No restaurants found.')
    else:
        st.error('Failed to load restaurants.')
except Exception as e:
    st.error(f'Error connecting to API: {e}')

st.write('---')

# ── ADD NEW RESTAURANT ───────────────────────────────────────
st.subheader('Add New Restaurant')

with st.form('add_restaurant_form'):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input('Restaurant Name')
        location = st.text_input('Location / Address')
        cuisine_id = st.number_input('Cuisine ID', min_value=1, step=1)
        neighborhood_id = st.number_input('Neighborhood ID', min_value=1, step=1)
        hours = st.text_input('Hours (e.g. 9am-10pm)')
    with col2:
        status = st.selectbox('Status', ['open', 'closed', 'inactive'])
        halal_certified = st.checkbox('Halal Certified')
        price_range = st.number_input('Price Range (1-4)', min_value=1.0, max_value=4.0, step=0.5)
        dist_from_campus = st.number_input('Distance from Campus (miles)', min_value=0.0, step=0.1)
        atmosphere = st.selectbox('Atmosphere', ['casual', 'cozy', 'lively', 'quiet', 'upscale'])
        dietary_options = st.text_input('Dietary Options (e.g. vegan, halal)')

    submitted = st.form_submit_button('Add Restaurant', type='primary')
    if submitted:
        if name and location:
            payload = {
                'name': name,
                'location': location,
                'cuisine_id': cuisine_id,
                'neighborhood_id': neighborhood_id,
                'hours': hours,
                'working_hours': hours,
                'status': status,
                'halal_certified': halal_certified,
                'price_range': price_range,
                'dist_from_campus': dist_from_campus,
                'atmosphere': atmosphere,
                'dietary_options': dietary_options
            }
            try:
                r = requests.post(f'{BASE_URL}/restaurants', json=payload)
                if r.status_code == 201:
                    st.success(f'Restaurant "{name}" added successfully!')
                    st.rerun()
                else:
                    st.error(f'Failed to add restaurant: {r.text}')
            except Exception as e:
                st.error(f'Error: {e}')
        else:
            st.warning('Name and Location are required.')

st.write('---')

# ── UPDATE RESTAURANT ────────────────────────────────────────
st.subheader('Update Restaurant Info')

with st.form('update_restaurant_form'):
    update_id = st.number_input('Restaurant ID to Update', min_value=1, step=1)
    col1, col2 = st.columns(2)
    with col1:
        new_location = st.text_input('New Location')
        new_hours = st.text_input('New Hours')
        new_dietary = st.text_input('New Dietary Options')
    with col2:
        new_halal = st.checkbox('Halal Certified')
        new_price = st.number_input('New Price Range', min_value=1.0, max_value=4.0, step=0.5)
        new_atmosphere = st.selectbox('New Atmosphere', ['casual', 'cozy', 'lively', 'quiet', 'upscale'])

    update_submitted = st.form_submit_button('Update Restaurant', type='primary')
    if update_submitted:
        payload = {
            'location': new_location,
            'hours': new_hours,
            'working_hours': new_hours,
            'dietary_options': new_dietary,
            'halal_certified': new_halal,
            'price_range': new_price,
            'atmosphere': new_atmosphere
        }
        try:
            r = requests.put(f'{BASE_URL}/restaurants/{update_id}', json=payload)
            if r.status_code == 200:
                st.success(f'Restaurant {update_id} updated successfully!')
            else:
                st.error(f'Failed to update: {r.text}')
        except Exception as e:
            st.error(f'Error: {e}')

st.write('---')

# ── UPDATE STATUS ────────────────────────────────────────────
st.subheader('Change Restaurant Status')

with st.form('status_form'):
    status_id = st.number_input('Restaurant ID', min_value=1, step=1, key='status_id')
    new_status = st.selectbox('New Status', ['open', 'closed', 'inactive', 'deleted'])
    status_submitted = st.form_submit_button('Update Status', type='primary')
    if status_submitted:
        try:
            r = requests.put(f'{BASE_URL}/restaurants/{status_id}/status',
                             json={'status': new_status})
            if r.status_code == 200:
                st.success(f'Restaurant {status_id} marked as {new_status}.')
            else:
                st.error(f'Failed: {r.text}')
        except Exception as e:
            st.error(f'Error: {e}')

st.write('---')

# ── DELETE RESTAURANT ────────────────────────────────────────
st.subheader('Delete Restaurant')

with st.form('delete_restaurant_form'):
    delete_id = st.number_input('Restaurant ID to Delete', min_value=1, step=1)
    st.warning('This will soft-delete the restaurant (marks as deleted). Cannot be undone easily.')
    delete_submitted = st.form_submit_button('Delete Restaurant', type='primary')
    if delete_submitted:
        try:
            r = requests.delete(f'{BASE_URL}/restaurants/{delete_id}')
            if r.status_code == 200:
                st.success(f'Restaurant {delete_id} deleted.')
                st.rerun()
            else:
                st.error(f'Failed: {r.text}')
        except Exception as e:
            st.error(f'Error: {e}')
