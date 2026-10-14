import csv
import io
from flask import Blueprint, Response, make_response
from flask_login import login_required, current_user
from app.models import ResearchPaper, Patent

export_bp = Blueprint('export', __name__)

@export_bp.route('/export/papers')
@login_required
def export_papers():
    papers = ResearchPaper.query.filter_by(user_id=current_user.id).order_by(ResearchPaper.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['title', 'authors', 'journal', 'year', 'doi', 'url', 'status'])
    
    for paper in papers:
        writer.writerow([
            paper.title or '',
            paper.authors or '',
            paper.journal or '',
            paper.publication_year or '',
            paper.doi or '',
            paper.url or '',
            paper.status or ''
        ])
        
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=research_papers.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response

@export_bp.route('/export/patents')
@login_required
def export_patents():
    patents = Patent.query.filter_by(user_id=current_user.id).order_by(Patent.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['title', 'patent_number', 'description', 'filing_date', 'publication_date', 'url'])
    
    for patent in patents:
        writer.writerow([
            patent.title or '',
            patent.patent_number or '',
            patent.description or '',
            str(patent.filing_date) if patent.filing_date else '',
            str(patent.publication_date) if patent.publication_date else '',
            patent.url or ''
        ])
        
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=patents.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response

@export_bp.route('/export/papers/bibtex')
@login_required
def export_papers_bibtex():
    from app.services.citation_service import format_citation
    papers = ResearchPaper.query.filter_by(user_id=current_user.id).order_by(ResearchPaper.created_at.desc()).all()
    entries = [format_citation(paper, style='bibtex') for paper in papers]
    content = "\n\n".join(entries)
    
    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=research_papers.bib"
    response.headers["Content-type"] = "text/plain; charset=utf-8"
    return response

