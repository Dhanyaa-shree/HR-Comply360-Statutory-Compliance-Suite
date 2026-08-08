# backend/import_now.py
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================
# ENVIRONMENT DETECTION
# ============================================
if os.path.exists('/opt/render'):
    print("🔗 Connected to Render database")
else:
    print("🔗 Connected to Local database")

from app import app, db, User, Compliance
import pandas as pd
from datetime import datetime, timedelta, date
import bcrypt
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================
DEFAULT_CSV_FILE = 'LPT Statutory Checklist 2026.csv'
DEFAULT_USER_EMAIL = 'hr@company.com'
DEFAULT_USER_PASSWORD = 'password123'
DEFAULT_USER_NAME = 'HR Admin'

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
CHECKMARKS = ['✓', '✔', '☑', '⃝', '●', '•', '✅', '?', '1', 'Yes', 'yes', 'YES']

HIGH_PRIORITY_KEYWORDS = [
    'EPF', 'ESIC', 'Factory', 'Fire', 'Salary', 'Bonus', 
    'Gratuity', 'Insurance', 'RTO', 'License', 'FSSAI', 
    'Critical', 'Urgent', 'POSH'
]

CATEGORY_KEYWORDS = {
    'Labour Compliance': ['EPFO', 'ESIC', 'Gratuity', 'DISH', 'Labour', 'Factory Act'],
    'Insurance': ['Insurance', 'Mediclaim', 'Policy'],
    'Vehicle Compliance': ['RTO', 'TAX', 'FC', 'Permit', 'Vehicle', 'Motor'],
    'Factory Compliance': ['Factory', 'License', 'Fire', 'Industrial'],
    'HR Activity': ['LPT', 'Salary', 'Wage', 'Training', 'Recruitment', 'Bonus', 'Encashment'],
    'Food Safety': ['FSSAI', 'Food'],
    'HR Compliance': ['POSH', 'Sexual Harassment']
}

# ============================================
# UTILITY FUNCTIONS
# ============================================

