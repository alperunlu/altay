# Altay sprite kit -- exec()'d inside Blender. Builds cel-shaded creatures on
# named armatures and renders directions x frames into a PNG atlas.
import bpy, bmesh, math, os
from mathutils import Vector, Matrix, Euler

SCENE = 'AltaySprites'
PX_PER_M = 24.0          # creatures: one metre = 24 world px, one scale for all
ELEV = math.radians(28)  # camera pitch: 3/4 view that still shows a profile
SUN_DIR = Vector((-0.55, 0.55, -0.62)).normalized()   # the game's LIGHT: screen up-left
DIRS5 = [0, 1, 2, 3, 4]  # south, SE, east, NE, north; the west half is mirrored in-game


def c255(*v): return tuple(x / 255 for x in v)


def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


# ------------------------------------------------------------------ scene
def scene():
    sc = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
    bpy.context.window.scene = sc
    r = sc.render
    r.engine = 'BLENDER_EEVEE'; r.film_transparent = True; r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    if sc.world is None: sc.world = bpy.data.worlds.new('AltayWorld')
    w = sc.world; w.use_nodes = True
    bg = w.node_tree.nodes.get('Background')
    bg.inputs[0].default_value = (0.42, 0.44, 0.50, 1); bg.inputs[1].default_value = 0.35
    return sc


def clear_scene(sc):
    for o in list(sc.collection.all_objects): bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        if m.users == 0: bpy.data.meshes.remove(m)
    for a in list(bpy.data.armatures):
        if a.users == 0: bpy.data.armatures.remove(a)


def rig_camera_and_sun(sc):
    cam_d = bpy.data.cameras.new('SprCam'); cam_d.type = 'ORTHO'
    cam = bpy.data.objects.new('SprCam', cam_d); sc.collection.objects.link(cam)
    dist = 20
    cam.location = (0, -dist * math.cos(ELEV), dist * math.sin(ELEV))
    cam.rotation_euler = (math.pi / 2 - ELEV, 0, 0)
    sc.camera = cam
    sun_d = bpy.data.lights.new('SprSun', 'SUN'); sun_d.energy = 3.2; sun_d.angle = math.radians(8)
    sun = bpy.data.objects.new('SprSun', sun_d); sc.collection.objects.link(sun)
    sun.rotation_euler = SUN_DIR.to_track_quat('-Z', 'Y').to_euler()
    fill_d = bpy.data.lights.new('SprFill', 'SUN'); fill_d.energy = 0.45; fill_d.color = (0.75, 0.82, 1.0)
    fill = bpy.data.objects.new('SprFill', fill_d); sc.collection.objects.link(fill)
    fill.rotation_euler = Vector((0.4, 0.8, -0.35)).normalized().to_track_quat('-Z', 'Y').to_euler()
    return cam


def frame_camera(sc, cam, cell_px, render_px, px_per_m=PX_PER_M, foot_y=0.62):
    """Square frame cell_px world pixels wide; ground origin at (0.5, foot_y) from the top."""
    cam.data.ortho_scale = cell_px / px_per_m
    sc.render.resolution_x = sc.render.resolution_y = render_px
    cam.data.shift_x = 0
    cam.data.shift_y = (foot_y - 0.5)


