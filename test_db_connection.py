#!/usr/bin/env python
"""Test Supabase database connection"""
import os
from application import app, db
from app.models.user import User

print("Testing Supabase Connection...\n")

with app.app_context():
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    print(f"Database URI configured: {db_uri[:60]}...")
    
    try:
        # Test connection
        result = db.session.execute(db.text('SELECT version();'))
        version = result.fetchone()[0]
        print(f"✓ Connected to PostgreSQL: {version[:50]}...")
        
        # Check if users table exists
        result = db.session.execute(db.text("SELECT to_regclass('users');"))
        table_exists = result.fetchone()[0]
        
        if table_exists:
            print("✓ Users table exists")
            user_count = User.query.count()
            print(f"✓ Total users: {user_count}")
        else:
            print("⚠ Users table does not exist - run migrations")
            
    except Exception as e:
        print(f"✗ Connection failed: {str(e)[:100]}")
        print("\nCheck your .env file:")
        print("  - SUPABASE_DB_HOST")
        print("  - SUPABASE_DB_USER") 
        print("  - SUPABASE_DB_PASSWORD")
        print("  - SUPABASE_DB_PORT")
