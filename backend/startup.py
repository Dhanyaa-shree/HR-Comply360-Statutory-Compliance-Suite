from app import app, init_db

def init_database():
    # ✅ Use the existing init_db() function from app.py
    init_db()
    print("✅ Database initialization completed")

if __name__ == '__main__':
    init_database()