import os
from flask import Flask
from dotenv import load_dotenv
from config import Config
from extensions import db, login_manager, mail
from models import AdminUser
from routes.public import public_bp
from routes.admin import admin_bp
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

# Load .env
load_dotenv()

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

    return app
    
app = create_app()

if __name__ == "__main__":

    app.run(debug=True)
