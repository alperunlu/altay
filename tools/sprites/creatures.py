# The bestiary. Each builder returns (root, anim(p, f), lift or None).
# Palettes follow CREEPS[k].pal / eye in index.html, pushed a touch darker and
# more saturated so they sit in the game's dusky steppe instead of floating on it.
import math
from mathutils import Vector

R = math.radians


def V(*a): return Vector(a)


def _hold(sc, arm, K, side, ob):
    attach(ob, arm, f'hand.{side}')
    return ob


# ---------------------------------------------------------------- kobold
def kobold(sc):
    fur = toon('kob_fur', c255(150, 98, 54), mottle=0.4, form=0.35)
    belly = toon('kob_belly', c255(196, 160, 110), form=0.3)
    leather = toon('kob_leather', c255(92, 64, 40), mottle=0.2)
    wood = toon('kob_wood', c255(120, 84, 50))
    iron = toon('kob_iron', c255(170, 172, 180), rim=0.45)
    arm, K = humanoid(sc, 'Kob', fur, h=1.15, leg=0.42, bulk=0.2, belly=1.05, head=0.2, neck=0.08, hunch=0.12,
                      arm_len=0.95, limb=0.07, hand=0.065, foot=0.14)
    hc, hr = K['head'], K['head_r']
    P = []
    P.append((prim(sc, 'cone', 'snout', fur, loc=tuple(hc + V(0, -hr * 1.05, -hr * 0.2)), rot=(R(95), 0, 0), radius1=hr * 0.55, radius2=hr * 0.25, depth=hr * 1.1), 'head'))
    P.append((prim(sc, 'sphere', 'nose', toon('kob_nose', c255(40, 26, 20)), loc=tuple(hc + V(0, -hr * 1.62, -hr * 0.12)), scale=(0.035, 0.03, 0.03)), 'head'))
    for sx in (1, -1):
        P.append((prim(sc, 'cone', f'ear{sx}', fur, loc=tuple(hc + V(sx * hr * 0.62, hr * 0.1, hr * 0.8)), rot=(R(-15), R(28 * sx), 0), radius1=hr * 0.34, radius2=0, depth=hr * 1.3, vertices=4), 'head'))
        P.append((prim(sc, 'cone', f'fang{sx}', toon('kob_tooth', c255(240, 232, 210), form=0), loc=tuple(hc + V(sx * hr * 0.2, -hr * 1.35, -hr * 0.5)), rot=(R(180), 0, 0), radius1=0.018, radius2=0, depth=0.06, vertices=6), 'head'))
    P.append((prim(sc, 'sphere', 'vest', leather, loc=tuple(K['chest'] + V(0, 0, -0.02)), scale=(0.22, 0.18, 0.2)), 'chest'))
    P.append((prim(sc, 'sphere', 'bellyfur', belly, loc=tuple(K['belly'] + V(0, -0.12, 0)), scale=(0.13, 0.08, 0.14)), 'spine'))
    h = K['hand.R']
    P.append((prim(sc, 'cyl', 'spear', wood, loc=tuple(h + V(0, -0.05, 0.1)), rot=(R(-110), 0, 0), radius=0.018, depth=1.3), 'hand.R'))
    P.append((prim(sc, 'cone', 'spearhead', iron, loc=tuple(h + V(0, -0.72, 0.34)), rot=(R(70), 0, 0), radius1=0.04, radius2=0, depth=0.16, vertices=4), 'hand.R'))
    for ob, b in P: attach(ob, arm, b)
    glow_eyes(sc, arm, K, hexrgb('#ffe07a'), spread=0.42, size=0.03, fwd=0.82, up=0.2)
    return arm, (lambda p, f: walk(arm, p, stride=0.6, arms=0.3, lean=0.12,
                                   armR=lambda s, c: {'upperarm.R': (-0.5 + s * 0.1, 0, -0.1), 'forearm.R': (-0.6, 0, 0)})), step_lift(0.03)


# ---------------------------------------------------------------- ghoul
def ghoul(sc):
    skin = toon('gh_skin', c255(118, 140, 104), mottle=0.45, form=0.4)
    rag = toon('gh_rag', c255(70, 64, 58), mottle=0.3)
    hair = toon('gh_hair', c255(34, 36, 30), rim=0.15)
    claw = toon('gh_claw', c255(226, 220, 196), form=0)
    arm, K = humanoid(sc, 'Gh', skin, h=1.6, leg=0.44, bulk=0.2, belly=0.8, head=0.17, neck=0.07, hunch=0.28,
                      arm_len=1.45, limb=0.065, hand=0.08, foot=0.17)
    hc, hr = K['head'], K['head_r']
    P = [(prim(sc, 'cone', 'hair', hair, loc=tuple(hc + V(0, hr * 0.5, 0)), rot=(R(-150), 0, 0), radius1=hr * 1.0, radius2=hr * 0.3, depth=hr * 2.6, vertices=8), 'head'),
         (prim(sc, 'sphere', 'jaw', skin, loc=tuple(hc + V(0, -hr * 0.6, -hr * 0.55)), scale=(hr * 0.7, hr * 0.6, hr * 0.45)), 'head'),
         (prim(sc, 'cone', 'loin', rag, loc=tuple(K['pelvis'] + V(0, 0, -0.08)), radius1=0.25, radius2=0.18, depth=0.3, vertices=9), 'hips')]
    for s, sx in (('L', 1), ('R', -1)):
        for k in range(3):
            P.append((prim(sc, 'cone', f'claw{s}{k}', claw, loc=tuple(K[f'hand.{s}'] + V(sx * 0.03 * (k - 1), -0.05, -0.08)), rot=(R(160), 0, 0), radius1=0.018, radius2=0, depth=0.12, vertices=5), f'hand.{s}'))
    for ob, b in P: attach(ob, arm, b)
    glow_eyes(sc, arm, K, hexrgb('#c8ff7a'), spread=0.45, size=0.028, fwd=0.85, up=0.15)
    return arm, (lambda p, f: walk(arm, p, stride=0.5, arms=0.55, lean=0.2, knee=0.8,
                                   armL=lambda s, c: {'upperarm.L': (-0.9 - s * 0.4, 0, 0.1), 'forearm.L': (-0.2, 0, 0)},
                                   armR=lambda s, c: {'upperarm.R': (-0.9 + s * 0.4, 0, -0.1), 'forearm.R': (-0.2, 0, 0)})), step_lift(0.035)


