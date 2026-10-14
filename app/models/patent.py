from datetime import datetime
from app.extensions import db

class Patent(db.Model):
    __tablename__ = 'patents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    patent_number = db.Column(db.String(100), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    filing_date = db.Column(db.Date, nullable=True)
    publication_date = db.Column(db.Date, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    notes = db.relationship('Note', backref='patent', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Patent {self.patent_number}: {self.title}>'
