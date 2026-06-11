#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import math

F = "/tmp/nw/assets/fonts/norwester.ttf"

def arched(text, size, max_deg=7.5, depth=0.30, spacing=0.045):
    """Render arched text, return RGBA image (black ink). depth = fraction of size the ends drop."""
    font = ImageFont.truetype(F, size)
    tmp = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    widths = [tmp.textlength(ch, font=font) for ch in text]
    sp = size * spacing
    total = sum(widths) + sp * (len(text) - 1)
    drop = size * depth
    asc, desc = font.getmetrics()
    gh = asc + desc
    pad = int(size * 0.6)
    W, H = int(total + pad * 2), int(gh + drop + pad * 2)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    x = pad
    for i, ch in enumerate(text):
        w = widths[i]
        cxl = x + w / 2
        t = (cxl - W / 2) / (total / 2)
        ang = -t * max_deg
        yoff = drop * (t * t)
        tw, th = int(w) + 40, gh + 40
        tile = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((20, 20), ch, font=font, fill=(0, 0, 0, 255))
        tile = tile.rotate(ang, expand=True, resample=Image.BICUBIC)
        canvas.alpha_composite(tile, (int(cxl - tile.width / 2), int(pad + yoff + (gh - tile.height) / 2) + int(drop * 0.0)))
        x += w + sp
    return canvas.crop(canvas.getbbox())

def spaced_len(d, text, font, sp):
    return sum(d.textlength(ch, font=font) for ch in text) + sp * (len(text) - 1)

def draw_spaced(d, pos, text, font, sp, fill, anchor_y='mm'):
    x, y = pos
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill, anchor='l' + anchor_y[1])
        x += d.textlength(ch, font=font) + sp

def banner_knockout(width, height, spear, text, tsize, tspacing_frac):
    """Banner lozenge with spear points; text knocked out (transparent). Returns RGBA black-ink image."""
    W, H = width + 2 * spear, height
    mask = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(mask)
    x0, x1 = spear, spear + width
    ym = H / 2
    hh = height * 0.42
    bow = height * 0.13
    pts_top, pts_bot = [], []
    N = 60
    for i in range(N + 1):
        x = x0 + (x1 - x0) * i / N
        t = (x - W / 2) / (width / 2)
        pts_top.append((x, ym - hh - bow * (1 - t * t)))
        pts_bot.append((x, ym + hh + bow * (1 - t * t)))
    d.polygon(pts_top + pts_bot[::-1], fill=255)
    th = height * 0.10
    d.polygon([(x0 + 2, ym - th), (0, ym), (x0 + 2, ym + th)], fill=255)
    d.polygon([(x1 - 2, ym - th), (W, ym), (x1 - 2, ym + th)], fill=255)
    # knock out the text
    font = ImageFont.truetype(F, tsize)
    sp = tsize * tspacing_frac
    tw = spaced_len(d, text, font, sp)
    draw_spaced(d, (W / 2 - tw / 2, ym + bow * 0.1), text, font, sp, 0)
    ink = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    ink.putalpha(mask)
    return ink

def compose(parts, W, H, gap_overrides=None):
    """Stack centered parts vertically with given y positions [(img, y_center)] onto transparent canvas."""
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for img, ycen in parts:
        canvas.alpha_composite(img, (int(W / 2 - img.width / 2), int(ycen - img.height / 2)))
    return canvas

def tint(img, color):
    """Recolor black-ink RGBA image to color, preserving alpha."""
    out = Image.new('RGBA', img.size, color + (255,))
    out.putalpha(img.getchannel('A'))
    return out

# ---------- logo.png (1100x264): CLEAN PLATE + banner ----------
cp = arched("CLEAN PLATE", 168)
cp.thumbnail((1080, 10000), Image.LANCZOS)
ban = banner_knockout(int(cp.width * 0.62), 86, int(cp.width * 0.19), "HAULING CO.", 46, 0.45)
logo = compose([(cp, 102), (ban, 218)], 1100, 264)
logo.save('logo_new.png')

