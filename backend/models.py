from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = 'department'
    
    department_id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    employees = db.relationship('Employee', backref='department', lazy=True)


class Role(db.Model):
    __tablename__ = 'role'
    
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)
    base_salary = db.Column(db.Numeric(10, 2), nullable=True)  # Base salary for the role
    salary_type = db.Column(db.Enum('monthly', 'hourly'), nullable=True)  # Defines if the role is monthly or hourly    

    # Relationships
    employees = db.relationship('Employee', backref='role', lazy=True)


class Employee(db.Model):
    __tablename__ = 'employee'
    
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    hire_date = db.Column(db.Date)
    employee_status = db.Column(db.Enum('full_time', 'part_time', 'contractor'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), nullable=True)
    contract_start_date = db.Column(db.Date, nullable=False)
    contract_end_date = db.Column(db.Date, nullable=True)
    contract_status = db.Column(db.Enum('active', 'expired', 'terminated'), nullable=False)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)
    performance_reviews = db.relationship('Performance', foreign_keys='Performance.employee_id', backref='employee', lazy=True)
    performance_given = db.relationship('Performance', foreign_keys='Performance.reviewer_id', backref='reviewer', lazy=True)
    leave_requests = db.relationship('Leave', foreign_keys='Leave.employee_id', backref='employee', lazy=True)
    leave_approvals = db.relationship('Leave', foreign_keys='Leave.approver_id', backref='approver', lazy=True)
    payrolls = db.relationship('Payroll', backref='employee', lazy=True)
    leave_balances = db.relationship('LeaveBalance', backref='employee', lazy=True)


class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_in = db.Column(db.Time, nullable=True)
    time_out = db.Column(db.Time, nullable=True)
    work_hours = db.Column(db.Numeric(4, 2), nullable=False)
    overtime_hours = db.Column(db.Numeric(4, 2), nullable=False)
    employee_status = db.Column(db.Enum('present', 'absent', 'leave', 'remote'), nullable=False)


class Performance(db.Model):
    __tablename__ = 'performance'
    
    performance_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    review_score = db.Column(db.Numeric(3, 1), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=True)
    review_date = db.Column(db.Date)
    
    # Relationships
    kpis = db.relationship('KPI', backref='performance', lazy=True)
    goals = db.relationship('Goal', backref='performance', lazy=True)
    achievements = db.relationship('Achievement', backref='performance', lazy=True)


class KPI(db.Model):
    __tablename__ = 'kpi'
    
    kpi_id = db.Column(db.Integer, primary_key=True)
    performance_id = db.Column(db.Integer, db.ForeignKey('performance.performance_id'), nullable=False)
    kpi_description = db.Column(db.String(255), nullable=False)
    kpi_score = db.Column(db.Numeric(2, 1), nullable=False)


class Goal(db.Model):
    __tablename__ = 'goal'
    
    goal_id = db.Column(db.Integer, primary_key=True)
    performance_id = db.Column(db.Integer, db.ForeignKey('performance.performance_id'), nullable=False)
    goal_description = db.Column(db.String(255), nullable=False)
    goal_status = db.Column(db.Enum('not started', 'in progress', 'achieved'), nullable=False)


class Achievement(db.Model):
    __tablename__ = 'achievement'
    
    achievement_id = db.Column(db.Integer, primary_key=True)
    performance_id = db.Column(db.Integer, db.ForeignKey('performance.performance_id'), nullable=False)
    achievement_description = db.Column(db.String(255), nullable=False)
    achievement_date = db.Column(db.Date)


class Payroll(db.Model):
    __tablename__ = 'payroll'
    
    payroll_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    base_salary = db.Column(db.Numeric(10, 2), nullable=False)
    bonus = db.Column(db.Numeric(10, 2), default=0)
    tax = db.Column(db.Numeric(10, 2), nullable=False)
    deduction = db.Column(db.Numeric(10, 2), default=0)
    
    # Relationships
    payments = db.relationship('Payment', backref='payroll', lazy=True)


class Payment(db.Model):
    __tablename__ = 'payment'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    payroll_id = db.Column(db.Integer, db.ForeignKey('payroll.payroll_id'), nullable=False)
    payment_method = db.Column(db.Enum('bank transfer', 'cash', 'check'))
    payment_status = db.Column(db.Enum('paid', 'failed', 'pending'))
    payment_date = db.Column(db.Date)
    amount_paid = db.Column(db.Numeric(10, 2))


class LeaveType(db.Model):
    __tablename__ = 'leave_type'
    
    leave_type_id = db.Column(db.Integer, primary_key=True)
    leave_type_name = db.Column(db.String(50), nullable=False)
    
    # Relationships
    leave_balances = db.relationship('LeaveBalance', backref='leave_type', lazy=True)
    leave_requests = db.relationship('Leave', backref='leave_type', lazy=True)


class LeaveBalance(db.Model):
    __tablename__ = 'leave_balance'
    
    balance_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_type.leave_type_id'), nullable=True)
    leave_balance = db.Column(db.Integer, nullable=False, default=0)


class Leave(db.Model):
    __tablename__ = 'leave'
    
    leave_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_type.leave_type_id'), nullable=True)
    leave_start = db.Column(db.Date)
    leave_end = db.Column(db.Date)
    leave_status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    approver_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=True)