# ---------------------------------------------------------------- grunt (orc warrior)
def grunt(sc):
    skin = toon('gr_skin', c255(92, 128, 72), mottle=0.35, form=0.35)
    leather = toon('gr_leather', c255(112, 80, 50), mottle=0.25)
    iron = toon('gr_iron', c255(132, 136, 146), rim=0.45, mottle=0.15)
    gold = toon('gr_gold', c255(210, 160, 70), rim=0.4)
    wood = toon('gr_wood', c255(96, 66, 40))
    arm, K = humanoid(sc, 'Gr', skin, h=1.75, leg=0.44, bulk=0.3, belly=1.0, head=0.18, neck=0.12, hunch=0.1,
                      arm_len=1.1, limb=0.11, hand=0.09, foot=0.18, shoulder=1.1)
    hc, hr = K['head'], K['head_r']
    P = []
    # helmet with nose guard + crest
    P.append((prim(sc, 'sphere', 'helm', iron, loc=tuple(hc + V(0, 0, hr * 0.28)), scale=(hr * 1.12, hr * 1.12, hr * 0.85)), 'head'))
    P.append((prim(sc, 'cube', 'noseguard', iron, loc=tuple(hc + V(0, -hr * 1.05, 0)), scale=(0.02, 0.02, hr * 0.5)), 'head'))
    P.append((prim(sc, 'cone', 'spike', iron, loc=tuple(hc + V(0, 0, hr * 1.25)), radius1=0.04, radius2=0, depth=0.16, vertices=8), 'head'))
    for sx in (1, -1):
        P.append((prim(sc, 'cone', f'tusk{sx}', toon('gr_tusk', c255(236, 226, 200), form=0), loc=tuple(hc + V(sx * hr * 0.35, -hr * 0.9, -hr * 0.45)), rot=(R(-10), 0, 0), radius1=0.02, radius2=0, depth=0.07, vertices=6), 'head'))
        side = 'L' if sx > 0 else 'R'
        P.append((prim(sc, 'sphere', f'pauldron{side}', iron, loc=tuple(K[f'sh.{side}'] + V(sx * 0.04, 0, 0.06)), scale=(0.17, 0.17, 0.11)), f'upperarm.{side}'))
        P.append((prim(sc, 'cone', f'pspike{side}', iron, loc=tuple(K[f'sh.{side}'] + V(sx * 0.1, 0, 0.16)), rot=(0, R(35 * sx), 0), radius1=0.03, radius2=0, depth=0.12, vertices=6), f'upperarm.{side}'))
    P.append((prim(sc, 'sphere', 'cuirass', leather, loc=tuple(K['chest'] + V(0, -0.02, -0.05)), scale=(0.33, 0.27, 0.3)), 'chest'))
    P.append((prim(sc, 'cyl', 'belt', leather, loc=tuple(K['pelvis'] + V(0, 0, 0.08)), scale=(1, 0.85, 1), radius=0.28, depth=0.1), 'hips'))
    P.append((prim(sc, 'cyl', 'buckle', gold, loc=tuple(K['pelvis'] + V(0, -0.25, 0.08)), rot=(R(90), 0, 0), radius=0.05, depth=0.03), 'hips'))
    P.append((prim(sc, 'cone', 'skirt', leather, loc=tuple(K['pelvis'] + V(0, 0, -0.1)), radius1=0.32, radius2=0.26, depth=0.26, vertices=8), 'hips'))
    # axe in the right hand
    h = K['hand.R']
    P.append((prim(sc, 'cyl', 'haft', wood, loc=tuple(h + V(0, -0.1, 0.12)), rot=(R(-120), 0, 0), radius=0.022, depth=0.85), 'hand.R'))
    ax = poly_obj(sc, 'axehead', iron, [(0, 0), (0.1, 0.12), (0.22, 0.08), (0.24, -0.1), (0.1, -0.12), (0, -0.04)], thick=0.03)
    ax.location = tuple(h + V(-0.02, -0.46, 0.32)); ax.rotation_euler = (0, 0, R(-90)); P.append((ax, 'hand.R'))
    for ob, b in P: attach(ob, arm, b)
    glow_eyes(sc, arm, K, hexrgb('#ff9a5a'), spread=0.38, size=0.028, fwd=0.9, up=0.05)
    return arm, (lambda p, f: walk(arm, p, stride=0.55, arms=0.35, lean=0.06,
                                   armR=lambda s, c: {'upperarm.R': (-0.35 + s * 0.15, 0, -0.1), 'forearm.R': (-0.7, 0, 0)})), step_lift(0.035)


