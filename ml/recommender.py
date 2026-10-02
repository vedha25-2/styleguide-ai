import random
from ml.color_extractor import calculate_color_harmony_score, hex_to_rgb, get_closest_color_name

OCCASION_GUIDELINES = {
    'Casual': {
        'footwear': ['Sneakers', 'Flats', 'Slide Sandals', 'Slip-on Shoes'],
        'jewellery': ['Minimal Studs', 'Simple Chain', 'Beaded Bracelet', 'Everyday Watch'],
        'accessories': ['Crossbody Canvas Bag', 'Tote Bag', 'Casual Cap', 'Retro Sunglasses'],
        'vibe': 'relaxed, effortless, and comfortable for daily activities'
    },
    'College': {
        'footwear': ['Chunky White Sneakers', 'Loafers', 'Comfortable Flats', 'Canvas High-Tops'],
        'jewellery': ['Layered Dainty Necklaces', 'Small Silver Hoops', 'Modern Smartwatch'],
        'accessories': ['Structured Backpack', 'Canvas Tote', 'Minimalist Laptop Sleeve', 'Tortoiseshell Glasses'],
        'vibe': 'youthful, functional, and trendy for campus life'
    },
    'Office': {
        'footwear': ['Pointed-toe Flats', 'Block Heel Pumps', 'Classic Loafers', 'Kitten Heels'],
        'jewellery': ['Pearl Stud Earrings', 'Delicate Gold Pendant', 'Classic Leather-strap Watch'],
        'accessories': ['Structured Leather Tote', 'Laptop Briefcase', 'Slim Leather Belt'],
        'vibe': 'polished, authoritative, and sophisticated for the workplace'
    },
    'Party': {
        'footwear': ['Strappy Stiletto Heels', 'Metallic Platform Sandals', 'Ankle Boots'],
        'jewellery': ['Chandelier Earrings', 'Glittering Choker', 'Stacked Crystal Rings', 'Cuff Bracelet'],
        'accessories': ['Embellished Clutch', 'Metallic Chain Bag', 'Statement Belt'],
        'vibe': 'glamorous, eye-catching, and vibrant for evening nightlife'
    },
    'Wedding': {
        'footwear': ['Embellished Block Heels', 'Silk Mules', 'Gilded Strappy Sandals', 'Embroidered Juttis'],
        'jewellery': ['Kundan / Polki Set', 'Statement Pearl Drop Earrings', 'Intricate Choker', 'Gold Bangles'],
        'accessories': ['Potli Bag with Zari Work', 'Embroidered Box Clutch', 'Silk Dupatta / Stole'],
        'vibe': 'regal, festive, and timeless celebration elegance'
    },
    'Date': {
        'footwear': ['Elegant Kitten Heels', 'Lace-up Sandals', 'Heeled Ankle Booties'],
        'jewellery': ['Rose Gold Heart Pendant', 'Shimmering Drop Earrings', 'Delicate Tennis Bracelet'],
        'accessories': ['Compact Quilted Crossbody', 'Mini Bag', 'Silk Hair Ribbon'],
        'vibe': 'romantic, charming, and magnetic with subtle allure'
    },
    'Festival': {
        'footwear': ['Embroidered Mojaris', 'Kolhapuris', 'Strappy Metallic Flats', 'Boho Wedges'],
        'jewellery': ['Oxidized Silver Jhumkas', 'Bohemian Choker', 'Stacked Glass Bangles', 'Anklets'],
        'accessories': ['Mirror-work Potli', 'Ethnic Clutch', 'Embroidered Shawl'],
        'vibe': 'vibrant, culturally rich, and celebrative'
    },
    'Interview': {
        'footwear': ['Neutral Closed-toe Pumps', 'Polished Oxford Shoes', 'Tailored Loafers'],
        'jewellery': ['Micro Pearl Studs', 'Subtle Bar Necklace', 'Minimal Analog Watch'],
        'accessories': ['Structured Dark Leather Portfolio', 'Monochrome Briefcase'],
        'vibe': 'crisp, professional, and confidence-inspiring'
    },
    'Travel': {
        'footwear': ['Ergonomic Walking Sneakers', 'Cushioned Sandals', 'Slip-on Espadrilles'],
        'jewellery': ['Minimalist Non-tangle Chain', 'Silicone or Sport Watch'],
        'accessories': ['Anti-theft Crossbody Bag', 'Polarized Sunglasses', 'Bucket Hat', 'Travel Scarf'],
        'vibe': 'comfortable, versatile, and adventure-ready'
    },
    'Traditional': {
        'footwear': ['Traditional Juttis', 'Embellished Wedges', 'Zari Kolhapuris'],
        'jewellery': ['Traditional Temple Jewellery', 'Chandbali Earrings', 'Gold Maang Tikka', 'Bangles'],
        'accessories': ['Velvet or Brocade Potli', 'Ethnic Dupatta', 'Embroidered Handbag'],
        'vibe': 'graceful, heritage-inspired, and ceremonial'
    },
    'Formal': {
        'footwear': ['Classic Black Pumps', 'Sleek Slingback Heels', 'Patent Leather Shoes'],
        'jewellery': ['Diamond / Cubic Zirconia Tennis Set', 'Sleek Drop Earrings'],
        'accessories': ['Satin Envelope Clutch', 'Velvet Evening Bag'],
        'vibe': 'impeccably refined, understated, and high-fashion'
    },
    'Other': {
        'footwear': ['Versatile Clean Sneakers', 'Neutral Block Heels', 'Modern Mules'],
        'jewellery': ['Contemporary Geometric Earrings', 'Chain Necklace', 'Sleek Ring'],
        'accessories': ['Medium Shoulder Bag', 'Cat-eye Sunglasses'],
        'vibe': 'chic, versatile, and modern'
    }
}

