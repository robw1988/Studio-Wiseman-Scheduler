from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.payment import Payment
from src.models.job import WorkshopJob
from datetime import datetime, timedelta
from flask_login import login_required, current_user
import calendar

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/api/payments', methods=['GET'])
@login_required
def get_payments():
    """Get all payments"""
    payments = Payment.query.all()
    return jsonify([payment.to_dict() for payment in payments])

@payment_bp.route('/api/payments/<int:payment_id>', methods=['GET'])
@login_required
def get_payment(payment_id):
    """Get a specific payment"""
    payment = Payment.query.get_or_404(payment_id)
    return jsonify(payment.to_dict())

@payment_bp.route('/api/payments', methods=['POST'])
@login_required
def create_payment():
    """Create a new payment"""
    data = request.json
    
    payment = Payment(
        job_id=data['job_id'],
        type=data['type'],
        amount=data['amount'],
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
        paid_date=datetime.strptime(data['paid_date'], '%Y-%m-%d').date() if data.get('paid_date') else None,
        status=data.get('status', 'Due')
    )
    
    db.session.add(payment)
    db.session.commit()
    return jsonify(payment.to_dict()), 201

@payment_bp.route('/api/payments/<int:payment_id>/status', methods=['PUT'])
@login_required
def update_payment_status(payment_id):
    """Update a payment's status"""
    payment = Payment.query.get_or_404(payment_id)
    data = request.json
    
    if 'status' in data:
        payment.status = data['status']
        
        if data['status'] == 'Paid' and not payment.paid_date:
            payment.paid_date = datetime.now().date()
    
    if 'paid_date' in data:
        payment.paid_date = datetime.strptime(data['paid_date'], '%Y-%m-%d').date() if data['paid_date'] else None
        
        if payment.paid_date and payment.status == 'Due':
            payment.status = 'Paid'
    
    db.session.commit()
    return jsonify(payment.to_dict())

@payment_bp.route('/api/payments/<int:payment_id>/create-in-xero', methods=['POST'])
@login_required
def create_payment_in_xero(payment_id):
    """Create invoice in Xero for this payment"""
    payment = Payment.query.get_or_404(payment_id)
    
    # This would be implemented when Xero integration is added
    # For now, just update the xero_invoice_id field with a placeholder
    payment.xero_invoice_id = f"XERO-INV-{payment_id}-{datetime.now().strftime('%Y%m%d')}"
    db.session.commit()
    
    return jsonify({
        'message': 'Invoice created in Xero (simulated)',
        'xero_invoice_id': payment.xero_invoice_id
    })

@payment_bp.route('/api/reports/financial-forecast', methods=['GET'])
@login_required
def get_financial_forecast():
    """Get financial forecast for the next 6 months"""
    # Get current date and calculate start/end of current month
    today = datetime.now().date()
    current_month_start = today.replace(day=1)
    
    # Calculate the next 6 months
    months = []
    for i in range(7):  # Current month + 6 future months
        month_start = (current_month_start + timedelta(days=32 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        months.append({
            'month': month_start.strftime('%B %Y'),
            'start_date': month_start.isoformat(),
            'end_date': month_end.isoformat(),
            'total': 0,
            'deposit': 0,
            'build': 0,
            'fit': 0,
            'completion': 0
        })
    
    # Get all payments with due dates in the next 6 months
    end_date = months[-1]['end_date']
    payments = Payment.query.filter(
        Payment.due_date >= current_month_start,
        Payment.due_date <= end_date,
        Payment.status == 'Due'
    ).all()
    
    # Add payments to the appropriate month
    for payment in payments:
        for month in months:
            month_start = datetime.strptime(month['start_date'], '%Y-%m-%d').date()
            month_end = datetime.strptime(month['end_date'], '%Y-%m-%d').date()
            
            if month_start <= payment.due_date <= month_end:
                month['total'] += payment.amount
                
                if payment.type == 'Deposit':
                    month['deposit'] += payment.amount
                elif payment.type == 'Build Installment':
                    month['build'] += payment.amount
                elif payment.type == 'Fitting Installment':
                    month['fit'] += payment.amount
                elif payment.type == 'Completion':
                    month['completion'] += payment.amount
                
                break
    
    return jsonify(months)

@payment_bp.route('/api/reports/income-history', methods=['GET'])
@login_required
def get_income_history():
    """Get income history for the past 3 months"""
    # Get current date and calculate start of 3 months ago
    today = datetime.now().date()
    three_months_ago = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    three_months_ago = (three_months_ago - timedelta(days=1)).replace(day=1)
    
    # Calculate the past 3 months
    months = []
    for i in range(3):
        month_start = (three_months_ago + timedelta(days=32 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        months.append({
            'month': month_start.strftime('%B %Y'),
            'start_date': month_start.isoformat(),
            'end_date': month_end.isoformat(),
            'total': 0,
            'deposit': 0,
            'build': 0,
            'fit': 0,
            'completion': 0
        })
    
    # Get all payments with paid dates in the past 3 months
    start_date = months[0]['start_date']
    end_date = months[-1]['end_date']
    payments = Payment.query.filter(
        Payment.paid_date >= start_date,
        Payment.paid_date <= end_date,
        Payment.status == 'Paid'
    ).all()
    
    # Add payments to the appropriate month
    for payment in payments:
        for month in months:
            month_start = datetime.strptime(month['start_date'], '%Y-%m-%d').date()
            month_end = datetime.strptime(month['end_date'], '%Y-%m-%d').date()
            
            if month_start <= payment.paid_date <= month_end:
                month['total'] += payment.amount
                
                if payment.type == 'Deposit':
                    month['deposit'] += payment.amount
                elif payment.type == 'Build Installment':
                    month['build'] += payment.amount
                elif payment.type == 'Fitting Installment':
                    month['fit'] += payment.amount
                elif payment.type == 'Completion':
                    month['completion'] += payment.amount
                
                break
    
    # Calculate totals and percentages
    total_income = sum(month['total'] for month in months)
    total_deposit = sum(month['deposit'] for month in months)
    total_build = sum(month['build'] for month in months)
    total_fit = sum(month['fit'] for month in months)
    total_completion = sum(month['completion'] for month in months)
    
    percentages = {
        'deposit': (total_deposit / total_income * 100) if total_income > 0 else 0,
        'build': (total_build / total_income * 100) if total_income > 0 else 0,
        'fit': (total_fit / total_income * 100) if total_income > 0 else 0,
        'completion': (total_completion / total_income * 100) if total_income > 0 else 0
    }
    
    return jsonify({
        'months': months,
        'total_income': total_income,
        'percentages': percentages
    })
