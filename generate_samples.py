import os

samples_dir = os.path.join(os.path.dirname(__file__), 'static', 'images', 'samples')
os.makedirs(samples_dir, exist_ok=True)

items = {
    'white_shirt.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#f8fafc"/>
  <path d="M 40 50 L 70 30 L 100 50 L 130 30 L 160 50 L 145 90 L 125 80 L 125 170 L 75 170 L 75 80 L 55 90 Z" fill="#ffffff" stroke="#cbd5e1" stroke-width="2"/>
  <path d="M 100 50 L 100 170" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 4"/>
  <polygon points="85,30 100,55 75,45" fill="#f1f5f9" stroke="#cbd5e1"/>
  <polygon points="115,30 100,55 125,45" fill="#f1f5f9" stroke="#cbd5e1"/>
</svg>''',

    'blue_jeans.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#f0fdf4"/>
  <path d="M 60 40 L 140 40 L 135 175 L 105 175 L 100 95 L 95 175 L 65 175 Z" fill="#2563eb" stroke="#1d4ed8" stroke-width="2"/>
  <path d="M 60 55 L 140 55" stroke="#d97706" stroke-width="1.5"/>
  <path d="M 75 60 C 80 80 90 80 95 60" fill="none" stroke="#d97706" stroke-width="1.5"/>
  <path d="M 105 60 C 110 80 120 80 125 60" fill="none" stroke="#d97706" stroke-width="1.5"/>
</svg>''',

    'floral_dress.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#fdf2f8"/>
  <path d="M 75 35 L 85 30 L 100 45 L 115 30 L 125 35 L 120 80 C 115 85 135 120 155 170 L 45 170 C 65 120 85 85 80 80 Z" fill="#ec4899" stroke="#db2777" stroke-width="2"/>
  <rect x="78" y="78" width="44" height="8" rx="2" fill="#9333ea"/>
  <circle cx="90" cy="120" r="5" fill="#fbcfe8"/>
  <circle cx="115" cy="140" r="6" fill="#fef08a"/>
  <circle cx="75" cy="150" r="5" fill="#ddd6fe"/>
</svg>''',

    'blush_kurti.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#faf5ff"/>
  <path d="M 50 50 L 75 30 L 100 45 L 125 30 L 150 50 L 138 85 L 125 78 L 132 175 L 105 175 L 103 125 L 97 125 L 95 175 L 68 175 L 75 78 L 62 85 Z" fill="#d946ef" stroke="#a21caf" stroke-width="2"/>
  <path d="M 100 45 L 100 95" stroke="#fef08a" stroke-width="2" stroke-dasharray="3 3"/>
</svg>''',

    'white_sneakers.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#f1f5f9"/>
  <path d="M 35 135 C 35 115 55 90 90 90 L 120 90 L 155 125 L 165 145 L 35 145 Z" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
  <path d="M 30 145 L 170 145 C 170 155 160 160 140 160 L 40 160 C 30 160 30 155 30 145 Z" fill="#ec4899"/>
  <line x1="95" y1="95" x2="115" y2="115" stroke="#8b5cf6" stroke-width="2"/>
  <line x1="105" y1="95" x2="125" y2="115" stroke="#8b5cf6" stroke-width="2"/>
</svg>''',

    'nude_heels.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#fff7ed"/>
  <path d="M 45 75 C 55 110 95 130 140 135 L 155 145 L 125 150 C 90 145 60 130 45 105 Z" fill="#e0a96d" stroke="#c27803" stroke-width="1.5"/>
  <path d="M 48 100 L 46 160 L 52 160 L 54 105 Z" fill="#333333"/>
  <path d="M 40 75 C 50 65 70 70 70 85" fill="none" stroke="#c27803" stroke-width="2"/>
</svg>''',

    'pearl_earrings.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#f8fafc"/>
  <circle cx="80" cy="65" r="8" fill="#f59e0b" stroke="#d97706" stroke-width="1"/>
  <line x1="80" y1="73" x2="80" y2="100" stroke="#d97706" stroke-width="2"/>
  <circle cx="80" cy="115" r="16" fill="#f8fafc" stroke="#e2e8f0" stroke-width="2"/>
  <circle cx="75" cy="110" r="4" fill="#ffffff"/>
  <circle cx="120" cy="65" r="8" fill="#f59e0b" stroke="#d97706" stroke-width="1"/>
  <line x1="120" y1="73" x2="120" y2="100" stroke="#d97706" stroke-width="2"/>
  <circle cx="120" cy="115" r="16" fill="#f8fafc" stroke="#e2e8f0" stroke-width="2"/>
  <circle cx="115" cy="110" r="4" fill="#ffffff"/>
</svg>''',

    'gold_necklace.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#fdf4ff"/>
  <path d="M 55 45 C 55 125 145 125 145 45" fill="none" stroke="#f59e0b" stroke-width="3" stroke-dasharray="4 2"/>
  <polygon points="100,105 115,125 100,145 85,125" fill="#fbbf24" stroke="#d97706" stroke-width="2"/>
  <circle cx="100" cy="125" r="4" fill="#ec4899"/>
</svg>''',

    'leather_tote.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#fefce8"/>
  <path d="M 45 85 L 60 165 L 140 165 L 155 85 Z" fill="#78350f" stroke="#451a03" stroke-width="2"/>
  <path d="M 70 85 C 70 45 90 45 90 85" fill="none" stroke="#451a03" stroke-width="3"/>
  <path d="M 110 85 C 110 45 130 45 130 85" fill="none" stroke="#451a03" stroke-width="3"/>
  <rect x="95" y="95" width="10" height="14" rx="2" fill="#f59e0b"/>
</svg>''',

    'retro_sunglasses.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#fdf2f8"/>
  <path d="M 40 90 C 35 115 65 125 80 105 C 85 95 80 85 45 85 Z" fill="#831843"/>
  <path d="M 120 105 C 135 125 165 115 160 90 C 155 85 120 85 115 95 Z" fill="#831843"/>
  <path d="M 80 92 C 90 88 110 88 120 92" fill="none" stroke="#f59e0b" stroke-width="3"/>
  <path d="M 40 90 L 25 85" stroke="#f59e0b" stroke-width="3"/>
  <path d="M 160 90 L 175 85" stroke="#f59e0b" stroke-width="3"/>
</svg>''',

    'trench_coat.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#f8fafc"/>
  <path d="M 45 45 L 80 30 L 100 50 L 120 30 L 155 45 L 140 95 L 125 90 L 135 175 L 65 175 L 75 90 L 60 95 Z" fill="#d97706" stroke="#b45309" stroke-width="2"/>
  <line x1="100" y1="50" x2="100" y2="175" stroke="#78350f" stroke-width="1.5"/>
  <rect x="72" y="105" width="56" height="8" rx="2" fill="#78350f"/>
</svg>''',

    'silk_saree.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%">
  <rect width="200" height="200" rx="16" fill="#fff1f2"/>
  <path d="M 85 35 L 115 35 L 120 65 L 80 65 Z" fill="#831843" stroke="#f59e0b" stroke-width="2"/>
  <path d="M 65 80 C 80 80 135 80 145 175 L 55 175 C 65 125 60 95 65 80 Z" fill="#be123c" stroke="#9f1239" stroke-width="2"/>
  <path d="M 75 35 L 60 55 L 140 170 L 150 150 Z" fill="#f59e0b" stroke="#d97706" stroke-width="1.5"/>
</svg>'''
}

for filename, content in items.items():
    filepath = os.path.join(samples_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
print(f"Generated {len(items)} sample SVGs successfully.")
