"""Original unicorn: a slender white equine with a spiral horn and rainbow mane.

Brogue describes the unicorn's flowing mane and tail shining with rainbow
light, a horn that glows with healing and protective magic, and imploring
eyes; its attack verbs are "pokes", "stabs" and "gores". Everything here is
presentation only: the horn's glow and the mane's colours emit no light and
imply no healing, shielding, target, collision, damage, AI, turn or RNG
behaviour. Brogue owns the unicorn's bolts, allegiance and every outcome.

The horse body is derived from the accepted centaur's equine half (the same
lofted trunk, four-bone legs, rigid-joint weighting, hoof IK and planted-hoof
rules), rebuilt lighter, with an arched neck and a refined head.
+X is forward, Z is up and the floor is Z=0.
"""
import hashlib
import json
import math
from . import iqm, unicorn_materials
from .creatures import Sculpt, TILE
from .rat import ROOT, Part, add, sub, mul, unit, cross, spline, ellipsoid, tube
from .skeletal import Rig, axis, between, inverse, qmul, rotate, assemble, sample_clips
from .centaur_animation import torso_loft, clamp, smooth, window, slerp, lerp, mirror

SKIN = 'graphics/BRGUNI.png'
SKIN_VOXEL_SIZE = .2
SKIN_FACE_BUDGET = 9800


def CONNECTED_SKIN(name):
    """Fused skin: trunk, arched neck, head planes and the four legs."""
    return name in ('horse_body', 'neck', 'tail_dock') or name.startswith(('head_', 'fore_', 'hind_'))


# Equine legs: shoulder/hip anchor, elbow|stifle, knee|hock, fetlock.
FORE = dict(shoulder=(10.2, 5.6, 36.0), upper=(8.6, 5.4, 25.8), lower=(10.2, 5.2, 14.4), end=(9.0, 5.2, 4.8))
HIND = dict(hip=(-15.0, 6.0, 34.5), upper=(-10.4, 6.4, 24.4), lower=(-16.8, 5.6, 14.0), end=(-15.2, 5.2, 4.8))
# Head frame: the poll, the axis running down the face (D) and the forehead
# normal (F). The head is carried collected, the face about 60 degrees down.
POLL = (21.2, 0, 55.8)
D = (.5, 0, -.8660254)
F = (.8660254, 0, .5)
HORN_BASE_S, HORN_BASE_F = 2.3, 2.45
HORN_DIR = unit((.28, 0, .96))
HORN_LEN = 12.2
HORN_R = 1.3
HORN_TURNS = 4.25


def head_point(s, f=0., y=0.):
    return (POLL[0]+s*D[0]+f*F[0], y, POLL[2]+s*D[2]+f*F[2])


HORN_ROOT = head_point(HORN_BASE_S, HORN_BASE_F)
HORN_TIP = add(HORN_ROOT, mul(HORN_DIR, HORN_LEN))

NECK_BONES = ((11.4, 0, 39.2), (14.8, 0, 45.4), (18.2, 0, 51.0))
MANE_BONES = ((8.4, 0, 43.4), (11.8, 0, 49.4), (15.4, 0, 55.0))
TAIL = [(-22.0, 0, 38.8), (-25.0, 0, 38.8), (-27.2, 0, 34.0), (-27.6, 0, 26.6), (-27.0, 0, 19.0)]

SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (-13, 0, 34)), ('barrel', 'pelvis', (-2, 0, 34)),
         ('withers', 'barrel', (8, 0, 37))]
parent = 'withers'
for i, p in enumerate(NECK_BONES):
    SPECS.append((f'neck_{i}', parent, p))
    parent = f'neck_{i}'
SPECS.append(('head', 'neck_2', POLL))
for side, sign in (('L', 1), ('R', -1)):
    SPECS.append((f'ear_{side}', 'head', head_point(-.3, 1.3, sign*1.45)))
for side, sign in (('L', 1), ('R', -1)):
    for i, p in enumerate(MANE_BONES):
        SPECS.append((f'mane_{side}{i}', f'neck_{i}', mirror(p, 1)))
for side, sign in (('L', 1), ('R', -1)):
    parent = 'withers'
    for joint in ('shoulder', 'upper', 'lower', 'end'):
        SPECS.append((f'fore_{side}_{joint}', parent, mirror(FORE[joint], sign)))
        parent = f'fore_{side}_{joint}'
    parent = 'pelvis'
    for joint in ('hip', 'upper', 'lower', 'end'):
        SPECS.append((f'hind_{side}_{joint}', parent, mirror(HIND[joint], sign)))
        parent = f'hind_{side}_{joint}'
parent = 'pelvis'
for i, p in enumerate(TAIL):
    SPECS.append((f'tail_{i}', parent, p))
    parent = f'tail_{i}'
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CLIPS = [('idle', 48, 16, True), ('trot', 32, 35, True), ('gore', 36, 35, False),
         ('rear_strike', 40, 35, False), ('flinch', 14, 35, False), ('fall', 46, 35, False)]


# --- shapes -------------------------------------------------------------------

def oriented(name, center, frame, radii, mat='body', seg=20, rings=12):
    """Ellipsoid whose local x/y/z radii follow the three given world axes."""
    p = ellipsoid(name, (0, 0, 0), radii, TILE[mat], seg, rings)
    a, b, c = frame
    p.vertices = [add(center, add(add(mul(a, v[0]), mul(b, v[1])), mul(c, v[2]))) for v in p.vertices]
    return p


