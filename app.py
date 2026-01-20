from flask import Flask
from config import Config
from extensions import db, login_manager, mail
from routes.public import public_bp
from routes.admin import admin_bp
from flask_migrate import Migrate, upgrade
from flask_wtf import CSRFProtect

csrf = CSRFProtect()

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

    # 🔥 AUTO RUN MIGRATIONS (FREE TIER FIX)
    with app.app_context():
        upgrade()

    return app

app = create_app()
