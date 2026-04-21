from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.db_connection import init_app as init_db
from backend.jordan.jordan_routes import jordan
from backend.marcus.marcus_routes import marcus_routes
from backend.maya.maya_routes import maya
from backend.olivia.olivia_routes import olivia

def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    
    load_dotenv()

    # Database configuration from environment variables
    db_user = os.getenv("DB_USER", "root")
    mysql_root_password = os.getenv("MYSQL_ROOT_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "huskybites")
    secret_key = os.getenv("SECRET_KEY", "dev")

    app.config["SECRET_KEY"] = secret_key
    app.config["MYSQL_DATABASE_USER"] = db_user.strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = mysql_root_password.strip()
    app.config["MYSQL_DATABASE_HOST"] = db_host.strip()
    app.config["MYSQL_DATABASE_PORT"] = int(db_port.strip())
    app.config["MYSQL_DATABASE_DB"] = db_name.strip()

    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    app.logger.info("create_app(): registering blueprints")

    # Jordan — system admin routes
    app.register_blueprint(jordan, url_prefix="/jordan")

    # Olivia — international student routes
    app.register_blueprint(olivia, url_prefix="/olivia")

    # Marcus — data analyst routes
    app.register_blueprint(marcus_routes, url_prefix="/marcus")

    # Maya — pre-med student routes
    app.register_blueprint(maya, url_prefix="/maya")

    return app
