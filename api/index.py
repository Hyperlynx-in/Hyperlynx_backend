"""
Vercel serverless function entry point
"""
import sys
import traceback

try:
    # Try to import the application
    from application import app
    print("✓ Successfully imported Flask app", file=sys.stderr)
except Exception as e:
    print(f"✗ Failed to import application: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    
    # Create a minimal fallback Flask app to show the error
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    error_msg = str(e)
    error_trace = traceback.format_exc()
    
    @app.route('/')
    @app.route('/<path:path>')
    def show_error(path=''):
        return jsonify({
            'error': 'Failed to initialize application',
            'message': error_msg,
            'traceback': error_trace.split('\n'),
            'path': path
        }), 500

# Export for Vercel
app = app

