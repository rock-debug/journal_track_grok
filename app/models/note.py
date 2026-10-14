from datetime import datetime
from app.extensions import db

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('research_papers.id', ondelete='CASCADE'), nullable=True, index=True)
    patent_id = db.Column(db.Integer, db.ForeignKey('patents.id', ondelete='CASCADE'), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.id}>'
