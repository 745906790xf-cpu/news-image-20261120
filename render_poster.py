#!/usr/bin/env python3
"""Render the one-day world-news poster for Friday 20 November 2026.

Draws a 1024x1024 newspaper-style front page with Pillow: a masthead
naming the day, one lead story, and a 3x3 grid of the day's other big
stories across regions and fields, each with a small drawn icon.
Output: poster.png next to this file (the entry's image).
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 236)
INK = (22, 24, 29)
NAVY = (20, 33, 61)
GOLD = (242, 193, 78)
RED = (178, 34, 34)
MUTED = (92, 96, 104)
CARD = (255, 253, 248)
LINE = (205, 198, 184)

SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerif-Black.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS_REG = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def spaced(draw, xy, text, fnt, fill, spacing=6, anchor="la"):
    """Draw text with manual letter spacing."""
    x, y = xy
    total = sum(draw.textlength(ch, font=fnt) + spacing for ch in text) - spacing
    if anchor == "ma":
        x -= total / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + spacing


# ---------- icons (drawn in a 64x64 box at ox, oy) ----------

def icon_globe(d, ox, oy, c):
    d.ellipse([ox + 6, oy + 6, ox + 58, oy + 58], outline=c, width=4)
    d.line([ox + 6, oy + 32, ox + 58, oy + 32], fill=c, width=3)
    d.ellipse([ox + 22, oy + 6, ox + 42, oy + 58], outline=c, width=3)


def icon_scales(d, ox, oy, c):
    d.line([ox + 32, oy + 8, ox + 32, oy + 48], fill=c, width=4)
    d.line([ox + 10, oy + 14, ox + 54, oy + 14], fill=c, width=4)
    for cx in (ox + 14, ox + 50):
        d.line([cx, oy + 14, cx - 8, oy + 30], fill=c, width=3)
        d.line([cx, oy + 14, cx + 8, oy + 30], fill=c, width=3)
        d.arc([cx - 10, oy + 24, cx + 10, oy + 40], 0, 180, fill=c, width=3)
    d.line([ox + 20, oy + 52, ox + 44, oy + 52], fill=c, width=4)


def icon_chart(d, ox, oy, c):
    d.line([ox + 8, oy + 56, ox + 8, oy + 8], fill=c, width=4)
    d.line([ox + 8, oy + 56, ox + 58, oy + 56], fill=c, width=4)
    pts = [(ox + 14, oy + 46), (ox + 28, oy + 36), (ox + 38, oy + 40), (ox + 54, oy + 16)]
    d.line(pts, fill=c, width=5, joint="curve")
    d.polygon([(ox + 54, oy + 10), (ox + 58, oy + 22), (ox + 46, oy + 20)], fill=c)


def icon_leaf(d, ox, oy, c):
    d.pieslice([ox + 8, oy + 6, ox + 58, oy + 56], 300, 150, fill=c)
    d.line([ox + 14, oy + 54, ox + 50, oy + 14], fill=PAPER, width=3)


def icon_chip(d, ox, oy, c):
    d.rectangle([ox + 16, oy + 16, ox + 48, oy + 48], outline=c, width=4)
    d.rectangle([ox + 26, oy + 26, ox + 38, oy + 38], fill=c)
    for i in range(3):
        t = ox + 22 + i * 10
        d.line([t, oy + 6, t, oy + 16], fill=c, width=3)
        d.line([t, oy + 48, t, oy + 58], fill=c, width=3)
        d.line([ox + 6, oy + 22 + i * 10, ox + 16, oy + 22 + i * 10], fill=c, width=3)
        d.line([ox + 48, oy + 22 + i * 10, ox + 58, oy + 22 + i * 10], fill=c, width=3)


def icon_drone(d, ox, oy, c):
    d.rectangle([ox + 26, oy + 26, ox + 38, oy + 38], fill=c)
    for cx, cy in ((ox + 12, oy + 12), (ox + 52, oy + 12), (ox + 12, oy + 52), (ox + 52, oy + 52)):
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=c, width=3)
        d.line([cx, cy, ox + 32, oy + 32], fill=c, width=3)


def icon_sunrise(d, ox, oy, c):
    d.pieslice([ox + 14, oy + 16, ox + 50, oy + 52], 180, 360, fill=c)
    d.line([ox + 6, oy + 52, ox + 58, oy + 52], fill=c, width=4)
    for dx, dy in ((-20, -6), (0, -12), (20, -6)):
        d.line([ox + 32 + dx, oy + 18 + dy, ox + 32 + dx * 1.3, oy + 8 + dy], fill=c, width=3)


def icon_tent(d, ox, oy, c):
    d.polygon([(ox + 32, oy + 10), (ox + 58, oy + 54), (ox + 6, oy + 54)], outline=c, width=4)
    d.polygon([(ox + 32, oy + 32), (ox + 42, oy + 54), (ox + 22, oy + 54)], fill=c)


def icon_frame(d, ox, oy, c):
    d.rectangle([ox + 8, oy + 12, ox + 56, oy + 52], outline=c, width=4)
    d.ellipse([ox + 16, oy + 18, ox + 34, oy + 34], fill=c)
    d.arc([ox + 30, oy + 30, ox + 52, oy + 48], 300, 120, fill=c, width=4)


def icon_sprout(d, ox, oy, c):
    d.ellipse([ox + 38, oy + 6, ox + 58, oy + 26], outline=c, width=3)
    d.line([ox + 30, oy + 56, ox + 30, oy + 30], fill=c, width=4)
    d.pieslice([ox + 8, oy + 16, ox + 32, oy + 36], 270, 90, fill=c)
    d.pieslice([ox + 28, oy + 22, ox + 50, oy + 40], 270, 90, fill=c)
    d.line([ox + 12, oy + 58, ox + 48, oy + 58], fill=c, width=4)


ICONS = {
    "globe": icon_globe, "scales": icon_scales, "chart": icon_chart,
    "leaf": icon_leaf, "chip": icon_chip, "drone": icon_drone,
    "sunrise": icon_sunrise, "tent": icon_tent, "frame": icon_frame,
    "sprout": icon_sprout,
}

STORIES = [
    ("JUSTICE", "scales", (120, 72, 160),
     "ICJ: Myanmar committed genocide",
     "Rohingya ruling passes 9-6."),
    ("MARKETS", "chart", (30, 130, 76),
     "Anthropic soars 34% in record IPO",
     "Valued near $2 trillion."),
    ("CLIMATE", "leaf", (46, 140, 110),
     "COP31 draft drops fossil fuels",
     "Outrage at UN climate talks."),
    ("TECH", "chip", (38, 92, 160),
     "California subpoenas Nvidia",
     "Did AI chips reach China?"),
    ("WAR", "drone", (150, 60, 50),
     "UK sends 1,000+ drones to Ukraine",
     "£260m package, Berlin speech."),
    ("ASIA", "sunrise", (200, 120, 30),
     "Xi at APEC: 'must not turn back'",
     "Cooperation urged at summit."),
    ("MIDDLE EAST", "tent", (160, 110, 40),
     "Gaza: 65,000 tents await entry",
     "Winter aid stalls in cold."),
    ("CULTURE", "frame", (170, 80, 120),
     "Van Gogh sells for record $190m",
     "Record price after dispute."),
    ("SCIENCE", "sprout", (90, 140, 60),
     "Potatoes grown in moon soil",
     "Harvest from lunar regolith."),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 168], fill=NAVY)
    d.rectangle([0, 168, W, 174], fill=GOLD)
    d.text((W / 2, 14), "THE WORLD IN A DAY", font=font(SERIF_BLACK, 62),
           fill=(255, 255, 255), anchor="ma")
    spaced(d, (W / 2, 94), "FRIDAY · 20 NOVEMBER 2026", font(SANS_BOLD, 40),
           GOLD, spacing=5, anchor="ma")
    d.text((W / 2, 140), "One picture of the day's world news",
           font=font(SANS_REG, 19), fill=(200, 208, 224), anchor="ma")

    # ---- lead story ----
    y = 174
    d.rectangle([0, y, W, y + 192], fill=(255, 255, 255))
    d.rectangle([0, y + 192, W, y + 195], fill=LINE)
    spaced(d, (36, y + 14), "LEAD STORY — WORLD POLITICS", font(SANS_BOLD, 20),
           RED, spacing=3)
    d.text((36, y + 40), "Trump, Putin & Xi hold", font=font(SERIF_BOLD, 50), fill=INK)
    d.text((36, y + 94), "first trilateral talks", font=font(SERIF_BOLD, 50), fill=INK)
    d.text((36, y + 152), "The three leaders meet and issue a joint 'peace declaration'.",
           font=font(SANS_REG, 25), fill=(52, 56, 64))
    # three flags, right side
    fx = 812
    for i, col in enumerate([(58, 90, 170), (200, 60, 60), (222, 170, 40)]):
        x0 = fx + i * 64
        d.line([x0, y + 140, x0, y + 40], fill=INK, width=4)
        d.rectangle([x0, y + 40, x0 + 46, y + 70], fill=col)
    for i, lab in enumerate(["USA", "RUS", "CHN"]):
        d.text((fx + i * 64 + 23, y + 148), lab, font=font(SANS_BOLD, 18),
               fill=MUTED, anchor="ma")

    # ---- 3x3 grid ----
    gx, gy = 24, 378
    cw, ch, gap = 320, 192, 8
    for idx, (kick, icon, color, head, summ) in enumerate(STORIES):
        cx = gx + (idx % 3) * (cw + gap)
        cy = gy + (idx // 3) * (ch + gap)
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=CARD, outline=LINE, width=2)
        d.rectangle([cx, cy, cx + cw, cy + 8], fill=color)
        ICONS[icon](d, cx + 12, cy + 14, color)
        spaced(d, (cx + 86, cy + 30), kick, font(SANS_BOLD, 19), color, spacing=2)
        hy = cy + 80
        for line in wrap(d, head, font(SANS_BOLD, 26), cw - 28):
            d.text((cx + 14, hy), line, font=font(SANS_BOLD, 26), fill=INK)
            hy += 31
        sy = hy + 6
        for line in wrap(d, summ, font(SANS_REG, 19), cw - 28):
            d.text((cx + 14, sy), line, font=font(SANS_REG, 19), fill=MUTED)
            sy += 23

    # ---- footer ----
    fy = gy + 3 * (ch + gap) + 6
    d.rectangle([0, fy, W, H], fill=NAVY)
    spaced(d, (W / 2, fy + 9), "FRIDAY 20 NOVEMBER 2026 — THE DAY IN ONE PICTURE",
           font(SANS_BOLD, 20), (255, 255, 255), spacing=3, anchor="ma")

    img.save("poster.png", optimize=True)
    print("wrote poster.png")


if __name__ == "__main__":
    main()
