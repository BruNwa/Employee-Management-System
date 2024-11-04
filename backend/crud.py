from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models import db, Department, Role, Employee , Leave , Payroll , Performance  
from sqlalchemy.exc import SQLAlchemyError

crud_bp = Blueprint('crud', __name__)

@crud_bp.route('/employees', methods=['GET'])
def get_employees():
    """Retrieve all employees and render them in the employee list template."""
    try:
        employees = Employee.query.all()
        return render_template('employee_list.html', employees=employees)
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 400

@crud_bp.route('/employee/new', methods=['GET'])
def new_employee_form():
    """Render the employee creation form with departments and roles."""
    departments = Department.query.all()
    roles = Role.query.all()
    return render_template('creation.html', departments=departments, roles=roles)

@crud_bp.route('/employee/new', methods=['POST'])
def create_employee():
    """Create a new employee and save to the database."""
    try:
        employee = Employee(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            hire_date=request.form['hire_date'],
            employee_status=request.form['employee_status'],
            department_id=request.form['department_id'],
            role_id=request.form['role_id'],
            contract_start_date=request.form['contract_start_date'],
            contract_end_date=request.form['contract_end_date'],
            contract_status=request.form['contract_status']
        )
        db.session.add(employee)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Employee created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'An unexpected error occurred: ' + str(e)}), 500

@crud_bp.route('/employee/edit/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    """Edit an existing employee's details."""
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    
    if request.method == 'POST':
        try:
            employee.first_name = request.form['first_name']
            employee.last_name = request.form['last_name']
            employee.email = request.form['email']
            employee.phone = request.form['phone']
            employee.hire_date = request.form['hire_date']
            employee.employee_status = request.form['employee_status']
            employee.department_id = request.form['department_id']
            employee.role_id = request.form['role_id']
            employee.contract_start_date = request.form['contract_start_date']
            employee.contract_end_date = request.form['contract_end_date']
            employee.contract_status = request.form['contract_status']
            db.session.commit()
            return redirect(url_for('crud.get_employees'))
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    departments = Department.query.all()
    roles = Role.query.all()
    return render_template('creation.html', employee=employee, departments=departments, roles=roles)

@crud_bp.route('/employee/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    """Delete an employee from the database."""
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    try:
        # Delete related payroll records
        Payroll.query.filter_by(employee_id=employee_id).delete()
        
        # Delete related leave requests (add other related records if needed)
        Leave.query.filter_by(employee_id=employee_id).delete()

        Performance.query.filter_by(employee_id=employee_id).delete()


        db.session.delete(employee)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Employee deleted successfully.'})  # Return a JSON response
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