def flat_strand(name, points, flat_axis, keep, mat, sides=12, samples=3):
    """Tube flattened across flat_axis (a unit vector) about its own centreline."""
    p = tube(name, points, TILE[mat], sides, samples)
    rows = spline(points, samples)
    ring = sides+1
    out = []
    for i, v in enumerate(p.vertices):
        r = min(i//ring, len(rows)-1) if i < len(rows)*ring else (0 if i == len(rows)*ring else len(rows)-1)
        c = rows[r][:3]
        d = sub(v, c)
        along = sum(x*y for x, y in zip(d, flat_axis))
        out.append(sub(v, mul(flat_axis, along*(1-keep))))
    p.vertices = out
    return p


def build_horn():
    """Spiral horn: a two-start helical ridge twisting round a tapered cone.

    UV u runs base to tip and v round the horn; the painted groove follows the
    same helix phase, so paint and geometry agree.
    """
    p = Part('horn')
    d = HORN_DIR
    a = unit(cross(d, (0, 1, 0)))
    b = cross(d, a)
    rows, sides = 56, 24
    base = sub(HORN_ROOT, mul(d, 1.2))
    for i in range(rows+1):
        s = i/rows
        radius = HORN_R*(1-s)**.8+.05
        if s < .06:
            radius = HORN_R*1.08
        for j in range(sides+1):
            ang = math.tau*j/sides
            ridge = 1+.17*math.cos(2*ang-s*HORN_TURNS*math.tau)*clamp((s-.05)/.06)*clamp((.97-s)/.1)
            r = radius*ridge
            co = add(add(base, mul(d, (HORN_LEN+1.2)*s)), add(mul(a, r*math.cos(ang)), mul(b, r*math.sin(ang))))
            p.vertex(co, 'tail', s, j/sides)
    for i in range(rows):
        for j in range(sides):
            k = i*(sides+1)+j
            p.faces.append((k, k+1, k+sides+2, k+sides+1))
    c0 = p.vertex(base, 'tail', 0, .5)
    for j in range(sides):
        p.faces.append((c0, j+1, j))
    tip = p.vertex(add(base, mul(d, HORN_LEN+1.35)), 'tail', 1, .5)
    last = rows*(sides+1)
    for j in range(sides):
        p.faces.append((tip, last+j, last+j+1))
    return p


def horse_loft(name, rows, sides=40, samples=4, e=.92):
    """Equine trunk lofted along +X: x, centre z, half width, back, belly.

    The centaur's loft with a rounder section (exponent near 1): a lighter,
    rounded barrel with no hard back corners under flat light.
    """
    p = Part(name)
    rows = spline(rows, samples)
    for i, (x, zc, w, top, bottom) in enumerate(rows):
        for j in range(sides+1):
            a = math.tau*j/sides
            c, s = math.cos(a), math.sin(a)
            y = w*math.copysign(abs(s)**e, s)
            z = zc+(top if c > 0 else bottom)*math.copysign(abs(c)**e, c)
            p.vertex((x, y, z), 'fur', i/(len(rows)-1), j/sides)
    for i in range(len(rows)-1):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+1, a+sides+2, a+sides+1))
    for end, reverse in ((0, True), (len(rows)-1, False)):
        x, zc = rows[end][:2]
        center = p.vertex((x, 0, zc), 'fur', end/(len(rows)-1), .5)
        for j in range(sides):
            a = end*(sides+1)+j
            p.faces.append((center, a+1, a) if reverse else (center, a, a+1))
    return p


HORSE = [(-24.0, 34.8, .8, .8, .8), (-23.3, 34.9, 3.8, 3.9, 4.2), (-21.8, 35.0, 6.6, 6.1, 6.6),
         (-19.2, 34.9, 7.8, 6.8, 7.0), (-15.0, 34.8, 8.2, 7.0, 6.4), (-8.6, 34.5, 8.0, 6.3, 6.6),
         (-2.0, 34.2, 8.5, 6.6, 9.0),
         (4.0, 34.4, 8.3, 7.2, 9.2), (9.0, 35.0, 7.4, 7.8, 8.8), (12.8, 35.6, 6.2, 6.8, 7.4),
         (15.2, 36.0, 4.6, 5.0, 5.6), (16.6, 36.2, 2.2, 2.4, 2.6), (17.1, 36.2, .6, .6, .6)]
# Arched neck: x, z, half width, throat depth, crest depth.
NECK = [(9.4, 35.0, 6.0, 5.4, 5.0), (11.9, 40.2, 5.0, 4.8, 4.5), (14.3, 44.6, 4.1, 3.8, 3.9),
        (16.5, 48.4, 3.4, 2.9, 3.5), (18.3, 51.8, 2.9, 2.2, 3.2), (19.7, 54.9, 2.6, 1.8, 2.8),
        (20.3, 57.0, 1.6, 1.2, 1.6)]
# Head profile along the face axis: s, half width, jaw depth, forehead depth.
HEAD = [(-1.4, 1.5, 1.5, 1.5), (0.0, 2.6, 2.7, 2.5), (1.8, 3.2, 4.0, 2.8), (3.6, 3.3, 4.3, 2.7),
        (5.4, 2.75, 3.0, 2.35), (7.4, 2.2, 2.2, 2.0), (9.4, 2.05, 2.05, 1.95), (10.8, 2.3, 2.3, 2.05),
        (11.9, 1.95, 1.95, 1.6), (12.7, .9, .9, .8)]


def crest_line():
    rows = spline(NECK, 4)
    out = []
    for i, (x, z, w, front, back) in enumerate(rows):
        a, b = rows[max(0, i-1)], rows[min(len(rows)-1, i+1)]
        tx, tz = b[0]-a[0], b[1]-a[1]
        n = math.hypot(tx, tz)
        nx, nz = tz/n, -tx/n
        out.append(((x-nx*back, 0, z-nz*back), w, (nx, 0, nz)))
    return out


def neck_width(z):
    rows = spline(NECK, 4)
    best = min(rows, key=lambda r: abs(r[1]-z))
    return best[2]


