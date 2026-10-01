"""Original Project Broom tentacle horror: a towering braided column of tentacles.

Brogue facts (pinned Globals.c): "This seething, towering nightmare of fleshy
tentacles slinks through the bowels of the world. The tentacle horror's
incredible strength and regeneration make $HIMHER one of the most fearsome
creatures of the dungeon." It is large, bleeds purple (DF_PURPLE_BLOOD) and its
verbs are "slaps", "batters", "crushes", "sucking on" and "Consuming".

Art interpretation (not source facts): four thick tentacles braided into a
twisting trunk, a knotted fleshy crown with a round sucking maw ringed with
pale hooks (the "sucking on" verb; no eyes), six crown tentacles arching over,
four heavy mid-trunk arms, seven splayed root tentacles it slinks on, four thin
tendrils, and pale sucker rows. The purple glyph and blood are identity cues,
not literal paint rules; regeneration and strength are Brogue-owned and have no
visual effect here. There is no collision, AI, RNG or autonomous grabbing.

Geometry, rig and posing reuse the kraken module's tentacle toolkit read-only.
"""
import hashlib
import json
import math
from . import connected_skin
from .rat import ROOT, Part, ellipsoid, tube
from .rat import add, sub, mul  # noqa: F401 - blender_skeletal reads rigdata.sub/add
from .skeletal import assemble, sample_clips
from .kraken_animation import (osc, Limb, Chains, cup_part, floor_spiral, relative, blend_shapes, resample, wiggle,
                               quantize, r6, dot, norm, crs, unit, lerp, clamp, smooth, bell, iqm_bytes, TAU)

SKIN = 'graphics/BRGTHOR.png'
MODEL = 'models/monsters/48_tentacle_horror.iqm'
SKIN_VOXEL_SIZE = .24
SKIN_FACE_BUDGET = 12000


def CONNECTED_SKIN(name):
    return name.startswith('skin_')


TRUNK_TOP = 48.
TRUNK_Z = (2., 11.5, 21., 30.5, 40., 48.)
HEAD_C = (1., 0., 56.5)
HEAD_R = (11.5, 11., 10.)
MAW_AXIS = unit((1., 0., .15))
MAW = add(HEAD_C, mul(MAW_AXIS, 11.))
MAW_E1 = unit(crs(MAW_AXIS, (0, 0, 1)))
MAW_E2 = crs(MAW_E1, MAW_AXIS)


def polar(angle_deg, r, z, twist=0.):
    a = math.radians(angle_deg+twist)
    return (r*math.cos(a), r*math.sin(a), z)


def strand_controls(k):
    out = []
    for i in range(9):
        z = 2.6+(TRUNK_TOP+3-2.6)*i/8
        f = (z-2.6)/TRUNK_TOP
        R = 6.2-3.2*f+2.2*f*f
        rs = 5.3-2.0*f+.9*f*f
        angle = 20+90*k+200*f
        c = polar(angle, R, z)
        out.append((*r6(c), round(c[0], 6), round(c[1], 6), 0., round(rs, 6)))
    return out


def radial_limb(angle, pts, r0, tip, power=1.2, refs=None, twist_per=0.):
    """pts: (radius, z, twist-degrees) around the trunk axis; returns controls."""
    xyz = [polar(angle, r, z, tw) for r, z, tw in pts]
    arcs = [0.]
    for a, b in zip(xyz, xyz[1:]):
        arcs.append(arcs[-1]+norm(sub(b, a)))
    out = []
    for i, (p, arc) in enumerate(zip(xyz, arcs)):
        s = arc/arcs[-1]
        r = tip+(r0-tip)*(1-s)**power
        ref = refs[i] if refs else (0, 0, -1)
        # refs are (outward, tangential, up) in the limb's radial frame
        a = math.radians(angle+pts[i][2])
        out_dir = (math.cos(a), math.sin(a), 0.)
        tan_dir = (-math.sin(a), math.cos(a), 0.)
        v = add(add(mul(out_dir, ref[0]), mul(tan_dir, ref[1])), (0, 0, ref[2]))
        out.append((*r6(p), *r6(v), round(r, 6)))
    return out, arcs[1]


