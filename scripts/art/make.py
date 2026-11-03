import numpy as np, json, math, random
from PIL import Image, ImageOps, ImageFilter
from scipy import ndimage as nd
ART = '/home/claude/bbb/art/'; OUT = '/home/claude/bbb/web/art/'
hexc = lambda h: np.array([int(h[i:i+2], 16) for i in (1,3,5)], np.float32)
CONCRETE, SLAB, CHALK, AMBER, STEEL = map(hexc, ['#101317', '#181d22', '#e7e2d7', '#f2a93b', '#7db3bb'])
masks = {n: np.asarray(Image.open(ART + f'ink/{n}.png'), np.float32)/255 for n in ['spikes','islands','bloom','figures']}
rng = np.random.default_rng(7)
def grain(h, w, amt): return (rng.standard_normal((h, w, 1))*amt).astype(np.float32)

# ---- 1. title plate: the cover photo turned so its type reads level, graded to the game's palette
cov = ImageOps.exif_transpose(Image.open(ART + 'src/PXL_20261103_215029108.jpg')).convert('L')
cov = cov.resize((2000, 1500), Image.LANCZOS).rotate(-35.5, resample=Image.BICUBIC, expand=True, fillcolor=0)
cx, cy = cov.width//2, cov.height//2
cov = cov.crop((cx - 980, cy - 250, cx + 980, cy + 410))
g = np.asarray(cov, np.float32)/255
g = np.clip((g - 0.18)/(0.92 - 0.18), 0, 1)**1.15
# duotone: shadows in concrete, highlights in chalk, a warm lift in the upper mids
col = CONCRETE[None,None]*(1-g[...,None]) + CHALK[None,None]*g[...,None]
col += (AMBER - CHALK)[None,None]*(0.18*np.exp(-((g-0.6)/0.18)**2))[...,None]
h, w = g.shape
x = np.linspace(0, 1, w)[None,:,None]; y = np.linspace(0, 1, h)[:,None,None]
fade = np.clip((x - 0.04)/0.42, 0, 1)**1.4 * np.clip(1 - (np.abs(y - 0.5)*2)**3, 0, 1)   # fade into the page on the left and edges
col = CONCRETE[None,None]*(1-fade) + col*fade + grain(h, w, 6)
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save(OUT + 'cover-plate.webp', quality=82)

# ---- 2. track sleeves: a crop of one print, lit like the photos (warm lamp to cool shadow), ink in concrete
order = ['spikes','islands','bloom','figures']
sleeves = []
for slot in range(16):            # 0 = Basement Test, 1..15 album
    name = order[slot % 4]; m = masks[name]; H, W = m.shape
    for _ in range(60):
        s = int(rng.uniform(620, 1150)); x0 = int(rng.uniform(0, W - s)); y0 = int(rng.uniform(0, H - s))
        c = m[y0:y0+s, x0:x0+s]; cov_ = (c > 0.5).mean()
        if 0.38 <= cov_ <= 0.62 and c.std() > 0.38: break
    rot = int(rng.integers(0, 4))
    c = np.rot90(c, rot)
    c = np.asarray(Image.fromarray((c*255).astype(np.uint8)).resize((640, 640), Image.LANCZOS), np.float32)/255
    ang = rng.uniform(0, 2*math.pi); yy, xx = np.mgrid[0:640, 0:640]/639.0
    u = np.clip(0.5 + (np.cos(ang)*(xx-0.5) + np.sin(ang)*(yy-0.5))*1.2, 0, 1)[...,None]
    paper = AMBER*0.55 + CHALK*0.45
    paper = paper[None,None]*(1-u) + (STEEL*0.7 + SLAB*0.3)[None,None]*u                # warm lamp side → cool side
    vign = 1 - 0.35*np.clip(np.hypot(xx-0.5, yy-0.5)*1.5, 0, 1)[...,None]**2
    img = paper*vign*(1 - c[...,None]) + (CONCRETE + 6)[None,None]*c[...,None] + grain(640, 640, 7)
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS).save(OUT + f'sleeve-{slot:02d}.webp', quality=80)
    sleeves.append({'slot':slot, 'print':name, 'box':[x0, y0, s], 'rot':rot})

# ---- 3. play backdrops: ink as alpha, light where the paper was (drawn inverted and tinted in the game)
for name, m in masks.items():
    a = np.asarray(Image.fromarray(((1 - m)*255).astype(np.uint8)).resize((900, 1200), Image.LANCZOS))
    rgba = np.dstack([np.full_like(a, 255)]*3 + [a])
    Image.fromarray(rgba, 'RGBA').save(OUT + f'paper-{name}.webp', quality=70)

# ---- 4. hit splats: spiky ink fragments from the "spikes" print, isolated by connected component
m = masks['spikes']; lab, n = nd.label(m > 0.5); sizes = nd.sum(np.ones_like(m), lab, range(1, n+1))
cands = [i+1 for i in np.argsort(-sizes) if 4000 < sizes[i] < 90000][:40]
picked = 0
for li in cands:
    sl = nd.find_objects((lab == li).astype(int))[0]; hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if min(hh, ww) < 60 or max(hh, ww)/min(hh, ww) > 3.2: continue
    pad = 12; y0, y1 = max(0, sl[0].start - pad), sl[0].stop + pad; x0, x1 = max(0, sl[1].start - pad), sl[1].stop + pad
    frag = np.where(lab[y0:y1, x0:x1] == li, m[y0:y1, x0:x1], 0)
    S = max(frag.shape); sq = np.zeros((S, S), np.float32); oy, ox = (S - frag.shape[0])//2, (S - frag.shape[1])//2; sq[oy:oy+frag.shape[0], ox:ox+frag.shape[1]] = frag
    a = np.asarray(Image.fromarray((sq*255).astype(np.uint8)).resize((192, 192), Image.LANCZOS))
    Image.fromarray(np.dstack([np.full_like(a, 255)]*3 + [a]), 'RGBA').save(OUT + f'splat-{picked}.webp', quality=85)
    picked += 1
    if picked == 6: break

# ---- 5. halftone texture from the dotted area of the "islands" print
ht = masks['islands'][90:602, 150:662]
a = (ht*255).astype(np.uint8)
Image.fromarray(np.dstack([np.full_like(a, 255)]*3 + [a]), 'RGBA').resize((256, 256), Image.LANCZOS).save(OUT + 'halftone.webp', quality=85)

json.dump({'sleeves':sleeves, 'splats':picked}, open(ART + 'manifest.json', 'w'), indent=1)
print('splats', picked)
