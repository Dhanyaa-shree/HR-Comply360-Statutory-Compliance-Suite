from app import app, db
import bcrypt
from models.user import User

def init_database():
    with app.app_context():
        # ✅ Create all tables first
        db.create_all()
        print("✅ Database tables created/verified")
        
        # ✅ Then query the user
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
            print("✅ Default user created: hr@company.com / password123")
        else:
            print("✅ User already exists")

if __name__ == '__main__':
    init_database()