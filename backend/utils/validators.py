import pandas as pd
from datetime import datetime
import re

def parse_date(date_value):
    """Parse date from various formats"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, pd.Timestamp):
        return date_value.strftime('%Y-%m-%d')
    
    date_str = str(date_value).strip()
    if not date_str or date_str == 'nan' or date_str == 'NA':
        return None
    
    # Handle special cases
    if 'Every Month' in date_str or 'every month' in date_str.lower():
        return datetime.now().strftime('%Y-%m-%d')
    
    if 'Diwali' in date_str:
        return datetime.now().strftime('%Y-%m-%d')
    
    if 'Quarter' in date_str:
        return datetime.now().strftime('%Y-%m-%d')
    
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
        return f"{int(year)}-{int(month):02d}-{int(day):02d}"
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return None

def get_status_from_row(row):
    """Determine status from month columns"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    checked_count = 0
    total_months = 0
    
    for col in row.index:
        col_str = str(col)
        for month in months:
            if month in col_str:
                total_months += 1
                value = str(row[col]).strip()
                if value in ['✓', '✔', '☑', '⃝', '●', '•', '✅', '?']:
                    checked_count += 1
                break
    
    if checked_count == 0:
        return 'Planned'
    elif checked_count >= total_months and total_months > 0:
        return 'Completed'
    elif checked_count > 0:
        return 'Ongoing'
    return 'Planned'

def read_excel_file(file_path):
    """Read Excel or CSV file and return records"""
    try:
        # Support both Excel and CSV
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            print(f"📊 CSV loaded: {len(df)} rows")
        else:
            df = pd.read_excel(file_path, sheet_name=0)
            print(f"📊 Excel loaded: {len(df)} rows")
        
        records = []
        errors = []
        
        print(f"📋 Columns: {df.columns.tolist()}")
        
        for idx, row in df.iterrows():
            try:
                # Skip empty rows
                compliance_name = str(row.get('Statutory Compliance', '')).strip()
                if pd.isna(compliance_name) or compliance_name == 'nan' or compliance_name == '':
                    continue
                
                # Skip summary rows
                if compliance_name in ['PLANNED', 'COMPLETED', 'NOT COMPLETED']:
                    continue
                
                authority = str(row.get('Authority', '')).strip()
                if pd.isna(authority) or authority == 'nan':
                    authority = 'Unknown'
                
                # Parse valid date
                valid_date = None
                valid_up_to = row.get('Valid up to', row.get('Valid Up To', ''))
                if pd.notna(valid_up_to):
                    valid_date_str = parse_date(valid_up_to)
                    if valid_date_str:
                        valid_date = valid_date_str
                
                if not valid_date:
                    due_date = row.get('Due Date', '')
                    if pd.notna(due_date):
                        valid_date_str = parse_date(due_date)
                        if valid_date_str:
                            valid_date = valid_date_str
                
                if not valid_date:
                    valid_date = datetime.now().strftime('%Y-%m-%d')
                    errors.append(f"Row {idx+2}: No valid date found, using today")
                
                # Parse submission date
                submission_date = None
                submission = row.get('Submission Date', '')
                if pd.notna(submission):
                    sub_date_str = parse_date(submission)
                    if sub_date_str:
                        submission_date = sub_date_str
                
                # Parse process time
                process_time = None
                if 'Process Time' in df.columns:
                    pt = row.get('Process Time', '')
                    if pd.notna(pt) and str(pt).strip() != 'nan':
                        process_time = str(pt).strip()
                
                # Determine frequency
                frequency = 'OneTime'
                valid_text = str(valid_up_to).lower() if pd.notna(valid_up_to) else ''
                if 'every month' in valid_text or 'monthly' in valid_text:
                    frequency = 'Monthly'
                elif 'quarter' in valid_text:
                    frequency = 'Quarterly'
                elif 'annual' in valid_text or 'renewal' in str(compliance_name).lower():
                    frequency = 'Annual'
                
                # Determine status
                status = get_status_from_row(row)
                
                # Determine priority
                priority = 'Medium'
                high_priority = ['EPF', 'ESIC', 'Factory', 'Fire', 'Salary', 'Bonus', 'Gratuity', 'Insurance']
                for keyword in high_priority:
                    if keyword.lower() in compliance_name.lower() or keyword.lower() in authority.lower():
                        priority = 'High'
                        break
                
                # Determine category
                category = 'Other'
                if any(x in authority for x in ['EPFO', 'ESIC', 'Gratuity', 'DISH']):
                    category = 'Labour Compliance'
                elif 'Insurance' in authority or 'Mediclaim' in authority:
                    category = 'Insurance'
                elif any(x in authority for x in ['RTO', 'Tax', 'FC']):
                    category = 'Vehicle Compliance'
                elif 'Factory' in compliance_name or 'License' in compliance_name:
                    category = 'Factory Compliance'
                elif 'LPT' in authority or compliance_name in ['Staff / Trainee Salary', 'Workers / Contract Wage', 'Leave Encashment']:
                    category = 'HR Activity'
                
                record = {
                    'authority': authority,
                    'compliance_name': compliance_name,
                    'category': category,
                    'valid_date': valid_date,
                    'submission_date': submission_date,
                    'process_time': process_time,
                    'frequency': frequency,
                    'priority': priority,
                    'status': status,
                    'row': idx + 2
                }
                
                records.append(record)
                
            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")
                print(f"❌ Row {idx+2}: {str(e)}")
        
        print(f"✅ Found {len(records)} valid records, {len(errors)} errors")
        return records, errors
        
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return [], [str(e)]