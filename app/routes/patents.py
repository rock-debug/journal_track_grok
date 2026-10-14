from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Patent, Note

patents_bp = Blueprint('patents', __name__)

def parse_date(date_str):
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
    except ValueError:
        return None

@patents_bp.route('/patents')
@login_required
def index():
    query = request.args.get('q', '').strip()
    patents_query = Patent.query.filter_by(user_id=current_user.id)
    
    if query:
        search_pattern = f"%{query}%"
        patents_query = patents_query.filter(
            (Patent.title.ilike(search_pattern)) |
            (Patent.patent_number.ilike(search_pattern)) |
            (Patent.description.ilike(search_pattern))
        )
        
    patents = patents_query.order_by(Patent.created_at.desc()).all()
    return render_template('patents/index.html', patents=patents, query=query)

@patents_bp.route('/patents/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        patent_number = request.form.get('patent_number', '').strip()
        description = request.form.get('description', '').strip()
        filing_date_str = request.form.get('filing_date', '').strip()
        pub_date_str = request.form.get('publication_date', '').strip()
        url = request.form.get('url', '').strip()
        
        if not title:
            flash('Patent title is required.', 'danger')
            return render_template('patents/create.html')
            
        patent = Patent(
            user_id=current_user.id,
            title=title,
            patent_number=patent_number,
            description=description,
            filing_date=parse_date(filing_date_str),
            publication_date=parse_date(pub_date_str),
            url=url
        )
        
        db.session.add(patent)
        db.session.commit()
        
        flash('Patent created successfully!', 'success')
        return redirect(url_for('patents.index'))
        
    return render_template('patents/create.html')

@patents_bp.route('/patents/<int:patent_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(patent_id):
    patent = Patent.query.get_or_404(patent_id)
    if patent.user_id != current_user.id:
        abort(403)
        
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title cannot be empty.', 'danger')
            return render_template('patents/edit.html', patent=patent)
            
        patent.title = title
        patent.patent_number = request.form.get('patent_number', '').strip()
        patent.description = request.form.get('description', '').strip()
        patent.filing_date = parse_date(request.form.get('filing_date', ''))
        patent.publication_date = parse_date(request.form.get('publication_date', ''))
        patent.url = request.form.get('url', '').strip()
        
        db.session.commit()
        flash('Patent updated successfully.', 'success')
        return redirect(url_for('patents.index'))
        
    notes = Note.query.filter_by(patent_id=patent.id, user_id=current_user.id).all()
    return render_template('patents/edit.html', patent=patent, notes=notes)

@patents_bp.route('/patents/<int:patent_id>/delete', methods=['POST'])
@login_required
def delete(patent_id):
    patent = Patent.query.get_or_404(patent_id)
    if patent.user_id != current_user.id:
        abort(403)
        
    db.session.delete(patent)
    db.session.commit()
    
    flash('Patent record deleted.', 'info')
    return redirect(url_for('patents.index'))
