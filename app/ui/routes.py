from flask import Blueprint, render_template, jsonify, request
from datetime import datetime, timezone
from app.extensions import mongo

ui = Blueprint("ui", __name__)


@ui.route("/")
def dashboard():
    """Render the main dashboard page."""
    return render_template("dashboard.html")




@ui.route("/api/events")
def get_events():
    try:
        if mongo.db is None:
            return jsonify({"error": "MongoDB not connected", "events": []}), 503
        
        # Get last_seen and validate
        last_seen_str = request.args.get("last_seen")
        query = {}
        
        if last_seen_str:
            try:
                # Simple parsing - just try to parse it
                from dateutil import parser
                last_seen = parser.isoparse(last_seen_str)
                query["timestamp"] = {"$gt": last_seen}
            except:
                # If parsing fails, ignore the filter
                pass
        
        # Always limit to last 24 hours
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        
        if "timestamp" not in query:
            query["timestamp"] = {"$gt": cutoff}
        
        events_cursor = mongo.db.events.find(query).sort("timestamp", -1).limit(50)
        
        events = []
        for event in events_cursor:
            events.append({
                "id": str(event["_id"]),
                "request_id": event.get("request_id"),
                "author": event.get("author"),
                "action": event.get("action"),
                "from_branch": event.get("from_branch"),
                "to_branch": event.get("to_branch"),
                "timestamp": event.get("timestamp").isoformat() if event.get("timestamp") else None,
                "display_time": event.get("display_time"),
                "message": format_event_message(event)
            })
        
        return jsonify({
            "events": events,
            "count": len(events),
            "server_time": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "events": []}), 500

def format_event_message(event):
    """Format event into human-readable message."""
    action = event.get("action")
    author = event.get("author")
    from_branch = event.get("from_branch")
    to_branch = event.get("to_branch")
    display_time = event.get("display_time", "")
    
    if action == "PUSH":
        return f'{author} pushed to "{to_branch}" on {display_time}'
    
    elif action == "PULL_REQUEST":
        return f'{author} submitted a pull request from "{from_branch}" to "{to_branch}" on {display_time}'
    
    elif action == "MERGE":
        return f'{author} merged branch "{from_branch}" to "{to_branch}" on {display_time}'
    
    return f"Unknown event by {author}"