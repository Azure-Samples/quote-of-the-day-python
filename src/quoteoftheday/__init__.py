import os
from azure.appconfiguration.provider import load
from featuremanagement import FeatureManager
from featuremanagement.azuremonitor import publish_telemetry
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace import get_tracer_provider
from flask_bcrypt import Bcrypt

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

DEBUG = True

configure_azure_monitor(connection_string=os.getenv("ApplicationInsightsConnectionString"))

from flask import Flask

app = Flask(__name__, template_folder="../templates", static_folder="../static")
bcrypt = Bcrypt(app)

tracer = trace.get_tracer(__name__, tracer_provider=get_tracer_provider())

CONNECTION_STRING = os.getenv("AzureAppConfigurationConnectionString")

def callback():
    app.config.update(azure_app_config)

def custom_publish(evaluation_event):
    feature_flag_reference = evaluation_event.feature.telemetry.metadata["feature_flag_reference"]
    feature_flag_id = evaluation_event.feature.telemetry.metadata["feature_flag_id"]
    etag = evaluation_event.feature.telemetry.metadata["etag"]
    evaluation_event.feature.telemetry.metadata["FeatureFlagReference"] = feature_flag_reference
    evaluation_event.feature.telemetry.metadata["FeatureFlagId"] = feature_flag_id
    evaluation_event.feature.telemetry.metadata["ETag"] = etag
    publish_telemetry(evaluation_event)

global azure_app_config
azure_app_config = load(
    connection_string=CONNECTION_STRING,
    on_refresh_success=callback,
    feature_flag_enabled=True,
    feature_flag_refresh_enabled=True,
)
app.config.update(azure_app_config)
feature_manager = FeatureManager(azure_app_config, on_feature_evaluated=custom_publish)

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
