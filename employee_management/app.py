import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = 'secret_key'

# Sample data structure to hold employee records insted of database for now 
employees = {}
attendance_records = {}
payroll_records = {}

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Add employee route
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        employee_id = int(request.form['employee_id'])
        name = request.form['name']
        role = request.form['role']
        department = request.form['department']
        salary = float(request.form['salary'])
        employment_status = request.form['employment_status']
        
        if employee_id in employees:
            flash("Employee ID already exists!", "error")
        else:
            employees[employee_id] = {
                'name': name,
                'role': role,
                'department': department,
                'salary': salary,
                'employment_status': employment_status,
                'attendance': [],
                'leaves': 0
            }
            flash(f"Employee {name} added successfully!", "success")
        return redirect(url_for('add_employee'))
    return render_template('add_employee.html')

# Record attendance route
@app.route('/record_attendance', methods=['GET', 'POST'])
def record_attendance():
    if request.method == 'POST':
        employee_id = int(request.form['employee_id'])
        status = request.form['status']
        date = str(datetime.date.today())
        
        if employee_id in employees:
            attendance_records.setdefault(employee_id, []).append({'date': date, 'status': status})
            flash(f"Attendance for {employees[employee_id]['name']} recorded as {status} on {date}.", "success")
        else:
            flash("Employee not found!", "error")
        return redirect(url_for('record_attendance'))
    return render_template('record_attendance.html')

# Calculate payroll route
@app.route('/calculate_payroll', methods=['GET', 'POST'])
def calculate_payroll():
    if request.method == 'POST':
        employee_id = int(request.form['employee_id'])
        
        if employee_id not in employees:
            flash("Employee not found!", "error")
            return redirect(url_for('calculate_payroll'))
        
        # Fetch employee's attendance and salary details
        employee = employees[employee_id]
        attendance = attendance_records.get(employee_id, [])
        total_days = len(attendance)
        present_days = sum(1 for record in attendance if record['status'] == 'Present')

        salary = employee['salary']
        actual_salary = (present_days / total_days) * salary if total_days > 0 else 0

        # Storing payroll record
        payroll_records[employee_id] = {
            'total_days': total_days,
            'present_days': present_days,
            'basic_salary': salary,
            'final_salary': actual_salary
        }
        
        flash(f"Payroll calculated for {employee['name']}: Final Salary = ${actual_salary:.2f} (Present: {present_days}/{total_days})", "success")
        return redirect(url_for('calculate_payroll'))
    return render_template('calculate_payroll.html')

# Generate payslip route
@app.route('/payslip', methods=['GET', 'POST'])
def payslip():
    if request.method == 'POST':
        employee_id = int(request.form['employee_id'])
        
        if employee_id in payroll_records:
            payroll = payroll_records[employee_id]
            employee = employees[employee_id]
            payslip_data = {
                'name': employee['name'],
                'basic_salary': payroll['basic_salary'],
                'total_days': payroll['total_days'],
                'present_days': payroll['present_days'],
                'final_salary': payroll['final_salary']
            }
            return render_template('payslip.html', payslip_data=payslip_data)
        else:
            flash("Payroll not calculated for this employee yet!", "error")
            return redirect(url_for('payslip'))
    return render_template('payslip.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
