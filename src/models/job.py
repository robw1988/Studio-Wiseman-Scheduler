from src.models.user import db
from datetime import datetime

class WorkshopJob(db.Model):
    __tablename__ = 'workshop_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    cabinetry_type = db.Column(db.String(50), nullable=False)  # Kitchen, Wardrobe, Media Wall, etc.
    build_start_date = db.Column(db.Date)
    build_duration_days = db.Column(db.Integer)
    stage = db.Column(db.String(20), default='Not Started')  # Not Started, Planned, Build, Spray, Fit, Snag, Finished
    actual_build_days = db.Column(db.Integer)
    actual_fitting_days = db.Column(db.Integer)
    booking_date = db.Column(db.Date)
    fitting_date = db.Column(db.Date)
    job_price = db.Column(db.Float)
    fitting_date_status = db.Column(db.String(20), default='Planned')  # Planned, Provisional, Confirmed
    client_needs_update = db.Column(db.Boolean, default=False)
    client_contacted = db.Column(db.Boolean, default=False)
    estimated_build_days = db.Column(db.Integer)
    estimated_fitting_days = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='jobs')
    quote = db.relationship('Quote', back_populates='job')
    assignments = db.relationship('JobAssignment', back_populates='job', cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='job', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'quote_id': self.quote_id,
            'cabinetry_type': self.cabinetry_type,
            'build_start_date': self.build_start_date.isoformat() if self.build_start_date else None,
            'build_duration_days': self.build_duration_days,
            'stage': self.stage,
            'actual_build_days': self.actual_build_days,
            'actual_fitting_days': self.actual_fitting_days,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'fitting_date': self.fitting_date.isoformat() if self.fitting_date else None,
            'job_price': self.job_price,
            'fitting_date_status': self.fitting_date_status,
            'client_needs_update': self.client_needs_update,
            'client_contacted': self.client_contacted,
            'estimated_build_days': self.estimated_build_days,
            'estimated_fitting_days': self.estimated_fitting_days,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'build_team': [assignment.user.full_name for assignment in self.get_build_team()],
            'fit_team': [assignment.user.full_name for assignment in self.get_fit_team()],
            'payments': [payment.to_dict() for payment in self.payments],
            'status': self.calculate_status()
        }
    
    def get_build_team(self):
        return [a for a in self.assignments if a.role == 'Build Team']
        
    def get_fit_team(self):
        return [a for a in self.assignments if a.role == 'Fit Team']
    
    def calculate_status(self):
        """Calculate job status based on dates and progress"""
        today = datetime.now().date()
        
        if self.stage == 'Finished':
            return 'Completed'
            
        if self.stage == 'Snag':
            return 'Issue'
            
        if not self.build_start_date:
            return 'Not Scheduled'
            
        if self.build_start_date > today:
            return 'Scheduled'
            
        # Check if we're behind schedule
        if self.stage == 'Build' and self.build_start_date and self.build_duration_days:
            expected_end = self.build_start_date + datetime.timedelta(days=self.build_duration_days)
            if today > expected_end:
                return 'Delayed'
                
        if self.stage == 'Fit' and self.fitting_date and today > self.fitting_date:
            return 'Delayed'
            
        return 'On Track'
    
    def generate_payment_schedule(self):
        """Generate payment schedule based on job type and price"""
        if not self.job_price:
            return
            
        from src.models.payment import Payment
        
        # Delete existing payments
        for payment in self.payments:
            db.session.delete(payment)
            
        # Create new payment schedule
        if self.cabinetry_type.lower() == 'kitchen':
            # Kitchens: 10% deposit, 40% build, 40% fit, 10% completion
            deposit = Payment(
                job_id=self.id,
                type='Deposit',
                amount=self.job_price * 0.1,
                due_date=self.booking_date,
                status='Due'
            )
            
            build = Payment(
                job_id=self.id,
                type='Build Installment',
                amount=self.job_price * 0.4,
                due_date=self.build_start_date,
                status='Due'
            )
            
            fit = Payment(
                job_id=self.id,
                type='Fitting Installment',
                amount=self.job_price * 0.4,
                due_date=self.fitting_date,
                status='Due'
            )
            
            completion = Payment(
                job_id=self.id,
                type='Completion',
                amount=self.job_price * 0.1,
                due_date=self.fitting_date,  # Will be updated when job is completed
                status='Due'
            )
            
            db.session.add_all([deposit, build, fit, completion])
        else:
            # Cabinetry: 50% deposit, 40% fit, 10% completion
            deposit = Payment(
                job_id=self.id,
                type='Deposit',
                amount=self.job_price * 0.5,
                due_date=self.booking_date,
                status='Due'
            )
            
            fit = Payment(
                job_id=self.id,
                type='Fitting Installment',
                amount=self.job_price * 0.4,
                due_date=self.fitting_date,
                status='Due'
            )
            
            completion = Payment(
                job_id=self.id,
                type='Completion',
                amount=self.job_price * 0.1,
                due_date=self.fitting_date,  # Will be updated when job is completed
                status='Due'
            )
            
            db.session.add_all([deposit, fit, completion])
            
        db.session.commit()
