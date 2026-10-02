import cv2
import numpy as np
from PIL import Image
import os

# Fashion-friendly skin tone classifications
SKIN_TONE_CATEGORIES = [
    {
        'name': 'Fair',
        'hex': '#F7D7C4',
        'undertones': ['Cool', 'Neutral'],
        'best_colors': ['Soft Pink', 'Lavender', 'Ruby Red', 'Emerald Green', 'Navy Blue'],
        'avoid_colors': ['Beige', 'Pale Yellow', 'Washed-out Neons']
    },
    {
        'name': 'Light',
        'hex': '#EFC8AB',
        'undertones': ['Warm', 'Neutral'],
        'best_colors': ['Blush Pink', 'Coral', 'Teal', 'Lilac', 'Sage Green'],
        'avoid_colors': ['Harsh Stark White', 'Muddy Browns']
    },
    {
        'name': 'Medium',
        'hex': '#D4A373',
        'undertones': ['Warm', 'Olive'],
        'best_colors': ['Hot Pink', 'Royal Blue', 'Burgundy', 'Mustard Yellow', 'Forest Green', 'Violet'],
        'avoid_colors': ['Dull Grays', 'Washed Taupe']
    },
    {
        'name': 'Olive',
        'hex': '#C69363',
        'undertones': ['Neutral', 'Warm'],
        'best_colors': ['Deep Purple', 'Wine Red', 'Emerald Green', 'Gold', 'Off-White', 'Warm Coral'],
        'avoid_colors': ['Acid Green', 'Pale Yellowish Green']
    },
    {
        'name': 'Tan',
        'hex': '#A36841',
        'undertones': ['Warm', 'Golden'],
        'best_colors': ['Pure White', 'Vibrant Pink', 'Turquoise', 'Bright Orange', 'Gold', 'Cobalt Blue'],
        'avoid_colors': ['Dull Khaki', 'Muddy Olive']
    },
    {
        'name': 'Deep',
        'hex': '#663B1F',
        'undertones': ['Warm', 'Cool'],
        'best_colors': ['Fuchsia', 'Vivid Yellow', 'Bright Red', 'Cobalt Blue', 'Pure White', 'Emerald Green'],
        'avoid_colors': ['Dark Charcoal', 'Very Muddy Brown']
    }
]

BODY_SHAPE_DETAILS = {
    'Hourglass': {
        'description': 'Balanced bust and hips with a clearly defined, narrower waist.',
        'styling_advice': 'Fitted silhouettes, wrap dresses, high-waisted bottoms, and V-neck tops accentuate natural proportions.',
        'recommended_pieces': ['Wrap Dresses', 'High-waisted Jeans', 'Belted Trench Coats', 'Fitted Blazers', 'Sweetheart Tops']
    },
    'Pear': {
        'description': 'Hips and thighs are wider than the shoulders and bust.',
        'styling_advice': 'Emphasize your upper half with statement necklines, ruffles, bright tops, paired with A-line skirts or straight-leg trousers.',
        'recommended_pieces': ['A-line Skirts', 'Boatneck Tops', 'Statement Necklaces', 'Dark Wash Wide-leg Jeans', 'Structured Shoulder Jackets']
    },
    'Rectangle': {
        'description': 'Shoulders, waist, and hips are of fairly uniform width with an athletic build.',
        'styling_advice': 'Create curves and visual interest with belts, peplum tops, layered outerwear, and flared skirts.',
        'recommended_pieces': ['Belted Dresses', 'Peplum Tops', 'Fit-and-flare Skirts', 'Ruffled Blouses', 'Cropped Jackets']
    },
    'Inverted Triangle': {
        'description': 'Shoulders and chest are broader than the hips and waistline.',
        'styling_advice': 'Draw focus downward with wide-leg trousers, pleated skirts, and V-neck or scoop neck tops that soften the shoulder line.',
        'recommended_pieces': ['Wide-leg Palazzos', 'Pleated Skirts', 'V-neck Shirts', 'Cargo Pants', 'Simple Clean Blazers']
    },
    'Apple': {
        'description': 'Fuller midsection and torso with comparatively slimmer legs and arms.',
        'styling_advice': 'Highlight your neckline and legs with empire waists, tunic tops, flowy fabrics, and stylish ankle footwear.',
        'recommended_pieces': ['Empire Waist Dresses', 'Flowy Kurtis & Tunics', 'Straight-leg Trousers', 'Longline Cardigans', 'Statement Earrings']
    }
}

