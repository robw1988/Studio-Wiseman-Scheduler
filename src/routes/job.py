from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.job import WorkshopJob
from src.models.job_assignment import JobAssignment
from src.models.staff_absence import StaffAbsence
from datetime import datetime, timedelta
from flask_login import login_required, current_user
import json

job_bp = Blueprint('job', __name__)

@job_bp.route('/api/jobs', methods=['GET'])
@login_required
def get_jobs():
    """Get all workshop jobs"""
    jobs = WorkshopJob.query.all()
    return jsonify([job.to_dict() for job in jobs])

@job_bp.route('/api/jobs/<int:job_id>', methods=['GET'])
@login_required
def get_job(job_id):
    """Get a specific workshop job"""
    job = WorkshopJob.query.get_or_404(job_id)
    return jsonify(job.to_dict())

@job_bp.route('/api/jobs', methods=['POST'])
@login_required
def create_job():
    """Create a new workshop job"""
    data = request.json
    
    job = WorkshopJob(
        name=data['name'],
        client_id=data['client_id'],
        quote_id=data.get('quote_id'),
        cabinetry_type=data['cabinetry_type'],
        build_start_date=datetime.strptime(data['build_start_date'], '%Y-%m-%d').date() if data.get('build_start_date') else None,
        build_duration_days=data.get('build_duration_days'),
        stage=data.get('stage', 'Not Started'),
        estimated_build_days=data.get('estimated_build_days'),
        estimated_fitting_days=data.get('estimated_fitting_days'),
        fitting_date=datetime.strptime(data['fitting_date'], '%Y-%m-%d').date() if data.get('fitting_date') else None,
        job_price=data.get('job_price')
    )
    
    db.session.add(job)
    db.session.commit()
    
    # Generate payment schedule if job price is provided
    if job.job_price:
        job.generate_payment_schedule()
    
    return jsonify(job.to_dict()), 201

@job_bp.route('/api/jobs/<int:job_id>', methods=['PUT'])
@login_required
def update_job(job_id):
    """Update a workshop job"""
    job = WorkshopJob.query.get_or_404(job_id)
    data = request.json
    
    # Update basic fields
    if 'name' in data:
        job.name = data['name']
    if 'cabinetry_type' in data:
        job.cabinetry_type = data['cabinetry_type']
    if 'build_start_date' in data:
        job.build_start_date = datetime.strptime(data['build_start_date'], '%Y-%m-%d').date() if data['build_start_date'] else None
    if 'build_duration_days' in data:
        job.build_duration_days = data['build_duration_days']
    if 'stage' in data:
        job.stage = data['stage']
    if 'actual_build_days' in data:
        job.actual_build_days = data['actual_build_days']
    if 'actual_fitting_days' in data:
        job.actual_fitting_days = data['actual_fitting_days']
    if 'fitting_date' in data:
        old_fitting_date = job.fitting_date
        job.fitting_date = datetime.strptime(data['fitting_date'], '%Y-%m-%d').date() if data['fitting_date'] else None
        
        # Flag client for update if fitting date changed
        if old_fitting_date != job.fitting_date:
            job.client_needs_update = True
            job.client_contacted = False
    
    if 'fitting_date_status' in data:
        job.fitting_date_status = data['fitting_date_status']
    if 'job_price' in data:
        job.job_price = data['job_price']
        # Regenerate payment schedule if price changed
        job.generate_payment_schedule()
    if 'client_contacted' in data:
        job.client_contacted = data['client_contacted']
        if data['client_contacted']:
            job.client_needs_update = False
    
    db.session.commit()
    return jsonify(job.to_dict())

@job_bp.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@login_required
def delete_job(job_id):
    """Delete a workshop job"""
    job = WorkshopJob.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return '', 204

@job_bp.route('/api/jobs/<int:job_id>/status', methods=['PUT'])
@login_required
def update_job_status(job_id):
    """Update a job's stage"""
    job = WorkshopJob.query.get_or_404(job_id)
    data = request.json
    
    if 'stage' in data:
        job.stage = data['stage']
        
        # If moving to Fit stage, ensure build is complete
        if job.stage == 'Fit' and job.build_start_date:
            job.actual_build_days = (datetime.now().date() - job.build_start_date).days
        
        # If job is finished, update completion payment due date
        if job.stage == 'Finished':
            for payment in job.payments:
                if payment.type == 'Completion':
                    payment.due_date = datetime.now().date()
                    db.session.commit()
    
    db.session.commit()
    return jsonify(job.to_dict())

