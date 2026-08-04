# ✅ For standalone app.py - import models from app directly
from app import app, db, Compliance

with app.app_context():
    total = Compliance.query.count()
    print(f'📊 Total records in database: {total}')
    
    if total > 0:
        rec = Compliance.query.first()
        print(f'First record: {rec.compliance_name} - {rec.authority} - {rec.status}')
        
        # Show status breakdown
        completed = Compliance.query.filter_by(status='Completed').count()
        ongoing = Compliance.query.filter_by(status='Ongoing').count()
        planned = Compliance.query.filter_by(status='Planned').count()
        overdue = Compliance.query.filter_by(status='Overdue').count()
        
        print(f'\n📊 Status Breakdown:')
        print(f'  Completed: {completed}')
        print(f'  Ongoing: {ongoing}')
        print(f'  Planned: {planned}')
        print(f'  Overdue: {overdue}')
    else:
        print('⚠️ No data found! Please import CSV files.')