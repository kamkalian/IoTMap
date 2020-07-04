from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
from app.main.grid_view_preparation import GridViewPreparation

print("GridViewPreparation")
gvp = GridViewPreparation()
