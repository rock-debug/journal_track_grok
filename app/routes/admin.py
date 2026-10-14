from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_authenticated or current_user.role != 'admin':
        abort(403)

@admin_bp.route('/admin')
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/index.html', users=users)

@admin_bp.route('/admin/users/<int:user_id>/role', methods=['POST'])
def change_role(user_id):
    if user_id == current_user.id:
        flash("You cannot change your own admin role.", "warning")
        return redirect(url_for('admin.index'))
        
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', 'researcher')
    if new_role in ['researcher', 'admin']:
        user.role = new_role
        db.session.commit()
        flash(f"User {user.username}'s role updated to {new_role}.", "success")
        
    return redirect(url_for('admin.index'))

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if user_id == current_user.id:
        flash("You cannot delete your own account from the admin dashboard.", "warning")
        return redirect(url_for('admin.index'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User {user.username} deleted successfully.", "info")
    return redirect(url_for('admin.index'))
