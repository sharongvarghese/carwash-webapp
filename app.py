from flask import Flask
from config import Config
from extensions import db, login_manager, mail
from routes.public import public_bp
from routes.admin import admin_bp
from flask_migrate import Migrate, upgrade
from flask_wtf import CSRFProtect
import os

from models import AdminUser   # 👈 your admin model

csrf = CSRFProtect()

def create_admin():
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")

    if not username or not password:
        print("⚠️ ADMIN_USERNAME or ADMIN_PASSWORD not set")
        return

    admin = AdminUser.query.filter_by(username=username).first()

    if not admin:
        admin = AdminUser(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created")
    else:
        print("ℹ️ Admin already exists")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    csrf.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    migrate = Migrate(app, db)

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # 🔥 Render Free Tier fix
    with app.app_context():
        upgrade()          # create tables
        create_admin()     # create admin user

    return app


app = create_app()
