from src.models.user import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('workshop_jobs.id'), nullable=False)
    type = db.Column(db.String(30), nullable=False)  # Deposit, Build Installment, Fitting Installment, Completion
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date)
    paid_date = db.Column(db.Date)
    status = db.Column(db.String(10), default='Due')  # Due, Paid
    xero_invoice_id = db.Column(db.String(100))  # For Xero integration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = db.relationship('WorkshopJob', back_populates='payments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'job_name': self.job.name if self.job else None,
            'type': self.type,
            'amount': self.amount,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'status': self.status,
            'xero_invoice_id': self.xero_invoice_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'client_name': self.job.client.name if self.job and self.job.client else None
        }
    
    def mark_as_paid(self, paid_date=None):
        """Mark this payment as paid"""
        self.status = 'Paid'
        self.paid_date = paid_date or datetime.now().date()
        db.session.commit()
        
    def create_in_xero(self):
        """Create an invoice in Xero for this payment"""
        # This would be implemented when Xero integration is added
        pass