# ------------------------------------------------------------------ materials
def toon(name, rgb, bands=(0.32, 0.6, 1.0), mottle=0.0, form=0.35, rim=0.22, emit=None, emit_strength=1.6):
    """Cel material: diffuse stepped into 3 bands x base colour, darkened toward the
    feet (form), noise in the albedo (mottle), a lit edge on the sun side (rim).
    `emit` makes it a flat glowing colour instead (eyes, runes)."""
    m = bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear(); N = nt.nodes.new; Lk = nt.links.new
    out = N('ShaderNodeOutputMaterial')
    if emit is not None:
        em = N('ShaderNodeEmission'); em.inputs['Color'].default_value = (*[lin(v) for v in emit], 1)
        em.inputs['Strength'].default_value = emit_strength
        Lk(em.outputs[0], out.inputs['Surface']); return m
    base = tuple(lin(v) for v in rgb); bands = tuple(lin(v) for v in bands)
    dif = N('ShaderNodeBsdfDiffuse'); dif.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = N('ShaderNodeShaderToRGB'); Lk(dif.outputs[0], s2r.inputs[0])
    bw = N('ShaderNodeRGBToBW'); Lk(s2r.outputs['Color'], bw.inputs[0])
    ramp = N('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'CONSTANT'
    els = ramp.color_ramp.elements
    els[0].position = 0.0; els[0].color = (bands[0],) * 3 + (1,)
    els[1].position = 0.16; els[1].color = (bands[1],) * 3 + (1,)
    e = els.new(0.55); e.color = (bands[2],) * 3 + (1,)
    Lk(bw.outputs[0], ramp.inputs['Fac'])
    alb = N('ShaderNodeMix'); alb.data_type = 'RGBA'; alb.blend_type = 'MULTIPLY'
    alb.inputs['Factor'].default_value = mottle; alb.inputs[6].default_value = (*base, 1)
    noise = N('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 7.0; noise.inputs['Detail'].default_value = 3.0
    tc = N('ShaderNodeTexCoord'); Lk(tc.outputs['Object'], noise.inputs['Vector'])
    nr = N('ShaderNodeValToRGB')
    nr.color_ramp.elements[0].position = 0.35; nr.color_ramp.elements[0].color = (0.55, 0.5, 0.45, 1)
    nr.color_ramp.elements[1].position = 0.65; nr.color_ramp.elements[1].color = (1, 1, 1, 1)
    Lk(noise.outputs['Fac'], nr.inputs['Fac']); Lk(nr.outputs['Color'], alb.inputs[7])
    lit = N('ShaderNodeMix'); lit.data_type = 'RGBA'; lit.blend_type = 'MULTIPLY'; lit.inputs['Factor'].default_value = 1.0
    Lk(alb.outputs[2], lit.inputs[6]); Lk(ramp.outputs['Color'], lit.inputs[7])
    geo = N('ShaderNodeNewGeometry'); sep = N('ShaderNodeSeparateXYZ'); Lk(geo.outputs['Position'], sep.inputs[0])
    fr = N('ShaderNodeMapRange'); fr.inputs['From Min'].default_value = 0.0; fr.inputs['From Max'].default_value = 1.6
    fr.inputs['To Min'].default_value = 1.0 - form; fr.inputs['To Max'].default_value = 1.0
    Lk(sep.outputs['Z'], fr.inputs['Value'])
    fm = N('ShaderNodeMix'); fm.data_type = 'RGBA'; fm.blend_type = 'MULTIPLY'; fm.inputs['Factor'].default_value = 1.0
    Lk(lit.outputs[2], fm.inputs[6]); Lk(fr.outputs['Result'], fm.inputs[7])
    col = fm.outputs[2]
    if rim > 0:
        lw = N('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.18
        rr = N('ShaderNodeValToRGB'); rr.color_ramp.interpolation = 'CONSTANT'
        rr.color_ramp.elements[0].color = (0, 0, 0, 1); rr.color_ramp.elements[1].position = 0.55; rr.color_ramp.elements[1].color = (1, 1, 1, 1)
        Lk(lw.outputs['Facing'], rr.inputs['Fac'])
        lm = N('ShaderNodeMath'); lm.operation = 'GREATER_THAN'; lm.inputs[1].default_value = 0.5; Lk(bw.outputs[0], lm.inputs[0])
        rm = N('ShaderNodeMath'); rm.operation = 'MULTIPLY'; Lk(rr.outputs['Color'], rm.inputs[0]); Lk(lm.outputs[0], rm.inputs[1])
        rs = N('ShaderNodeMath'); rs.operation = 'MULTIPLY'; rs.inputs[1].default_value = rim; Lk(rm.outputs[0], rs.inputs[0])
        add = N('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'SCREEN'
        Lk(rs.outputs[0], add.inputs['Factor']); Lk(col, add.inputs[6]); add.inputs[7].default_value = (1.0, 0.93, 0.8, 1)
        col = add.outputs[2]
    emn = N('ShaderNodeEmission'); emn.inputs['Strength'].default_value = 1.0
    Lk(col, emn.inputs['Color']); Lk(emn.outputs[0], out.inputs['Surface'])
    return m


def hexrgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------ geometry
def _link(sc, ob):
    for c in list(ob.users_collection): c.objects.unlink(ob)
    sc.collection.objects.link(ob)


def build_armature(sc, name, bones):
    """bones: list of (name, head, tail, parent or None)."""
    ad = bpy.data.armatures.new(name + 'Arm')
    arm = bpy.data.objects.new(name + 'Arm', ad); sc.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    for o in bpy.context.view_layer.objects: o.select_set(False)
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = ad.edit_bones
    for bn, h, t, p in bones:
        b = eb.new(bn); b.head = h; b.tail = t
        if p: b.parent = eb[p]
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm


def skin_body(sc, name, joints, edges, mat, root=0, subsurf=2):
    """joints: list of (co, radius | (rx, ry))."""
    me = bpy.data.meshes.new(name); me.from_pydata([j[0] for j in joints], edges, [])
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    sk = ob.modifiers.new('Skin', 'SKIN'); sk.use_smooth_shade = True; sk.branch_smoothing = 0.6
    for i, (co, r) in enumerate(joints):
        ob.data.skin_vertices[0].data[i].radius = r if isinstance(r, (tuple, list)) else (r, r)
    ob.data.skin_vertices[0].data[root].use_root = True
    ss = ob.modifiers.new('Sub', 'SUBSURF'); ss.levels = subsurf; ss.render_levels = subsurf
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.view_layer.objects: o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    ob.data.materials.append(mat)
    for p in ob.data.polygons: p.use_smooth = True
    return ob


def bind(mesh_ob, arm):
    for o in bpy.context.view_layer.objects: o.select_set(False)
    mesh_ob.select_set(True); arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')


def prim(sc, kind, name, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), smooth=True, **kw):
    fn = {'sphere': bpy.ops.mesh.primitive_uv_sphere_add, 'cyl': bpy.ops.mesh.primitive_cylinder_add,
          'cone': bpy.ops.mesh.primitive_cone_add, 'cube': bpy.ops.mesh.primitive_cube_add,
          'ico': bpy.ops.mesh.primitive_ico_sphere_add, 'torus': bpy.ops.mesh.primitive_torus_add}[kind]
    if kind == 'sphere': kw.setdefault('segments', 16); kw.setdefault('ring_count', 8)
    if kind in ('cyl', 'cone'): kw.setdefault('vertices', 12)
    fn(location=loc, rotation=rot, **kw)
    ob = bpy.context.active_object; ob.name = name; ob.scale = scale
    _link(sc, ob)
    ob.data.materials.append(mat)
    for p in ob.data.polygons: p.use_smooth = smooth and kind != 'cube'
    return ob


def poly_obj(sc, name, mat, pts, thick=0.03):
    """Flat polygon in the local XZ plane (y = 0), given as [(x, z), ...], with some thickness."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]
    bm.faces.new(vs); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    so = ob.modifiers.new('Solid', 'SOLIDIFY'); so.thickness = thick; so.offset = 0
    ob.data.materials.append(mat)
    return ob


def empty(sc, name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e)
    e.location = loc
    if parent: e.parent = parent
    return e


def attach(ob, arm, bone):
    bpy.context.view_layer.update()      # a just-created object's matrix_world is stale until this
    mw = ob.matrix_world.copy()
    ob.parent = arm; ob.parent_type = 'BONE'; ob.parent_bone = bone
    bpy.context.view_layer.update()
    ob.matrix_world = mw


def attach_obj(ob, parent):
    bpy.context.view_layer.update()
    mw = ob.matrix_world.copy()
    ob.parent = parent; ob.parent_type = 'OBJECT'
    bpy.context.view_layer.update()
    ob.matrix_world = mw


def pose(arm, rots):
    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = rots.get(pb.name, (0, 0, 0))
        pb.location = (0, 0, 0)


# ------------------------------------------------------------------ humanoid
def humanoid(sc, name, skin, h=1.8, leg=0.46, bulk=0.3, belly=1.0, head=0.2, neck=0.1, hunch=0.05,
             arm_len=1.0, limb=0.11, hand=0.1, foot=0.16, shoulder=1.0, subsurf=2, head_ry=None):
    """A stick figure dressed by a skin modifier, bound to a named skeleton.
    Faces -Y. Returns (armature, key points)."""
    hipZ = h * leg
    torso = h - hipZ - head * 2.05
    hz = hipZ + torso
    K = {
        'pelvis': Vector((0, 0, hipZ)),
        'belly': Vector((0, -hunch * 0.3, hipZ + torso * 0.38)),
        'chest': Vector((0, -hunch * 0.55, hipZ + torso * 0.78)),
        'neck': Vector((0, -hunch * 0.85, hz)),
        'head': Vector((0, -hunch * 1.05 - head * 0.1, hz + head * 1.0)),
        'head_r': head,
    }
    sw = bulk * 1.05 * shoulder
    for side, sx in (('L', 1), ('R', -1)):
        sh = Vector((sw * sx, -hunch * 0.5, hipZ + torso * 0.9))
        el = sh + Vector((0.12 * sx * arm_len, -0.02, -0.28 * h * arm_len * 0.55))
        wr = el + Vector((0.04 * sx, -0.1 * arm_len, -0.27 * h * arm_len * 0.5))
        hd = wr + Vector((0.01 * sx, -0.04, -hand * 1.4))
        hip = Vector((bulk * 0.55 * sx, 0, hipZ * 0.96))
        kn = Vector((bulk * 0.6 * sx, -0.04, hipZ * 0.5))
        an = Vector((bulk * 0.6 * sx, 0.02, 0.1 * h / 1.8))
        to = Vector((bulk * 0.6 * sx, -foot, 0.04))
        K.update({f'sh.{side}': sh, f'el.{side}': el, f'wr.{side}': wr, f'hand.{side}': hd,
                  f'hip.{side}': hip, f'knee.{side}': kn, f'ankle.{side}': an, f'toe.{side}': to})
    t = lambda v: tuple(v)
    bones = [('hips', t(K['pelvis']), t(K['belly']), None), ('spine', t(K['belly']), t(K['chest']), 'hips'),
             ('chest', t(K['chest']), t(K['neck']), 'spine'),
             ('head', t(K['neck']), t(K['head'] + Vector((0, -head * 0.3, head * 0.9))), 'chest')]
    for s in 'LR':
        bones += [(f'thigh.{s}', t(K[f'hip.{s}']), t(K[f'knee.{s}']), 'hips'),
                  (f'shin.{s}', t(K[f'knee.{s}']), t(K[f'ankle.{s}']), f'thigh.{s}'),
                  (f'foot.{s}', t(K[f'ankle.{s}']), t(K[f'toe.{s}']), f'shin.{s}'),
                  (f'upperarm.{s}', t(K[f'sh.{s}']), t(K[f'el.{s}']), 'chest'),
                  (f'forearm.{s}', t(K[f'el.{s}']), t(K[f'wr.{s}']), f'upperarm.{s}'),
                  (f'hand.{s}', t(K[f'wr.{s}']), t(K[f'hand.{s}']), f'forearm.{s}')]
    arm = build_armature(sc, name, bones)
    J = [(t(K['pelvis']), (bulk * 0.85, bulk * 0.72)), (t(K['belly']), (bulk * belly, bulk * belly * 0.9)),
         (t(K['chest']), (bulk * 1.0, bulk * 0.8)), (t(K['neck']), neck),
         (t(K['head']), (head, head_ry or head))]
    E = [(0, 1), (1, 2), (2, 3), (3, 4)]
    def chain(keys, rads, start):
        idx = []
        for k, r in zip(keys, rads): J.append((t(K[k]), r)); idx.append(len(J) - 1)
        E.append((start, idx[0])); E.extend(zip(idx, idx[1:]))
    for s in 'LR':
        chain([f'hip.{s}', f'knee.{s}', f'ankle.{s}', f'toe.{s}'], [limb * 1.25, limb, limb * 0.85, (limb * 0.8, limb * 0.55)], 0)
        chain([f'sh.{s}', f'el.{s}', f'wr.{s}', f'hand.{s}'], [limb * 1.1, limb * 0.85, limb * 0.72, hand], 2)
    body = skin_body(sc, name + 'Body', J, E, skin, subsurf=subsurf)
    bind(body, arm)
    K['body'] = body
    return arm, K


def paint(body, pick):
    """Per-polygon material by rest-pose position: pick(center) -> material or None."""
    idx = {}
    for p in body.data.polygons:
        m = pick(Vector(p.center))
        if m is None: continue
        if m.name not in idx:
            body.data.materials.append(m); idx[m.name] = len(body.data.materials) - 1
        p.material_index = idx[m.name]


def glow_eyes(sc, arm, K, col, spread=0.4, size=0.035, fwd=0.9, up=0.1, bone='head', count=2, name='eye'):
    """Small emissive eyes on the front of the head -- the one detail that still
    reads at 30px, in the creature's CREEPS eye colour."""
    m = toon(name + '_glow', None, emit=col, emit_strength=2.4)
    hr = K['head_r']; hc = K['head']
    obs = []
    for i in range(count):
        sx = 0 if count == 1 else (-1 + 2 * i / (count - 1))
        p = hc + Vector((sx * hr * spread, -hr * fwd, hr * up))
        obs.append(prim(sc, 'sphere', f'{name}{i}', m, loc=tuple(p), scale=(size, size * 0.6, size * 0.85)))
    for o in obs: attach(o, arm, bone)
    return obs


def walk(arm, p, stride=0.55, arms=0.45, bob_twist=0.12, lean=0.06, knee=0.7, armL=None, armR=None):
    ph = p * math.tau; s, c = math.sin(ph), math.cos(ph)
    R = {
        'thigh.L': (s * stride, 0, 0), 'thigh.R': (-s * stride, 0, 0),
        'shin.L': (-max(0, -c) * knee, 0, 0), 'shin.R': (-max(0, c) * knee, 0, 0),
        'foot.L': (max(0, c) * 0.25, 0, 0), 'foot.R': (max(0, -c) * 0.25, 0, 0),
        'upperarm.L': (-s * arms, 0, 0.08), 'upperarm.R': (s * arms, 0, -0.08),
        'forearm.L': (-0.3, 0, 0), 'forearm.R': (-0.3, 0, 0),
        'spine': (lean, 0, 0), 'chest': (0.03, 0, s * bob_twist), 'hips': (0, 0, -s * bob_twist * 0.6),
    }
    if armL: R.update(armL(s, c))
    if armR: R.update(armR(s, c))
    pose(arm, R)


def step_lift(amount=0.04):
    return lambda p: -abs(math.cos(p * math.tau)) * amount


# ------------------------------------------------------------------ wings
def wing(sc, name, mat, kind, span, chord, side, root, parent, droop=0.0):
    """A rigid wing on a pivot at `root`; flap by rotating the pivot's Y.
    kind 'bat' = membrane with scalloped trailing edge; 'feather' = notched primaries."""
    sx = 1 if side == 'L' else -1
    if kind == 'bat':
        pts = [(0, 0.05), (span * 0.45, chord * 0.55), (span, chord * 0.2),
               (span * 0.82, -chord * 0.25), (span * 0.62, -chord * 0.05), (span * 0.5, -chord * 0.45),
               (span * 0.32, -chord * 0.2), (span * 0.18, -chord * 0.55), (0, -chord * 0.3)]
    else:
        pts = [(0, 0.06), (span * 0.5, chord * 0.35), (span, chord * 0.1)]
        n = 6
        for k in range(n):
            x0 = span * (1 - k / n); x1 = span * (1 - (k + 0.5) / n)
            pts += [(x0 * 0.98, -chord * (0.55 + 0.25 * (k / n))), (x1, -chord * 0.35)]
        pts += [(0, -chord * 0.45)]
    if sx < 0: pts = [(-x, z) for x, z in pts][::-1]
    w = poly_obj(sc, name, mat, pts, thick=0.025)
    piv = empty(sc, name + 'Piv', loc=root)
    w.parent = piv; w.location = (0, 0, 0)
    w.rotation_euler = (math.radians(80), 0, 0)     # chord +Z -> forward (-Y): leading edge ahead, scallops trail
    piv.parent = parent
    piv['side'] = sx; piv['droop'] = droop
    return piv


def flap(pivots, p, amp=0.9, base=0.15):
    a = math.sin(p * math.tau)
    for pv in pivots:
        sx = pv['side']
        pv.rotation_euler = (0, -sx * (base + a * amp) + sx * pv['droop'], 0)


# ------------------------------------------------------------------ render
def render_sheet(sc, cam, root, cell_px, frames, anim, out_path, dirs=DIRS5, supersample=4,
                 lift=None, px_per_m=PX_PER_M, foot_y=0.62):
    import numpy as np
    rp = cell_px * supersample
    frame_camera(sc, cam, cell_px, rp, px_per_m, foot_y)
    tmp = os.path.join(os.path.dirname(out_path), '_tmp_cell.png')
    buf = np.zeros((cell_px * len(dirs), cell_px * frames, 4), dtype=np.float32)
    base_z = root.location.z
    for di, d in enumerate(dirs):
        root.rotation_euler = (0, 0, d * math.pi / 4)
        for f in range(frames):
            anim(f / frames, f)
            root.location.z = base_z + (lift(f / frames) if lift else 0)
            bpy.context.view_layer.update()
            sc.render.filepath = tmp
            bpy.ops.render.render(write_still=True)
            img = bpy.data.images.load(tmp, check_existing=False)
            px = np.array(img.pixels[:], dtype=np.float32).reshape(rp, rp, 4)
            bpy.data.images.remove(img)
            a = px[..., 3:4]
            pm = np.concatenate([px[..., :3] * a, a], axis=2)
            small = pm.reshape(cell_px, supersample, cell_px, supersample, 4).mean(axis=(1, 3))
            al = small[..., 3:4]
            small[..., :3] = np.where(al > 1e-4, small[..., :3] / np.maximum(al, 1e-4), 0)
            y0 = (len(dirs) - 1 - di) * cell_px
            buf[y0:y0 + cell_px, f * cell_px:(f + 1) * cell_px] = small
    root.location.z = base_z
    atlas = bpy.data.images.new('atlas_tmp', cell_px * frames, cell_px * len(dirs), alpha=True)
    atlas.pixels = buf.ravel()
    atlas.filepath_raw = out_path; atlas.file_format = 'PNG'; atlas.save()
    bpy.data.images.remove(atlas)
    return out_path


def preview(sc, cam, root, cell_px, anim, out_prefix, degs=(0, 45, 90), px_per_m=PX_PER_M, foot_y=0.62, size=420):
    for i, deg in enumerate(degs):
        root.rotation_euler = (0, 0, math.radians(deg))
        anim(0.0, 0)
        frame_camera(sc, cam, cell_px, size, px_per_m, foot_y)
        sc.render.filepath = f'{out_prefix}_prev{i}.png'
        bpy.ops.render.render(write_still=True)


def autofit(sc, cam, root, cell_px, anim, lift=None, foot_y=0.62, probe_dirs=(0, 2, 4), frames=4,
            margin_top=0.04, margin_side=0.03, margin_bottom=0.02, base=PX_PER_M):
    """Largest px-per-metre at which every probed direction/frame fits the cell,
    with the ground point pinned at (0.5, foot_y). Extents scale linearly about
    that point, so one probe at `base` is enough to solve for the scale."""
    import numpy as np
    rp = 160
    frame_camera(sc, cam, cell_px, rp, base, foot_y)
    top, bot, left, right = 1.0, 0.0, 1.0, 0.0
    base_z = root.location.z
    for d in probe_dirs:
        root.rotation_euler = (0, 0, d * math.pi / 4)
        for f in range(frames):
            anim(f / frames, f)
            root.location.z = base_z + (lift(f / frames) if lift else 0)
            bpy.context.view_layer.update()
            sc.render.filepath = FIT_TMP
            bpy.ops.render.render(write_still=True)
            img = bpy.data.images.load(FIT_TMP, check_existing=False)
            a = np.array(img.pixels[:], dtype=np.float32).reshape(rp, rp, 4)[..., 3]
            bpy.data.images.remove(img)
            ys, xs = np.nonzero(a > 0.08)
            if not len(ys): continue
            # pixel rows are bottom-up
            top = min(top, 1 - (ys.max() + 1) / rp); bot = max(bot, 1 - ys.min() / rp)
            left = min(left, xs.min() / rp); right = max(right, (xs.max() + 1) / rp)
    root.location.z = base_z
    up, down = foot_y - top, bot - foot_y            # extents about the ground point, at `base`
    side = max(0.5 - left, right - 0.5)
    best = (0, foot_y)
    # the ground point is free too: the game reads each creature's foot line from
    # its atlas entry, so pick the one that lets the figure grow the most
    for i in range(27):
        f = 0.62 + i * 0.01
        k = min((f - margin_top) / max(1e-3, up), (1 - margin_bottom - f) / max(1e-3, down),
                (0.5 - margin_side) / max(1e-3, side))
        if k > best[0]: best = (k, f)
    return base * best[0], best[1]
