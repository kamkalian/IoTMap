from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from app.polygon_builder.polygon_builder import run_polygon_builder

db = SQLAlchemy()

print('Create Polygon Builder App')
app = Flask(__name__)
app.config.from_object(Config)
app.app_context().push()

db.init_app(app)

from app.polygon_builder import bp as polygon_builder_bp
app.register_blueprint(polygon_builder_bp)

run_polygon_builder()