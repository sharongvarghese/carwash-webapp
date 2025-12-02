# app.py
from flask import Flask
from config import Config
from extensions import db, login_manager
from models import AdminUser
from routes.public import public_bp
from routes.admin import admin_bp
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # Create default admin user if not exists
    with app.app_context():
        if not AdminUser.query.filter_by(username="admin").first():
            admin = AdminUser(username="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: username=admin, password=admin123")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
