import os
import base64

images = [
"medical/paracetamol.png",
"medical/cough_syrup.png",
"medical/dettol.png",
"medical/hellokitty_bandaid.png",
"medical/generic_bandaid.png",
"medical/spiderman_bandaid.png",
"medical/vicks_inhaler.png",
"medical/vicks_vaporub.png",
"medical/volini_gel.png",
"medical/volini_spray.png",

"essentials/sanitizer.png",
"essentials/tissue.png",
"essentials/detergent.png",
"essentials/trashbags.png",

"food/pizza.png",
"food/coldbrew.png",
"food/honey.png",
"food/cake.png",

"dresses/floral.png",
"dresses/denim.png",
"dresses/gown.png",

"jewelry/necklace.png",
"jewelry/earrings.png",

"watches/chrono.png",
"watches/leather.png",

"skincare/vitc.png",
"skincare/facewash.png",
"skincare/sunscreen.png",

"electronics/earbuds.png",
"electronics/fitband.png",
"electronics/powerbank.png",

"toys/blocks.png",
"toys/rccar.png",

"print/photoframe.png",
"print/tshirt.png",
]

root = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
# 1x1 transparent PNG
png_b64 = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/w8AAn8B9lW6RAAAAABJRU5ErkJggg=='
png_data = base64.b64decode(png_b64)

for rel in images:
    out = os.path.join(root, *rel.split('/'))
    d = os.path.dirname(out)
    os.makedirs(d, exist_ok=True)
    with open(out, 'wb') as f:
        f.write(png_data)
    print('Created', out)
print('Done')
