import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

# ── Page header ───────────────────────────────────────────────────────────────
st.title("My Saved Favorites")
st.write("Restaurants you've saved to revisit later.")
st.divider()

# ── Get the logged-in user's ID from session state ────────────────────────────
# user_id is stored in session_state when the user logs in on Home.py
user_id = st.session_state.get('user_id', 42)   # default to 42 (Olivia's mock user)

# ── Fetch favorites from Flask API ───────────────────────────────────────────
FAV_URL = f"http://web-api:4000/olivia/students/{user_id}/favorites"

try:
    response = requests.get(FAV_URL)

    if response.status_code == 200:
        favorites = response.json()

        if not favorites:
            st.info("You haven't saved any restaurants yet. "
                    "Browse recommendations or filter restaurants to find some!")
        else:
            st.write(f"**{len(favorites)} saved restaurant(s)**")
            st.write("")

            # Display each favorite with a remove button
            for fav in favorites:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.write(f"**{fav['name']}**")
                        st.write(f"📍 {fav.get('location', '')}  |  "
                                 f"🍴 {fav.get('cuisine_name', '')}")
                        st.caption(f"Saved on {fav.get('saved_date', '')}")

                    with col2:
                        rating = fav.get('avg_rating', 'N/A')
                        st.metric("Rating", f"⭐ {rating}" if rating != 'N/A' else 'N/A')

                    with col3:
                        # Remove from favorites button — triggers DELETE route
                        restaurant_id = fav['restaurant_id']
                        if st.button("🗑️ Remove",
                                     key=f"remove_{restaurant_id}",
                                     use_container_width=True):
                            delete_url = (f"http://web-api:4000/olivia/students/"
                                          f"{user_id}/favorites/{restaurant_id}")
                            try:
                                del_response = requests.delete(delete_url)
                                if del_response.status_code == 200:
                                    st.success(f"Removed {fav['name']} from favorites.")
                                    st.rerun()
                                else:
                                    st.error("Could not remove — please try again.")
                            except requests.exceptions.RequestException as e:
                                st.error(f"API error: {str(e)}")

    else:
        st.error(f"Could not load favorites. API returned status {response.status_code}.")

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the API: {str(e)}")
    st.info("Make sure the API container is running on http://web-api:4000")

# ── Save a new favorite ───────────────────────────────────────────────────────
st.divider()
st.write("### ➕ Save a new restaurant")
st.write("Enter a restaurant ID to add it to your favorites.")

with st.form("add_favorite_form"):
    new_restaurant_id = st.number_input(
        "Restaurant ID", min_value=1, step=1,
        help="You can find the restaurant ID on the recommendations or filter pages."
    )
    submitted = st.form_submit_button("Save to Favorites", type="primary")

    if submitted:
        post_url = f"http://web-api:4000/olivia/students/{user_id}/favorites"
        try:
            post_response = requests.post(
                post_url,
                json={"restaurant_id": int(new_restaurant_id)}
            )
            if post_response.status_code == 201:
                st.success("Restaurant saved to your favorites!")
                st.rerun()
            elif post_response.status_code == 400:
                st.error(post_response.json().get('error', 'Invalid request.'))
            else:
                st.error(f"Could not save — API returned {post_response.status_code}.")
        except requests.exceptions.RequestException as e:
            st.error(f"API error: {str(e)}")

# ── Navigation ────────────────────────────────────────────────────────────────
st.divider()
if st.button("← Back to Home", use_container_width=False):
    st.switch_page("pages/00_Olivia_Home.py")
