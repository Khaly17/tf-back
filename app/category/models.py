import uuid
from app import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255),unique=True, nullable=False)
    
    items = db.relationship('Item', backref='type', lazy=True)
