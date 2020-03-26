from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.app_context().push()

    db.init_app(app)
    migrate.init_app(app, db)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.gps_tracker import bp as gps_tracker_bp
    app.register_blueprint(gps_tracker_bp)

    from app.gateway_sync import bp as gateway_sync_bp
    app.register_blueprint(gateway_sync_bp)

    return app


from app import models
