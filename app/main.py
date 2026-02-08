from flask import Flask
from app.extensions import mongo
from app.blueprints import register_blueprints
import os
from app.config.env import ENV
from app.libs.logger import get_logger

logger = get_logger()

def create_app() -> Flask:
    try:
        # Static files
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        template_dir = os.path.join(base_dir, 'templates')
        static_dir = os.path.join(base_dir, 'static')

        # Create Flask application
        app = Flask(
            __name__,
            template_folder=template_dir,
            static_folder=static_dir
        )

        # Configuration
        app.config["SECRET_KEY"] = ENV["SECRET_KEY"]
        app.config["MONGO_URI"] = ENV["MONGO_URI"]

        # Database Connection
        logger.debug("Initializing MongoDB connection")
        mongo.init_app(app)
        logger.debug("MongoDB connection initialized")
        # Register blueprints (routers)
        logger.debug("Registering blueprints")
        register_blueprints(app)
        logger.debug("Blueprints registered")
        return app
    except Exception as e:
        logger.exception("Error creating the Flask application")
        exit(1)


app = create_app()