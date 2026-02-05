"""
Vercel serverless function entry point for Flask app
"""
import os
import sys

# Add parent directory to path so we can import application
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from application import app as app
except Exception as e:
    import traceback
    from flask import Flask, jsonify

    app = Flask(__name__)
    error_details = {
        'error': str(e),
        'traceback': traceback.format_exc().split('\n')
    }

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            'status': 'error',
            'message': 'Application failed to initialize',
            'details': error_details,
            'path': path
        }), 500