# ---------------------------------------------------------------- ogre (Tepegöz)
def ogre(sc):
    skin = toon('og_skin', c255(162, 116, 80), mottle=0.4, form=0.42)
    hide = toon('og_hide', c255(92, 64, 40), mottle=0.25, form=0.3)
    hair = toon('og_hair', c255(44, 30, 26), form=0.1, rim=0.3)
    bone = toon('og_bone', c255(232, 220, 190), form=0.15)
    wood = toon('og_wood', c255(110, 74, 42), mottle=0.3, form=0.25)
    iron = toon('og_iron', c255(122, 126, 136), form=0.2, rim=0.45)
    dark = toon('og_mouth', c255(60, 22, 18), rim=0)
    arm, K = humanoid(sc, 'Og', skin, h=2.35, leg=0.38, bulk=0.52, belly=1.18, head=0.36, neck=0.26, hunch=0.34,
                      arm_len=1.05, limb=0.2, hand=0.22, foot=0.24, shoulder=1.12)
    hc, hr = K['head'], K['head_r']
    P = []
    ew = toon('og_eyewhite', c255(255, 238, 160), bands=(0.8, 0.95, 1.0), form=0, rim=0)
    P.append((prim(sc, 'sphere', 'eye', ew, loc=tuple(hc + V(0, -hr * 0.88, hr * 0.12)), scale=(hr * 0.55, hr * 0.42, hr * 0.52), segments=24, ring_count=12), 'head'))
    P.append((prim(sc, 'sphere', 'pupil', toon('og_pupil', None, emit=(0.95, 0.25, 0.1), emit_strength=2.2), loc=tuple(hc + V(0, -hr * 1.26, hr * 0.12)), scale=(hr * 0.22, hr * 0.1, hr * 0.3)), 'head'))
    P.append((prim(sc, 'sphere', 'brow', skin, loc=tuple(hc + V(0, -hr * 0.78, hr * 0.62)), rot=(R(-15), 0, 0), scale=(hr * 0.85, hr * 0.38, hr * 0.24)), 'head'))
    P.append((prim(sc, 'sphere', 'mouth', dark, loc=tuple(hc + V(0, -hr * 0.9, -hr * 0.5)), scale=(hr * 0.55, hr * 0.16, hr * 0.13)), 'head'))
    for sx in (1, -1):
        P.append((prim(sc, 'cone', f'horn{sx}', bone, loc=tuple(hc + V(sx * hr * 0.7, 0, hr * 0.9)), rot=(R(-10), R(40 * sx), 0), radius1=hr * 0.3, radius2=0, depth=hr * 1.4), 'head'))
        P.append((prim(sc, 'cone', f'tusk{sx}', bone, loc=tuple(hc + V(sx * hr * 0.38, -hr * 0.92, -hr * 0.36)), rot=(R(-15), R(-12 * sx), 0), radius1=hr * 0.14, radius2=0, depth=hr * 0.55, vertices=8), 'head'))
        side = 'L' if sx > 0 else 'R'
        P.append((prim(sc, 'cyl', f'bracer{side}', iron, loc=tuple((K[f'el.{side}'] + K[f'wr.{side}']) / 2), rot=(R(-18), R(-10 * sx), 0), radius=0.22, depth=0.2, vertices=14), f'forearm.{side}'))
    P.append((prim(sc, 'cone', 'topknot', hair, loc=tuple(hc + V(0, hr * 0.3, hr * 1.05)), rot=(R(25), 0, 0), radius1=hr * 0.36, radius2=hr * 0.08, depth=hr * 0.95, vertices=10), 'head'))
    for k in range(9):
        a = R(-70 + k * 17.5); c = K['chest']
        P.append((prim(sc, 'cone', f'fang{k}', bone, loc=(math.sin(a) * 0.46, c.y - 0.18 - math.cos(a) * 0.36, c.z - 0.02), rot=(R(200), 0, -a), radius1=0.035, radius2=0, depth=0.12, vertices=6), 'chest'))
    pv = K['pelvis']
    P.append((prim(sc, 'sphere', 'flapF', hide, loc=tuple(pv + V(0, -0.44, -0.2)), rot=(R(10), 0, 0), scale=(0.3, 0.05, 0.3)), 'hips'))
    P.append((prim(sc, 'sphere', 'flapB', hide, loc=tuple(pv + V(0, 0.38, -0.18)), rot=(R(-10), 0, 0), scale=(0.34, 0.05, 0.28)), 'hips'))
    P.append((prim(sc, 'torus', 'belt', hide, loc=tuple(pv + V(0, -0.06, 0.06)), scale=(1.0, 0.86, 1.8), major_radius=0.47, minor_radius=0.055), 'hips'))
    # carried low at the side, fat end down: a club that sticks far forward
    # dictated the whole sprite's scale and left the ogre as small as a kobold
    ang = R(-22); h = K['hand.R']
    ctr = h + V(-0.02, -0.2, -0.5)
    P.append((prim(sc, 'cone', 'club', wood, loc=tuple(ctr), rot=(ang, 0, 0), radius1=0.22, radius2=0.07, depth=1.35, vertices=16), 'hand.R'))
    axv = V(0, -math.sin(ang), math.cos(ang))
    for k, t in enumerate((0.22, 0.52)):
        P.append((prim(sc, 'torus', f'band{k}', iron, loc=tuple(ctr + axv * ((t - 0.5) * 1.35)), rot=(ang, 0, 0), major_radius=0.22 - 0.15 * t, minor_radius=0.03), 'hand.R'))
    base = ctr - axv * 0.62
    for k in range(6):
        a = k / 6 * math.tau
        P.append((prim(sc, 'cone', f'spike{k}', iron, loc=(base.x + math.cos(a) * 0.21, base.y + math.sin(a) * 0.11, base.z + math.sin(a) * 0.18),
                       rot=(ang + math.sin(a) * 1.2, math.cos(a) * 1.3, 0), radius1=0.05, radius2=0, depth=0.18, vertices=6), 'hand.R'))
    for ob, b in P: attach(ob, arm, b)
    return arm, (lambda p, f: walk(arm, p, stride=0.6, arms=0.45, lean=0.08, knee=0.8,
                                   armR=lambda s, c: {'upperarm.R': (s * 0.25, 0, -0.1), 'forearm.R': (-0.35, 0, 0)})), step_lift(0.06)


# ---------------------------------------------------------------- khan (Erlik Kağan, boss)
def khan(sc):
    skin = toon('kh_skin', c255(110, 48, 52), mottle=0.3)
    plate = toon('kh_plate', c255(70, 60, 82), rim=0.5, mottle=0.15, form=0.3)
    trim = toon('kh_trim', c255(214, 150, 70), rim=0.45)
    cape = toon('kh_cape', c255(120, 20, 26), mottle=0.2, form=0.45)
    horn = toon('kh_horn', c255(96, 36, 36), rim=0.5, form=0.1)
    steel = toon('kh_steel', c255(170, 176, 190), rim=0.6)
    ember = toon('kh_ember', None, emit=hexrgb('#ff4d3a'), emit_strength=2.5)
    arm, K = humanoid(sc, 'Kh', plate, h=2.5, leg=0.45, bulk=0.42, belly=0.95, head=0.25, neck=0.16, hunch=0.06,
                      arm_len=1.05, limb=0.15, hand=0.13, foot=0.22, shoulder=1.2)
    hc, hr = K['head'], K['head_r']
    P = []
    P.append((prim(sc, 'sphere', 'helm', plate, loc=tuple(hc + V(0, 0, hr * 0.2)), scale=(hr * 1.1, hr * 1.1, hr * 1.05)), 'head'))
    P.append((prim(sc, 'cube', 'visor', skin, loc=tuple(hc + V(0, -hr * 1.0, -hr * 0.1)), scale=(hr * 0.55, 0.03, hr * 0.35)), 'head'))
    for sx in (1, -1):
        side = 'L' if sx > 0 else 'R'
        P.append((prim(sc, 'cone', f'horn{sx}', horn, loc=tuple(hc + V(sx * hr * 1.05, 0, hr * 0.85)), rot=(R(-25), R(45 * sx), 0), radius1=hr * 0.38, radius2=0, depth=hr * 3.2), 'head'))
        P.append((prim(sc, 'sphere', f'pauld{side}', plate, loc=tuple(K[f'sh.{side}'] + V(sx * 0.06, 0, 0.1)), scale=(0.26, 0.26, 0.16)), f'upperarm.{side}'))
        P.append((prim(sc, 'torus', f'ptrim{side}', trim, loc=tuple(K[f'sh.{side}'] + V(sx * 0.06, 0, 0.06)), major_radius=0.24, minor_radius=0.025), f'upperarm.{side}'))
        for k in range(2):
            P.append((prim(sc, 'cone', f'pspike{side}{k}', horn, loc=tuple(K[f'sh.{side}'] + V(sx * 0.12, -0.08 + k * 0.16, 0.22)), rot=(0, R(25 * sx), 0), radius1=0.04, radius2=0, depth=0.2, vertices=6), f'upperarm.{side}'))
    for sx in (-1, 1):
        P.append((prim(sc, 'sphere', f'glow{sx}', ember, loc=tuple(hc + V(sx * hr * 0.25, -hr * 1.04, 0)), scale=(0.04, 0.02, 0.025)), 'head'))
    P.append((prim(sc, 'sphere', 'breast', plate, loc=tuple(K['chest'] + V(0, -0.06, -0.04)), scale=(0.46, 0.34, 0.4)), 'chest'))
    P.append((prim(sc, 'sphere', 'gem', ember, loc=tuple(K['chest'] + V(0, -0.4, 0)), scale=(0.06, 0.04, 0.07)), 'chest'))
    P.append((prim(sc, 'cone', 'skirt', plate, loc=tuple(K['pelvis'] + V(0, 0, -0.16)), radius1=0.5, radius2=0.38, depth=0.5, vertices=10), 'hips'))
    P.append((prim(sc, 'torus', 'belt', trim, loc=tuple(K['pelvis'] + V(0, 0, 0.08)), scale=(1, 0.85, 1.4), major_radius=0.4, minor_radius=0.04), 'hips'))
    # cape: a tapered plane down the back from the shoulders
    c = K['chest']
    cp = poly_obj(sc, 'cape', cape, [(-0.5, 0), (0.5, 0), (0.75, -1.7), (0.3, -1.6), (0, -1.75), (-0.3, -1.6), (-0.75, -1.7)], thick=0.04)
    cp.location = (0, c.y + 0.38, c.z + 0.22); cp.rotation_euler = (R(8), 0, 0); P.append((cp, 'chest'))
    # the blade: long curved sword, forward
    h = K['hand.R']
    bl = poly_obj(sc, 'blade', steel, [(0, 0), (0.07, 0.05), (0.09, 1.0), (0.02, 1.35), (-0.05, 1.0), (-0.05, 0.05)], thick=0.03)
    bl.location = tuple(h + V(0, -0.1, 0.05)); bl.rotation_euler = (R(75), 0, 0); P.append((bl, 'hand.R'))
    P.append((prim(sc, 'cube', 'guard', trim, loc=tuple(h + V(0, -0.1, 0.05)), rot=(R(75), 0, 0), scale=(0.16, 0.03, 0.03)), 'hand.R'))
    for ob, b in P: attach(ob, arm, b)
    return arm, (lambda p, f: walk(arm, p, stride=0.45, arms=0.3, lean=0.03,
                                   armR=lambda s, c: {'upperarm.R': (-0.5 + s * 0.1, 0, -0.15), 'forearm.R': (-0.6, 0, 0)})), step_lift(0.05)


