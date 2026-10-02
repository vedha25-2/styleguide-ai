import os
import unittest
import base64
from io import BytesIO
from app import app, db
from models.user import User
from models.wardrobe import WardrobeItem
from models.personal_features import PersonalFeatures
from models.outfit import Outfit
from models.favorite import Favorite
from models.recommendation import RecommendationHistory

import tempfile

class StyleGuideAIE2ETestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_full_user_journey(self):
        """Exercises every single user journey and route in the system."""
        # 1. Register
        res = self.client.post('/register', data={
            'full_name': 'Aanya Kapoor',
            'email': 'aanya@fashion.ai',
            'password': 'secretPassword123',
            'confirm_password': 'secretPassword123',
            'gender': 'Female',
            'age': '22'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Aanya', res.data)

        # 2. View Dashboard
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'My Wardrobe', res.data)
        self.assertIn(b'AI Outfit Generator', res.data)

        # 3. Load Demo Wardrobe Data
        res = self.client.post('/load-demo-data', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Successfully loaded', res.data)

        # 4. View Wardrobe
        res = self.client.get('/wardrobe')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Crisp White Oxford Shirt', res.data)

        # 5. Add custom item with camera Base64 snapshot
        sample_b64 = "data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9").decode('utf-8')
        res = self.client.post('/wardrobe/add', data={
            'name': 'Velvet Evening Blazer',
            'main_category': 'Clothes',
            'sub_category': 'Jackets',
            'color': 'Midnight Blue',
            'style': 'Formal',
            'occasion': 'Party',
            'notes': 'Silk lapel tailored blazer',
            'camera_photo_base64': sample_b64
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Velvet Evening Blazer', res.data)

        # 6. Edit item
        with app.app_context():
            u = User.query.filter_by(email='aanya@fashion.ai').first()
            item = WardrobeItem.query.filter_by(user_id=u.id, name='Velvet Evening Blazer').first()
            self.assertIsNotNone(item)
            item_id = item.id

        res = self.client.post(f'/wardrobe/edit/{item_id}', data={
            'name': 'Royal Velvet Evening Blazer',
            'main_category': 'Clothes',
            'sub_category': 'Jackets',
            'color': 'Navy Blue',
            'hex_code': '#142350',
            'style': 'Formal',
            'occasion': 'Party',
            'notes': 'Updated blazer notes'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Royal Velvet Evening Blazer', res.data)

        # 7. Style studio consultation
        with app.app_context():
            u = User.query.filter_by(email='aanya@fashion.ai').first()
            shirt = WardrobeItem.query.filter_by(user_id=u.id, sub_category='Shirts').first()
            jeans = WardrobeItem.query.filter_by(user_id=u.id, sub_category='Jeans').first()

        res = self.client.post('/style/recommend', data={
            'occasion': 'Office',
            'top_id': str(shirt.id),
            'bottom_id': str(jeans.id)
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'AI Style Report', res.data)
        self.assertIn(b'Jewellery Recommendation', res.data)
        self.assertIn(b'Footwear Recommendation', res.data)

        # 8. Save Styled Outfit
        res = self.client.post('/style/save-outfit', data={
            'occasion': 'Office',
            'top_id': str(shirt.id),
            'bottom_id': str(jeans.id),
            'style_score': '93',
            'reasoning': 'Timeless classic pairing with optimal proportions',
            'color_harmony': 'Neutral Complementary'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Outfit saved to your Favorites', res.data)

        # 9. Personal Features Analysis (simulated camera capture)
        res = self.client.post('/personal-features/analyze', data={
            'camera_photo_base64': sample_b64
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Computer vision analysis complete', res.data)

        # 10. AI Outfit Generator
        res = self.client.post('/outfit-generator/generate', data={
            'occasion': 'Party',
            'season': 'Summer',
            'preferred_color': 'Pink',
            'preferred_style': 'Chic'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'AI Curated Ensemble', res.data)

        # 11. Save AI Generated Outfit
        res = self.client.post('/outfit-generator/save', data={
            'name': 'Party Chic Look',
            'occasion': 'Party',
            'season': 'Summer',
            'top_id': str(shirt.id),
            'bottom_id': str(jeans.id),
            'style_score': '95',
            'reasoning': 'Sleek and polished party look',
            'color_harmony': 'Monochromatic Chic'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Generated outfit saved to your Favorites', res.data)

        # 12. Outfit History
        res = self.client.get('/outfit-history')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Recommendation History', res.data)
        self.assertIn(b'Office Consultation', res.data)

        # 13. Favorites page
        res = self.client.get('/favorites')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Party Chic Look', res.data)

        # 14. Profile Update
        res = self.client.post('/profile/update', data={
            'full_name': 'Aanya Kapoor Style Pro',
            'gender': 'Female',
            'age': '23'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Profile updated successfully', res.data)

        # 15. Delete piece
        res = self.client.post(f'/wardrobe/delete/{item_id}', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'was removed from your wardrobe', res.data)

        # 16. Logout
        res = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'signed out safely', res.data)

if __name__ == '__main__':
    unittest.main()
