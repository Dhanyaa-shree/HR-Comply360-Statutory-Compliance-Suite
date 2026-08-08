from app import app, init_db

def init_database():
    # ✅ Use the existing init_db() function from app.py
    init_db()
    print("✅ Database initialization completed")
    
    # ✅ Import data on startup
    try:
        from import_now import import_data
        import_data()
        print("✅ Data import completed on startup")
    except Exception as e:
        print(f"⚠️ Data import failed (this is okay if no CSV exists): {e}")

if __name__ == '__main__':
    init_database()