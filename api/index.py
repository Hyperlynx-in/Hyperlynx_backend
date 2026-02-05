"""
Vercel serverless function entry point for Flask app
"""
import sys
import os

# Add parent directory to path so we can import application
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from application import app
    
    # Vercel expects the Flask app to be named 'app'
    # This handles all routes
    def handler(environ, start_response):
        return app(environ, start_response)
    
except Exception as e:
    import traceback
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    error_details = {
        'error': str(e),
        'traceback': traceback.format_exc()
    }
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            'status': 'error',
            'message': 'Application failed to initialize',
            'details': error_details
        }), 500

