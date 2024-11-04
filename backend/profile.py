from flask import Blueprint, jsonify, request, session, current_app
from models import db, Employee, Leave, Performance, LeaveType, KPI, Goal, Achievement, Attendance, Payroll, Payment, Role, Department, LeaveBalance
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from decimal import Decimal


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
        # Create aliases for the Employee table
        EmployeeRequester = aliased(Employee)  # For the employee who requested the leave
        Approver = aliased(Employee)  # For the approver
        
        # Query to fetch the latest 5 leave requests with approver details
        leaves = (
            db.session.query(
                Leave,
                EmployeeRequester.first_name.label('requester_first_name'),
                EmployeeRequester.last_name.label('requester_last_name'),
                # Use a case statement to provide default name if approver is NULL
                (Approver.first_name + ' ' + Approver.last_name).label('approver_name')  # Concatenate names
            )
            .join(EmployeeRequester, Leave.employee_id == EmployeeRequester.employee_id)  # Join to get requester's details
            .outerjoin(Approver, Leave.approver_id == Approver.employee_id)  # Outer join to get approver's details
            .filter(Leave.employee_id == session['employee_id'])  # Filter by the employee who made the request
            .order_by(Leave.leave_start.desc())  # Order by latest leave start date
            .limit(5)  # Limit to 5 results
            .all()
        )
        
        leave_list = []
        for leave, requester_first_name, requester_last_name, approver_full_name in leaves:
            # Use the default 'Pending' if approver_full_name is NULL
            approver_name = approver_full_name if approver_full_name else 'Pending'
            leave_list.append({
                'leave_id': leave.leave_id,
                'leave_type': leave.leave_type.leave_type_name if leave.leave_type else 'N/A',
                'balance': leave.leave_type.leave_balances[0].leave_balance if leave.leave_type and leave.leave_type.leave_balances else 0,
                'start_date': leave.leave_start.strftime('%Y-%m-%d'),
                'end_date': leave.leave_end.strftime('%Y-%m-%d'),
                'status': leave.leave_status,
                'requester': f"{requester_first_name} {requester_last_name}",
                'approver': approver_name
            })
        
        return jsonify(leave_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


'''@profile_bp.route('/profile/leave-request', methods=['POST'])
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
        return jsonify({'error': str(e)}), 500'''

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

    
@profile_bp.route('/profile/attendance/logs', methods=['GET'])
@login_required
def get_attendance_logs():
    try:
        logs = Attendance.query.filter_by(
            employee_id=session['employee_id']
        ).order_by(Attendance.date.desc()).limit(5).all()  # Limit to last 5 logs
        
        log_data = [
            {
                'date': log.date.strftime('%Y-%m-%d'),
                'time_in': log.time_in.strftime('%H:%M:%S') if log.time_in else '--:--',
                'time_out': log.time_out.strftime('%H:%M:%S') if log.time_out else '--:--',
                'work_hours': float(log.work_hours) if log.work_hours else 0,
                'overtime_hours': float(log.overtime_hours) if log.overtime_hours else 0,
                'status': log.employee_status
            }
            for log in logs
        ]
        
        return jsonify(log_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/profile/attendance/status', methods=['GET'])
@login_required
def get_attendance_status():
    try:
        today = datetime.now().date()
        attendance = Attendance.query.filter_by(
            employee_id=session['employee_id'],
            date=today
        ).first()
        
        if not attendance:
            return jsonify({
                'checked_in': False,
                'checked_out': False,
                'time_in': None,
                'time_out': None,
                'work_hours': 0,
                'status': 'absent'
            })
            
        return jsonify({
            'checked_in': attendance.time_in is not None,
            'checked_out': attendance.time_out is not None,
            'time_in': attendance.time_in.strftime('%H:%M:%S') if attendance.time_in else None,
            'time_out': attendance.time_out.strftime('%H:%M:%S') if attendance.time_out else None,
            'work_hours': float(attendance.work_hours) if attendance.work_hours else 0,
            'status': attendance.employee_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/profile/attendance/checkin', methods=['POST'])
@login_required
def check_in():
    try:
        now = datetime.now()
        today = now.date()
        
        # Check if already checked in today
        existing_attendance = Attendance.query.filter_by(
            employee_id=session['employee_id'],
            date=today
        ).first()
        
        if existing_attendance and existing_attendance.time_in:
            return jsonify({'error': 'Already checked in today'}), 400
            
        if not existing_attendance:
            attendance = Attendance(
                employee_id=session['employee_id'],
                date=today,
                time_in=now.time(),
                work_hours=Decimal('0.00'),
                overtime_hours=Decimal('0.00'),
                employee_status='present'
            )
            db.session.add(attendance)
        else:
            existing_attendance.time_in = now.time()
            existing_attendance.employee_status = 'present'
            
        db.session.commit()
        
        return jsonify({
            'message': 'Check-in successful',
            'time': now.strftime('%H:%M:%S'),
            'date': today.strftime('%Y-%m-%d')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/profile/attendance/checkout', methods=['POST'])
@login_required
def check_out():
    try:
        now = datetime.now()
        today = now.date()
        
        attendance = Attendance.query.filter_by(
            employee_id=session['employee_id'],
            date=today
        ).first()
        
        if not attendance or not attendance.time_in:
            return jsonify({'error': 'No check-in record found for today'}), 400
            
        if attendance.time_out:
            return jsonify({'error': 'Already checked out today'}), 400
            
        # Calculate work hours
        time_in = datetime.combine(today, attendance.time_in)
        time_out = datetime.combine(today, now.time())
        duration = time_out - time_in
        
        # Convert to decimal hours
        hours = duration.total_seconds() / 3600
        regular_hours = min(8, hours)  # Assuming 8-hour workday
        overtime = max(0, hours - 8)
        
        attendance.time_out = now.time()
        attendance.work_hours = Decimal(str(round(regular_hours, 2)))
        attendance.overtime_hours = Decimal(str(round(overtime, 2)))
        
        db.session.commit()
        
        return jsonify({
            'message': 'Check-out successful',
            'time': now.strftime('%H:%M:%S'),
            'date': today.strftime('%Y-%m-%d'),
            'work_hours': round(hours, 2)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@profile_bp.route('/profile/payslip', methods=['GET'])
@login_required
def get_payslip():
    try:
        # Get payroll and latest payment information for the logged-in employee
        payroll_with_payment = db.session.query(
            Payroll, Payment
        ).join(
            Payment, Payroll.payroll_id == Payment.payroll_id
        ).filter(
            Payroll.employee_id == session['employee_id']
        ).order_by(
            Payment.payment_date.desc()
        ).first()
        
        if not payroll_with_payment:
            return jsonify({'error': 'Payroll information not found'}), 404
            
        payroll, payment = payroll_with_payment
            
        # Get employee details
        employee = Employee.query.get(session['employee_id'])
        
        if not employee:
            return jsonify({'error': 'Employee information not found'}), 404
        
        # Calculate total earnings and net salary
        total_earnings = payroll.base_salary + payroll.bonus
        total_deductions = payroll.tax + payroll.deduction
        net_salary = total_earnings - total_deductions
        
        # Format the payslip response
        payslip = {
            'employee_details': {
                'employee_id': employee.employee_id,
                'name': f"{employee.first_name} {employee.last_name}",
                'department': employee.department.department_name if employee.department else None,
                'role': employee.role.role_name if employee.role else None
            },
            'earnings': {
                'base_salary': float(payroll.base_salary),
                'bonus': float(payroll.bonus),
                'total_earnings': float(total_earnings)
            },
            'deductions': {
                'tax': float(payroll.tax),
                'other_deductions': float(payroll.deduction),
                'total_deductions': float(total_deductions)
            },
            'payment_details': {
                'payment_method': payment.payment_method,
                'payment_status': payment.payment_status,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'amount_paid': float(payment.amount_paid)
            },
            'summary': {
                'gross_salary': float(total_earnings),
                'total_deductions': float(total_deductions),
                'net_salary': float(net_salary)
            },
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(payslip)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_payslip: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving payslip data'}), 500

@profile_bp.route('/profile/payslip/history', methods=['GET'])
@login_required
def get_payslip_history():
    try:
        # Get optional query parameters for date filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Base query joining Payroll and Payment tables
        query = db.session.query(Payroll, Payment).join(
            Payment, Payroll.payroll_id == Payment.payroll_id
        ).filter(Payroll.employee_id == session['employee_id'])
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Payment.payment_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Payment.payment_date <= datetime.strptime(end_date, '%Y-%m-%d'))
            
        # Get all payroll records ordered by payment date
        payroll_history = query.order_by(desc(Payment.payment_date)).all()
        
        history_list = []
        for payroll, payment in payroll_history:
            total_earnings = payroll.base_salary + payroll.bonus
            total_deductions = payroll.tax + payroll.deduction
            net_salary = total_earnings - total_deductions
            
            history_list.append({
                'payroll_id': payroll.payroll_id,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'payment_status': payment.payment_status,
                'payment_method': payment.payment_method,
                'base_salary': float(payroll.base_salary),
                'bonus': float(payroll.bonus),
                'total_earnings': float(total_earnings),
                'tax': float(payroll.tax),
                'deductions': float(payroll.deduction),
                'total_deductions': float(total_deductions),
                'net_salary': float(net_salary),
                'amount_paid': float(payment.amount_paid)
            })
            
        return jsonify(history_list)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_payslip_history: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving payslip history'}), 500
    
def count_workdays(start_date, end_date):
    current_day = start_date
    workdays = 0
    while current_day <= end_date:
        if current_day.weekday() < 5:  
            workdays += 1
        current_day += timedelta(days=1)
    return workdays   

@profile_bp.route('/leaves/apply', methods=['GET', 'POST'])
@login_required
def leave_apply():
    try:
        # Check if employee_id exists in the session
        employee_id = session.get('employee_id')
        if not employee_id:
            return jsonify({'error': 'Employee ID not found in session'}), 401

        # Handle GET request: retrieve leave types and balances
        if request.method == 'GET':
            # Fetch leave types and balances for the employee
            leave_types = LeaveType.query.all()
            balances = LeaveBalance.query.filter_by(employee_id=employee_id).all()

            # Prepare response data
            leave_data = []
            for leave_type in leave_types:
                balance = next((b for b in balances if b.leave_type_id == leave_type.leave_type_id), None)
                leave_data.append({
                    'leave_type_id': leave_type.leave_type_id,
                    'leave_type_name': leave_type.leave_type_name,
                    'balance': balance.leave_balance if balance else 0
                })

            return jsonify({
                'employee_id': employee_id,
                'leave_types': leave_data
            })

        # Handle POST request: create a leave request
        elif request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # Extract and validate required fields
            leave_type_id = data.get('leave_type_id')
            leave_start = data.get('leave_start')
            leave_end = data.get('leave_end')

            if not all([leave_type_id, leave_start, leave_end]):
                return jsonify({'error': 'Missing required fields'}), 400

            # Parse and validate dates
            try:
                leave_start_date = datetime.strptime(leave_start, '%Y-%m-%d').date()
                leave_end_date = datetime.strptime(leave_end, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

            if leave_end_date < leave_start_date:
                return jsonify({'error': 'End date cannot be before start date'}), 400

            # Fetch leave balance and validate
            leave_balance = LeaveBalance.query.filter_by(
                employee_id=employee_id,
                leave_type_id=leave_type_id
            ).first()

            if not leave_balance:
                return jsonify({'error': 'Leave balance not found'}), 404

            # Calculate total days and verify balance
            total_days = count_workdays(leave_start_date, leave_end_date)
            if leave_balance.leave_balance < total_days:
                return jsonify({'error': 'Insufficient leave balance'}), 400

            # Create leave request
            try:
                new_leave = Leave(
                    employee_id=employee_id,
                    leave_type_id=leave_type_id,
                    leave_start=leave_start_date,
                    leave_end=leave_end_date,
                    leave_status='pending'
                )
                db.session.add(new_leave)
                leave_balance.leave_balance -= total_days
                db.session.commit()

                return jsonify({
                    'status': 'success',
                    'leave_id': new_leave.leave_id,
                    'employee_id': employee_id,
                    'leave_type_id': leave_type_id,
                    'leave_start': leave_start,
                    'leave_end': leave_end,
                    'days_requested': total_days,
                    'remaining_balance': leave_balance.leave_balance
                })

            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'Database error occurred: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
