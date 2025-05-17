from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.job import WorkshopJob
from src.models.quote import Quote
from src.models.client import Client
from src.models.payment import Payment
from datetime import datetime, timedelta
from flask_login import login_required, current_user

report_bp = Blueprint('report', __name__)

@report_bp.route('/api/reports/dashboard-summary', methods=['GET'])
@login_required
def get_dashboard_summary():
    """Get summary data for dashboard"""
    # Count active jobs
    active_jobs = WorkshopJob.query.filter(WorkshopJob.stage != 'Finished').count()
    
    # Count pending quotes
    pending_quotes = Quote.query.filter(Quote.status.in_(['Not Sent', 'Sent', 'Negotiating'])).count()
    
    # Calculate upcoming payments (next 30 days)
    today = datetime.now().date()
    thirty_days = today + timedelta(days=30)
    upcoming_payments = Payment.query.filter(
        Payment.due_date >= today,
        Payment.due_date <= thirty_days,
        Payment.status == 'Due'
    ).all()
    upcoming_payment_total = sum(payment.amount for payment in upcoming_payments)
    
    # Count clients needing updates
    clients_needing_updates = WorkshopJob.query.filter_by(client_needs_update=True).count()
    
    return jsonify({
        'active_jobs': active_jobs,
        'pending_quotes': pending_quotes,
        'upcoming_payment_total': upcoming_payment_total,
        'clients_needing_updates': clients_needing_updates
    })

@report_bp.route('/api/reports/quote-conversion', methods=['GET'])
@login_required
def get_quote_conversion():
    """Get quote conversion statistics"""
    # Get all quotes
    quotes = Quote.query.all()
    
    # Count by status
    total = len(quotes)
    accepted = sum(1 for q in quotes if q.status in ['Accepted', 'Accepted-Negotiated'])
    rejected = sum(1 for q in quotes if q.status == 'Rejected')
    pending = sum(1 for q in quotes if q.status in ['Not Sent', 'Sent', 'Negotiating'])
    
    # Calculate conversion rate
    conversion_rate = (accepted / total * 100) if total > 0 else 0
    
    # Calculate average quote value
    avg_quote_value = sum(q.initial_quote_amount for q in quotes) / total if total > 0 else 0
    
    # Calculate average negotiation discount
    negotiated_quotes = [q for q in quotes if q.status == 'Accepted-Negotiated' and q.final_quote_amount]
    avg_discount = 0
    if negotiated_quotes:
        discounts = [(q.initial_quote_amount - q.final_quote_amount) / q.initial_quote_amount * 100 for q in negotiated_quotes]
        avg_discount = sum(discounts) / len(discounts)
    
    return jsonify({
        'total_quotes': total,
        'accepted_quotes': accepted,
        'rejected_quotes': rejected,
        'pending_quotes': pending,
        'conversion_rate': conversion_rate,
        'avg_quote_value': avg_quote_value,
        'avg_discount': avg_discount
    })

@report_bp.route('/api/reports/job-performance', methods=['GET'])
@login_required
def get_job_performance():
    """Get job performance statistics"""
    # Get completed jobs
    completed_jobs = WorkshopJob.query.filter_by(stage='Finished').all()
    
    # Calculate average build time variance
    build_variances = []
    for job in completed_jobs:
        if job.estimated_build_days and job.actual_build_days:
            variance = (job.actual_build_days - job.estimated_build_days) / job.estimated_build_days * 100
            build_variances.append(variance)
    
    avg_build_variance = sum(build_variances) / len(build_variances) if build_variances else 0
    
    # Calculate average fitting time variance
    fitting_variances = []
    for job in completed_jobs:
        if job.estimated_fitting_days and job.actual_fitting_days:
            variance = (job.actual_fitting_days - job.estimated_fitting_days) / job.estimated_fitting_days * 100
            fitting_variances.append(variance)
    
    avg_fitting_variance = sum(fitting_variances) / len(fitting_variances) if fitting_variances else 0
    
    # Calculate average job price by type
    job_types = {}
    for job in WorkshopJob.query.all():
        if job.cabinetry_type not in job_types:
            job_types[job.cabinetry_type] = []
        if job.job_price:
            job_types[job.cabinetry_type].append(job.job_price)
    
    avg_prices = {}
    for job_type, prices in job_types.items():
        avg_prices[job_type] = sum(prices) / len(prices) if prices else 0
    
    return jsonify({
        'completed_jobs': len(completed_jobs),
        'avg_build_variance': avg_build_variance,
        'avg_fitting_variance': avg_fitting_variance,
        'avg_prices_by_type': avg_prices
    })

@report_bp.route('/api/reports/staff-workload', methods=['GET'])
@login_required
def get_staff_workload():
    """Get staff workload statistics"""
    from src.models.user import User
    
    # Get all cabinet makers
    staff = User.query.filter(User.role.in_(['CabinetMaker', 'Manager'])).all()
    
    workloads = []
    for user in staff:
        # Count active job assignments
        active_assignments = 0
        for assignment in user.job_assignments:
            if assignment.job and assignment.job.stage not in ['Finished', 'Not Started']:
                active_assignments += 1
        
        # Count upcoming absences
        today = datetime.now().date()
        upcoming_absences = sum(1 for absence in user.absences if absence.end_date >= today)
        
        workloads.append({
            'user_id': user.id,
            'name': user.full_name,
            'role': user.role,
            'active_assignments': active_assignments,
            'upcoming_absences': upcoming_absences
        })
    
    return jsonify(workloads)

@report_bp.route('/api/reports/clients-needing-updates', methods=['GET'])
@login_required
def get_clients_needing_updates():
    """Get list of clients that need updates"""
    jobs = WorkshopJob.query.filter_by(client_needs_update=True).all()
    
    clients = []
    for job in jobs:
        clients.append({
            'job_id': job.id,
            'job_name': job.name,
            'client_id': job.client_id,
            'client_name': job.client.name if job.client else '',
            'fitting_date': job.fitting_date.isoformat() if job.fitting_date else None,
            'fitting_date_status': job.fitting_date_status
        })
    
    return jsonify(clients)
