# Blender driver. Run inside Blender (Text editor, Python console or MCP) with:
#   D = r"<repo>/tools/sprites"; KEYS = ['kobold', ...] or ['hero']; MODE = 'sheet' | 'preview'
#   exec(open(D + '/run.py', encoding='utf8').read())
# Renders into D/sheets (sheets) or D/prev (previews). Everything is built in a
# separate 'AltaySprites' scene, so the open file's own scenes are not touched.
import bpy, os, math, json
g = {'FIT_TMP': os.path.join(D, '_fit.png')}
exec(open(os.path.join(D, 'kit.py'), encoding='utf8').read(), g)
exec(open(os.path.join(D, 'creatures.py'), encoding='utf8').read(), g)
exec(open(os.path.join(D, 'hero.py'), encoding='utf8').read(), g)
os.makedirs(os.path.join(D, 'sheets'), exist_ok=True); os.makedirs(os.path.join(D, 'prev'), exist_ok=True)
done = {}
fits_path = os.path.join(D, 'sheets', 'fits.json')
fits = json.load(open(fits_path)) if os.path.exists(fits_path) else {}
FIT = dict(probe_dirs=(0, 1, 2, 3, 4), margin_top=0.02, margin_side=0.02, margin_bottom=0.02)
for key in KEYS:
    sc = g['scene'](); g['clear_scene'](sc)
    cam = g['rig_camera_and_sun'](sc)
    if key == 'hero':
        root, anim, lift = g['hero'](sc); cell, frames = 112, 12
    else:
        build, cell = g['CREATURES'][key]; frames = 4
        root, anim, lift = build(sc)
    if MODE == 'preview':
        g['preview'](sc, cam, root, cell, anim, os.path.join(D, 'prev', key), size=360)
        done[key] = 1; continue
    # the largest scale, and the foot line, at which every facing and frame fits the cell
    ppm, foot = g['autofit'](sc, cam, root, cell, anim, lift, frames=frames, **FIT)
    ppm = min(ppm, g['MAX_PPM'].get(key, 1e9))
    g['render_sheet'](sc, cam, root, cell, frames, anim, os.path.join(D, 'sheets', key + '.png'),
                      lift=lift, px_per_m=ppm, foot_y=foot)
    fits[key] = [round(ppm, 2), round(foot, 2)]; done[key] = fits[key]
json.dump(fits, open(fits_path, 'w'), indent=1)
result = {'done': done}