# ---------------------------------------------------------------- basci (Kara Bakşı)
def basci(sc):
    robe = toon('ba_robe', c255(66, 42, 88), mottle=0.3, form=0.4)
    fur = toon('ba_fur', c255(84, 66, 52), mottle=0.4)
    skin = toon('ba_skin', c255(150, 112, 86))
    hide = toon('ba_hide', c255(208, 184, 140), form=0.1)
    wood = toon('ba_wood', c255(92, 64, 40))
    feather = toon('ba_feather', c255(34, 30, 38), rim=0.35)
    rune = toon('ba_rune', None, emit=hexrgb('#c79bff'), emit_strength=2.2)
    arm, K = humanoid(sc, 'Ba', skin, h=1.65, leg=0.44, bulk=0.22, belly=0.95, head=0.16, neck=0.07, hunch=0.12,
                      arm_len=1.0, limb=0.075, hand=0.07, foot=0.15)
    hc, hr = K['head'], K['head_r']
    P = []
    P.append((prim(sc, 'cone', 'robe', robe, loc=tuple(K['pelvis'] + V(0, 0.02, 0.05)), radius1=0.44, radius2=0.2, depth=0.95, vertices=12), 'hips'))
    P.append((prim(sc, 'sphere', 'mantle', fur, loc=tuple(K['chest'] + V(0, 0, 0.05)), scale=(0.3, 0.26, 0.2)), 'chest'))
    P.append((prim(sc, 'sphere', 'hood', robe, loc=tuple(hc + V(0, hr * 0.15, hr * 0.15)), scale=(hr * 1.2, hr * 1.2, hr * 1.1)), 'head'))
    for k in range(7):
        a = R(-60 + k * 20)
        P.append((prim(sc, 'cone', f'feather{k}', feather, loc=tuple(hc + V(math.sin(a) * hr * 0.9, math.cos(a) * hr * 0.35, hr * 1.1)), rot=(R(-10), math.sin(a) * 0.6, 0), radius1=0.035, radius2=0.005, depth=0.3, vertices=4), 'head'))
    # frame drum on the left arm, staff with a glowing charm in the right
    d = K['hand.L']
    P.append((prim(sc, 'cyl', 'drum', hide, loc=tuple(d + V(0.05, -0.12, 0.1)), rot=(R(90), 0, R(20)), radius=0.2, depth=0.06, vertices=20), 'hand.L'))
    P.append((prim(sc, 'torus', 'drumrim', wood, loc=tuple(d + V(0.05, -0.12, 0.1)), rot=(R(90), 0, R(20)), major_radius=0.2, minor_radius=0.02), 'hand.L'))
    h = K['hand.R']
    P.append((prim(sc, 'cyl', 'staff', wood, loc=tuple(h + V(0, -0.04, 0.25)), radius=0.02, depth=1.5), 'hand.R'))
    P.append((prim(sc, 'ico', 'charm', rune, loc=tuple(h + V(0, -0.04, 1.02)), radius=0.065, subdivisions=1, smooth=False), 'hand.R'))
    for ob, b in P: attach(ob, arm, b)
    glow_eyes(sc, arm, K, hexrgb('#c79bff'), spread=0.4, size=0.026, fwd=0.9, up=0.05)
    return arm, (lambda p, f: walk(arm, p, stride=0.4, arms=0.2, lean=0.08,
                                   armL=lambda s, c: {'upperarm.L': (-0.6, 0, 0.3), 'forearm.L': (-0.9, 0, 0)},
                                   armR=lambda s, c: {'upperarm.R': (-0.3 + s * 0.1, 0, -0.1), 'forearm.R': (-0.5, 0, 0)})), step_lift(0.025)


