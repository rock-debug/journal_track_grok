import pytest
from app.extensions import db
from app.models import ResearchPaper

def test_create_paper(auth_client, researcher_user):
    response = auth_client.post('/papers/create', data={
        'title': 'Test Quantum Computing Paper',
        'authors': 'Alice, Bob',
        'journal': 'Nature Physics',
        'publication_year': '2023',
        'doi': '10.1038/s41567-023-00001-x',
        'url': 'https://example.com/paper',
        'abstract': 'Abstract about quantum computing.',
        'keywords': 'Quantum, Computing',
        'status': 'Unread'
    }, follow_redirects=True)
    assert response.status_code == 200
    paper = ResearchPaper.query.filter_by(title='Test Quantum Computing Paper').first()
    assert paper is not None
    assert paper.user_id == researcher_user.id
    assert paper.doi == '10.1038/s41567-023-00001-x'

def test_paper_detail(auth_client, researcher_user):
    paper = ResearchPaper(
        user_id=researcher_user.id,
        title='Sample Paper for Detail Test',
        authors='Charlie',
        abstract='Detailed abstract'
    )
    db.session.add(paper)
    db.session.commit()

    response = auth_client.get(f'/papers/{paper.id}')
    assert response.status_code == 200
    assert b'Sample Paper for Detail Test' in response.data

def test_paper_user_isolation(client, researcher_user, second_user):
    # Paper created by researcher_user
    paper = ResearchPaper(
        user_id=researcher_user.id,
        title='Private Researcher Paper',
        authors='Secret Author'
    )
    db.session.add(paper)
    db.session.commit()

    # Log in as second_user
    client.post('/login', data={'username': 'other_researcher', 'password': 'password123'}, follow_redirects=True)

    # Attempt to access researcher_user's paper
    response = client.get(f'/papers/{paper.id}')
    assert response.status_code == 403

def test_edit_paper(auth_client, researcher_user):
    paper = ResearchPaper(
        user_id=researcher_user.id,
        title='Original Title',
        authors='Original Author'
    )
    db.session.add(paper)
    db.session.commit()

    response = auth_client.post(f'/papers/{paper.id}/edit', data={
        'title': 'Updated Title',
        'authors': 'Updated Author',
        'status': 'Completed'
    }, follow_redirects=True)
    assert response.status_code == 200
    updated = ResearchPaper.query.get(paper.id)
    assert updated.title == 'Updated Title'
    assert updated.status == 'Completed'

def test_delete_paper(auth_client, researcher_user):
    paper = ResearchPaper(
        user_id=researcher_user.id,
        title='Paper to Delete'
    )
    db.session.add(paper)
    db.session.commit()

    response = auth_client.post(f'/papers/{paper.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert ResearchPaper.query.get(paper.id) is None
