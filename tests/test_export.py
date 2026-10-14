import pytest
from app.extensions import db
from app.models import ResearchPaper, Patent

def test_export_papers_csv(auth_client, researcher_user):
    paper = ResearchPaper(
        user_id=researcher_user.id,
        title='Exportable Paper',
        authors='Dr. Export',
        journal='CSV Journal',
        publication_year=2025,
        doi='10.1111/csv.123'
    )
    db.session.add(paper)
    db.session.commit()

    resp = auth_client.get('/export/papers')
    assert resp.status_code == 200
    assert resp.headers['Content-Type'].startswith('text/csv')
    assert b'Exportable Paper' in resp.data
    assert b'10.1111/csv.123' in resp.data

def test_export_patents_csv(auth_client, researcher_user):
    patent = Patent(
        user_id=researcher_user.id,
        title='Exportable Patent',
        patent_number='US 9,999,999'
    )
    db.session.add(patent)
    db.session.commit()

    resp = auth_client.get('/export/patents')
    assert resp.status_code == 200
    assert resp.headers['Content-Type'].startswith('text/csv')
    assert b'Exportable Patent' in resp.data
    assert b'US 9,999,999' in resp.data

def test_export_papers_bibtex(auth_client, researcher_user):
    paper = ResearchPaper(
        user_id=researcher_user.id,
        title='BibTeX Test Paper',
        authors='Alice Smith',
        journal='BibTeX Journal',
        publication_year=2026,
        doi='10.1000/bibtex.456'
    )
    db.session.add(paper)
    db.session.commit()

    resp = auth_client.get('/export/papers/bibtex')
    assert resp.status_code == 200
    assert b'@article' in resp.data or b'BibTeX Test Paper' in resp.data

