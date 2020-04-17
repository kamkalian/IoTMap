from flask import Blueprint
from app.polygon_builder.polygon_builder import run_polygon_builder
import os

bp = Blueprint('polygon_builder', __name__)

#run_polygon_builder()
