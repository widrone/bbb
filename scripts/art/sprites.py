# Finds free-floating ink fragments in every print (connected components that don't touch the photo edge),
# turns each so its long axis lies flat, and saves candidates plus a numbered contact sheet.
import numpy as np, json, math
from PIL import Image, ImageDraw
from scipy import ndimage as nd
ART = '/home/claude/bbb/art/'
names = ['spikes','islands','bloom','figures','branches']
cands = []
for name in names:
    m0 = np.asarray(Image.open(ART + f'ink/{name}.png'), np.float32)/255
    for kind, m in (('ink', m0), ('paper', 1 - m0)):     # ink fragments, and paper shapes enclosed by ink
        H, W = m.shape
        solid = m > 0.5
        lab, n = nd.label(nd.binary_opening(solid, structure=np.ones((3,3)), iterations=4))   # cut thin threads
        for i, sl in enumerate(nd.find_objects(lab), 1):
            if sl is None: continue
            y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
            if y0 < 6 or x0 < 6 or y1 > H - 6 or x1 > W - 6: continue          # cut off by the photo edge
            h, w = y1 - y0, x1 - x0
            if max(h, w) < 70 or max(h, w) > 1100: continue
            mask = nd.binary_dilation(lab[y0:y1, x0:x1] == i, iterations=4) & solid[y0:y1, x0:x1]
            area = mask.sum(); fill = area/(h*w)
            if area < 1800 or fill > 0.72: continue
            per = (mask ^ nd.binary_erosion(mask)).sum(); spiky = per*per/area
            yy, xx = np.nonzero(mask); cy, cx = yy.mean(), xx.mean()
            ev, evec = np.linalg.eigh(np.cov(np.vstack([xx - cx, yy - cy])))
            ang = math.degrees(math.atan2(evec[1, 1], evec[0, 1])); elong = math.sqrt(ev[1]/max(ev[0], 1e-6))
            pad = 10
            crop = np.where(np.pad(mask, pad), np.pad(m[y0:y1, x0:x1], pad), 0)
            cands.append(dict(name=name, kind=kind, box=[int(x0), int(y0), int(w), int(h)], area=int(area), fill=round(float(fill), 3),
                              spiky=round(float(spiky), 1), ang=round(ang, 1), elong=round(elong, 2), crop=crop))
print(len(cands), 'candidates')
cands.sort(key=lambda c: -c['spiky']*min(c['area'], 40000)**0.3)
keep = cands[:72]
# contact sheet, 12 per row, each laid flat and fitted into 150 px
S = 150; cols = 12; rows = math.ceil(len(keep)/cols)
sheet = Image.new('RGB', (cols*S, rows*(S + 16)), (16, 19, 23)); d = ImageDraw.Draw(sheet)
for k, c in enumerate(keep):
    a = Image.fromarray((c['crop']*255).astype(np.uint8)).rotate(c['ang'], expand=True, resample=Image.BICUBIC)
    bb = a.getbbox(); a = a.crop(bb) if bb else a
    a.thumbnail((S - 12, S - 12)); tile = Image.new('RGBA', a.size, (231, 226, 215, 255)); tile.putalpha(a)
    x, y = (k % cols)*S, (k//cols)*(S + 16)
    sheet.paste(tile, (x + (S - a.width)//2, y + (S - a.height)//2), tile)
    d.text((x + 4, y + S), f"{k} {c['kind'][0]}{c['name'][:4]} e{c['elong']:.1f}", fill=(154, 164, 168))
    c['flat'] = a; c['idx'] = k
sheet.save(ART + 'prev/sprite-candidates.png')
np.save(ART + 'sprites/cands.npy', np.array([dict((k, v) for k, v in c.items() if k not in ('flat',)) for c in keep], dtype=object), allow_pickle=True)
