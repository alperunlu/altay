#!/usr/bin/env node
/* The game is one self-contained file and it lives at the repository root,
   where GitHub Pages serves it. Metro bundles from inside app/, so it cannot
   reach up past its own project root -- the file is copied in instead of
   symlinked, because Metro does not follow symlinks reliably.
   Root stays the single source of truth; this runs before start and build. */
const fs = require('fs'), path = require('path');
const src = path.join(__dirname, '..', '..', 'index.html');
const dst = path.join(__dirname, '..', 'assets', 'game', 'index.html');
const html = fs.readFileSync(src, 'utf8');

// Guard the two things that must hold for the wrapped build: no remote code,
// no remote fonts. Fail the sync loudly rather than shipping a binary that
// review would reject (or that would simply not work offline).
const remote = [...html.matchAll(/<(?:script|link)[^>]+(?:src|href)\s*=\s*["'](https?:\/\/[^"']+)/gi)].map(m => m[1]);
if (remote.length) {
  console.error('sync-game: index.html still loads remote resources:\n  ' + remote.join('\n  '));
  process.exit(1);
}
fs.mkdirSync(path.dirname(dst), { recursive: true });
fs.writeFileSync(dst, html);
console.log(`sync-game: ${(html.length / 1024).toFixed(0)} KB -> assets/game/index.html`);
