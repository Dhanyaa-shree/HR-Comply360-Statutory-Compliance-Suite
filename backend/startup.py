from app import app, init_db

def init_database():
    with app.app_context():
        # ✅ Force create ALL tables
        from app import db
        db.create_all()
        print("✅ Database tables created/verified")
        
        # ✅ Initialize user
        init_db()
        print("✅ Database initialization completed")
        
        # ✅ Import data
        try:
            from import_now import import_data
            import_data()
            print("✅ Data import completed on startup")
        except Exception as e:
            print(f"⚠️ Data import failed: {e}")

if __name__ == '__main__':
    init_database()