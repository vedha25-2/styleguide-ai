import os
import shutil
from database.db import db
from models.wardrobe import WardrobeItem
from models.personal_features import PersonalFeatures

SAMPLE_ITEMS = [
    {
        'name': 'Crisp White Oxford Shirt',
        'main_category': 'Clothes',
        'sub_category': 'Shirts',
        'color': 'White',
        'hex_code': '#FFFFFF',
        'style': 'Smart Casual',
        'occasion': 'Office',
        'sample_file': 'white_shirt.svg'
    },
    {
        'name': 'Classic Indigo Denim Jeans',
        'main_category': 'Clothes',
        'sub_category': 'Jeans',
        'color': 'Navy Blue',
        'hex_code': '#2563EB',
        'style': 'Casual Chic',
        'occasion': 'Casual',
        'sample_file': 'blue_jeans.svg'
    },
    {
        'name': 'Pink Floral A-Line Dress',
        'main_category': 'Clothes',
        'sub_category': 'Dresses',
        'color': 'Blush Pink',
        'hex_code': '#EC4899',
        'style': 'Romantic Chic',
        'occasion': 'Party',
        'sample_file': 'floral_dress.svg'
    },
    {
        'name': 'Blush Embroidered Silk Kurti',
        'main_category': 'Clothes',
        'sub_category': 'Kurtis',
        'color': 'Lilac',
        'hex_code': '#D946EF',
        'style': 'Ethnic Glam',
        'occasion': 'Festival',
        'sample_file': 'blush_kurti.svg'
    },
    {
        'name': 'Caramel Belted Trench Coat',
        'main_category': 'Clothes',
        'sub_category': 'Jackets',
        'color': 'Camel',
        'hex_code': '#D97706',
        'style': 'Classic Formal',
        'occasion': 'Formal',
        'sample_file': 'trench_coat.svg'
    },
    {
        'name': 'Crimson Silk Festive Saree',
        'main_category': 'Clothes',
        'sub_category': 'Sarees',
        'color': 'Wine Red',
        'hex_code': '#BE123C',
        'style': 'Traditional Regal',
        'occasion': 'Wedding',
        'sample_file': 'silk_saree.svg'
    },
    {
        'name': 'Clean Streetwear White Sneakers',
        'main_category': 'Footwear',
        'sub_category': 'Sneakers',
        'color': 'White',
        'hex_code': '#FFFFFF',
        'style': 'Urban Casual',
        'occasion': 'Casual',
        'sample_file': 'white_sneakers.svg'
    },
    {
        'name': 'Nude Strappy Kitten Heels',
        'main_category': 'Footwear',
        'sub_category': 'Heels',
        'color': 'Tan',
        'hex_code': '#E0A96D',
        'style': 'Cocktail Elegance',
        'occasion': 'Party',
        'sample_file': 'nude_heels.svg'
    },
    {
        'name': 'Freshwater Pearl Drop Earrings',
        'main_category': 'Jewellery',
        'sub_category': 'Earrings',
        'color': 'White',
        'hex_code': '#F8FAFC',
        'style': 'Timeless Grace',
        'occasion': 'Office',
        'sample_file': 'pearl_earrings.svg'
    },
    {
        'name': 'Geometric Gold Pendant Necklace',
        'main_category': 'Jewellery',
        'sub_category': 'Necklace',
        'color': 'Gold',
        'hex_code': '#FBBF24',
        'style': 'Contemporary Dainty',
        'occasion': 'Date',
        'sample_file': 'gold_necklace.svg'
    },
    {
        'name': 'Italian Leather Structured Tote',
        'main_category': 'Accessories',
        'sub_category': 'Handbags',
        'color': 'Chocolate Brown',
        'hex_code': '#78350F',
        'style': 'Professional Luxury',
        'occasion': 'Office',
        'sample_file': 'leather_tote.svg'
    },
    {
        'name': 'Retro Tortoiseshell Sunglasses',
        'main_category': 'Accessories',
        'sub_category': 'Sunglasses',
        'color': 'Burgundy',
        'hex_code': '#831843',
        'style': 'Vintage Chic',
        'occasion': 'Travel',
        'sample_file': 'retro_sunglasses.svg'
    }
]

def load_sample_wardrobe_for_user(user_id, base_dir):
    """
    Populates starter wardrobe items for a user by copying sample SVGs to user's upload directory.
    Prevents duplicates.
    """
    upload_dir = os.path.join(base_dir, 'static', 'uploads', 'wardrobe')
    os.makedirs(upload_dir, exist_ok=True)
    samples_dir = os.path.join(base_dir, 'static', 'images', 'samples')

    added_count = 0
    for item_data in SAMPLE_ITEMS:
        # Check if already added
        exists = WardrobeItem.query.filter_by(user_id=user_id, name=item_data['name']).first()
        if exists:
            continue

        src_path = os.path.join(samples_dir, item_data['sample_file'])
        dest_filename = f"user_{user_id}_{item_data['sample_file']}"
        dest_path = os.path.join(upload_dir, dest_filename)

        if os.path.exists(src_path):
            shutil.copyfile(src_path, dest_path)
            rel_image_path = f"uploads/wardrobe/{dest_filename}"
        else:
            rel_image_path = f"images/samples/{item_data['sample_file']}"

        item = WardrobeItem(
            user_id=user_id,
            name=item_data['name'],
            main_category=item_data['main_category'],
            sub_category=item_data['sub_category'],
            color=item_data['color'],
            hex_code=item_data['hex_code'],
            style=item_data['style'],
            occasion=item_data['occasion'],
            image_path=rel_image_path,
            is_favorite=False
        )
        db.session.add(item)
        added_count += 1

    # Also ensure personal features entry exists if not already
    features = PersonalFeatures.query.filter_by(user_id=user_id).first()
    if not features:
        features = PersonalFeatures(
            user_id=user_id,
            height_cm=165.0,
            weight_kg=56.0,
            skin_tone='Medium',
            skin_hex='#D4A373',
            skin_undertone='Warm',
            body_shape='Hourglass',
            analysis_notes='AI baseline personal profile initialized. Upload a photo or use camera to recalculate real-time.'
        )
        db.session.add(features)

    db.session.commit()
    return added_count
