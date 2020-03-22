from flask import Blueprint
from app.gps_tracker.ttnmqttclient import TTNMQTTClient
from app.config import Config

bp = Blueprint('gps_tracker', __name__)

client = TTNMQTTClient(Config.APP_ID, Config.ACCESS_KEY)

from app.gps_tracker import routes