from app.main import create_app
from app.libs.logger import get_logger
from app.config.env import ENV

logger = get_logger()
app = create_app()

PORT = ENV["PORT"]
FLASK_DEBUG = ENV["FLASK_DEBUG"]
FLASK_ENV = ENV["FLASK_ENV"]

if __name__ == "__main__":
    try:
        if FLASK_ENV == "development":
            logger.info(f"Starting application in DEVELOPMENT mode on port {PORT}...")
            use_reload = True
        else:
            logger.info(f"Starting application in PRODUCTION mode on port {PORT}...")
            use_reload = False
        
        app.run(
            debug=FLASK_DEBUG, 
            host="0.0.0.0", 
            port=PORT, 
            use_reloader=use_reload
        )
        
        # Only logs when server shuts down
        logger.info("Application stopped")
        
    except Exception as e:
        logger.exception("Error starting the application")
        exit(1)