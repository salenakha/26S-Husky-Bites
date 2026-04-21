# HuskyBites 🐾
<img width="1035" height="339" alt="Screenshot 2026-04-19 at 6 17 57 PM" src="https://github.com/user-attachments/assets/e3408c25-2f59-40e1-9a68-a74493acd17b" />

## Overview

HuskyBites is a restaurant discovery and rating app built exclusively for Northeastern University students. Unlike general-purpose platforms like Yelp or Google Maps, HuskyBites only surfaces dining options within a 30-minute walk of the NU Boston campus, and every review comes from a fellow Husky.

The app is designed around how students actually eat: fast decisions, dietary needs, tight schedules, and real peer recommendations. Key features include the **Husky Leaderboard** (top student-rated dishes at any restaurant), the **Between Class Recommendation** (fastest realistic meal option based on live wait times and service speed), and a robust **dietary and allergen tagging system**.

## Team Members

- Salena Kha
- Shi En Leung
- Lam Truong
- Alston Si
- Jaden Pham

## User Personas

HuskyBites supports four distinct user roles, each with a tailored experience:

| Persona | Role | Key Features |
|---|---|---|
| **Olivia** | International Student | Personalized recommendations, favorites feed, wait times, restaurant comparisons, dietary filtering |
| **Jordan** | System Administrator | Manage restaurants, moderate reviews, view activity metrics, export data |
| **Marcus** | Data Analyst | Rating trend dashboard, wait time vs. rating correlation, sensitivity analysis |
| **Maya** | Pre-Med Student | Between-class meal finder, Husky Leaderboard, submit reviews, allergen/halal filtering |

## Prerequisites

- A GitHub Account
- A terminal-based git client or GUI Git client such as GitHub Desktop or the Git plugin for VSCode.
- A distribution of Python running on your laptop. The distribution supported by the course is [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install).
  - Create a new Python 3.11 environment in `conda` named `db-proj` by running:
     ```bash
     conda create -n db-proj python=3.11
     ```
  - Install the Python dependencies listed in `api/requirements.txt` and `app/src/requirements.txt` into your local Python environment. You can do this by running `pip install -r requirements.txt` in each respective directory.
     ```bash
     cd api
     pip install -r requirements.txt
     cd ../app/src
     pip install -r requirements.txt
     ```
     Note that the `..` means go to the parent folder of the folder you're currently in (which is `api/` after the first command).
     > **Why install locally if everything runs in Docker?** Installing the packages locally lets your IDE (VSCode) provide autocompletion, linting, and error highlighting as you write code. The app itself always runs inside the Docker containers — the local install is just for editor support.
- VSCode with the Python Plugin installed
  - You may use some other Python/code editor. However, course staff will only support VS Code.

## Structure of the Repo

This repository is organized into five main directories:

- `./app` — the Streamlit frontend app
- `./api` — the Flask REST API
- `./database-files` — SQL scripts to initialize the MySQL database
- `./datasets` — folder for storing datasets
- `./ml-src` — folder for future ML model development (Jupyter notebooks, training scripts)

The repo also contains a `docker-compose.yaml` file used to set up Docker containers for the frontend, REST API, and MySQL database.

## Setting Up the Repo

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/salenakha/26S-Husky-Bites.git
   cd 26S-Husky-Bites
   ```

1. Set up the `.env` file in the `api/` folder based on the `.env.template` file.
   1. Make a copy of `.env.template` and name it `.env`.
   1. Open the new `.env` file.
   1. On the last line, delete the `<...>` placeholder text and set a password.

1. Start all containers:
   ```bash
   docker compose up -d
   ```

   This will spin up three services:
   - **db** — MySQL database, auto-executes all `.sql` files in `database-files/` on first creation
   - **api** — Flask REST API, running on `http://localhost:4000`
   - **app** — Streamlit frontend, running on `http://localhost:8501`

## Docker Commands Reference

```bash
# Start all containers in the background
docker compose up -d

# Shut down and delete all containers
docker compose down

# Start only the database container
docker compose up db -d

# Stop containers without deleting them
docker compose stop

# Recreate the database container (required after any SQL file changes)
docker compose down db -v && docker compose up db -d
```

> **Important:** The MySQL container only executes `.sql` files in `database-files/` when it is first **created**, not when it is restarted. If you update the schema or mock data, you must recreate the container using the last command above.

## Important Tips

- Any changes made to the Flask API or Streamlit app code are hot-reloaded when files are saved.
  - In the Streamlit browser tab, click **Always Rerun** so changes are reflected immediately.
  - If a bug shuts a container down, fix the bug and restart with `docker compose restart`.
- The MySQL container logs are your friend. Access them in Docker Desktop under the container's **Logs** tab. Search for `Error` to quickly find issues with your `.sql` files.
- `.sql` files in `database-files/` are executed in **alphabetical order**.

## Role-Based Access Control (RBAC)

HuskyBites uses a simple RBAC system in Streamlit — no real authentication, just role selection on the home screen. When a persona button is clicked on `Home.py`, a role is stored in Streamlit's `session_state`, and the sidebar dynamically shows only the pages relevant to that role.

### How It Works

1. **Sidebar navigation is disabled** globally via `app/src/.streamlit/config.toml` so the app controls exactly which links appear.
1. **`app/src/modules/nav.py`** defines sidebar link functions per page, organized by role. `SideBarLinks()` reads `session_state.role` and renders the appropriate links.
1. **`app/src/Home.py`** presents four persona buttons. Clicking one sets `session_state.role`, `session_state.first_name`, and `session_state.authenticated`, then redirects to that persona's home page.
1. **Pages are prefixed by role:**
   - `00_` — Olivia (International Student)
   - `20_` — Jordan (System Administrator) and Marcus (Data Analyst)
   - `30_` — Maya (Pre-Med Student)

## Demo Video

[Watch the HuskyBites demo -- COMING SOON]