# ---------------------------------------------------------------- umay (Umay Ana)
def umay(sc):
    robe = toon('um_robe', c255(226, 208, 164), mottle=0.15, form=0.3)
    gold = toon('um_gold', c255(220, 170, 70), rim=0.5)
    skin = toon('um_skin', c255(214, 174, 136))
    hair = toon('um_hair', c255(236, 226, 196), rim=0.3, form=0.15)
    light = toon('um_light', None, emit=hexrgb('#ffe9a0'), emit_strength=2.6)
    wood = toon('um_wood', c255(170, 130, 80))
    arm, K = humanoid(sc, 'Um', skin, h=1.72, leg=0.46, bulk=0.2, belly=0.85, head=0.15, neck=0.06, hunch=0.02,
                      arm_len=1.0, limb=0.065, hand=0.06, foot=0.14)
    hc, hr = K['head'], K['head_r']
    P = [(prim(sc, 'cone', 'gown', robe, loc=tuple(K['pelvis'] + V(0, 0.02, 0.0)), radius1=0.46, radius2=0.18, depth=1.05, vertices=14), 'hips'),
         (prim(sc, 'sphere', 'bodice', robe, loc=tuple(K['chest'] + V(0, 0, -0.04)), scale=(0.22, 0.18, 0.24)), 'chest'),
         (prim(sc, 'torus', 'girdle', gold, loc=tuple(K['belly'] + V(0, 0, 0)), scale=(1, 0.85, 1.4), major_radius=0.2, minor_radius=0.025), 'spine'),
         (prim(sc, 'sphere', 'hairback', hair, loc=tuple(hc + V(0, hr * 0.45, -hr * 0.6)), scale=(hr * 1.05, hr * 0.6, hr * 2.0)), 'head'),
         (prim(sc, 'sphere', 'haircap', hair, loc=tuple(hc + V(0, hr * 0.15, hr * 0.3)), scale=(hr * 1.1, hr * 1.1, hr * 0.8)), 'head'),
         (prim(sc, 'torus', 'circlet', gold, loc=tuple(hc + V(0, 0, hr * 0.35)), rot=(R(-12), 0, 0), major_radius=hr * 1.02, minor_radius=0.015), 'head')]
    h = K['hand.R']
    P.append((prim(sc, 'cyl', 'staff', wood, loc=tuple(h + V(0, -0.04, 0.2)), radius=0.018, depth=1.55), 'hand.R'))
    P.append((prim(sc, 'sphere', 'orb', light, loc=tuple(h + V(0, -0.04, 1.02)), scale=(0.09, 0.09, 0.09)), 'hand.R'))
    P.append((prim(sc, 'torus', 'orbring', gold, loc=tuple(h + V(0, -0.04, 1.02)), rot=(R(90), 0, 0), major_radius=0.12, minor_radius=0.015), 'hand.R'))
    for ob, b in P: attach(ob, arm, b)
    glow_eyes(sc, arm, K, hexrgb('#ffe9a0'), spread=0.4, size=0.022, fwd=0.9, up=0.05)
    return arm, (lambda p, f: walk(arm, p, stride=0.35, arms=0.2, lean=0.0,
                                   armL=lambda s, c: {'upperarm.L': (-0.4, 0, 0.25), 'forearm.L': (-0.8, 0, 0)},
                                   armR=lambda s, c: {'upperarm.R': (-0.25, 0, -0.1), 'forearm.R': (-0.5, 0, 0)})), step_lift(0.02)


# ---------------------------------------------------------------- yelbegen (many-headed giant)
def yelbegen(sc):
    skin = toon('ye_skin', c255(104, 68, 50), mottle=0.45, form=0.42)
    hide = toon('ye_hide', c255(70, 52, 38), mottle=0.3)
    horn = toon('ye_horn', c255(52, 40, 36), rim=0.35)
    wood = toon('ye_wood', c255(88, 60, 36))
    bone = toon('ye_bone', c255(228, 214, 186), form=0)
    arm, K = humanoid(sc, 'Ye', skin, h=2.4, leg=0.4, bulk=0.5, belly=1.1, head=0.27, neck=0.22, hunch=0.2,
                      arm_len=1.05, limb=0.18, hand=0.18, foot=0.24, shoulder=1.15)
    hc, hr = K['head'], K['head_r']
    P = []
    eyem = toon('ye_eye', None, emit=hexrgb('#ff6a3a'), emit_strength=2.4)
    heads = [(0, V(0, 0, 0)), (1, V(0.46, 0.08, -0.1)), (-1, V(-0.46, 0.08, -0.1))]
    for sx, off in heads:
        c = hc + off
        r = hr * (1.0 if sx == 0 else 0.82)
        if sx:
            P.append((prim(sc, 'sphere', f'neck{sx}', skin, loc=tuple((c + K['chest']) / 2 + V(0, 0, 0.1)), scale=(0.16, 0.16, 0.3)), 'chest'))
        P.append((prim(sc, 'sphere', f'head{sx}', skin, loc=tuple(c), scale=(r, r * 1.05, r * 0.95)), 'head' if sx == 0 else 'chest'))
        P.append((prim(sc, 'sphere', f'jaw{sx}', skin, loc=tuple(c + V(0, -r * 0.55, -r * 0.45)), scale=(r * 0.7, r * 0.6, r * 0.4)), 'head' if sx == 0 else 'chest'))
        for ex in (-1, 1):
            P.append((prim(sc, 'sphere', f'eye{sx}{ex}', eyem, loc=tuple(c + V(ex * r * 0.38, -r * 0.9, r * 0.12)), scale=(0.035, 0.02, 0.028)), 'head' if sx == 0 else 'chest'))
            P.append((prim(sc, 'cone', f'horn{sx}{ex}', horn, loc=tuple(c + V(ex * r * 0.6, 0, r * 0.75)), rot=(R(-20), R(35 * ex), 0), radius1=r * 0.22, radius2=0, depth=r * 1.1, vertices=8), 'head' if sx == 0 else 'chest'))
            P.append((prim(sc, 'cone', f'fang{sx}{ex}', bone, loc=tuple(c + V(ex * r * 0.3, -r * 0.95, -r * 0.4)), rot=(R(180), 0, 0), radius1=0.03, radius2=0, depth=0.08, vertices=6), 'head' if sx == 0 else 'chest'))
    pv = K['pelvis']
    P.append((prim(sc, 'cone', 'loin', hide, loc=tuple(pv + V(0, 0, -0.12)), radius1=0.55, radius2=0.45, depth=0.4, vertices=10), 'hips'))
    h = K['hand.R']; ang = R(-55)
    P.append((prim(sc, 'cone', 'club', wood, loc=tuple(h + V(0, -0.4, -0.12)), rot=(ang, 0, 0), radius1=0.2, radius2=0.07, depth=1.3, vertices=14), 'hand.R'))
    for ob, b in P: attach(ob, arm, b)
    return arm, (lambda p, f: walk(arm, p, stride=0.5, arms=0.4, lean=0.08, knee=0.75,
                                   armR=lambda s, c: {'upperarm.R': (s * 0.2, 0, -0.1), 'forearm.R': (-0.35, 0, 0)})), step_lift(0.055)


# ---------------------------------------------------------------- yelbegenYavru (severed head, still snapping)
def yelbegenYavru(sc):
    skin = toon('yy_skin', c255(112, 74, 54), mottle=0.45, form=0.3)
    horn = toon('yy_horn', c255(60, 44, 40), rim=0.35)
    bone = toon('yy_bone', c255(236, 224, 196), form=0)
    dark = toon('yy_mouth', c255(70, 20, 16), rim=0)
    arm, K = humanoid(sc, 'Yy', skin, h=0.95, leg=0.3, bulk=0.22, belly=1.3, head=0.26, neck=0.18, hunch=0.12,
                      arm_len=0.6, limb=0.07, hand=0.07, foot=0.12)
    hc, hr = K['head'], K['head_r']
    P = [(prim(sc, 'sphere', 'maw', dark, loc=tuple(hc + V(0, -hr * 0.82, -hr * 0.3)), scale=(hr * 0.6, hr * 0.3, hr * 0.28)), 'head')]
    for ex in (-1, 1):
        P.append((prim(sc, 'cone', f'horn{ex}', horn, loc=tuple(hc + V(ex * hr * 0.65, 0, hr * 0.7)), rot=(R(-25), R(45 * ex), 0), radius1=hr * 0.24, radius2=0, depth=hr * 1.2, vertices=8), 'head'))
        for k in range(3):
            P.append((prim(sc, 'cone', f'tooth{ex}{k}', bone, loc=tuple(hc + V(ex * hr * (0.12 + 0.18 * k), -hr * 0.95, -hr * 0.15)), rot=(R(180), 0, 0), radius1=0.02, radius2=0, depth=0.06, vertices=5), 'head'))
    for ob, b in P: attach(ob, arm, b)
    glow_eyes(sc, arm, K, hexrgb('#ff6a3a'), spread=0.45, size=0.035, fwd=0.85, up=0.28)
    return arm, (lambda p, f: walk(arm, p, stride=0.75, arms=0.5, lean=0.15, knee=0.9)), (lambda p: abs(math.sin(p * math.tau)) * 0.08)


