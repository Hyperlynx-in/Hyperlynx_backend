from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    CORS(app)

    db.init_app(app)

    from app.models import company_profile 

    return app