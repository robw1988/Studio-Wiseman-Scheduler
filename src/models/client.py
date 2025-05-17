from src.models.user import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    xero_client_id = db.Column(db.String(100))  # For Xero integration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quotes = db.relationship('Quote', back_populates='client', lazy='dynamic')
    jobs = db.relationship('WorkshopJob', back_populates='client', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'notes': self.notes,
            'xero_client_id': self.xero_client_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'lifetime_spend': self.calculate_lifetime_spend(),
            'job_count': self.jobs.count()
        }
    
    def calculate_lifetime_spend(self):
        total = 0
        for job in self.jobs:
            if job.job_price:
                total += job.job_price
        return total
