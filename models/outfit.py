from datetime import datetime
from database.db import db

class Outfit(db.Model):
    __tablename__ = 'outfits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    occasion = db.Column(db.String(50), default='Casual')
    season = db.Column(db.String(50), default='All-Season')
    
    top_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id', ondelete='SET NULL'), nullable=True)
    bottom_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id', ondelete='SET NULL'), nullable=True)
    dress_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id', ondelete='SET NULL'), nullable=True)
    footwear_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id', ondelete='SET NULL'), nullable=True)
    jewellery_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id', ondelete='SET NULL'), nullable=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id', ondelete='SET NULL'), nullable=True)

    style_score = db.Column(db.Integer, default=85)
    reasoning = db.Column(db.Text, nullable=True)
    color_harmony = db.Column(db.String(100), default='Balanced Complementary')
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to wardrobe items
    top = db.relationship('WardrobeItem', foreign_keys=[top_id])
    bottom = db.relationship('WardrobeItem', foreign_keys=[bottom_id])
    dress = db.relationship('WardrobeItem', foreign_keys=[dress_id])
    footwear = db.relationship('WardrobeItem', foreign_keys=[footwear_id])
    jewellery = db.relationship('WardrobeItem', foreign_keys=[jewellery_id])
    accessory = db.relationship('WardrobeItem', foreign_keys=[accessory_id])

    def get_items(self):
        items = []
        if self.dress:
            items.append(('Dress', self.dress))
        else:
            if self.top:
                items.append(('Top', self.top))
            if self.bottom:
                items.append(('Bottom', self.bottom))
        if self.footwear:
            items.append(('Footwear', self.footwear))
        if self.jewellery:
            items.append(('Jewellery', self.jewellery))
        if self.accessory:
            items.append(('Accessory', self.accessory))
        return items

    def __repr__(self):
        return f"<Outfit {self.name} ({self.occasion})>"
