from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for
from models import db, Role

role_bp = Blueprint('role', __name__)

@role_bp.route('/salary-setup', methods=['GET', 'POST'])
def role_salary_setup():
    # Fetch all roles from the database using SQLAlchemy ORM
    roles = Role.query.all()

    if request.method == 'POST':
        # Get data from the form
        role_id = request.form.get('role_id')
        base_salary = request.form.get('base_salary')
        salary_type = request.form.get('salary_type')

        # Find the role by ID
        role = Role.query.get(role_id)
        if role:
            # Update role salary and type information
            role.base_salary = float(base_salary)
            role.salary_type = salary_type
            db.session.commit()
            return jsonify({'message': 'Role salary data updated successfully!'}), 200
        else:
            return jsonify({'error': 'Role not found.'}), 404  # Handle case where role is not found
        
    return render_template('role_salary_setup.html', roles=roles)
