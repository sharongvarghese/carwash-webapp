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

    migrate = Migrate(app, db)

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # Create default admin user if not exists
    with app.app_context():
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if admin_username and admin_password:
            if not AdminUser.query.filter_by(username=admin_username).first():
                admin = AdminUser(username=admin_username)
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print(f"Default admin created: {admin_username}")
        else:
            print("⚠️ ADMIN_USERNAME or ADMIN_PASSWORD not set in .env")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
