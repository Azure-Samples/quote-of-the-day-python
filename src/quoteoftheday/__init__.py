import os
from azure.appconfiguration.provider import load
from featuremanagement import FeatureManager, TargetingContext
from featuremanagement.azuremonitor import publish_telemetry, TargetingSpanProcessor
from azure.monitor.opentelemetry import configure_azure_monitor

from opentelemetry import trace
from opentelemetry.trace import get_tracer_provider

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

DEBUG = True

def targeting_context_accessor() -> TargetingContext:
    if current_user and current_user.is_authenticated:
        user = current_user.username
        user_id = user
    else:
        user_id = "Guest"
    return TargetingContext(user_id=user_id)

configure_azure_monitor(#connection_string=os.getenv("ApplicationInsightsConnectionString"))
    connection_string=os.getenv("ApplicationInsightsConnectionString"),
    span_processors=[TargetingSpanProcessor(targeting_context_accessor=targeting_context_accessor)])

from flask import Flask

app = Flask(__name__, template_folder="../templates", static_folder="../static")
bcrypt = Bcrypt(app)

tracer = trace.get_tracer(__name__, tracer_provider=get_tracer_provider())

CONNECTION_STRING = os.getenv("AzureAppConfigurationConnectionString")

def callback():
    app.config.update(azure_app_config)

global azure_app_config
azure_app_config = load(
    connection_string=CONNECTION_STRING,
    on_refresh_success=callback,
    feature_flag_enabled=True,
    feature_flag_refresh_enabled=True,
)
app.config.update(azure_app_config)
feature_manager = FeatureManager(
    azure_app_config, 
    on_feature_evaluated=publish_telemetry,
    targeting_context_accessor=targeting_context_accessor)

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


from .model import Users

@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

from . import routes
app.register_blueprint(routes.bp)
