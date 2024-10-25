from flask import Blueprint, request, jsonify, session
from models import db, Employee, Role
from functools import wraps

login_bp = Blueprint('login', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated_function

def check_role_permission(employee_id):
    employee = Employee.query.join(Role).filter(Employee.employee_id == employee_id).first()
    if not employee or not employee.role:
        return None
    
    admin_roles = ['Manager', 'Team Lead']
    employee_roles = ['Senior Developer', 'Junior Developer', 'Intern']
    
    if employee.role.role_name in admin_roles:
        return 'admin'
    elif employee.role.role_name in employee_roles:
        return 'employee'
    return None


@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'phone' not in data:
        return jsonify({'error': 'Email and phone number required'}), 400
    
    try:
        employee = Employee.query.filter_by(
            email=data['email'].lower(),
            phone=data['phone']
        ).first()
        
        if not employee:
            return jsonify({'error': 'Invalid credentials'}), 401
        

        permission = check_role_permission(employee.employee_id)
        if not permission:
            return jsonify({'error': 'Unauthorized role'}), 403
        

        session['employee_id'] = employee.employee_id
        session['permission'] = permission
        
        return jsonify({
            'message': 'Login successful',
            'employee_id': employee.employee_id,
            'permission': permission,
            'name': f"{employee.first_name} {employee.last_name}"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@login_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()  
    return jsonify({'message': 'Logout successful'})

@login_bp.route('/check-auth', methods=['GET'])
@login_required
def check_auth():
    return jsonify({
        'authenticated': True,
        'employee_id': session.get('employee_id'),
        'permission': session.get('permission')
    })