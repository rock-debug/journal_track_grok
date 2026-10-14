import pytest
from unittest.mock import patch, MagicMock
from app.extensions import db
from app.models import ResearchPaper

def test_ai_summarization(auth_client, researcher_user):
    paper = ResearchPaper(
        user_id=researcher_user.id,
        title='Transformer Architecture Paper',
        authors='Vaswani et al.',
        abstract='Attention mechanism replaces recurrent networks.',
        keywords='NLP, Transformer'
    )
    db.session.add(paper)
    db.session.commit()

    with patch('app.services.groq_service.get_groq_client') as mock_client_factory:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content='### Research Problem\nAttention mechanism'))]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_client_factory.return_value = mock_client

        resp = auth_client.post(f'/ai/summarize/{paper.id}', headers={'X-Requested-With': 'XMLHttpRequest'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'Research Problem' in data['summary']

def test_citation_generation(auth_client, researcher_user):
    paper = ResearchPaper(
        user_id=researcher_user.id,
        title='Attention Is All You Need',
        authors='Vaswani, A.',
        journal='NeurIPS',
        publication_year=2017,
        doi='10.48550/arXiv.1706.03762'
    )
    db.session.add(paper)
    db.session.commit()

    resp = auth_client.post(f'/ai/citation/{paper.id}', json={'style': 'APA'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'Vaswani' in data['citation']

def test_rag_question_answering(auth_client, researcher_user):
    paper = ResearchPaper(
        user_id=researcher_user.id,
        title='Convolutional Neural Networks for Vision',
        authors='LeCun et al.',
        abstract='Convolutional layers extract spatial hierarchies in images.'
    )
    db.session.add(paper)
    db.session.commit()

    with patch('app.services.groq_service.get_groq_client') as mock_client_factory:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content='Convolutional networks use spatial layers.'))]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_client_factory.return_value = mock_client

        resp = auth_client.post('/ai/ask', json={'question': 'What layers are used in vision models?'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'answer' in data
        assert len(data['sources']) > 0
