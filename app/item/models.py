import uuid
from app import db
from datetime import datetime

class Item(db.Model):
    __tablename__ = 'items'
    
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    type_id = db.Column(db.String(36), db.ForeignKey('categories.id'))
    unique_number = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(100))
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    notifications = db.relationship('Notification', backref='item', lazy=True)
    history = db.relationship('History', backref='item', lazy=True)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    item_id = db.Column(db.String(36), db.ForeignKey('items.id'))
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class History(db.Model):
    __tablename__ = 'history'
    
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = db.Column(db.String(36), db.ForeignKey('items.id'))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    action = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
