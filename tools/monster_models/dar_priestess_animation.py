"""Original dar priestess: robed relic-bearer built on dar family anatomy.

Presentation-only. Brogue CE owns haste, healing, negation, spark, targeting,
drops, turns and every outcome. Clips are cosmetic roles only.
"""
import hashlib
import json
import math
from . import iqm, dar_priestess_materials as mats
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit, cross
from .skeletal import Rig, axis, between, inverse, qmul, rotate, assemble, sample_clips
from .dar_blademaster_animation import rings

SLUG = 'dar_priestess'
SKIN = 'graphics/BRGDPRS.png'
MODEL = 'mod/BrogueDoom/models/monsters/32_dar_priestess.iqm'
L_HAND = (4.6, 8.5, 30.8)
R_HAND = (5.4, -8.3, 31.0)
STAFF_FOOT, STAFF_TOP, RING_Z, RING_R = 1.2, 49.6, 52.4, 2.5
CHARM_PIVOT = (4.6, 8.5, RING_Z-1.0)
GRIP_ABOVE_FOOT = L_HAND[2]-STAFF_FOOT
# Relics hang from the girdle: (angle degrees, kind, chain drop).
RELICS = [(68, 'bell', 3.2), (112, 'box', 4.4), (150, 'tooth', 3.0),
          (-64, 'icon', 3.6), (-104, 'vial', 4.2), (-146, 'bell', 2.8)]
GIRDLE_Z = 30.5

SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 28)), ('spine', 'pelvis', (-.4, 0, 40)),
         ('neck', 'spine', (0, 0, 49)), ('head', 'neck', (.2, 0, 55))]
for side, sign, hand in (('L', 1, L_HAND), ('R', -1, R_HAND)):
    parent = 'spine'
    for joint, point in zip(('upper', 'lower', 'end'), [(0, sign*6.0, 45.3), (.8, sign*7.9, 36.4), hand]):
        SPECS.append((f'arm_{side}_{joint}', parent, point))
        parent = f'arm_{side}_{joint}'
for side, sign in (('L', 1), ('R', -1)):
    parent = 'pelvis'
    for joint, point in zip(('upper', 'lower', 'end'), [(0, sign*3.0, 28), (1.6, sign*3.3, 15), (0, sign*3.6, 2.4)]):
        SPECS.append((f'leg_{side}_{joint}', parent, point))
        parent = f'leg_{side}_{joint}'
# The staff is a root child that follows the left hand exactly while held, so
# the death clip can let it topple free without detaching any mesh.
SPECS += [('staff', 'root', L_HAND), ('charms', 'staff', CHARM_PIVOT), ('sickle', 'arm_R_end', R_HAND)]


def girdle_point(a_deg, z=GIRDLE_Z, pad=.35):
    a = math.radians(a_deg)
    return (robe_cx(z)+(robe_rx(z)+pad)*math.cos(a), (robe_ry(z)+pad)*math.sin(a), z)


# Robe profile rows: z, centre x, half depth, half width.
ROBE_ROWS = [(.5, .7, 8.4, 9.0), (4, .6, 7.8, 8.5), (10, .5, 6.9, 7.7), (16, .4, 6.0, 6.9), (22, .2, 5.2, 6.3),
             (27, 0, 4.5, 5.8), (30.5, 0, 3.75, 5.0), (34, -.2, 3.5, 4.7), (38.5, -.1, 3.9, 5.4),
             (41, .3, 4.3, 5.7), (44, -.2, 3.95, 6.1), (46.2, 0, 3.2, 5.6), (47.8, 0, 2.25, 2.7), (48.6, 0, 2.0, 2.3)]


def _interp(z, k):
    rows = ROBE_ROWS
    if z <= rows[0][0]:
        return rows[0][k]
    for a, b in zip(rows, rows[1:]):
        if a[0] <= z <= b[0]:
            t = (z-a[0])/(b[0]-a[0])
            return a[k]+(b[k]-a[k])*t
    return rows[-1][k]


def robe_cx(z): return _interp(z, 1)
def robe_rx(z): return _interp(z, 2)
def robe_ry(z): return _interp(z, 3)


def robe_fold(a, z):
    k = max(0, min(1, (30-z)/25))
    return 1+k*(.055*math.sin(9*a+.6)+.028*math.sin(17*a))


RELIC_BONES = [f'relic_{i}' for i in range(len(RELICS))]
for i, (a, kind, drop) in enumerate(RELICS):
    SPECS.append((RELIC_BONES[i], 'pelvis', girdle_point(a)))

RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CLIPS = [('idle', 40, 20, True), ('advance', 32, 35, True), ('slice', 24, 35, False),
         ('invoke', 26, 35, False), ('recoil', 14, 35, False), ('fall', 36, 35, False)]


def CONNECTED_SKIN(name):
    return name in ('pelvis', 'torso') or name.startswith(('head_', 'shoulder_', 'arm_', 'leg_', 'hand_', 'foot_'))


