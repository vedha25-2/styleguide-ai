from datetime import datetime
from database.db import db

class WardrobeItem(db.Model):
    __tablename__ = 'wardrobe_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    main_category = db.Column(db.String(50), nullable=False)  # 'Clothes', 'Jewellery', 'Footwear', 'Accessories'
    sub_category = db.Column(db.String(50), nullable=False)   # 'Tops', 'Jeans', 'Sneakers', etc.
    color = db.Column(db.String(50), default='Unknown')
    hex_code = db.Column(db.String(10), default='#888888')
    style = db.Column(db.String(50), default='Casual')        # 'Casual', 'Formal', 'Chic', 'Boho', 'Sporty', 'Traditional', etc.
    occasion = db.Column(db.String(50), default='Casual')     # 'Casual', 'Office', 'Party', 'Wedding', etc.
    image_path = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'main_category': self.main_category,
            'sub_category': self.sub_category,
            'color': self.color,
            'hex_code': self.hex_code,
            'style': self.style,
            'occasion': self.occasion,
            'image_path': self.image_path,
            'is_favorite': self.is_favorite
        }

    def __repr__(self):
        return f"<WardrobeItem {self.name} ({self.sub_category})>"
