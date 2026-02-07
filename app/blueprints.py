from flask import Flask
from app.module.health.routes import health
from app.module.webhook.routes import webhook
from app.module.events.routes import events 
from app.module.ui.routes import ui

API_PREFIX = "/api"
API_VERSION_PREFIX = "/v1"

API_PREFIX_V1 = API_PREFIX + API_VERSION_PREFIX

def register_blueprints(app: Flask) -> None:

    app.register_blueprint(health, url_prefix=API_PREFIX_V1 + "/health")
    app.register_blueprint(webhook, url_prefix=API_PREFIX_V1 + "/webhook")
    app.register_blueprint(events, url_prefix=API_PREFIX_V1 + "/events") 
    app.register_blueprint(ui, url_prefix="/")
    