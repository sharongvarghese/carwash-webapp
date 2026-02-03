from flask import Flask
from config import Config
from extensions import db, login_manager, mail
from routes.public import public_bp
from routes.admin import admin_bp
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
import pytz
import os

from sqlalchemy.exc import ProgrammingError
from models import AdminUser

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    Migrate(app, db)

    # ✅ Render Free: create tables + admin (ENV based)
    with app.app_context():
        try:
            db.create_all()
        except ProgrammingError:
            pass

        try:
            admin_username = os.environ.get("ADMIN_USERNAME")
            admin_password = os.environ.get("ADMIN_PASSWORD")

            if admin_username and admin_password:
                if not AdminUser.query.filter_by(username=admin_username).first():
                    admin = AdminUser(username=admin_username)
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    db.session.commit()
        except Exception:
            pass

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