def parse_date(date_value):
    """Parse date from various formats"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, pd.Timestamp):
        return date_value.date()
    
    date_str = str(date_value).strip()
    if not date_str or date_str.lower() in ['nan', 'na', 'none', '']:
        return None
    
    # Special cases
    special_cases = {
        'every month': datetime.now().date(),
        'monthly': datetime.now().date(),
        'diwali': datetime.now().date(),
        'quarter': datetime.now().date(),
        'annual': datetime.now().date(),
    }
    
    for key, value in special_cases.items():
        if key in date_str.lower():
            return value
    
    # Extract date from text
    date_match = re.search(r'(\d{1,2})[\.\-/](\d{1,2})[\.\-/](\d{2,4})', date_str)
    if date_match:
        day, month, year = date_match.groups()
        if len(year) == 2:
            year = f"20{year}"
        try:
            return datetime(int(year), int(month), int(day)).date()
        except ValueError:
            pass
    
    # Try various formats
    formats = [
        '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y',
        '%d-%b-%Y', '%d/%b/%Y', '%d.%b.%Y',
        '%b %d, %Y', '%d-%m-%y', '%d/%m/%y', '%d.%m.%y',
        '%b %d %Y', '%d %b %Y'
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.date()
        except ValueError:
            continue
    
    return None

def clean_authority(authority):
    """Clean and simplify authority name"""
    if not authority or authority == 'nan':
        return 'Unknown'
    
    # Remove extra whitespace
    authority = ' '.join(str(authority).split())
    
    # Extract known authorities
    known_authorities = ['EPFO', 'ESIC', 'DISH', 'LPT', 'Gratuity', 'Panchayat', 
                         'Insurance', 'RTO', 'FSSAI', 'POSH', 'Factory', 'Fire']
    
    for keyword in known_authorities:
        if keyword.lower() in authority.lower():
            return keyword
    
    if len(authority) > 30:
        return 'Other'
    
    return authority

def determine_status(row):
    """Determine compliance status from month columns"""
    checked = 0
    total_months = 0
    
    for month in MONTHS:
        # Try different column name variations
        for col_name in [month, f"{month}'26", f"{month} 26", f"{month} 27"]:
            if col_name in row.index:
                value = str(row.get(col_name, '')).strip()
                if value and value not in ['nan', '']:
                    total_months += 1
                    if value in CHECKMARKS:
                        checked += 1
                break
    
    if total_months == 0:
        return 'Planned'
    
    completion_ratio = checked / total_months
    
    if completion_ratio >= 0.95:
        return 'Completed'
    elif completion_ratio >= 0.3:
        return 'Ongoing'
    else:
        return 'Planned'

def determine_priority(name, authority):
    """Determine priority based on keywords"""
    text = f"{name} {authority}".lower()
    
    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword.lower() in text:
            return 'High'
    
    return 'Medium'

def determine_category(authority, name):
    """Determine category based on keywords"""
    text = f"{authority} {name}".lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return category
    
    return 'Other'

def determine_frequency(valid_up_to, name):
    """Determine frequency based on text"""
    valid_text = str(valid_up_to).lower() if pd.notna(valid_up_to) else ''
    name_text = str(name).lower()
    
    if 'every month' in valid_text or 'monthly' in valid_text:
        return 'Monthly'
    elif 'quarter' in valid_text or 'quarterly' in valid_text:
        return 'Quarterly'
    elif 'annual' in valid_text or 'yearly' in valid_text or 'annual' in name_text:
        return 'Yearly'
    elif 'half-yearly' in valid_text or 'semi-annual' in valid_text:
        return 'Half-Yearly'
    
    return 'OneTime'

def find_file(filename):
    """Find file in multiple locations (Local and Render)"""
    # ✅ Updated paths for both Local and Render
    locations = [
        filename,
        f'uploads/{filename}',
        f'../{filename}',
        f'../uploads/{filename}',
        f'/opt/render/project/src/backend/uploads/{filename}',
        f'/opt/render/project/src/backend/{filename}',
        f'/opt/render/project/src/uploads/{filename}',
        # ✅ Add absolute path for current directory
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
    ]
    
    # Remove duplicates
    locations = list(dict.fromkeys(locations))
    
    for location in locations:
        if os.path.exists(location):
            print(f"✅ Found file at: {location}")
            return location
    
    print(f"❌ File not found: {filename}")
    print(f"📁 Tried locations:")
    for loc in locations:
        print(f"   - {loc}")
    return None

# ============================================
# MAIN IMPORT FUNCTION
# ============================================

def import_data(csv_file=None, user_email=None, clear_existing=True, verbose=True):
    """
    Import compliance data from CSV
    
    Args:
        csv_file: Path to CSV file (default: LPT Statutory Checklist 2026.csv)
        user_email: User email for ownership (default: hr@company.com)
        clear_existing: Clear existing data (default: True)
        verbose: Show detailed output (default: True)
    """
    with app.app_context():
        print("\n" + "=" * 70)
        print("📊 HR-Comply360 Data Import")
        print("=" * 70)
        
        # Find CSV file
        csv_file = csv_file or DEFAULT_CSV_FILE
        file_path = find_file(csv_file)
        
        if not file_path:
            print(f"❌ File not found: {csv_file}")
            return False
        
        print(f"📁 File found: {file_path}")
        
        # Get or create user
        user_email = user_email or DEFAULT_USER_EMAIL
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            print(f"👤 Creating user: {user_email}")
            hashed = bcrypt.hashpw(DEFAULT_USER_PASSWORD.encode('utf-8'), bcrypt.gensalt())
            user = User(
                name=DEFAULT_USER_NAME,
                email=user_email,
                password_hash=hashed.decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            print(f"✅ User created: {user_email} / {DEFAULT_USER_PASSWORD}")
        else:
            print(f"✅ User already exists: {user.email}")
        
        # Clear existing data if requested
        if clear_existing:
            count_before = Compliance.query.count()
            if count_before > 0:
                Compliance.query.delete()
                db.session.commit()
                print(f"🗑️ Cleared {count_before} existing records")
            else:
                print("📭 No existing data to clear")
        
        # Read CSV
        print(f"\n📊 Importing {os.path.basename(file_path)}...")
        
        try:
            # Try different header rows
            df = None
            for header_row in range(0, 5):
                try:
                    df = pd.read_csv(file_path, header=header_row)
                    # Check if this looks like a valid header
                    if 'Statutory Compliance' in df.columns or 'Authority' in df.columns:
                        print(f"✅ Found header at row {header_row}")
                        break
                except Exception as e:
                    continue
            
            if df is None:
                # Fallback: read with default header
                df = pd.read_csv(file_path, header=0)
                print("⚠️ Using first row as header")
                
        except Exception as e:
            print(f"❌ Error reading CSV: {str(e)}")
            return False
        
        print(f"📝 Rows: {len(df)}")
        print(f"📋 Columns: {df.columns.tolist()}")
        
        count = 0
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                # Get compliance name (required)
                name = str(row.get('Statutory Compliance', '')).strip()
                if not name or name.lower() in ['nan', '']:
                    continue
                
                # Skip summary rows
                if name.upper() in ['PLANNED', 'COMPLETED', 'NOT COMPLETED']:
                    continue
                
                # Get authority
                authority = str(row.get('Authority', '')).strip()
                if authority.lower() in ['nan', '']:
                    authority = 'Unknown'
                
                # Clean authority
                authority = clean_authority(authority)
                
                # Parse valid date
                valid_date = datetime.now().date()
                valid_up_to = row.get('Valid up to', row.get('Valid Up To', ''))
                if pd.notna(valid_up_to):
                    parsed = parse_date(valid_up_to)
                    if parsed:
                        valid_date = parsed
                
                if not valid_date:
                    due_date = row.get('Due Date', '')
                    if pd.notna(due_date):
                        parsed = parse_date(due_date)
                        if parsed:
                            valid_date = parsed
                
                # Parse submission date
                submission_date = None
                sub_date = row.get('Submission Date', '')
                if pd.notna(sub_date):
                    parsed = parse_date(sub_date)
                    if parsed:
                        submission_date = parsed
                
                # Get process time
                process_time = None
                pt = row.get('Process Time', '')
                if pd.notna(pt) and str(pt).strip() not in ['nan', '']:
                    process_time = str(pt).strip()
                
                # Determine fields
                status = determine_status(row)
                priority = determine_priority(name, authority)
                category = determine_category(authority, name)
                frequency = determine_frequency(valid_up_to, name)
                
                # Create compliance with reminder dates
                reminder_1_date = valid_date - timedelta(days=30)
                reminder_2_date = valid_date - timedelta(days=5)
                reminder_3_date = valid_date - timedelta(days=2)
                
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
                    remarks=f'Imported from {os.path.basename(file_path)}',
                    reminder_1_date=reminder_1_date,
                    reminder_2_date=reminder_2_date,
                    reminder_3_date=reminder_3_date,
                    reminder_1_sent=False,
                    reminder_2_sent=False,
                    reminder_3_sent=False
                )
                db.session.add(compliance)
                count += 1
                
                if verbose and count % 10 == 0:
                    print(f"✅ Imported {count} records...")
                
            except Exception as e:
                errors += 1
                print(f"❌ Row {idx+2}: {str(e)}")
                continue
        
        db.session.commit()
        
        print("\n" + "=" * 70)
        print(f"✅ IMPORT COMPLETE!")
        print(f"📊 Records Imported: {count}")
        print(f"❌ Errors: {errors}")
        print("=" * 70)
        
        return True

# ============================================
# RUN
# ============================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Import compliance data from CSV')
    parser.add_argument('--file', '-f', help='CSV file path')
    parser.add_argument('--user', '-u', help='User email')
    parser.add_argument('--append', '-a', action='store_true', help='Append data (don\'t clear existing)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    import_data(
        csv_file=args.file,
        user_email=args.user,
        clear_existing=not args.append,
        verbose=args.verbose
    )