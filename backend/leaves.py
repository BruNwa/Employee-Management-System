from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for, session
from models import db,Leave, LeaveBalance, LeaveType, Employee, Attendance
from datetime import datetime, timedelta,date

lb = Blueprint('leaves', __name__)

def is_workday(date):
    return date.weekday() < 5  # True if weekday, False if weekend
###########################################################################################
##################### MANAGER SECTION #####################################################
###########################################################################################

@lb.route('/list', methods=['GET'])
def leave_list():
    leaves = Leave.query.all()
    return render_template('leave_list.html', leaves=leaves)

@lb.route('/approve/<int:leave_id>', methods=['POST'])
def approve_leave(leave_id):
    leave_request = Leave.query.get_or_404(leave_id)

    # Remove the flash messages and redirect, since we are using AJAX
    if not leave_request:
        return jsonify({'error': "Leave request not found."}), 404
    
    leave_request.leave_status = 'approved'
    leave_request.approver_id = session['employee_id']

    start_date = leave_request.leave_start
    end_date = leave_request.leave_end

    current_date = start_date
    while current_date <= end_date:
        if is_workday(current_date):
            attendance_record = Attendance(
                employee_id=leave_request.employee_id,
                date=current_date,
                time_in=None,  # or set to default value
                time_out=None,  # or set to default value
                work_hours=0,   # Fixed 8 hours for leave
                overtime_hours=0,  # Assuming no overtime on leave
                employee_status='leave'  # Set status to leave
            )
            db.session.add(attendance_record)
        current_date += timedelta(days=1)
    db.session.commit()
    return jsonify({'message': "Leave request approved."}), 200

@lb.route('/deny/<int:leave_id>', methods=['POST'])
def deny_leave(leave_id):
    leave_request = Leave.query.get_or_404(leave_id)

    if not leave_request:
        return jsonify({'error': "Leave request not found."}), 404
    
    leave_request.leave_status = 'rejected'
    leave_request.approver_id = session['employee_id']
    leave_balance = LeaveBalance.query.filter_by(employee_id=leave_request.employee_id, leave_type_id=leave_request.leave_type_id).first()
    days_requested = (leave_request.leave_end - leave_request.leave_start).days + 1

    if leave_balance:
        leave_balance.leave_balance += days_requested

    db.session.commit()
    return jsonify({'message': "Leave request denied and days returned."}), 200

###########################################################################################
##################### EMPLOYEE SECTION ####################################################
###########################################################################################

def count_workdays(start_date, end_date):
    workdays = 0
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday to Friday are 0 to 4
            workdays += 1
        current_date += timedelta(days=1)

    return workdays


@lb.route('/apply/<int:employee_id>', methods=['GET', 'POST'])
def leave_apply(employee_id):
    if request.method == 'GET':
        # Fetch leave types
        leave_types = LeaveType.query.all()

        # Initialize leave balances
        leave_balances = {leave_type.leave_type_id: 0 for leave_type in leave_types}
        
        # Fetch leave balances for the employee
        balances = LeaveBalance.query.filter_by(employee_id=employee_id).all()
        for balance in balances:
            leave_balances[balance.leave_type_id] = balance.leave_balance

        # Pass this data to the template
        return render_template(
            'apply_leave.html', 
            leave_types=leave_types, 
            leave_balances=leave_balances,  # Ensure this is defined
            employee_id=employee_id
        )
        
    
    # POST request logic for applying leave
    if request.method == 'POST':
        leave_type_id = request.form.get('leave_type', type=int)
        leave_start = request.form.get('leave_start', type=str)
        leave_end = request.form.get('leave_end', type=str)
        
        # Fetch leave balance
        leave_balance = LeaveBalance.query.filter_by(
            employee_id=employee_id, 
            leave_type_id=leave_type_id
        ).first()

        # Check availability
        if leave_balance is None:
            flash('Leave balance not found for the specified leave type.', 'danger')
            return redirect(url_for('leaves.leave_apply', employee_id=employee_id))


        # Parse the leave dates
        try:
            leave_start_date = datetime.strptime(leave_start, '%Y-%m-%d').date()
            leave_end_date = datetime.strptime(leave_end, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('leaves.leave_apply', employee_id=employee_id))

        
        # Check if the end date is before the start date
        if leave_end_date < leave_start_date:
            flash('End date cannot be before the start date.', 'danger')
            return redirect(url_for('leaves.leave_apply', employee_id=employee_id))

        total_days_requested = count_workdays(leave_start_date, leave_end_date)

        # Check availability
        if leave_balance.leave_balance < total_days_requested:
            flash('Insufficient leave balance for the requested days.', 'danger')
            return redirect(url_for('leaves.leave_apply', employee_id=employee_id))

        

        # Apply leave and update balance
        new_leave = Leave(
            employee_id=employee_id,
            leave_type_id=leave_type_id,
            leave_start=leave_start_date,
            leave_end=leave_end_date,
            leave_status='pending'
        )
        db.session.add(new_leave)
        leave_balance.leave_balance -= total_days_requested
        db.session.commit()

        flash('Leave applied successfully', 'success')
        return redirect(url_for('leaves.leave_apply', employee_id=employee_id))

    return render_template('apply_leave.html')





# Backup  for manager 
# @lb.route('/list', methods=['GET'])
# def leave_list():
#     leaves = Leave.query.all()
#     return render_template('leave_list.html',leaves=leaves)

# @lb.route('/approve/<int:leave_id>', methods=['POST'])
# def approve_leave(leave_id):
#     leave_request = Leave.query.get_or_404(leave_id)

#     if not leave_request:
#         flash("Leave request not found.", "danger")
#         return redirect(url_for('leaves.leave_list'))
    
#     leave_request.leave_status = 'approved'
#     db.session.commit()
#     flash("Leave request approved.", "success")
#     return redirect(url_for('leaves.leave_list'))

# @lb.route('/deny/<int:leave_id>', methods=['POST'])
# def deny_leave(leave_id):
#     leave_request = Leave.query.get_or_404(leave_id)

#     if not leave_request:
#         flash("Leave request not found.", "danger")
#         return redirect(url_for('leaves.leave_list'))
    
#     leave_request.leave_status = 'rejected'

#     leave_balance = LeaveBalance.query.filter_by(employee_id=leave_request.employee_id, leave_type_id=leave_request.leave_type_id).first()
#     days_requested = (leave_request.leave_end - leave_request.leave_start).days + 1

#     if leave_balance:
#         leave_balance.leave_balance += days_requested

#     db.session.commit()
#     flash("Leave request denied and days returned.", "danger")
#     return redirect(url_for('leaves.leave_list'))