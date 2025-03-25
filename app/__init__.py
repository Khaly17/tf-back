import os
from flask import Flask, jsonify
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger

from config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
mail = Mail()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_FOLDER = os.path.join(BASE_DIR, '..', 'templates')

def create_app(config_class=Config):
    app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        print("❌ Token invalide :", reason)
        return jsonify({"error": "Invalid token", "reason": reason}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        print("⚠️ Token manquant ou mal formé :", reason)
        return jsonify({"error": "Missing or invalid token", "reason": reason}), 401
    
    CORS(app)
    migrate.init_app(app, db)
    mail.init_app(app) 
    Swagger(app)

    from app.auth.models import User
    from app.category.models import Category
    from app.item.models import Item, Notification, History

    from app.auth.routes import auth_bp
    from app.category.routes import category_bp
    from app.item.routes import item_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(category_bp, url_prefix="/categories")
    app.register_blueprint(item_bp, url_prefix="/items")



    return app
