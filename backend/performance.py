from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for, session
from models import db, Employee, Performance, KPI, Goal, Achievement
from datetime import datetime

performance_bp = Blueprint('performance', __name__)

@performance_bp.route('/', methods=['GET'])
def list_performance():
    employee_id = request.args.get('employee_id', type=int)
    reviewer_id = request.args.get('reviewer_id', type=int)

    # Start querying performance records
    query = db.session.query(Performance).join(Employee, Performance.employee_id == Employee.employee_id)

    if employee_id:
        query = query.filter(Performance.employee_id == employee_id)

    if reviewer_id:
        query = query.filter(Performance.reviewer_id == reviewer_id)

    performance_records = query.all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('performance_table_body.html', performance_records=performance_records)

    return render_template('performance_list.html', performance_records=performance_records)

@performance_bp.route('/<int:performance_id>', methods=['GET'])
def view_performance(performance_id):
    performance = Performance.query.get_or_404(performance_id)

    kpis = KPI.query.filter_by(performance_id=performance_id).all()
    goals = Goal.query.filter_by(performance_id=performance_id).all()
    achievements = Achievement.query.filter_by(performance_id=performance_id).all()

    return render_template('performance_detail.html', performance=performance, kpis=kpis, goals=goals, achievements=achievements)

# Create - Add a New Performance Record
@performance_bp.route('/new', methods=['GET', 'POST'])
def create_performance():    
    if request.method == 'POST':
        # Get data from form
        employee_id = request.form.get('employee_id', type=int)
        reviewer_id = session['employee_id']
        review_score = request.form.get('review_score', type=float)
        review_date = request.form.get('review_date', type=str)

        if review_score is None or not (1 <= review_score <= 10):
            flash('Review score must be between 1 and 10. Please enter a valid score.', 'error')
            return render_template('performance_form.html', action='Create')

        new_performance = Performance(
            employee_id=employee_id,
            reviewer_id=reviewer_id,
            review_score=review_score,
            review_date=datetime.strptime(review_date, '%Y-%m-%d')
        )

        db.session.add(new_performance)
        db.session.commit()
        flash('Performance record created successfully!', 'success')
        return redirect(url_for('performance.list_performance'))

    return render_template('performance_form.html', action='Create')

# Update - Edit an Existing Performance Record
@performance_bp.route('/edit/<int:performance_id>', methods=['GET', 'POST'])
def edit_performance(performance_id):
    performance = Performance.query.get_or_404(performance_id)

    if request.method == 'POST':
        
        employee_id = request.form.get('employee_id', type=int)
        performance.review_score = request.form.get('review_score', type=float)
        performance.review_date = datetime.strptime(request.form.get('review_date', type=str), '%Y-%m-%d')

        db.session.commit()
        flash('Performance record updated successfully!', 'success')
        return redirect(url_for('performance.list_performance'))

    return render_template('performance_form.html', action='Edit', performance=performance)

# Delete - Remove a Performance Record
@performance_bp.route('/delete/<int:performance_id>', methods=['POST'])
def delete_performance(performance_id):
    performance = Performance.query.get_or_404(performance_id)

    for kpi in performance.kpis:
        db.session.delete(kpi)
    for goal in performance.goals:
        db.session.delete(goal)
    for achievement in performance.achievements:
        db.session.delete(achievement)

    db.session.delete(performance)
    db.session.commit()
    flash('Performance record deleted successfully!', 'success')
    return redirect(url_for('performance.list_performance'))

# Create a new KPI
@performance_bp.route('/kpi/new', methods=['GET', 'POST'])
def create_kpi():
    if request.method == 'POST':
        kpi_description = request.form.get('description',type=str)
        kpi_score = request.form.get('score',type=float)
        performance_id = request.form.get('performance_id',type=int)
        
        if kpi_score is None or not (1 <= kpi_score <= 5):
            flash('KPI score must be between 1 and 5. Please enter a valid score.', 'error')
            return render_template('kpi_form.html', performance_id=performance_id)

        new_kpi = KPI(
            kpi_description=kpi_description,
            kpi_score=kpi_score,
            performance_id=performance_id
        )
        db.session.add(new_kpi)
        db.session.commit()
        flash('KPI created successfully!', 'success')
        return redirect(url_for('performance.view_performance', performance_id=performance_id))
    
    performance_id = request.args.get('performance_id')
    return render_template('kpi_form.html', performance_id=performance_id)

# Update - Edit an Existing KPI
@performance_bp.route('/kpi/edit/<int:kpi_id>', methods=['GET','POST'])
def edit_kpi(kpi_id):
    kpi=KPI.query.get_or_404(kpi_id)

    if request.method == 'POST':
        kpi.kpi_description = request.form.get('description',type=str)
        kpi.kpi_score = request.form.get('score',type=float)
        performance_id = request.form.get('performance_id',type=int)

        if kpi.kpi_score is None or not (1 <= kpi.kpi_score <= 5):
            flash('KPI score must be between 1 and 5. Please enter a valid score.', 'error')
            return render_template('kpi_form.html', performance_id=performance_id)

        db.session.commit()
        flash('KPI edited successfully!', 'success')
        return redirect(url_for('performance.view_performance', performance_id=performance_id)) 
    return render_template('kpi_form.html', performance_id=kpi.performance_id, kpi=kpi)

