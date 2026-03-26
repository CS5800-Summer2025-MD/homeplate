from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager

# Create the db object globally, but initialize it inside the factory
db = SQLAlchemy()
login_manager = LoginManager()

# contains the instructions to get up the database, routes, and Blueprints
# returns a Flask object
def create_app():
    # create web server object
    app = Flask(__name__)
    # grabs configuration from config.py
    app.config.from_object(Config)

    # Initialize the database with the app, handshake
    # connect the db object created at top to this Flask app
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'main.login'

    # Register Blueprints (Main and API)
    from .routes.main import main_bp
    from .routes.api import api_bp
    # handles front end requests
    app.register_blueprint(main_bp)
    # handles backend requests
    app.register_blueprint(api_bp)

    # Import models here so the database knows the tables exist
    with app.app_context():
        # register models to the db object
        from . import models
        # Creates all the tables needed in Azure, handles SQL
        db.create_all()

    return app