# ---------- logo-full.png (1200x419): + subline + phone ----------
cp2 = arched("CLEAN PLATE", 190)
cp2.thumbnail((1140, 10000), Image.LANCZOS)
ban2 = banner_knockout(int(cp2.width * 0.62), 96, int(cp2.width * 0.19), "HAULING CO.", 52, 0.45)
# subline with manual bullet
sub_f = ImageFont.truetype(F, 44)
tmpd = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
sub_sp = 44 * 0.10
t1, t2 = "JUNK REMOVAL", "CLEANOUTS"
w1 = spaced_len(tmpd, t1, sub_f, sub_sp); w2 = spaced_len(tmpd, t2, sub_f, sub_sp)
dotgap = 38
subW = int(w1 + dotgap * 2 + 10 + w2) + 8
sub = Image.new('RGBA', (subW, 64), (0, 0, 0, 0))
sd = ImageDraw.Draw(sub)
draw_spaced(sd, (2, 32), t1, sub_f, sub_sp, (0, 0, 0, 255))
sd.ellipse([w1 + dotgap - 7, 32 - 7, w1 + dotgap + 7, 32 + 7], fill=(0, 0, 0, 255))
draw_spaced(sd, (w1 + dotgap * 2 + 10, 32), t2, sub_f, sub_sp, (0, 0, 0, 255))
sub = sub.crop(sub.getbbox())
phone_f = ImageFont.truetype(F, 74)
ph = Image.new('RGBA', (900, 130), (0, 0, 0, 0))
pd = ImageDraw.Draw(ph)
pw = spaced_len(pd, "734-743-1877", phone_f, 74 * 0.04)
draw_spaced(pd, ((900 - pw) / 2, 65), "734-743-1877", phone_f, 74 * 0.04, (0, 0, 0, 255))
ph = ph.crop(ph.getbbox())
full = compose([(cp2, 102), (ban2, 240), (sub, 314), (ph, 374)], 1200, 419)
full.save('logo-full_new.png')

# ---------- og.png (1200x630): white lockup on brand green + tagline + strip ----------
BG, STRIP, TAG = (7, 24, 16), (29, 99, 64), (74, 171, 116)
og = Image.new('RGB', (1200, 630), BG)
cp3 = arched("CLEAN PLATE", 130)
cp3.thumbnail((700, 10000), Image.LANCZOS)
ban3 = banner_knockout(int(cp3.width * 0.64), 64, int(cp3.width * 0.20), "HAULING CO.", 34, 0.45)
sub3_f = ImageFont.truetype(F, 30)
sp3 = 30 * 0.10
w1b = spaced_len(tmpd, t1, sub3_f, sp3); w2b = spaced_len(tmpd, t2, sub3_f, sp3)
sub3 = Image.new('RGBA', (int(w1b + 60 + w2b) + 8, 44), (0, 0, 0, 0))
s3 = ImageDraw.Draw(sub3)
draw_spaced(s3, (2, 22), t1, sub3_f, sp3, (0, 0, 0, 255))
s3.ellipse([w1b + 26 - 5, 22 - 5, w1b + 26 + 5, 22 + 5], fill=(0, 0, 0, 255))
draw_spaced(s3, (w1b + 56, 22), t2, sub3_f, sp3, (0, 0, 0, 255))
sub3 = sub3.crop(sub3.getbbox())
ph3_f = ImageFont.truetype(F, 56)
ph3 = Image.new('RGBA', (700, 90), (0, 0, 0, 0))
p3 = ImageDraw.Draw(ph3)
pw3 = spaced_len(p3, "734-743-1877", ph3_f, 56 * 0.04)
draw_spaced(p3, ((700 - pw3) / 2, 45), "734-743-1877", ph3_f, 56 * 0.04, (0, 0, 0, 255))
ph3 = ph3.crop(ph3.getbbox())
lock = compose([(cp3, 90), (ban3, 196), (sub3, 252), (ph3, 302)], 1200, 360)
og.paste((255, 255, 255), (0, 95, 1200, 95 + 360), tint(lock, (255, 255, 255)).getchannel('A'))
# tagline
tag_f = ImageFont.truetype(F, 40)
tag_sp = 40 * 0.14
tg1, tg2 = "VETERAN-OWNED", "WIXOM & METRO DETROIT"
d_og = ImageDraw.Draw(og)
wt1 = spaced_len(d_og, tg1, tag_f, tag_sp); wt2 = spaced_len(d_og, tg2, tag_f, tag_sp)
gap = 70
startx = 600 - (wt1 + gap + wt2) / 2
draw_spaced(d_og, (startx, 512), tg1, tag_f, tag_sp, TAG)
d_og.ellipse([startx + wt1 + gap / 2 - 5, 512 - 5, startx + wt1 + gap / 2 + 5, 512 + 5], fill=TAG)
draw_spaced(d_og, (startx + wt1 + gap, 512), tg2, tag_f, tag_sp, TAG)
d_og.rectangle([0, 602, 1200, 630], fill=STRIP)
og.save('og_new.png')

print("logo_new:", logo.size, "logo-full_new:", full.size, "og_new:", og.size)
