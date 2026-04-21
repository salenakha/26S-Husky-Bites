# `pages` Folder
All Streamlit pages for HuskyBites live here. Pages are prefixed by persona so Streamlit loads them in the correct order, and `modules/nav.py` uses the role stored in `session_state` to show only the relevant sidebar links for each user.

## Page Prefixes by Persona

| Prefix | Persona |
|---|---|
| `00–09` | Olivia — International Student |
| `20–29` | Jordan — System Administrator |
| `20–29` | Marcus — Data Analyst |
| `30–39` | Maya — Pre-Med Student |

> Jordan and Marcus share the `20–29` prefix range. Their home pages (`20_Jordan_Home.py` and `20_Marcus_Home.py`) are separate entry points — each persona only sees their own links via the sidebar.

## Olivia — International Student

| File | Description |
|---|---|
| `00_Olivia_Home.py` | Olivia's landing page with navigation to her features |
| `01_Recommendations.py` | Personalized restaurant recommendations based on preferences |
| `02_Filter_Restaurants.py` | Browse restaurants filtered by cuisine, price, and atmosphere |
| `03_My_Favorites.py` | View and manage saved favorite restaurants |

## Jordan — System Administrator

| File | Description |
|---|---|
| `20_Jordan_Home.py` | Jordan's landing page with navigation to admin tools |
| `21_Manage_Restaurants.py` | Add, edit, or update restaurant status (open/closed/inactive) |
| `22_Review_Moderation.py` | Approve, flag, or remove student-submitted reviews |
| `23_DB_Activity.py` | View activity metrics and system usage over time |

## Marcus — Data Analyst

| File | Description |
|---|---|
| `20_Marcus_Home.py` | Marcus's landing page with navigation to analytics tools |
| `21_Trend_Dashboard.py` | Visualize rating trends over time, optionally by restaurant |
| `22_Sensitivity_Analysis.py` | Explore correlations (e.g. wait time vs. rating) |
| `23_Export_Data.py` | Export analytics data for external use |

## Maya — Pre-Med Student

| File | Description |
|---|---|
| `30_Maya_Home.py` | Maya's landing page with navigation to her features |
| `31_Between_Class.py` | Find the fastest realistic meal option based on wait times |
| `32_Leaderboard.py` | Browse top student-rated dishes across all restaurants |
| `33_Submit_Review.py` | Submit a review with dietary tags and allergen info |

## Shared

| File | Description |
|---|---|
| `30_About.py` | About page accessible from all personas via the sidebar |