def hidden_floor(centre, n, row):
    return not (n[2] < -.45 and centre[2] < row['r']+2.4)


CROWN_SPECS = (  # (angle around the trunk, root radius, (radial, z, twist) path)
    (22, 3.4, [(3, 62, 0), (6, 65, 0), (9.5, 71, 5), (13, 74, 15), (17, 72.5, 25), (19.5, 68, 32), (19, 63.5, 30),
               (17, 62, 22)]),
    (-35, 3.8, [(3, 62, 0), (6.5, 64.5, 0), (10, 68.5, -4), (12.5, 70, -12), (14, 67, -20), (13, 64, -26)]),
    (95, 3.2, [(3, 62, 0), (6, 65, 0), (8, 71.5, 6), (7, 76.5, 14), (9, 79.5, 22), (12.5, 80.5, 28), (15.5, 79, 26),
               (16, 75.5, 20)]),
    (150, 3.0, [(3, 62, 0), (7, 64, 0), (12, 65, 4), (16.5, 62, 8), (19, 56, 12), (19.5, 49, 14), (18, 43, 10),
                (15.5, 41, 4)]),
    (205, 2.8, [(3, 62, 0), (6.5, 65, 0), (9.5, 70, -6), (9, 74.5, -14), (12, 77.5, -20), (16.5, 77, -22), (18.5, 73.5, -18),
                (17, 70.5, -12)]),
    (5, 3.0, [(3, 62, 0), (6.5, 66, 0), (10, 70.5, 3), (14, 72, 6), (17.5, 70, 10), (19, 66, 14), (18, 62.5, 18),
              (16, 61.5, 24)]),
    (250, 2.2, [(3, 62, 0), (7, 64, 0), (12, 66, -5), (17, 65, -10), (21, 61, -14), (23, 55, -16), (22.5, 50, -14),
                (20, 48, -8)]),
    (300, 3.6, [(3, 62, 0), (6.5, 65, 0), (10, 69, 4), (13, 71, 8), (15.5, 69, 14), (16, 65, 18), (14, 62, 20)]),
    (-8, 1.9, [(3, 62, 0), (6, 64.5, 0), (9.5, 67.5, -6), (13, 69, -14), (16, 67, -22), (17, 63.5, -30), (15.5, 61, -34)]),
)