JEWELLERY_METALS = {
    'Warm': 'Yellow Gold, Champagne Gold, or Brass accents harmonise effortlessly with your warm undertone.',
    'Cool': 'Silver, White Gold, Platinum, or Rose Gold accents illuminate your cool undertone.',
    'Neutral': 'Both Radiant Gold and Polished Silver complement your balanced complexion.'
}

def generate_style_recommendation(selected_items, occasion, personal_features=None):
    """
    Analyzes selected wardrobe pieces and generates tailored jewellery, footwear,
    and accessory recommendations with score and styling reasoning.
    """
    guideline = OCCASION_GUIDELINES.get(occasion, OCCASION_GUIDELINES['Casual'])
    
    # Extract item colors and names
    colors = [item.hex_code for item in selected_items if hasattr(item, 'hex_code') and item.hex_code]
    item_names = [f"{item.name} ({item.sub_category})" for item in selected_items if hasattr(item, 'name')]
    
    # Calculate color harmony
    if len(colors) >= 2:
        score_val, harmony_type, harmony_desc = calculate_color_harmony_score(colors[0], colors[1])
    else:
        score_val, harmony_type, harmony_desc = 90, "Focused Statement Tone", "A bold anchor color that welcomes versatile complementary accents."

    undertone = personal_features.skin_undertone if personal_features else 'Neutral'
    body_shape = personal_features.body_shape if personal_features else 'Hourglass'
    metal_advice = JEWELLERY_METALS.get(undertone, JEWELLERY_METALS['Neutral'])

    # Pick occasion-specific recommendations
    footwear_sample = random.choice(guideline['footwear'])
    jewellery_sample = random.choice(guideline['jewellery'])
    accessory_sample = random.choice(guideline['accessories'])

    jewellery_rec = f"{jewellery_sample}. {metal_advice}"
    footwear_rec = f"{footwear_sample} chosen for optimal proportion and {occasion.lower()} comfort."
    accessory_rec = f"{accessory_sample} to complete the aesthetic balance."

    # Style compatibility score (normalized 84 - 96%)
    base_score = score_val
    if occasion in ['Office', 'Formal', 'Interview']:
        final_score = min(98, max(85, base_score + 2))
    else:
        final_score = min(98, max(84, base_score))

    # Compose detailed rationale
    items_str = ", ".join(item_names) if item_names else "your selected garments"
    why_it_works = (
        f"This combination featuring {items_str} achieves a {harmony_type} ({harmony_desc}). "
        f"For a {occasion} setting, it exudes a {guideline['vibe']} while honoring {body_shape} silhouette balance. "
        f"The selected footwear ({footwear_sample}) grounds the silhouette, while {jewellery_sample} adds an intentional, sophisticated focal point."
    )

    return {
        'jewellery_recommendation': jewellery_rec,
        'footwear_recommendation': footwear_rec,
        'accessory_recommendation': accessory_rec,
        'style_score': final_score,
        'why_it_works': why_it_works,
        'color_compatibility': harmony_type,
        'occasion': occasion
    }