def surface(name, rows, sides=36, radius=None, tile='fur'):
    """Closed ring surface with a duplicated UV seam: u around, v along rows."""
    p = Part(name)
    z0, z1 = rows[0][0], rows[-1][0]
    for j, (z, cx, rx, ry) in enumerate(rows):
        for i in range(sides+1):
            a = math.tau*i/sides
            m = radius(a, z) if radius else 1
            p.vertex((cx+rx*m*math.cos(a), ry*m*math.sin(a), z), tile, i/sides, (z-z0)/(z1-z0) if z1 != z0 else j/(len(rows)-1))
    w = sides+1
    for j in range(len(rows)-1):
        for i in range(sides):
            a = j*w+i
            p.faces.append((a, a+1, a+1+w, a+w))
    p.faces.append(tuple(reversed(range(sides))))
    p.faces.append(tuple((len(rows)-1)*w+i for i in range(sides)))
    return p


def ribbon(name, points, across, half_width, half_thick, tile='fur'):
    """Closed thin strip: u across, v along. across/half_* are per-point."""
    p = Part(name)
    n = len(points)
    for k, c in enumerate(points):
        t = unit(sub(points[min(k+1, n-1)], points[max(k-1, 0)]))
        w = unit(across[k] if isinstance(across, list) else across)
        nrm = unit(cross(w, t))
        hw = half_width[k] if isinstance(half_width, list) else half_width
        ht = half_thick[k] if isinstance(half_thick, list) else half_thick
        for sw, st, u in ((-1, 1, 0), (1, 1, 1), (1, -1, 1), (-1, -1, 0)):
            p.vertex(add(c, add(mul(w, sw*hw), mul(nrm, st*ht))), tile, u, k/(n-1))
    for k in range(n-1):
        for s in range(4):
            a = k*4+s
            b = k*4+(s+1) % 4
            p.faces.append((a, b, b+4, a+4))
    p.faces.append((3, 2, 1, 0))
    last = (n-1)*4
    p.faces.append((last, last+1, last+2, last+3))
    return p


def loop_points(center, rx, ry, z, count=40, tilt=0, radius=.2):
    cx, cy = center
    return [(cx+rx*math.cos(math.tau*i/count), cy+ry*math.sin(math.tau*i/count),
             z+tilt*math.cos(math.tau*i/count), radius) for i in range(count+1)]


def hand_wrap(s, side, grip, sign):
    """Four curled fingers and a thumb closed around a vertical grip."""
    gx, gy, gz = grip
    s.oval(f'hand_{side}_palm', (gx-.3, gy+sign*.35, gz), (1.35, 1.45, 1.6), 'body', 20, 12)
    for i in range(4):
        z = gz-1.05+i*.68
        offs = [(-.7, -1.0), (.9, -1.05), (1.1, 0), (.7, .7), (-.1, .6)]
        pts = [(gx+dx, gy+sign*-dy, z, r) for (dx, dy), r in zip(offs, (.37, .38, .36, .31, .25))]
        s.strand(f'hand_{side}_finger{i}', pts, 'body', 10, 3)
    s.strand(f'hand_{side}_thumb', [(gx-1.2, gy+sign*.9, gz+1.1, .45), (gx+.5, gy+sign*1.5, gz+1.1, .38),
                                    (gx+1.0, gy+sign*.7, gz+.7, .25)], 'body', 10)