def make_limbs():
    limbs = []
    strands = []
    for k in range(4):
        strands.append(Limb(f'trunk_{k}', strand_controls(k), bones=2, sides=26, samples=5, exit=0.,
                            parent='trunk_0', flatten=0., cup_span=(2, 2)))
    # An irregular writhing crown: tentacles of clearly varied length, thickness
    # and curl. Some writhe forward over the maw, some droop, one towers.
    for k, (angle, r0, pts) in enumerate(CROWN_SPECS):
        refs = [(0, 0, -1), (0, 0, -1)]+[(-.3, 0, -1)]*(len(pts)-4)+[(-1, 0, .2), (-.5, 0, .8)]
        controls, exit_arc = radial_limb(angle, pts, r0, .45, 1.25, refs)
        limbs.append(Limb(f'crown_{k}', controls, bones=8, sides=16 if r0 > 2.5 else 12, samples=6, exit=exit_arc,
                          parent='head', cup_rows=2, cup_scale=.32, cup_spacing=1.5))
    for k, angle in enumerate((45, 135, 225, 315)):
        pts = [(3, 35, 0), (7.5, 37, 0), (13, 40, 3), (19, 37.5, 6), (23, 31, 8), (24.5, 24, 8), (23, 18, 5),
               (20, 15, 0), (18.5, 17.5, -4)]
        refs = [(0, 0, -1), (0, 0, -1), (-.2, 0, -1), (-.6, 0, -.8), (-.9, 0, -.3), (-1, 0, 0), (-1, 0, .3),
                (-.5, 0, .9), (.3, 0, 1)]
        controls, exit_arc = radial_limb(angle, pts, 3.9, .5, 1.1, refs)
        limbs.append(Limb(f'arm_{k}', controls, bones=9, sides=18, samples=6, exit=exit_arc, parent='trunk_3',
                          cup_rows=2, cup_scale=.32, cup_spacing=1.5))
    for k in range(7):
        angle = 25+k*360/7
        pts = [(2.5, 6, 0), (8, 4.6, 0), (13, 3.9, 2), (18.5, 3.6, 5), (23.5, 3.6, 7), (27, 4.6, 7), (27.5, 7.8, 3),
               (25.5, 10.2, -3), (23.5, 9, -7)]
        refs = [(0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1), (-.2, 0, -1), (-1, 0, -.2),
                (-.8, 0, .7), (0, 0, 1)]
        controls, exit_arc = radial_limb(angle, pts, 4.2, .5, 1.1, refs)
        limbs.append(Limb(f'root_{k}', controls, bones=7, sides=18, samples=6, exit=exit_arc, parent='trunk_0',
                          cup_rows=2, cup_scale=.32, cup_filter=hidden_floor, cup_spacing=1.5))
    # Drooping curls hang from the upper trunk, thickening the writhing mass.
    for k, angle in enumerate((0, 90, 180, 270)):
        pts = [(2.5, 43, 0), (8, 45, 0), (13.5, 46.5, 5), (18.5, 43, 10), (20.5, 37.5, 14), (20, 32.5, 16), (18, 29.5, 12),
               (16.5, 31.5, 6)]
        refs = [(0, 0, -1), (0, 0, -1), (-.2, 0, -1), (-.6, 0, -.8), (-1, 0, -.2), (-1, 0, .2), (-.6, 0, .8), (0, 0, 1)]
        controls, exit_arc = radial_limb(angle, pts, 2.6, .45, 1.1, refs)
        limbs.append(Limb(f'hang_{k}', controls, bones=7, sides=14, samples=6, exit=exit_arc, parent='trunk_4',
                          cup_rows=2, cup_scale=.34, cup_spacing=1.5))
    # Thin tendrils sprout between the heavy arms and curl sideways, clear of them.
    for k, (angle, z) in enumerate(((0, 18), (90, 16), (180, 20), (270, 17))):
        pts = [(2.5, z, 0), (7.5, z+1, 0), (12, z+3.5, 4), (16, z+3, 9), (18.5, z-.5, 14), (17.5, z-3.5, 18),
               (15, z-2.5, 20)]
        refs = [(0, 0, -1), (0, 0, -1), (0, -.3, -1), (-.3, -.6, -.6), (-.6, -.8, 0), (-.5, -.6, .6), (0, 0, 1)]
        controls, exit_arc = radial_limb(angle, pts, 1.7, .45, 1.0, refs)
        limbs.append(Limb(f'tendril_{k}', controls, bones=6, sides=12, samples=6, exit=exit_arc, parent='trunk_2',
                          cup_rows=1, cup_scale=.4, cup_spacing=1.4))
    return strands, limbs


STRANDS, LIMBS = make_limbs()
TRUNK = [f'spine_{k}' for k in range(6)]
SPECS = [('root', None, (0., 0., 0.))]
for _k, _z in enumerate(TRUNK_Z):
    SPECS.append((TRUNK[_k], 'root' if _k == 0 else TRUNK[_k-1], (0., 0., _z)))
SPECS.append(('head', TRUNK[-1], (1., 0., 52.)))
SPECS.append(('maw', 'head', r6(MAW)))
_PARENT = {'trunk_0': TRUNK[0], 'trunk_2': TRUNK[2], 'trunk_3': TRUNK[3], 'trunk_4': TRUNK[4], 'head': 'head'}
for _limb in LIMBS:
    _limb.parent = _PARENT[_limb.parent]
    for _k, (_n, _p) in enumerate(zip(_limb.bone_names, _limb.bone_points)):
        SPECS.append((_n, _limb.parent if _k == 0 else _limb.bone_names[_k-1], _p))
KIT = Chains(SPECS, LIMBS)
RIG, BONES, REST, IDS = KIT.rig, KIT.bones, KIT.rest, KIT.ids
BY_NAME = {l.name: l for l in LIMBS}
TRUNK_IDS = [IDS[b] for b in TRUNK]
CLIPS = [('idle', 48, 20, True), ('slink', 32, 35, True), ('batter', 27, 35, False),
         ('crush', 31, 35, False), ('flinch', 15, 35, False), ('collapse', 41, 35, False)]


