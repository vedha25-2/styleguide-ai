import os
import unittest
import tempfile
import cv2
import numpy as np
from PIL import Image
from app import app, db
from models.user import User
from models.wardrobe import WardrobeItem
from models.personal_features import PersonalFeatures
from models.outfit import Outfit
from models.favorite import Favorite
from models.recommendation import RecommendationHistory
from sample_data import load_sample_wardrobe_for_user
from ml.color_extractor import extract_dominant_color, calculate_color_harmony_score
from ml.personal_analyzer import analyze_personal_features
from ml.recommender import generate_style_recommendation, generate_ai_outfit

class StyleGuideAITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.config['DATABASE']}"
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        try:
            os.close(self.db_fd)
            os.unlink(app.config['DATABASE'])
        except Exception:
            pass

    def test_user_registration_and_login(self):
        """Test registration, duplicate prevention, and login authentication."""
        # 1. Register User 1
        resp = self.client.post('/register', data={
            'full_name': 'Vedha Sharma',
            'email': 'vedha@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'gender': 'Female',
            'age': '24'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Vedha', resp.data)

        # Logout to test duplicate registration from unauthenticated session
        self.client.get('/logout', follow_redirects=True)

        # 2. Prevent duplicate email registration
        resp_dup = self.client.post('/register', data={
            'full_name': 'Duplicate User',
            'email': 'vedha@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'gender': 'Female'
        }, follow_redirects=True)
        self.assertIn(b'already exists', resp_dup.data)

        # 3. Failed login
        resp_fail = self.client.post('/login', data={
            'email': 'vedha@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', resp_fail.data)

        # 4. Successful login
        resp_succ = self.client.post('/login', data={
            'email': 'vedha@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(resp_succ.status_code, 200)
        self.assertIn(b'Vedha', resp_succ.data)

    def test_sample_wardrobe_loading_and_isolation(self):
        """Test loading demo wardrobe items and strict isolation between two accounts."""
        # Create User A
        with app.app_context():
            u1 = User(full_name='User A', email='usera@example.com')
            u1.set_password('pass123')
            db.session.add(u1)
            
            u2 = User(full_name='User B', email='userb@example.com')
            u2.set_password('pass123')
            db.session.add(u2)
            db.session.commit()

            # Load demo wardrobe for User A
            count1 = load_sample_wardrobe_for_user(u1.id, app.root_path)
            self.assertEqual(count1, 12)

            # Check User A items count
            items_a = WardrobeItem.query.filter_by(user_id=u1.id).all()
            self.assertEqual(len(items_a), 12)

            # Check User B has 0 items (strict isolation)
            items_b = WardrobeItem.query.filter_by(user_id=u2.id).all()
            self.assertEqual(len(items_b), 0)

    def test_ml_color_extraction(self):
        """Test KMeans color extraction on sample item image."""
        sample_path = os.path.join(app.root_path, 'static', 'images', 'samples', 'white_shirt.svg')
        if os.path.exists(sample_path):
            name, hex_code, rgb = extract_dominant_color(sample_path)
            self.assertTrue(name is not None)
            self.assertTrue(hex_code.startswith('#'))

        # Test color harmony calculation
        score, harmony_type, desc = calculate_color_harmony_score('#FFFFFF', '#2563EB')
        self.assertGreaterEqual(score, 80)
        self.assertTrue(len(harmony_type) > 0)

    def test_ml_personal_features_analysis(self):
        """Test computer vision analysis on a generated test portrait image."""
        test_img_path = os.path.join(app.root_path, 'static', 'uploads', 'test_portrait.jpg')
        # Create a synthetic portrait image with simulated face & skin tones
        img = np.zeros((300, 200, 3), dtype=np.uint8)
        img[:] = (240, 230, 220)  # light background
        # Torso
        cv2.rectangle(img, (40, 140), (160, 290), (180, 50, 120), -1)
        # Face
        cv2.circle(img, (100, 80), 40, (160, 190, 230), -1)
        cv2.imwrite(test_img_path, img)

        analysis = analyze_personal_features(test_img_path)
        self.assertTrue(analysis['success'])
        self.assertIn(analysis['body_shape'], ['Hourglass', 'Pear', 'Rectangle', 'Apple', 'Inverted Triangle'])
        self.assertIn(analysis['skin_tone'], ['Fair', 'Light', 'Medium', 'Olive', 'Tan', 'Deep'])
        self.assertGreater(analysis['height_cm'], 140)
        self.assertGreater(analysis['weight_kg'], 40)

        if os.path.exists(test_img_path):
            os.remove(test_img_path)

    def test_recommendation_and_outfit_generator(self):
        """Test recommendation engine and AI outfit generator."""
        with app.app_context():
            u = User(full_name='Test Stylist', email='stylist@example.com')
            u.set_password('pass123')
            db.session.add(u)
            db.session.commit()

            load_sample_wardrobe_for_user(u.id, app.root_path)
            items = WardrobeItem.query.filter_by(user_id=u.id).all()
            features = PersonalFeatures.query.filter_by(user_id=u.id).first()

            # 1. My Style Recommendation
            selected = items[:2]
            rec = generate_style_recommendation(selected, 'Office', features)
            self.assertIn('jewellery_recommendation', rec)
            self.assertIn('footwear_recommendation', rec)
            self.assertGreaterEqual(rec['style_score'], 80)
            self.assertTrue(len(rec['why_it_works']) > 20)

            # 2. AI Outfit Generator
            outfit_look = generate_ai_outfit(
                wardrobe_items=items,
                occasion='Party',
                season='Summer',
                preferred_color='Pink',
                personal_features=features
            )
            self.assertIsNotNone(outfit_look)
            self.assertGreaterEqual(outfit_look['style_score'], 80)

if __name__ == '__main__':
    unittest.main()
