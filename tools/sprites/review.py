import sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
KEYS = ['kobold','ghoul','grunt','harpy','gargoyle','ogre','wraith','khan','wyrm','titan','basci','umay','yelbegen','yelbegenYavru']
CELL = dict(kobold=68,ghoul=74,grunt=80,harpy=92,gargoyle=100,ogre=100,wraith=84,khan=126,wyrm=146,titan=144,basci=78,umay=76,yelbegen=118,yelbegenYavru=62)
Z = float(sys.argv[1]) if len(sys.argv) > 1 else 1.25
def outline(im, w=1):
    a = im.split()[3]
    dil = a.filter(ImageFilter.MaxFilter(3))
    sil = Image.new('RGBA', im.size, (6, 4, 9, 255)); sil.putalpha(dil.point(lambda v: int(v * 0.85)))
    sil.alpha_composite(im); return sil
rows = []
for k in KEYS:
    c = CELL[k]; sh = Image.open(f'sheets/{k}.png').convert('RGBA')
    cells = [sh.crop((0, d * c, c, d * c + c)) for d in range(5)] + [sh.crop((f * c, 2 * c, f * c + c, 3 * c)) for f in range(4)]
    row = Image.new('RGBA', (c * 9 + 8 * 4, c), (74, 104, 58, 255))
    for i, cc in enumerate(cells): row.alpha_composite(outline(cc), (i * (c + 4), 0))
    rows.append((k, row.resize((int(row.width * Z), int(row.height * Z)), Image.LANCZOS)))
W = max(r.width for _, r in rows) + 110; H = sum(r.height + 6 for _, r in rows)
out = Image.new('RGB', (W, H), (24, 22, 26)); dr = ImageDraw.Draw(out); y = 0
for k, r in rows:
    dr.text((6, y + 6), k, fill=(255, 220, 150)); out.paste(r.convert('RGB'), (110, y)); y += r.height + 6
out.save('review.png'); print(out.size)
