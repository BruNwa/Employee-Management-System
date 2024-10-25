from flask import Blueprint, jsonify, request, session
from models import db, Employee, Leave, Performance, LeaveType, KPI, Goal, Achievement
from datetime import datetime
from functools import wraps
from sqlalchemy import desc

profile_bp = Blueprint('profile', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated_function

@profile_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    try:
        employee = Employee.query.get(session['employee_id'])
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
            
        return jsonify({
            'employee_id': employee.employee_id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'email': employee.email,
            'phone': employee.phone,
            'department': employee.department.department_name if employee.department else None,
            'role': employee.role.role_name if employee.role else None,
            'status': employee.employee_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/profile/update', methods=['PUT'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        employee = Employee.query.get(session['employee_id'])
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
            
        if 'email' in data:
            employee.email = data['email']
        if 'phone' in data:
            employee.phone = data['phone']
            
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/profile/leave-requests', methods=['GET'])
@login_required
def get_leave_requests():
    try:
        
        leaves = Leave.query.filter_by(employee_id=session['employee_id']).order_by(desc(Leave.leave_start)).all()
        
        leave_list = []
        for leave in leaves:
            leave_list.append({
                'leave_id': leave.leave_id,
                'leave_type': leave.leave_type.leave_type_name if leave.leave_type else 'N/A',
                'start_date': leave.leave_start.strftime('%Y-%m-%d'),
                'end_date': leave.leave_end.strftime('%Y-%m-%d'),
                'status': leave.leave_status,
                'approver': f"{leave.approver.first_name} {leave.approver.last_name}" if leave.approver else 'Pending'
            })
            
        return jsonify(leave_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

"""@profile_bp.route('/profile/leave-request', methods=['POST'])
@login_required
def create_leave_request():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['leave_type_id', 'start_date', 'end_date']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Create new leave request
        new_leave = Leave(
            employee_id=session['employee_id'],
            leave_type_id=data['leave_type_id'],
            leave_start=datetime.strptime(data['start_date'], '%Y-%m-%d'),
            leave_end=datetime.strptime(data['end_date'], '%Y-%m-%d'),
            leave_status='pending'
        )
        
        db.session.add(new_leave)
        db.session.commit()
        
        return jsonify({'message': 'Leave request created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500"""

@profile_bp.route('/profile/performance-reviews', methods=['GET'])
@login_required
def get_performance_reviews():
    try:
        # Get all performance reviews for the employee
        reviews = Performance.query.filter_by(employee_id=session['employee_id']).order_by(desc(Performance.review_date)).all()
        
        review_list = []
        for review in reviews:
            # Get KPIs, goals, and achievements for this review
            kpis = [{'description': kpi.kpi_description, 'score': float(kpi.kpi_score)} 
                   for kpi in review.kpis]
            goals = [{'description': goal.goal_description, 'status': goal.goal_status} 
                    for goal in review.goals]
            achievements = [{'description': ach.achievement_description, 
                           'date': ach.achievement_date.strftime('%Y-%m-%d')} 
                          for ach in review.achievements]
            
            review_list.append({
                'review_id': review.performance_id,
                'review_date': review.review_date.strftime('%Y-%m-%d'),
                'review_score': float(review.review_score),
                'reviewer': f"{review.reviewer.first_name} {review.reviewer.last_name}" if review.reviewer else 'N/A',
                'kpis': kpis,
                'goals': goals,
                'achievements': achievements
            })
            
        return jsonify(review_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/profile/leave-types', methods=['GET'])
@login_required
def get_leave_types():
    try:
        leave_types = LeaveType.query.all()
        return jsonify([{
            'id': lt.leave_type_id,
            'name': lt.leave_type_name
        } for lt in leave_types])
    except Exception as e:
        return jsonify({'error': str(e)}), 500