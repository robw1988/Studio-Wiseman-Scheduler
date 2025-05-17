from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.client import Client
from flask_login import login_required, current_user
from datetime import datetime

client_bp = Blueprint('client', __name__)

@client_bp.route('/api/clients', methods=['GET'])
@login_required
def get_clients():
    """Get all clients"""
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients])

@client_bp.route('/api/clients/<int:client_id>', methods=['GET'])
@login_required
def get_client(client_id):
    """Get a specific client"""
    client = Client.query.get_or_404(client_id)
    return jsonify(client.to_dict())

@client_bp.route('/api/clients', methods=['POST'])
@login_required
def create_client():
    """Create a new client"""
    data = request.json
    
    client = Client(
        name=data['name'],
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        notes=data.get('notes')
    )
    
    db.session.add(client)
    db.session.commit()
    return jsonify(client.to_dict()), 201

@client_bp.route('/api/clients/<int:client_id>', methods=['PUT'])
@login_required
def update_client(client_id):
    """Update a client"""
    client = Client.query.get_or_404(client_id)
    data = request.json
    
    if 'name' in data:
        client.name = data['name']
    if 'email' in data:
        client.email = data['email']
    if 'phone' in data:
        client.phone = data['phone']
    if 'address' in data:
        client.address = data['address']
    if 'notes' in data:
        client.notes = data['notes']
    if 'xero_client_id' in data:
        client.xero_client_id = data['xero_client_id']
    
    db.session.commit()
    return jsonify(client.to_dict())

@client_bp.route('/api/clients/<int:client_id>', methods=['DELETE'])
@login_required
def delete_client(client_id):
    """Delete a client"""
    client = Client.query.get_or_404(client_id)
    
    # Check if client has quotes or jobs
    if client.quotes.count() > 0 or client.jobs.count() > 0:
        return jsonify({'error': 'Cannot delete client with associated quotes or jobs'}), 400
    
    db.session.delete(client)
    db.session.commit()
    return '', 204

@client_bp.route('/api/clients/<int:client_id>/quotes', methods=['GET'])
@login_required
def get_client_quotes(client_id):
    """Get quotes for a client"""
    client = Client.query.get_or_404(client_id)
    return jsonify([quote.to_dict() for quote in client.quotes])

@client_bp.route('/api/clients/<int:client_id>/jobs', methods=['GET'])
@login_required
def get_client_jobs(client_id):
    """Get jobs for a client"""
    client = Client.query.get_or_404(client_id)
    return jsonify([job.to_dict() for job in client.jobs])

@client_bp.route('/api/clients/<int:client_id>/create-in-xero', methods=['POST'])
@login_required
def create_client_in_xero(client_id):
    """Create client in Xero"""
    client = Client.query.get_or_404(client_id)
    
    # This would be implemented when Xero integration is added
    # For now, just update the xero_client_id field with a placeholder
    client.xero_client_id = f"XERO-{client_id}-{datetime.now().strftime('%Y%m%d')}"
    db.session.commit()
    
    return jsonify({
        'message': 'Client created in Xero (simulated)',
        'xero_client_id': client.xero_client_id
    })
