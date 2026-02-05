"""
Vercel serverless WSGI entry point for Flask
"""
import os
import sys

# Ensure parent dir is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import and initialize the real Flask app
try:
    from application import create_app
    app = create_app()
except Exception as e:
    # Fallback minimal app if initialization fails
    import traceback
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    error_info = {
        'error': str(e),
        'type': type(e).__name__,
        'traceback': traceback.format_exc()
    }
    
    # This route will show the error to help debug
    @app.errorhandler(404)
    @app.errorhandler(500)
    def error_handler(e):
        return jsonify({
            'status': 'error',
            'message': 'Application initialization failed',
            'details': error_info
        }), 500
    
    @app.route('/')
    def index():
        return jsonify({
            'status': 'error',
            'message': 'Application initialization failed',
            'details': error_info
        }), 500

# Vercel will call this as the WSGI app
# No need to export as handler—Vercel auto-detects 'app'


