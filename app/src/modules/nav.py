import streamlit as st


def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


# ---- Role: olivia -----------------------------------------------------------

def olivia_home_nav():
    st.sidebar.page_link("pages/00_Olivia_Home.py", label="Olivia Home", icon="👤")


# ---- Role: jordan -----------------------------------------------------------

def jordan_home_nav():
    st.sidebar.page_link("pages/20_Jordan_Home.py", label="Jordan Home", icon="🛠️")


# ---- Role: marcus -----------------------------------------------------------

def marcus_home_nav():
    st.sidebar.page_link("pages/20_Marcus_Home.py", label="Marcus Home", icon="📊")


# ---- Role: maya -------------------------------------------------------------

def maya_home_nav():
    st.sidebar.page_link("pages/30_Maya_Home.py", label="Maya Home", icon="🍱")


def between_class_nav():
    st.sidebar.page_link("pages/31_Between_Class.py", label="Between-Class Finder", icon="⚡")


def leaderboard_nav():
    st.sidebar.page_link("pages/32_Leaderboard.py", label="Husky Leaderboard", icon="🏆")


def submit_review_nav():
    st.sidebar.page_link("pages/33_Submit_Review.py", label="Submit a Review", icon="✍️")

# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    st.sidebar.image("assets/huskybites_logo.png", width=150)

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "olivia":
            olivia_home_nav()

        if st.session_state["role"] == "jordan":
            jordan_home_nav()

        if st.session_state["role"] == "marcus":
            marcus_home_nav()

        if st.session_state["role"] == "maya":
            maya_home_nav()
            between_class_nav()
            leaderboard_nav()
            submit_review_nav()

    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")