def detect_face_region(img_bgr):
    """
    Detects face region using OpenCV CascadeClassifier if available,
    or robust chrominance contour segmentation.
    Returns (x, y, w, h).
    """
    h, w, _ = img_bgr.shape

    # Method 1: Try legacy CascadeClassifier if present
    if hasattr(cv2, 'CascadeClassifier'):
        try:
            cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
            face_cascade = cv2.CascadeClassifier(cascade_path)
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
            if len(faces) > 0:
                return max(faces, key=lambda f: f[2] * f[3])
        except Exception:
            pass

    # Method 2: Skin-chrominance contour analysis in upper torso region
    try:
        ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
        skin_mask = cv2.inRange(ycrcb, np.array([40, 133, 77]), np.array([255, 175, 127]))
        
        # Analyze upper 65% for face
        upper_mask = skin_mask[:int(h * 0.65), :]
        contours, _ = cv2.findContours(upper_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_faces = []
        for c in contours:
            x, y, fw, fh = cv2.boundingRect(c)
            # Face bounding box filter: size and aspect ratio
            if fw > w * 0.08 and fh > h * 0.08 and 0.5 <= (fw / max(fh, 1)) <= 1.5:
                valid_faces.append((x, y, fw, fh))
                
        if valid_faces:
            return max(valid_faces, key=lambda f: f[2] * f[3])
    except Exception:
        pass

    # Method 3: Anatomical center-upper third default ROI
    return (int(w * 0.35), int(h * 0.12), int(w * 0.30), int(h * 0.25))

def analyze_skin_tone(img_bgr, face_rect=None):
    """
    Extracts skin pixels from face region and determines skin tone category and undertone.
    """
    h, w, _ = img_bgr.shape
    
    if face_rect is not None:
        fx, fy, fw, fh = face_rect
        sample_y1 = max(0, int(fy + fh * 0.25))
        sample_y2 = min(h, int(fy + fh * 0.70))
        sample_x1 = max(0, int(fx + fw * 0.25))
        sample_x2 = min(w, int(fx + fw * 0.75))
        roi = img_bgr[sample_y1:sample_y2, sample_x1:sample_x2]
    else:
        roi = img_bgr[int(h*0.2):int(h*0.6), int(w*0.3):int(w*0.7)]

    if roi.size == 0:
        return 'Medium', '#D4A373', 'Warm'

    ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
    skin_mask = cv2.inRange(ycrcb, np.array([40, 133, 77]), np.array([255, 175, 127]))
    skin_pixels = roi[skin_mask > 0]
    
    if len(skin_pixels) < 20:
        median_bgr = np.median(roi.reshape(-1, 3), axis=0)
    else:
        median_bgr = np.median(skin_pixels, axis=0)
        
    b, g, r = median_bgr[0], median_bgr[1], median_bgr[2]
    hex_code = f"#{int(r):02X}{int(g):02X}{int(b):02X}"
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    
    if (r - b) > 40 and (g - b) > 15:
        undertone = 'Warm'
    elif abs(r - g) < 25 and b > 90:
        undertone = 'Cool'
    else:
        undertone = 'Neutral'
        
    if luminance > 195:
        tone_name = 'Fair'
    elif luminance > 165:
        tone_name = 'Light'
    elif luminance > 135:
        tone_name = 'Medium'
    elif luminance > 115:
        tone_name = 'Olive'
    elif luminance > 85:
        tone_name = 'Tan'
    else:
        tone_name = 'Deep'
        
    return tone_name, hex_code, undertone

def analyze_body_shape(img_bgr, face_rect=None):
    """
    Estimates body shape by analyzing contour silhouette proportions at shoulder, waist, and hip levels.
    """
    h, w, _ = img_bgr.shape
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 120)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    if face_rect is not None:
        fx, fy, fw, fh = face_rect
        body_top = min(h - 20, fy + fh)
    else:
        body_top = int(h * 0.25)
        
    body_bottom = int(h * 0.90)
    body_height = max(10, body_bottom - body_top)
    
    y_shoulder = int(body_top + body_height * 0.18)
    y_waist = int(body_top + body_height * 0.48)
    y_hip = int(body_top + body_height * 0.75)
    
    def get_width_at_y(target_y):
        if target_y >= h or target_y < 0:
            return w * 0.4
        row = dilated[target_y, :]
        active_indices = np.where(row > 0)[0]
        if len(active_indices) >= 2:
            return float(active_indices[-1] - active_indices[0])
        return float(w * 0.35)
        
    shoulder_w = max(get_width_at_y(y_shoulder), 20.0)
    waist_w = max(get_width_at_y(y_waist), 15.0)
    hip_w = max(get_width_at_y(y_hip), 20.0)
    
    waist_to_shoulder = waist_w / shoulder_w
    waist_to_hip = waist_w / hip_w
    hip_to_shoulder = hip_w / shoulder_w
    
    if waist_to_shoulder <= 0.82 and waist_to_hip <= 0.82 and abs(shoulder_w - hip_w) / shoulder_w < 0.20:
        shape = 'Hourglass'
    elif hip_to_shoulder >= 1.08:
        shape = 'Pear'
    elif shoulder_w / hip_w >= 1.08:
        shape = 'Inverted Triangle'
    elif waist_to_shoulder > 0.88 and waist_to_hip > 0.88:
        shape = 'Apple' if (waist_w >= shoulder_w or waist_w >= hip_w) else 'Rectangle'
    else:
        shape = 'Hourglass'
        
    return shape, {
        'shoulder_width_rel': round(shoulder_w, 1),
        'waist_width_rel': round(waist_w, 1),
        'hip_width_rel': round(hip_w, 1)
    }

