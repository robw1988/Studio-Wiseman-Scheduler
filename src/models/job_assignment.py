from src.models.user import db
from datetime import datetime

class JobAssignment(db.Model):
    __tablename__ = 'job_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('workshop_jobs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Build Team, Fit Team
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = db.relationship('WorkshopJob', back_populates='assignments')
    user = db.relationship('User', back_populates='job_assignments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'job_name': self.job.name if self.job else None,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
