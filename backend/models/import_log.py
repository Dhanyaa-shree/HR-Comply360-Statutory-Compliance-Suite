from database.db import db
from datetime import datetime

class ImportLog(db.Model):
    __tablename__ = 'import_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255))
    records_count = db.Column(db.Integer)
    success_count = db.Column(db.Integer)
    error_count = db.Column(db.Integer)
    errors = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_name': self.file_name,
            'records_count': self.records_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'errors': self.errors,
            'status': self.status,
            'imported_at': self.imported_at.isoformat() if self.imported_at else None
        }