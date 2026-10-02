import os
import base64
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from config import Config
from database.db import db
from models.user import User
from models.wardrobe import WardrobeItem
from models.personal_features import PersonalFeatures
from models.outfit import Outfit
from models.favorite import Favorite
from models.recommendation import RecommendationHistory

from ml.color_extractor import extract_dominant_color
from ml.personal_analyzer import analyze_personal_features, BODY_SHAPE_DETAILS, SKIN_TONE_CATEGORIES
from ml.recommender import generate_style_recommendation, generate_ai_outfit
from sample_data import load_sample_wardrobe_for_user

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please sign in to access your digital wardrobe."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# --------------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_image_from_request(file_obj, base64_str, subfolder, user_id):
    """
    Saves either a file upload or a camera Base64 Data URL to static/uploads/{subfolder}.
    Returns the relative path suitable for web serving (e.g. 'uploads/wardrobe/filename.jpg').
    """
    dest_dir = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(dest_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')

    # Case 1: Base64 data URL from live camera
    if base64_str and ',' in base64_str:
        try:
            header, encoded = base64_str.split(',', 1)
            img_data = base64.b64decode(encoded)
            filename = f"cam_{user_id}_{timestamp}.jpg"
            file_path = os.path.join(dest_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(img_data)
            return f"uploads/{subfolder}/{filename}", file_path
        except Exception as e:
            app.logger.error(f"Error saving base64 image: {e}")
            return None, None

    # Case 2: Regular file upload
    if file_obj and file_obj.filename != '' and allowed_file(file_obj.filename):
        ext = file_obj.filename.rsplit('.', 1)[1].lower()
        filename = f"file_{user_id}_{timestamp}.{ext}"
        file_path = os.path.join(dest_dir, filename)
        file_obj.save(file_path)
        return f"uploads/{subfolder}/{filename}", file_path

    return None, None

# --------------------------------------------------------------------------
# Authentication Routes
# --------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember_me'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please verify your credentials.", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        gender = request.form.get('gender', 'Female')
        age_str = request.form.get('age', '')

        # Validations
        if not full_name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email address already exists. Please sign in.", "warning")
            return redirect(url_for('login'))

        age = int(age_str) if age_str.isdigit() else None

        new_user = User(
            full_name=full_name,
            email=email,
            gender=gender,
            age=age,
            profile_image='avatar-default.svg'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Initialize baseline Personal Features
        features = PersonalFeatures(
            user_id=new_user.id,
            height_cm=165.0,
            weight_kg=56.0,
            skin_tone='Medium',
            skin_hex='#D4A373',
            skin_undertone='Warm',
            body_shape='Hourglass',
            analysis_notes='Initial baseline profile. Upload a photo or use camera in Personal Features for computer vision analysis.'
        )
        db.session.add(features)
        db.session.commit()

        login_user(new_user)
        flash("Registration successful! Welcome to StyleGuide AI.", "success")
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('login'))

# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    items = WardrobeItem.query.filter_by(user_id=user_id).all()

    clothes_count = sum(1 for i in items if i.main_category == 'Clothes')
    jewellery_count = sum(1 for i in items if i.main_category == 'Jewellery')
    footwear_count = sum(1 for i in items if i.main_category == 'Footwear')
    accessories_count = sum(1 for i in items if i.main_category == 'Accessories')
    outfits_count = Outfit.query.filter_by(user_id=user_id).count()

    stats = {
        'total_items': len(items),
        'clothes_count': clothes_count,
        'jewellery_count': jewellery_count,
        'footwear_count': footwear_count,
        'accessories_count': accessories_count,
        'outfits_count': outfits_count
    }

    recent_recommendations = RecommendationHistory.query.filter_by(user_id=user_id)\
        .order_by(RecommendationHistory.created_at.desc()).limit(3).all()

    return render_template('dashboard.html', stats=stats, recent_recommendations=recent_recommendations)

# --------------------------------------------------------------------------
# Wardrobe Management Routes
# --------------------------------------------------------------------------
@app.route('/wardrobe')
@login_required
def wardrobe():
    user_id = current_user.id
    items = WardrobeItem.query.filter_by(user_id=user_id).order_by(WardrobeItem.created_at.desc()).all()

    clothes_count = sum(1 for i in items if i.main_category == 'Clothes')
    jewellery_count = sum(1 for i in items if i.main_category == 'Jewellery')
    footwear_count = sum(1 for i in items if i.main_category == 'Footwear')
    accessories_count = sum(1 for i in items if i.main_category == 'Accessories')

    return render_template(
        'wardrobe.html',
        items=items,
        clothes_count=clothes_count,
        jewellery_count=jewellery_count,
        footwear_count=footwear_count,
        accessories_count=accessories_count
    )

@app.route('/wardrobe/add', methods=['GET', 'POST'])
@login_required
def wardrobe_add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        main_category = request.form.get('main_category', 'Clothes')
        sub_category = request.form.get('sub_category', 'Tops')
        user_color = request.form.get('color', '').strip()
        style = request.form.get('style', 'Casual')
        occasion = request.form.get('occasion', 'Casual')
        notes = request.form.get('notes', '').strip()

        file_obj = request.files.get('image_file')
        cam_base64 = request.form.get('camera_photo_base64', '')

        rel_path, abs_path = save_image_from_request(file_obj, cam_base64, 'wardrobe', current_user.id)

        if not rel_path:
            flash("Please provide a valid image from your gallery or capture one using your camera.", "danger")
            return redirect(url_for('wardrobe_add'))

        # Color extraction: if user left color empty, extract automatically via KMeans
        if not user_color and abs_path and os.path.exists(abs_path):
            extracted_name, extracted_hex, _ = extract_dominant_color(abs_path)
            item_color = extracted_name
            item_hex = extracted_hex
        else:
            item_color = user_color if user_color else 'Multicolor'
            # Estimate hex or default
            if abs_path and os.path.exists(abs_path):
                _, item_hex, _ = extract_dominant_color(abs_path)
            else:
                item_hex = '#EC4899'

        new_item = WardrobeItem(
            user_id=current_user.id,
            name=name,
            main_category=main_category,
            sub_category=sub_category,
            color=item_color,
            hex_code=item_hex,
            style=style,
            occasion=occasion,
            notes=notes,
            image_path=rel_path
        )
        db.session.add(new_item)
        db.session.commit()

        flash(f"'{name}' successfully added to your wardrobe!", "success")
        return redirect(url_for('wardrobe'))

    return render_template('wardrobe_add.html')

@app.route('/wardrobe/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def wardrobe_edit(item_id):
    item = db.get_or_404(WardrobeItem, item_id)
    if item.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        item.name = request.form.get('name', item.name).strip()
        item.main_category = request.form.get('main_category', item.main_category)
        item.sub_category = request.form.get('sub_category', item.sub_category)
        item.color = request.form.get('color', item.color).strip()
        item.hex_code = request.form.get('hex_code', item.hex_code)
        item.style = request.form.get('style', item.style)
        item.occasion = request.form.get('occasion', item.occasion)
        item.notes = request.form.get('notes', item.notes)

        # Check for image replacement
        file_obj = request.files.get('image_file')
        if file_obj and file_obj.filename != '' and allowed_file(file_obj.filename):
            rel_path, abs_path = save_image_from_request(file_obj, None, 'wardrobe', current_user.id)
            if rel_path:
                item.image_path = rel_path

        db.session.commit()
        flash(f"'{item.name}' updated successfully.", "success")
        return redirect(url_for('wardrobe'))

    return render_template('wardrobe_edit.html', item=item)

@app.route('/wardrobe/delete/<int:item_id>', methods=['POST'])
@login_required
def wardrobe_delete(item_id):
    item = db.get_or_404(WardrobeItem, item_id)
    if item.user_id != current_user.id:
        abort(403)

    # Remove file from disk if in uploads
    if item.image_path and item.image_path.startswith('uploads/'):
        disk_path = os.path.join(app.root_path, 'static', item.image_path)
        if os.path.exists(disk_path):
            try:
                os.remove(disk_path)
            except Exception as e:
                app.logger.warning(f"Failed to delete file {disk_path}: {e}")

    db.session.delete(item)
    db.session.commit()
    flash(f"'{item.name}' was removed from your wardrobe.", "info")
    return redirect(url_for('wardrobe'))

# --------------------------------------------------------------------------
# My Style & Recommendation Routes
# --------------------------------------------------------------------------
@app.route('/style')
@login_required
def style():
    user_id = current_user.id
    items = WardrobeItem.query.filter_by(user_id=user_id).all()

    tops = [i for i in items if i.sub_category in ['Tops', 'Shirts', 'T-shirts', 'Jackets']]
    bottoms = [i for i in items if i.sub_category in ['Jeans', 'Trousers', 'Skirts', 'Other'] and i.main_category == 'Clothes']
    dresses = [i for i in items if i.sub_category in ['Dresses', 'Kurtis', 'Sarees']]
    footwears = [i for i in items if i.main_category == 'Footwear']
    jewelleries = [i for i in items if i.main_category == 'Jewellery']
    accessories = [i for i in items if i.main_category == 'Accessories']

    return render_template(
        'style.html',
        tops=tops,
        bottoms=bottoms,
        dresses=dresses,
        footwears=footwears,
        jewelleries=jewelleries,
        accessories=accessories,
        recommendation=None,
        current_occasion='Casual'
    )

@app.route('/style/recommend', methods=['POST'])
@login_required
def style_recommend():
    user_id = current_user.id
    occasion = request.form.get('occasion', 'Casual')

    top_id = request.form.get('top_id')
    bottom_id = request.form.get('bottom_id')
    dress_id = request.form.get('dress_id')
    footwear_id = request.form.get('footwear_id')
    jewellery_id = request.form.get('jewellery_id')
    accessory_id = request.form.get('accessory_id')

    selected_items = []
    for i_id in [top_id, bottom_id, dress_id, footwear_id, jewellery_id, accessory_id]:
        if i_id and i_id.isdigit():
            item = WardrobeItem.query.filter_by(id=int(i_id), user_id=user_id).first()
            if item:
                selected_items.append(item)

    if not selected_items:
        flash("Please select at least one garment from your wardrobe to style.", "warning")
        return redirect(url_for('style'))

    features = PersonalFeatures.query.filter_by(user_id=user_id).first()
    recommendation = generate_style_recommendation(selected_items, occasion, features)

    # Save to Recommendation History
    summary_names = [f"{i.name} ({i.color})" for i in selected_items]
    rec_history = RecommendationHistory(
        user_id=user_id,
        occasion=occasion,
        selected_items_summary=", ".join(summary_names),
        jewellery_recommendation=recommendation['jewellery_recommendation'],
        footwear_recommendation=recommendation['footwear_recommendation'],
        accessory_recommendation=recommendation['accessory_recommendation'],
        style_score=recommendation['style_score'],
        why_it_works=recommendation['why_it_works'],
        color_compatibility=recommendation['color_compatibility']
    )
    db.session.add(rec_history)
    db.session.commit()

    # Re-fetch items for template
    items = WardrobeItem.query.filter_by(user_id=user_id).all()
    tops = [i for i in items if i.sub_category in ['Tops', 'Shirts', 'T-shirts', 'Jackets']]
    bottoms = [i for i in items if i.sub_category in ['Jeans', 'Trousers', 'Skirts', 'Other'] and i.main_category == 'Clothes']
    dresses = [i for i in items if i.sub_category in ['Dresses', 'Kurtis', 'Sarees']]
    footwears = [i for i in items if i.main_category == 'Footwear']
    jewelleries = [i for i in items if i.main_category == 'Jewellery']
    accessories = [i for i in items if i.main_category == 'Accessories']

    return render_template(
        'style.html',
        tops=tops,
        bottoms=bottoms,
        dresses=dresses,
        footwears=footwears,
        jewelleries=jewelleries,
        accessories=accessories,
        recommendation=recommendation,
        current_occasion=occasion,
        selected_top_id=int(top_id) if top_id and top_id.isdigit() else None,
        selected_bottom_id=int(bottom_id) if bottom_id and bottom_id.isdigit() else None,
        selected_dress_id=int(dress_id) if dress_id and dress_id.isdigit() else None,
        selected_footwear_id=int(footwear_id) if footwear_id and footwear_id.isdigit() else None,
        selected_jewellery_id=int(jewellery_id) if jewellery_id and jewellery_id.isdigit() else None,
        selected_accessory_id=int(accessory_id) if accessory_id and accessory_id.isdigit() else None
    )

@app.route('/style/save-outfit', methods=['POST'])
@login_required
def outfit_save_from_style():
    user_id = current_user.id
    occasion = request.form.get('occasion', 'Casual')
    top_id = request.form.get('top_id') or None
    bottom_id = request.form.get('bottom_id') or None
    dress_id = request.form.get('dress_id') or None
    footwear_id = request.form.get('footwear_id') or None
    jewellery_id = request.form.get('jewellery_id') or None
    accessory_id = request.form.get('accessory_id') or None
    score = int(request.form.get('style_score', 90))
    reasoning = request.form.get('reasoning', '')
    harmony = request.form.get('color_harmony', 'Harmonious')

    outfit = Outfit(
        user_id=user_id,
        name=f"{occasion} Ensemble",
        occasion=occasion,
        season='All-Season',
        top_id=int(top_id) if top_id and top_id.isdigit() else None,
        bottom_id=int(bottom_id) if bottom_id and bottom_id.isdigit() else None,
        dress_id=int(dress_id) if dress_id and dress_id.isdigit() else None,
        footwear_id=int(footwear_id) if footwear_id and footwear_id.isdigit() else None,
        jewellery_id=int(jewellery_id) if jewellery_id and jewellery_id.isdigit() else None,
        accessory_id=int(accessory_id) if accessory_id and accessory_id.isdigit() else None,
        style_score=score,
        reasoning=reasoning,
        color_harmony=harmony,
        is_favorite=True
    )
    db.session.add(outfit)
    db.session.commit()

    # Also record in Favorite table
    fav = Favorite(user_id=user_id, item_type='outfit', outfit_id=outfit.id)
    db.session.add(fav)
    db.session.commit()

    flash("Outfit saved to your Favorites and Lookbook!", "success")
    return redirect(url_for('favorites'))

# --------------------------------------------------------------------------
# Personal Features & Computer Vision Analysis
# --------------------------------------------------------------------------
@app.route('/personal-features')
@login_required
def personal_features():
    user_id = current_user.id
    features = PersonalFeatures.query.filter_by(user_id=user_id).first()

    styling_info = None
    flattering_colors = []

    if features:
        styling_info = BODY_SHAPE_DETAILS.get(features.body_shape, BODY_SHAPE_DETAILS['Hourglass'])
        tone_info = next((t for t in SKIN_TONE_CATEGORIES if t['name'] == features.skin_tone), SKIN_TONE_CATEGORIES[2])
        flattering_colors = tone_info['best_colors']

    return render_template(
        'personal_features.html',
        features=features,
        styling_info=styling_info,
        flattering_colors=flattering_colors
    )

@app.route('/personal-features/analyze', methods=['POST'])
@login_required
def personal_features_analyze():
    user_id = current_user.id
    file_obj = request.files.get('photo_file')
    cam_base64 = request.form.get('camera_photo_base64', '')

    rel_path, abs_path = save_image_from_request(file_obj, cam_base64, 'analysis', user_id)

    if not rel_path or not abs_path:
        flash("Please upload a photograph or snap one using your camera to analyze your features.", "danger")
        return redirect(url_for('personal_features'))

    # Run OpenCV & ML Analysis
    analysis = analyze_personal_features(abs_path)

    features = PersonalFeatures.query.filter_by(user_id=user_id).first()
    if not features:
        features = PersonalFeatures(user_id=user_id)
        db.session.add(features)

    features.height_cm = analysis['height_cm']
    features.weight_kg = analysis['weight_kg']
    features.skin_tone = analysis['skin_tone']
    features.skin_hex = analysis['skin_hex']
    features.skin_undertone = analysis['skin_undertone']
    features.body_shape = analysis['body_shape']
    features.photo_path = rel_path
    features.analysis_notes = analysis['analysis_notes']

    db.session.commit()

    flash("Computer vision analysis complete! Style proportions updated.", "success")
    return redirect(url_for('personal_features'))

# --------------------------------------------------------------------------
# AI Outfit Generator
# --------------------------------------------------------------------------
@app.route('/outfit-generator')
@login_required
def outfit_generator():
    return render_template(
        'outfit_generator.html',
        outfit_result=None,
        current_occasion='Casual',
        current_season='All-Season',
        current_color='',
        current_style=''
    )

@app.route('/outfit-generator/generate', methods=['POST'])
@login_required
def outfit_generator_generate():
    user_id = current_user.id
    occasion = request.form.get('occasion', 'Casual')
    season = request.form.get('season', 'All-Season')
    preferred_color = request.form.get('preferred_color', '')
    preferred_style = request.form.get('preferred_style', '')

    wardrobe_items = WardrobeItem.query.filter_by(user_id=user_id).all()
    if not wardrobe_items:
        flash("You need items in your wardrobe to generate outfits. Add some pieces or load the demo wardrobe.", "warning")
        return redirect(url_for('wardrobe'))

    features = PersonalFeatures.query.filter_by(user_id=user_id).first()
    outfit_result = generate_ai_outfit(
        wardrobe_items=wardrobe_items,
        occasion=occasion,
        season=season,
        preferred_color=preferred_color,
        preferred_style=preferred_style,
        personal_features=features
    )

    return render_template(
        'outfit_generator.html',
        outfit_result=outfit_result,
        current_occasion=occasion,
        current_season=season,
        current_color=preferred_color,
        current_style=preferred_style
    )

@app.route('/outfit-generator/save', methods=['POST'])
@login_required
def outfit_save():
    user_id = current_user.id
    name = request.form.get('name', 'AI Curated Look')
    occasion = request.form.get('occasion', 'Casual')
    season = request.form.get('season', 'All-Season')
    top_id = request.form.get('top_id') or None
    bottom_id = request.form.get('bottom_id') or None
    dress_id = request.form.get('dress_id') or None
    footwear_id = request.form.get('footwear_id') or None
    jewellery_id = request.form.get('jewellery_id') or None
    accessory_id = request.form.get('accessory_id') or None
    score = int(request.form.get('style_score', 88))
    reasoning = request.form.get('reasoning', '')
    harmony = request.form.get('color_harmony', 'Harmonious')

    outfit = Outfit(
        user_id=user_id,
        name=name,
        occasion=occasion,
        season=season,
        top_id=int(top_id) if top_id and top_id.isdigit() else None,
        bottom_id=int(bottom_id) if bottom_id and bottom_id.isdigit() else None,
        dress_id=int(dress_id) if dress_id and dress_id.isdigit() else None,
        footwear_id=int(footwear_id) if footwear_id and footwear_id.isdigit() else None,
        jewellery_id=int(jewellery_id) if jewellery_id and jewellery_id.isdigit() else None,
        accessory_id=int(accessory_id) if accessory_id and accessory_id.isdigit() else None,
        style_score=score,
        reasoning=reasoning,
        color_harmony=harmony,
        is_favorite=True
    )
    db.session.add(outfit)
    db.session.commit()

    fav = Favorite(user_id=user_id, item_type='outfit', outfit_id=outfit.id)
    db.session.add(fav)
    db.session.commit()

    flash("Generated outfit saved to your Favorites!", "success")
    return redirect(url_for('favorites'))

# --------------------------------------------------------------------------
# Favorites
# --------------------------------------------------------------------------
@app.route('/favorites')
@login_required
def favorites():
    user_id = current_user.id
    favorite_items = WardrobeItem.query.filter_by(user_id=user_id, is_favorite=True).all()
    favorite_outfits = Outfit.query.filter_by(user_id=user_id, is_favorite=True).all()

    return render_template(
        'favorites.html',
        favorite_items=favorite_items,
        favorite_outfits=favorite_outfits
    )

@app.route('/favorites/toggle', methods=['POST'])
@login_required
def favorites_toggle():
    data = request.get_json() or {}
    item_type = data.get('item_type', 'item')
    target_id = data.get('id')

    if not target_id:
        return jsonify({'success': False, 'error': 'Missing ID'}), 400

    if item_type == 'item':
        item = WardrobeItem.query.filter_by(id=target_id, user_id=current_user.id).first()
        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        item.is_favorite = not item.is_favorite
        if item.is_favorite:
            fav = Favorite(user_id=current_user.id, item_type='item', wardrobe_item_id=item.id)
            db.session.add(fav)
        else:
            Favorite.query.filter_by(user_id=current_user.id, item_type='item', wardrobe_item_id=item.id).delete()

        db.session.commit()
        return jsonify({'success': True, 'is_favorite': item.is_favorite})

    elif item_type == 'outfit':
        outfit = Outfit.query.filter_by(id=target_id, user_id=current_user.id).first()
        if not outfit:
            return jsonify({'success': False, 'error': 'Outfit not found'}), 404

        outfit.is_favorite = not outfit.is_favorite
        if outfit.is_favorite:
            fav = Favorite(user_id=current_user.id, item_type='outfit', outfit_id=outfit.id)
            db.session.add(fav)
        else:
            Favorite.query.filter_by(user_id=current_user.id, item_type='outfit', outfit_id=outfit.id).delete()

        db.session.commit()
        return jsonify({'success': True, 'is_favorite': outfit.is_favorite})

    return jsonify({'success': False, 'error': 'Invalid type'}), 400

@app.route('/favorites/remove/<string:fav_type>/<int:item_id>', methods=['POST'])
@login_required
def favorites_remove(fav_type, item_id):
    user_id = current_user.id
    if fav_type == 'item':
        item = WardrobeItem.query.filter_by(id=item_id, user_id=user_id).first()
        if item:
            item.is_favorite = False
            Favorite.query.filter_by(user_id=user_id, item_type='item', wardrobe_item_id=item.id).delete()
            db.session.commit()
            flash("Piece removed from favorites.", "info")
    elif fav_type == 'outfit':
        outfit = Outfit.query.filter_by(id=item_id, user_id=user_id).first()
        if outfit:
            outfit.is_favorite = False
            Favorite.query.filter_by(user_id=user_id, item_type='outfit', outfit_id=outfit.id).delete()
            db.session.commit()
            flash("Outfit removed from favorites.", "info")

    return redirect(url_for('favorites'))

# --------------------------------------------------------------------------
# Outfit History
# --------------------------------------------------------------------------
@app.route('/outfit-history')
@login_required
def outfit_history():
    user_id = current_user.id
    recommendations = RecommendationHistory.query.filter_by(user_id=user_id)\
        .order_by(RecommendationHistory.created_at.desc()).all()

    return render_template('outfit_history.html', recommendations=recommendations)

# --------------------------------------------------------------------------
# Profile Management
# --------------------------------------------------------------------------
@app.route('/profile')
@login_required
def profile():
    user_id = current_user.id
    items_count = WardrobeItem.query.filter_by(user_id=user_id).count()
    outfits_count = Outfit.query.filter_by(user_id=user_id).count()

    stats = {
        'total_items': items_count,
        'outfits_count': outfits_count
    }
    return render_template('profile.html', stats=stats)

@app.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    current_user.full_name = request.form.get('full_name', current_user.full_name).strip()
    current_user.gender = request.form.get('gender', current_user.gender)
    age_str = request.form.get('age', '')
    current_user.age = int(age_str) if age_str.isdigit() else current_user.age

    db.session.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for('profile'))

@app.route('/profile/photo', methods=['POST'])
@login_required
def profile_photo():
    file_obj = request.files.get('photo_file')
    cam_base64 = request.form.get('camera_photo_base64', '')

    rel_path, abs_path = save_image_from_request(file_obj, cam_base64, 'profiles', current_user.id)
    if rel_path:
        current_user.profile_image = rel_path
        db.session.commit()
        flash("Profile picture updated.", "success")
    else:
        flash("No valid image provided.", "warning")

    return redirect(url_for('profile'))

# --------------------------------------------------------------------------
# Settings & System Demo Loader
# --------------------------------------------------------------------------
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/load-demo-data', methods=['POST'])
@login_required
def load_demo_data():
    added = load_sample_wardrobe_for_user(current_user.id, app.root_path)
    flash(f"Successfully loaded {added} curated demo items into your digital wardrobe!", "success")
    return redirect(url_for('wardrobe'))

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = db.session.get(User, current_user.id)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("Your account and all associated wardrobe data have been permanently deleted.", "info")
    return redirect(url_for('register'))

# --------------------------------------------------------------------------
# Error Handlers
# --------------------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', public_content=True), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html', public_content=True), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