def build_parts():
    s = Sculpt()
    # --- Connected anatomy (fused by the cage bake) -----------------------
    s.oval('pelvis', (0, 0, 28), (3.2, 4.0, 4.2))
    s.parts.append(rings('torso', [(27, 0, 3.3, 4.5), (31, 0, 2.8, 3.8), (35, -.3, 2.9, 4.0), (38.5, -.2, 3.3, 4.8),
                                   (41, .2, 3.6, 5.0), (44, -.2, 3.3, 5.3), (46, 0, 2.6, 4.9), (48, 0, 1.85, 2.2),
                                   (52, 0, 1.7, 1.7)]))
    s.parts.append(rings('head_cranium', [(50.4, 1, 1, 1.4), (51.3, 1, 1.9, 2), (52.7, .6, 2.45, 2.45), (54.5, .1, 2.85, 3.0),
                                          (56, .1, 2.9, 3.05), (58, -.1, 2.75, 2.75), (59.6, -.3, 2, 2.1), (60.2, -.4, .15, .2)]))
    for sign in (-1, 1):
        s.strand(f'head_ear_{sign}', [(-.4, sign*2.5, 55.6, 1.0), (-1.1, sign*4.3, 56.8, .8), (-2.4, sign*7.0, 59.2, .06)], 'body', 14, 4)
        s.strand(f'head_brow_{sign}', [(2.9, sign*.8, 56.45, .24), (2.78, sign*1.65, 56.62, .3), (2.23, sign*2.4, 56.75, .18)], 'body', 12)
    for side, sign in (('L', 1), ('R', -1)):
        s.oval(f'shoulder_{side}', (0, sign*5.4, 44.6), (2.2, 2.3, 2.4))
        for limb in ('arm', 'leg'):
            points = [REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper', 'lower', 'end')]
            rs = (1.75, 1.3, .95) if limb == 'arm' else (2.05, 1.6, 1.1)
            s.strand(f'{limb}_{side}', [(*p, r) for p, r in zip(points, rs)], sides=18, samples=5)
        s.oval(f'foot_{side}', (1.5, sign*3.6, 1.6), (3.0, 1.45, 1.3), 'body', 24, 12)
    hand_wrap(s, 'L', L_HAND, 1)
    hand_wrap(s, 'R', R_HAND, -1)
    # --- Face details --------------------------------------------------------
    for sign in (-1, 1):
        s.strand(f'detail_ear_{sign}', [(.15, sign*3.1, 55.7, .18), (-.45, sign*4.2, 56.7, .22), (-1.8, sign*6.0, 58.4, .04)], 'accent', 10)
        s.oval(f'detail_eye_socket_{sign}', (2.65, sign*1.6, 55.8), (.17, .67, .29), 'dark', 18, 10)
        s.oval(f'detail_iris_{sign}', (2.83, sign*1.6, 55.76), (.06, .23, .17), 'accent', 14, 8)
        # Serene, lowered lids and a lash line: devotion, not a stare.
        s.oval(f'detail_lid_{sign}', (2.74, sign*1.6, 55.98), (.2, .74, .2), 'body', 18, 10)
        s.strand(f'detail_lash_{sign}', [(2.9, sign*.98, 55.86, .05), (2.95, sign*1.6, 55.8, .06), (2.82, sign*2.28, 55.92, .04)], 'dark', 6)
        s.strand(f'hairbrow_{sign}', [(3.0, sign*.8, 56.64, .08), (2.88, sign*1.7, 56.8, .11), (2.3, sign*2.4, 56.86, .06)], 'dark', 8)
    s.strand('detail_lip', [(3.1, -1.0, 52.9, .11), (3.46, 0, 52.8, .12), (3.1, 1.0, 52.9, .11)], 'dark', 10)
    # --- Long silver hair swept back beneath the circlet ------------------
    for i in range(15):
        y = (i-7)*.37
        crown = (abs(y)/2.7)**2
        spread = 1.35
        s.strand(f'hair_{i}', [(1.9, y, 58.4-1.1*crown, .36), (.1, y*1.05, 60.3-1.5*crown, .55),
                               (-2.4, y*1.05, 59.0-1.2*crown, .55), (-3.2, y*1.05, 54.6, .52),
                               (-3.7, y*1.1, 50.6, .5), (-5.1, y*spread, 47.0, .48),
                               (-6.0, y*spread, 43.6, .45), (-6.3, y*spread*1.02, 40.4-1.8*((i*3) % 5)/4, .12)], 'dark', 10, 4)
    # A few separated locks break the back-hair curtain.
    for k, y in enumerate((-3.1, .5, 2.7)):
        s.strand(f'hair_lock_{k}', [(-3.3, y*.85, 55.0, .5), (-5.4, y*1.0, 48.4, .55), (-6.85, y*1.12, 43.8, .5),
                                    (-7.0, y*1.18, 40.0-1.2*k, .32), (-6.8, y*1.2, 37.6-1.2*k, .08)], 'dark', 10, 4)
    # --- Circlet and original crescent crest ---------------------------------
    s.strand('crown_circlet', loop_points((-.05, 0), 3.35, 3.6, 57.5, 40, tilt=-.35, radius=.2), 'bone', 6, 1)
    s.strand('crown_crescent', [(1.2, -3.1, 63.6, .08), (2.0, -2.5, 61.2, .34), (2.55, -1.2, 59.3, .52), (2.7, 0, 58.7, .6),
                                (2.55, 1.2, 59.3, .52), (2.0, 2.5, 61.2, .34), (1.2, 3.1, 63.6, .08)], 'bone', 10, 4)
    s.oval('gem_crown', (2.95, 0, 60.4), (.5, .8, .8), 'accent', 16, 10)
    # --- Vestments --------------------------------------------------------------
    s.parts.append(surface('robe', ROBE_ROWS, 40, robe_fold))
    s.parts.append(surface('mantle', [(42.0, -.1, 5.4, 9.6), (43.6, -.1, 5.3, 9.6), (46.2, -.1, 4.8, 9.2),
                                      (47.6, 0, 3.6, 6.4), (48.4, 0, 2.4, 2.9), (49.0, 0, 2.15, 2.45)], 40,
                           lambda a, z: 1+.035*math.sin(12*a)*max(0, (45-z)/3)))
    for side, sign in (('L', 1), ('R', -1)):
        up, lo, en = [REST[IDS[f'arm_{side}_{j}']] for j in ('upper', 'lower', 'end')]
        p0 = add(up, mul(sub(lo, up), .16))
        wrist = add(lo, mul(sub(en, lo), .78))
        s.strand(f'sleeve_{side}', [(*p0, 2.35), (*add(up, mul(sub(lo, up), .6)), 2.3), (*lo, 2.25),
                                    (*add(lo, mul(sub(en, lo), .45)), 2.5), (*wrist, 3.0)], 'cloth', 20, 4)
    # Stole: two cream strips down the front, following the robe surface.
    for k, sign in enumerate((1, -1)):
        pts, across = [], []
        for i in range(19):
            z = 43.4-i*(43.4-11.5)/18
            y = sign*1.9*(1+.25*(43.4-z)/32)
            a = math.asin(max(-1, min(1, y/robe_ry(z))))
            pad = .32
            x = robe_cx(z)+(robe_rx(z)*robe_fold(a, z))*math.cos(a)+pad
            pts.append((x, y, z))
            across.append((-math.sin(a)*.25, 1, 0))
        s.parts.append(ribbon(f'stole_{k}', pts, across, 1.05, .14))
        s.oval(f'bell_stole_tassel_{k}', add(pts[-1], (.2, 0, -.9)), (.45, .45, .9), 'bone', 12, 8)
    # Gold girdle cord, knot and hanging ends.
    s.strand('girdle', [(*girdle_point(360*i/40), .34) for i in range(41)], 'bone', 8, 1)
    s.oval('girdle_knot', girdle_point(28, pad=.7), (.8, .8, .75), 'bone', 14, 10)
    for k, (a0, a1) in enumerate(((22, 18), (34, 40))):
        top = girdle_point(a0, pad=.7)
        low = girdle_point(a1, 20.2, .5)
        mid = girdle_point((a0+a1)/2, 25.5, .45)
        s.strand(f'girdle_end_{k}', [(*top, .26), (*mid, .24), (*low, .22)], 'bone', 8, 3)
        s.oval(f'girdle_tassel_{k}', add(low, (0, 0, -.8)), (.5, .5, 1.0), 'bone', 12, 8)
    # Necklace and chest medallion.
    s.strand('necklace_back', [(1.1, -2.5, 48.6, .12), (-.9, -2.7, 49.25, .12), (-2.6, 0, 49.3, .12),
                               (-.9, 2.7, 49.25, .12), (1.1, 2.5, 48.6, .12)], 'bone', 6, 3)
    for sign in (-1, 1):
        s.strand(f'necklace_{sign}', [(1.1, sign*2.5, 48.6, .12), (3.6, sign*2.2, 47.3, .12), (5.0, sign*1.0, 45.6, .12), (5.3, 0, 45.1, .12)], 'bone', 6, 3)
    s.oval('medallion', (5.25, 0, 44.1), (.45, 1.35, 1.35), 'bone', 20, 12)
    s.oval('gem_medallion', (5.62, 0, 44.1), (.3, .62, .62), 'accent', 14, 8)
    # Relics on short chains from the girdle, clear of the flaring robe.
    for i, (a_deg, kind, drop) in enumerate(RELICS):
        top = girdle_point(a_deg, pad=.45)
        zb = GIRDLE_Z-drop
        bottom = girdle_point(a_deg, zb, 1.05)
        s.strand(f'relic_{i}_chain', [(*top, .13), (*add(mul(add(top, bottom), .5), (0, 0, 0)), .13), (*bottom, .13)], 'bone', 6, 3, ribbed=True)
        a = math.radians(a_deg)
        out = (math.cos(a), math.sin(a), 0)
        c = add(bottom, mul(out, .35))
        if kind == 'bell':
            p = surface(f'bell_{i}', [(c[2]-2.0, 0, 1.15, 1.15), (c[2]-1.7, 0, 1.05, 1.05), (c[2]-.9, 0, .7, .7),
                                      (c[2]-.2, 0, .55, .55), (c[2], 0, .25, .25)], 16)
            p.vertices = [(x+c[0], y+c[1], z) for x, y, z in p.vertices]
            s.parts.append(p)
            s.oval(f'bell_{i}_clapper', (c[0], c[1], c[2]-2.1), (.28, .28, .28), 'bone', 10, 6)
        elif kind == 'box':
            p = s.box(f'relic_{i}_box', (c[0], c[1], c[2]-1.4), (.75, .75, 1.3), 'bone')
            s.oval(f'gem_relic_{i}', add((c[0], c[1], c[2]-1.4), mul(out, .8)), (.4, .4, .5), 'accent', 12, 8)
        elif kind == 'tooth':
            s.strand(f'ivory_{i}', [(c[0], c[1], c[2]-.2, .42), (c[0]+.3*out[0], c[1]+.3*out[1], c[2]-1.8, .36),
                                    (c[0]+.9*out[0], c[1]+.9*out[1], c[2]-3.1, .04)], 'bone', 10, 3)
        elif kind == 'icon':
            s.oval(f'relic_{i}_icon', (c[0], c[1], c[2]-1.4), (.35+.9*abs(out[1]), .35+.9*abs(out[0]), 1.35), 'bone', 18, 10)
            s.oval(f'gem_relic_{i}', add((c[0], c[1], c[2]-1.4), mul(out, .45)), (.3, .3, .55), 'accent', 12, 8)
        else:
            s.oval(f'glass_relic_{i}', (c[0], c[1], c[2]-1.7), (.62, .62, 1.3), 'accent', 14, 10)
            s.oval(f'relic_{i}_cap', (c[0], c[1], c[2]-.35), (.38, .38, .3), 'bone', 10, 6)
    # --- Relic staff (left hand) ------------------------------------------
    sx, sy, _ = L_HAND
    s.strand('staff_shaft', [(sx, sy, STAFF_FOOT, .42), (sx, sy, 30, .5), (sx, sy, STAFF_TOP, .46)], 'wood', 12, 3)
    s.oval('staff_ferrule', (sx, sy, STAFF_FOOT+.85), (.55, .55, .8), 'bone', 12, 8)
    s.oval('staff_collar', (sx, sy, STAFF_TOP-.2), (.8, .8, 1.0), 'bone', 14, 8)
    ring = [(sx, sy+RING_R*math.sin(math.tau*i/32), RING_Z-RING_R*math.cos(math.tau*i/32), .3) for i in range(33)]
    s.strand('staff_ring', ring, 'bone', 8, 1)
    s.strand('staff_spoke', [(sx, sy, RING_Z-RING_R, .16), (sx, sy, RING_Z+RING_R, .16)], 'bone', 6, 1)
    s.strand('staff_spoke_cross', [(sx, sy-RING_R, RING_Z, .14), (sx, sy+RING_R, RING_Z, .14)], 'bone', 6, 1)
    s.oval('gem_staff', (sx, sy, RING_Z), (.75, 1.0, 1.0), 'accent', 16, 10)
    s.strand('staff_finial', [(sx, sy, RING_Z+RING_R+.1, .45), (sx, sy, RING_Z+RING_R+1.4, .3), (sx, sy, RING_Z+RING_R+3.4, .03)], 'bone', 10, 3)
    for k, dy in enumerate((-1.9, 1.9)):
        top = (sx, sy+dy*.92, RING_Z-1.2)
        s.strand(f'charm_{k}_chain', [(*top, .1), (sx, sy+dy, RING_Z-2.7, .1), (sx, sy+dy, RING_Z-3.6, .1)], 'bone', 6, 2, ribbed=True)
        if k == 0:
            p = surface('bell_charm', [(RING_Z-5.1, 0, .72, .72), (RING_Z-4.8, 0, .66, .66), (RING_Z-4.2, 0, .45, .45), (RING_Z-3.6, 0, .18, .18)], 14)
            p.vertices = [(x+sx, y+sy+dy, z) for x, y, z in p.vertices]
            s.parts.append(p)
        else:
            s.oval('charm_disc', (sx, sy+dy, RING_Z-4.5), (.25, .8, .8), 'bone', 14, 8)
    # --- Ritual sickle (right hand) --------------------------------------------
    hx, hy, hz = R_HAND
    s.strand('sickle_grip', [(hx, hy, hz-2.6, .46), (hx, hy, hz+2.8, .43)], 'wood', 12)
    s.oval('sickle_pommel', (hx, hy, hz-2.8), (.6, .6, .5), 'bone', 12, 8)
    s.oval('sickle_collar', (hx, hy, hz+3.0), (.62, .62, .45), 'bone', 12, 8)
    arc, across, widths = [], [], []
    for i in range(13):
        t = i/12
        ang = math.radians(170-195*t)
        r = 4.3
        cx, cz = hx+4.25, hz+2.4
        arc.append((cx+r*math.cos(ang), hy, cz+r*math.sin(ang)*.95))
        across.append((math.cos(ang), 0, math.sin(ang)))
        widths.append(.95*math.sin(math.pi*min(1, .15+t*.95))+.05)
    s.parts.append(ribbon('sickle_blade', arc, across, widths, .1))
    parts = mats.repack(s.parts)
    for p in parts:
        p.vertices = [tuple(round(c, 6) for c in v) for v in p.vertices]
    return parts


def _robe_weights(v):
    x, y, z = v
    if z >= 28:
        if z < 35:
            t = (z-28)/7
            return [(IDS['pelvis'], 1-t), (IDS['spine'], t)]
        if z < 46.8:
            return [(IDS['spine'], 1)]
        t = max(0, min(1, (z-46.8)/2.2))
        return [(IDS['spine'], 1-t), (IDS['neck'], t)]
    a = max(0, min(1, (28-z)/25))**.8
    side = max(0, min(1, .5+y/5))
    # Front cloth drapes over thighs/knees; back cloth hangs from the pelvis
    # to the feet so a kneeling collapse never swings it through the floor.
    ang = math.atan2(y/max(.1, robe_ry(z)), (x-robe_cx(z))/max(.1, robe_rx(z)))
    front = max(0, min(1, .5+.9*math.cos(ang)))
    # Front cloth near the hips still tracks the thighs, so a seated
    # collapse carries the skirt over the legs rather than letting knees out.
    a = a+(1-a)*front*.65*min(1, (28-z)/4)
    out = {IDS['pelvis']: 1-a}
    for s, share in (('L', side), ('R', 1-side)):
        if share <= 0:
            continue
        ids = [IDS[f'leg_{s}_{j}'] for j in ('upper', 'lower', 'end')]
        zz = max(REST[ids[2]][2], min(REST[ids[0]][2], z))
        ref = (REST[ids[0]][0]+(REST[ids[1]][0]-REST[ids[0]][0])*max(0, min(1, (28-zz)/13)), REST[ids[0]][1], zz)
        for b, w in RIG.chain_weights(ref, ids):
            out[b] = out.get(b, 0)+a*share*front*w
        out[ids[2]] = out.get(ids[2], 0)+a*share*(1-front)
    return list(out.items())


def _normalize(rows):
    rows = sorted(((b, w) for b, w in rows if w > 1e-7), key=lambda r: (-r[1], r[0]))[:4]
    total = sum(w for b, w in rows)
    q = [(b, round(w/total, 6)) for b, w in rows]
    q[-1] = (q[-1][0], round(1-sum(w for b, w in q[:-1]), 6))
    return sorted(q, key=lambda r: r[0])


def weights(part, v, uv):
    return _normalize(_weights(part, v))


def _weights(part, v):
    n = part.name
    if n.startswith(('staff', 'gem_staff')):
        return [(IDS['staff'], 1)]
    if n.startswith(('charm', 'bell_charm')):
        return [(IDS['charms'], 1)]
    if n.startswith('sickle'):
        return [(IDS['sickle'], 1)]
    if n.startswith(('relic_', 'gem_relic_', 'glass_relic_', 'ivory_', 'bell_')) and not n.startswith('bell_stole'):
        i = int(n.split('_')[1] if not n.startswith(('gem_relic', 'glass_relic')) else n.split('_')[2])
        return [(IDS[RELIC_BONES[i]], 1)]
    if n.startswith(('head', 'detail', 'hairbrow', 'crown', 'gem_crown')):
        return [(IDS['head'], 1)]
    if n.startswith('hair'):
        t = max(0, min(1, (53-v[2])/9))
        return [(IDS['head'], 1-t), (IDS['spine'], t)] if t < 1 else [(IDS['spine'], 1)]
    if n.startswith(('necklace', 'medallion', 'gem_medallion')):
        t = max(0, min(1, (v[2]-47.8)/1.5))
        return [(IDS['spine'], 1-t), (IDS['neck'], t)]
    if n.startswith(('robe', 'stole', 'girdle', 'bell_stole', 'mantle')):
        return _robe_weights(v)
    if n.startswith('sleeve_'):
        side = n[-1]
        return RIG.chain_weights(v, [IDS[f'arm_{side}_{j}'] for j in ('upper', 'lower', 'end')])
    if n.startswith('shoulder_'):
        t = max(0, min(1, (abs(v[1])-3.8)/3))
        return [(IDS['spine'], 1-t), (IDS[f'arm_{n[-1]}_upper'], t)]
    if n.startswith(('hand_', 'foot_')):
        return [(IDS[f'{"arm" if n.startswith("hand") else "leg"}_{n.split("_")[1]}_end'], 1)]
    if n.startswith(('arm_', 'leg_')):
        return RIG.chain_weights(v, [IDS[n+'_'+j] for j in ('upper', 'lower', 'end')])
    if n == 'pelvis':
        return [(IDS['pelvis'], 1)]
    if n == 'torso':
        if v[2] < 35:
            return RIG.chain_weights(v, [IDS['pelvis'], IDS['spine']])
        t = max(0, min(1, (v[2]-46)/6))
        return [(IDS['spine'], 1-t), (IDS['neck'], t)]
    return [(IDS['spine'], 1)]


def solve_leg(side, target, rotations, pole=None):
    ids = [IDS[f'leg_{side}_{j}'] for j in ('upper', 'lower', 'end')]
    hip, knee, foot = [REST[i] for i in ids]
    a = math.dist(hip, knee)
    b = math.dist(knee, foot)
    distance = math.dist(target, hip)
    if not abs(a-b) < distance < a+b:
        raise ValueError(('unreachable priestess foot', side, target, distance, a+b))
    direction = unit(sub(target, hip))
    along = (a*a-b*b+distance*distance)/(2*distance)
    pole = sub(knee, hip) if pole is None else pole
    d = pole[0]*direction[0]+pole[1]*direction[1]+pole[2]*direction[2]
    bend = unit(sub(pole, mul(direction, d)))
    nk = add(hip, add(mul(direction, along), mul(bend, math.sqrt(max(0, a*a-along*along)))))
    upper = between(sub(knee, hip), sub(nk, hip))
    lower = between(sub(foot, knee), sub(target, nk))
    rotations[ids[0]] = upper
    rotations[ids[1]] = qmul(inverse(upper), lower)
    rotations[ids[2]] = inverse(lower)


def nlerp(a, b, t):
    if sum(x*y for x, y in zip(a, b)) < 0:
        b = tuple(-x for x in b)
    q = tuple(x+(y-x)*t for x, y in zip(a, b))
    n = math.sqrt(sum(x*x for x in q))
    return tuple(x/n for x in q)


def basis_quat(xa, ya, za):
    """Quaternion (x,y,z,w) whose rotation maps local X/Y/Z to the given axes."""
    m00, m10, m20 = xa
    m01, m11, m21 = ya
    m02, m12, m22 = za
    tr = m00+m11+m22
    if tr > 0:
        s = math.sqrt(tr+1)*2
        return ((m21-m12)/s, (m02-m20)/s, (m10-m01)/s, .25*s)
    if m00 > m11 and m00 > m22:
        s = math.sqrt(1+m00-m11-m22)*2
        return (.25*s, (m01+m10)/s, (m02+m20)/s, (m21-m12)/s)
    if m11 > m22:
        s = math.sqrt(1+m11-m00-m22)*2
        return ((m01+m10)/s, .25*s, (m12+m21)/s, (m02-m20)/s)
    s = math.sqrt(1+m22-m00-m11)*2
    return ((m02+m20)/s, (m12+m21)/s, .25*s, (m10-m01)/s)


# Settled staff on the floor behind the collapsed priestess (ring lying flat).
STAFF_REST_Q = basis_quat((0, 0, 1), (0, -1, 0), (1, 0, 0))
STAFF_REST_FOOT = (-27.4, 16.5, 1.0)


SLICE_ARM = (-34, -2, -30, 85)


def smooth(x):
    x = max(0, min(1, x))
    return x*x*(3-2*x)


def pose(name, t):
    rot = [(0, 0, 0, 1) for _ in BONES]
    shift = [(0, 0, 0) for _ in BONES]

    def turn(b, d, deg):
        rot[IDS[b]] = qmul(rot[IDS[b]], axis(d, math.radians(deg)))
    phase = math.tau*t
    release = 0
    if name == 'idle':
        turn('spine', (0, 1, 0), 1.2+.5*math.sin(phase))
        turn('head', (0, 1, 0), 7+1.5*math.sin(phase))
        turn('head', (0, 0, 1), 2*math.sin(phase))
        turn('arm_R_lower', (0, 1, 0), -8+2*math.sin(phase))
        for i, b in enumerate(RELIC_BONES):
            turn(b, (1, 0, 0), 2.2*math.sin(phase+i))
        turn('charms', (1, 0, 0), 3*math.sin(phase+1))
    elif name == 'advance':
        bob = -.6+.25*math.cos(2*phase)
        for side, offset in (('L', 0), ('R', .5)):
            q = (t+offset) % 1
            if q < .6:
                dx, lift = 1.6-3.2*q/.6, 0
            else:
                u = (q-.6)/.4
                dx, lift = -1.6+3.2*u, 1.6*math.sin(math.pi*u)
            solve_leg(side, add(REST[IDS[f'leg_{side}_end']], (dx+.3, 0, lift-bob)), rot)
        shift[IDS['pelvis']] = (-.3, 0, bob)
        turn('spine', (0, 0, 1), 2.5*math.sin(phase))
        turn('spine', (0, 1, 0), 3)
        turn('head', (0, 1, 0), 4)
        turn('arm_L_upper', (0, 1, 0), -4+2.5*math.cos(phase))
        turn('arm_R_upper', (0, 1, 0), -6-4*math.cos(phase))
        turn('arm_R_lower', (0, 1, 0), -10)
        # Relics jangle: each swings on its own chain pivot with a lagged phase.
        for i, b in enumerate(RELIC_BONES):
            turn(b, (1, 0, 0), 9*math.sin(2*phase+i*.9))
            turn(b, (0, 1, 0), 6*math.cos(2*phase+i*1.3))
        turn('charms', (1, 0, 0), 10*math.sin(2*phase+.5))
        turn('charms', (0, 1, 0), 5*math.cos(2*phase))
    elif name == 'slice':
        # Wind high behind the right shoulder, then a committed diagonal slash
        # forward and down across the body, peaking on the middle frame, with
        # the torso twisted into it and weight stepped onto the right foot.
        w = math.sin(math.pi*min(1, t/.46))**2 if t < .46 else 0
        h = math.exp(-((t-.52)/.15)**2)
        hs = smooth((t-.16)/.3)*(1-smooth((t-.74)/.24))
        lift = 1.3*(math.sin(math.pi*max(0, min(1, (t-.16)/.3)))+math.sin(math.pi*max(0, min(1, (t-.74)/.24))))
        turn('spine', (0, 0, 1), -18*w+28*h)
        turn('spine', (0, 1, 0), -6*w+16*h)
        turn('spine', (1, 0, 0), 5*h)
        uy, ux, ly, ey = SLICE_ARM
        turn('arm_R_upper', (0, 1, 0), -140*w+uy*h)
        turn('arm_R_upper', (1, 0, 0), -26*w+ux*h)
        turn('arm_R_lower', (0, 1, 0), -46*w+ly*h)
        turn('arm_R_end', (0, 1, 0), 34*w+ey*h)
        turn('arm_L_upper', (0, 1, 0), 10*h)
        turn('arm_L_upper', (1, 0, 0), 8*h)
        turn('arm_L_end', (0, 1, 0), -10*h)
        turn('arm_L_lower', (0, 1, 0), -6*hs)
        turn('head', (0, 0, 1), -12*h)
        turn('head', (0, 1, 0), 3+4*h)
        for i, b in enumerate(RELIC_BONES):
            turn(b, (1, 0, 0), 14*h*math.sin(i*1.9+1))
            turn(b, (0, 1, 0), -12*hs)
        turn('charms', (1, 0, 0), 12*h)
        pelvis = (-.3+1.5*hs, -.5*hs, -.6-.3*hs)
        shift[IDS['pelvis']] = pelvis
        for side, foot in (('L', (1.2, 0, 0)), ('R', (-1.2+4.6*hs, -.4*hs, lift))):
            solve_leg(side, sub(add(REST[IDS[f'leg_{side}_end']], foot), pelvis), rot)
    elif name == 'invoke':
        h = min(1, 1.4*math.sin(math.pi*t))**2
        turn('spine', (0, 1, 0), -7*h)
        turn('neck', (0, 1, 0), -6*h)
        turn('head', (0, 1, 0), -10*h)
        turn('arm_L_upper', (0, 1, 0), -58*h)
        turn('arm_L_upper', (1, 0, 0), 10*h)
        turn('arm_L_lower', (0, 1, 0), -38*h)
        turn('arm_L_end', (0, 1, 0), 80*h)
        turn('arm_R_upper', (0, 1, 0), -72*h)
        turn('arm_R_upper', (1, 0, 0), -24*h)
        turn('arm_R_lower', (0, 1, 0), -48*h)
        turn('arm_R_end', (0, 1, 0), 30*h)
        for i, b in enumerate(RELIC_BONES):
            turn(b, (1, 0, 0), 5*h*math.sin(i*2.1))
        turn('charms', (0, 1, 0), -14*h)
    elif name == 'recoil':
        p = math.sin(math.pi*t)**2
        turn('spine', (0, 1, 0), -12*p)
        turn('head', (0, 0, 1), -11*p)
        turn('head', (0, 1, 0), -6*p)
        turn('arm_R_upper', (1, 0, 0), -12*p)
        turn('arm_R_lower', (0, 1, 0), -20*p)
        turn('arm_L_upper', (1, 0, 0), 8*p)
        for i, b in enumerate(RELIC_BONES):
            turn(b, (0, 1, 0), -10*p)
        turn('charms', (0, 1, 0), 12*p)
    elif name == 'fall':
        # Limp seated collapse: the knees give, she sits onto the floor with
        # legs sliding forward under the robe, then slumps over them.
        s = smooth(t/.8)
        fs = smooth(t/.7)
        drop = (-2.5*s, 0, -22.4*s)
        shift[IDS['pelvis']] = drop
        for side, sign in (('L', 1), ('R', -1)):
            solve_leg(side, sub(add(REST[IDS[f'leg_{side}_end']], (20.5*fs, sign*1.6*fs, 0)), drop), rot,
                      add(mul(sub(REST[IDS[f'leg_{side}_lower']], REST[IDS[f'leg_{side}_upper']]), 1-fs), (0, 0, 13*fs)))
        slump = smooth((t-.2)/.72)
        turn('spine', (0, 1, 0), 44*slump)
        turn('spine', (1, 0, 0), 9*slump)
        turn('neck', (0, 1, 0), 20*slump)
        turn('head', (0, 1, 0), 30*slump)
        turn('head', (0, 0, 1), 16*slump)
        turn('head', (1, 0, 0), 12*slump)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), -34*slump)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*14*slump)
            turn(f'arm_{side}_lower', (0, 1, 0), 10*slump)
            turn(f'arm_{side}_end', (0, 1, 0), 30*slump)
        # The sickle hand sags into her lap rather than through the floor.
        turn('arm_R_lower', (0, 1, 0), -38*slump)
        turn('arm_R_end', (1, 0, 0), 35*slump)
        for i, b in enumerate(RELIC_BONES):
            turn(b, (0, 1, 0), -8*s)
        release = smooth((t-.08)/.72)
    if name not in ('advance', 'fall', 'slice'):
        shift[IDS['pelvis']] = (-.3, 0, -.6)
        for side, dx in (('L', 1.2), ('R', -1.2)):
            solve_leg(side, add(REST[IDS[f'leg_{side}_end']], (dx+.3, 0, .6)), rot)
    frame = [(*add(local, shift[i]), *rot[i], 1, 1, 1) for i, (n, p, local) in enumerate(BONES)]
    # Staff follows the left hand exactly while held (root child).
    hand = RIG.matrices(frame)[IDS['arm_L_end']]
    loc, q = hand
    if name == 'fall':
        # The loosening hand lets the staff slide: its foot never enters the
        # floor, then it topples about that foot and settles flat at her side.
        foot = add(loc, rotate(q, (0, 0, -GRIP_ABOVE_FOOT)))
        foot = (foot[0], foot[1], max(STAFF_REST_FOOT[2], foot[2]))
        slide = smooth(release*1.4)
        foot = add(mul(foot, 1-slide), mul(STAFF_REST_FOOT, slide))
        if release > 0:
            # Topple about the foot toward +X, turning the ring flat early.
            d = unit(add(mul(rotate(q, (0, 0, 1)), 1-release), mul((1, 0, 0), release)))
            xa = add(mul(rotate(q, (1, 0, 0)), 1-smooth(release*1.7)), mul((0, 0, 1), smooth(release*1.7)))
            xa = unit(sub(xa, mul(d, sum(i*j for i, j in zip(xa, d)))))
            q = basis_quat(xa, cross(d, xa), d)
        loc = add(foot, rotate(q, (0, 0, GRIP_ABOVE_FOOT)))
    si = IDS['staff']
    frame[si] = (*loc, *q, 1, 1, 1)
    return frame


def geometry():
    from .connected_skin import attach
    return assemble(mats.connected_atlas(attach(SLUG, build_parts(), weights)), weights)


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from .connected_skin import attach
    return mats.connected_atlas(attach(SLUG, build_parts(), weights), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_dar_priestess', material_path=SKIN)
    path = ROOT/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M32', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/dar_priestess/dar-priestess-animated.blend')
    out = ROOT/'assets/monsters/dar_priestess'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    print(importlib.import_module('tools.monster_models.dar_priestess_animation').build()['sha256'])
