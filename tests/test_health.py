import pytest

def test_health_check(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'healthy'
    assert data['database_connected'] is True
    assert 'version' in data
