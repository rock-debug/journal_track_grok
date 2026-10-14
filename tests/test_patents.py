import pytest
from app.extensions import db
from app.models import Patent

def test_patent_crud(auth_client, researcher_user):
    # Create
    resp = auth_client.post('/patents/create', data={
        'title': 'Test Battery Patent',
        'patent_number': 'US 9,876,543',
        'description': 'Solid state battery cell.'
    }, follow_redirects=True)
    assert resp.status_code == 200
    patent = Patent.query.filter_by(patent_number='US 9,876,543').first()
    assert patent is not None
    assert patent.user_id == researcher_user.id

    # Edit
    resp = auth_client.post(f'/patents/{patent.id}/edit', data={
        'title': 'Updated Battery Patent',
        'patent_number': 'US 9,876,543',
        'description': 'Updated solid state cell.'
    }, follow_redirects=True)
    assert resp.status_code == 200
    updated = Patent.query.get(patent.id)
    assert updated.title == 'Updated Battery Patent'

    # Delete
    resp = auth_client.post(f'/patents/{patent.id}/delete', follow_redirects=True)
    assert resp.status_code == 200
    assert Patent.query.get(patent.id) is None

def test_patent_authorization(client, researcher_user, second_user):
    patent = Patent(
        user_id=researcher_user.id,
        title='Private Patent',
        patent_number='US 1,111,111'
    )
    db.session.add(patent)
    db.session.commit()

    # Login second user
    client.post('/login', data={'username': 'other_researcher', 'password': 'password123'}, follow_redirects=True)
    resp = client.get(f'/patents/{patent.id}/edit')
    assert resp.status_code == 403