# ---------------------------------------------------------------- titan (Ötüken Devi, stone giant)
def titan(sc):
    rock = toon('ti_rock', c255(88, 104, 98), mottle=0.5, form=0.35, rim=0.3)
    moss = toon('ti_moss', c255(72, 110, 58), mottle=0.4)
    crack = toon('ti_crack', None, emit=hexrgb('#8affd0'), emit_strength=2.4)
    inner = toon('ti_core', c255(40, 50, 48))
    arm, K = humanoid(sc, 'Ti', inner, h=3.0, leg=0.38, bulk=0.55, belly=1.0, head=0.3, neck=0.2, hunch=0.22,
                      arm_len=1.15, limb=0.2, hand=0.26, foot=0.28, shoulder=1.25, subsurf=1)
    import random
    rnd = random.Random(7)
    P = []
    def chunk(name, at, bone, r, n=1, jitter=0.1):
        for i in range(n):
            o = prim(sc, 'ico', f'{name}{i}', rock, loc=tuple(at + V(rnd.uniform(-jitter, jitter), rnd.uniform(-jitter, jitter), rnd.uniform(-jitter, jitter))),
                     rot=(rnd.random() * 3, rnd.random() * 3, rnd.random() * 3), scale=(r * rnd.uniform(0.85, 1.15), r * rnd.uniform(0.8, 1.1), r * rnd.uniform(0.85, 1.15)),
                     radius=1, subdivisions=1, smooth=False)
            P.append((o, bone))
    chunk('chest', K['chest'], 'chest', 0.62, 2, 0.12)
    chunk('belly', K['belly'], 'spine', 0.52, 2, 0.1)
    chunk('pelvis', K['pelvis'], 'hips', 0.45, 1)
    chunk('head', K['head'], 'head', 0.34, 1)
    for s, sx in (('L', 1), ('R', -1)):
        chunk(f'sh{s}', K[f'sh.{s}'] + V(sx * 0.08, 0, 0.1), f'upperarm.{s}', 0.36, 1)
        chunk(f'ua{s}', (K[f'sh.{s}'] + K[f'el.{s}']) / 2, f'upperarm.{s}', 0.24, 1)
        chunk(f'fa{s}', (K[f'el.{s}'] + K[f'wr.{s}']) / 2, f'forearm.{s}', 0.25, 1)
        chunk(f'fist{s}', K[f'hand.{s}'], f'hand.{s}', 0.3, 1)
        chunk(f'th{s}', (K[f'hip.{s}'] + K[f'knee.{s}']) / 2, f'thigh.{s}', 0.3, 1)
        chunk(f'sn{s}', (K[f'knee.{s}'] + K[f'ankle.{s}']) / 2, f'shin.{s}', 0.26, 1)
        chunk(f'ft{s}', K[f'ankle.{s}'] + V(0, -0.1, 0), f'foot.{s}', 0.24, 1)
        P.append((prim(sc, 'sphere', f'moss{s}', moss, loc=tuple(K[f'sh.{s}'] + V(sx * 0.1, 0, 0.36)), scale=(0.3, 0.26, 0.1)), f'upperarm.{s}'))
    P.append((prim(sc, 'sphere', 'mossback', moss, loc=tuple(K['chest'] + V(0, 0.3, 0.45)), scale=(0.5, 0.4, 0.14)), 'chest'))
    # glowing seams: the core showing through
    hc = K['head']
    for ex in (-1, 1):
        P.append((prim(sc, 'sphere', f'eye{ex}', crack, loc=tuple(hc + V(ex * 0.1, -0.33, 0.02)), scale=(0.05, 0.02, 0.03)), 'head'))
    P.append((prim(sc, 'cube', 'seam', crack, loc=tuple(K['chest'] + V(0, -0.62, 0)), rot=(0, R(20), 0), scale=(0.03, 0.02, 0.3)), 'chest'))
    P.append((prim(sc, 'cube', 'seam2', crack, loc=tuple(K['belly'] + V(0.1, -0.52, 0)), rot=(0, R(-35), 0), scale=(0.025, 0.02, 0.22)), 'spine'))
    for ob, b in P: attach(ob, arm, b)
    return arm, (lambda p, f: walk(arm, p, stride=0.4, arms=0.35, lean=0.08, knee=0.6)), step_lift(0.07)


# ---------------------------------------------------------------- flyers
def _flyer_body(sc, name, skin, body_len, body_r, head_r, neck_len=0.2, legs=True, alt=0.55):
    """Horizontal-ish body on a rig with one root; wings attach to the root object."""
    bones = [('body', (0, 0.25 * body_len, alt), (0, -0.25 * body_len, alt + 0.05), None),
             ('head', (0, -0.25 * body_len, alt + 0.05), (0, -0.25 * body_len - neck_len - head_r, alt + 0.12), 'body')]
    if legs:
        for s, sx in (('L', 1), ('R', -1)):
            bones.append((f'leg.{s}', (sx * body_r * 0.5, 0.05, alt - body_r * 0.5), (sx * body_r * 0.5, 0.0, alt - body_r * 0.5 - 0.35), 'body'))
    arm = build_armature(sc, name, bones)
    return arm