def accessory_strip(y):
    return lambda u: (round(.02+.96*clamp(u), 6), round(1-y/1024, 6))


def maw_point(a, radius, depth):
    d = add(mul(MAW_E1, math.cos(a)), mul(MAW_E2, math.sin(a)))
    return add(MAW, add(mul(d, radius), mul(MAW_AXIS, depth)))


def build_maw():
    parts = []
    throat = Part('maw_throat')
    S = 28
    throat.vertices.append(r6(add(MAW, mul(MAW_AXIS, .15))))
    throat.uv.append((256/1024, 1-256/1024))
    for j in range(S):
        a = TAU*j/S
        throat.vertices.append(r6(maw_point(a, 4.4, .75)))
        throat.uv.append((round((256+238*math.cos(a))/1024, 6), round(1-(256-238*math.sin(a))/1024, 6)))
    for j in range(S):
        throat.faces.append((0, 1+j, 1+(j+1) % S))
    parts.append(throat)
    strip = accessory_strip(680)
    for ring, (count, radius, depth, length) in enumerate(((14, 3.7, .9, 1.9), (9, 2.3, .6, 1.4))):
        for j in range(count):
            a = TAU*(j+.5*ring)/count
            base = maw_point(a, radius, depth)
            inward = unit(sub(add(MAW, mul(MAW_AXIS, depth+.6)), base))
            hook = unit(add(mul(inward, 1.), mul(MAW_AXIS, .55)))
            tip = add(base, mul(hook, length))
            mid = add(base, add(mul(hook, length*.55), mul(MAW_AXIS, .25)))
            t = tube(f'tooth_{ring}_{j}', [(*base, .42 if ring == 0 else .32), (*mid, .26 if ring == 0 else .2), (*tip, .02)],
                     'fur', 8, 2)
            t.uv = [strip(norm(sub(v, base))/length) for v in t.vertices]
            t.vertices = [r6(v) for v in t.vertices]
            parts.append(t)
    return parts


def build_parts():
    parts = []
    for strand in STRANDS:
        parts.append(strand.part())
    parts.append(ellipsoid('skin_core', (0, 0, 25), (5.2, 5.2, 23.5), 'fur', 28, 20))
    parts.append(ellipsoid('skin_head', HEAD_C, HEAD_R, 'fur', 40, 22))
    for k, (c, r) in enumerate((((-4.5, 6, 62), (7, 6.5, 6.5)), ((-3.5, -7, 54), (6.5, 6, 6)),
                                ((3.5, 0, 48.5), (8, 8.5, 6)), ((-6, -1, 58), (6, 6.5, 7)))):
        parts.append(ellipsoid(f'skin_lump_{k}', c, r, 'fur', 24, 14))
    for k in range(10):
        a = TAU*k/10
        parts.append(ellipsoid(f'skin_lip_{k}', maw_point(a, 4.5, .45), (1.8, 1.8, 1.8), 'fur', 14, 8))
    for limb in LIMBS:
        parts.append(limb.part())
    for p in parts:
        p.vertices = [r6(v) for v in p.vertices]
        p.uv = [(round(u, 6), round(v, 6)) for u, v in p.uv]
    parts += build_maw()
    strip = accessory_strip(600)
    for limb in LIMBS:
        for k, (centre, n, tangent, size, arc) in enumerate(limb.cups()):
            cup = cup_part(f'cup_{limb.name}_{k}', centre, n, tangent, size, strip)
            cup.anchor = centre
            cup.bones = limb.bones_near(arc)
            parts.append(cup)
    return parts


def trunk_weights(v):
    return quantize(RIG.chain_weights(v, TRUNK_IDS+[IDS['head']]))


