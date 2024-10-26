from flask import request, jsonify, Blueprint, render_template  
from models import db, Attendance, Employee
from datetime import datetime

ab = Blueprint('attendance', __name__)


@ab.route('/', methods=['GET'])
def view_attendance():
    # Get query parameters from the form submission
    employee_id = request.args.get('employee_id', type=int)
    date_str = request.args.get('date', type=str)

    # Initialize a query
    query = db.session.query(Attendance).join(Employee)

    # Apply filter by employee_id if provided
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)

    # Apply filter by date if provided
    if date_str:
        try:
            # Parse the date string to a date object
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(Attendance.date == date_obj)
        except ValueError:
            return render_template('attendance_list.html', attendance_records=[], error="Invalid date format. Use YYYY-MM-DD.")

    attendance_records = query.all()
    # Execute the query to get filtered attendance records


    return render_template('attendance_list.html', attendance_records=attendance_records), 200



# Check-in function
@ab.route('/check_in/<int:employee_id>', methods=['POST'])
def check_in(employee_id):
   
        # Check if the employee exists
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee does not exist!"}), 404


    today = datetime.now().date()

    # Check if the employee already checked in today
    existing_attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()

    if existing_attendance and existing_attendance.time_in:
        return jsonify({"message": "Already checked in today!"}), 200

    if existing_attendance and existing_attendance.employee_status in ['absent', 'leave']:
        return jsonify({"error": "Cannot check out while status is 'absent' or 'leave'."}), 400

    # Create a new attendance record or update if record exists
    if not existing_attendance:
        attendance = Attendance(
            employee_id=employee_id,
            date=today,
            time_in=datetime.now().time(),
            work_hours=0,
            overtime_hours=0,
            employee_status='present'
        )
        db.session.add(attendance)
        
    else:
        existing_attendance.time_in = datetime.now()

    db.session.commit()

    return jsonify({"message": "Check-in successful!"}), 200

@ab.route('/checking')
def attendance_page():
    return render_template('attendance_buttons.html')


# Check-out function
@ab.route('/check_out/<int:employee_id>', methods=['POST'])
def check_out(employee_id):
    
    # Check if the employee exists
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee does not exist!"}), 404


    today = datetime.now().date()

    # Find the employee's attendance record for today
    attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()

    if not attendance or not attendance.time_in:
        return jsonify({"error": "You have not checked in today!"}), 400

    if attendance.time_out:
        return jsonify({"message": "Already checked out today!"}), 200

    # Set the check-out time and calculate work hours
    attendance.time_out = datetime.now().time()
    datetime_in = datetime.combine(today, attendance.time_in)
    datetime_out = datetime.combine(today, attendance.time_out)    
    time_diff = datetime_out - datetime_in
    total_time= round(time_diff.total_seconds() / 3600, 2)
    attendance.work_hours = min(8.0, total_time)
    attendance.overtime_hours= max(0.0, total_time-8.0)

    db.session.commit()

    return jsonify({"message": "Check-out successful!"}), 200



@ab.route('/data', methods=['GET'])
def get_attendance_data():
    # Query to count attendance by status
    attendance_data = Attendance.query.with_entities(
        Attendance.employee_status, db.func.count(Attendance.attendance_id)
    ).group_by(Attendance.employee_status).all()

    # Convert the result to a list of dictionaries or tuples
    attendance_data_list = [{'status': status, 'count': count} for status, count in attendance_data]

    # Return the data in a JSON format
    return jsonify(attendance_data_list)

@ab.route('/chart')
def attendance_chart():
    return render_template('attendance_chart.html')

@ab.route('/chart2')
def attendance_chart2():
    return render_template('attendance_chart2.html')