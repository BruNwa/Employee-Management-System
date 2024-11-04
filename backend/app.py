from flask import Flask, render_template, send_from_directory, redirect, url_for, session, jsonify
from models import db, Employee, Leave, Performance, LeaveType, KPI, Goal, Achievement, Attendance, Payroll, Payment, Role, Department, LeaveBalance
from profile import profile_bp
from login import login_bp
from crud import crud_bp
from performance import performance_bp
from leaves import lb
from attendance import ab
from payslip import payment_bp
import os
import secrets
from flask_cors import CORS
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from role import role_bp

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates')
CORS(app)

# Database configuration
db_role = os.getenv('DB_ROLE', 'admin')

if db_role == 'employee':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://employee:Mthree&&C402@172.20.0.11:3306/employee_management_system'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Mthree&C402@172.20.0.11:3306/employee_management_system'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize the database
db.init_app(app)

# Register blueprints
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(performance_bp, url_prefix='/performance')
app.register_blueprint(crud_bp, url_prefix='/crud')
app.register_blueprint(ab,url_prefix='/attendance')
app.register_blueprint(lb, url_prefix='/leaves')
app.register_blueprint(role_bp)
app.register_blueprint(payment_bp,url_prefix='/payslip')

# Ensure the user is authenticated to access certain routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

#Route handlers for HTML pages
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard_page():
    
    permission = session.get('permission')
    if permission == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('employee_dashboard.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    departments = Department.query.all()
    roles = Role.query.all()
    return render_template('admin_dashboard.html',departments=departments, roles=roles)

@login_bp.route('login/logout', methods=['POST'])
def logout():
    app.logger.info(f"User {session.get('employee_id')} logged out")
    session.clear()
    return jsonify({'message': 'Logout successful'})

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    employee_name = session.get('employee_name')
    permission = session.get('permission')
    
    return render_template('emp_dashboard.html', employee_name=employee_name, permission=permission)



# @app.route('/admin/dashboard')
# def payroll_dashboard():
#     return render_template('payroll.html')




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
