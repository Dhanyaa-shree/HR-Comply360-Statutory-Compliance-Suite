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
    
    formats = [
        '%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y',
        '%d-%b-%Y', '%d/%b/%Y', '%d.%b.%Y'
    ]
    
    date_match = re.search(r'(\d{1,2})[\.\-/](\d{1,2})[\.\-/](\d{4})', date_str)
    if date_match:
        day, month, year = date_match.groups()
        date_str = f"{int(day):02d}-{int(month):02d}-{year}"
    
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
    
    for col in row.index:
        col_str = str(col)
        for month in months:
            if month in col_str:
                value = str(row[col]).strip()
                if value in ['✓', '✔', '☑', '⃝', '●', '•', '✅', '1', 'yes', 'Yes']:
                    checked_count += 1
                break
    
    if checked_count == 0:
        return 'Planned'
    elif checked_count >= 12:
        return 'Completed'
    elif checked_count > 0:
        return 'Ongoing'
    return 'Planned'

def read_excel_file(file_path):
    """Read Excel file and return records"""
    try:
        df = pd.read_excel(file_path, sheet_name=0)
        records = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                compliance_name = str(row.get('Statutory Compliance', '')).strip()
                if pd.isna(compliance_name) or compliance_name == 'nan' or compliance_name == '':
                    continue
                
                authority = str(row.get('Authority', '')).strip()
                if pd.isna(authority) or authority == 'nan':
                    authority = 'Unknown'
                
                # Parse dates
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
                
                # Submission date
                submission_date = None
                submission = row.get('Submission Date', '')
                if pd.notna(submission):
                    sub_date_str = parse_date(submission)
                    if sub_date_str:
                        submission_date = sub_date_str
                
                # Determine frequency
                frequency = 'OneTime'
                valid_text = str(valid_up_to).lower() if pd.notna(valid_up_to) else ''
                if 'every month' in valid_text or 'monthly' in valid_text:
                    frequency = 'Monthly'
                elif 'quarter' in valid_text:
                    frequency = 'Quarterly'
                elif 'annual' in valid_text or 'renewal' in str(compliance_name).lower():
                    frequency = 'Annual'
                
                # Status
                status = get_status_from_row(row)
                
                # Priority
                priority = 'Medium'
                high_priority = ['EPF', 'ESIC', 'Factory', 'Fire', 'Salary', 'Bonus', 'Gratuity', 'Insurance']
                for keyword in high_priority:
                    if keyword.lower() in compliance_name.lower() or keyword.lower() in authority.lower():
                        priority = 'High'
                        break
                
                # Category
                category = 'Other'
                if any(x in authority for x in ['EPFO', 'ESIC', 'Gratuity', 'DISH']):
                    category = 'Labour Compliance'
                elif 'Insurance' in authority or 'Mediclaim' in authority:
                    category = 'Insurance'
                elif any(x in authority for x in ['RTO', 'Tax', 'FC']):
                    category = 'Vehicle Compliance'
                elif 'Factory' in compliance_name or 'License' in compliance_name:
                    category = 'Factory Compliance'
                
                record = {
                    'authority': authority,
                    'compliance_name': compliance_name,
                    'category': category,
                    'valid_date': valid_date,
                    'submission_date': submission_date,
                    'process_time': str(row.get('Process Time', '')).strip() if pd.notna(row.get('Process Time', '')) else None,
                    'frequency': frequency,
                    'priority': priority,
                    'status': status,
                    'row': idx + 2
                }
                
                records.append(record)
                
            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")
        
        return records, errors
        
    except Exception as e:
        return [], [str(e)]