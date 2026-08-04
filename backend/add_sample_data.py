from app import create_app
from database.db import db
from models.compliance import Compliance
from models.user import User
from datetime import date, timedelta
import bcrypt

def add_sample_data():
    app = create_app()
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if user exists, if not create one
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
        
        # Check if data already exists
        existing = Compliance.query.first()
        if existing:
            print("✅ Sample data already exists!")
            print(f"📊 Total records: {Compliance.query.count()}")
            return
        
        # Add sample compliance data
        today = date.today()
        
        sample_data = [
            {
                'authority': 'EPFO',
                'compliance_name': 'EPF Payment Remittance',
                'category': 'Labour Compliance',
                'valid_date': today + timedelta(days=30),
                'submission_date': today + timedelta(days=25),
                'process_time': '10 Days',
                'frequency': 'Monthly',
                'priority': 'High',
                'status': 'Planned',
                'remarks': 'Monthly EPF payment to be processed'
            },
            {
                'authority': 'ESIC',
                'compliance_name': 'ESIC Payment Remittance',
                'category': 'Labour Compliance',
                'valid_date': today + timedelta(days=15),
                'submission_date': today + timedelta(days=10),
                'process_time': '10 Days',
                'frequency': 'Monthly',
                'priority': 'High',
                'status': 'Ongoing',
                'remarks': 'ESIC payment in process'
            },
            {
                'authority': 'DISH',
                'compliance_name': 'Factory License Renewal',
                'category': 'Factory Compliance',
                'valid_date': today - timedelta(days=5),
                'submission_date': today - timedelta(days=15),
                'process_time': '90 Days',
                'frequency': 'Annual',
                'priority': 'High',
                'status': 'Overdue',
                'remarks': 'URGENT: Factory license expired!'
            },
            {
                'authority': 'RTO',
                'compliance_name': 'Vehicle FC Renewal - Bus TN 66 A 5650',
                'category': 'Vehicle Compliance',
                'valid_date': today + timedelta(days=60),
                'submission_date': today + timedelta(days=45),
                'process_time': '20 Days',
                'frequency': 'Annual',
                'priority': 'Medium',
                'status': 'Planned',
                'remarks': 'Fitness certificate renewal for bus'
            },
            {
                'authority': 'Insurance Company',
                'compliance_name': 'Group Mediclaim Renewal',
                'category': 'Insurance',
                'valid_date': today + timedelta(days=45),
                'submission_date': today + timedelta(days=35),
                'process_time': '20 Days',
                'frequency': 'Annual',
                'priority': 'High',
                'status': 'Planned',
                'remarks': 'Employee group mediclaim policy renewal'
            },
            {
                'authority': 'LPT',
                'compliance_name': 'Staff Salary Processing - Monthly',
                'category': 'HR Activity',
                'valid_date': today + timedelta(days=5),
                'submission_date': today + timedelta(days=3),
                'process_time': '3 Days',
                'frequency': 'Monthly',
                'priority': 'High',
                'status': 'Ongoing',
                'remarks': 'Monthly salary processing for all staff'
            },
            {
                'authority': 'Fire Department',
                'compliance_name': 'Fire License Renewal',
                'category': 'Factory Compliance',
                'valid_date': today + timedelta(days=90),
                'submission_date': today + timedelta(days=75),
                'process_time': '30 Days',
                'frequency': 'Annual',
                'priority': 'High',
                'status': 'Planned',
                'remarks': 'Fire safety license renewal'
            },
            {
                'authority': 'FSSAI',
                'compliance_name': 'FSSAI License Renewal',
                'category': 'Other',
                'valid_date': today + timedelta(days=120),
                'submission_date': today + timedelta(days=100),
                'process_time': '60 Days',
                'frequency': 'Annual',
                'priority': 'Medium',
                'status': 'Planned',
                'remarks': 'Food safety license renewal'
            },
            {
                'authority': 'Panchayat',
                'compliance_name': 'Factory Running License',
                'category': 'Other',
                'valid_date': today + timedelta(days=180),
                'submission_date': today + timedelta(days=160),
                'process_time': '20 Days',
                'frequency': 'Annual',
                'priority': 'Medium',
                'status': 'Planned',
                'remarks': 'Panchayat factory running license'
            },
            {
                'authority': 'Gratuity',
                'compliance_name': 'Gratuity Exemption Renewal - LIC',
                'category': 'Labour Compliance',
                'valid_date': today + timedelta(days=200),
                'submission_date': today + timedelta(days=180),
                'process_time': '20 Days',
                'frequency': 'Annual',
                'priority': 'High',
                'status': 'Planned',
                'remarks': 'Gratuity exemption renewal with LIC'
            }
        ]
        
        for data in sample_data:
            compliance = Compliance(**data)
            db.session.add(compliance)
        
        db.session.commit()
        
        print("=" * 60)
        print("✅ Sample data added successfully!")
        print(f"📊 Added {len(sample_data)} sample compliance records")
        print("=" * 60)
        print("\n📋 Sample Records Added:")
        for i, d in enumerate(sample_data, 1):
            print(f"  {i}. {d['compliance_name']}")
            print(f"     Authority: {d['authority']}")
            print(f"     Due Date: {d['valid_date'].strftime('%d-%m-%Y') if isinstance(d['valid_date'], date) else d['valid_date']}")
            print(f"     Status: {d['status']}")
            print(f"     Priority: {d['priority']}")
            print()
        
        print("✅ User credentials:")
        print("   📧 Email: hr@company.com")
        print("   🔑 Password: password123")
        print("=" * 60)

if __name__ == '__main__':
    add_sample_data()