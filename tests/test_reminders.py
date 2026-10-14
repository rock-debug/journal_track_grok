import pytest
from app.extensions import db
from app.models import Reminder

def test_reminders_workflow(auth_client, researcher_user):
    # Create reminder
    resp = auth_client.post('/reminders/create', data={
        'title': 'Submit Review Report',
        'description': 'Review manuscript for IEEE journal.',
        'reminder_date': '2026-10-15T14:00'
    }, follow_redirects=True)
    assert resp.status_code == 200

    reminder = Reminder.query.filter_by(title='Submit Review Report').first()
    assert reminder is not None
    assert reminder.completed is False

    # Mark complete
    resp = auth_client.post(f'/reminders/{reminder.id}/complete', follow_redirects=True)
    assert resp.status_code == 200
    assert Reminder.query.get(reminder.id).completed is True

    # Delete
    resp = auth_client.post(f'/reminders/{reminder.id}/delete', follow_redirects=True)
    assert resp.status_code == 200
    assert Reminder.query.get(reminder.id) is None
