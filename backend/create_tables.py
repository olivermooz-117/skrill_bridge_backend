
import os
import sys
from app import create_app
from app.extensions import db
from app.models import User, Gig, Order, Review, Tag

def create_tables():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        print("📊 Creating database tables...")
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables created: {tables}")
        
        # Check if any users exist
        if not User.query.first():
            print("👤 No users found. You may want to create a test user.")
        else:
            user_count = User.query.count()
            print(f"👥 Existing users: {user_count}")

if __name__ == "__main__":
    create_tables()