#!/usr/bin/env python3
"""Build the v5-lite assets from Ashar's other-AI zip (lite-incoming/).

1. Home background: lite mugen_home_screen_lite.png (1376x768) with the 4 baked
   empty select slots painted out (dark-rock gradient + noise + embers), then:
   - select-bg-lite.png : plain (no title)  -> SFF sprite (101,0)
   - title-bg-lite.png  : "CURSED CLASH" composited into the flame frame
                           -> SFF sprite (100,0)
   Both resized to 1280x720 (engine canvas).
2. Touch icons: extract the neon graphic (fist / kicking figure / bolt) from the
   glass-tile PNGs (their checkerboard background is BAKED IN - RGB, no alpha),
   via a chroma+warmth mask, on transparent. -> site/touch/icons/*.png (128px)
   The block/shield icon is NOT used: IKEMEN has no block key (blocking is
   holding back on the D-pad), so there is no button for it.
3. Portrait thumbnails: face-centred square crops -> site/portraits/*.png (96px)
   for the MOVES panel tabs (the engine reads select portraits from the SFF,
   not from loose files, so these only show in the panel).
"""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

BASE = '/home/hatch/workspace/webmugen-build'
LITE = BASE + '/lite-incoming/mugen-build'
OUT = BASE + '/v5-assets'
random.seed(7)
np.random.seed(7)

# ---------------------------------------------------------------- home background
home = Image.open(LITE + '/site/data/mugen_home_screen_lite.png').convert('RGB')
W, H = home.size  # 1376 x 768
assert (W, H) == (1376, 768), (W, H)
arr = np.array(home).astype(np.float32)

# Slot rects (incl. orange border), measured from the image:
#   top border y 481-482, bottom border y 668-670, left/right borders from y=580 scan.
SLOTS = [(397, 481, 527, 669), (547, 481, 677, 669),
         (698, 481, 828, 669), (848, 481, 979, 669)]
PAD = 22  # paint over the border glow too (the orange border + halo reach ~15px
          # past the rect; PAD 8 + a 12px feather only diluted it, so the four
          # rounded rectangles stayed clearly visible on the title screen)
FEATHER = 4  # short feather: a long blend lets the bright border show through

def ring_median(x0, y0, x1, y1, band=14):
    """Median colour of the ring of pixels just outside a rect."""
    pts = []
    pts.append(arr[max(0, y0 - band):y0, x0:x1 + 1].reshape(-1, 3))
    pts.append(arr[y1 + 1:y1 + 1 + band, x0:x1 + 1].reshape(-1, 3))
    pts.append(arr[y0:y1 + 1, max(0, x0 - band):x0].reshape(-1, 3))
    pts.append(arr[y0:y1 + 1, x1 + 1:x1 + 1 + band].reshape(-1, 3))
    allp = np.concatenate([p for p in pts if len(p)])
    return np.median(allp, axis=0)

