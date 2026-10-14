import pytest
from app.models.user import User

def test_register_user(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword',
        'role': 'researcher'
    }, follow_redirects=True)
    assert response.status_code == 200
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'newuser@example.com'
    assert user.check_password('securepassword')

def test_register_duplicate_email(client, researcher_user):
    response = client.post('/register', data={
        'username': 'anotheruser',
        'email': 'researcher@test.com',
        'password': 'password123',
        'role': 'researcher'
    }, follow_redirects=True)
    assert b'Email is already registered' in response.data

def test_login_success(client, researcher_user):
    response = client.post('/login', data={
        'username': 'test_researcher',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged in successfully' in response.data or b'Welcome back' in response.data

def test_login_invalid_credentials(client, researcher_user):
    response = client.post('/login', data={
        'username': 'test_researcher',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b'Invalid credentials' in response.data

def test_logout(auth_client):
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out successfully' in response.data
