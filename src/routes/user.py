from flask import Blueprint, request, jsonify
from src.models import db
from src.models.user import User
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__)

@user_bp.route('/health', methods=['GET'])
@login_required
def health_check():
    """Health check endpoint to verify authentication status"""
    return jsonify({
        'status': 'authenticated',
        'user': current_user.to_dict() if current_user.is_authenticated else None
    })

@user_bp.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username
    user = User.query.filter_by(username=data['username']).first()
    
    # Check if user exists and password is correct
    if user and user.verify_password(data['password']):
        login_user(user)
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        })
    
    return jsonify({'error': 'Invalid username or password'}), 401

@user_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return jsonify({'message': 'Logout successful'})

@user_bp.route('/', methods=['GET'])
@login_required
def get_users():
    """Get all users (requires admin privileges)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
        
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get a specific user"""
    # Allow users to view their own profile or admins to view any profile
    if current_user.id != user_id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
        
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/', methods=['POST'])
@login_required
def create_user():
    """Create a new user (requires admin privileges)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
        
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data['role']
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(new_user.to_dict()), 201

@user_bp.route('/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update a user"""
    # Allow users to update their own profile or admins to update any profile
    if current_user.id != user_id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
        
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Update fields
    if 'email' in data:
        # Check if email already exists for another user
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
        
    if 'first_name' in data:
        user.first_name = data['first_name']
        
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    # Only admins can change roles
    if 'role' in data and current_user.role == 'admin':
        user.role = data['role']
    
    # Update password if provided
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete a user (requires admin privileges)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
        
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the last admin
    if user.role == 'admin' and User.query.filter_by(role='admin').count() <= 1:
        return jsonify({'error': 'Cannot delete the last admin user'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'})
