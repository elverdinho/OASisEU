import re
"""Per-page header scrim strength, measured on the real background pixels.

The header floats over the first block's background image. We composite a dark
scrim over the region where the nav links sit and binary-search the smallest
opacity that brings the nav colour to a WCAG contrast ratio of 4.5:1.
"""
import os
from PIL import Image

SCRIM = (17, 19, 22)
TARGET = 4.5

def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def luminance(rgb):
    r, g, b = rgb[:3]
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

def ratio(l1, l2):
    a, b = max(l1, l2), min(l1, l2)
    return (a + 0.05) / (b + 0.05)

def _composite(px, colour, alpha):
    return tuple(px[i] * (1 - alpha) + colour[i] * alpha for i in range(3))

def header_scrim(image_path, overlay_opacity, nav_rgb, block_w=1440, header_h=152,
                 nav_fraction=0.55, cap=0.88, target=5.2):
    """Smallest scrim alpha (0..cap) that makes nav_rgb readable, or 0 if already fine."""
    if not image_path or not os.path.exists(image_path):
        return 0.45
    try:
        im = Image.open(image_path).convert("RGB")
    except Exception:
        return 0.45
    w, h = im.size
    # the background is painted with `cover` at block_w wide; the header covers the
    # top header_h css px, and the links sit in the right-hand nav_fraction of it.
    # `cover` at block_w wide: 1 css px = (w / block_w) image px
    scale = block_w / w
    crop_h = max(1, min(h, int(header_h / scale)))
    x0 = int(w * (1 - nav_fraction))
    region = im.crop((x0, 0, w, crop_h))
    # sample raw pixels on a stride: downscaling would average bright strokes away,
    # and it is exactly those local bright spots that swallow the nav text
    rw, rh = region.size
    sx, sy = max(1, rw // 90), max(1, rh // 30)
    px = [region.getpixel((x, y)) for y in range(0, rh, sy) for x in range(0, rw, sx)]
    # ignore the harshest 2% of pixels: a couple of specks should not darken the whole bar
    px.sort(key=lambda p: -luminance(p))
    px = px[int(len(px) * 0.02):] or px
    if overlay_opacity:
        px = [_composite(p, SCRIM, float(overlay_opacity)) for p in px]
    nav_l = luminance(nav_rgb)

    def worst(alpha):
        return min(ratio(nav_l, luminance(_composite(p, SCRIM, alpha))) for p in px)

    if worst(0) >= target:
        return 0.0
    lo, hi = 0.0, cap
    if worst(cap) < target:
        return cap
    for _ in range(18):
        mid = (lo + hi) / 2
        if worst(mid) >= target: hi = mid
        else: lo = mid
    return round(hi, 3)


def parse_rgb(css):
    n = [int(x) for x in re.findall(r"\d+", css or "")[:3]]
    return tuple(n) if len(n) == 3 else (0, 0, 0)

def darken_to_pass(fg, bg_rgb, target=TARGET, steps=60):
    """Darken fg (keeping its hue) until it clears `target` against bg_rgb."""
    lb = luminance(bg_rgb)
    if ratio(luminance(fg), lb) >= target: return fg, False
    r, g, b = fg
    for i in range(1, steps + 1):
        k = 1 - i / steps
        cand = (r * k, g * k, b * k)
        if ratio(luminance(cand), lb) >= target:
            return tuple(int(round(c)) for c in cand), True
    return (17, 19, 22), True


def needed_overlay(image_path, base_overlay, fg_rgb, cap=0.55, region=None):
    """Smallest extra scrim over a background image that lets fg_rgb read on it."""
    if not image_path or not os.path.exists(image_path):
        return float(base_overlay or 0)
    try:
        im = Image.open(image_path).convert("RGB")
    except Exception:
        return float(base_overlay or 0)
    if region:
        im = im.crop(region)
    w, h = im.size
    sx, sy = max(1, w // 70), max(1, h // 40)
    px = [im.getpixel((x, y)) for y in range(0, h, sy) for x in range(0, w, sx)]
    px.sort(key=lambda p: -luminance(p))
    px = px[int(len(px) * 0.05):] or px
    fl = luminance(fg_rgb)

    def worst(alpha):
        return min(ratio(fl, luminance(_composite(p, SCRIM, alpha))) for p in px)

    base = float(base_overlay or 0)
    if worst(base) >= TARGET:
        return base
    if worst(cap) < TARGET:
        return cap
    lo, hi = base, cap
    for _ in range(16):
        mid = (lo + hi) / 2
        if worst(mid) >= TARGET: hi = mid
        else: lo = mid
    return round(hi, 3)
