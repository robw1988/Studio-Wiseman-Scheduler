from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(20), default='Staff')  # Admin, Manager, CabinetMaker
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_assignments = db.relationship('JobAssignment', back_populates='user', lazy='dynamic')
    absences = db.relationship('StaffAbsence', back_populates='user', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_available(self, start_date, end_date):
        """Check if user is available during the given date range"""
        for absence in self.absences:
            if absence.overlaps_with_dates(start_date, end_date):
                return False
        return True
    
    def get_current_workload(self):
        """Calculate current workload based on assigned jobs"""
        active_assignments = 0
        for assignment in self.job_assignments:
            if assignment.job.stage not in ['Finished', 'Not Started']:
                active_assignments += 1
        return active_assignments
