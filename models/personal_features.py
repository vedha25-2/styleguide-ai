from datetime import datetime
from database.db import db

class PersonalFeatures(db.Model):
    __tablename__ = 'personal_features'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    height_cm = db.Column(db.Float, default=165.0)
    weight_kg = db.Column(db.Float, default=58.0)
    skin_tone = db.Column(db.String(50), default='Medium')
    skin_hex = db.Column(db.String(10), default='#d29a6b')
    skin_undertone = db.Column(db.String(20), default='Warm')
    body_shape = db.Column(db.String(50), default='Hourglass')
    photo_path = db.Column(db.String(255), nullable=True)
    analysis_notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'skin_tone': self.skin_tone,
            'skin_hex': self.skin_hex,
            'skin_undertone': self.skin_undertone,
            'body_shape': self.body_shape,
            'photo_path': self.photo_path,
            'analysis_notes': self.analysis_notes,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else ''
        }

    def __repr__(self):
        return f"<PersonalFeatures User:{self.user_id} Shape:{self.body_shape}>"
