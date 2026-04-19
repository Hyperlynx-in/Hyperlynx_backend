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
    
    # Swagger Metadata
    app.config['SWAGGER'] = {
        'title': 'Hyperlynx Backend API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'Django-to-Flask API with JWT Authentication and Framework Library Management',
        'termsOfService': '',
        'contact': {
            'name': 'Hyperlynx Support',
            'email': 'support@hyperlynx.com',
            'url': 'https://hyperlynx.com'
        },
        'license': {
            'name': 'MIT',
            'url': 'https://opensource.org/licenses/MIT'
        },
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
            }
        },
        'security': [
            {
                'Bearer': []
            }
        ]
    }
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = _get_int_env('JWT_ACCESS_TOKEN_LIFETIME', 3600)
    
    # Database Configuration
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Construct from individual variables
        db_name = os.getenv('SUPABASE_DB_NAME', 'postgres')
        db_user = os.getenv('SUPABASE_DB_USER', 'postgres')
        raw_password = os.getenv('SUPABASE_DB_PASSWORD', '')
        db_password = urllib.parse.quote_plus(raw_password)
        db_host = os.getenv('SUPABASE_DB_HOST', 'localhost')
        db_port = os.getenv('SUPABASE_DB_PORT', '5432')
        database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 1,  # Serverless functions should use minimal pool
        'max_overflow': 0,  # No overflow for serverless
        'pool_timeout': 10,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10
        }
    }
    
    # CORS Configuration
    cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173", 
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://localhost:8080",
                "http://localhost:5678/",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"]
        }
    }, supports_credentials=True)
    
    # Initialize extensions
    db.init_app(app)
    # Don't initialize migrate on Vercel serverless
    if os.getenv('VERCEL') != '1':
        migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Swagger/OpenAPI Configuration - enabled everywhere
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
        "url_prefix": None
    }
    
    # Initialize Swagger with error handling
    try:
        swagger = Swagger(app, config=swagger_config)
    except Exception as e:
        print(f"Warning: Swagger initialization failed: {e}", file=sys.stderr)
        pass
    
    # Register routes
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'status': 'success',
            'message': 'Hyperlynx Backend API',
            'version': '1.0.0',
            'docs': '/docs',
            'health': '/api/health'
        }), 200
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'success',
            'message': 'Hyperlynx API is running',
            'code': 200
        }), 200
    
    @app.route('/api/framework-library', methods=['GET'])
    def framework_library():
        framework_name = request.args.get('name', None)
        base_dir = Path(__file__).resolve().parent
        libraries_dir = base_dir / 'libraries'
        
        if not libraries_dir.exists():
            return jsonify({
                'status': 'error',
                'message': 'Libraries directory not found',
                'code': 404
            }), 404
        
        # If specific framework requested
        if framework_name:
            if not framework_name.endswith('.yaml'):
                framework_name = f"{framework_name}.yaml"
            
            framework_path = libraries_dir / framework_name
            
            if not framework_path.exists():
                return jsonify({
                    'status': 'error',
                    'message': f'Framework "{framework_name}" not found',
                    'code': 404
                }), 404
            
            try:
                with open(framework_path, 'r', encoding='utf-8') as file:
                    framework_data = yaml.safe_load(file)
                
                return jsonify({
                    'status': 'success',
                    'data': framework_data,
                    'code': 200
                }), 200
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Error reading framework: {str(e)}',
                    'code': 500
                }), 500
        
        # List all available frameworks (metadata only)
        try:
            yaml_files = sorted([f for f in libraries_dir.glob('*.yaml') if f.is_file()])
            
            frameworks = []
            for yaml_file in yaml_files[:100]:  # Limit to first 100 for performance
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as file:
                        content = file.read(1000)
                        frameworks.append({
                            'filename': yaml_file.name,
                            'name': yaml_file.stem,
                            'size': yaml_file.stat().st_size
                        })
                except Exception as e:
                    continue
            
            return jsonify({
                'status': 'success',
                'count': len(frameworks),
                'data': frameworks,
                'code': 200
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error listing frameworks: {str(e)}',
                'code': 500
            }), 500
    
    # Auth routes
    from app.models.user import User
    from werkzeug.security import generate_password_hash, check_password_hash
    from flask_jwt_extended import create_access_token, create_refresh_token
    
    @app.route('/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        password2 = data.get('password2', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400
        if password != password2:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        try:
            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Username already exists'}), 400
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already exists'}), 400
            
            user = User(username=username, email=email, first_name=first_name, last_name=last_name)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'message': 'User registered successfully',
                'user': user.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    
    @app.route('/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        try:
            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user or not user.check_password(password):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            if not user.is_active:
                return jsonify({'error': 'Account is inactive'}), 401
            
            # FIXED: Identity cast to string
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }), 200
        except Exception as e:
            return jsonify({'error': f'Login failed: {str(e)}'}), 500
    
    # JWT Token endpoints
    @app.route('/api/token/', methods=['POST'])
    def get_token():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        try:
            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user or not user.check_password(password):
                return jsonify({'error': 'Invalid credentials'}), 401
            
            if not user.is_active:
                return jsonify({'error': 'Account is inactive'}), 401
            
            # FIXED: Identity cast to string
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return jsonify({
                'access': access_token,
                'refresh': refresh_token
            }), 200
        except Exception as e:
            return jsonify({'error': f'Token generation failed: {str(e)}'}), 500
    
    @app.route('/api/token/refresh/', methods=['POST'])
    def refresh_token_endpoint():
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        # Try to get refresh token from body or header
        data = request.get_json() or {}
        refresh_token = data.get('refresh')
        
        try:
            # This requires the refresh token in the Authorization header
            @jwt_required(refresh=True)
            def _refresh():
                user_id = get_jwt_identity()
                # FIXED: Identity cast to string
                new_access_token = create_access_token(identity=str(user_id))
                return jsonify({'access': new_access_token}), 200
            
            return _refresh()
        except Exception as e:
            return jsonify({'error': f'Token refresh failed: {str(e)}'}), 401
    
    # User endpoints with /api/users/ prefix
    @app.route('/api/users/register/', methods=['POST'])
    def register_user():
        return register()  # Reuse the register function
    
    @app.route('/api/users/profile/', methods=['GET'])
    def get_user_profile():
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        @jwt_required()
        def _get_profile():
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify(user.to_dict()), 200
        
        return _get_profile()
    
    @app.route('/api/users/profile/', methods=['PUT'])
    def update_user_profile():
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        @jwt_required()
        def _update_profile():
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            try:
                if 'email' in data:
                    email = data['email'].strip()
                    existing = User.query.filter(User.email == email, User.id != user.id).first()
                    if existing:
                        return jsonify({'error': 'Email already in use'}), 400
                    user.email = email
                
                if 'first_name' in data:
                    user.first_name = data['first_name'].strip()
                
                if 'last_name' in data:
                    user.last_name = data['last_name'].strip()
                
                db.session.commit()
                
                return jsonify({
                    'message': 'Profile updated successfully',
                    'user': user.to_dict()
                }), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'Update failed: {str(e)}'}), 500
        
        return _update_profile()
    
    # Framework Library CRUD Operations
    @app.route('/api/framework-library/', methods=['POST'])
    def create_framework_yaml():
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        @jwt_required()
        def _create():
            data = request.get_json()
            
            if not data or 'filename' not in data or 'content' not in data:
                return jsonify({'error': 'Filename and content required'}), 400
            
            filename = data['filename']
            if not filename.endswith('.yaml'):
                filename = f"{filename}.yaml"
            
            base_dir = Path(__file__).resolve().parent
            libraries_dir = base_dir / 'libraries'
            framework_path = libraries_dir / filename
            
            if framework_path.exists():
                return jsonify({'error': 'Framework already exists'}), 400
            
            try:
                with open(framework_path, 'w', encoding='utf-8') as file:
                    yaml.dump(data['content'], file)
                
                return jsonify({
                    'message': 'Framework created successfully',
                    'filename': filename
                }), 201
            except Exception as e:
                return jsonify({'error': f'Creation failed: {str(e)}'}), 500
        
        return _create()
    
    @app.route('/api/framework-library/<filename>', methods=['PUT'])
    def update_framework_yaml(filename):
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        @jwt_required()
        def _update():
            data = request.get_json()
            
            if not data or 'content' not in data:
                return jsonify({'error': 'Content required'}), 400
            
            if not filename.endswith('.yaml'):
                fname = f"{filename}.yaml"
            else:
                fname = filename
            
            base_dir = Path(__file__).resolve().parent
            libraries_dir = base_dir / 'libraries'
            framework_path = libraries_dir / fname
            
            if not framework_path.exists():
                return jsonify({'error': 'Framework not found'}), 404
            
            try:
                with open(framework_path, 'w', encoding='utf-8') as file:
                    yaml.dump(data['content'], file)
                
                return jsonify({
                    'message': 'Framework updated successfully',
                    'filename': fname
                }), 200
            except Exception as e:
                return jsonify({'error': f'Update failed: {str(e)}'}), 500
        
        return _update()
    
    @app.route('/api/framework-library/<filename>', methods=['DELETE'])
    def delete_framework_yaml(filename):
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        @jwt_required()
        def _delete():
            if not filename.endswith('.yaml'):
                fname = f"{filename}.yaml"
            else:
                fname = filename
            
            base_dir = Path(__file__).resolve().parent
            libraries_dir = base_dir / 'libraries'
            framework_path = libraries_dir / fname
            
            if not framework_path.exists():
                return jsonify({'error': 'Framework not found'}), 404
            
            try:
                framework_path.unlink()
                
                return jsonify({
                    'message': 'Framework deleted successfully',
                    'filename': fname
                }), 200
            except Exception as e:
                return jsonify({'error': f'Deletion failed: {str(e)}'}), 500
        
        return _delete()
    
    # Admin Dashboard
    @app.route('/admin/', methods=['GET'])
    def admin_dashboard():
        try:
            base_dir = Path(__file__).resolve().parent
            libraries_dir = base_dir / 'libraries'
            
            framework_count = len(list(libraries_dir.glob('*.yaml'))) if libraries_dir.exists() else 0
            user_count = User.query.count() if User.query else 0
            
            return jsonify({
                'message': 'Admin Dashboard',
                'stats': {
                    'total_frameworks': framework_count,
                    'total_users': user_count,
                    'api_status': 'running'
                },
                'endpoints': {
                    'frameworks': '/api/framework-library/',
                    'users': '/api/users/',
                    'auth': '/api/token/'
                }
            }), 200
        except Exception as e:
            return jsonify({
                'message': 'Admin Dashboard',
                'stats': {
                    'total_frameworks': 0,
                    'total_users': 0,
                    'api_status': 'running'
                },
                'note': 'Limited stats available'
            }), 200
    
    # Register library management routes
    try:
        from app.routes import register_all_routes
        register_all_routes(app)
    except Exception as e:
        print(f"Warning: Failed to register library routes: {e}", file=sys.stderr)
    
    return app


# Create app instance for development and direct imports
app = create_app()