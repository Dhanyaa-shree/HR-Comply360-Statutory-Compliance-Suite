from database.db import db
from datetime import datetime

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
    
    # ✅ NEW FIELDS FOR CUSTOM REMINDERS
    reminder_1_date = db.Column(db.Date)      # First notification date (manual)
    reminder_2_date = db.Column(db.Date)      # Second notification (5 days before due date)
    reminder_3_date = db.Column(db.Date)      # Third notification (2 days before due date)
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
            # ✅ NEW FIELDS
            'reminder_1_date': self.reminder_1_date.isoformat() if self.reminder_1_date else None,
            'reminder_2_date': self.reminder_2_date.isoformat() if self.reminder_2_date else None,
            'reminder_3_date': self.reminder_3_date.isoformat() if self.reminder_3_date else None,
            'reminder_1_sent': self.reminder_1_sent,
            'reminder_2_sent': self.reminder_2_sent,
            'reminder_3_sent': self.reminder_3_sent
        }