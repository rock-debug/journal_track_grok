from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import ResearchPaper, Patent, Note, Reminder

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = current_user.id
    
    total_papers = ResearchPaper.query.filter_by(user_id=user_id).count()
    total_patents = Patent.query.filter_by(user_id=user_id).count()
    total_notes = Note.query.filter_by(user_id=user_id).count()
    pending_reminders = Reminder.query.filter_by(user_id=user_id, completed=False).count()
    
    recent_papers = ResearchPaper.query.filter_by(user_id=user_id).order_by(ResearchPaper.created_at.desc()).limit(5).all()
    recent_patents = Patent.query.filter_by(user_id=user_id).order_by(Patent.created_at.desc()).limit(5).all()
    upcoming_reminders = Reminder.query.filter_by(user_id=user_id, completed=False).order_by(Reminder.reminder_date.asc()).limit(5).all()
    
    return render_template(
        'dashboard/index.html',
        total_papers=total_papers,
        total_patents=total_patents,
        total_notes=total_notes,
        pending_reminders=pending_reminders,
        recent_papers=recent_papers,
        recent_patents=recent_patents,
        upcoming_reminders=upcoming_reminders
    )
