from pathlib import Path
from PIL import Image, ImageOps
import re
p=Path(__file__).parent
source=Path('C:/Users/Victor/Downloads')
items=[('IMG_7379.JPG.jpeg','butterfly','Butterflies & crystals','nails'),('IMG_9500.JPG.jpeg','pink-sculpt','Pink sculpted tips','nails'),('IMG_9163.JPG.jpeg','french-fine','The fine-line French','nails'),('IMG_7378.JPG.jpeg','olive','Olive obsession','nails'),('IMG_7370.PNG','pink-gold','Pink, with a little gold','nails'),('IMG_7367.PNG','monochrome','Monochrome curves','nails'),('IMG_8267.PNG','soft-pink','Soft pink energy','nails'),('IMG_8076.PNG','star-french','A star moment','nails'),('IMG_7846.PNG','blue-floral','Something blue','nails'),('IMG_8203.PNG','ruby','Ruby glow','nails'),('IMG_9376.PNG','polka','Polka-dot French','nails'),('IMG_9587.JPG.jpeg','mixed-art','A little of everything','nails'),('IMG_9715.PNG','gold-pink','Pink & gold details','nails'),('IMG_9792.PNG','pearl','Pearls & petals','nails'),('IMG_7364.PNG','toes','Fresh French toes','nails')]
for filename,slug,label,category in items:
    im=ImageOps.exif_transpose(Image.open(source/filename)).convert('RGB')
    if filename.endswith('.PNG'):
        # Supplied phone screenshots have black UI margins above and below the photograph.
        w,h=im.size
        im=im.crop((0,round(h*.09),w,round(h*.91)))
    for width,suffix in [(1100,''),(550,'-small')]:
        out=im.copy();out.thumbnail((width,2000));out.save(p/'dist/assets'/f'{slug}{suffix}.webp','WEBP',quality=87,method=6)
html=(p/'dist/index.html').read_text(encoding='utf-8')
html=html.replace('assets/pink.jpg','assets/butterfly.webp').replace('Soft pink almond nails with delicate embellishments','Butterfly and crystal nail art with pink and zebra details')
html=html.replace('assets/chrome.jpg','assets/french-fine.webp').replace('Metallic silver chrome nail design','Fine white and brown French tips on nude almond nails')
cards=[]
for filename,slug,label,category in items:
    cards.append(f'<button class="gallery-item" data-category="{category}" data-label="{label}"><img loading="lazy" decoding="async" src="assets/{slug}.webp" srcset="assets/{slug}-small.webp 550w, assets/{slug}.webp 1100w" sizes="(max-width:800px) 44vw, 29vw" alt="{label} — nail work by 23 Lux Nails"><span>{label} ↗</span></button>')
cards.extend(['<button class="gallery-item" data-category="piercings" data-label="A little ear candy"><img loading="lazy" src="assets/piercing.jpg" alt="Ear piercing jewellery from the studio gallery"><span>A little ear candy ↗</span></button>','<button class="gallery-item" data-category="tattoos" data-label="Ink with meaning"><img loading="lazy" src="assets/ink.jpg" alt="Script and butterfly tattoo design from the studio TikTok"><span>Ink with meaning ↗</span></button>'])
start=html.index('<div class="gallery">');end=html.index('</div><a class="text-link"',start)
html=html[:start]+'<div class="gallery">'+''.join(cards)+html[end:]
html=html.replace('Real work from the 23 Lux gallery.','Find your next look in the 23 Lux gallery.')
html=html.replace('<a href="#work">The work</a>','<a href="#work">The work</a><a href="#prices">Prices</a>')
prices='''<section class="price-section section" id="prices"><div class="section-heading"><div><p class="eyebrow">THE SERVICE MENU</p><h2>Your look.<br><em>Your little luxury.</em></h2></div><p>Explore the studio price lists.<br>Choose a service, then let's get you booked.</p></div><div class="price-preview"><article><h3>Nails & finishing touches</h3><p>Gel polish from ₦10,000 · Acrylic sets from ₦18,000<br>Manicure ₦7,000 · Pedicure ₦12,000</p><a class="text-link" href="assets/nails-prices.webp" target="_blank" rel="noopener">Open full nail price list ↗</a><img loading="lazy" src="assets/nails-prices.webp" alt="23 Lux Nails full nail service price list"></article><article><h3>Piercings</h3><p>Helix ₦8,000 · Nostril ₦9,000 · Lobe pair ₦10,000<br>View the full list for placements and prices.</p><a class="text-link" href="assets/piercing-prices.webp" target="_blank" rel="noopener">Open full piercing price list ↗</a><img loading="lazy" src="assets/piercing-prices.webp" alt="23 Lux Nails full piercing service price list"></article></div><p class="service-footnote">Nail art and other extras are listed separately. Semi-permanent tattoo prices are available on consultation.</p><a class="button dark" href="#book">Book your next appointment ↗</a></section>'''
html=html.replace('<section class="booking section"',prices+'<section class="booking section"')
(p/'dist/index.html').write_text(html,encoding='utf-8')
for filename,name in [('WhatsApp Image 2026-10-19 at 10.26.05.jpeg','nails-prices'),('WhatsApp Image 2026-10-19 at 10.26.30.jpeg','piercing-prices')]:
    im=Image.open(source/filename).convert('RGB');im.save(p/'dist/assets'/f'{name}.webp','WEBP',quality=92)
print(f'Prepared {len(items)} portfolio photographs and two price lists.')