@job_bp.route('/api/jobs/schedule', methods=['GET'])
@login_required
def get_job_schedule():
    """Get job schedule data for Gantt view"""
    jobs = WorkshopJob.query.filter(WorkshopJob.stage != 'Finished').all()
    
    schedule_data = []
    for job in jobs:
        if not job.build_start_date:
            continue
            
        # Calculate dates for each stage
        build_start = job.build_start_date
        build_end = build_start + timedelta(days=job.build_duration_days or job.estimated_build_days or 7)
        
        # Spray starts on the last day of build and lasts 5 days
        spray_start = build_end - timedelta(days=1)
        spray_end = spray_start + timedelta(days=5)
        
        # Fit starts after spray is complete
        fit_start = job.fitting_date or (spray_end + timedelta(days=1))
        fit_end = fit_start + timedelta(days=job.estimated_fitting_days or 3)
        
        job_data = {
            'id': job.id,
            'name': job.name,
            'client': job.client.name if job.client else '',
            'stages': [
                {
                    'name': 'Build',
                    'start': build_start.isoformat(),
                    'end': build_end.isoformat(),
                    'progress': 100 if job.stage in ['Spray', 'Fit', 'Snag', 'Finished'] else (
                        50 if job.stage == 'Build' else 0
                    )
                },
                {
                    'name': 'Spray',
                    'start': spray_start.isoformat(),
                    'end': spray_end.isoformat(),
                    'progress': 100 if job.stage in ['Fit', 'Snag', 'Finished'] else (
                        50 if job.stage == 'Spray' else 0
                    )
                },
                {
                    'name': 'Fit',
                    'start': fit_start.isoformat(),
                    'end': fit_end.isoformat(),
                    'progress': 100 if job.stage in ['Snag', 'Finished'] else (
                        50 if job.stage == 'Fit' else 0
                    )
                }
            ]
        }
        
        # Add snag stage if job is in snag
        if job.stage == 'Snag':
            job_data['stages'].append({
                'name': 'Snag',
                'start': fit_end.isoformat(),
                'end': (fit_end + timedelta(days=2)).isoformat(),
                'progress': 50
            })
        
        schedule_data.append(job_data)
    
    return jsonify(schedule_data)

@job_bp.route('/api/jobs/<int:job_id>/reschedule', methods=['PUT'])
@login_required
def reschedule_job(job_id):
    """Reschedule a job (drag and drop in Gantt view)"""
    job = WorkshopJob.query.get_or_404(job_id)
    data = request.json
    
    if 'build_start_date' in data:
        job.build_start_date = datetime.strptime(data['build_start_date'], '%Y-%m-%d').date()
    
    if 'fitting_date' in data:
        old_fitting_date = job.fitting_date
        job.fitting_date = datetime.strptime(data['fitting_date'], '%Y-%m-%d').date()
        
        # Flag client for update if fitting date changed
        if old_fitting_date != job.fitting_date:
            job.client_needs_update = True
            job.client_contacted = False
    
    db.session.commit()
    
    # Update payment due dates
    for payment in job.payments:
        if payment.type == 'Build Installment':
            payment.due_date = job.build_start_date
        elif payment.type in ['Fitting Installment', 'Completion']:
            payment.due_date = job.fitting_date
    
    db.session.commit()
    return jsonify(job.to_dict())

@job_bp.route('/api/jobs/<int:job_id>/assignments', methods=['GET'])
@login_required
def get_job_assignments(job_id):
    """Get staff assignments for a job"""
    job = WorkshopJob.query.get_or_404(job_id)
    return jsonify([assignment.to_dict() for assignment in job.assignments])

@job_bp.route('/api/jobs/<int:job_id>/assignments', methods=['POST'])
@login_required
def create_job_assignment(job_id):
    """Assign staff to a job"""
    job = WorkshopJob.query.get_or_404(job_id)
    data = request.json
    
    # Check if user is available during job dates
    user = User.query.get_or_404(data['user_id'])
    
    if data['role'] == 'Build Team' and job.build_start_date:
        build_end = job.build_start_date + timedelta(days=job.build_duration_days or job.estimated_build_days or 7)
        if not user.is_available(job.build_start_date, build_end):
            return jsonify({'error': 'User is not available during build dates'}), 400
    
    if data['role'] == 'Fit Team' and job.fitting_date:
        fit_end = job.fitting_date + timedelta(days=job.estimated_fitting_days or 3)
        if not user.is_available(job.fitting_date, fit_end):
            return jsonify({'error': 'User is not available during fitting dates'}), 400
    
    assignment = JobAssignment(
        job_id=job_id,
        user_id=data['user_id'],
        role=data['role']
    )
    
    db.session.add(assignment)
    db.session.commit()
    return jsonify(assignment.to_dict()), 201

@job_bp.route('/api/jobs/<int:job_id>/assignments/<int:assignment_id>', methods=['DELETE'])
@login_required
def delete_job_assignment(job_id, assignment_id):
    """Remove staff from a job"""
    assignment = JobAssignment.query.get_or_404(assignment_id)
    if assignment.job_id != job_id:
        return jsonify({'error': 'Assignment does not belong to this job'}), 400
    
    db.session.delete(assignment)
    db.session.commit()
    return '', 204

