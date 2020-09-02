from flask import Blueprint

bp = Blueprint('http_integration', __name__)

from app.http_integration import routes
