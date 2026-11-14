"""
Create visible placeholder images for products
"""
import os
from PIL import Image, ImageDraw, ImageFont

images = [
    ("medical/paracetamol.png", "💊 Paracetamol", "#FF6B6B"),
    ("medical/cough_syrup.png", "🧪 Cough Syrup", "#FF8C42"),
    ("medical/dettol.png", "🧴 Dettol", "#4ECDC4"),
    ("medical/hellokitty_bandaid.png", "🎀 Hello Kitty", "#FF69B4"),
    ("medical/generic_bandaid.png", "🩹 Bandaid", "#FFB6C1"),
    ("medical/spiderman_bandaid.png", "🕷️ Spiderman", "#DC143C"),
    ("medical/vicks_inhaler.png", "💨 Vicks", "#90EE90"),
    ("medical/vicks_vaporub.png", "🧴 VapoRub", "#98FB98"),
    ("medical/volini_gel.png", "💪 Volini Gel", "#87CEEB"),
    ("medical/volini_spray.png", "🌊 Volini Spray", "#4169E1"),
    
    ("essentials/sanitizer.png", "🧼 Sanitizer", "#FFDAB9"),
    ("essentials/tissue.png", "📄 Tissue", "#F0F8FF"),
    ("essentials/detergent.png", "🧺 Detergent", "#FFD700"),
    ("essentials/trashbags.png", "🛍️ Trash Bags", "#A9A9A9"),
    
    ("food/pizza.png", "🍕 Pizza", "#FF6347"),
    ("food/coldbrew.png", "☕ Cold Brew", "#8B4513"),
    ("food/honey.png", "🍯 Honey", "#FFD700"),
    ("food/cake.png", "🍰 Cake", "#FFB6C1"),
    
    ("dresses/floral.png", "👗 Floral Dress", "#FF69B4"),
    ("dresses/denim.png", "👔 Denim", "#191970"),
    ("dresses/gown.png", "👠 Gown", "#8B008B"),
    
    ("jewelry/necklace.png", "📿 Necklace", "#FFD700"),
    ("jewelry/earrings.png", "💎 Earrings", "#E6E6FA"),
    
    ("watches/chrono.png", "⌚ Chrono", "#C0C0C0"),
    ("watches/leather.png", "⌚ Leather", "#8B4513"),
    
    ("skincare/vitc.png", "💊 Vitamin C", "#FFA500"),
    ("skincare/facewash.png", "🧴 Face Wash", "#87CEEB"),
    ("skincare/sunscreen.png", "☀️ Sunscreen", "#FFD700"),
    
    ("electronics/earbuds.png", "🎧 Earbuds", "#000000"),
    ("electronics/fitband.png", "⌚ Fit Band", "#00CED1"),
    ("electronics/powerbank.png", "🔋 Power Bank", "#FF4500"),
    
    ("toys/blocks.png", "🧩 Blocks", "#87CEEB"),
    ("toys/rccar.png", "🏎️ RC Car", "#FF0000"),
    
    ("print/photoframe.png", "🖼️ Photo Frame", "#8B7355"),
    ("print/tshirt.png", "👕 T-Shirt", "#00FF00"),
]

root = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')

for rel_path, label, color in images:
    out = os.path.join(root, *rel_path.split('/'))
    d = os.path.dirname(out)
    os.makedirs(d, exist_ok=True)
    
    # Create a visible placeholder image
    img = Image.new('RGB', (300, 300), color=color)
    draw = ImageDraw.Draw(img)
    
    # Add label text
    try:
        # Try to use a default font, if not available, use default
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Draw text in the center
    text_bbox = draw.textbbox((0, 0), label, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (300 - text_width) // 2
    y = (300 - text_height) // 2
    
    draw.text((x, y), label, fill='white', font=font, stroke_width=2, stroke_fill='black')
    
    img.save(out)
    print(f'Created {out}')

print('✅ All placeholder images created successfully!')
