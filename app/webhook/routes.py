from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.extensions import mongo

webhook = Blueprint("webhook", __name__, url_prefix="/webhook")


def format_timestamp(dt):
    """Format datetime to required string format: 1st April 2021 - 9:30 PM UTC"""
    day = dt.day
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    
    formatted = dt.strftime(f"{day}{suffix} %B %Y - %I:%M %p UTC")
    return formatted


@webhook.route("/receiver", methods=["POST"])
def receiver():
    """
    Receive GitHub webhook events.
    Handles: push, pull_request (opened, closed/merged)
    """
    try:
        # Get event type from header
        event_type = request.headers.get("X-GitHub-Event", "")
        payload = request.get_json() or {}
        print("Received event:", payload)
        
        # Skip ping events (GitHub webhook test)
        if event_type == "ping":
            return jsonify({"status": "ping received"}), 200
        
        # Skip if not a supported event
        if event_type not in ["push", "pull_request"]:
            return jsonify({"status": "ignored", "event": event_type}), 200
        
        # Parse based on event type
        if event_type == "push":
            event_data = parse_push_event(payload)
        elif event_type == "pull_request":
            event_data = parse_pull_request_event(payload)
        else:
            return jsonify({"status": "ignored"}), 200
        
        # Skip if parsing returned None (e.g., non-merge PR close)
        if event_data is None:
            return jsonify({"status": "ignored", "reason": "not a merge event"}), 200
        
        result = mongo.db.events.update_one({"request_id": event_data["request_id"]},{"$setOnInsert": event_data},upsert=True)

        if result.upserted_id:
            return jsonify({
                "status": "success",
                "event": event_data["action"],
                "request_id": event_data["request_id"]
            }), 201
        else:
            return jsonify({
                "status": "skipped",
                "message": "Event already exists",
                "request_id": event_data["request_id"]
            }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def parse_push_event(payload):
    """Parse GitHub push event."""
    # Get commit data
    commits = payload.get("commits", [])
    if not commits:
        # Handle empty push (branch creation, etc.)
        head_commit = payload.get("head_commit", {})
        author = head_commit.get("author", {}).get("name") if head_commit else "unknown"
        commit_hash = payload.get("after", "unknown")[:7]
    else:
        # Use first commit's author
        author = commits[0].get("author", {}).get("name", "unknown")
        commit_hash = commits[0].get("id", "unknown")[:7]
    
    # Get branch name (ref format: refs/heads/branch-name)
    ref = payload.get("ref", "")
    to_branch = ref.replace("refs/heads/", "") if ref else "unknown"
    
    # UTC timestamp
    timestamp = datetime.now(timezone.utc)
    
    return {
        "request_id": commit_hash,
        "author": author,
        "action": "PUSH",
        "from_branch": None,  # Push doesn't have from_branch
        "to_branch": to_branch,
        "timestamp": timestamp,
        "display_time": format_timestamp(timestamp)
    }


def parse_pull_request_event(payload):
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