def harpy(sc):
    skin = toon('hp_skin', c255(176, 132, 150), mottle=0.2)
    plume = toon('hp_plume', c255(128, 86, 142), mottle=0.3, form=0.3)
    wingm = toon('hp_wing', c255(168, 126, 184), mottle=0.3, form=0.25, rim=0.35)
    hair = toon('hp_hair', c255(62, 36, 70), rim=0.3)
    talon = toon('hp_talon', c255(226, 196, 110), rim=0.3)
    alt = 0.4
    arm = build_armature(sc, 'Hp', [('body', (0, 0.1, alt), (0, -0.05, alt + 0.4), None), ('head', (0, -0.05, alt + 0.4), (0, -0.12, alt + 0.62), 'body')])
    P = [(prim(sc, 'sphere', 'torso', skin, loc=(0, -0.02, alt + 0.26), scale=(0.18, 0.14, 0.24)), 'body'),
         (prim(sc, 'sphere', 'feathers', plume, loc=(0, 0.06, alt + 0.02), scale=(0.2, 0.2, 0.2)), 'body'),
         (prim(sc, 'cone', 'tail', plume, loc=(0, 0.3, alt - 0.02), rot=(R(-70), 0, 0), radius1=0.16, radius2=0.02, depth=0.4, vertices=6), 'body'),
         (prim(sc, 'sphere', 'head', skin, loc=(0, -0.1, alt + 0.6), scale=(0.12, 0.12, 0.13)), 'head'),
         (prim(sc, 'cone', 'hair', hair, loc=(0, 0.02, alt + 0.56), rot=(R(-160), 0, 0), radius1=0.13, radius2=0.03, depth=0.36, vertices=8), 'head')]
    for sx in (1, -1):
        P.append((prim(sc, 'cone', f'leg{sx}', talon, loc=(sx * 0.08, 0.02, alt - 0.2), rot=(R(160), 0, 0), radius1=0.035, radius2=0.015, depth=0.26, vertices=6), 'body'))
        for k in range(3):
            P.append((prim(sc, 'cone', f'claw{sx}{k}', talon, loc=(sx * 0.08 + (k - 1) * 0.025, -0.05, alt - 0.34), rot=(R(120), 0, 0), radius1=0.015, radius2=0, depth=0.08, vertices=4), 'body'))
    for ob, b in P: attach(ob, arm, b)
    em = toon('hp_eye', None, emit=hexrgb('#ffd0f0'), emit_strength=2.4)
    for ex in (-1, 1):
        e = prim(sc, 'sphere', f'eye{ex}', em, loc=(ex * 0.045, -0.21, alt + 0.62), scale=(0.022, 0.012, 0.018)); attach(e, arm, 'head')
    pivs = [wing(sc, f'wing{s}', wingm, 'feather', 0.85, 0.55, s, (sx * 0.12, 0.0, alt + 0.36), arm) for s, sx in (('L', 1), ('R', -1))]
    def anim(p, f):
        pose(arm, {'body': (R(12), 0, 0), 'head': (R(-10), 0, 0)})
        flap(pivs, p, amp=0.75, base=0.1)
    return arm, anim, (lambda p: math.sin(p * math.tau) * 0.06)


def gargoyle(sc):
    stone = toon('ga_stone', c255(118, 120, 130), mottle=0.5, rim=0.35)
    wingm = toon('ga_wing', c255(80, 82, 96), mottle=0.3, rim=0.3)
    horn = toon('ga_horn', c255(200, 202, 212), rim=0.4)
    alt = 0.45
    arm, K = humanoid(sc, 'Ga', stone, h=1.35, leg=0.36, bulk=0.26, belly=0.9, head=0.17, neck=0.1, hunch=0.22,
                      arm_len=0.9, limb=0.08, hand=0.08, foot=0.15)
    hc, hr = K['head'], K['head_r']
    P = [(prim(sc, 'cone', 'snout', stone, loc=tuple(hc + V(0, -hr * 0.9, -hr * 0.2)), rot=(R(95), 0, 0), radius1=hr * 0.5, radius2=hr * 0.25, depth=hr * 0.8), 'head'),
         (prim(sc, 'cone', 'tail', stone, loc=tuple(K['pelvis'] + V(0, 0.35, -0.1)), rot=(R(-60), 0, 0), radius1=0.06, radius2=0.0, depth=0.7, vertices=8), 'hips')]
    for sx in (1, -1):
        P.append((prim(sc, 'cone', f'horn{sx}', horn, loc=tuple(hc + V(sx * hr * 0.55, hr * 0.2, hr * 0.8)), rot=(R(-40), R(25 * sx), 0), radius1=hr * 0.2, radius2=0, depth=hr * 1.3, vertices=8), 'head'))
        P.append((prim(sc, 'cone', f'ear{sx}', stone, loc=tuple(hc + V(sx * hr * 0.9, 0, hr * 0.2)), rot=(0, R(80 * sx), 0), radius1=hr * 0.2, radius2=0, depth=hr * 0.6, vertices=4), 'head'))
    for ob, b in P: attach(ob, arm, b)
    glow_eyes(sc, arm, K, hexrgb('#ff7040'), spread=0.45, size=0.03, fwd=0.8, up=0.2)
    arm.location.z = alt
    c = K['chest']
    pivs = [wing(sc, f'wing{s}', wingm, 'bat', 1.1, 0.75, s, (sx * 0.2, c.y + 0.12, c.z + 0.1), arm, droop=0.1) for s, sx in (('L', 1), ('R', -1))]
    def anim(p, f):
        pose(arm, {'spine': (R(20), 0, 0), 'thigh.L': (R(-50), 0, 0), 'thigh.R': (R(-50), 0, 0), 'shin.L': (R(80), 0, 0), 'shin.R': (R(80), 0, 0),
                   'upperarm.L': (R(-40), 0, R(10)), 'upperarm.R': (R(-40), 0, R(-10)), 'forearm.L': (R(-50), 0, 0), 'forearm.R': (R(-50), 0, 0)})
        flap(pivs, p, amp=0.8, base=0.15)
    return arm, anim, (lambda p: math.sin(p * math.tau) * 0.07)


