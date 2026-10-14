from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import ResearchPaper
from app.services.groq_service import summarize_paper
from app.services.citation_service import format_citation
from app.services.rag_service import query_rag_system
from app.services.recommendation_service import generate_user_recommendations

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai')
@login_required
def index():
    papers = ResearchPaper.query.filter_by(user_id=current_user.id).all()
    recommendations_data = generate_user_recommendations(current_user.id)
    return render_template('ai/index.html', papers=papers, recommendations=recommendations_data)

@ai_bp.route('/ai/summarize/<int:paper_id>', methods=['POST'])
@login_required
def summarize(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    if paper.user_id != current_user.id:
        abort(403)
        
    summary_md = summarize_paper(paper)
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "paper_id": paper.id, "summary": summary_md})
        
    flash("AI Summary Generated Successfully.", "success")
    return render_template('papers/detail.html', paper=paper, ai_summary=summary_md, notes=paper.notes)

@ai_bp.route('/ai/citation/<int:paper_id>', methods=['POST'])
@login_required
def citation(paper_id):
    paper = ResearchPaper.query.get_or_404(paper_id)
    if paper.user_id != current_user.id:
        abort(403)
        
    style = request.form.get('style', 'APA')
    if request.is_json:
        data = request.get_json() or {}
        style = data.get('style', style)
        
    citation_text = format_citation(paper, style=style)
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "style": style, "citation": citation_text})
        
    return jsonify({"success": True, "style": style, "citation": citation_text})

@ai_bp.route('/ai/ask', methods=['POST'])
@login_required
def ask():
    question = request.form.get('question', '').strip()
    if request.is_json:
        data = request.get_json() or {}
        question = data.get('question', question).strip()
        
    if not question:
        return jsonify({"error": "Question is required."}), 400
        
    rag_result = query_rag_system(current_user.id, question)
    return jsonify(rag_result)

@ai_bp.route('/ai/recommendations', methods=['GET'])
@login_required
def recommendations():
    rec_data = generate_user_recommendations(current_user.id)
    return jsonify(rec_data)
