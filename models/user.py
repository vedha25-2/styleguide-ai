from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(20), default='Not Specified')
    age = db.Column(db.Integer, nullable=True)
    profile_image = db.Column(db.String(255), default='avatar-default.svg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wardrobe_items = db.relationship('WardrobeItem', backref='owner', cascade='all, delete-orphan', lazy=True)
    personal_features = db.relationship('PersonalFeatures', backref='user', uselist=False, cascade='all, delete-orphan', lazy=True)
    outfits = db.relationship('Outfit', backref='user', cascade='all, delete-orphan', lazy=True)
    favorites = db.relationship('Favorite', backref='user', cascade='all, delete-orphan', lazy=True)
    recommendations = db.relationship('RecommendationHistory', backref='user', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
