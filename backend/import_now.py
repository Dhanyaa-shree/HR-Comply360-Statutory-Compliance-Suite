import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Compliance
import pandas as pd
from datetime import datetime
import bcrypt
import re

def parse_date(date_value):
    if pd.isna(date_value):
        return None
    if isinstance(date_value, pd.Timestamp):
        return date_value.date()
    
    date_str = str(date_value).strip()
    if not date_str or date_str == 'nan' or date_str == 'NA':
        return None
    
    if 'Every Month' in date_str or 'every month' in date_str.lower():
        return datetime.now().date()
    if 'Diwali' in date_str:
        return datetime.now().date()
    if 'Quarter' in date_str:
        return datetime.now().date()
    
    formats = [
        '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y',
        '%d-%b-%Y', '%d/%b/%Y', '%d.%b.%Y', '%b %d, %Y',
        '%d-%m-%y', '%d/%m/%y', '%d.%m.%y'
    ]
    
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

def import_data():
    with app.app_context():
        print("=" * 60)
        print("📊 Starting Import - LPT Statutory Checklist 2026")
        print("=" * 60)
        
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
        existing_count = Compliance.query.count()
        if existing_count > 0:
            Compliance.query.delete()
            db.session.commit()
            print(f"🗑️ Cleared {existing_count} existing records")
        else:
            print("📭 No existing data to clear")
        
        # Find file
        file_path = 'uploads/LPT Statutory Checklist 2026.csv'
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        
        print(f"\n📁 File found: {file_path}")
        
        # ✅ FIX: Read CSV - row 3 (index 2) is the header
        df = pd.read_csv(file_path, header=2)
        
        print(f"📝 Total rows in CSV: {len(df)}")
        
        # Show actual column names
        cols = df.columns.tolist()
        print(f"📋 Columns found: {cols[:5]}...")  # Show first 5 columns
        
        count = 0
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                # Skip empty rows
                name = str(row.get('Statutory Compliance', '')).strip()
                if not name or name == 'nan' or name == '':
                    continue
                
                if name in ['PLANNED', 'COMPLETED', 'NOT COMPLETED']:
                    continue
                
                # Get authority
                authority = str(row.get('Authority', '')).strip()
                if authority == 'nan' or authority == '':
                    authority = 'Unknown'
                
                # Clean multi-line authority
                authority = ' '.join(authority.split())
                if len(authority) > 30:
                    for keyword in ['EPFO', 'ESIC', 'DISH', 'LPT', 'Gratuity', 'Panchayat', 'Insurance', 'RTO', 'FSSAI', 'POSH']:
                        if keyword in authority:
                            authority = keyword
                            break
                
                print(f"✅ Row {idx+2}: {name} - {authority}")
                
                # Valid date
                valid_date = datetime.now().date()
                valid_up_to = row.get('Valid up to ', '')
                if pd.notna(valid_up_to) and str(valid_up_to).strip():
                    parsed = parse_date(valid_up_to)
                    if parsed:
                        valid_date = parsed
                
                # Submission date
                submission_date = None
                sub_date = row.get('Submission Date', '')
                if pd.notna(sub_date) and str(sub_date).strip():
                    parsed = parse_date(sub_date)
                    if parsed:
                        submission_date = parsed
                
                # Process time
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
                    for col_name in [month, f"{month}'26", f"{month} 26"]:
                        if col_name in cols:
                            value = str(row.get(col_name, '')).strip()
                            if value and value != 'nan':
                                total_months += 1
                                if value in ['✓', '✔', '☑', '⃝', '●', '•', '✅', '?']:
                                    checked += 1
                                break
                
                if total_months > 0 and checked >= total_months:
                    status = 'Completed'
                elif checked > 0:
                    status = 'Ongoing'
                
                # Frequency
                frequency = 'OneTime'
                valid_text = str(valid_up_to).lower() if pd.notna(valid_up_to) else ''
                if 'every month' in valid_text or 'monthly' in valid_text:
                    frequency = 'Monthly'
                elif 'quarter' in valid_text:
                    frequency = 'Quarterly'
                elif 'annual' in valid_text or 'renewal' in name.lower():
                    frequency = 'Annual'
                
                # Priority
                priority = 'Medium'
                high_keywords = ['EPF', 'ESIC', 'Factory', 'Fire', 'Salary', 'Bonus', 'Gratuity', 'Insurance', 'RTO', 'License', 'FSSAI']
                for keyword in high_keywords:
                    if keyword.lower() in name.lower() or keyword.lower() in authority.lower():
                        priority = 'High'
                        break
                
                # Category
                category = 'Other'
                if any(x in authority for x in ['EPFO', 'ESIC', 'Gratuity', 'DISH']):
                    category = 'Labour Compliance'
                elif 'Insurance' in authority:
                    category = 'Insurance'
                elif any(x in authority for x in ['RTO', 'TAX']) or 'FC' in name or 'PERMIT' in name:
                    category = 'Vehicle Compliance'
                elif 'Factory' in name or 'License' in name or 'Fire' in name:
                    category = 'Factory Compliance'
                elif 'LPT' in authority or name in ['Staff / Trainee Salary', 'Workers / Contract Wage', 'Leave Encashment', 'Variable Pay', 'Bonus']:
                    category = 'HR Activity'
                elif 'FSSAI' in authority:
                    category = 'Food Safety'
                elif 'POSH' in name:
                    category = 'HR Compliance'
                
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
                    remarks='Imported from LPT Statutory Checklist 2026.csv'
                )
                db.session.add(compliance)
                count += 1
                
                if count % 10 == 0:
                    print(f"✅ Imported {count} records...")
                
            except Exception as e:
                errors += 1
                print(f"❌ Row {idx+2}: {str(e)}")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ IMPORT COMPLETE!")
        print(f"📊 Records Imported: {count}")
        print(f"❌ Errors: {errors}")
        print("=" * 60)

if __name__ == '__main__':
    import_data()