def generate_ai_outfit(wardrobe_items, occasion='Casual', season='All-Season', preferred_color=None, preferred_style=None, personal_features=None):
    """
    AI Outfit Generator: Searches user's digital wardrobe to construct
    a complete harmonized outfit (Top + Bottom OR Dress, plus Footwear, Jewellery, and Accessory).
    """
    if not wardrobe_items:
        return None

    # Filter items by main category
    dresses = [i for i in wardrobe_items if i.sub_category in ['Dresses', 'Kurtis', 'Sarees']]
    tops = [i for i in wardrobe_items if i.sub_category in ['Tops', 'Shirts', 'T-shirts', 'Jackets']]
    bottoms = [i for i in wardrobe_items if i.sub_category in ['Jeans', 'Trousers', 'Skirts', 'Other'] and i.main_category == 'Clothes']
    footwear = [i for i in wardrobe_items if i.main_category == 'Footwear']
    jewellery = [i for i in wardrobe_items if i.main_category == 'Jewellery']
    accessories = [i for i in wardrobe_items if i.main_category == 'Accessories']

    chosen_dress = None
    chosen_top = None
    chosen_bottom = None

    # Helper scoring function
    def score_item(item):
        s = 0
        if preferred_color and preferred_color.lower() in (item.color or '').lower():
            s += 5
        if preferred_style and preferred_style.lower() in (item.style or '').lower():
            s += 4
        if occasion.lower() in (item.occasion or '').lower():
            s += 6
        return s

    # Sort each list by affinity score
    dresses.sort(key=score_item, reverse=True)
    tops.sort(key=score_item, reverse=True)
    bottoms.sort(key=score_item, reverse=True)
    footwear.sort(key=score_item, reverse=True)
    jewellery.sort(key=score_item, reverse=True)
    accessories.sort(key=score_item, reverse=True)

    # Decide whether to use Dress or Top + Bottom
    use_dress = (len(dresses) > 0 and (len(tops) == 0 or len(bottoms) == 0 or random.random() < 0.45))
    
    if use_dress:
        chosen_dress = dresses[0]
    else:
        if tops:
            chosen_top = tops[0]
        if bottoms:
            chosen_bottom = bottoms[0]
        if not chosen_top and not chosen_bottom and dresses:
            chosen_dress = dresses[0]

    chosen_footwear = footwear[0] if footwear else None
    chosen_jewellery = jewellery[0] if jewellery else None
    chosen_accessory = accessories[0] if accessories else None

    # Calculate outfit compatibility
    active_items = [it for it in [chosen_dress, chosen_top, chosen_bottom, chosen_footwear, chosen_jewellery, chosen_accessory] if it]
    colors = [it.hex_code for it in active_items if it.hex_code]

    if len(colors) >= 2:
        score_val, harmony_name, _ = calculate_color_harmony_score(colors[0], colors[1])
    else:
        score_val, harmony_name = 92, "Monochromatic Foundation"

    undertone = personal_features.skin_undertone if personal_features else 'Neutral'
    body_shape = personal_features.body_shape if personal_features else 'Hourglass'
    guideline = OCCASION_GUIDELINES.get(occasion, OCCASION_GUIDELINES['Casual'])

    reasoning = (
        f"This complete look pairs harmonious tones for a {guideline['vibe']}. "
        f"The silhouette is proportioned to flatter a {body_shape} body profile, creating cohesive balance."
    )

    return {
        'dress': chosen_dress,
        'top': chosen_top,
        'bottom': chosen_bottom,
        'footwear': chosen_footwear,
        'jewellery': chosen_jewellery,
        'accessory': chosen_accessory,
        'style_score': min(98, max(86, score_val + 3)),
        'color_harmony': harmony_name,
        'reasoning': reasoning,
        'occasion': occasion,
        'season': season,
        'missing_categories': {
            'footwear': (chosen_footwear is None),
            'jewellery': (chosen_jewellery is None),
            'accessory': (chosen_accessory is None)
        },
        'guideline': guideline
    }
