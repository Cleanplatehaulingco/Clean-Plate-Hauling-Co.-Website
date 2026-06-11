#!/usr/bin/env python3
"""Clean Plate Hauling Co. logo generator — Norwester, supersampled."""
from PIL import Image, ImageDraw, ImageFont

F = "/tmp/nw/assets/fonts/norwester.ttf"
INK = (0, 0, 0, 255)

def arched(text, size, max_deg=7.5, depth=0.30, spacing=0.045):
    font = ImageFont.truetype(F, int(size))
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
        tile = Image.new('RGBA', (int(w) + 80, gh + 80), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((40, 40), ch, font=font, fill=INK)
        tile = tile.rotate(ang, expand=True, resample=Image.BICUBIC)
        canvas.alpha_composite(tile, (int(cxl - tile.width / 2), int(pad + yoff + (gh - tile.height) / 2)))
        x += w + sp
    return canvas.crop(canvas.getbbox())

def spaced_len(d, text, font, sp):
    return sum(d.textlength(ch, font=font) for ch in text) + sp * (len(text) - 1)

def draw_spaced(d, pos, text, font, sp, fill):
    x, y = pos
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill, anchor='lm')
        x += d.textlength(ch, font=font) + sp

def qbez(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])
            for t in (i / n for i in range(n + 1))]

def banner_knockout(width, height, spear, text, tsize, tspacing_frac):
    """Banner lozenge with curved blade spears; text knocked out."""
    W, H = int(width + 2 * spear), int(height * 1.3)
    mask = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(mask)
    x0, x1 = spear, spear + width
    ym = H / 2
    hh = height * 0.42
    bow = height * 0.13
    pts_top, pts_bot = [], []
    N = 80
    for i in range(N + 1):
        x = x0 + (x1 - x0) * i / N
        t = (x - W / 2) / (width / 2)
        pts_top.append((x, ym - hh - bow * (1 - t * t)))
        pts_bot.append((x, ym + hh + bow * (1 - t * t)))
    d.polygon(pts_top + pts_bot[::-1], fill=255)
    # curved blade spears: tapered, slightly concave edges, sharp tip
    th = height * 0.155
    ins = width * 0.012
    left = (qbez((x0 + ins, ym - th), (x0 - spear * 0.52, ym - th * 0.42), (x0 - spear + 2, ym))
            + qbez((x0 - spear + 2, ym), (x0 - spear * 0.52, ym + th * 0.42), (x0 + ins, ym + th)))
    d.polygon(left, fill=255)
    right = (qbez((x1 - ins, ym - th), (x1 + spear * 0.52, ym - th * 0.42), (x1 + spear - 2, ym))
             + qbez((x1 + spear - 2, ym), (x1 + spear * 0.52, ym + th * 0.42), (x1 - ins, ym + th)))
    d.polygon(right, fill=255)
    font = ImageFont.truetype(F, int(tsize))
    sp = tsize * tspacing_frac
    tw = spaced_len(d, text, font, sp)
    draw_spaced(d, (W / 2 - tw / 2, ym + bow * 0.1), text, font, sp, 0)
    ink = Image.new('RGBA', (W, H), INK)
    ink.putalpha(mask)
    return ink

def compose(parts, W, H):
    canvas = Image.new('RGBA', (int(W), int(H)), (0, 0, 0, 0))
    for img, ycen in parts:
        canvas.alpha_composite(img, (int(W / 2 - img.width / 2), int(ycen - img.height / 2)))
    return canvas

def subline(size, gapdot):
    f = ImageFont.truetype(F, int(size))
    tmp = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    sp = size * 0.10
    t1, t2 = "JUNK REMOVAL", "CLEANOUTS"
    w1, w2 = spaced_len(tmp, t1, f, sp), spaced_len(tmp, t2, f, sp)
    W = int(w1 + gapdot * 2 + 10 + w2) + 8
    H = int(size * 1.5)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.16
    draw_spaced(d, (2, H / 2), t1, f, sp, INK)
    d.ellipse([w1 + gapdot - r, H / 2 - r, w1 + gapdot + r, H / 2 + r], fill=INK)
    draw_spaced(d, (w1 + gapdot * 2 + 10, H / 2), t2, f, sp, INK)
    return img.crop(img.getbbox())

