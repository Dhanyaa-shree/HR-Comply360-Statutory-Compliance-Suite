from database.db import db
from datetime import datetime

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