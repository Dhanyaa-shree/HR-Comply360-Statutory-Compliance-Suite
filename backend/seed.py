from app import create_app
from database.db import db
from models.user import User
import bcrypt

def seed():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if user exists
        user = User.query.filter_by(email='hr@company.com').first()
        
        if not user:
            # Create default user
            hashed = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
            user = User(
                name='HR Admin',
                email='hr@company.com',
                password_hash=hashed.decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            print("✅ Default user created!")
            print("📧 Email: hr@company.com")
            print("🔑 Password: password123")
        else:
            print("✅ User already exists!")
            print(f"📧 Email: {user.email}")
            print(f"👤 Name: {user.name}")

if __name__ == '__main__':
    seed()