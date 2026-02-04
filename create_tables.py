"""Script to create database tables"""
from application import app, db
from app.models.user import User

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
        print('✓ Users table created successfully')
        print(f'✓ Database: {app.config["SQLALCHEMY_DATABASE_URI"].split("@")[1]}')
