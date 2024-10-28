from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for
from models import db,Leave, LeaveBalance, LeaveType, Employee
from datetime import datetime

lb = Blueprint('leaves', __name__)



###########################################################################################
##################### MANAGER SECTION #####################################################
###########################################################################################

@lb.route('/list', methods=['GET'])
def leave_list():
    leaves = Leave.query.all()
    return render_template('leave_list.html',leaves=leaves)

@lb.route('/approve/<int:leave_id>', methods=['POST'])
def approve_leave(leave_id):
    leave_request = Leave.query.get_or_404(leave_id)

    if not leave_request:
        flash("Leave request not found.", "danger")
        return redirect(url_for('leaves.leave_list'))
    
    leave_request.status = 'approved'
    db.session.commit()
    flash("Leave request approved.", "success")
    return redirect(url_for('leaves.leave_list'))

@lb.route('/deny/<int:leave_id>', methods=['POST'])
def deny_leave(leave_id):
    leave_request = Leave.query.get_or_404(leave_id)

    if not leave_request:
        flash("Leave request not found.", "danger")
        return redirect(url_for('leaves.leave_list'))
    
    leave_request.status = 'rejected'

    leave_balance = LeaveBalance.query.filter_by(employee_id=leave_request.employee_id, leave_type_id=leave_request.leave_type_id).first()
    days_requested = (leave_request.end_date - leave_request.start_date).days + 1

    if leave_balance:
        leave_balance.leave_balance += days_requested

    db.session.commit()
    flash("Leave request denied and days returned.", "danger")
    return redirect(url_for('leaves.leave_list'))


###########################################################################################
##################### EMPLOYEE SECTION ####################################################
###########################################################################################

@lb.route('/apply', methods=['GET','POST'])
def leave_apply():
    if request.method == 'GET':
        # Fetch leave types for the dropdown
        leave_types = LeaveType.query.all()
        return render_template('apply_leave.html', leave_types=leave_types)
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id', type=int)
        leave_type_name = request.form.get('leave_type', type=str)
        leave_start = request.form.get('leave_start', type=str)
        leave_end = request.form.get('leave_end', type=str)
        
        leave_type = LeaveType.query.filter_by(leave_type_name=leave_type_name).first()
        #validate if leave type exist
        if not leave_type:
            flash('Invalid leave type.', 'danger')
            return redirect(url_for('leaves.apply_leave'))
        
        leave_start_date = datetime.strptime(leave_start, '%Y-%m-%d').date()
        leave_end_date = datetime.strptime(leave_end, '%Y-%m-%d').date()
        total_days_requested = (leave_end_date - leave_start_date).days + 1 

        # Validate leave dates
        if leave_start_date > leave_end_date:
            flash('Start date must be before the end date.', 'danger')
            return redirect(url_for('leaves.apply_leave'))
        
        #balidate if leave balance exist
        leave_balance = LeaveBalance.query.filter_by(employee_id=employee_id, leave_type_id=leave_type.leave_type_id).first()
        if leave_balance is None or leave_balance.leave_balance <= 0:
            flash('Insufficient leave balance.', 'danger')
            return redirect(url_for('leaves.apply_leave'))

        if leave_balance.leave_balance < total_days_requested:
            flash('Insufficient leave balance for the requested days.', 'danger')
            return redirect(url_for('leaves.apply_leave'))
        
        new_leave = Leave(
            employee_id = employee_id,
            leave_type_id = leave_type.leave_type_id,
            leave_start=leave_start_date,
            leave_end=leave_end_date,
            leave_status='pending'
        )
        db.session.add(new_leave)
        db.session.commit()

        leave_balance.leave_balance -= total_days_requested

        db.session.commit()

        flash('Leave applied successfully','success')
        return redirect(url_for('leaves.leave_list'))

    return render_template('leave_apply.html')