from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from app.extensions import mongo
from app.webhook.routes import webhook
from app.ui.routes import ui
from app.health.routes import health


def create_app():
    # Load environment variables
    load_dotenv()
    
    # Get absolute paths for templates and static
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    
    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/github_webhooks")
    
    print(f"Connecting to MongoDB: {app.config['MONGO_URI']}")  # Debug line
    # Initialize extensions
    mongo.init_app(app)
    print(f"Connected to MongoDB: {mongo.db}")  # Debug line
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(webhook)  # /webhook/receiver
    app.register_blueprint(ui)       # / and /api/events
    app.register_blueprint(health)   # /
    
    return app