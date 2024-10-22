import datetime

# Sample data structure to hold employee records
employees = {}
attendance_records = {}
payroll_records = {}

# Function to add a new employee
def add_employee():
    print("\n--- Add New Employee ---")
    employee_id = int(input("Enter Employee ID: "))
    name = input("Enter Employee Name: ")
    role = input("Enter Role: ")
    department = input("Enter Department: ")
    salary = float(input("Enter Salary: "))
    employment_status = input("Enter Employment Status (Full-Time/Part-Time/Contractor): ")
    
    employees[employee_id] = {
        'name': name,
        'role': role,
        'department': department,
        'salary': salary,
        'employment_status': employment_status,
        'attendance': [],
        'leaves': 0
    }
    print(f"Employee {name} added successfully!\n")

# Function to view all employees
def view_employees():
    if employees:
        print("\n--- Employee List ---")
        for emp_id, details in employees.items():
            print(f"ID: {emp_id}, Name: {details['name']}, Role: {details['role']}, Department: {details['department']}, Status: {details['employment_status']}")
    else:
        print("\nNo employees found.")

# Function to record attendance
def record_attendance():
    print("\n--- Record Attendance ---")
    employee_id = int(input("Enter Employee ID: "))
    status = input("Enter Attendance Status (Present/Absent): ")
    
    date = str(datetime.date.today())
    if employee_id in employees:
        attendance_records.setdefault(employee_id, []).append({'date': date, 'status': status})
        print(f"Attendance for {employees[employee_id]['name']} recorded as {status} on {date}.")
    else:
        print("Employee not found.")

# Function to calculate salary based on attendance
def calculate_payroll():
    print("\n--- Calculate Payroll ---")
    employee_id = int(input("Enter Employee ID: "))
    
    if employee_id not in employees:
        print("Employee not found.")
        return

    # Fetch employee's attendance and salary details
    employee = employees[employee_id]
    attendance = attendance_records.get(employee_id, [])
    total_days = len(attendance)
    present_days = sum(1 for record in attendance if record['status'] == 'Present')

    # Simple payroll calculation based on attendance (full salary if present, no deductions)
    salary = employee['salary']
    actual_salary = (present_days / total_days) * salary if total_days > 0 else 0

    # Storing payroll record
    payroll_records[employee_id] = {
        'total_days': total_days,
        'present_days': present_days,
        'basic_salary': salary,
        'final_salary': actual_salary
    }
    
    print(f"Payroll calculated for {employee['name']}: Final Salary = ${actual_salary:.2f} (Present: {present_days}/{total_days})")

# Function to generate payslip
def generate_payslip():
    print("\n--- Generate Payslip ---")
    employee_id = int(input("Enter Employee ID: "))
    
    if employee_id in payroll_records:
        payroll = payroll_records[employee_id]
        employee = employees[employee_id]
        print(f"\n--- Payslip for {employee['name']} ---")
        print(f"Basic Salary: ${payroll['basic_salary']:.2f}")
        print(f"Total Working Days: {payroll['total_days']}")
        print(f"Days Present: {payroll['present_days']}")
        print(f"Final Salary: ${payroll['final_salary']:.2f}")
    else:
        print("Payroll not calculated for this employee yet.")

# Main menu for the system
def main_menu():
    while True:
        print("\n=== Employee Management System ===")
        print("1. Add Employee")
        print("2. View Employees")
        print("3. Record Attendance")
        print("4. Calculate Payroll")
        print("5. Generate Payslip")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_employee()
        elif choice == '2':
            view_employees()
        elif choice == '3':
            record_attendance()
        elif choice == '4':
            calculate_payroll()
        elif choice == '5':
            generate_payslip()
        elif choice == '6':
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

# Run the main menu
main_menu()