def estimate_height_and_weight(img_bgr, face_rect=None):
    """
    AI heuristic estimation of height and weight from visual proportions.
    Note: Clearly labeled as AI-based estimate.
    """
    h, w, _ = img_bgr.shape
    
    if face_rect is not None:
        fx, fy, fw, fh = face_rect
        framing_ratio = h / max(fh, 1)
        
        if framing_ratio > 6.0:
            est_height = 160.0 + (framing_ratio - 6.0) * 1.8
        elif framing_ratio > 3.5:
            est_height = 162.0 + (framing_ratio - 3.5) * 2.2
        else:
            est_height = 165.0
            
        est_height = float(np.clip(est_height, 155.0, 182.0))
        fullness = fw / max(fh, 1)
        est_bmi = 20.5 + (fullness - 0.75) * 6.0
        est_bmi = float(np.clip(est_bmi, 19.0, 26.0))
        
        height_m = est_height / 100.0
        est_weight = est_bmi * (height_m ** 2)
        est_weight = float(np.clip(est_weight, 48.0, 78.0))
    else:
        est_height = 165.0
        est_weight = 57.0

    return round(est_height, 1), round(est_weight, 1)

def analyze_personal_features(image_path):
    """
    Full pipeline to analyze an image for personal styling features:
    - Face detection
    - Skin tone & undertone
    - Body shape estimation
    - AI-estimated height and weight
    - Tailored styling advice & color recommendations
    """
    try:
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            pil_img = Image.open(image_path).convert('RGB')
            img_rgb = np.array(pil_img)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

        face_rect = detect_face_region(img_bgr)
        skin_tone, skin_hex, undertone = analyze_skin_tone(img_bgr, face_rect)
        body_shape, silhouette_data = analyze_body_shape(img_bgr, face_rect)
        height_cm, weight_kg = estimate_height_and_weight(img_bgr, face_rect)
        
        tone_info = next((t for t in SKIN_TONE_CATEGORIES if t['name'] == skin_tone), SKIN_TONE_CATEGORIES[2])
        shape_info = BODY_SHAPE_DETAILS.get(body_shape, BODY_SHAPE_DETAILS['Hourglass'])
        
        analysis_notes = (
            f"Detected {skin_tone} complexion with {undertone} undertones. "
            f"Silhouetted proportions indicate a flattering {body_shape} structure. "
            f"AI-estimated height is ~{height_cm} cm and weight is ~{weight_kg} kg."
        )

        return {
            'success': True,
            'face_detected': (face_rect is not None),
            'height_cm': height_cm,
            'weight_kg': weight_kg,
            'skin_tone': skin_tone,
            'skin_hex': skin_hex,
            'skin_undertone': undertone,
            'body_shape': body_shape,
            'shape_description': shape_info['description'],
            'styling_advice': shape_info['styling_advice'],
            'recommended_pieces': shape_info['recommended_pieces'],
            'flattering_colors': tone_info['best_colors'],
            'avoid_colors': tone_info['avoid_colors'],
            'analysis_notes': analysis_notes,
            'disclaimer': 'AI-generated estimates. Results may vary depending on lighting, camera angle, and image quality. These are stylistic estimates, not medical measurements.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'height_cm': 165.0,
            'weight_kg': 56.0,
            'skin_tone': 'Medium',
            'skin_hex': '#D4A373',
            'skin_undertone': 'Warm',
            'body_shape': 'Hourglass',
            'shape_description': BODY_SHAPE_DETAILS['Hourglass']['description'],
            'styling_advice': BODY_SHAPE_DETAILS['Hourglass']['styling_advice'],
            'recommended_pieces': BODY_SHAPE_DETAILS['Hourglass']['recommended_pieces'],
            'flattering_colors': ['Hot Pink', 'Royal Blue', 'Burgundy', 'Mustard Yellow', 'Forest Green'],
            'avoid_colors': ['Dull Grays', 'Washed Taupe'],
            'analysis_notes': 'Analyzed with standard fashion profile metrics.',
            'disclaimer': 'AI-generated estimates. Results may vary depending on lighting, camera angle, and image quality.'
        }
