from flask import Flask, render_template, send_from_directory, redirect, url_for, session
from models import db
from profile import profile_bp
from login import login_bp
import os
import secrets
from flask_cors import CORS
from functools import wraps


app = Flask(__name__, 
    static_folder='static',
    template_folder='templates')
CORS(app)
# Database configuration
db_role = os.getenv('DB_ROLE', 'admin')

if db_role == 'employee':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://employee:employee@db:3306/employee_management_system'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:mthree@db:3306/employee_management_system'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize the database
db.init_app(app)

# Register blueprints
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(login_bp, url_prefix='/login')

# Ensure the user is authenticated to access certain routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Route handlers for HTML pages
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard_page():
    
    permission = session.get('permission')
    if permission == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('employee_dashboard.html')

@app.route('/dashboard/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@login_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear session data
    return jsonify({'message': 'Logout successful'})

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    employee_name = session.get('employee_name')
    permission = session.get('permission')
    
    return render_template('dashboard.html', employee_name=employee_name, permission=permission)








if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
