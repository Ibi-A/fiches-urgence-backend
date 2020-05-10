from flask import Flask
from flask_cors import CORS
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object(Config)
cors = CORS(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

from app import routes, models

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5000)