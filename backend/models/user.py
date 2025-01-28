from extensions import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app
from decimal import Decimal
from sqlalchemy import DECIMAL

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    balance = db.Column(DECIMAL(10, 2), default=Decimal('0'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        """生成 JWT token"""
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256') 