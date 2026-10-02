from datetime import datetime
from database.db import db

class RecommendationHistory(db.Model):
    __tablename__ = 'recommendation_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    occasion = db.Column(db.String(50), nullable=False)
    selected_items_summary = db.Column(db.Text, nullable=False)
    jewellery_recommendation = db.Column(db.Text, nullable=False)
    footwear_recommendation = db.Column(db.Text, nullable=False)
    accessory_recommendation = db.Column(db.Text, nullable=False)
    style_score = db.Column(db.Integer, default=90)
    why_it_works = db.Column(db.Text, nullable=False)
    color_compatibility = db.Column(db.String(100), default='Harmonious')
    item_ids_json = db.Column(db.Text, nullable=True)  # JSON array of selected item IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RecommendationHistory User:{self.user_id} Occasion:{self.occasion}>"
