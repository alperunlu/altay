# Packs sheets/*.png into the two WebP atlases and the cell table -> packed.json
import json, base64, io, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, features
assert features.check('webp'), 'no webp'
KEYS = ['kobold','ghoul','grunt','harpy','gargoyle','ogre','wraith','khan','wyrm','titan','basci','umay','yelbegen','yelbegenYavru']
CELL = dict(kobold=68,ghoul=74,grunt=80,harpy=92,gargoyle=100,ogre=100,wraith=84,khan=126,wyrm=146,titan=144,basci=78,umay=76,yelbegen=118,yelbegenYavru=62)
fits = json.load(open('sheets/fits.json'))
W = 4 * max(CELL.values())
blocks, cells, y = [], {}, 0
for k in KEYS:
    c = CELL[k]; sh = Image.open(f'sheets/{k}.png').convert('RGBA')
    assert sh.size == (4 * c, 5 * c), (k, sh.size)
    a = np.array(sh)[..., 3]; ys, xs = np.nonzero(a > 24)
    # topmost opaque row over every direction and frame, as a fraction of the cell
    # east (row 2) is what is on screen nearly all the time; the health bar sits above that
    top = np.nonzero(np.array(sh.crop((0, 2 * c, 4 * c, 3 * c)))[..., 3].max(axis=1) > 24)[0].min() / c
    cells[k] = [y, c, fits[k][1], round(float(top), 3)]
    blocks.append((y, sh)); y += 5 * c
atlas = Image.new('RGBA', (W, y), (0, 0, 0, 0))
for yy, sh in blocks: atlas.paste(sh, (0, yy))
def webp_b64(im, q):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6, alpha_quality=90); return base64.b64encode(b.getvalue()).decode(), len(b.getvalue())
cre_b64, cre_n = webp_b64(atlas, 86)
hero = Image.open('sheets/hero.png').convert('RGBA'); assert hero.size == (12 * 112, 5 * 112), hero.size
hero_b64, hero_n = webp_b64(hero, 88)
json.dump({'cells': cells, 'creep_b64': cre_b64, 'hero_b64': hero_b64, 'hero_foot': round(fits['hero'][1] * 112)}, open('packed.json', 'w'))
print('creep atlas', atlas.size, cre_n // 1024, 'KB; hero', hero.size, hero_n // 1024, 'KB')
print(json.dumps(cells))