def build_mane(s):
    """Broad overlapping locks along the crest; most fall to the left, some right."""
    crest = crest_line()
    count = 16
    for i in range(count):
        f = (i+.5)/count
        k = int(f*(len(crest)-5))+3
        root, w, n = crest[k]
        side = -1 if i % 4 == 1 else 1
        root = add(sub(root, mul(n, -.4)), (0, side*.35, 0))    # seat the root just inside the crest
        length = 10.8-4.2*f**1.5+1.1*math.sin(i*2.9)
        length = min(length, root[2]-39.5)       # base locks end above the shoulder
        wave = .8*math.sin(i*1.7)
        back = mul(n, -1)
        pts = [(*root, 1.5)]
        p1 = add(add(root, mul(back, .9)), (0, side*1.3, .8))
        pts.append((*p1, 1.8))
        for q, drop in enumerate((.3, .55, .8, 1.0)):
            z = root[2]+.5-drop*length
            y = side*(neck_width(z)+.75+.3*drop*length/4)
            x = p1[0]-.2*drop*length+wave*math.sin(drop*3.2)
            pts.append((x, y, z, (1.85-1.3*drop) if q < 3 else .12))
        s.parts.append(flat_strand(f'mane_lock{i}', pts, (0, 1, 0), .3, 'wood', 12, 3))
    # Forelock: soft locks from between the ears, parted round the horn.
    for i, (y, reach) in enumerate(((-1.3, 5.2), (-.5, 4.2), (.5, 4.4), (1.3, 5.0))):
        root = head_point(-.4, 2.2, y*.8)
        p1 = head_point(.9, 3.2, y*1.25)
        p2 = head_point(2.6+.4*abs(y), 3.1, y*1.6)
        p3 = head_point(reach, 2.9, y*1.75)
        s.strand(f'forelock_{i}', [(*root, .6), (*p1, .62), (*p2, .45), (*p3, .08)], 'wood', 8, 3)


def build_tail(s):
    """Long, high-carried tail: many locks falling in a soft S-curve."""
    path = [(-21.8, 0, 37.8), (-24.8, 0, 38.6), (-27.0, 0, 35.6), (-27.9, 0, 30.0), (-27.5, 0, 23.2),
            (-26.6, 0, 16.4), (-26.4, 0, 10.8)]
    count = 15
    for i in range(count):
        a = math.tau*i/count
        spread = (math.cos(a), math.sin(a))
        length = .8+.2*((i*7) % 5)/4
        pts = []
        for k, (x, y, z) in enumerate(path):
            f = k/(len(path)-1)
            fan = 1.1*f**.8
            zz = 37.8-(37.8-z)*length
            r = (1.0 if k == 0 else 1.1-.85*f)
            pts.append((x+spread[0]*fan*.9+(.6*f*math.sin(i*2.3)), spread[1]*fan*1.7+.5*f*math.sin(i*1.3+f*4), zz, r))
        pts[-1] = (*pts[-1][:3], .08)
        s.strand(f'tail_lock{i}', pts, 'wood', 10, 3)


def build_head(s):
    """Refined head: dished face, round jowls, fine muzzle and soft nostrils."""
    # torso_loft's "front" follows the path normal, which faces the jaw here.
    rows = [(head_point(sv)[0], head_point(sv)[2], w, jd, fd) for sv, w, jd, fd in HEAD]
    s.parts.append(torso_loft('head_skull', rows, 32, 3))
    frame = (D, (0, 1, 0), F)
    for sign in (-1, 1):
        # Round jowl (lower jaw) at the back of the cheek, and cheek ridge.
        s.parts.append(oriented(f'head_jowl_{sign}', head_point(3.0, -1.6, sign*1.7), frame, (2.6, 1.55, 2.3)))
        s.parts.append(oriented(f'head_cheek_{sign}', head_point(5.4, .2, sign*1.95), frame, (2.6, .8, .9)))
        # Orbit ridge above the eye, nostril flare and the soft lip.
        s.parts.append(oriented(f'head_orbit_{sign}', head_point(3.0, 1.6, sign*2.55), frame, (1.3, .75, .9)))
        s.parts.append(oriented(f'head_nostril_{sign}', head_point(11.0, 1.0, sign*1.25), frame, (1.2, .65, .75)))
    s.parts.append(oriented('head_lip', head_point(12.1, -1.1, 0), frame, (1.1, 1.35, 1.0)))
    s.parts.append(oriented('head_chin', head_point(11.6, -2.0, 0), frame, (1.3, 1.0, .9)))
    # Eyes: large, dark and set a little forward, with a lid and a lash line.
    for sign in (-1, 1):
        side = 'L' if sign > 0 else 'R'
        out = unit((.25, sign, .1))
        c = head_point(3.35, 1.25, sign*2.72)
        s.parts.append(oriented(f'eye_{side}', c, (D, out, F), (.95, .55, .78), 'dark', 16, 10))
        s.parts.append(oriented(f'eye_glint_{side}', add(c, add(mul(out, .5), add(mul(F, .32), mul(D, -.22)))),
                                (D, out, F), (.16, .07, .16), 'glow', 8, 6))
        lid = [head_point(3.35+ds, 1.25+.55+.25*(1-abs(ds)), sign*(2.72+.38*(1-abs(ds)**2))) for ds in (-1.05, -.5, 0, .5, 1.05)]
        s.strand(f'lid_upper_{side}', [(*p, .2) for p in lid], 'body', 8, 3)
        lash = [add(p, (0, sign*.12, .1)) for p in lid]
        s.strand(f'lash_line_{side}', [(*p, .1) for p in lash], 'dark', 6, 3)
        for k, ds in enumerate((-.6, -.2, .2, .6)):
            root = head_point(3.35+ds, 1.25+.8, sign*(2.72+.38))
            tipp = add(root, add(mul(F, .5), add(mul(out, .55), mul(D, -.35+ds*.2))))
            s.strand(f'lash_{side}{k}', [(*root, .07), (*tipp, .02)], 'dark', 5, 1)
        low = [head_point(3.35+ds, 1.25-.62-.1*(1-abs(ds)), sign*(2.72+.25*(1-abs(ds)**2))) for ds in (-.9, 0, .9)]
        s.strand(f'lid_lower_{side}', [(*p, .12) for p in low], 'body', 8, 3)
    # Ears: pointed, cupped forward, alert.
    for sign in (-1, 1):
        side = 'L' if sign > 0 else 'R'
        root = REST[IDS[f'ear_{side}']]
        up = unit(add(add(mul(D, -.85), mul(F, .32)), (0, sign*.33, 0)))
        flat = unit(cross(up, (1, 0, 0)))
        if flat[1]*sign < 0:
            flat = mul(flat, -1)
        pts = [(*add(root, mul(up, -.4)), .85), (*add(root, mul(up, 1.3)), 1.15), (*add(root, mul(up, 2.8)), .9),
               (*add(root, mul(up, 3.9)), .45), (*add(root, mul(up, 4.5)), .06)]
        s.parts.append(flat_strand(f'ear_{side}', pts, flat, .5, 'accent'))
        inner = [(*add(add(root, mul(up, k)), add(mul(flat, -.32), mul((1, 0, 0), .25))), r)
                 for k, r in ((.6, .55), (1.6, .7), (2.8, .5), (3.7, .15))]
        s.parts.append(flat_strand(f'ear_inner_{side}', inner, flat, .35, 'dark'))


