"""
Vercel serverless WSGI entry point
Minimal Flask app for Vercel serverless—no heavy imports at module level
"""
import os
import sys
from flask import Flask, jsonify

# Ensure parent dir is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# Store initialization errors for debugging
init_error = None

def init_app_lazy():
    """Initialize the real app on first request"""
    global init_error
    if init_error is not None:
        return None
    
    try:
        from application import create_app
        return create_app()
    except Exception as e:
        import traceback
        init_error = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return None

# Lazy load the real app on first request
_real_app = None

@app.before_request
def lazy_load():
    global _real_app
    if _real_app is None:
        _real_app = init_app_lazy()
        if _real_app is None and init_error:
            return jsonify({
                'status': 'error',
                'message': 'Failed to initialize application',
                'error': init_error['error']
            }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def catch_all(path):
    """Forward all requests to the real app"""
    global _real_app
    if _real_app is None:
        _real_app = init_app_lazy()
    
    if _real_app is None:
        return jsonify({
            'status': 'error',
            'message': 'Application initialization failed',
            'details': init_error
        }), 500
    
    # Forward to real app
    return _real_app.dispatch_request(path or '/')

# Export for Vercel
app = app