@performance_bp.route('/kpi/delete/<int:kpi_id>', methods=['POST'])
def delete_kpi(kpi_id):
    kpi=KPI.query.get_or_404(kpi_id)

    db.session.delete(kpi)
    db.session.commit()

    flash('KPI deleted sucesssfully!', 'success')
    return redirect(url_for('performance.view_performance',performance_id=kpi.performance_id))

# Create a new goal
@performance_bp.route('/goal/new', methods=['GET', 'POST'])
def create_goal():
    valid_statuses = ['not started', 'in progress', 'achieved']
    if request.method == 'POST':
        goal_description = request.form.get('goal_description',type=str)
        goal_status = request.form.get('goal_status',type=str)
        performance_id = request.form.get('performance_id',type=int)
        
        if goal_status not in valid_statuses:
            flash(f'Invalid goal status! Please choose one of the following: {", ".join(valid_statuses)}', 'error')
            performance_id = request.args.get('performance_id')
            return render_template('goal_form.html', performance_id=performance_id)
        
        new_goal = Goal(
            goal_description=goal_description,
            goal_status=goal_status,
            performance_id=performance_id
        )
        db.session.add(new_goal)
        db.session.commit()
        flash('Goal created successfully!', 'success')
        return redirect(url_for('performance.view_performance', performance_id=performance_id))
    
    performance_id = request.args.get('performance_id')
    return render_template('goal_form.html', performance_id=performance_id)

#edit goal
@performance_bp.route('/goal/edit/<int:goal_id>', methods=['GET', 'POST'])
def edit_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    valid_statuses = ['not started', 'in progress', 'achieved']

    if request.method == 'POST':
        goal_description = request.form.get('goal_description', type=str)
        goal_status = request.form.get('goal_status', type=str)

        if goal_status not in valid_statuses:
            flash(f'Invalid goal status! Please choose one of the following: {", ".join(valid_statuses)}', 'error')
            return render_template('goal_form.html', goal=goal, performance_id=goal.performance_id)
        
        goal.goal_description = goal_description
        goal.goal_status = goal_status
        db.session.commit()
        flash('Goal updated successfully!', 'success')
        return redirect(url_for('performance.view_performance', performance_id=goal.performance_id))

    return render_template('goal_form.html', goal=goal, performance_id=goal.performance_id)

#delete goal
@performance_bp.route('/goal/delete/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully', 'success')
    return redirect(url_for('performance.view_performance', performance_id=goal.performance_id))

# Create a new Achievement
@performance_bp.route('/achievement/new', methods=['GET', 'POST'])
def create_achievement():
    if request.method == 'POST':
        achievement_description = request.form.get('achievement_description',type=str)
        achievement_date = request.form.get('achievement_date',type=str)
        performance_id = request.form.get('performance_id',type=int)
        try:
            achievement_date = datetime.strptime(achievement_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format!', 'danger')
            return redirect(url_for('create_achievement', performance_id=performance_id))

            
        new_achievement = Achievement(
            achievement_description=achievement_description,
            achievement_date=achievement_date,
            performance_id=performance_id
        )
        db.session.add(new_achievement)
        db.session.commit()
        flash('Achivement created successfully!', 'success')
        return redirect(url_for('performance.view_performance', performance_id=performance_id))
    
    performance_id = request.args.get('performance_id')
    return render_template('achievement_form.html', performance_id=performance_id)

#edit an achievement
@performance_bp.route('/achievement/edit/<int:achievement_id>', methods=['GET', 'POST'])
def edit_achievement(achievement_id):
    achievement = Achievement.query.get_or_404(achievement_id)

    if request.method == "POST":
        achievement_description = request.form.get('achievement_description',type=str)
        achievement_date = request.form.get('achievement_date',type=str)

        try:
            achievement_date = datetime.strptime(achievement_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format!', 'danger')
            return render_template('achievement_form.html', achievement=achievement, performance_id=achievement.performance_id)

        achievement.achievement_description = achievement_description
        achievement.achievement_date = achievement_date
        db.session.commit()
        flash('Achievement updated successfully!', 'success')
        return redirect(url_for('performance.view_performance', performance_id=achievement.performance_id))
    return render_template('achievement_form.html', achievement=achievement, performance_id=achievement.performance_id)

#delete an achievement
@performance_bp.route('/achievement/delete/<int:achievement_id>', methods=['GET', 'POST'])
def delete_achievement(achievement_id):
    achievement = Achievement.query.get_or_404(achievement_id)    
    db.session.delete(achievement)
    db.session.commit()
    flash('Achievement deleted successfully!', 'success')
    return redirect(url_for('performance.view_performance', performance_id=achievement.performance_id))