def build_parts():
    s = Sculpt()
    s.parts.append(horse_loft('horse_body', HORSE))
    s.parts.append(torso_loft('neck', NECK, 32, 4))
    for side, sign in (('L', 1), ('R', -1)):
        s.oval(f'fore_{side}_scapula', (9.6, sign*5.2, 33.0), (4.2, 2.4, 6.2))
        s.oval(f'fore_{side}_breast', (13.2, sign*3.2, 31.4), (2.4, 2.4, 3.6))
        s.oval(f'hind_{side}_thigh', (-13.8, sign*6.2, 29.6), (5.4, 2.5, 6.6))
        s.oval(f'hind_{side}_buttock', (-19.8, sign*4.0, 32.0), (2.8, 2.9, 5.0))
        sh, el, kn, fe = (mirror(FORE[j], sign) for j in ('shoulder', 'upper', 'lower', 'end'))
        s.strand(f'fore_{side}_forearm', [(*add(el, (.6, -sign*.3, 4.6)), 3.4), (*add(el, (.4, 0, 2.4)), 3.0), (*el, 2.7), (*add(el, mul(sub(kn, el), .45)), 1.95),
                                          (*add(kn, (0, 0, 2.2)), 1.45), (*kn, 1.5)], sides=16, samples=4)
        s.oval(f'fore_{side}_knee', add(kn, (.3, 0, 0)), (1.5, 1.6, 1.85))
        s.strand(f'fore_{side}_cannon', [(*kn, 1.3), (*add(kn, mul(sub(fe, kn), .5)), 1.0), (*add(fe, (0, 0, 1.2)), 1.08)],
                 sides=14, samples=3)
        s.oval(f'fore_{side}_fetlock', add(fe, (-.15, 0, 0)), (1.5, 1.35, 1.5))
        s.strand(f'fore_{side}_pastern', [(*fe, 1.15), (*add(fe, (.9, 0, -1.4)), 1.05), (*add(fe, (1.45, 0, -2.3)), 1.15)],
                 sides=14, samples=2)
        s.oval(f'fore_{side}_elbow', add(el, (-1.4, -sign*.3, .9)), (1.7, 1.7, 1.9))
        hp, st, hk, hf = (mirror(HIND[j], sign) for j in ('hip', 'upper', 'lower', 'end'))
        s.strand(f'hind_{side}_gaskin', [(*add(st, (.2, 0, 3.4)), 3.5), (*add(st, (.8, 0, 1.6)), 3.2), (*st, 2.9), (*add(st, mul(sub(hk, st), .5)), 2.05),
                                         (*add(hk, (.6, 0, 1.3)), 1.5), (*hk, 1.35)], sides=16, samples=4)
        s.oval(f'hind_{side}_hock', add(hk, (-.6, 0, .3)), (1.45, 1.35, 2.0))
        s.strand(f'hind_{side}_cannon', [(*hk, 1.35), (*add(hk, mul(sub(hf, hk), .5)), 1.02), (*add(hf, (0, 0, 1.2)), 1.08)],
                 sides=14, samples=3)
        s.oval(f'hind_{side}_fetlock', add(hf, (-.2, 0, 0)), (1.5, 1.35, 1.45))
        s.strand(f'hind_{side}_pastern', [(*hf, 1.12), (*add(hf, (.8, 0, -1.4)), 1.02), (*add(hf, (1.3, 0, -2.3)), 1.12)],
                 sides=14, samples=2)
        s.oval(f'hind_{side}_stifle', add(st, (.9, -sign*.2, .6)), (1.5, 1.8, 1.8))
        # Gilded hooves with a painted cleft, and silky feathering over the coronet.
        for limb, fe_ in (('fore', fe), ('hind', hf)):
            c = add(fe_, (1.5 if limb == 'fore' else 1.35, 0, -3.8))
            s.strand(f'hoof_{limb}_{side}', [(c[0]-.1, c[1], 2.5, 1.3), (c[0]+.1, c[1], 1.7, 1.6), (c[0]+.35, c[1], .75, 1.85),
                                              (c[0]+.4, c[1], .24, 1.9)], 'dark', 16, 2)
            for k in range(9):
                ang = math.pi*.28+math.pi*1.44*k/8
                base = (fe_[0]+.2+1.35*math.cos(ang), fe_[1]+1.3*math.sin(ang), fe_[2]-.2)
                mid = (c[0]-.3+2.0*math.cos(ang)-.5, c[1]+2.0*math.sin(ang), 2.6)
                tip = (c[0]-.2+2.25*math.cos(ang)-.9, c[1]+2.2*math.sin(ang), 1.05+.25*math.sin(k*1.9))
                s.strand(f'feather_{limb}_{side}{k}', [(*base, .5), (*mid, .32), (*tip, .06)], 'glow', 6, 2)
    s.strand('tail_dock', [(-21.0, 0, 37.4, 1.9), (-23.4, 0, 38.0, 1.7), (-25.0, 0, 37.2, 1.3)], sides=16, samples=2)
    build_head(s)
    s.parts.append(build_horn())
    build_mane(s)
    build_tail(s)
    for part in s.parts:
        part.vertices = [tuple(round(c, 6)+0. for c in v) for v in part.vertices]
    return unicorn_materials.repack(s.parts)