def phone_img(size):
    f = ImageFont.truetype(F, int(size))
    img = Image.new('RGBA', (int(size * 10), int(size * 1.6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sp = size * 0.04
    w = spaced_len(d, "734-743-1877", f, sp)
    draw_spaced(d, ((img.width - w) / 2, img.height / 2), "734-743-1877", f, sp, INK)
    return img.crop(img.getbbox())

def tint(img, color):
    out = Image.new('RGBA', img.size, color + (255,))
    out.putalpha(img.getchannel('A'))
    return out

def build_logo(K):
    cp = arched("CLEAN PLATE", 168 * K)
    cp.thumbnail((int(1080 * K), 10 ** 6), Image.LANCZOS)
    ban = banner_knockout(cp.width * 0.62, 86 * K, cp.width * 0.19, "HAULING CO.", 46 * K, 0.45)
    return compose([(cp, 102 * K), (ban, 218 * K)], 1100 * K, 264 * K)

def build_full(K):
    cp = arched("CLEAN PLATE", 190 * K)
    cp.thumbnail((int(1140 * K), 10 ** 6), Image.LANCZOS)
    ban = banner_knockout(cp.width * 0.62, 96 * K, cp.width * 0.19, "HAULING CO.", 52 * K, 0.45)
    sub = subline(44 * K, 38 * K)
    ph = phone_img(74 * K)
    return compose([(cp, 102 * K), (ban, 240 * K), (sub, 314 * K), (ph, 374 * K)], 1200 * K, 419 * K)

def build_og(K):
    BGC, STRIP, TAG = (7, 24, 16), (29, 99, 64), (74, 171, 116)
    og = Image.new('RGB', (int(1200 * K), int(630 * K)), BGC)
    cp = arched("CLEAN PLATE", 130 * K)
    cp.thumbnail((int(700 * K), 10 ** 6), Image.LANCZOS)
    ban = banner_knockout(cp.width * 0.64, 64 * K, cp.width * 0.20, "HAULING CO.", 34 * K, 0.45)
    sub = subline(30 * K, 26 * K)
    ph = phone_img(56 * K)
    lock = compose([(cp, 90 * K), (ban, 196 * K), (sub, 252 * K), (ph, 302 * K)], 1200 * K, 360 * K)
    og.paste((255, 255, 255), (0, int(95 * K), int(1200 * K), int(95 * K) + lock.height), lock.getchannel('A'))
    d = ImageDraw.Draw(og)
    tf = ImageFont.truetype(F, int(40 * K))
    tsp = 40 * K * 0.14
    tg1, tg2 = "VETERAN-OWNED", "WIXOM & METRO DETROIT"
    w1, w2 = spaced_len(d, tg1, tf, tsp), spaced_len(d, tg2, tf, tsp)
    gap = 70 * K
    sx = 600 * K - (w1 + gap + w2) / 2
    r = 5 * K
    draw_spaced(d, (sx, 512 * K), tg1, tf, tsp, TAG)
    d.ellipse([sx + w1 + gap / 2 - r, 512 * K - r, sx + w1 + gap / 2 + r, 512 * K + r], fill=TAG)
    draw_spaced(d, (sx + w1 + gap, 512 * K), tg2, tf, tsp, TAG)
    d.rectangle([0, 602 * K, 1200 * K, 630 * K], fill=STRIP)
    return og

import os
os.makedirs('print', exist_ok=True)

m_logo = build_logo(6.98)            # 7678 px wide master
m_logo.save('print/logo-8k.png')
m_logo.resize((2200, 528), Image.LANCZOS).save('logo_new.png')

m_full = build_full(6.4)             # 7680 px wide master
m_full.save('print/logo-full-8k.png')
m_full.resize((2400, 838), Image.LANCZOS).save('logo-full_new.png')

build_og(4).resize((1200, 630), Image.LANCZOS).save('og_new.png')

print("masters:", m_logo.size, m_full.size, "| web: 2200x528, 2400x838, og 1200x630")