def remove_slots(img_arr):
    """Paint out the 4 baked slots by cloning dark rock from the right side.
    The v1 gradient fill read as flat empty boxes; real texture is needed.
    Source windows are dark rock (mean ~50-65, p90 < 110) at x 1010-1290."""
    a = img_arr.copy()
    # (slot rect, source window) - source is 146x204 to cover the PAD expansion
    jobs = [((397, 481, 527, 669), (1010, 477)),
            ((547, 481, 677, 669), (1140, 477)),
            ((698, 481, 828, 669), (1010, 481)),
            ((848, 481, 979, 669), (1140, 481))]
    for ((x0, y0, x1, y1), (sx, sy)) in jobs:
        X0, Y0, X1, Y1 = x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD
        w, h = X1 - X0 + 1, Y1 - Y0 + 1
        patch = a[sy:sy + h, sx:sx + w].copy()
        # the right-side rock is darker than the slot surroundings: lift it,
        # then break it up with noise + diagonal ember streaks like the rock
        # around the slots has
        patch = patch * 1.18
        patch = patch + np.random.normal(0, 8, patch.shape)
        tmp = Image.fromarray(np.clip(patch, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(tmp, 'RGBA')
        ember_cols = [(255, 150, 40), (255, 200, 80), (255, 120, 20)]
        for _ in range(10):
            ex, ey = random.randint(2, w - 3), random.randint(2, h - 3)
            r = random.randint(1, 2)
            d.ellipse([ex - r, ey - r, ex + r, ey + r],
                      fill=random.choice(ember_cols) + (random.randint(90, 180),))
        for _ in range(7):
            ex, ey = random.randint(5, w - 35), random.randint(5, h - 35)
            ln = random.randint(15, 40)
            ang = random.uniform(-0.9, 0.9)
            ex2, ey2 = ex + ln * math.cos(ang), ey + ln * math.sin(ang)
            d.line([ex, ey, ex2, ey2], fill=(255, 140, 30, random.randint(70, 140)), width=2)
        patch = np.array(tmp).astype(np.float32)
        # feather the rect edges (FEATHER px) into the original
        mask = np.ones((h, w), dtype=np.float32)
        f = FEATHER
        for i in range(f):
            v = (i + 1) / (f + 1)
            mask[i, :] *= v; mask[-1 - i, :] *= v
            mask[:, i] *= v; mask[:, -1 - i] *= v
        m3 = mask[:, :, None]
        a[Y0:Y1 + 1, X0:X1 + 1] = a[Y0:Y1 + 1, X0:X1 + 1] * (1 - m3) + patch * m3
    return a

clean = remove_slots(arr)
select_bg = Image.fromarray(np.clip(clean, 0, 255).astype(np.uint8))
select_bg = select_bg.resize((1280, 720), Image.LANCZOS)
select_bg.save(OUT + '/select-bg-lite.png', optimize=True)
print('select-bg-lite.png', select_bg.size)

# title version: CURSED CLASH centred in the flame frame (frame x 320-1080, y 37-~400)
title_bg = select_bg.copy()
d = ImageDraw.Draw(title_bg)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 96)
except Exception:
    font = ImageFont.load_default()
text = 'CURSED CLASH'
# gradient fill yellow -> orange, dark-red outline
bbox = d.textbbox((0, 0), text, font=font, stroke_width=7)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
cx, cy = 1280 // 2, 205  # frame centre in 1280x720 coords (700,218 scaled by .93)
grad = Image.new('RGB', (tw, th))
gd = ImageDraw.Draw(grad)
for y in range(th):
    t = y / max(1, th - 1)
    r = int(255 - (255 - 255) * t)
    g = int(210 - (210 - 122) * t)
    b = int(62 - (62 - 30) * t)
    gd.line([(0, y), (tw, y)], fill=(r, g, b))
mask = Image.new('L', (tw, th), 0)
md = ImageDraw.Draw(mask)
md.text((-bbox[0], -bbox[1]), text, font=font, fill=255, stroke_width=7, stroke_fill=255)
# outline: draw the mask slightly expanded in dark red behind the gradient text
outline = mask.filter(ImageFilter.MaxFilter(7))
title_bg.paste((90, 10, 0), (cx - tw // 2, cy - th // 2), outline)
title_bg.paste(grad, (cx - tw // 2, cy - th // 2), mask)
title_bg.save(OUT + '/title-bg-lite.png', optimize=True)
print('title-bg-lite.png', title_bg.size)

# ---------------------------------------------------------------- touch icons
def extract_icon(src, dst, thresh=70, erode=2, fill_holes=True):
    """Extract the neon graphic only. The tile PNGs are RGB with a CHECKERBOARD
    baked in, so the mask must be chroma-only (the glass/checkerboard is
    neutral grey, chroma ~0-15; the neon graphic is chroma 70+). Two traps:
    (1) the glass tile's orange border is also high-chroma and forms a closed
    outline - if it stays in the mask, the hole-fill treats the whole tile
    interior (checkerboard and all) as a hole. Keep ONLY the largest connected
    component (the graphic itself); the border is a separate thin component.
    (2) the charge bolt is a neon OUTLINE with a big soft halo: the halo's RGB
    is checkerboard-modulated, so it must be excluded entirely (high threshold,
    no hole-fill, light erosion) - only the bright outline survives.
    The soft edge only shows where there is real colour (chroma>25)."""
    from scipy import ndimage
    im = Image.open(src).convert('RGB')
    a = np.array(im).astype(np.float32)
    mx = a.max(axis=2); mn = a.min(axis=2)
    chroma = mx - mn
    core = chroma > thresh
    lab, n = ndimage.label(core)
    if n == 0:
        raise SystemExit('no icon found in ' + src)
    sizes = ndimage.sum_labels(np.ones_like(lab), lab, range(1, n + 1))
    keep = 1 + int(np.argmax(sizes))
    core = lab == keep
    filled = ndimage.binary_fill_holes(core) if fill_holes else core
    # Erode the silhouette before building alpha: the bolt's thin tip and
    # zigzag notches carry a pale glow-tinted checkerboard fringe that colour
    # tests cannot separate from real graphic (both are faint cyan). Erosion
    # drops that fringe; the thick graphics are unaffected.
    eroded = ndimage.binary_erosion(filled, iterations=erode)
    m = np.array(Image.fromarray((eroded * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(1))).astype(np.float32) / 255.0
    alpha = np.clip(m * (0.5 + 0.5 * np.clip(chroma / 100, 0, 1)), 0, 1)
    ys, xs = np.where(m > 0.08)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pad = 4
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(a.shape[1] - 1, x1 + pad), min(a.shape[0] - 1, y1 + pad)
    crop_rgb = a[y0:y1 + 1, x0:x1 + 1]
    crop_a = (alpha[y0:y1 + 1, x0:x1 + 1] * 255).astype(np.uint8)
    out = np.dstack([np.clip(crop_rgb, 0, 255).astype(np.uint8), crop_a])
    img = Image.fromarray(out, 'RGBA')
    img.thumbnail((128, 128), Image.LANCZOS)
    canvas = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    canvas.paste(img, ((128 - img.width) // 2, (128 - img.height) // 2))
    canvas.save(dst, optimize=True)
    print(dst.split('/')[-1], 'from box', (x0, y0, x1, y1), '->', canvas.size)

import os
os.makedirs(BASE + '/site/touch/icons', exist_ok=True)
os.makedirs(BASE + '/site/portraits', exist_ok=True)
extract_icon(LITE + '/site/touch/icon_punch.png', BASE + '/site/touch/icons/punch.png')
extract_icon(LITE + '/site/touch/icon_kick.png', BASE + '/site/touch/icons/kick.png')
# charge bolt: outline-only graphic - high threshold, no hole-fill, light erosion
extract_icon(LITE + '/site/touch/icon_charge.png', BASE + '/site/touch/icons/charge.png',
             thresh=110, erode=1, fill_holes=False)

# ---------------------------------------------------------------- portrait thumbnails
def thumb(src, dst, cx, cy, size):
    im = Image.open(src).convert('RGB')
    x0 = max(0, min(im.width - size, cx - size // 2))
    y0 = max(0, min(im.height - size, cy - size // 2))
    im.crop((x0, y0, x0 + size, y0 + size)).resize((96, 96), Image.LANCZOS).save(dst, optimize=True)
    print(dst.split('/')[-1], 'crop', (x0, y0, size))

thumb(LITE + '/site/chars/gojo/portrait_gojo.png', BASE + '/site/portraits/gojo.png', 690, 320, 700)
thumb(LITE + '/site/chars/sukuna/portrait_sukuna.png', BASE + '/site/portraits/sukuna.png', 384, 520, 640)
thumb(LITE + '/site/chars/meliodas/portrait_meliodas.png', BASE + '/site/portraits/meliodas.png', 448, 520, 640)
thumb(LITE + '/site/chars/escanor/portrait_escanor.png', BASE + '/site/portraits/escanor.png', 384, 480, 640)

# verification contact sheet: icons on the button dark colour, portraits row
sheet = Image.new('RGB', (128 * 3 + 96 * 4 + 40, 220), (24, 24, 24))
x = 10
for name in ('punch', 'kick', 'charge'):
    ic = Image.open(BASE + f'/site/touch/icons/{name}.png')
    sheet.paste(ic, (x, 10), ic)
    x += 128 + 10
for name in ('gojo', 'sukuna', 'meliodas', 'escanor'):
    th = Image.open(BASE + f'/site/portraits/{name}.png')
    sheet.paste(th, (x, 20))  # RGB, no mask
    x += 96 + 5
sheet.save('/tmp/v5-lite-contact.png')
print('contact sheet /tmp/v5-lite-contact.png')
import os as _os
for p in [OUT + '/title-bg-lite.png', OUT + '/select-bg-lite.png',
          BASE + '/site/touch/icons/punch.png', BASE + '/site/touch/icons/kick.png',
          BASE + '/site/touch/icons/charge.png', BASE + '/site/portraits/gojo.png',
          BASE + '/site/portraits/sukuna.png', BASE + '/site/portraits/meliodas.png',
          BASE + '/site/portraits/escanor.png']:
    print(p.split('webmugen-build/')[-1], _os.path.getsize(p), 'bytes')
