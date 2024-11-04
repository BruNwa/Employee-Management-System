from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for
from models import db, Employee, Payroll, Role, Attendance, Payment
from datetime import datetime, timedelta, date
from decimal import Decimal
from unittest.mock import Mock
import unittest
import random

payment_bp = Blueprint('payslip', __name__)

def is_workday(date):
    return date.weekday() < 5  # True if weekday, False if weekend

def hours_per_month(year, month):
    first_day = date(year, month, 1)
    last_day = (date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)) - timedelta(days=1)
    workdays = sum(1 for day in range((last_day - first_day).days + 1)
                   if is_workday(first_day + timedelta(days=day)))
    return 8 * workdays

def calculate_payslip(employee_id,today,payment_method, period_type="last_month", additional_bonus=0, deductions=0):
    employee = Employee.query.get(employee_id)
    if not employee:
        return {"error": "Employee not found"}
    role = Role.query.get(employee.role_id)
    if not role:
        return {"error": "Role not found"}

    rate = role.base_salary if role.salary_type == 'hourly' else role.base_salary / Decimal(hours_per_month(today.year, today.month))

    # Determine the date range based on period_type
    
    if period_type == "last_month":
        start_date = today.replace(day=1) - timedelta(days=1)
        start_date = start_date.replace(day=1)
        end_date = today.replace(day=1) - timedelta(days=1)
    elif period_type == "14_days":
        start_date = today - timedelta(days=14)
        end_date = today
    else:
        return {"error": "Invalid period type"}

    # Fetch attendance within the specified period
    attendance_records = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        Attendance.date.between(start_date, end_date)
    ).all()

    total_hours_present_remote = Decimal(0)
    total_hours_leave = Decimal(0)
    overtime_hours = Decimal(0)
    non_workday_hours = Decimal(0)

    for record in attendance_records:
        if record.employee_status in ['present', 'remote']:
            total_hours_present_remote += record.work_hours
            overtime_hours += record.overtime_hours
            if not is_workday(record.date):
                non_workday_hours += record.work_hours + record.overtime_hours
        elif record.employee_status == 'leave' and is_workday(record.date):
            total_hours_leave += record.work_hours

    base_salary = rate * total_hours_present_remote + rate * total_hours_leave * Decimal(0.8)
    overtime_bonus = overtime_hours * rate * Decimal(1.5)
    non_workday_bonus = non_workday_hours * rate * Decimal(0.5)
    bonus = overtime_bonus + non_workday_bonus + additional_bonus

    gross_salary = base_salary + bonus
    taxable_salary = gross_salary - deductions
    tax = taxable_salary * Decimal(0.19)
    net_salary = taxable_salary - tax

    payroll = Payroll(
        employee_id=employee_id,
        base_salary=base_salary,
        bonus=bonus,
        tax=tax,
        deduction=deductions
    )

    db.session.add(payroll)
    db.session.commit()

    
    payment = Payment(
        payroll_id=payroll.payroll_id,
        payment_method=payment_method,  # Assuming you want to set this to pending
        payment_status='pending',   # Set status to pending
        payment_date=datetime.today().date(),  # Set to today's date
        amount_paid=net_salary  # Assuming this is the amount to be paid
    )

    db.session.add(payment)  # Add payment to the session
    db.session.commit()  # Commit to save the payment instance



    payslip_data = {
        "employee_name": f"{employee.first_name} {employee.last_name}",
        "period_type": period_type,
        "base_salary": base_salary,
        "overtime_pay": overtime_bonus,
        "non_workday_bonus": non_workday_bonus,
        "additional_bonus": additional_bonus,
        "tax": tax,
        "deductions": deductions,
        "net_salary": net_salary
    }
    return payslip_data

@payment_bp.route('/generate', methods=['GET', 'POST'])
def generate_payslip():
    today=date.today()
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        period_type = request.form.get('period_type')  # "14_days" or "last_month"
        additional_bonus = Decimal(request.form.get('additional_bonus', 0))
        deductions = Decimal(request.form.get('deductions', 0))

        payment_method = request.form.get('payment_method')
        payslip_data = calculate_payslip(employee_id,today,payment_method, period_type, additional_bonus, deductions)
        return render_template('payslip.html', payslip_data=payslip_data)

    return render_template('generate_payslip.html')

@payment_bp.route('/list', methods=['GET'])
def list_payrolls():
    payrolls = Payroll.query.order_by(Payroll.payroll_id.desc()).all()  # Fetch all payroll records from the database
    return render_template('list_payslips.html', payrolls=payrolls)

@payment_bp.route('/payments/list', methods=['GET'])
def list_payments():
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()  # Fetch all payroll records from the database
    return render_template('list_payment.html', payments=payments)

def get_next_workday(start_date):
    next_day = start_date + timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    return next_day

def create_pending_payment(payment):
    next_workday = get_next_workday(payment.payment_date or date.today())
    new_payment = Payment(
        payroll_id=payment.payroll_id,
        payment_method=payment.payment_method,
        payment_status='pending',
        payment_date=next_workday,
        amount_paid=payment.amount_paid
    )
    db.session.add(new_payment)  # Add the new payment to the session
    db.session.commit()  # Commit the new payment

@payment_bp.route('/payments/update_status/<int:payment_id>', methods=['PUT'])
def update_payment_status(payment_id):
    data = request.get_json()
    new_status = data.get('status')
    
    # Fetch payment and update its status if it exists
    payment = Payment.query.get_or_404(payment_id)
    if payment.payment_method in ['check', 'cash']:
        payment.payment_status = new_status
        db.session.commit()

        if new_status == 'failed':
            create_pending_payment(payment)

        return jsonify({'success': True, 'message': 'Payment status updated successfully'}), 200
    else:
        return jsonify({'success': False, 'message': 'Status update not allowed for this payment method'}), 400

#simulate bank connection
def process_payment(api_client):
    response = api_client.process_payment()
    return response['status']

class TestBankPayment(unittest.TestCase):
    
    def test_process_payment(self):
        mock_api_client = Mock()

        payment_success = random.random()
        print(f"Simulating payment to the employee with success set to: {payment_success}")
        if payment_success<0.9:
            mock_api_client.process_payment.return_value = {'status': 'Payment Successful'}
            self.payment_result = 'Payment Successful' 
        else:
            mock_api_client.process_payment.return_value = {'status': 'Payment Failed'}
            self.payment_result = 'Payment Failed'

        result = process_payment(mock_api_client)

        print(f"Test result: {result}")
        assert result in ['Payment Successful']
        mock_api_client.process_payment.assert_called_once()
        #return self.payment_result

@payment_bp.route('/payments/run_test/<int:payment_id>', methods=['PUT'])
def run_payment_test(payment_id):
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBankPayment)
    runner = unittest.TextTestRunner(resultclass=unittest.TextTestResult)

    result = runner.run(suite)

    if result.failures or result.errors:
        new_status= 'failed'
        flash('Payment Failed!', 'danger')
    else:
        new_status= 'paid'
        flash('Payment Successful!', 'success')

    payment = Payment.query.get_or_404(payment_id)

    payment.payment_status = new_status
    db.session.commit()

    if new_status == 'failed':
            create_pending_payment(payment)
            return jsonify({'success': True, 'message': 'Payment failed. New pending payment created'}), 200
    return jsonify({'success': True, 'message': 'Payment status updated successfully'}), 200

