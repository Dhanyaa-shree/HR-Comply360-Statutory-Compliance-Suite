from app import app  # ✅ Changed from create_app
from database.db import db
from models.compliance import Compliance
from models.user import User
import pandas as pd
import os
from datetime import datetime
import bcrypt
import re

def parse_date(date_value):
    """Parse date from various formats"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, pd.Timestamp):
        return date_value.date()
    
    date_str = str(date_value).strip()
    if not date_str or date_str == 'nan' or date_str == 'NA':
        return None
    
    # Handle special cases
    if 'Every Month' in date_str or 'every month' in date_str.lower():
        return datetime.now().date()
    
    if 'Diwali' in date_str:
        return datetime.now().date()
    
    if 'Quarter' in date_str:
        return datetime.now().date()
    
    # Try different formats
    formats = [
        '%d-%m-%Y',    # 31-12-2026
        '%d/%m/%Y',    # 31/12/2026
        '%Y-%m-%d',    # 2026-12-31
        '%d.%m.%Y',    # 31.12.2026
        '%d-%b-%Y',    # 31-Dec-2026
        '%d/%b/%Y',    # 31/Dec/2026
        '%d.%b.%Y',    # 31.Dec.2026
        '%b %d, %Y',   # Dec 31, 2026
        '%d-%m-%y',    # 31-12-26
        '%d/%m/%y',    # 31/12/26
        '%d.%m.%y',    # 31.12.26
    ]
    
    # Try to extract date from text
    date_match = re.search(r'(\d{1,2})[\.\-/](\d{1,2})[\.\-/](\d{4})', date_str)
    if date_match:
        day, month, year = date_match.groups()
        return datetime(int(year), int(month), int(day)).date()
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.date()
        except ValueError:
            continue
    
    return None

def import_2026_data():
    # ✅ Use app directly (not create_app)
    with app.app_context():
        # Create user if not exists
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
            print("✅ User created")
        else:
            print("✅ User already exists")
        
        # Clear existing data
        count_before = Compliance.query.count()
        if count_before > 0:
            Compliance.query.delete()
            db.session.commit()
            print(f"🗑️ Cleared {count_before} existing records")
        else:
            print("📭 No existing data to clear")
        
        # Import ONLY 2026 file
        csv_file = 'LPT Statutory Checklist 2026.csv'
        file_path = os.path.join('uploads', csv_file)
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            print(f"📁 Current directory: {os.getcwd()}")
            print(f"📁 Looking for: {os.path.abspath(file_path)}")
            return
        
        print(f"\n📊 Importing {csv_file}...")
        
        # Read CSV - skip first 3 rows, keep first 19 columns
        df = pd.read_csv(file_path, skiprows=3).iloc[:, :19]
        
        # Rename columns
        df.columns = ['S.No', 'Authority', 'Statutory Compliance', 'As Per ACT', 'Valid up to', 
                      'Process Time', 'Submission Date', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 
                      'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        print(f"📝 Rows: {len(df)}")
        print(f"📋 Columns: {df.columns.tolist()}")
        
        count = 0
        for idx, row in df.iterrows():
            try:
                # Skip empty rows
                name = str(row.get('Statutory Compliance', '')).strip()
                if not name or name == 'nan' or name == '':
                    continue
                
                # Skip summary rows
                if name in ['PLANNED', 'COMPLETED', 'NOT COMPLETED']:
                    continue
                
                # Get authority
                authority = str(row.get('Authority', '')).strip()
                if authority == 'nan' or authority == '':
                    authority = 'Unknown'
                
                # Get valid date
                valid_date = datetime.now().date()
                valid_up_to = row.get('Valid up to', '')
                if pd.notna(valid_up_to):
                    parsed = parse_date(valid_up_to)
                    if parsed:
                        valid_date = parsed
                
                # Get submission date
                submission_date = None
                sub_date = row.get('Submission Date', '')
                if pd.notna(sub_date):
                    parsed = parse_date(sub_date)
                    if parsed:
                        submission_date = parsed
                
                # Get process time
                process_time = None
                pt = row.get('Process Time', '')
                if pd.notna(pt) and str(pt).strip() != 'nan':
                    process_time = str(pt).strip()
                
                # Determine status from month columns
                status = 'Planned'
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                checked = 0
                total_months = 0
                
                for month in months:
                    value = str(row.get(month, '')).strip()
                    if value and value != 'nan':
                        total_months += 1
                        if value in ['✓', '✔', '☑', '⃝', '●', '•', '✅', '?']:
                            checked += 1
                
                if total_months > 0 and checked >= total_months:
                    status = 'Completed'
                elif checked > 0:
                    status = 'Ongoing'
                
                # Determine frequency
                frequency = 'OneTime'
                valid_text = str(valid_up_to).lower() if pd.notna(valid_up_to) else ''
                if 'every month' in valid_text or 'monthly' in valid_text:
                    frequency = 'Monthly'
                elif 'quarter' in valid_text:
                    frequency = 'Quarterly'
                elif 'annual' in valid_text or 'renewal' in name.lower():
                    frequency = 'Annual'
                
                # Determine priority
                priority = 'Medium'
                high_keywords = ['EPF', 'ESIC', 'Factory', 'Fire', 'Salary', 'Bonus', 'Gratuity', 'Insurance']
                for keyword in high_keywords:
                    if keyword.lower() in name.lower():
                        priority = 'High'
                        break
                
                # Determine category
                category = 'Other'
                if any(x in authority for x in ['EPFO', 'ESIC', 'Gratuity', 'DISH']):
                    category = 'Labour Compliance'
                elif 'Insurance' in authority:
                    category = 'Insurance'
                elif any(x in authority for x in ['RTO', 'TAX']):
                    category = 'Vehicle Compliance'
                elif 'Factory' in name or 'License' in name:
                    category = 'Factory Compliance'
                elif 'LPT' in authority or name in ['Staff / Trainee Salary', 'Workers / Contract Wage', 'Leave Encashment']:
                    category = 'HR Activity'
                
                # Create compliance
                compliance = Compliance(
                    authority=authority,
                    compliance_name=name,
                    category=category,
                    valid_date=valid_date,
                    submission_date=submission_date,
                    process_time=process_time,
                    frequency=frequency,
                    priority=priority,
                    status=status,
                    updated_by=str(user.id),
                    remarks=f'Imported from {csv_file}'
                )
                db.session.add(compliance)
                count += 1
                
                if count % 10 == 0:
                    print(f"✅ Imported {count} records...")
                
            except Exception as e:
                print(f"❌ Row {idx+2}: {str(e)}")
        
        db.session.commit()
        print(f"\n✅ Imported {count} records from {csv_file}")
        print(f"\n📊 TOTAL: {count} records imported!")

if __name__ == '__main__':
    import_2026_data()