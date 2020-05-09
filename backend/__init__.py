from flask import Flask
from flask_cors import CORS
from backend.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    cors = CORS(app)
    db.init_app(app)

    with app.app_context():
        from backend import routes, models, schemas 
        db.create_all()
    
        return app

