from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.staff_absence import StaffAbsence
from datetime import datetime, timedelta
from flask_login import login_required, current_user

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/api/staff', methods=['GET'])
@login_required
def get_staff():
    """Get all staff members"""
    staff = User.query.filter(User.role.in_(['CabinetMaker', 'Manager'])).all()
    return jsonify([user.to_dict() for user in staff])

@staff_bp.route('/api/staff/<int:user_id>', methods=['GET'])
@login_required
def get_staff_member(user_id):
    """Get a specific staff member"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@staff_bp.route('/api/staff/<int:user_id>/schedule', methods=['GET'])
@login_required
def get_staff_schedule(user_id):
    """Get schedule for a staff member"""
    user = User.query.get_or_404(user_id)
    
    # Get start and end dates for the next 30 days
    today = datetime.now().date()
    end_date = today + timedelta(days=30)
    
    # Get all job assignments for this user
    assignments = []
    for assignment in user.job_assignments:
        job = assignment.job
        if not job:
            continue
            
        if assignment.role == 'Build Team' and job.build_start_date:
            build_end = job.build_start_date + timedelta(days=job.build_duration_days or job.estimated_build_days or 7)
            
            # Only include if build period overlaps with next 30 days
            if job.build_start_date <= end_date and build_end >= today:
                assignments.append({
                    'job_id': job.id,
                    'job_name': job.name,
                    'client_name': job.client.name if job.client else '',
                    'start_date': job.build_start_date.isoformat(),
                    'end_date': build_end.isoformat(),
                    'role': 'Build Team',
                    'stage': 'Build'
                })
                
        if assignment.role == 'Fit Team' and job.fitting_date:
            fit_end = job.fitting_date + timedelta(days=job.estimated_fitting_days or 3)
            
            # Only include if fitting period overlaps with next 30 days
            if job.fitting_date <= end_date and fit_end >= today:
                assignments.append({
                    'job_id': job.id,
                    'job_name': job.name,
                    'client_name': job.client.name if job.client else '',
                    'start_date': job.fitting_date.isoformat(),
                    'end_date': fit_end.isoformat(),
                    'role': 'Fit Team',
                    'stage': 'Fit'
                })
    
    # Get all absences for this user
    absences = []
    for absence in user.absences:
        # Only include if absence period overlaps with next 30 days
        if absence.start_date <= end_date and absence.end_date >= today:
            absences.append({
                'id': absence.id,
                'start_date': absence.start_date.isoformat(),
                'end_date': absence.end_date.isoformat(),
                'type': absence.type,
                'notes': absence.notes
            })
    
    return jsonify({
        'assignments': assignments,
        'absences': absences
    })

@staff_bp.route('/api/staff/<int:user_id>/absences', methods=['GET'])
@login_required
def get_staff_absences(user_id):
    """Get absences for a staff member"""
    user = User.query.get_or_404(user_id)
    return jsonify([absence.to_dict() for absence in user.absences])

@staff_bp.route('/api/staff/<int:user_id>/absences', methods=['POST'])
@login_required
def create_staff_absence(user_id):
    """Create a new absence for a staff member"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    # Check for overlapping absences
    for absence in user.absences:
        if absence.overlaps_with_dates(start_date, end_date):
            return jsonify({'error': 'Absence overlaps with existing absence'}), 400
    
    # Check for job assignments during this period
    for assignment in user.job_assignments:
        job = assignment.job
        if not job:
            continue
            
        if assignment.role == 'Build Team' and job.build_start_date:
            build_end = job.build_start_date + timedelta(days=job.build_duration_days or job.estimated_build_days or 7)
            
            if job.build_start_date <= end_date and build_end >= start_date:
                return jsonify({
                    'error': 'Staff member is assigned to build team during this period',
                    'job_name': job.name,
                    'build_start': job.build_start_date.isoformat(),
                    'build_end': build_end.isoformat()
                }), 400
                
        if assignment.role == 'Fit Team' and job.fitting_date:
            fit_end = job.fitting_date + timedelta(days=job.estimated_fitting_days or 3)
            
            if job.fitting_date <= end_date and fit_end >= start_date:
                return jsonify({
                    'error': 'Staff member is assigned to fit team during this period',
                    'job_name': job.name,
                    'fit_start': job.fitting_date.isoformat(),
                    'fit_end': fit_end.isoformat()
                }), 400
    
    absence = StaffAbsence(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        type=data['type'],
        notes=data.get('notes')
    )
    
    db.session.add(absence)
    db.session.commit()
    return jsonify(absence.to_dict()), 201

