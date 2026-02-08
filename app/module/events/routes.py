from flask import Blueprint, jsonify, request
from datetime import datetime, timezone, timedelta
from app.extensions import mongo
from app.libs.logger import get_logger
from .utils import format_event_message
logger = get_logger()
events = Blueprint("events", __name__)


@events.route("/")
def get_events():
    try:
        if mongo.db is None:
            logger.warning("MongoDB not connected")
            return jsonify({"error": "MongoDB not connected", "events": []}), 503
        
        # Get last_seen and validate
        last_seen_str = request.args.get("last_seen")
        query = {}
        
        if last_seen_str:
            try:
                from dateutil import parser
                last_seen = parser.isoparse(last_seen_str)
                query["timestamp"] = {"$gt": last_seen}
            except:
                pass
        
        # Always limit to last 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=10*24)
        
        if "timestamp" not in query:
            query["timestamp"] = {"$gt": cutoff}
        
        events_cursor = mongo.db.events.find(query).sort("timestamp", -1).limit(50)

        if events_cursor is None:
            logger.warning("No events found with query: %s", query)
            return jsonify({"error": "No events found", "events": []}), 404
        
        events_list = []
        for event in events_cursor:
            events_list.append({
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

        logger.debug("Fetched %d events with query: %s", len(events_list), query)
        
        return jsonify({
            "events": events_list,
            "count": len(events_list),
            "server_time": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.exception("Error fetching events: %s", e)
        return jsonify({"error": str(e), "events": []}), 500


