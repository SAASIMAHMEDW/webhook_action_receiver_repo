from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from app.extensions import mongo
from app.libs.logger import get_logger

logger = get_logger()
health = Blueprint("health", __name__)


@health.route("/", methods=["GET"])
def index():
    # Send a ping to confirm a successful connection
    try:
        mongo.db.command("ping")
        logger.info("MongoDB connection is healthy.")
        return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}), 200
    except Exception as e:
        logger.error(f"Error checking MongoDB health: {e}")
        return jsonify({"status": "error", "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}), 500