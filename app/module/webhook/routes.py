from flask import Blueprint, request, jsonify
from app.extensions import mongo
from app.libs.logger import get_logger
from .utils import parse_push_event, parse_pull_request_event
webhook = Blueprint("webhook", __name__)
logger = get_logger()


@webhook.route("/github", methods=["POST"])
def receiver():
    """
    Receive GitHub webhook events.
    Handles: push, pull_request (opened, closed/merged)
    """
    try:
        logger.info("Received webhook event from GitHub")
        # Get event type from header
        event_type = request.headers.get("X-GitHub-Event", "")
        payload = request.get_json() or {}
        
        logger.info("Event type: %s", event_type)
        logger.debug("Payload keys: %s", list(payload.keys()))
        logger.debug("Repository: %s", payload.get('repository', {}).get('full_name'))
        
        # Skip ping events (GitHub webhook test)
        if event_type == "ping":
            logger.info("Received ping event from GitHub")
            return jsonify({"status": "ping received"}), 200
        
        # Skip if not a supported event
        if event_type not in ["push", "pull_request"]:
            logger.warning("Unsupported event type: %s", event_type)
            return jsonify({"status": "ignored", "event": event_type}), 200
        
        # Parse based on event type
        if event_type == "push":
            event_data = parse_push_event(payload)
        elif event_type == "pull_request":
            event_data = parse_pull_request_event(payload)
        else:
            logger.warning("Unsupported event type: %s", event_type)
            return jsonify({"status": "ignored"}), 200
        
        # Skip if parsing returned None (e.g., non-merge PR close)
        if event_data is None:
            logger.warning("Failed to parse event data")
            return jsonify({"status": "ignored", "reason": "not a merge event"}), 200
        
        result = mongo.db.events.update_one({"request_id": event_data["request_id"]},{"$setOnInsert": event_data},upsert=True)

        if result.upserted_id:
            logger.info("Event added: %s by %s", event_data['action'], event_data['author'])
            return jsonify({
                "status": "success",
                "event": event_data["action"],
                "request_id": event_data["request_id"]
            }), 201
        else:
            logger.info("Event already exists: %s by %s", event_data['action'], event_data['author'])
            return jsonify({
                "status": "skipped",
                "message": "Event already exists",
                "request_id": event_data["request_id"]
            }), 200
        
    except Exception as e:
        logger.exception("Error receiving webhook event")
        return jsonify({"status": "error", "message": str(e)}), 500
