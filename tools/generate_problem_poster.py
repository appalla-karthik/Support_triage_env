from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


OUT = Path("output/imagegen/mobile-nav-problem-poster.png")
W, H = 1600, 900


def font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/seguiemj.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), "#090d14")
draw = ImageDraw.Draw(img)

# Background glow
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
g = ImageDraw.Draw(glow)
g.ellipse((40, 20, 700, 620), fill=(95, 108, 255, 60))
g.ellipse((980, 180, 1550, 820), fill=(0, 201, 255, 40))
g.ellipse((420, 500, 1040, 980), fill=(162, 77, 255, 38))
glow = glow.filter(ImageFilter.GaussianBlur(80))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img)

title_font = font(52, True)
sub_font = font(24, False)
label_font = font(22, True)
small_font = font(18, False)

draw.text((70, 56), "Responsive Navigation Failure", fill="#f4f7fb", font=title_font)
draw.text(
    (72, 122),
    "Desktop dashboard stays clean while the mobile experience breaks.",
    fill="#9fb0c8",
    font=sub_font,
)


def rounded_box(xy, radius=26, fill="#111827", outline="#243044", width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


# Laptop frame
laptop = (78, 220, 1010, 760)
rounded_box(laptop, 34, "#0d121c", "#202b3d", 3)
draw.rounded_rectangle((108, 250, 980, 710), radius=24, fill="#101725", outline="#283449", width=2)
draw.rounded_rectangle((420, 742, 668, 762), radius=9, fill="#1a2232")

# Laptop UI
draw.rounded_rectangle((132, 272, 270, 668), radius=22, fill="#121926", outline="#243146", width=2)
for i, (y, text, active) in enumerate(
    [(305, "Dashboard", True), (374, "Operations", False), (443, "Inspectors", False), (512, "API Docs", False)]
):
    fill = "#5d69ff" if active else "#1a2231"
    outline = "#6d79ff" if active else "#1a2231"
    draw.rounded_rectangle((152, y, 250, y + 46), radius=15, fill=fill, outline=outline)
    draw.text((173, y + 12), text[:2].upper(), fill="#ffffff", font=small_font)

draw.rounded_rectangle((298, 272, 950, 428), radius=26, fill="#131b2a", outline="#243146", width=2)
draw.text((332, 306), "Desktop View", fill="#f4f7fb", font=label_font)
draw.text((332, 345), "Stable navigation, aligned cards, clear controls", fill="#94a2b8", font=small_font)

for x in [300, 465, 630, 795]:
    draw.rounded_rectangle((x, 462, x + 145, 578), radius=22, fill="#131b2a", outline="#243146", width=2)
draw.text((332, 500), "Works", fill="#31d0aa", font=label_font)
draw.text((498, 500), "Clean", fill="#dce5ff", font=label_font)
draw.text((662, 500), "Stable", fill="#dce5ff", font=label_font)
draw.text((822, 500), "Ready", fill="#dce5ff", font=label_font)

# Phone frame
phone = (1090, 170, 1450, 790)
rounded_box(phone, 42, "#0b1018", "#273246", 3)
draw.rounded_rectangle((1110, 205, 1430, 760), radius=30, fill="#0f1623", outline="#1f2a3a", width=2)

# Drawer overlay
draw.rounded_rectangle((1118, 214, 1418, 278), radius=18, fill="#101722", outline="#263246", width=2)
draw.rounded_rectangle((1128, 224, 1178, 264), radius=14, fill="#6674ff")
draw.rounded_rectangle((1358, 224, 1402, 264), radius=12, fill="#171f2d")

draw.rectangle((1120, 285, 1418, 760), fill="#080d14")
drawer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d2 = ImageDraw.Draw(drawer)
d2.rounded_rectangle((1128, 286, 1338, 760), radius=26, fill=(11, 16, 24, 235), outline=(34, 45, 63, 255), width=2)
drawer = drawer.filter(ImageFilter.GaussianBlur(0))
img = Image.alpha_composite(img.convert("RGBA"), drawer).convert("RGB")
draw = ImageDraw.Draw(img)

for y, text in [(322, "Dashboard"), (390, "Operations"), (458, "Inspectors"), (526, "API Docs")]:
    draw.rounded_rectangle((1144, y, 1318, y + 46), radius=15, fill="#121a28", outline="#1e2b3e")
    draw.text((1161, y + 12), text[:2].upper(), fill="#c9d5ee", font=small_font)
    draw.text((1208, y + 12), text, fill="#b7c4da", font=small_font)

# Broken content behind drawer
draw.text((1146, 620), "Reset", fill="#ffffff", font=label_font)
draw.text((1365, 620), "cut off", fill="#ff8b8b", font=small_font)
draw.rounded_rectangle((1140, 675, 1442, 730), radius=18, fill="#5d69ff")
draw.text((1360, 688), "Overflow", fill="#ffffff", font=small_font)

# Callouts
draw.line((1010, 345, 1085, 345), fill="#ffb648", width=4)
draw.rounded_rectangle((824, 316, 1000, 378), radius=18, fill="#2c241d", outline="#6b4b1f", width=2)
draw.text((846, 334), "Desktop works", fill="#ffd89f", font=small_font)

draw.line((1328, 582, 1540, 620), fill="#ff6f91", width=4)
draw.rounded_rectangle((1220, 620, 1542, 710), radius=22, fill="#271820", outline="#6a2f43", width=2)
draw.text((1242, 646), "Mobile issues:", fill="#ffd3df", font=label_font)
draw.text((1242, 678), "drawer navigation, cropped controls, overflow", fill="#f2b3c6", font=small_font)

draw.text((72, 824), "Problem theme visual for presentation / video cover", fill="#7f90aa", font=small_font)

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, quality=95)
print(OUT)
