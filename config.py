# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-change-me")
    SQLALCHEMY_DATABASE_URI = "sqlite:///carwash.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
