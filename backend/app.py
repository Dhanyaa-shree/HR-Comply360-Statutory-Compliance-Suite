from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from sqlalchemy import func
import bcrypt
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_PATH, exist_ok=True)

DB_PATH = os.path.join(INSTANCE_PATH, 'dev.db')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('DEBUG', 'True') == 'True'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# ============ CORS ============
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     supports_credentials=True,
     expose_headers=["Authorization", "Content-Type"]
)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ============ ENSURE TABLES EXIST ON STARTUP ============
# ✅ This runs when gunicorn starts the app (and also when running python app.py)
with app.app_context():
    db.create_all()
    print("✅ Database tables created/verified on startup")

print(f"📁 Database path: {DB_PATH}")
print(f"📧 Email configured for: {app.config['MAIL_USERNAME']}")

# ============ MODELS ============
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id, 
            'name': self.name, 
            'email': self.email, 
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Compliance(db.Model):
    __tablename__ = 'compliance'
    id = db.Column(db.Integer, primary_key=True)
    serial_no = db.Column(db.Integer)
    authority = db.Column(db.String(100), nullable=False)
    compliance_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    valid_date = db.Column(db.Date, nullable=False)
    submission_date = db.Column(db.Date)
    process_time = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    reminder_days = db.Column(db.String(100))
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(20), default='Planned')
    remarks = db.Column(db.Text)
    completion_date = db.Column(db.Date)
    updated_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Reminder fields
    reminder_1_date = db.Column(db.Date)
    reminder_2_date = db.Column(db.Date)
    reminder_3_date = db.Column(db.Date)
    reminder_1_sent = db.Column(db.Boolean, default=False)
    reminder_2_sent = db.Column(db.Boolean, default=False)
    reminder_3_sent = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'serial_no': self.serial_no,
            'authority': self.authority,
            'compliance_name': self.compliance_name,
            'category': self.category,
            'valid_date': self.valid_date.isoformat() if self.valid_date else None,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'process_time': self.process_time,
            'frequency': self.frequency,
            'reminder_days': self.reminder_days,
            'priority': self.priority,
            'status': self.status,
            'remarks': self.remarks,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'reminder_1_date': self.reminder_1_date.isoformat() if self.reminder_1_date else None,
            'reminder_2_date': self.reminder_2_date.isoformat() if self.reminder_2_date else None,
            'reminder_3_date': self.reminder_3_date.isoformat() if self.reminder_3_date else None,
            'reminder_1_sent': self.reminder_1_sent,
            'reminder_2_sent': self.reminder_2_sent,
            'reminder_3_sent': self.reminder_3_sent
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='Info')
    is_read = db.Column(db.Boolean, default=False)
    compliance_id = db.Column(db.Integer, db.ForeignKey('compliance.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'compliance_id': self.compliance_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    compliance_id = db.Column(db.Integer, db.ForeignKey('compliance.id', ondelete='CASCADE'))
    recipient_email = db.Column(db.String(100))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    reminder_type = db.Column(db.String(50))
    email_status = db.Column(db.String(20), default='Pending')
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'compliance_id': self.compliance_id,
            'recipient_email': self.recipient_email,
            'subject': self.subject,
            'message': self.message,
            'reminder_type': self.reminder_type,
            'email_status': self.email_status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    compliance_id = db.Column(db.Integer, db.ForeignKey('compliance.id', ondelete='CASCADE'))
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'compliance_id': self.compliance_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

# ============ INIT DB ============
def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
        
        # ✅ CHANGED: Default user email is now thangaraj4u@gmail.com
        user = User.query.filter_by(email='thangaraj4u@gmail.com').first()
        if not user:
            hashed = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
            user = User(
                name='HR Admin',
                email='thangaraj4u@gmail.com',  # ← CHANGED HERE
                password_hash=hashed.decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            print("✅ Default user created: thangaraj4u@gmail.com / password123")
        else:
            print("✅ User already exists")

# ============ EMAIL ============
def send_email(recipient, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return False

def generate_reminder_email_body(compliance, days_remaining, reminder_type):
    urgency_color = '#10B981'
    if days_remaining <= 2 and days_remaining >= 0:
        urgency_color = '#EF4444'
    elif days_remaining <= 5:
        urgency_color = '#F59E0B'
    elif days_remaining <= 10:
        urgency_color = '#F97316'
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #2563EB, #4F46E5); color: white; padding: 25px; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; border: 1px solid #e5e7eb; }}
            .field {{ margin: 10px 0; padding: 12px; background: white; border-radius: 4px; border-left: 4px solid {urgency_color}; }}
            .label {{ font-weight: bold; color: #4B5563; font-size: 12px; }}
            .value {{ font-size: 16px; color: #111827; }}
            .urgency {{ background: {urgency_color}; color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; font-size: 14px; font-weight: bold; }}
            .footer {{ margin-top: 20px; padding: 15px; background: #f3f4f6; border-radius: 8px; text-align: center; font-size: 12px; color: #6B7280; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">📋 HR Comply360</h2>
                <p style="margin: 5px 0 0; opacity: 0.9;">Centralized HR Compliance Portal</p>
            </div>
            <div class="content">
                <h3 style="margin-top: 0;">{reminder_type}</h3>
                <div style="text-align: center; margin: 20px 0;">
                    <span class="urgency">{reminder_type}</span>
                </div>
                <div class="field">
                    <div class="label">📌 Compliance Name</div>
                    <div class="value"><strong>{compliance.compliance_name}</strong></div>
                </div>
                <div class="field">
                    <div class="label">🏛️ Authority</div>
                    <div class="value">{compliance.authority}</div>
                </div>
                <div class="field">
                    <div class="label">📅 Due Date</div>
                    <div class="value"><strong>{compliance.valid_date.strftime('%d-%m-%Y')}</strong></div>
                </div>
                <div class="field">
                    <div class="label">⏰ Days Remaining</div>
                    <div class="value"><strong style="color: {urgency_color}; font-size: 20px;">{abs(days_remaining)} days</strong></div>
                </div>
                <div class="field">
                    <div class="label">📊 Status</div>
                    <div class="value">{compliance.status}</div>
                </div>
                <div class="field">
                    <div class="label">⚡ Priority</div>
                    <div class="value">{compliance.priority}</div>
                </div>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">
                <div style="background: #FEF2F2; padding: 15px; border-radius: 8px; border-left: 4px solid #EF4444;">
                    <p style="margin: 0; color: #991B1B;">
                        ⚠️ <strong>Action Required:</strong> Please complete this compliance by the due date.
                    </p>
                </div>
            </div>
            <div class="footer">
                <p>This is an automated reminder from HR Comply360.</p>
                <p style="margin: 0;">Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

# ============ ROUTES ============

# ===== AUTH =====
@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email', '')).first()
        if not user or not bcrypt.checkpw(data.get('password', '').encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
        return jsonify({'access_token': token, 'user': user.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== COMPLIANCE - GET ALL =====
@app.route('/api/compliance', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_compliance():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Compliance.query
        if search:
            query = query.filter(Compliance.compliance_name.ilike(f'%{search}%'))
        
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'data': [c.to_dict() for c in items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if total > 0 else 1
            }
        })
    except Exception as e:
        print(f"❌ Error in get_compliance: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ===== COMPLIANCE - STATS =====
@app.route('/api/compliance/stats', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_stats():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        print("📊 Fetching stats...")
        total = Compliance.query.count()
        completed = Compliance.query.filter_by(status='Completed').count()
        ongoing = Compliance.query.filter_by(status='Ongoing').count()
        planned = Compliance.query.filter_by(status='Planned').count()
        overdue = Compliance.query.filter_by(status='Overdue').count()
        
        category_stats = db.session.query(
            Compliance.category,
            func.count(Compliance.id).label('count')
        ).group_by(Compliance.category).all()
        
        return jsonify({
            'total': total,
            'completed': completed,
            'ongoing': ongoing,
            'planned': planned,
            'overdue': overdue,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 2),
            'category_stats': [{'category': c[0], 'count': c[1]} for c in category_stats],
            'monthly_stats': [],
            'due_this_month': 0
        })
    except Exception as e:
        print(f"❌ Error in get_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ===== COMPLIANCE - CREATE =====
@app.route('/api/compliance', methods=['POST'])
@jwt_required()
def create_compliance():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        valid_date = datetime.strptime(data.get('valid_date'), '%Y-%m-%d').date()
        
        reminder_1_date = None
        if data.get('reminder_1_date'):
            reminder_1_date = datetime.strptime(data.get('reminder_1_date'), '%Y-%m-%d').date()
        
        compliance = Compliance(
            authority=data.get('authority'),
            compliance_name=data.get('compliance_name'),
            category=data.get('category'),
            valid_date=valid_date,
            submission_date=datetime.strptime(data.get('submission_date'), '%Y-%m-%d').date() if data.get('submission_date') else None,
            process_time=data.get('process_time'),
            frequency=data.get('frequency', 'OneTime'),
            reminder_days=data.get('reminder_days', '30,15,7,3,1'),
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'Planned'),
            remarks=data.get('remarks'),
            updated_by=str(user_id),
            reminder_1_date=reminder_1_date,
            reminder_2_date=valid_date - timedelta(days=5),
            reminder_3_date=valid_date - timedelta(days=2),
            reminder_1_sent=False,
            reminder_2_sent=False,
            reminder_3_sent=False
        )
        
        db.session.add(compliance)
        db.session.commit()
        return jsonify(compliance.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== COMPLIANCE - GET ONE =====
@app.route('/api/compliance/<int:id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_compliance_by_id(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        compliance = Compliance.query.get_or_404(id)
        return jsonify(compliance.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== COMPLIANCE - UPDATE =====
@app.route('/api/compliance/<int:id>', methods=['PUT'])
@jwt_required()
def update_compliance(id):
    try:
        compliance = Compliance.query.get_or_404(id)
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if 'authority' in data:
            compliance.authority = data['authority']
        if 'compliance_name' in data:
            compliance.compliance_name = data['compliance_name']
        if 'category' in data:
            compliance.category = data['category']
        if 'valid_date' in data:
            compliance.valid_date = datetime.strptime(data['valid_date'], '%Y-%m-%d').date()
            compliance.reminder_2_date = compliance.valid_date - timedelta(days=5)
            compliance.reminder_3_date = compliance.valid_date - timedelta(days=2)
            compliance.reminder_2_sent = False
            compliance.reminder_3_sent = False
        if 'submission_date' in data and data['submission_date']:
            compliance.submission_date = datetime.strptime(data['submission_date'], '%Y-%m-%d').date()
        if 'process_time' in data:
            compliance.process_time = data['process_time']
        if 'frequency' in data:
            compliance.frequency = data['frequency']
        if 'reminder_days' in data:
            compliance.reminder_days = data['reminder_days']
        if 'priority' in data:
            compliance.priority = data['priority']
        if 'status' in data:
            compliance.status = data['status']
            if data['status'] == 'Completed':
                compliance.completion_date = date.today()
        if 'remarks' in data:
            compliance.remarks = data['remarks']
        if 'reminder_1_date' in data:
            if data['reminder_1_date']:
                compliance.reminder_1_date = datetime.strptime(data['reminder_1_date'], '%Y-%m-%d').date()
                compliance.reminder_1_sent = False
            else:
                compliance.reminder_1_date = None
        
        compliance.updated_by = str(user_id)
        db.session.commit()
        return jsonify(compliance.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== COMPLIANCE - DELETE =====
@app.route('/api/compliance/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_compliance(id):
    try:
        compliance = Compliance.query.get_or_404(id)
        db.session.delete(compliance)
        db.session.commit()
        return jsonify({'message': 'Deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== NOTIFICATIONS =====
@app.route('/api/notifications', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_notifications():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        user_id = get_jwt_identity()
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
        return jsonify([n.to_dict() for n in notifications])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/unread-count', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_unread_count():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        user_id = get_jwt_identity()
        count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        return jsonify({'unread_count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<int:id>/read', methods=['PUT'])
@jwt_required()
def mark_read(id):
    try:
        notification = Notification.query.get_or_404(id)
        notification.is_read = True
        db.session.commit()
        return jsonify({'message': 'Marked as read'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    try:
        user_id = get_jwt_identity()
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({'message': 'All marked as read'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== DOCUMENTS =====
@app.route('/api/documents', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_documents():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        documents = Document.query.order_by(Document.uploaded_at.desc()).all()
        return jsonify([d.to_dict() for d in documents])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/upload', methods=['POST', 'OPTIONS'])
@jwt_required()
def upload_document():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        compliance_id = request.form.get('compliance_id', type=int)
        
        if not compliance_id:
            return jsonify({'error': 'compliance_id is required'}), 400
        
        compliance = Compliance.query.get(compliance_id)
        if not compliance:
            return jsonify({'error': 'Compliance not found'}), 404
        
        upload_folder = os.path.join(BASE_DIR, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = file.filename
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        doc = Document(
            compliance_id=compliance_id,
            file_name=filename,
            file_path=file_path,
            file_type=file.content_type or 'unknown',
            file_size=os.path.getsize(file_path)
        )
        db.session.add(doc)
        db.session.commit()
        
        return jsonify({'message': 'Document uploaded successfully', 'document': doc.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<int:id>', methods=['GET'])
@jwt_required()
def download_document(id):
    try:
        doc = Document.query.get_or_404(id)
        return send_file(doc.file_path, as_attachment=True, download_name=doc.file_name)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_document(id):
    try:
        doc = Document.query.get_or_404(id)
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        db.session.delete(doc)
        db.session.commit()
        return jsonify({'message': 'Document deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== UPLOAD =====
@app.route('/api/upload/excel', methods=['POST', 'OPTIONS'])
@jwt_required()
def upload_excel():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        return jsonify({'success': True, 'records_imported': 0, 'message': 'Upload received'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== REMINDERS =====
@app.route('/api/reminders/check', methods=['GET'])
def check_reminders():
    try:
        today = date.today()
        compliance_list = Compliance.query.filter(Compliance.status != 'Completed').all()
        users = User.query.all()
        
        sent_count = 0
        for compliance in compliance_list:
            if not compliance.valid_date:
                continue
            
            if not compliance.reminder_1_date:
                compliance.reminder_1_date = compliance.valid_date - timedelta(days=30)
            compliance.reminder_2_date = compliance.valid_date - timedelta(days=5)
            compliance.reminder_3_date = compliance.valid_date - timedelta(days=2)
            db.session.commit()
            
            reminders = []
            if compliance.reminder_1_date and not compliance.reminder_1_sent and today >= compliance.reminder_1_date:
                days_until_due = (compliance.valid_date - today).days
                reminders.append(('First Reminder', 'reminder_1_sent', days_until_due))
            if compliance.reminder_2_date and not compliance.reminder_2_sent and today >= compliance.reminder_2_date:
                days_until_due = (compliance.valid_date - today).days
                reminders.append(('Second Reminder (5 Days Before)', 'reminder_2_sent', days_until_due))
            if compliance.reminder_3_date and not compliance.reminder_3_sent and today >= compliance.reminder_3_date:
                days_until_due = (compliance.valid_date - today).days
                reminders.append(('Third Reminder (2 Days Before)', 'reminder_3_sent', days_until_due))
            
            for reminder_type, sent_field, days_until_due in reminders:
                for user in users:
                    subject = f"{reminder_type}: {compliance.compliance_name}"
                    body = generate_reminder_email_body(compliance, days_until_due if days_until_due > 0 else 0, reminder_type)
                    send_email(user.email, subject, body)
                    
                    email_log = EmailLog(
                        user_id=user.id,
                        compliance_id=compliance.id,
                        recipient_email=user.email,
                        subject=subject,
                        message=body,
                        reminder_type=reminder_type,
                        email_status='Sent'
                    )
                    db.session.add(email_log)
                    
                    notification = Notification(
                        user_id=user.id,
                        title=f"Compliance Reminder: {compliance.compliance_name}",
                        message=f"{reminder_type}: Due on {compliance.valid_date.strftime('%d-%m-%Y')}",
                        type='Reminder',
                        compliance_id=compliance.id
                    )
                    db.session.add(notification)
                
                setattr(compliance, sent_field, True)
                db.session.commit()
                sent_count += 1
                print(f"📧 Sent {reminder_type} for: {compliance.compliance_name}")
        
        return jsonify({'success': True, 'sent': sent_count, 'errors': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== TEST EMAIL =====
@app.route('/api/test-email', methods=['GET'])
def test_email_route():
    try:
        success = send_email(app.config['MAIL_USERNAME'], '🧪 Test Email', '<h2>✅ Email Working!</h2>')
        if success:
            return jsonify({'message': 'Email sent successfully!'})
        else:
            return jsonify({'error': 'Failed to send email'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ROOT =====
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'HR Comply360 API is running!', 'status': 'ok'})

@app.route('/api', methods=['GET'])
def api_home():
    return jsonify({
        'message': 'HR Comply360 API',
        'status': 'ok',
        'endpoints': [
            '/api/auth/login',
            '/api/compliance',
            '/api/compliance/stats',
            '/api/notifications',
            '/api/documents',
            '/api/upload/excel'
        ]
    })

# ============================================================
# ===== GITHUB ACTIONS REMINDER ENDPOINT =====================
# ============================================================

@app.route('/api/check-reminders', methods=['POST', 'OPTIONS'])
def check_reminders_endpoint():
    """
    Endpoint that GitHub Actions will call to trigger reminder checks.
    Protected by API key to prevent unauthorized access.
    """
    # ✅ Handle CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        # ✅ Verify API key from GitHub Actions
        api_key = request.headers.get('X-API-Key')
        expected_key = os.getenv('GITHUB_ACTIONS_API_KEY')
        
        if not expected_key:
            print("⚠️ GITHUB_ACTIONS_API_KEY not set in environment variables")
            return jsonify({
                'error': 'API key not configured',
                'message': 'Please set GITHUB_ACTIONS_API_KEY in your .env file'
            }), 500
        
        if not api_key or api_key != expected_key:
            print(f"❌ Invalid API key attempt")
            return jsonify({'error': 'Unauthorized - Invalid API key'}), 401
        
        print(f"🔔 GitHub Actions triggered reminder check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ✅ Call the same logic as /api/reminders/check
        return run_reminder_check()

    except Exception as e:
        print(f"❌ Error in reminder endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


def run_reminder_check():
    """
    Internal function that does the actual reminder checking.
    This is the SAME logic as your /api/reminders/check endpoint.
    """
    try:
        today = date.today()
        compliance_list = Compliance.query.filter(Compliance.status != 'Completed').all()
        users = User.query.all()
        
        sent_count = 0
        error_count = 0
        errors = []
        
        if not users:
            print("⚠️ No users found in database")
            return jsonify({
                'success': False,
                'message': 'No users found to send reminders',
                'sent': 0
            }), 200
        
        for compliance in compliance_list:
            if not compliance.valid_date:
                continue
            
            # Ensure reminder dates are set
            if not compliance.reminder_1_date:
                compliance.reminder_1_date = compliance.valid_date - timedelta(days=30)
            compliance.reminder_2_date = compliance.valid_date - timedelta(days=5)
            compliance.reminder_3_date = compliance.valid_date - timedelta(days=2)
            
            reminders = []
            
            # Check Reminder 1
            if compliance.reminder_1_date and not compliance.reminder_1_sent and today >= compliance.reminder_1_date:
                days_until_due = (compliance.valid_date - today).days
                reminders.append(('First Reminder', 'reminder_1_sent', days_until_due))
            
            # Check Reminder 2
            if compliance.reminder_2_date and not compliance.reminder_2_sent and today >= compliance.reminder_2_date:
                days_until_due = (compliance.valid_date - today).days
                reminders.append(('Second Reminder (5 Days Before)', 'reminder_2_sent', days_until_due))
            
            # Check Reminder 3
            if compliance.reminder_3_date and not compliance.reminder_3_sent and today >= compliance.reminder_3_date:
                days_until_due = (compliance.valid_date - today).days
                reminders.append(('Third Reminder (2 Days Before)', 'reminder_3_sent', days_until_due))
            
            for reminder_type, sent_field, days_until_due in reminders:
                try:
                    for user in users:
                        subject = f"{reminder_type}: {compliance.compliance_name}"
                        body = generate_reminder_email_body(
                            compliance, 
                            days_until_due if days_until_due > 0 else 0, 
                            reminder_type
                        )
                        
                        # Send email
                        email_sent = send_email(user.email, subject, body)
                        
                        # Log email
                        email_log = EmailLog(
                            user_id=user.id,
                            compliance_id=compliance.id,
                            recipient_email=user.email,
                            subject=subject,
                            message=body[:500],
                            reminder_type=reminder_type,
                            email_status='Sent' if email_sent else 'Failed'
                        )
                        db.session.add(email_log)
                        
                        # Create in-app notification
                        notification = Notification(
                            user_id=user.id,
                            title=f"Compliance Reminder: {compliance.compliance_name}",
                            message=f"{reminder_type}: Due on {compliance.valid_date.strftime('%d-%m-%Y')}",
                            type='Reminder',
                            compliance_id=compliance.id
                        )
                        db.session.add(notification)
                    
                    # Mark reminder as sent
                    setattr(compliance, sent_field, True)
                    sent_count += 1
                    print(f"📧 Sent {reminder_type} for: {compliance.compliance_name}")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"Error sending {reminder_type} for {compliance.compliance_name}: {str(e)}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")
                    db.session.rollback()
        
        # Commit all changes
        db.session.commit()
        
        print(f"✅ Reminder check completed: {sent_count} sent, {error_count} errors")
        
        return jsonify({
            'success': True,
            'message': 'Reminder check completed',
            'sent': sent_count,
            'errors': error_count,
            'error_details': errors[:10] if errors else [],
            'checked_records': len(compliance_list),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in run_reminder_check: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


# ============ RUN ============
if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("🚀 HR Comply360 Backend")
    print("="*50)
    print("📧 Login: thangaraj4u@gmail.com")  # ← UPDATED
    print("🔑 Password: password123")
    print("📍 Server: http://localhost:5000")
    print("📧 Email: " + (app.config['MAIL_USERNAME'] or 'Not configured'))
    print("="*50 + "\n")
    
    # ✅ Ensure all tables exist before running
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    app.run(host='0.0.0.0', port=5000, debug=True)