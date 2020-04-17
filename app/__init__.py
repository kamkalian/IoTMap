from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler


db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.app_context().push()

    db.init_app(app)
    migrate.init_app(app, db)
    scheduler.init_app(app)
    scheduler.start()
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.gps_tracker import bp as gps_tracker_bp
    app.register_blueprint(gps_tracker_bp)

    from app.gateway_sync import bp as gateway_sync_bp
    app.register_blueprint(gateway_sync_bp)

    return app


def create_pb_app():

    print('Create Polygon Builder App')
    app = Flask(__name__)
    app.config.from_object(Config)
    app.app_context().push()

    db.init_app(app)

    from app.polygon_builder import bp as polygon_builder_bp
    app.register_blueprint(polygon_builder_bp)

    return app
    

from app import models
