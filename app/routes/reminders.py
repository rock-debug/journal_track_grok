from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Reminder

reminders_bp = Blueprint('reminders', __name__)

@reminders_bp.route('/reminders')
@login_required
def index():
    user_id = current_user.id
    upcoming = Reminder.query.filter_by(user_id=user_id, completed=False).order_by(Reminder.reminder_date.asc()).all()
    completed = Reminder.query.filter_by(user_id=user_id, completed=True).order_by(Reminder.reminder_date.desc()).all()
    return render_template('reminders/index.html', upcoming=upcoming, completed=completed)

@reminders_bp.route('/reminders/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        reminder_date_str = request.form.get('reminder_date', '').strip()
        
        if not title or not reminder_date_str:
            flash('Title and reminder date are required.', 'danger')
            return render_template('reminders/create.html')
            
        try:
            if 'T' in reminder_date_str:
                reminder_date = datetime.strptime(reminder_date_str, '%Y-%m-%dT%H:%M')
            else:
                reminder_date = datetime.strptime(reminder_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date/time format.', 'danger')
            return render_template('reminders/create.html')
            
        reminder = Reminder(
            user_id=current_user.id,
            title=title,
            description=description,
            reminder_date=reminder_date,
            completed=False
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        flash('Reminder created successfully!', 'success')
        return redirect(url_for('reminders.index'))
        
    return render_template('reminders/create.html')

@reminders_bp.route('/reminders/<int:reminder_id>/complete', methods=['POST'])
@login_required
def complete(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    if reminder.user_id != current_user.id:
        abort(403)
        
    reminder.completed = not reminder.completed
    db.session.commit()
    
    status_str = "completed" if reminder.completed else "re-opened"
    flash(f'Reminder marked as {status_str}.', 'success')
    return redirect(url_for('reminders.index'))

@reminders_bp.route('/reminders/<int:reminder_id>/delete', methods=['POST'])
@login_required
def delete(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    if reminder.user_id != current_user.id:
        abort(403)
        
    db.session.delete(reminder)
    db.session.commit()
    
    flash('Reminder deleted.', 'info')
    return redirect(url_for('reminders.index'))
