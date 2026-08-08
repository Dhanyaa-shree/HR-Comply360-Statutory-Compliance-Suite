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

# ============================================
# APP CONFIGURATION
# ============================================
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_PATH, exist_ok=True)

# ✅ Use absolute path for SQLite
DB_PATH = os.path.join(INSTANCE_PATH, 'dev.db')

# ✅ Render.com specific path
if os.path.exists('/opt/render'):
    DB_PATH = '/opt/render/project/src/backend/instance/dev.db'
    os.makedirs('/opt/render/project/src/backend/instance', exist_ok=True)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('DEBUG', 'True') == 'True'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Email config
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# CORS
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With", "X-API-Key"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     supports_credentials=True,
     expose_headers=["Authorization", "Content-Type"]
)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ============================================
# MODELS
# ============================================

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

# ============================================
# ✅ DATABASE INITIALIZATION (CRITICAL FIX)
# ============================================

with app.app_context():
    try:
        print("=" * 60)
        print("🚀 Starting HR Comply360 Backend...")
        print(f"📁 Database path: {DB_PATH}")
        print(f"📧 Email configured for: {app.config['MAIL_USERNAME']}")
        print("=" * 60)
        
        # ✅ CREATE ALL TABLES
        db.create_all()
        print("✅ Database tables created/verified")
        
        # ✅ CREATE DEFAULT USER
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
            print("✅ Default user created: hr@company.com / password123")
        else:
            print(f"✅ User already exists: {user.email}")
        
        # ✅ CHECK DATA
        count = Compliance.query.count()
        print(f"📊 Existing compliance records: {count}")
        
        print("=" * 60)
        print("✅ Database initialization complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")
        import traceback
        traceback.print_exc()

# ============================================
# ROUTES
# ============================================

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
        print(f"❌ Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

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

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'HR Comply360 API is running!', 'status': 'ok'})

# ============================================
# ✅ REMINDER ENDPOINT (for GitHub Actions)
# ============================================

@app.route('/api/check-reminders', methods=['POST', 'OPTIONS'])
def check_reminders_endpoint():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        api_key = request.headers.get('X-API-Key')
        expected_key = os.getenv('GITHUB_ACTIONS_API_KEY')
        
        if expected_key and (not api_key or api_key != expected_key):
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Send to target email
        target_email = os.getenv('REMINDER_EMAIL', 'thangaraj4u@gmail.com')
        return jsonify({
            'success': True,
            'message': f'Reminders sent to {target_email}',
            'target': target_email,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ============================================
# RUN APP
# ============================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)