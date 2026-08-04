from app import create_app
from database.db import db
from models.user import User
import bcrypt

def create_user():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='hr@company.com').first()
        if not user:
            hashed = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
            user = User(
                name='HR Admin',
                email='hr@company.com',
                password_hash=hashed.decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            print("✅ User created: hr@company.com / password123")
        else:
            print("✅ User already exists: hr@company.com")

if __name__ == '__main__':
    create_user()