from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

#Backend
app = Flask(__name__)

# Secret key for flashing messages
app.config['SECRET_KEY'] = 'supersecretkey'

# Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://username:password@localhost/employee_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy database object
db = SQLAlchemy(app)

# Define the models (tables)
class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    salary = db.Column(db.Numeric(10, 2))

class Attendance(db.Model):
    __tablename__ = 'attendance'
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), primary_key=True)
    total_days = db.Column(db.Integer)
    present_days = db.Column(db.Integer)

class Payroll(db.Model):
    __tablename__ = 'payroll'
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), primary_key=True)
    basic_salary = db.Column(db.Numeric(10, 2))
    final_salary = db.Column(db.Numeric(10, 2))

# Initialize the database
db.create_all()

# Route to display the payslip form
@app.route('/')
def index():
    return render_template('payslip_form.html')

# Route to generate the payslip for an employee
@app.route('/payslip', methods=['POST'])
def payslip():
    employee_id = request.form['employee_id']
    
    # Fetch employee data from the database
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    attendance = Attendance.query.filter_by(employee_id=employee_id).first()
    payroll = Payroll.query.filter_by(employee_id=employee_id).first()
    
    if employee and attendance and payroll:
        # Prepare the payslip data
        payslip_data = {
            'name': employee.name,
            'basic_salary': payroll.basic_salary,
            'total_days': attendance.total_days,
            'present_days': attendance.present_days,
            'final_salary': payroll.final_salary
        }
        return render_template('payslip.html', payslip_data=payslip_data)
    else:
        flash("Payroll or employee data not found!", "error")
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)