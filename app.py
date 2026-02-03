from flask import Flask
from config import Config
from extensions import db, login_manager, mail
from routes.public import public_bp
from routes.admin import admin_bp
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from datetime import datetime
import pytz

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    Migrate(app, db)

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    @app.template_filter('ist_time')
    def ist_time_filter(utc_time):
        if utc_time is None:
            return None
        if utc_time.tzinfo is None:
            utc_time = pytz.utc.localize(utc_time)
        ist_tz = pytz.timezone('Asia/Kolkata')
        return utc_time.astimezone(ist_tz)

    return app
