#!/usr/bin/env python
"""Test the Flask app directly"""
import traceback
from application import create_app

try:
    print("[*] Creating Flask app...")
    app = create_app()
    print("[✓] Flask app created successfully")
    
    print("[*] Starting Flask server on 0.0.0.0:5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
except Exception as e:
    print(f"[✗] Error starting server: {e}")
    traceback.print_exc()
