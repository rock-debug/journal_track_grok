import pytest
from unittest.mock import patch
from app.models import ResearchPaper

def test_crossref_search_and_save(auth_client, researcher_user):
    mock_results = [{
        'title': 'Mocked Quantum Paper',
        'authors': 'Mock Author',
        'journal': 'Mock Journal',
        'publication_year': 2024,
        'doi': '10.1000/mock.doi.123',
        'url': 'https://doi.org/10.1000/mock.doi.123',
        'abstract': 'Mock abstract content',
        'keywords': 'Quantum'
    }]

    with patch('app.routes.search.search_crossref', return_value=mock_results):
        resp = auth_client.get('/search/crossref?q=quantum')
        assert resp.status_code == 200
        assert b'Mocked Quantum Paper' in resp.data

    # Save to library
    resp_save = auth_client.post('/search/save_paper', data={
        'title': 'Mocked Quantum Paper',
        'authors': 'Mock Author',
        'journal': 'Mock Journal',
        'publication_year': '2024',
        'doi': '10.1000/mock.doi.123',
        'url': 'https://doi.org/10.1000/mock.doi.123',
        'abstract': 'Mock abstract content',
        'keywords': 'Quantum'
    }, follow_redirects=True)
    assert resp_save.status_code == 200
    saved = ResearchPaper.query.filter_by(doi='10.1000/mock.doi.123').first()
    assert saved is not None
    assert saved.user_id == researcher_user.id
