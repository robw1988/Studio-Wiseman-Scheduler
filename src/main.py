import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, send_from_directory, jsonify, session
from flask_login import LoginManager, current_user, login_user
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from src.models import db
from src.models.user import User
from src.routes.user import user_bp
from src.routes.client import client_bp
from src.routes.quote import quote_bp
from src.routes.job import job_bp
from src.routes.staff import staff_bp
from src.routes.payment import payment_bp
from src.routes.report import report_bp

app = Flask(__name__, 
             static_folder='static',
             static_url_path='/static')

# Apply ProxyFix to handle proxy headers from Railway
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
             
# Enable CORS with credentials support
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Enable debug mode
app.debug = True

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cabinetry_scheduler.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = None  # Changed from 'Lax' to None for cross-domain cookies
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours in seconds
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem session for better persistence
app.config['SESSION_COOKIE_NAME'] = 'cabinetry_session'  # Custom session name
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow the browser to set this automatically

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None  # Disable automatic redirects
login_manager.session_protection = None  # Disable session protection temporarily for debugging

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized access", "login_required": True}), 401

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(client_bp, url_prefix='/api/clients')
app.register_blueprint(quote_bp, url_prefix='/api/quotes')
app.register_blueprint(job_bp, url_prefix='/api/jobs')
app.register_blueprint(staff_bp, url_prefix='/api/staff')
app.register_blueprint(payment_bp, url_prefix='/api/payments')
app.register_blueprint(report_bp, url_prefix='/api/reports')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modified login route in user_bp to set session cookie flags
@app.route('/api/users/login-test', methods=['POST'])
def login_test():
    """Test login endpoint with explicit session handling"""
    from flask import request
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.verify_password(data['password']):
        # Set remember=True for persistent session
        login_user(user, remember=True)
        
        # Set additional session variables
        session['user_id'] = user.id
        session['authenticated'] = True
        session.permanent = True
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'session_id': session.sid if hasattr(session, 'sid') else 'session_active'
        })
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/login')
def login():
    # This route should not require authentication
    return send_from_directory('static', 'index.html')

@app.route('/test')
def test():
    return jsonify({"status": "ok", "message": "Test route is working"})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/session-debug')
def session_debug():
    """Debug endpoint to check session state"""
    return jsonify({
        'user_authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'session_vars': {key: session[key] for key in session if key != '_flashes'},
        'session_cookie_config': {
            'secure': app.config['SESSION_COOKIE_SECURE'],
            'httponly': app.config['SESSION_COOKIE_HTTPONLY'],
            'samesite': app.config['SESSION_COOKIE_SAMESITE'],
            'domain': app.config['SESSION_COOKIE_DOMAIN'],
            'name': app.config['SESSION_COOKIE_NAME']
        }
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"500 error: {str(e)}")
    return jsonify({'error': f'Server error: {str(e)}'}), 500

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@studiowiseman.com',
            first_name='Admin',
            last_name='User',
            role='Admin'
        )
        admin.password = 'admin123'  # This will be hashed
        db.session.add(admin)
        
        # Create some staff users
        staff1 = User(
            username='james',
            email='james@studiowiseman.com',
            first_name='James',
            last_name='Wilson',
            role='CabinetMaker'
        )
        staff1.password = 'password'
        
        staff2 = User(
            username='robert',
            email='robert@studiowiseman.com',
            first_name='Robert',
            last_name='Johnson',
            role='CabinetMaker'
        )
        staff2.password = 'password'
        
        staff3 = User(
            username='william',
            email='william@studiowiseman.com',
            first_name='William',
            last_name='Davis',
            role='CabinetMaker'
        )
        staff3.password = 'password'
        
        db.session.add_all([staff1, staff2, staff3])
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
