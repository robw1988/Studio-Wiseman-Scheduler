from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.quote import Quote, QuoteExtra
from src.models.job import WorkshopJob
from datetime import datetime
from flask_login import login_required, current_user

quote_bp = Blueprint('quote', __name__)

@quote_bp.route('/api/quotes', methods=['GET'])
@login_required
def get_quotes():
    """Get all quotes"""
    quotes = Quote.query.all()
    return jsonify([quote.to_dict() for quote in quotes])

@quote_bp.route('/api/quotes/<int:quote_id>', methods=['GET'])
@login_required
def get_quote(quote_id):
    """Get a specific quote"""
    quote = Quote.query.get_or_404(quote_id)
    return jsonify(quote.to_dict())

@quote_bp.route('/api/quotes', methods=['POST'])
@login_required
def create_quote():
    """Create a new quote"""
    data = request.json
    
    quote = Quote(
        name=data['name'],
        client_id=data['client_id'],
        cabinetry_type=data['cabinetry_type'],
        initial_quote_amount=data['initial_quote_amount'],
        final_quote_amount=data.get('final_quote_amount'),
        material_costs=data.get('material_costs'),
        status=data.get('status', 'Not Sent'),
        negotiation_details=data.get('negotiation_details'),
        deposit_paid_date=datetime.strptime(data['deposit_paid_date'], '%Y-%m-%d').date() if data.get('deposit_paid_date') else None,
        estimated_build_days=data.get('estimated_build_days'),
        estimated_fitting_days=data.get('estimated_fitting_days'),
        created_by=current_user.id
    )
    
    db.session.add(quote)
    db.session.commit()
    
    # Add extras if provided
    if 'extras' in data:
        for extra_data in data['extras']:
            extra = QuoteExtra(
                quote_id=quote.id,
                description=extra_data['description'],
                price=extra_data['price']
            )
            db.session.add(extra)
        db.session.commit()
    
    return jsonify(quote.to_dict()), 201

@quote_bp.route('/api/quotes/<int:quote_id>', methods=['PUT'])
@login_required
def update_quote(quote_id):
    """Update a quote"""
    quote = Quote.query.get_or_404(quote_id)
    data = request.json
    
    # Update basic fields
    if 'name' in data:
        quote.name = data['name']
    if 'cabinetry_type' in data:
        quote.cabinetry_type = data['cabinetry_type']
    if 'initial_quote_amount' in data:
        quote.initial_quote_amount = data['initial_quote_amount']
    if 'final_quote_amount' in data:
        quote.final_quote_amount = data['final_quote_amount']
    if 'material_costs' in data:
        quote.material_costs = data['material_costs']
    if 'status' in data:
        quote.status = data['status']
    if 'negotiation_details' in data:
        quote.negotiation_details = data['negotiation_details']
    if 'deposit_paid_date' in data:
        quote.deposit_paid_date = datetime.strptime(data['deposit_paid_date'], '%Y-%m-%d').date() if data['deposit_paid_date'] else None
    if 'estimated_build_days' in data:
        quote.estimated_build_days = data['estimated_build_days']
    if 'estimated_fitting_days' in data:
        quote.estimated_fitting_days = data['estimated_fitting_days']
    
    db.session.commit()
    
    # Update extras if provided
    if 'extras' in data:
        # Delete existing extras
        for extra in quote.extras:
            db.session.delete(extra)
        
        # Add new extras
        for extra_data in data['extras']:
            extra = QuoteExtra(
                quote_id=quote.id,
                description=extra_data['description'],
                price=extra_data['price']
            )
            db.session.add(extra)
        
        db.session.commit()
    
    return jsonify(quote.to_dict())

@quote_bp.route('/api/quotes/<int:quote_id>', methods=['DELETE'])
@login_required
def delete_quote(quote_id):
    """Delete a quote"""
    quote = Quote.query.get_or_404(quote_id)
    
    # Check if quote has been converted to job
    if quote.job:
        return jsonify({'error': 'Cannot delete quote that has been converted to job'}), 400
    
    db.session.delete(quote)
    db.session.commit()
    return '', 204

@quote_bp.route('/api/quotes/<int:quote_id>/convert-to-job', methods=['POST'])
@login_required
def convert_quote_to_job(quote_id):
    """Convert a quote to a workshop job"""
    quote = Quote.query.get_or_404(quote_id)
    
    # Check if quote is already converted
    if quote.job:
        return jsonify({'error': 'Quote already converted to job'}), 400
    
    # Check if quote is accepted
    if quote.status not in ['Accepted', 'Accepted-Negotiated']:
        return jsonify({'error': 'Cannot convert quote to job: quote is not accepted'}), 400
    
    # Convert quote to job
    job = quote.convert_to_job()
    
    # Generate payment schedule
    job.generate_payment_schedule()
    
    return jsonify(job.to_dict()), 201

@quote_bp.route('/api/quotes/<int:quote_id>/extras', methods=['GET'])
@login_required
def get_quote_extras(quote_id):
    """Get extras for a quote"""
    quote = Quote.query.get_or_404(quote_id)
    return jsonify([extra.to_dict() for extra in quote.extras])

@quote_bp.route('/api/quotes/<int:quote_id>/extras', methods=['POST'])
@login_required
def add_quote_extra(quote_id):
    """Add an extra to a quote"""
    quote = Quote.query.get_or_404(quote_id)
    data = request.json
    
    extra = QuoteExtra(
        quote_id=quote_id,
        description=data['description'],
        price=data['price']
    )
    
    db.session.add(extra)
    db.session.commit()
    return jsonify(extra.to_dict()), 201

@quote_bp.route('/api/quotes/<int:quote_id>/extras/<int:extra_id>', methods=['PUT'])
@login_required
def update_quote_extra(quote_id, extra_id):
    """Update a quote extra"""
    extra = QuoteExtra.query.get_or_404(extra_id)
    if extra.quote_id != quote_id:
        return jsonify({'error': 'Extra does not belong to this quote'}), 400
    
    data = request.json
    
    if 'description' in data:
        extra.description = data['description']
    if 'price' in data:
        extra.price = data['price']
    
    db.session.commit()
    return jsonify(extra.to_dict())

@quote_bp.route('/api/quotes/<int:quote_id>/extras/<int:extra_id>', methods=['DELETE'])
@login_required
def delete_quote_extra(quote_id, extra_id):
    """Delete a quote extra"""
    extra = QuoteExtra.query.get_or_404(extra_id)
    if extra.quote_id != quote_id:
        return jsonify({'error': 'Extra does not belong to this quote'}), 400
    
    db.session.delete(extra)
    db.session.commit()
    return '', 204

@quote_bp.route('/api/quotes/stats', methods=['GET'])
@login_required
def get_quote_stats():
    """Get quote statistics"""
    total_quotes = Quote.query.count()
    accepted_quotes = Quote.query.filter(Quote.status.in_(['Accepted', 'Accepted-Negotiated'])).count()
    rejected_quotes = Quote.query.filter_by(status='Rejected').count()
    pending_quotes = Quote.query.filter(Quote.status.in_(['Not Sent', 'Sent', 'Negotiating'])).count()
    
    conversion_rate = (accepted_quotes / total_quotes) * 100 if total_quotes > 0 else 0
    
    return jsonify({
        'total_quotes': total_quotes,
        'accepted_quotes': accepted_quotes,
        'rejected_quotes': rejected_quotes,
        'pending_quotes': pending_quotes,
        'conversion_rate': conversion_rate
    })