# --- weights ------------------------------------------------------------------

def sharp_chain(point, chain, k=.24):
    """Rigid segments that blend only near each joint (crisp equine joints)."""
    ids = [IDS[b] for b in chain]
    best = None
    for n, (a, b) in enumerate(zip(ids, ids[1:])):
        start, end = REST[a], REST[b]
        d = sub(end, start)
        t = clamp(sum(x*y for x, y in zip(sub(point, start), d))/sum(x*x for x in d))
        distance = math.dist(point, add(start, mul(d, t)))
        if best is None or distance < best[0]-1e-9:
            best = (distance, n, t)
    _, n, t = best
    a, b = ids[n], ids[n+1]
    if n == len(ids)-2 and t >= 1:
        return [(b, 1)]
    wb = .5*smooth((t-(1-k))/k)
    out = {a: 1-wb, b: wb}
    if n > 0 and t < k:
        wp = .5*smooth((k-t)/k)
        out = {ids[n-1]: wp, a: (1-wp)*(1-wb), b: (1-wp)*wb}
    return [(i, w) for i, w in out.items() if w > 1e-9]


LEG = {'fore': ('shoulder', 'upper', 'lower', 'end'), 'hind': ('hip', 'upper', 'lower', 'end')}
NECK_CHAIN = ('withers', 'neck_0', 'neck_1', 'neck_2', 'head')


def weights(part, v, uv):
    """Quantised skin weights (1e-6, exact complement last) so Blender's and
    system Python produce identical bake fingerprints."""
    raw = raw_weights(part, v, uv)
    if len(raw) == 1:
        return [(raw[0][0], 1)]
    out = [(b, round(w, 6)) for b, w in raw[:-1]]
    rest = 1.
    for b, w in out:
        rest -= w
    result = [(b, w) for b, w in out if w > 0]+([(raw[-1][0], rest)] if rest > 0 else [])
    return [(result[0][0], 1)] if len(result) == 1 else result


def lock_root(part):
    return part.vertices[-2]     # a tube's first cap centre is its root row centre


