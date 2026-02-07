from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.extensions import mongo
from app.utils.timestamp import format_timestamp
from app.libs.logger import get_logger
from .utils import parse_push_event, parse_pull_request_event
webhook = Blueprint("webhook", __name__)
logger = get_logger()


@webhook.route("/receiver", methods=["POST"])
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
        
        logger.info(f"Event type: {event_type}")
        logger.debug(f"Payload: {payload}")
        
        # Skip ping events (GitHub webhook test)
        if event_type == "ping":
            logger.info("Received ping event from GitHub")
            return jsonify({"status": "ping received"}), 200
        
        # Skip if not a supported event
        if event_type not in ["push", "pull_request"]:
            logger.warning(f"Unsupported event type: {event_type}")
            return jsonify({"status": "ignored", "event": event_type}), 200
        
        # Parse based on event type
        if event_type == "push":
            event_data = parse_push_event(payload)
        elif event_type == "pull_request":
            event_data = parse_pull_request_event(payload)
        else:
            logger.warning(f"Unsupported event type: {event_type}")
            return jsonify({"status": "ignored"}), 200
        
        # Skip if parsing returned None (e.g., non-merge PR close)
        if event_data is None:
            logger.warning("Failed to parse event data")
            return jsonify({"status": "ignored", "reason": "not a merge event"}), 200
        
        result = mongo.db.events.update_one({"request_id": event_data["request_id"]},{"$setOnInsert": event_data},upsert=True)

        if result.upserted_id:
            logger.info("Event added to database")
            return jsonify({
                "status": "success",
                "event": event_data["action"],
                "request_id": event_data["request_id"]
            }), 201
        else:
            logger.info("Event already exists in database")
            return jsonify({
                "status": "skipped",
                "message": "Event already exists",
                "request_id": event_data["request_id"]
            }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


    """Parse GitHub pull_request event."""
    pr = payload.get("pull_request", {})
    action = payload.get("action", "")
    
    # Get author
    author = pr.get("user", {}).get("login", "unknown")
    
    # Get branches
    from_branch = pr.get("head", {}).get("ref", "unknown")
    to_branch = pr.get("base", {}).get("ref", "unknown")
    
    # PR number as request_id
    pr_number = pr.get("number", "unknown")
    
    # UTC timestamp
    timestamp = datetime.now(timezone.utc)
    
    # Determine if it's a merge or just a PR submission
    merged = pr.get("merged", False)
    
    if action == "opened":
        # New PR submitted
        return {
            "request_id": f"PR-{pr_number}",
            "author": author,
            "action": "PULL_REQUEST",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "display_time": format_timestamp(timestamp)
        }
    
    elif action == "closed" and merged:
        # PR was merged (bonus brownie points)
        return {
            "request_id": f"MERGE-{pr_number}",
            "author": author,
            "action": "MERGE",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "display_time": format_timestamp(timestamp)
        }
    
    else:
        # PR closed without merge or other actions - ignore
        return None