def wraith(sc):
    robe = toon('wr_robe', c255(44, 52, 76), mottle=0.35, form=0.5, rim=0.45)
    inner = toon('wr_inner', c255(12, 14, 22), rim=0)
    bone = toon('wr_bone', c255(176, 196, 206), rim=0.4)
    steel = toon('wr_steel', c255(150, 196, 214), rim=0.6)
    glow = toon('wr_glow', None, emit=hexrgb('#7ef2ff'), emit_strength=2.8)
    alt = 0.35
    arm = build_armature(sc, 'Wr', [('body', (0, 0, alt), (0, -0.05, alt + 0.9), None), ('head', (0, -0.05, alt + 0.9), (0, -0.12, alt + 1.25), 'body'),
                                    ('arm.L', (0.22, -0.05, alt + 0.78), (0.3, -0.45, alt + 0.6), 'body'), ('arm.R', (-0.22, -0.05, alt + 0.78), (-0.3, -0.45, alt + 0.6), 'body')])
    P = [(prim(sc, 'cone', 'robe', robe, loc=(0, 0.05, alt + 0.4), radius1=0.34, radius2=0.18, depth=1.1, vertices=10), 'body'),
         (prim(sc, 'sphere', 'hood', robe, loc=(0, -0.05, alt + 1.05), scale=(0.2, 0.22, 0.22)), 'head'),
         (prim(sc, 'sphere', 'void', inner, loc=(0, -0.2, alt + 1.02), scale=(0.13, 0.08, 0.14)), 'head')]
    # tattered hem: wisps trailing behind and below
    for k in range(7):
        a = R(-90 + k * 30)
        P.append((prim(sc, 'cone', f'wisp{k}', robe, loc=(math.sin(a) * 0.25, 0.1 + math.cos(a) * 0.15, alt - 0.25), rot=(R(200 + (k % 2) * 15), 0, 0), radius1=0.09, radius2=0.0, depth=0.45, vertices=5), 'body'))
    for s, sx in (('L', 1), ('R', -1)):
        P.append((prim(sc, 'cone', f'sleeve{s}', robe, loc=(sx * 0.27, -0.25, alt + 0.7), rot=(R(-60), 0, 0), radius1=0.06, radius2=0.1, depth=0.4, vertices=8), f'arm.{s}'))
        P.append((prim(sc, 'sphere', f'hand{s}', bone, loc=(sx * 0.3, -0.48, alt + 0.6), scale=(0.05, 0.06, 0.05)), f'arm.{s}'))
    for ex in (-1, 1):
        P.append((prim(sc, 'sphere', f'eye{ex}', glow, loc=(ex * 0.05, -0.27, alt + 1.04), scale=(0.028, 0.012, 0.02)), 'head'))
    # scythe
    P.append((prim(sc, 'cyl', 'snath', toon('wr_wood', c255(40, 34, 38)), loc=(-0.3, -0.5, alt + 0.75), rot=(R(-15), 0, 0), radius=0.018, depth=1.5), 'arm.R'))
    bl = poly_obj(sc, 'scythe', steel, [(0, 0), (0.1, 0.05), (0.55, -0.05), (0.75, -0.25), (0.45, -0.12), (0.05, -0.06)], thick=0.02)
    bl.location = (-0.3, -0.35, alt + 1.47); bl.rotation_euler = (0, 0, R(-90)); P.append((bl, 'arm.R'))
    for ob, b in P: attach(ob, arm, b)
    def anim(p, f):
        s = math.sin(p * math.tau)
        pose(arm, {'body': (R(18) + s * 0.05, 0, s * 0.08), 'head': (R(-10), 0, 0), 'arm.L': (s * 0.2, 0, 0), 'arm.R': (-s * 0.1, 0, 0)})
    return arm, anim, (lambda p: math.sin(p * math.tau) * 0.08)


def wyrm(sc):
    scale = toon('wy_scale', c255(158, 88, 50), mottle=0.45, form=0.35, rim=0.35)
    belly = toon('wy_belly', c255(214, 170, 96), form=0.2)
    wingm = toon('wy_wing', c255(170, 96, 52), mottle=0.3, rim=0.35)
    horn = toon('wy_horn', c255(236, 222, 186), rim=0.4)
    alt = 0.7
    # spine chain: tail -> hips -> chest -> neck -> head, gently S-curved
    pts = [V(0, 1.6, alt - 0.15), V(0, 1.05, alt - 0.02), V(0, 0.5, alt + 0.05), V(0, 0.0, alt + 0.08), V(0, -0.45, alt + 0.1),
           V(0, -0.8, alt + 0.35), V(0, -1.05, alt + 0.6), V(0, -1.35, alt + 0.65)]
    rad = [0.05, 0.14, 0.3, 0.4, 0.34, 0.2, 0.17, 0.27]
    names = ['tail2', 'tail1', 'hips', 'chest', 'neck0', 'neck1', 'neck2', 'head']
    bones = []
    for i in range(len(pts) - 1):
        bones.append((names[i], tuple(pts[i]), tuple(pts[i + 1]), names[i - 1] if i else None))
    arm = build_armature(sc, 'Wy', bones)
    J = [(tuple(p), r) for p, r in zip(pts, rad)]
    E = [(i, i + 1) for i in range(len(pts) - 1)]
    for s, sx in (('L', 1), ('R', -1)):
        J += [((sx * 0.2, 0.5, alt - 0.1), 0.09), ((sx * 0.26, 0.45, alt - 0.4), 0.07), ((sx * 0.24, 0.35, alt - 0.55), 0.06)]
        n = len(J); E += [(2, n - 3), (n - 3, n - 2), (n - 2, n - 1)]
        J += [((sx * 0.22, -0.3, alt - 0.05), 0.08), ((sx * 0.28, -0.4, alt - 0.3), 0.06)]
        n = len(J); E += [(4, n - 2), (n - 2, n - 1)]
    body = skin_body(sc, 'WyBody', J, E, scale, root=3)
    bind(body, arm)
    hp = pts[-1]
    P = [(prim(sc, 'cone', 'jaw', scale, loc=tuple(hp + V(0, -0.28, -0.06)), rot=(R(95), 0, 0), radius1=0.18, radius2=0.07, depth=0.45), 'head'),
         (prim(sc, 'sphere', 'bellyplate', belly, loc=(0, -0.1, alt - 0.14), scale=(0.2, 0.45, 0.12)), 'chest')]
    for ex in (-1, 1):
        P.append((prim(sc, 'cone', f'horn{ex}', horn, loc=tuple(hp + V(ex * 0.13, 0.14, 0.18)), rot=(R(-60), R(22 * ex), 0), radius1=0.06, radius2=0, depth=0.45, vertices=8), 'head'))
    for k in range(5):
        P.append((prim(sc, 'cone', f'spine{k}', horn, loc=(0, 0.9 - k * 0.35, alt + 0.2 + 0.05 * (k > 2)), rot=(R(-20), 0, 0), radius1=0.05, radius2=0, depth=0.16, vertices=6), names[max(0, 3 - k // 2)] if k < 4 else 'chest'))
    for ob, b in P: attach(ob, arm, b)
    em = toon('wy_eye', None, emit=hexrgb('#ffe14a'), emit_strength=2.6)
    for ex in (-1, 1):
        e = prim(sc, 'sphere', f'eye{ex}', em, loc=tuple(hp + V(ex * 0.15, -0.1, 0.08)), scale=(0.04, 0.025, 0.028)); attach(e, arm, 'head')
    pivs = [wing(sc, f'wing{s}', wingm, 'bat', 1.75, 1.15, s, (sx * 0.3, -0.1, alt + 0.2), arm, droop=0.05) for s, sx in (('L', 1), ('R', -1))]
    def anim(p, f):
        s = math.sin(p * math.tau)
        pose(arm, {'tail1': (0, 0, s * 0.2), 'tail2': (0, 0, s * 0.3), 'neck1': (-s * 0.06, 0, 0), 'head': (s * 0.08, 0, 0)})
        flap(pivs, p, amp=0.7, base=0.15)
    return arm, anim, (lambda p: math.sin(p * math.tau) * 0.1)


CREATURES = {
    'kobold': (kobold, 68), 'ghoul': (ghoul, 74), 'grunt': (grunt, 80), 'harpy': (harpy, 92),
    'gargoyle': (gargoyle, 100), 'ogre': (ogre, 100), 'wraith': (wraith, 84), 'khan': (khan, 126),
    'wyrm': (wyrm, 146), 'titan': (titan, 144), 'basci': (basci, 78), 'umay': (umay, 76),
    'yelbegen': (yelbegen, 118), 'yelbegenYavru': (yelbegenYavru, 62),
}
# ceiling on the fitted scale, for creatures whose cell is roomier than they should look
MAX_PPM = {'yelbegenYavru': 36
}