@job_bp.route('/api/jobs/<int:job_id>/auto-assign', methods=['POST'])
@login_required
def auto_assign_staff(job_id):
    """Auto-assign staff to a job based on availability and workload"""
    job = WorkshopJob.query.get_or_404(job_id)
    
    # Clear existing assignments
    for assignment in job.assignments:
        db.session.delete(assignment)
    
    # Find available staff for build team
    if job.build_start_date:
        build_end = job.build_start_date + timedelta(days=job.build_duration_days or job.estimated_build_days or 7)
        
        # Get cabinet makers
        cabinet_makers = User.query.filter_by(role='CabinetMaker').all()
        
        # Filter by availability and sort by workload
        available_builders = [
            cm for cm in cabinet_makers 
            if cm.is_available(job.build_start_date, build_end)
        ]
        available_builders.sort(key=lambda cm: cm.get_current_workload())
        
        # Assign 1-2 builders based on job size
        num_builders = 2 if (job.estimated_build_days or 0) > 10 else 1
        for i in range(min(num_builders, len(available_builders))):
            assignment = JobAssignment(
                job_id=job_id,
                user_id=available_builders[i].id,
                role='Build Team'
            )
            db.session.add(assignment)
    
    # Find available staff for fit team
    if job.fitting_date:
        fit_end = job.fitting_date + timedelta(days=job.estimated_fitting_days or 3)
        
        # Get fitters
        fitters = User.query.filter(User.role.in_(['CabinetMaker', 'Fitter'])).all()
        
        # Filter by availability and sort by workload
        available_fitters = [
            f for f in fitters 
            if f.is_available(job.fitting_date, fit_end)
        ]
        available_fitters.sort(key=lambda f: f.get_current_workload())
        
        # Assign 1 fitter
        if available_fitters:
            assignment = JobAssignment(
                job_id=job_id,
                user_id=available_fitters[0].id,
                role='Fit Team'
            )
            db.session.add(assignment)
    
    db.session.commit()
    return jsonify([assignment.to_dict() for assignment in job.assignments])

@job_bp.route('/api/jobs/weekly-calendar', methods=['GET'])
@login_required
def get_weekly_calendar():
    """Get job schedule data for weekly calendar view"""
    # Get start and end dates for the week
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Get jobs that overlap with this week
    jobs = WorkshopJob.query.filter(
        (WorkshopJob.build_start_date <= end_of_week) & 
        ((WorkshopJob.fitting_date >= start_of_week) | (WorkshopJob.build_start_date >= start_of_week))
    ).all()
    
    calendar_data = []
    for job in jobs:
        # Add build events
        if job.build_start_date:
            build_end = job.build_start_date + timedelta(days=job.build_duration_days or job.estimated_build_days or 7)
            
            # For each day in the build period that falls within this week
            current_date = max(job.build_start_date, start_of_week)
            end_date = min(build_end, end_of_week)
            
            while current_date <= end_date:
                calendar_data.append({
                    'job_id': job.id,
                    'job_name': job.name,
                    'client_name': job.client.name if job.client else '',
                    'date': current_date.isoformat(),
                    'stage': 'Build',
                    'team': [assignment.user.full_name for assignment in job.get_build_team()]
                })
                current_date += timedelta(days=1)
        
        # Add spray events
        if job.build_start_date:
            build_end = job.build_start_date + timedelta(days=job.build_duration_days or job.estimated_build_days or 7)
            spray_start = build_end - timedelta(days=1)
            spray_end = spray_start + timedelta(days=5)
            
            # For each day in the spray period that falls within this week
            current_date = max(spray_start, start_of_week)
            end_date = min(spray_end, end_of_week)
            
            while current_date <= end_date:
                calendar_data.append({
                    'job_id': job.id,
                    'job_name': job.name,
                    'client_name': job.client.name if job.client else '',
                    'date': current_date.isoformat(),
                    'stage': 'Spray',
                    'team': []  # Spray team not tracked in assignments
                })
                current_date += timedelta(days=1)
        
        # Add fit events
        if job.fitting_date:
            fit_end = job.fitting_date + timedelta(days=job.estimated_fitting_days or 3)
            
            # For each day in the fit period that falls within this week
            current_date = max(job.fitting_date, start_of_week)
            end_date = min(fit_end, end_of_week)
            
            while current_date <= end_date:
                calendar_data.append({
                    'job_id': job.id,
                    'job_name': job.name,
                    'client_name': job.client.name if job.client else '',
                    'date': current_date.isoformat(),
                    'stage': 'Fit',
                    'team': [assignment.user.full_name for assignment in job.get_fit_team()]
                })
                current_date += timedelta(days=1)
    
    return jsonify(calendar_data)

@job_bp.route('/api/jobs/clients-needing-updates', methods=['GET'])
@login_required
def get_clients_needing_updates():
    """Get list of clients that need updates"""
    jobs = WorkshopJob.query.filter_by(client_needs_update=True).all()
    return jsonify([{
        'job_id': job.id,
        'job_name': job.name,
        'client_id': job.client_id,
        'client_name': job.client.name if job.client else '',
        'fitting_date': job.fitting_date.isoformat() if job.fitting_date else None,
        'fitting_date_status': job.fitting_date_status
    } for job in jobs])