@staff_bp.route('/api/staff/<int:user_id>/absences/<int:absence_id>', methods=['PUT'])
@login_required
def update_staff_absence(user_id, absence_id):
    """Update an absence for a staff member"""
    absence = StaffAbsence.query.get_or_404(absence_id)
    if absence.user_id != user_id:
        return jsonify({'error': 'Absence does not belong to this staff member'}), 400
    
    data = request.json
    
    if 'start_date' in data or 'end_date' in data:
        start_date = datetime.strptime(data.get('start_date', absence.start_date.isoformat()), '%Y-%m-%d').date()
        end_date = datetime.strptime(data.get('end_date', absence.end_date.isoformat()), '%Y-%m-%d').date()
        
        # Check for overlapping absences (excluding this one)
        for other_absence in absence.user.absences:
            if other_absence.id != absence.id and other_absence.overlaps_with_dates(start_date, end_date):
                return jsonify({'error': 'Absence overlaps with existing absence'}), 400
        
        # Check for job assignments during this period
        for assignment in absence.user.job_assignments:
            job = assignment.job
            if not job:
                continue
                
            if assignment.role == 'Build Team' and job.build_start_date:
                build_end = job.build_start_date + timedelta(days=job.build_duration_days or job.estimated_build_days or 7)
                
                if job.build_start_date <= end_date and build_end >= start_date:
                    return jsonify({
                        'error': 'Staff member is assigned to build team during this period',
                        'job_name': job.name,
                        'build_start': job.build_start_date.isoformat(),
                        'build_end': build_end.isoformat()
                    }), 400
                    
            if assignment.role == 'Fit Team' and job.fitting_date:
                fit_end = job.fitting_date + timedelta(days=job.estimated_fitting_days or 3)
                
                if job.fitting_date <= end_date and fit_end >= start_date:
                    return jsonify({
                        'error': 'Staff member is assigned to fit team during this period',
                        'job_name': job.name,
                        'fit_start': job.fitting_date.isoformat(),
                        'fit_end': fit_end.isoformat()
                    }), 400
        
        absence.start_date = start_date
        absence.end_date = end_date
    
    if 'type' in data:
        absence.type = data['type']
    if 'notes' in data:
        absence.notes = data['notes']
    
    db.session.commit()
    return jsonify(absence.to_dict())

@staff_bp.route('/api/staff/<int:user_id>/absences/<int:absence_id>', methods=['DELETE'])
@login_required
def delete_staff_absence(user_id, absence_id):
    """Delete an absence for a staff member"""
    absence = StaffAbsence.query.get_or_404(absence_id)
    if absence.user_id != user_id:
        return jsonify({'error': 'Absence does not belong to this staff member'}), 400
    
    db.session.delete(absence)
    db.session.commit()
    return '', 204

@staff_bp.route('/api/staff/availability', methods=['GET'])
@login_required
def get_staff_availability():
    """Get availability for all staff members"""
    # Get start and end dates from query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if not start_date_str or not end_date_str:
        return jsonify({'error': 'Start date and end date are required'}), 400
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    # Get all staff members
    staff = User.query.filter(User.role.in_(['CabinetMaker', 'Manager'])).all()
    
    availability = []
    for user in staff:
        # Check if user has any absences during this period
        has_absence = False
        for absence in user.absences:
            if absence.overlaps_with_dates(start_date, end_date):
                has_absence = True
                break
        
        # Check if user has any job assignments during this period
        assignments = []
        for assignment in user.job_assignments:
            job = assignment.job
            if not job:
                continue
                
            if assignment.role == 'Build Team' and job.build_start_date:
                build_end = job.build_start_date + timedelta(days=job.build_duration_days or job.estimated_build_days or 7)
                
                if job.build_start_date <= end_date and build_end >= start_date:
                    assignments.append({
                        'job_id': job.id,
                        'job_name': job.name,
                        'start_date': job.build_start_date.isoformat(),
                        'end_date': build_end.isoformat(),
                        'role': 'Build Team'
                    })
                    
            if assignment.role == 'Fit Team' and job.fitting_date:
                fit_end = job.fitting_date + timedelta(days=job.estimated_fitting_days or 3)
                
                if job.fitting_date <= end_date and fit_end >= start_date:
                    assignments.append({
                        'job_id': job.id,
                        'job_name': job.name,
                        'start_date': job.fitting_date.isoformat(),
                        'end_date': fit_end.isoformat(),
                        'role': 'Fit Team'
                    })
        
        availability.append({
            'user_id': user.id,
            'name': user.full_name,
            'role': user.role,
            'available': not has_absence,
            'assignments': assignments,
            'workload': len(assignments)
        })
    
    return jsonify(availability)
