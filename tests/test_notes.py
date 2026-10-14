import pytest
from app.extensions import db
from app.models import Note, ResearchPaper

def test_notes_crud(auth_client, researcher_user):
    paper = ResearchPaper(user_id=researcher_user.id, title='Paper for Note Test')
    db.session.add(paper)
    db.session.commit()

    # Create note linked to paper
    resp = auth_client.post('/notes/create', data={
        'paper_id': str(paper.id),
        'content': 'Important observation regarding theorem 1.'
    }, follow_redirects=True)
    assert resp.status_code == 200

    note = Note.query.filter_by(paper_id=paper.id).first()
    assert note is not None
    assert note.user_id == researcher_user.id

    # Edit note
    resp = auth_client.post(f'/notes/{note.id}/edit', data={
        'content': 'Updated observation text.'
    }, follow_redirects=True)
    assert resp.status_code == 200
    updated = Note.query.get(note.id)
    assert updated.content == 'Updated observation text.'

    # Delete note
    resp = auth_client.post(f'/notes/{note.id}/delete', follow_redirects=True)
    assert resp.status_code == 200
    assert Note.query.get(note.id) is None
