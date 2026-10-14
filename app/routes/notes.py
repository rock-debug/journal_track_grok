from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Note, ResearchPaper, Patent

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/notes')
@login_required
def index():
    query = request.args.get('q', '').strip()
    notes_query = Note.query.filter_by(user_id=current_user.id)
    
    if query:
        notes_query = notes_query.filter(Note.content.ilike(f"%{query}%"))
        
    notes = notes_query.order_by(Note.updated_at.desc()).all()
    return render_template('notes/index.html', notes=notes, query=query)

@notes_bp.route('/notes/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        paper_id_raw = request.form.get('paper_id', '').strip()
        patent_id_raw = request.form.get('patent_id', '').strip()
        
        if not content:
            flash('Note content cannot be empty.', 'danger')
            return redirect(request.referrer or url_for('notes.index'))
            
        paper_id = int(paper_id_raw) if paper_id_raw and paper_id_raw.isdigit() else None
        patent_id = int(patent_id_raw) if patent_id_raw and patent_id_raw.isdigit() else None
        
        if paper_id:
            paper = db.session.get(ResearchPaper, paper_id)
            if not paper or paper.user_id != current_user.id:
                abort(403)
        if patent_id:
            patent = db.session.get(Patent, patent_id)
            if not patent or patent.user_id != current_user.id:
                abort(403)
                
        note = Note(
            user_id=current_user.id,
            paper_id=paper_id,
            patent_id=patent_id,
            content=content
        )
        
        db.session.add(note)
        db.session.commit()
        
        flash('Note created successfully!', 'success')
        
        if paper_id:
            return redirect(url_for('papers.detail', paper_id=paper_id))
        elif patent_id:
            return redirect(url_for('patents.edit', patent_id=patent_id))
            
        return redirect(url_for('notes.index'))
        
    papers = ResearchPaper.query.filter_by(user_id=current_user.id).all()
    patents = Patent.query.filter_by(user_id=current_user.id).all()
    
    selected_paper_id = request.args.get('paper_id')
    selected_patent_id = request.args.get('patent_id')
    
    return render_template(
        'notes/create.html',
        papers=papers,
        patents=patents,
        selected_paper_id=selected_paper_id,
        selected_patent_id=selected_patent_id
    )

@notes_bp.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(note_id):
    note = db.session.get(Note, note_id)
    if not note:
        abort(404)
    if note.user_id != current_user.id:
        abort(403)
        
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        paper_id_raw = request.form.get('paper_id', '').strip()
        patent_id_raw = request.form.get('patent_id', '').strip()
        
        if not content:
            flash('Note content cannot be empty.', 'danger')
            return render_template('notes/edit.html', note=note)
            
        paper_id = int(paper_id_raw) if paper_id_raw and paper_id_raw.isdigit() else None
        patent_id = int(patent_id_raw) if patent_id_raw and patent_id_raw.isdigit() else None
        
        if paper_id:
            paper = db.session.get(ResearchPaper, paper_id)
            if not paper or paper.user_id != current_user.id:
                abort(403)
        if patent_id:
            patent = db.session.get(Patent, patent_id)
            if not patent or patent.user_id != current_user.id:
                abort(403)
                
        note.content = content
        note.paper_id = paper_id
        note.patent_id = patent_id
        
        db.session.commit()
        flash('Note updated successfully.', 'success')
        return redirect(url_for('notes.index'))
        
    papers = ResearchPaper.query.filter_by(user_id=current_user.id).all()
    patents = Patent.query.filter_by(user_id=current_user.id).all()
    return render_template('notes/edit.html', note=note, papers=papers, patents=patents)

@notes_bp.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete(note_id):
    note = db.session.get(Note, note_id)
    if not note:
        abort(404)
    if note.user_id != current_user.id:
        abort(403)
        
    db.session.delete(note)
    db.session.commit()
    
    flash('Note deleted.', 'info')
    redirect_target = request.referrer
    if redirect_target:
        return redirect(redirect_target)
    return redirect(url_for('notes.index'))
