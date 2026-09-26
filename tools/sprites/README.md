# Creature and hero sprites

Every enemy and the hero are built as simple models in Blender from code,
cel-shaded, and rendered from five facings into the atlases baked into
`index.html` (`CREEP_ATLAS`, `HERO_ATLAS`). The westward three facings are
mirrors, made at bake time in the game.

| file | what it is |
|---|---|
| `kit.py` | scene, camera, cel material, skin-modifier humanoid, wings, autofit, sheet renderer |
| `creatures.py` | one builder per enemy (`CREATURES`), palettes from `CREEPS` in index.html |
| `hero.py` | Alp: 8 walk frames + 4 axe-swing frames |
| `run.py` | Blender driver: renders sheets or previews |
| `pack.py` | sheets → two WebP atlases + the `CREEP_CELLS` table (`packed.json`) |
| `apply.py` | writes `packed.json` into `index.html` |
| `review.py` | all creatures at game scale on grass, for eyeballing (`review.png`) |

## Re-rendering

In Blender (Text editor, Python console, or the Blender MCP), with `D` set to
this folder:

```python
D = r"E:\dev\altay\tools\sprites"
KEYS = ['kobold', 'ogre', 'hero']      # any of CREATURES, or 'hero'
MODE = 'sheet'                          # or 'preview' for three big angles
exec(open(D + '/run.py', encoding='utf8').read())
```

Everything is built in its own `AltaySprites` scene. A creature takes 10–20 s;
keep batches to a few keys so a single call stays short.

Then, from this folder:

```bash
python pack.py
python apply.py
cd ../../app && npm run sync-game
```

## Things that are easy to get wrong

- Each creature's scale and ground line are solved per render (`autofit`) so
  the figure fills its cell in every facing and frame. `CREEP_CELLS` carries
  that foot line and the sprite's top, and the game anchors the sprite and the
  health bar from them. A long weapon held forward shrinks the whole creature,
  because it has to fit too.
- `MAX_PPM` in `creatures.py` caps creatures whose cell is roomier than they
  should look.
- Colours given to `toon()` are sRGB; it converts them to linear itself.
