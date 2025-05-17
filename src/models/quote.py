from src.models.user import db
from datetime import datetime

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    cabinetry_type = db.Column(db.String(50), nullable=False)  # Kitchen, Wardrobe, Media Wall, etc.
    initial_quote_amount = db.Column(db.Float, nullable=False)
    final_quote_amount = db.Column(db.Float)
    material_costs = db.Column(db.Float)
    status = db.Column(db.String(20), default='Not Sent')  # Not Sent, Sent, Negotiating, Accepted, Accepted-Negotiated, Rejected
    negotiation_details = db.Column(db.Text)
    deposit_paid_date = db.Column(db.Date)
    estimated_build_days = db.Column(db.Integer)
    estimated_fitting_days = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='quotes')
    extras = db.relationship('QuoteExtra', back_populates='quote', cascade='all, delete-orphan')
    job = db.relationship('WorkshopJob', back_populates='quote', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'cabinetry_type': self.cabinetry_type,
            'initial_quote_amount': self.initial_quote_amount,
            'final_quote_amount': self.final_quote_amount,
            'material_costs': self.material_costs,
            'status': self.status,
            'negotiation_details': self.negotiation_details,
            'deposit_paid_date': self.deposit_paid_date.isoformat() if self.deposit_paid_date else None,
            'estimated_build_days': self.estimated_build_days,
            'estimated_fitting_days': self.estimated_fitting_days,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'extras': [extra.to_dict() for extra in self.extras],
            'has_job': self.job is not None
        }
    
    def convert_to_job(self):
        """Convert this quote to a workshop job"""
        from src.models.job import WorkshopJob
        
        if self.job:
            return self.job
            
        if self.status not in ['Accepted', 'Accepted-Negotiated']:
            raise ValueError("Cannot convert quote to job: quote is not accepted")
            
        job = WorkshopJob(
            name=self.name,
            client_id=self.client_id,
            quote_id=self.id,
            cabinetry_type=self.cabinetry_type,
            job_price=self.final_quote_amount or self.initial_quote_amount,
            estimated_build_days=self.estimated_build_days,
            estimated_fitting_days=self.estimated_fitting_days,
            stage='Not Started'
        )
        
        db.session.add(job)
        db.session.commit()
        
        return job


class QuoteExtra(db.Model):
    __tablename__ = 'quote_extras'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quote = db.relationship('Quote', back_populates='extras')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quote_id': self.quote_id,
            'description': self.description,
            'price': self.price,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