def raw_weights(part, v, uv):
    n = part.name
    if n.startswith(('hoof_', 'feather_')):
        limb, side = n.split('_')[1], n.split('_')[2][0]
        return [(IDS[f'{limb}_{side}_end'], 1)]
    if n.startswith('tail_lock'):
        return RIG.chain_weights(v, [IDS[f'tail_{i}'] for i in range(5)])
    if n == 'tail_dock':
        return RIG.chain_weights(v, [IDS['pelvis'], IDS['tail_0'], IDS['tail_1']])
    if n.startswith('ear_'):
        return [(IDS['ear_'+n.split('_')[-1]], 1)]
    if n.startswith(('head', 'eye', 'lid', 'lash', 'horn', 'forelock')):
        return [(IDS['head'], 1)]
    if n.startswith('mane_lock'):
        root = lock_root(part)
        base = RIG.chain_weights(root, [IDS[b] for b in NECK_CHAIN])
        k = min(range(3), key=lambda i: math.dist(root, MANE_BONES[i]))
        side = 'L' if part.vertices[len(part.vertices)//2][1] > 0 else 'R'
        t = clamp(math.dist(v, root)/7.0)**1.3
        t = round(t, 6)
        out = [(b, w*(1-t)) for b, w in base if w*(1-t) > 1e-9]
        return out+[(IDS[f'mane_{side}{k}'], t)] if t > 0 else out
    if n.startswith(('fore_', 'hind_')):
        limb, side = n.split('_')[:2]
        chain = [f'{limb}_{side}_{j}' for j in LEG[limb]]
        if n.endswith(('scapula', 'breast', 'thigh', 'buttock')):
            parent_bone = 'withers' if limb == 'fore' else 'pelvis'
            top = 33.0 if limb == 'fore' else 30.0
            t = clamp((top-v[2])/9)*(.9 if n.endswith(('scapula', 'thigh')) else .5)
            return [(IDS[parent_bone], 1-t), (IDS[chain[0]], t)] if t > 0 else [(IDS[parent_bone], 1)]
        return sharp_chain(v, chain)
    if n == 'neck':
        return RIG.chain_weights(v, [IDS[b] for b in NECK_CHAIN])
    return RIG.chain_weights(v, [IDS[b] for b in ('pelvis', 'barrel', 'withers')])


# --- posing -------------------------------------------------------------------

class Pose:
    def __init__(self):
        self.rot = [(0, 0, 0, 1) for _ in BONES]
        self.shift = [(0, 0, 0) for _ in BONES]

    def turn(self, bone, direction, degrees):
        self.rot[IDS[bone]] = qmul(self.rot[IDS[bone]], axis(direction, math.radians(degrees)))

    def frame(self):
        return [(*add(local, self.shift[i]), *self.rot[i], 1, 1, 1) for i, (n, p, local) in enumerate(BONES)]

    def world(self):
        return RIG.matrices(self.frame())

    def reach(self, chain, target, world_q=None, pole=None, joints=('upper', 'lower', 'end')):
        """Two-bone IK to a world target, solved in the parent's frame."""
        ids = [IDS[f'{chain}_{j}'] for j in joints]
        parent_id = BONES[ids[0]][1]
        pw, pq = self.world()[parent_id]
        local = add(REST[parent_id], rotate(inverse(pq), sub(target, pw)))
        root, joint, end = [REST[i] for i in ids]
        root = add(root, self.shift[ids[0]])
        a, b = math.dist(REST[ids[0]], joint), math.dist(joint, end)
        distance = math.dist(local, root)
        if not abs(a-b)+1e-6 < distance < a+b-1e-6:
            raise ValueError(('unreachable', chain, target, distance, a+b))
        direction = unit(sub(local, root))
        along = (a*a-b*b+distance*distance)/(2*distance)
        pole = sub(joint, REST[ids[0]]) if pole is None else rotate(inverse(pq), pole)
        bend = unit(sub(pole, mul(direction, sum(x*y for x, y in zip(pole, direction)))))
        knee = add(root, add(mul(direction, along), mul(bend, math.sqrt(max(0, a*a-along*along)))))
        upper = between(sub(joint, REST[ids[0]]), sub(knee, root))
        lower = between(sub(end, joint), sub(local, knee))
        self.rot[ids[0]] = upper
        self.rot[ids[1]] = qmul(inverse(upper), lower)
        self.rot[ids[2]] = inverse(lower) if world_q is None else qmul(qmul(inverse(lower), inverse(pq)), world_q)


POLE = {'fore': (1, 0, 0), 'hind': (-1, 0, 0)}


def plant_hooves(P, offsets=None, flex=None, skip=()):
    """IK every leg to its hoof target; planted hooves stay level in world space."""
    for limb in ('fore', 'hind'):
        for side in ('L', 'R'):
            key = f'{limb}_{side}'
            if key in skip:
                continue
            d = (offsets or {}).get(key, (0, 0, 0))
            q = (flex or {}).get(key, (0, 0, 0, 1))
            anchor = f'{key}_{"shoulder" if limb == "fore" else "hip"}'
            P.turn(anchor, (0, 1, 0), -math.degrees(math.atan2(d[0], 30))*.8)
            P.reach(key, add(REST[IDS[f'{key}_end']], d), q, POLE[limb])


def tail_sway(P, phase, amp=4., lift=0., side=0.):
    for i in range(5):
        P.turn(f'tail_{i}', (0, 0, 1), amp*math.sin(phase-i*.7)+side*(1-i*.15))
        if lift:
            P.turn(f'tail_{i}', (0, 1, 0), -lift*(1-i*.2))


def mane_sway(P, phase, amp=3.):
    for side in 'LR':
        for i in range(3):
            P.turn(f'mane_{side}{i}', (1, 0, 0), amp*math.sin(phase-i*.8))


def ears(P, left, right, splay=0.):
    """Positive angles tip the ears back; splay turns them outward."""
    for side, angle, sign in (('L', left, 1), ('R', right, -1)):
        P.turn(f'ear_{side}', (0, 1, 0), -angle)
        if splay:
            P.turn(f'ear_{side}', (1, 0, 0), -sign*splay)


def horn_tip(world):
    pos, q = world[IDS['head']]
    return add(pos, rotate(q, sub(HORN_TIP, POLL)))


def neck_pose(P, pitch, head_pitch, yaw=0., head_yaw=0., roll=0.):
    """Spread a neck pitch (positive lowers the head) over the three neck bones."""
    for i, share in enumerate((.45, .33, .22)):
        P.turn(f'neck_{i}', (0, 1, 0), pitch*share)
        if yaw:
            P.turn(f'neck_{i}', (0, 0, 1), yaw*share)
    P.turn('head', (0, 1, 0), head_pitch)
    if head_yaw:
        P.turn('head', (0, 0, 1), head_yaw)
    if roll:
        P.turn('head', (1, 0, 0), roll)


def settle(P, w):
    """Blend an action's end into the idle clip's first frame (idle at t=0)."""
    if w <= 0:
        return
    for i, share in enumerate((.45, .33, .22)):
        P.turn(f'neck_{i}', (0, 1, 0), 2*math.sin(.6)*share*w)
    tail_sway(P, 0, 4*w)
    mane_sway(P, 0, 3*w)
    ears(P, 0, 0, 4*w)


def pose(name, t):
    P = Pose()
    phase = math.tau*t
    if name == 'idle':
        breath = math.sin(phase)
        P.shift[IDS['pelvis']] = (0, 0, -.3-.12*breath)
        P.turn('barrel', (1, 0, 0), .0)
        neck_pose(P, 2*math.sin(phase+.6), 3*math.sin(2*phase), 0, 7*math.sin(phase))
        flick = math.sin(math.pi*clamp((t-.55)/.12))**2
        ears(P, 4*math.sin(phase)+26*flick, -4*math.sin(phase), 4)
        k = (1-math.cos(phase))/2
        rest_q = axis((0, 1, 0), math.radians(18*k))
        plant_hooves(P, {'hind_R': (1.2*k, 0, (1.4+.2*math.sin(phase))*k)}, {'hind_R': rest_q})
        tail_sway(P, phase, 4)
        mane_sway(P, phase, 3)
    elif name == 'trot':
        trot_pose(P, t)
    elif name == 'gore':
        gore_pose(P, t)
    elif name == 'rear_strike':
        rear_pose(P, t)
    elif name == 'flinch':
        pulse = math.sin(math.pi*t)**2
        P.shift[IDS['pelvis']] = (-1.8*pulse, .8*pulse, -.3-.6*pulse)
        P.turn('pelvis', (0, 0, 1), 4*pulse)
        P.turn('withers', (0, 1, 0), -2*pulse)
        neck_pose(P, -16*pulse, -14*pulse, 12*pulse, -14*pulse, -8*pulse)
        ears(P, 55*pulse, 55*pulse, 10*pulse)
        plant_hooves(P)
        tail_sway(P, 0, 0, 20*pulse, -8*pulse)
        mane_sway(P, math.pi*.5, 7*pulse)
        settle(P, window(t, .6, 1))
    elif name == 'fall':
        fall_pose(P, t)
    return P.frame()


def trot_pose(P, t):
    """Elevated two-beat trot: diagonal pairs swing together with high knees."""
    phase = math.tau*t
    bob = math.cos(2*phase)
    P.shift[IDS['pelvis']] = (0, 0, -.8+.45*bob)
    P.turn('pelvis', (0, 1, 0), 1.0*math.sin(phase))
    P.turn('withers', (0, 1, 0), -.8*math.sin(phase))
    neck_pose(P, -3+1.2*bob, 2.5*bob, 0, 2*math.sin(phase))
    ears(P, 6, 6)
    offsets, flex = {}, {}
    stance = .56
    for key, offset in (('fore_L', 0), ('hind_R', 0), ('fore_R', .5), ('hind_L', .5)):
        q = (t+offset) % 1
        if q < stance:
            dx, lift, curl = 4.6-9.2*q/stance, 0, 0
        else:
            u = (q-stance)/(1-stance)
            dx = -4.6+9.2*smooth(u)
            lift = (6.4 if key.startswith('fore') else 4.4)*math.sin(math.pi*u)**1.2
            curl = math.sin(math.pi*min(1, u*1.25))
        offsets[key] = (dx, 0, lift)
        flex[key] = axis((0, 1, 0), math.radians((85 if key.startswith('fore') else 48)*curl))
    plant_hooves(P, offsets, flex)
    tail_sway(P, phase*2, 4, 8)
    mane_sway(P, phase*2, 6)


GORE_LIMIT = 30.6    # horn tip x limit inside the centred cell


def gore_pose(P, t):
    """Gather, then drive the horn forward and up; key pose at the middle frame."""
    gather = window(t, 0, .3)*(1-window(t, .3, .46))
    drive = window(t, .3, .5)*(1-window(t, .6, .95))
    toss = math.sin(math.pi*clamp((t-.52)/.3))*(t > .52)
    # A hooking thrust: the head tucks so the horn levels forward and up, and
    # the neck turns a little aside, as a horse strikes with its head.
    P.shift[IDS['pelvis']] = (-2.4*gather-1.2*drive, -.6*drive, -.3-1.6*gather-1.0*drive)
    P.turn('pelvis', (0, 1, 0), -2.5*gather+3.5*drive)
    P.turn('pelvis', (0, 0, 1), -5*drive)
    neck_pose(P, -14*gather+30*drive-12*toss, -12*gather+40*drive+4*toss, -45*drive-8*toss, 0)
    ears(P, 30*drive+10*gather, 30*drive+10*gather, 8*drive)
    w = window(t, .7, 1)
    tail_sway(P, math.tau*t, 3*(1-w), 16*drive, 12*drive)
    mane_sway(P, math.tau*t, 5*drive)
    settle(P, w)
    # Keep the thrust inside the cell: pull the body back if the tip overhangs.
    over = horn_tip(P.world())[0]-GORE_LIMIT
    if over > 0:
        x, y, z = P.shift[IDS['pelvis']]
        P.shift[IDS['pelvis']] = (x-over, y, z)
    plant_hooves(P)


def rear_pose(P, t):
    """Rear on the hind legs with forelegs pawing, then strike down, horn low."""
    rise = window(t, .04, .42)*(1-window(t, .6, .78))
    strike = window(t, .62, .78)*(1-window(t, .82, 1))
    paw = math.sin(math.tau*2.2*t)*rise
    P.shift[IDS['pelvis']] = (-1.2*rise-1.6*strike, -.6*strike, -.3-1.6*rise-1.0*strike)
    P.turn('pelvis', (0, 1, 0), -30*rise)
    P.turn('pelvis', (0, 0, 1), -3*strike)
    P.turn('withers', (0, 1, 0), -4*rise)
    for side in 'LR':
        P.turn(f'hind_{side}_hip', (0, 1, 0), 24*rise)
    neck_pose(P, -6*rise+30*strike, 10*rise+40*strike, 45*strike, 6*rise)
    ears(P, 12*rise+25*strike, 12*rise+25*strike)
    w = window(t, .82, 1)
    tail_sway(P, math.tau*t, 3*(1-w), 8*rise+22*strike, 10*rise+16*strike)
    mane_sway(P, math.tau*t*1.5, 7*rise)
    settle(P, w)
    over = horn_tip(P.world())[0]-GORE_LIMIT
    if over > 0:
        x, y, z = P.shift[IDS['pelvis']]
        P.shift[IDS['pelvis']] = (x-over, y, z)
    if rise > 1e-9:
        plant_hooves(P, skip=('fore_L', 'fore_R'))
        fold_forelegs(P, rise, paw)
    else:
        plant_hooves(P)


def fold_forelegs(P, amount, paw):
    """Rearing forelegs tuck up under the chest, knees folded, pawing the air."""
    world = P.world()
    for side, sign in (('L', 1), ('R', -1)):
        w = paw*sign
        key = f'fore_{side}'
        spos, sq = world[IDS[key+'_shoulder']]
        tucked = add(spos, rotate(sq, (5.5+1.6*w, 0, -15.0+1.8*w)))
        target = lerp(REST[IDS[key+'_end']], tucked, smooth(amount))
        q = qmul(sq, axis((0, 1, 0), math.radians(95*amount+12*w)))
        P.reach(key, target, q, (1, 0, -.3))


def blend(A, B, w, early=None, w_early=0.):
    P = Pose()
    ws = [w_early if early and n in early else w for n, p, v in BONES]
    P.shift = [lerp(a, b, k) for a, b, k in zip(A.shift, B.shift, ws)]
    P.rot = [slerp(a, b, k) for a, b, k in zip(A.rot, B.rot, ws)]
    return P


FALL_ROLL = 84.0             # onto the right side, legs toward the gallery camera; the mane (mostly left) lies uppermost
FALL_CENTRE = (-3.0, 0.0, 10.2)
FALL_LEGS = dict(top=(-16, -30, -10, 63, -16, 22, 20, -56), low=(-4, -8, -6, 55, -4, 6, 14, -50))
FALL = dict(neck=((3, 12), (2.4, 11), (1.8, 9)), head=(2, -12, 0), buckle_yaw=-24, lift=6.0)


def fall_buckle(t):
    A = Pose()
    sink = window(t, 0, .3)
    A.shift[IDS['pelvis']] = (-.6*sink, 0, -.3-8.0*sink)
    A.turn('pelvis', (0, 1, 0), 3*sink)
    A.turn('withers', (0, 1, 0), 5*sink)
    A.shift[IDS['pelvis']] = (-2.0*sink, 0, -.3-8.0*sink)
    neck_pose(A, -8*sink, 26*sink, FALL['buckle_yaw']*sink)
    ears(A, 40*sink, 40*sink, 10*sink)
    plant_hooves(A)
    return A


def fall_limp():
    """Final pose: on the right side, legs limp and loosely bent, neck limp on the floor."""
    B = Pose()
    q = axis((1, 0, 0), math.radians(FALL_ROLL))
    B.rot[IDS['root']] = q
    B.shift[IDS['root']] = sub(FALL_CENTRE, rotate(q, REST[IDS['barrel']]))
    # Limp legs lie out from the belly, knees loosely bent; the upper pair
    # rests a little forward of the lower pair so both read from the side.
    for side in ('L', 'R'):
        top = side == 'L'
        m = -1 if side == 'R' else 1       # x-axis angles mirror across the body
        L = FALL_LEGS['top' if top else 'low']
        B.turn(f'fore_{side}_shoulder', (1, 0, 0), m*L[0])
        B.turn(f'fore_{side}_shoulder', (0, 1, 0), L[1])
        B.turn(f'fore_{side}_upper', (0, 1, 0), L[2])
        B.turn(f'fore_{side}_lower', (0, 1, 0), L[3])
        B.turn(f'fore_{side}_end', (0, 1, 0), 28)
        B.turn(f'hind_{side}_hip', (1, 0, 0), m*L[4])
        B.turn(f'hind_{side}_hip', (0, 1, 0), L[5])
        B.turn(f'hind_{side}_upper', (0, 1, 0), L[6])
        B.turn(f'hind_{side}_lower', (0, 1, 0), L[7])
        B.turn(f'hind_{side}_end', (0, 1, 0), 24)
    # The neck droops sideways onto the floor; the head lies on its cheek.
    for i, (pitch, bend) in enumerate(FALL['neck']):
        B.turn(f'neck_{i}', (0, 1, 0), pitch)
        B.turn(f'neck_{i}', (1, 0, 0), bend)
    hp, hb, hy = FALL['head']
    B.turn('head', (0, 1, 0), hp)
    B.turn('head', (1, 0, 0), hb)
    if hy:
        B.turn('head', (0, 0, 1), hy)
    ears(B, 50, 50, 18)
    for i in range(5):
        B.turn(f'tail_{i}', (1, 0, 0), -14 if i == 0 else 3)
        B.turn(f'tail_{i}', (0, 1, 0), -16 if i == 0 else 6)
    for i in range(3):
        B.turn(f'mane_L{i}', (1, 0, 0), -12)    # uppermost locks settle onto the neck
        B.turn(f'mane_R{i}', (1, 0, 0), 10)
    return B


def fall_pose(P, t):
    """Knees buckle, the body rolls onto its right side, the neck goes limp."""
    A, B = fall_buckle(t), fall_limp()
    r = window(t, .24, .8)
    C = blend(A, B, r, ('neck_0', 'neck_1', 'neck_2', 'head'), window(t, .3, .85))
    P.shift, P.rot = C.shift, C.rot
    P.shift[IDS['root']], P.rot[IDS['root']] = (0, 0, 0), (0, 0, 0, 1)
    centre = P.world()[IDS['barrel']][0]
    q = axis((1, 0, 0), math.radians(FALL_ROLL*r))
    target = lerp(centre, FALL_CENTRE, r)
    target = add(target, (0, 2.0*math.sin(math.pi*r), FALL['lift']*math.sin(math.pi*r)**.5))
    P.rot[IDS['root']] = q
    P.shift[IDS['root']] = sub(target, rotate(q, centre))


def geometry():
    from .connected_skin import attach
    parts = attach('unicorn', build_parts(), weights)
    return assemble(unicorn_materials.connected_atlas(parts), weights)


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from .connected_skin import attach
    return unicorn_materials.connected_atlas(attach('unicorn', build_parts(), weights), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_unicorn', material_path=SKIN)
    path = ROOT/'mod/BrogueDoom/models/monsters/63_unicorn.iqm'
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M63', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/unicorn/unicorn-animated.blend')
    out = ROOT/'assets/monsters/unicorn'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    print(importlib.import_module('tools.monster_models.unicorn_animation').build()['sha256'])
