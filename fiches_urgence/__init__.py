from flask import Flask
from flask_cors import CORS
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from fiches_urgence.config import Config

db = SQLAlchemy()
ma = Marshmallow()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """ Forces any sqlite db to enable foreign keys check """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_app() -> Flask:
    """ Constructs the core applications

    Returns:
        Flask:  a flask app
    """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)

    with app.app_context():
        from fiches_urgence import routes, models, schemas  # noqa: F401
        db.create_all()
        return app
