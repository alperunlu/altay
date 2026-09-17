#!/usr/bin/env python3
"""Assert strings present/absent in an `expo export` output.

Hermes stores any string containing a non-ASCII character as UTF-16, so a
plain byte search for such a string finds nothing and looks like proof of
absence. Every needle is therefore searched in BOTH encodings.
"""
import sys, pathlib, argparse

ap = argparse.ArgumentParser()
ap.add_argument('dir')
ap.add_argument('--require', action='append', default=[])
ap.add_argument('--forbid', action='append', default=[])
a = ap.parse_args()

root = pathlib.Path(a.dir)
files = [p for p in root.rglob('*') if p.is_file()]
blobs = {p: p.read_bytes() for p in files}
print(f'{len(files)} dosya, toplam {sum(len(b) for b in blobs.values())/1024/1024:.2f} MB')
for p in sorted(files, key=lambda x: -len(blobs[x]))[:6]:
    print(f'   {len(blobs[p])/1024:>9.0f} KB  {p.relative_to(root)}')

def found_in(needle):
    hits = []
    for p, b in blobs.items():
        if needle.encode('utf-8') in b or needle.encode('utf-16-le') in b:
            hits.append(str(p.relative_to(root)))
    return hits

bad = 0
print('\nBULUNMASI GEREKENLER')
for n in a.require:
    h = found_in(n)
    print(f'  {"OK  " if h else "EKSİK"} {n}' + (f'  -> {h[0]}' if h else ''))
    if not h: bad += 1
print('\nBULUNMAMASI GEREKENLER')
for n in a.forbid:
    h = found_in(n)
    print(f'  {"OK  " if not h else "VAR!"} {n}' + (f'  -> {h}' if h else ''))
    if h: bad += 1
print('\n' + ('GEÇTİ' if bad == 0 else f'{bad} SORUN'))
sys.exit(1 if bad else 0)
