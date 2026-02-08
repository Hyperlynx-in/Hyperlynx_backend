"""Create database tables for library management"""
from application import db, create_app
from app.models import *

app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("✓ Database tables created successfully")
    
    print("\nTables created:")
    print("- stored_libraries")
    print("- loaded_libraries")
    print("- frameworks")
    print("- requirement_nodes")
    print("- reference_controls")
    print("- risk_matrices")
    print("- requirement_mapping_sets")
    print("- requirement_mappings")
    print("- users")
