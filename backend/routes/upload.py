from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models.compliance import Compliance
from models.import_log import ImportLog
import pandas as pd
import os
from datetime import datetime
import json

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/excel', methods=['POST'])
@jwt_required()
def upload_excel():
    try:
        print("=" * 60)
        print("📤 IMPORT FILE API CALLED")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        print(f"📁 File: {file.filename}")
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Support both Excel and CSV
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            return jsonify({'error': 'Only Excel (.xlsx, .xls) or CSV (.csv) files allowed'}), 400
        
        # Save file
        os.makedirs('uploads', exist_ok=True)
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        print(f"💾 File saved: {file_path}")
        
        # Read file (Excel or CSV)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            print(f"📊 CSV loaded: {len(df)} rows")
        else:
            df = pd.read_excel(file_path, header=2)
            print(f"📊 Excel loaded: {len(df)} rows")
        
        print(f"📋 Columns: {df.columns.tolist()}")
        
        user_id = get_jwt_identity()
        count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Get compliance name
                name = str(row.get('Statutory Compliance', '')).strip()
                if not name or name == 'nan' or name == '':
                    continue
                
                # Get authority
                authority = str(row.get('Authority', '')).strip()
                if authority == 'nan' or authority == '':
                    authority = 'Unknown'
                
                # Get valid date
                valid_date = datetime.now().date()
                valid_up_to = row.get('Valid up to', row.get('Due Date', ''))
                if pd.notna(valid_up_to):
                    try:
                        if isinstance(valid_up_to, pd.Timestamp):
                            valid_date = valid_up_to.date()
                        else:
                            date_str = str(valid_up_to)
                            for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y']:
                                try:
                                    valid_date = datetime.strptime(date_str, fmt).date()
                                    break
                                except:
                                    pass
                    except:
                        pass
                
                # Determine status
                status = 'Planned'
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                checked = 0
                for col in row.index:
                    col_str = str(col)
                    for month in months:
                        if month in col_str:
                            value = str(row[col]).strip()
                            if value in ['✓', '✔', '☑', '⃝', '●', '•', '✅']:
                                checked += 1
                            break
                if checked >= 12:
                    status = 'Completed'
                elif checked > 0:
                    status = 'Ongoing'
                
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
                elif 'LPT' in authority:
                    category = 'HR Activity'
                
                # Create compliance
                compliance = Compliance(
                    authority=authority,
                    compliance_name=name,
                    category=category,
                    valid_date=valid_date,
                    submission_date=None,
                    process_time=None,
                    frequency='OneTime',
                    priority='Medium',
                    status=status,
                    updated_by=str(user_id),
                    remarks=f'Imported from {file.filename}'
                )
                db.session.add(compliance)
                count += 1
                
                if count % 10 == 0:
                    print(f"✅ Imported {count} records...")
                    
            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")
                print(f"❌ Row {idx+2}: {str(e)}")
        
        db.session.commit()
        
        # Log import
        try:
            import_log = ImportLog(
                file_name=file.filename,
                records_count=count + len(errors),
                success_count=count,
                error_count=len(errors),
                errors=json.dumps(errors),
                status='Success' if len(errors) == 0 else 'Partial'
            )
            db.session.add(import_log)
            db.session.commit()
        except Exception as e:
            print(f"⚠️ Could not log import: {str(e)}")
        
        # Clean up
        try:
            os.remove(file_path)
            print(f"🗑️ Removed temp file")
        except:
            pass
        
        print(f"✅ Imported {count} records")
        print("=" * 60)
        
        return jsonify({
            'success': True,
            'records_imported': count,
            'errors': errors,
            'message': f'Successfully imported {count} records'
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500