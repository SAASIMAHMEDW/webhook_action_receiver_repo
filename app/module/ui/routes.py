from flask import Blueprint, render_template
from app.extensions import mongo
from app.libs.logger import get_logger

logger = get_logger()
ui = Blueprint("ui", __name__)


@ui.route("/")
def dashboard():
    """Render the main dashboard page."""
    logger.info("Rendering dashboard page")
    return render_template("dashboard.html")