# Packs the chosen fragments into one sprite sheet (white + alpha; tinted in the game) and writes its manifest.
import numpy as np, json
from PIL import Image
c = np.load('sprites/cands.npy', allow_pickle=True)
GROUPS = {   # contact-sheet numbers → role, and the size each is normalised to (longest side, px)
  'hit':    ([7, 11, 15, 17, 18, 25, 29, 31, 35, 37], 200),
  'head':   ([4], 260),
  'spark':  ([1, 3, 12, 13, 20, 22, 26, 34, 36, 8, 5, 6], 96),
  'drift':  ([0, 16, 23, 27, 32, 2, 19, 14, 30, 9], 340),
}
tiles = []
for role, (ids, size) in GROUPS.items():
    for k in ids:
        e = c[k]
        a = Image.fromarray((e['crop']*255).astype(np.uint8)).rotate(e['ang'], expand=True, resample=Image.BICUBIC)
        a = a.crop(a.getbbox())
        if role == 'head' and a.height > a.width: a = a.rotate(90, expand=True)
        sc = size/max(a.size); a = a.resize((max(1, round(a.width*sc)), max(1, round(a.height*sc))), Image.LANCZOS)
        tiles.append((role, k, e['name'], e['kind'], a))
# shelf packing, tallest first
W = 1024; tiles.sort(key=lambda t: -t[4].height)
x = y = shelf = 0; pad = 3; frames = []
for role, k, name, kind, a in tiles:
    if x + a.width + pad > W: x = 0; y += shelf + pad; shelf = 0
    frames.append({'role':role, 'src':f'{kind}:{name}#{k}', 'x':x, 'y':y, 'w':a.width, 'h':a.height, 'img':a})
    x += a.width + pad; shelf = max(shelf, a.height)
H = y + shelf
sheet = Image.new('L', (W, H), 0)
for f in frames: sheet.paste(f.pop('img'), (f['x'], f['y']))
rgba = Image.merge('RGBA', [Image.new('L', (W, H), 255)]*3 + [sheet])
rgba.save('/home/claude/bbb/web/art/sprites.webp', quality=88, method=6)
json.dump({'w':W, 'h':H, 'frames':frames}, open('/home/claude/bbb/web/art/sprites.json', 'w'), separators=(',', ':'))
from collections import Counter
print(W, 'x', H, dict(Counter(f['role'] for f in frames)))
prev = Image.new('RGBA', (W, H), (16, 19, 23, 255)); t = Image.new('RGBA', (W, H), (231, 226, 215, 255)); t.putalpha(sheet); prev.alpha_composite(t); prev.convert('RGB').save('prev/atlas.png')
