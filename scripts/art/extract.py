import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as nd
SRC = '/home/claude/bbb/art/src/'
inks = {'spikes':'PXL_20261103_215220638', 'islands':'PXL_20261103_215237826', 'bloom':'PXL_20261103_215245608', 'figures':'PXL_20261103_215309356'}
for name, f in inks.items():
    im = ImageOps.exif_transpose(Image.open(SRC + f + '.jpg')).convert('RGB')
    im = im.resize((im.width//2, im.height//2), Image.LANCZOS)          # 1500 x 2000 keeps the halftone dots
    g = np.asarray(im.convert('L'), dtype=np.float32)/255
    # paper estimate: local maximum over a window wider than the biggest ink blob, on a small copy, then smoothed
    small = g[::4, ::4]
    paper = nd.maximum_filter(small, size=121)
    paper = nd.gaussian_filter(paper, 18)
    paper = np.asarray(Image.fromarray(paper).resize(im.size, Image.BICUBIC))
    norm = np.clip(g/np.maximum(paper, 0.05), 0, 1.2)
    a = np.clip((0.66 - norm)/(0.66 - 0.40), 0, 1)
    if name == 'figures': a[:, int(a.shape[1]*0.80):] = 0     # dark table edge at the right, not part of the print
    a = (a*255).astype(np.uint8)
    Image.fromarray(a).save(f'/home/claude/bbb/art/ink/{name}.png')
    prev = Image.fromarray(255 - a); prev.thumbnail((600, 800)); prev.save(f'/home/claude/bbb/art/prev/ink-{name}.png')
    print(name, im.size, 'ink coverage', round((a > 128).mean(), 3))