def weights(part, v, uv):
    n = part.name
    if n.startswith('skin_trunk_') or n == 'skin_core':
        return trunk_weights(v)
    if n == 'skin_lump_2':
        return quantize(RIG.chain_weights(v, TRUNK_IDS[-2:]+[IDS['head']]))
    if n.startswith('skin_') and n[5:] in BY_NAME:
        limb = BY_NAME[n[5:]]
        raw = RIG.chain_weights(v, limb.ids)
        blend = smooth((uv[0]*limb.length-(limb.exit-1.6))/2.4)
        return quantize([(IDS[limb.parent], 1-blend)]+[(b, w*blend) for b, w in raw])
    if n.startswith('cup_'):
        limb = BY_NAME[n[4:].rsplit('_', 1)[0]]
        return quantize(RIG.chain_weights(v, limb.ids))
    if n.startswith(('tooth_', 'maw_')):
        return [(IDS['maw'], 1)]
    return [(IDS['head'], 1)]


_GEOMETRY = {}


def skin_parts():
    from .kraken_animation import attach_cups
    parts = connected_skin.attach('tentacle_horror', build_parts(), weights)
    parts[0].skin_weights = [[tuple(x) for x in w] for w in parts[0].skin_weights]
    attach_cups(parts, [b[0] for b in BONES])
    return parts


def geometry():
    if 'g' not in _GEOMETRY:
        from . import tentacle_horror_materials as materials
        _GEOMETRY['g'] = assemble(materials.connected_atlas(skin_parts()), weights)
    return _GEOMETRY['g']


# ------------------------------------------------------------------ poses
def side_of(limb):
    """Angle (degrees) of the limb's first control around the trunk."""
    p = limb.rows[-1]['c'] if limb.name.startswith('root') else limb.bone_points[1]
    return math.degrees(math.atan2(p[1], p[0]))


def shapes():
    if hasattr(shapes, 'cache'):
        return shapes.cache
    S = {}
    for limb in LIMBS:
        b0 = limb.bone_points[0]
        d = {'rest': list(limb.bone_points)}
        y = 1 if b0[1] >= 0 else -1
        if limb.name in ('arm_0', 'arm_3'):
            # Front arms: overhead wind-up, a head-height hammer (batter) and a
            # low wrap round a target on the floor (crush).
            d['raise'] = resample(limb, [b0, (6, 7*y, 44.0), (7, 9*y, 53.0), (4, 10*y, 61.0), (-1, 10*y, 67.0), (-6, 8*y, 70.0),
                                         (-9, 5*y, 68.0)])
            d['blow'] = resample(limb, [b0, (11, 8*y, 42.0), (18, 10*y, 42.0), (24.5, 10.5*y, 37.0), (27.5, 9*y, 29.0),
                                        (28.5, 7*y, 20.0), (27.5, 5*y, 11.0), (25, 3.5*y, 5.0)])
            d['wrap'] = resample(limb, [b0, (11, 9*y, 32), (17.5, 12*y, 26), (23, 12*y, 19), (27, 9*y, 12.5), (27.5, 4*y, 8),
                                        (25.5, -1*y, 6), (22, -2.5*y, 6.5), (20, 0, 9)])
        if limb.name in ('arm_1', 'arm_2'):
            d['raise'] = resample(limb, [b0, (-3, 13*y, 40), (-4, 18*y, 47), (-2, 21*y, 53), (2, 21*y, 57), (6, 19*y, 58)])
            d['blow'] = resample(limb, [b0, (0, 16*y, 36), (8, 21*y, 33), (16, 21*y, 28), (23, 17*y, 22), (27, 12*y, 17),
                                        (28, 7*y, 14)])
            d['wrap'] = resample(limb, [b0, (2, 16*y, 29), (10, 19*y, 22), (17.5, 17*y, 15), (23.5, 12*y, 10), (26, 6*y, 7),
                                        (25, 0, 6), (22, -2*y, 7)])
        if limb.name.startswith('crown'):
            # Batter: the whole crown streams forward at head height. Crush:
            # it pours forward and down over the target near the floor.
            yk = 13*math.sin(math.radians(side_of(limb)))
            up = add(b0, (1, 0, 6))
            d['lash'] = resample(limb, [b0, up, (10, yk, 71), (18, .9*yk, 69), (24.5, .8*yk, 62), (28, .65*yk, 53),
                                        (28.5, .5*yk, 44), (27, .4*yk, 37)])
            d['grip'] = resample(limb, [b0, (b0[0]+5, b0[1], 60), (15, .9*yk, 54), (21, .7*yk, 44), (25, .45*yk, 33),
                                        (26.5, .25*yk, 22), (25, .05*yk, 13), (22, -.1*yk, 8), (19.5, -.15*yk, 9.5),
                                        (18.5, -.1*yk, 12)])
        if limb.name.startswith('hang'):
            yk = 12*math.sin(math.radians(side_of(limb)))
            d['lash'] = resample(limb, [b0, (8, yk*.8, 46), (15, yk*.9, 45), (21, yk*.8, 41), (25.5, yk*.6, 35), (27, yk*.4, 29)])
            d['grip'] = resample(limb, [b0, (8, yk*.8, 36), (14, yk*.8, 28), (19, yk*.5, 19), (22, yk*.15, 11), (21, -yk*.1, 8)])
        S[limb.name] = d
    shapes.cache = S
    return S


