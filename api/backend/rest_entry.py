from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.db_connection import init_app as init_db
from backend.simple.simple_routes import simple_routes
from backend.ngos.ngo_routes import ngos


def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    load_dotenv()

    # Secret key used by Flask for securely signing session cookies.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Database connection settings — values come from the .env file.
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip()

    # Register the cleanup hook for the database connection.
    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    app.logger.info("create_app(): registering blueprints")
    app.register_blueprint(simple_routes)
    app.register_blueprint(ngos, url_prefix="/ngo")

    # Jordan — system admin routes (restaurants, reviews, activity metrics)
    from backend.jordan.jordan_routes import jordan
    app.register_blueprint(jordan, url_prefix="/jordan")

    # Marcus — data analyst routes (trends, crowd levels, export, performance)
    from backend.marcus.marcus_routes import marcus_routes
    app.register_blueprint(marcus_routes, url_prefix="/marcus")

    # Olivia — international student routes (discovery, filtering, favorites)
    from backend.olivia.olivia_routes import olivia
    app.register_blueprint(olivia, url_prefix="/olivia")

    # Maya — pre-med student routes (wait times, halal, leaderboard, reviews)
    from backend.maya.maya_routes import maya
    app.register_blueprint(maya, url_prefix="/maya")

    return app
