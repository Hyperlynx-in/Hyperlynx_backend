import os
import sys
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from pathlib import Path
import yaml
from flasgger import Swagger
import urllib.parse
from datetime import timedelta 

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def _get_int_env(name, default_value):
  value = os.getenv(name)
  if value is None or value == "":
    return default_value
  try:
    return int(value)
  except ValueError:
    return default_value

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        seconds=_get_int_env('JWT_ACCESS_TOKEN_LIFETIME', 3600)
    )
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        db_name = os.getenv('SUPABASE_DB_NAME', 'postgres')
        db_user = os.getenv('SUPABASE_DB_USER', 'postgres')
        raw_password = os.getenv('SUPABASE_DB_PASSWORD', '')
        db_password = urllib.parse.quote_plus(raw_password)
        db_host = os.getenv('SUPABASE_DB_HOST', 'localhost')
        db_port = os.getenv('SUPABASE_DB_PORT', '5432')
        database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'success', 'code': 200}), 200
        
   
    try:
        from app.routes import register_all_routes
        register_all_routes(app)
    except Exception as e:
        print(f"Warning: Failed to register routes: {e}", file=sys.stderr)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)