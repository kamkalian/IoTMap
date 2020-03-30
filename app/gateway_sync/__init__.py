from flask import Blueprint
from app.gateway_sync.ttn_sync import run_ttn_sync


bp = Blueprint('gateway_sync', __name__)
