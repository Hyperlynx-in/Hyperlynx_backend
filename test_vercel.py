#!/usr/bin/env python
"""Test Vercel entry point"""
import sys
sys.path.insert(0, '.')

# Test Vercel entry point
from api.index import app

print(f"✓ App imported from api/index.py")
print(f"✓ App type: {type(app)}")
print(f"✓ Routes: {len(app.url_map._rules)}")

# Test a request
with app.test_client() as client:
    r = client.get('/api/health')
    print(f"✓ GET /api/health: {r.status_code}")
    r = client.get('/')
    print(f"✓ GET /: {r.status_code}")

print("✓ Vercel entry point ready!")
