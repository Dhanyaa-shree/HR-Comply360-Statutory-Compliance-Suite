from app import create_app
from database.db import db
from models.compliance import Compliance
from datetime import date, timedelta
import sqlite3
import os

def migrate_database():
    """Add reminder fields to existing database"""
    app = create_app()
    with app.app_context():
        try:
            # Get database path
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'dev.db')
            
            # Connect to SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if columns already exist
            cursor.execute("PRAGMA table_info(compliance)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Add columns if they don't exist
            if 'reminder_1_date' not in columns:
                cursor.execute("ALTER TABLE compliance ADD COLUMN reminder_1_date DATE")
                print("✅ Added column: reminder_1_date")
            
            if 'reminder_2_date' not in columns:
                cursor.execute("ALTER TABLE compliance ADD COLUMN reminder_2_date DATE")
                print("✅ Added column: reminder_2_date")
            
            if 'reminder_3_date' not in columns:
                cursor.execute("ALTER TABLE compliance ADD COLUMN reminder_3_date DATE")
                print("✅ Added column: reminder_3_date")
            
            if 'reminder_1_sent' not in columns:
                cursor.execute("ALTER TABLE compliance ADD COLUMN reminder_1_sent BOOLEAN DEFAULT 0")
                print("✅ Added column: reminder_1_sent")
            
            if 'reminder_2_sent' not in columns:
                cursor.execute("ALTER TABLE compliance ADD COLUMN reminder_2_sent BOOLEAN DEFAULT 0")
                print("✅ Added column: reminder_2_sent")
            
            if 'reminder_3_sent' not in columns:
                cursor.execute("ALTER TABLE compliance ADD COLUMN reminder_3_sent BOOLEAN DEFAULT 0")
                print("✅ Added column: reminder_3_sent")
            
            conn.commit()
            print("✅ Migration completed successfully!")
            
            # Update existing records with default values
            compliance_list = Compliance.query.filter(
                Compliance.status != 'Completed'
            ).all()
            
            updated_count = 0
            for compliance in compliance_list:
                if compliance.valid_date:
                    if not compliance.reminder_1_date:
                        compliance.reminder_1_date = compliance.valid_date - timedelta(days=30)
                    compliance.reminder_2_date = compliance.valid_date - timedelta(days=5)
                    compliance.reminder_3_date = compliance.valid_date - timedelta(days=2)
                    updated_count += 1
            
            db.session.commit()
            print(f"✅ Updated {updated_count} existing records with reminder dates")
            
        except Exception as e:
            print(f"❌ Migration error: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_database()