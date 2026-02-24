"""Generate a 560x280 competition thumbnail for Kaggle submission."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 560, 280
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "thumbnail.png")

img = Image.new("RGBA", (W, H), (2, 27, 51, 255))
draw = ImageDraw.Draw(img)

# Subtle gradient glow from top-right
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
for r in range(200, 0, -2):
    alpha = max(0, int(12 * (1 - r / 200)))
    od.ellipse([W * 0.55 - r, -r, W * 0.55 + r, r * 2], fill=(44, 163, 250, alpha))
img = Image.alpha_composite(img, overlay)
draw = ImageDraw.Draw(img)

# Accent line at bottom
draw.rectangle([0, H - 3, W, H], fill=(44, 163, 250, 255))

# Fonts
def get_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

font_brand = get_font(40, bold=True)
font_sub = get_font(16)
font_models = get_font(13)
font_tag = get_font(11, bold=True)

# Medical cross icon
cx, cy = 50, 105
s = 15
draw.rectangle([cx - 5, cy - s, cx + 5, cy + s], fill=(44, 163, 250, 255))
draw.rectangle([cx - s, cy - 5, cx + s, cy + 5], fill=(44, 163, 250, 255))

# Brand name
draw.text((82, 85), "Keneya Lens", fill=(255, 255, 255, 255), font=font_brand)

# Subtitle
draw.text((82, 135), "Offline Agentic Clinical Decision Support", fill=(255, 255, 255, 170), font=font_sub)

# Model badges
y_models = 172
badge_texts = ["MedGemma 4B-IT", "CXR Foundation", "Derm Foundation"]
x_pos = 82
for badge in badge_texts:
    bbox = draw.textbbox((0, 0), badge, font=font_models)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.rounded_rectangle(
        [x_pos - 8, y_models - 5, x_pos + tw + 8, y_models + th + 7],
        radius=4,
        fill=(44, 163, 250, 50),
        outline=(44, 163, 250, 100),
    )
    draw.text((x_pos, y_models), badge, fill=(180, 220, 255, 255), font=font_models)
    x_pos += tw + 26

# Bottom tag
draw.text((82, 218), "Google HAI-DEF  \u2022  MedGemma Impact Challenge 2026", fill=(255, 255, 255, 90), font=font_tag)

# Decorative dot grid (top-right)
for i in range(6):
    for j in range(4):
        dx = W - 100 + i * 14
        dy = 24 + j * 14
        if dx < W - 12:
            draw.ellipse([dx, dy, dx + 3, dy + 3], fill=(44, 163, 250, 25))

# Convert to RGB for PNG
img_rgb = img.convert("RGB")
img_rgb.save(OUT, "PNG")
print(f"Saved: {OUT}")
print(f"Size: {W}x{H}")
