from flask import Blueprint
from app.config import Config


bp = Blueprint('gateway_sync', __name__)


from app.gateway_sync import routes