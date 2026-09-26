# Alp, the hero: a steppe warrior. 8 walk frames + 4 axe-swing frames per direction.
import math
from mathutils import Vector

R = math.radians
def V(*a): return Vector(a)


def hero(sc):
    skin = toon('al_skin', c255(206, 158, 120), form=0.2)
    steel = toon('al_steel', c255(150, 156, 170), rim=0.55, mottle=0.1, form=0.25)
    lamel = toon('al_lamel', c255(46, 104, 124), mottle=0.25, rim=0.35, form=0.3)
    leather = toon('al_leather', c255(104, 70, 44), mottle=0.25)
    cape = toon('al_cape', c255(34, 58, 120), mottle=0.2, form=0.45)
    gold = toon('al_gold', c255(222, 172, 84), rim=0.5)
    fur = toon('al_fur', c255(92, 72, 56), mottle=0.45)
    wood = toon('al_wood', c255(116, 78, 46))
    hair = toon('al_hair', c255(40, 28, 22), rim=0.2)
    glow = toon('al_glow', None, emit=(0.44, 0.85, 0.9), emit_strength=2.2)
    arm, K = humanoid(sc, 'Al', lamel, h=1.85, leg=0.47, bulk=0.27, belly=0.95, head=0.17, neck=0.08, hunch=0.03,
                      arm_len=1.0, limb=0.09, hand=0.075, foot=0.17, shoulder=1.12)
    hc, hr = K['head'], K['head_r']
    trousers = toon('al_trousers', c255(70, 56, 48), mottle=0.2)
    def pick(c):
        if (c - hc).length < hr * 1.35: return skin
        if min((c - K['hand.L']).length, (c - K['hand.R']).length) < 0.12: return leather
        if c.z < K['ankle.L'].z + 0.2: return leather
        if c.z < K['pelvis'].z * 0.92: return trousers
        return None
    paint(K['body'], pick)
    P = []
    # face, beard, spiked helmet with a plume and a mail aventail
    P.append((prim(sc, 'sphere', 'face', skin, loc=tuple(hc + V(0, -hr * 0.35, -hr * 0.1)), scale=(hr * 0.78, hr * 0.7, hr * 0.8)), 'head'))
    P.append((prim(sc, 'cone', 'beard', hair, loc=tuple(hc + V(0, -hr * 0.62, -hr * 0.7)), rot=(R(180 - 15), 0, 0), radius1=hr * 0.5, radius2=hr * 0.1, depth=hr * 0.9, vertices=10), 'head'))
    P.append((prim(sc, 'cone', 'helm', steel, loc=tuple(hc + V(0, 0, hr * 0.62)), radius1=hr * 1.12, radius2=0.0, depth=hr * 1.5, vertices=16), 'head'))
    P.append((prim(sc, 'torus', 'helmrim', gold, loc=tuple(hc + V(0, 0, hr * 0.02)), major_radius=hr * 1.08, minor_radius=0.022), 'head'))
    P.append((prim(sc, 'cone', 'plume', toon('al_plume', c255(176, 40, 36), form=0.1), loc=tuple(hc + V(0, hr * 0.35, hr * 1.35)), rot=(R(-130), 0, 0), radius1=0.04, radius2=0.005, depth=0.42, vertices=6), 'head'))
    P.append((prim(sc, 'cone', 'aventail', steel, loc=tuple(hc + V(0, hr * 0.25, -hr * 0.35)), radius1=hr * 1.15, radius2=hr * 0.95, depth=hr * 0.8, vertices=14), 'head'))
    P.append((prim(sc, 'cube', 'nasal', steel, loc=tuple(hc + V(0, -hr * 1.0, hr * 0.1)), scale=(0.018, 0.02, hr * 0.42)), 'head'))
    # fur collar, belt, lamellar skirt
    P.append((prim(sc, 'torus', 'collar', fur, loc=tuple(K['neck'] + V(0, 0.05, -0.07)), scale=(1, 0.9, 1.3), major_radius=0.16, minor_radius=0.05), 'chest'))
    P.append((prim(sc, 'cyl', 'belt', leather, loc=tuple(K['pelvis'] + V(0, 0, 0.1)), scale=(1, 0.85, 1), radius=0.25, depth=0.09), 'hips'))
    P.append((prim(sc, 'cyl', 'buckle', gold, loc=tuple(K['pelvis'] + V(0, -0.22, 0.1)), rot=(R(90), 0, 0), radius=0.045, depth=0.03), 'hips'))
    P.append((prim(sc, 'cone', 'skirt', lamel, loc=tuple(K['pelvis'] + V(0, 0, -0.1)), radius1=0.33, radius2=0.25, depth=0.34, vertices=10), 'hips'))
    for s, sx in (('L', 1), ('R', -1)):
        P.append((prim(sc, 'sphere', f'pauld{s}', steel, loc=tuple(K[f'sh.{s}'] + V(sx * 0.04, 0, 0.05)), scale=(0.13, 0.14, 0.09)), f'upperarm.{s}'))
        P.append((prim(sc, 'cyl', f'boot{s}', leather, loc=tuple(K[f'ankle.{s}'] + V(0, 0, 0.1)), radius=0.085, depth=0.26), f'shin.{s}'))
        P.append((prim(sc, 'cyl', f'bracer{s}', leather, loc=tuple((K[f'el.{s}'] * 0.4 + K[f'wr.{s}'] * 0.6)), rot=(R(-20), 0, 0), radius=0.07, depth=0.18), f'forearm.{s}'))
    # cape from the shoulders
    c = K['chest']
    cp = poly_obj(sc, 'cape', cape, [(-0.3, 0), (0.3, 0), (0.42, -1.1), (0.15, -1.05), (0, -1.12), (-0.15, -1.05), (-0.42, -1.1)], thick=0.03)
    cp.location = (0, c.y + 0.24, c.z + 0.16); cp.rotation_euler = (R(10), 0, 0); P.append((cp, 'chest'))
    # round shield on the left forearm
    wl = K['wr.L']
    P.append((prim(sc, 'cyl', 'shield', wood, loc=tuple(wl + V(0.08, -0.02, 0.05)), rot=(0, R(90), 0), radius=0.3, depth=0.05, vertices=20), 'forearm.L'))
    P.append((prim(sc, 'torus', 'shieldrim', steel, loc=tuple(wl + V(0.105, -0.02, 0.05)), rot=(0, R(90), 0), major_radius=0.3, minor_radius=0.02), 'forearm.L'))
    P.append((prim(sc, 'sphere', 'boss', gold, loc=tuple(wl + V(0.13, -0.02, 0.05)), scale=(0.04, 0.08, 0.08)), 'forearm.L'))
    # the axe: haft up out of the right fist, glowing bearded blade
    hR = K['hand.R']
    P.append((prim(sc, 'cyl', 'haft', wood, loc=tuple(hR + V(0, 0, 0.22)), radius=0.02, depth=0.85), 'hand.R'))
    blade = poly_obj(sc, 'axe', steel, [(0, 0.1), (0.2, 0.22), (0.3, 0.08), (0.28, -0.14), (0.12, -0.2), (0.04, -0.06)], thick=0.028)
    blade.location = tuple(hR + V(0, -0.02, 0.56)); blade.rotation_euler = (0, 0, R(-90)); P.append((blade, 'hand.R'))
    edge = poly_obj(sc, 'axeedge', glow, [(0.27, 0.1), (0.31, 0.08), (0.29, -0.15), (0.25, -0.12)], thick=0.034)
    edge.location = tuple(hR + V(0, -0.02, 0.56)); edge.rotation_euler = (0, 0, R(-90)); P.append((edge, 'hand.R'))
    for ob, b in P: attach(ob, arm, b)

    def anim(p, f):
        if f < 8:
            walk(arm, (f % 8) / 8, stride=0.55, arms=0.3, lean=0.04,
                 armL=lambda s, c: {'upperarm.L': (-0.35 + s * 0.1, 0, 0.2), 'forearm.L': (-0.9, 0, 0)},
                 armR=lambda s, c: {'upperarm.R': (s * 0.35, 0, -0.08), 'forearm.R': (-0.35, 0, 0), 'hand.R': (-0.6, 0, 0)})
            return
        # swing: wind-up, top, strike, follow-through
        k = f - 8
        up = [-2.7, -2.9, -1.0, 0.1][k]; fore = [-1.2, -0.5, -0.1, -0.2][k]; hand = [-0.4, 0.4, -0.2, -0.6][k]
        twist = [0.35, 0.25, -0.25, -0.35][k]; lean = [-0.05, 0.0, 0.15, 0.2][k]
        pose(arm, {'upperarm.R': (up, 0, -0.1), 'forearm.R': (fore, 0, 0), 'hand.R': (hand, 0, 0),
                   'upperarm.L': (-0.5, 0, 0.25), 'forearm.L': (-0.9, 0, 0),
                   'chest': (0.05, 0, twist), 'spine': (lean, 0, 0),
                   'thigh.L': (0.35, 0, 0), 'thigh.R': (-0.25, 0, 0), 'shin.R': (-0.3, 0, 0)})
    return arm, anim, None