def collapse_curve(t):
    return smooth(t/.6)*.88+.12*smooth((t-.45)/.55)


def body(f, name, t):
    K = KIT
    phase = TAU*t
    if name == 'idle':
        for k, b in enumerate(TRUNK[1:], 1):
            K.turn(f, b, (1, 0, 0), 2.2*osc(phase, phase-.9*k))
            K.turn(f, b, (0, 1, 0), 1.8*osc(phase, phase-.9*k+1.4))
            K.turn(f, b, (0, 0, 1), 3.5*osc(phase, phase-.6*k))
        K.turn(f, 'head', (0, 1, 0), 3*osc(phase, phase+.4))
        K.move(f, 'maw', mul(MAW_AXIS, .35*math.sin(2*phase)))
    elif name == 'slink':
        for k, b in enumerate(TRUNK[1:], 1):
            K.turn(f, b, (0, 1, 0), 2.2*osc(phase, phase-.8*k))
            K.turn(f, b, (1, 0, 0), 2.2*osc(phase, phase-.8*k+1.1))
            K.turn(f, b, (0, 0, 1), 3*osc(phase, phase-.5*k))
        K.turn(f, 'head', (0, 1, 0), 4*osc(phase, phase+.9))
    elif name == 'batter':
        wind, blow = bell(t/.56), bell((t-.2)/.72)
        for k, b in enumerate(TRUNK[1:], 1):
            K.turn(f, b, (0, 1, 0), -1.4*wind+(1.6+.7*k)*blow)
        K.turn(f, 'head', (0, 1, 0), -8*wind+24*blow)
        K.move(f, 'maw', mul(MAW_AXIS, 1.2*blow))
    elif name == 'crush':
        # The column bows forward over a target on the floor; the maw turns down to it.
        coil, grip = bell(t/.5), bell((t-.24)/.64)
        for k, b in enumerate(TRUNK[1:], 1):
            K.turn(f, b, (0, 1, 0), -1.2*coil+(3.2+1.3*k)*grip)
            K.turn(f, b, (0, 0, 1), 6*coil*math.sin(k))
        K.turn(f, 'head', (0, 1, 0), -6*coil+42*grip)
        K.move(f, 'maw', mul(MAW_AXIS, 2.6*grip))
    elif name == 'flinch':
        p = bell(t)
        for k, b in enumerate(TRUNK[1:], 1):
            K.turn(f, b, (0, 1, 0), -1.2*p)
            K.turn(f, b, (0, 0, 1), 5*p)
        K.turn(f, 'head', (0, 1, 0), -10*p)
        K.move(f, 'maw', mul(MAW_AXIS, -.8*p))
    elif name == 'collapse':
        q = collapse_curve(t)
        # The column buckles: segments shorten (flesh slumps into itself) and
        # fold forward and to one side until the crown lies on the floor.
        folds = (0, 12, 16, 16, 14, 10)
        rolls = (0, -6, 8, -10, 6, -4)
        for k, b in enumerate(TRUNK[1:]+['head'], 1):
            i = IDS[b]
            f[i][0:3] = [c*(1-SLUMP*q) for c in REST_LOCAL[i]]
            if b != 'head':
                K.turn(f, b, (0, 1, 0), folds[k]*q)
                K.turn(f, b, (1, 0, 0), rolls[k]*q)
        K.turn(f, 'head', (0, 1, 0), 18*q)
        K.move(f, 'maw', mul(MAW_AXIS, -.6*q))
    elif name != 'rest':
        raise ValueError(name)


