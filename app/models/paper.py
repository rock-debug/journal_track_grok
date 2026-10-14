from datetime import datetime
from app.extensions import db

class ResearchPaper(db.Model):
    __tablename__ = 'research_papers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.Text, nullable=True)
    abstract = db.Column(db.Text, nullable=True)
    journal = db.Column(db.String(255), nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    doi = db.Column(db.String(100), nullable=True, index=True)
    url = db.Column(db.String(500), nullable=True)
    keywords = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Unread')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    notes = db.relationship('Note', backref='paper', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<ResearchPaper {self.title}>'
