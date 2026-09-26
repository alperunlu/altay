# Writes packed.json into ../../index.html: CREEP_CELLS, CREEP_ATLAS, HERO_ATLAS, HERO_FOOT.
import json, os, re
here = os.path.dirname(os.path.abspath(__file__))
pk = json.load(open(os.path.join(here, 'packed.json')))
path = os.path.join(here, '..', '..', 'index.html')
s = open(path, encoding='utf8').read()
subs = [
    (r"const CREEP_CELLS = \{.*?\};", "const CREEP_CELLS = " + json.dumps(pk['cells']) + ";"),
    (r"const CREEP_ATLAS = 'data:image/webp;base64,[^']*';", "const CREEP_ATLAS = 'data:image/webp;base64," + pk['creep_b64'] + "';"),
    (r"const HERO_ATLAS = 'data:image/webp;base64,[^']*';", "const HERO_ATLAS = 'data:image/webp;base64," + pk['hero_b64'] + "';"),
    (r"const HERO_CELL = 112, HERO_FOOT = \d+;", "const HERO_CELL = 112, HERO_FOOT = %d;" % pk['hero_foot']),
]
for pat, rep in subs:
    s, n = re.subn(pat, lambda m: rep, s, count=1, flags=re.S)
    assert n == 1, pat
open(path, 'w', encoding='utf8', newline='\n').write(s)
print('index.html updated; now run: cd app && npm run sync-game')