REST_LOCAL = [tuple(local) for _, _, local in BONES]
SLUMP = .68
DEAD_CURL = {'crown': .32, 'arm': .22, 'root': .10, 'tendril': .40, 'hang': .36}


def limb_targets(limb, name, t, root):
    S = shapes()[limb.name]
    kind = limb.name.split('_')[0]
    k = LIMBS.index(limb)
    phase = TAU*t
    rest = relative(S['rest'], root)
    # Strike shapes are authored in cell space (only the root follows the body)
    # so a lunging trunk cannot carry a blow outside the cell.
    rel = lambda key: [root]+S[key][1:]
    floor = kind == 'root'
    if name in ('idle', 'slink'):
        amp = {'crown': 3.2, 'arm': 3.0, 'root': 1.5, 'tendril': 3.6, 'hang': 3.0}[kind]*(1.05 if name == 'slink' else 1.)
        return wiggle(rest, amp, phase+1.7*k, power=2.4 if floor else 1.3, lateral_only=floor,
                      wave=.9 if name == 'slink' else .75, start=1.7*k)
    if name == 'batter':
        if 'blow' in S:
            return blend_shapes([(0, rest), (.28, rel('raise')), (.5, rel('blow')), (.64, rel('blow')), (1, rest)], t)
        if 'lash' in S:
            return blend_shapes([(0, rest), (.3, wiggle(rest, 5, 2.2+k, power=1.1)), (.5, rel('lash')), (.62, rel('lash')),
                                 (1, rest)], t)
        return wiggle(rest, (1.8 if floor else 4.5)*bell(t), .7*k+1, power=2.2 if floor else 1.2, lateral_only=floor)
    if name == 'crush':
        if 'wrap' in S:
            return blend_shapes([(0, rest), (.26, wiggle(rest, 3, 1+k, power=1.1)), (.5, rel('wrap')), (.72, rel('wrap')),
                                 (1, rest)], t)
        if 'grip' in S:
            return blend_shapes([(0, rest), (.28, wiggle(rest, 4, 1+k, power=1.1)), (.5, rel('grip')), (.72, rel('grip')),
                                 (1, rest)], t)
        return wiggle(rest, (1.6 if floor else 4.0)*bell(t), .7*k+2, power=2.2 if floor else 1.2, lateral_only=floor)
    if name == 'flinch':
        return wiggle(rest, (1.4 if floor else 3.0)*bell(t), .9*k, power=2.0 if floor else 1.1, lateral_only=floor)
    if name == 'collapse':
        if kind == 'root':
            dead = wiggle(rest, 1.2, 1.3*k, power=2.5, lateral_only=True)
            return blend_shapes([(0, rest), (.62, dead), (1, dead)], t)
        # Limp limbs slide off the heap tangentially and coil around it.
        turn = 1 if k % 2 else -1
        heading = math.atan2(root[1], root[0]-4)+turn*math.radians(105)
        dead = floor_spiral(limb, root, heading, turn*DEAD_CURL[kind], lift=.9, drop_rate=.9)
        return blend_shapes([(0, rest), (.62, dead), (1, dead)], t)
    raise ValueError(name)


def pose(name, t):
    f = KIT.frame()
    body(f, name, t)
    world = RIG.matrices(f)
    for limb in LIMBS:
        root = KIT.root_of(world, f, limb)
        KIT.aim_limb(f, world, limb, limb_targets(limb, name, t, root))
    return [tuple(r) for r in f]


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from . import tentacle_horror_materials as materials
    return materials.connected_atlas(skin_parts(), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm_bytes(v, n, uv, tr, w, BONES, clips, bounds, 'Project_Broom_tentacle_horror', SKIN)
    path = ROOT/'mod/BrogueDoom'/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M48', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/tentacle_horror/tentacle-horror-animated.blend')
    out = ROOT/'assets/monsters/tentacle_horror'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    result = importlib.import_module('tools.monster_models.tentacle_horror_animation').build()
    print({k: result[k] for k in ('sha256', 'dimensions', 'vertices', 'triangles', 'boneCount')})
