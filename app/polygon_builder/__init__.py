from flask import Blueprint
from app.polygon_builder.polygon_builder import run_polygon_builder
import os


bp = Blueprint('polygon_builder', __name__)

run_pb = os.environ.get('RUN_PB')
if run_pb == '1':
    run_polygon_builder()
