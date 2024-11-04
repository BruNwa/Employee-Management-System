# payroll.py
from flask import Blueprint, request, jsonify
from models import db, Employee, Attendance, Payroll
from sqlalchemy import func
from datetime import datetime, timedelta

payroll_bp = Blueprint('payroll', __name__)

@payroll_bp.route('/process-payroll', methods=['POST'])
def process_payroll():
    data = request.get_json()
    period_type = data.get('period_type', 'monthly')
    
    # Validate period type
    if period_type not in ['monthly', 'bi-weekly']:
        return jsonify({'error': 'Invalid payroll period type'}), 400

    payroll_results = []

    # Set payroll period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30) if period_type == 'monthly' else end_date - timedelta(days=14)

    employees = Employee.query.all()
    
    for employee in employees:
        # Fetch attendance records within the payroll period
        attendance_records = Attendance.query.filter(
            Attendance.employee_id == employee.employee_id,
            Attendance.date.between(start_date, end_date)
        ).all()

        # Calculate total work hours and overtime
        total_hours = sum(float(record.work_hours) for record in attendance_records)
        overtime_hours = sum(float(record.overtime_hours) for record in attendance_records)

        # Fetch payroll details
        payroll = Payroll.query.filter_by(employee_id=employee.employee_id).first()
        if not payroll:
            continue
        
        # Compute base pay and additional calculations
        base_salary = float(payroll.base_salary)
        overtime_pay = overtime_hours * (base_salary / 160) * 1.5  # Assume 1.5x overtime
        deductions = float(payroll.deduction)
        bonus = float(payroll.bonus)
        total_pay = base_salary + overtime_pay + bonus - deductions

        payroll_results.append({
            'employee_id': employee.employee_id,
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'total_work_hours': total_hours,
            'overtime_hours': overtime_hours,
            'leave_deductions': deductions,
            'overtime_pay': round(overtime_pay, 2),
            'total_pay': round(total_pay, 2)
        })

    return jsonify({'payroll': payroll_results})
