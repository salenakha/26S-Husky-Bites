# 🐾 HuskyBites
<img width="1035" height="339" alt="Screenshot 2026-04-19 at 6 17 57 PM" src="https://github.com/user-attachments/assets/e3408c25-2f59-40e1-9a68-a74493acd17b" />

### CS 3200 Spring 2026
 
HuskyBites is a restaurant discovery and rating app built exclusively for Northeastern University students. Unlike general-purpose platforms like Yelp or Google Maps, HuskyBites only surfaces dining options within a 30-minute walk of the NU Boston campus, and every review comes from a fellow Husky.
 
The app is designed around how students actually eat: fast decisions, dietary needs, tight schedules, and real peer recommendations. Key features include the **Husky Leaderboard** (top student-rated dishes at any restaurant), the **Between Class Recommendation** (fastest realistic meal option based on live wait times and service speed), and a robust **dietary and allergen tagging system**.
 
## Team Members
 
- Salena Kha
- Shi En Leung
- Lam Truong
- Alston Si
- Jaden Pham

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
  - You may use some other Python/code editor.  However, Course staff will only support VS Code. 


## Structure of the Repo

- This repository is organized into five main directories:
  - `./app` - the Streamlit app
  - `./api` - the Flask REST API
  - `./database-files` - SQL scripts to initialize the MySQL database
  - `./datasets` - folder for storing datasets
  - `./ml-src` - folder for ML model development (Jupyter notebooks, training scripts)

- The repo also contains a `docker-compose.yaml` file that is used to set up the Docker containers for the front end app, the REST API, and MySQL database. 

## Setting Up the Repo
 
1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/salenakha/26S-Husky-Bites.git
   cd 26S-Husky-Bites
   ```
 
1. Set up the `.env` file in the `api/` folder based on the `.env.template` file.
   1. Make a copy of `.env.template` and name it `.env`.
   1. Open the new `.env` file.
   1. On the last line, delete the `<...>` placeholder text and set a password. Don't reuse passwords from other services.
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

## Handling User Role Access and Control

In most applications, when a user logs in, they assume a particular role in the app. For instance, when one logs in to a stock price prediction app, they may be a single investor, a portfolio manager, or a corporate executive (of a publicly traded company). Each of those _roles_ will likely present some similar features as well as some different features when compared to the other roles. So, how do you accomplish this in Streamlit? This is sometimes called Role-based Access Control, or **RBAC** for short.

The code in this project demonstrates how to implement a simple RBAC system in Streamlit but without actually using user authentication (usernames and passwords). The Streamlit pages from the original template repo are split up among 3 roles - Political Strategist, USAID Worker, and a System Administrator role (this is used for any sort of system tasks such as re-training ML model, etc.). It also demonstrates how to deploy an ML model.

Wrapping your head around this will take a little time and exploration of this code base. Some highlights are below.

### Getting Started with the RBAC

1. We need to turn off the standard panel of links on the left side of the Streamlit app. This is done through the `app/src/.streamlit/config.toml` file. So check that out. We are turning it off so we can control directly what links are shown.
1. Then I created a new python module in `app/src/modules/nav.py`. When you look at the file, you will see that there are functions for basically each page of the application. The `st.sidebar.page_link(...)` adds a single link to the sidebar. We have a separate function for each page so that we can organize the links/pages by role.
1. Next, check out the `app/src/Home.py` file. Notice that there are 3 buttons added to the page and when one is clicked, it redirects via `st.switch_page(...)` to that Roles Home page in `app/src/pages`. But before the redirect, I set a few different variables in the Streamlit `session_state` object to track role, first name of the user, and that the user is now authenticated.
1. Notice near the top of `app/src/Home.py` and all other pages, there is a call to `SideBarLinks(...)` from the `app/src/modules/nav.py` module. This is the function that will use the role set in `session_state` to determine what links to show the user in the sidebar.
1. The pages are organized by Role. Pages that start with a `0` are related to the _Political Strategist_ role. Pages that start with a `1` are related to the _USAID worker_ role. And, pages that start with a `2` are related to The _System Administrator_ role.


## Demo Video
 
[Watch the HuskyBites demo -- COMING SOON]
