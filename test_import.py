#!/usr/bin/env python
"""Test app import and initialization"""
from application import create_app

print("Creating app...")
app = create_app()
print("✓ App created successfully")
print(f"✓ Routes registered: {len(app.url_map._rules)}")
print(f"✓ Database URI configured: {bool(app.config.get('SQLALCHEMY_DATABASE_URI'))}")
print("✓ Ready for deployment")
