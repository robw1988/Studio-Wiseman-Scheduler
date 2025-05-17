from src.models.user import db
from datetime import datetime

class StaffAbsence(db.Model):
    __tablename__ = 'staff_absences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # Leave, Sickness, Training
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='absences')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'type': self.type,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'duration_days': (self.end_date - self.start_date).days + 1
        }
    
    def overlaps_with_dates(self, start_date, end_date):
        """Check if this absence overlaps with the given date range"""
        return (self.start_date <= end_date and self.end_date >= start_date)
