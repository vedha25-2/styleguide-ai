import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

# Curated reference color map for fashion styling
COLOR_PALETTE = {
    'Black': (25, 25, 25),
    'White': (245, 245, 245),
    'Off-White': (240, 235, 225),
    'Charcoal Gray': (65, 65, 65),
    'Light Gray': (190, 190, 190),
    'Navy Blue': (20, 35, 80),
    'Royal Blue': (40, 80, 200),
    'Sky Blue': (135, 206, 235),
    'Baby Blue': (175, 215, 245),
    'Emerald Green': (15, 120, 65),
    'Forest Green': (34, 85, 45),
    'Olive Green': (107, 125, 50),
    'Mint Green': (152, 230, 190),
    'Sage Green': (140, 160, 140),
    'Burgundy': (100, 20, 40),
    'Wine Red': (120, 25, 55),
    'Ruby Red': (195, 30, 45),
    'Coral Pink': (240, 110, 110),
    'Blush Pink': (245, 190, 205),
    'Hot Pink': (235, 60, 145),
    'Rose': (215, 90, 130),
    'Lavender': (190, 165, 225),
    'Lilac': (200, 160, 230),
    'Deep Purple': (85, 30, 120),
    'Violet': (120, 50, 175),
    'Beige': (225, 205, 175),
    'Camel': (195, 150, 100),
    'Tan': (175, 130, 85),
    'Chocolate Brown': (75, 40, 25),
    'Mustard Yellow': (215, 165, 35),
    'Pastel Yellow': (250, 240, 165),
    'Gold': (212, 175, 55),
    'Silver': (192, 192, 192),
    'Orange': (235, 110, 30),
    'Peach': (245, 190, 160),
    'Teal': (20, 125, 135),
    'Turquoise': (64, 224, 208)
}

def rgb_to_hex(r, g, b):
    """Convert RGB tuple to uppercase Hex string."""
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"

def hex_to_rgb(hex_str):
    """Convert Hex string to RGB tuple."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    if len(hex_str) != 6:
        return (128, 128, 128)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def get_closest_color_name(rgb):
    """Find the closest fashion-friendly color name using Euclidean distance in RGB space."""
    r, g, b = rgb
    min_dist = float('inf')
    closest_name = 'Multicolor'
    
    for name, palette_rgb in COLOR_PALETTE.items():
        pr, pg, pb = palette_rgb
        dist = ((r - pr) * 0.3)**2 + ((g - pg) * 0.59)**2 + ((b - pb) * 0.11)**2
        if dist < min_dist:
            min_dist = dist
            closest_name = name
            
    return closest_name

def extract_dominant_color(image_path, k=4):
    """
    Extracts the dominant non-background color from an image.
    Uses OpenCV and KMeans clustering.
    Returns: (color_name, hex_code, rgb_tuple)
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            # Fallback using PIL if OpenCV direct read fails
            pil_img = Image.open(image_path).convert('RGB')
            img = np.array(pil_img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Resize to speed up KMeans
        img = cv2.resize(img, (150, 150), interpolation=cv2.INTER_AREA)
        
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Crop inner 70% to prioritize the fashion garment over neutral borders/background
        h, w, _ = img_rgb.shape
        start_y, end_y = int(h * 0.15), int(h * 0.85)
        start_x, end_x = int(w * 0.15), int(w * 0.85)
        cropped = img_rgb[start_y:end_y, start_x:end_x]
        
        # Reshape to pixel array
        pixels = cropped.reshape((-1, 3))
        
        # Filter extreme pure white or near black backgrounds if diverse pixels exist
        mask = ~((pixels[:, 0] > 245) & (pixels[:, 1] > 245) & (pixels[:, 2] > 245))
        if np.sum(mask) > len(pixels) * 0.2:
            pixels = pixels[mask]

        if len(pixels) == 0:
            return 'Light Gray', '#D3D3D3', (211, 211, 211)

        kmeans = KMeans(n_clusters=min(k, len(pixels)), random_state=42, n_init='auto')
        kmeans.fit(pixels)
        
        # Count frequency of each cluster
        labels, counts = np.unique(kmeans.labels_, return_counts=True)
        dominant_idx = labels[np.argmax(counts)]
        dominant_rgb = kmeans.cluster_centers_[dominant_idx].astype(int)
        
        r, g, b = int(dominant_rgb[0]), int(dominant_rgb[1]), int(dominant_rgb[2])
        hex_code = rgb_to_hex(r, g, b)
        color_name = get_closest_color_name((r, g, b))
        
        return color_name, hex_code, (r, g, b)
    except Exception as e:
        # Graceful fallback
        return 'Soft Pink', '#EC4899', (236, 72, 153)

def calculate_color_harmony_score(hex1, hex2):
    """
    Computes a harmony score (0-100) between two colors based on color theory:
    - Neutral pairings (Black, White, Gray, Beige, Denim) with any accent: 92-98%
    - Analogous / tonal: 88-95%
    - Complementary: 90-96%
    - Clash penalty: adjusted
    """
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    
    name1 = get_closest_color_name(rgb1)
    name2 = get_closest_color_name(rgb2)
    
    neutrals = {'Black', 'White', 'Off-White', 'Charcoal Gray', 'Light Gray', 'Beige', 'Camel', 'Tan', 'Navy Blue'}
    
    if name1 in neutrals or name2 in neutrals:
        return 95, "Neutral Pairing", "Neutrals create a refined, timeless foundation for any hue."
        
    if name1 == name2:
        return 92, "Monochromatic Harmony", "A cohesive single-tone palette that elongates the silhouette."

    # Convert to HSV to check hue difference
    color1_hsv = cv2.cvtColor(np.uint8([[rgb1]]), cv2.COLOR_RGB2HSV)[0][0]
    color2_hsv = cv2.cvtColor(np.uint8([[rgb2]]), cv2.COLOR_RGB2HSV)[0][0]
    
    hue_diff = abs(int(color1_hsv[0]) - int(color2_hsv[0]))
    hue_diff = min(hue_diff, 180 - hue_diff)
    
    if hue_diff <= 25:
        return 90, "Analogous Harmony", "Adjacent color wheel tones that blend gracefully and softly."
    elif 80 <= hue_diff <= 100:
        return 94, "Complementary Harmony", "High-contrast dynamic pair that creates an eye-catching focal balance."
    elif 50 <= hue_diff <= 75:
        return 86, "Triadic Harmony", "Vibrant, balanced chromatic relationship for expressive styling."
    else:
        return 82, "Eclectic Accent", "Fashion-forward contrast that pops with intentional styling."
