from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models import User, Task
from forms import RegistrationForm, LoginForm, TaskForm

# Blueprint for main routes
main_routes = Blueprint('main_routes', __name__)

# Home Route: Redirect to dashboard
@main_routes.route('/')
def home():
    return redirect(url_for('main_routes.dashboard'))

# Dashboard Route: Shows task statistics and tasks
@main_routes.route('/dashboard')
@login_required
def dashboard():
    # Query tasks again to ensure you get the latest data
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    total_tasks = len(tasks)
    drafts = sum(1 for task in tasks if task.status == 'Draft') 

    # Filter tasks based on status if required
    pending_tasks = [task for task in tasks if task.status == 'Pending']  

    return render_template('dashboard.html', tasks=tasks, total_tasks=total_tasks, drafts=drafts, pending_tasks=pending_tasks)

# Register Route: User registration
@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_routes.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing_user:
            flash('Username or Email already exists. Please try again.', 'danger')
            return redirect(url_for('main_routes.register'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main_routes.login'))
    return render_template('register.html', form=form)

# Login Route: User login
@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_routes.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('main_routes.dashboard'))
        flash("Login Unsuccessful. Please check email and password.", 'danger')
    return render_template('login.html', form=form)

# Logout Route: User logout
@main_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main_routes.login'))

# New Task Route: Add new task
@main_routes.route('/new_task', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()  # Initialize form
    if form.validate_on_submit():  # If form passes validation
        try:
            task = Task(
                description=form.description.data,
                due_date=form.due_date.data,
                priority=form.priority.data,
                status=form.status.data,  # Capture status from the form
                user_id=current_user.id
            )
            db.session.add(task)
            db.session.commit()
            flash('Task added successfully!', 'success')
            return redirect(url_for('main_routes.dashboard'))
        except Exception as e:
            db.session.rollback()  # Rollback changes if an error occurs
            flash(f'Error adding task: {e}', 'danger')
            return redirect(url_for('main_routes.new_task'))
    else:
        if request.method == 'POST':  # If form submission failed
            flash('There were errors in your form. Please check the fields and try again.', 'danger')
    return render_template('new_task.html', form=form)

# Complete Task Route: Mark task as completed
@main_routes.route('/complete_task/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to update this task.', 'danger')
        return redirect(url_for('main_routes.dashboard'))
    task.completed = True
    db.session.commit()
    flash('Task marked as completed.', 'success')
    return redirect(url_for('main_routes.dashboard'))

# Delete Task Route: Delete task
@main_routes.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('main_routes.dashboard'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully.', 'success')
    return redirect(url_for('main_routes.dashboard'))

#Edit Task Route
@main_routes.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)  # Get the task by ID

    if task.user_id != current_user.id:  # Ensure the current user owns the task
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('main_routes.dashboard'))

    form = TaskForm(obj=task)  # Populate the form with existing data

    if form.validate_on_submit():  # Handle form submission
        try:
            task.description = form.description.data
            task.due_date = form.due_date.data
            task.priority = form.priority.data
            task.status = form.status.data  # Update status field
            db.session.commit()  # Commit changes to the database
            flash("Task updated successfully.", "success")
            return redirect(url_for('main_routes.dashboard'))  # Redirect to dashboard
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating task: {e}", "danger")
    elif request.method == 'POST':
        flash("There were errors in the form. Please check and try again.", "danger")

    return render_template('edit_task.html', form=form, task=task)

# View Task Route: View task details
@main_routes.route('/view_task/<int:task_id>')
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to view this task.', 'danger')
        return redirect(url_for('main_routes.dashboard'))
    return render_template('view_task.html', task=task)
