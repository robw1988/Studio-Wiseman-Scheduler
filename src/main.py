import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, send_from_directory, jsonify
from flask_login import LoginManager, current_user
from flask_cors import CORS
from src.models.user import db, User
from src.routes.user import user_bp
from src.routes.client import client_bp
from src.routes.quote import quote_bp
from src.routes.job import job_bp
from src.routes.staff import staff_bp
from src.routes.payment import payment_bp
from src.routes.report import report_bp

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cabinetry_scheduler.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(client_bp)
app.register_blueprint(quote_bp)
app.register_blueprint(job_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(report_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok'})

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

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
