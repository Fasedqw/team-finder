import io
import os
import random

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

PALETTE = [
    (149, 193, 228),
    (180, 223, 167),
    (253, 200, 149),
    (215, 173, 215),
    (248, 172, 172),
    (152, 210, 210),
    (230, 210, 160),
]

SIZE = (200, 200)
FONT_PATH = os.path.join(settings.BASE_DIR, "static", "fonts", "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf")


def generate_avatar(letter):
    letter = letter.upper()
    img = Image.new("RGB", SIZE, color=random.choice(PALETTE))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, size=100)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (SIZE[0] - (bbox[2] - bbox[0])) / 2 - bbox[0]
    y = (SIZE[1] - (bbox[3] - bbox[1])) / 2 - bbox[1]
    draw.text((x, y), letter, fill=(60, 60, 60), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ContentFile(buf.read(), name=f"avatar_{letter}.png")
