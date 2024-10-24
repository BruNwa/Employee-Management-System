from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
import enum

app = Flask(__name__)

# MySQL Database configuration (adjust these settings based on your docker-compose environment variables)
DATABASE_URI = 'mysql+pymysql://admin:mthree@db:3306/employee_management_system'

# Create an engine and session
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Enum types
class EmploymentStatusEnum(enum.Enum):
    full_time = 'full_time'
    part_time = 'part_time'
    contractor = 'contractor'

class ContractStatusEnum(enum.Enum):
    active = 'active'
    expired = 'expired'
    terminated = 'terminated'

# Define Department model
class Department(Base):
    __tablename__ = 'department'
    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(100), nullable=False)

# Define Role model
class Role(Base):
    __tablename__ = 'role'
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(100), nullable=False)

# Define Employee model
class Employee(Base):
    __tablename__ = 'employee'
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15))
    hire_date = Column(Date)
    employee_status = Column(Enum(EmploymentStatusEnum))
    department_id = Column(Integer, ForeignKey('department.department_id'), nullable=True)
    role_id = Column(Integer, ForeignKey('role.role_id'), nullable=True)
    contract_start_date = Column(Date, nullable=False)
    contract_end_date = Column(Date, nullable=True)
    contract_status = Column(Enum(ContractStatusEnum), nullable=False)

    department = relationship("Department")
    role = relationship("Role")

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Route to display the employee form
@app.route('/employee/new', methods=['GET'])
def new_employee():
    session = Session()
    departments = session.query(Department).all()
    roles = session.query(Role).all()
    session.close()
    return render_template('employee_form.html', departments=departments, roles=roles)

# Route to create a new employee
@app.route('/employee/new', methods=['POST'])
def create_employee():
    session = Session()
    try:
        # Collect data from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        hire_date = request.form['hire_date']
        employee_status = request.form['employee_status']
        department_id = request.form['department_id']
        role_id = request.form['role_id']
        contract_start_date = request.form['contract_start_date']
        contract_end_date = request.form['contract_end_date']
        contract_status = request.form['contract_status']

        # Create a new employee instance
        new_employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            hire_date=hire_date,
            employee_status=employee_status,
            department_id=department_id,
            role_id=role_id,
            contract_start_date=contract_start_date,
            contract_end_date=contract_end_date,
            contract_status=contract_status
        )
        session.add(new_employee)
        session.commit()
        return redirect(url_for('get_employees'))  # Redirect to the list of employees
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

# Route to get the list of employees (manage employees)
@app.route('/employees', methods=['GET'])
def get_employees():
    session = Session()
    try:
        employees = session.query(Employee).all()
        return render_template('employee_list.html', employees=employees)
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

# Route to update an employee profile
@app.route('/employee/edit/<int:id>', methods=['GET', 'POST'])
def update_employee(id):
    session = Session()
    employee = session.query(Employee).filter_by(employee_id=id).first()

    if request.method == 'POST':
        try:
            # Update employee fields from form input
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

            session.commit()
            return redirect(url_for('get_employees'))
        except SQLAlchemyError as e:
            session.rollback()
            return jsonify({'error': str(e)}), 400
        finally:
            session.close()

    departments = session.query(Department).all()
    roles = session.query(Role).all()
    return render_template('employee_form.html', employee=employee, departments=departments, roles=roles)

# Route to delete an employee profile
@app.route('/employee/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    session = Session()
    try:
        employee = session.query(Employee).filter_by(employee_id=id).first()
        if employee:
            session.delete(employee)
            session.commit()
            return redirect(url_for('get_employees'))
        else:
            return jsonify({'message': 'Employee not found'}), 404
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
