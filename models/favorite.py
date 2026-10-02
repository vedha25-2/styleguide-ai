from datetime import datetime
from database.db import db

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    item_type = db.Column(db.String(20), nullable=False)  # 'item' or 'outfit'
    wardrobe_item_id = db.Column(db.Integer, db.ForeignKey('wardrobe_items.id', ondelete='CASCADE'), nullable=True)
    outfit_id = db.Column(db.Integer, db.ForeignKey('outfits.id', ondelete='CASCADE'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wardrobe_item = db.relationship('WardrobeItem', foreign_keys=[wardrobe_item_id])
    outfit = db.relationship('Outfit', foreign_keys=[outfit_id])

    def __repr__(self):
        return f"<Favorite User:{self.user_id} Type:{self.item_type}>"
