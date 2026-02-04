#!/usr/bin/env python
"""Quick test of Flask app"""
import sys
import time

print("[*] Importing Flask app...")
try:
    from application import app
    print("[✓] Flask app imported successfully")
except Exception as e:
    print(f"[✗] Failed to import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# List routes
print(f"\n[*] Routes registered: {len(app.url_map._rules)}")
for i, rule in enumerate(list(app.url_map._rules)[:10]):
    print(f"  {i+1}. {rule}")

# Test with test client
print("\n[*] Testing with Flask test client...")
with app.test_client() as client:
    try:
        response = client.get('/api/health')
        print(f"[✓] GET /api/health: {response.status_code}")
        print(f"    Response: {response.get_json()}")
    except Exception as e:
        print(f"[✗] Test failed: {e}")
        import traceback
        traceback.print_exc()

# Now try running the server
print("\n[*] Starting Flask server...")
print("[*] The server is running! Connect to http://localhost:5000/docs for Swagger UI")
print("[*] Try endpoints like:")
print("  - GET  http://localhost:5000/api/health")
print("  - GET  http://localhost:5000/api/framework-library")
print("  - POST http://localhost:5000/api/users/register/")
print()

app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)
