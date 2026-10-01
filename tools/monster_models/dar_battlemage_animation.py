"""Original dar battlemage: ember-eyed battle caster built on dar family anatomy.

Presentation-only. Brogue CE owns fire, slowing, discord, targeting, drops,
turns and every outcome. Clips are cosmetic roles; the ember glow is a static
mesh-local material cue, never a light, spell or gameplay state.
"""
import hashlib
import json
import math
from . import iqm, dar_battlemage_materials as mats
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, rotate, assemble, sample_clips
from .dar_blademaster_animation import rings

SLUG = 'dar_battlemage'
SKIN = 'graphics/BRGDBMG.png'
MODEL = 'mod/BrogueDoom/models/monsters/33_dar_battlemage.iqm'
SHADER = 'shaders/dar-battlemage-embers.fp'
# Small, open casting hands and the scowling face need a finer fused cage.
SKIN_VOXEL_SIZE = .2
SKIN_FACE_BUDGET = 7000
HANDS = {'L': (3.4, 8.9, 30.6), 'R': (3.4, -8.9, 30.6)}
TOPKNOT = (-1.8, 0, 61.6)

SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 28)), ('spine', 'pelvis', (-.5, 0, 40)),
         ('neck', 'spine', (0, 0, 49)), ('head', 'neck', (.2, 0, 55))]
for side, sign in (('L', 1), ('R', -1)):
    parent = 'spine'
    for joint, point in zip(('upper', 'lower', 'end'), [(0, sign*6.3, 45.5), (.8, sign*8.3, 36.5), HANDS[side]]):
        SPECS.append((f'arm_{side}_{joint}', parent, point))
        parent = f'arm_{side}_{joint}'
for side, sign in (('L', 1), ('R', -1)):
    parent = 'pelvis'
    for joint, point in zip(('upper', 'lower', 'end'), [(0, sign*3.6, 28), (2, sign*4.4, 15), (0, sign*5.1, 2.4)]):
        SPECS.append((f'leg_{side}_{joint}', parent, point))
        parent = f'leg_{side}_{joint}'

COAT_ROWS = [(27.2, 0, 4.0, 5.3), (31, 0, 3.55, 4.6), (35, -.4, 3.5, 4.7), (40, -.5, 4.05, 5.9),
             (44, -.3, 4.25, 6.65), (46.2, 0, 3.45, 6.05), (47.6, 0, 2.45, 3.0), (48.3, 0, 2.2, 2.6)]
SKIRT_ROWS = [(8.2, .35, 6.9, 8.3), (12, .3, 6.4, 7.8), (18, .2, 5.7, 7.0), (24, .1, 4.9, 6.1), (29.8, 0, 4.15, 5.35)]
COLLAR_ROWS = [(46.4, 0, 2.75, 3.25), (48.6, -.05, 2.8, 3.45), (50.6, -.3, 3.5, 4.4), (53.2, -.6, 4.5, 5.7)]
BELT_Z = 29.6
TOME_ANGLE = -84


def _interp(rows, z, k):
    if z <= rows[0][0]:
        return rows[0][k]
    for a, b in zip(rows, rows[1:]):
        if a[0] <= z <= b[0]:
            return a[k]+(b[k]-a[k])*(z-a[0])/(b[0]-a[0])
    return rows[-1][k]


def ring_point(rows, a_deg, z, pad):
    a = math.radians(a_deg)
    return (_interp(rows, z, 1)+(_interp(rows, z, 2)+pad)*math.cos(a), (_interp(rows, z, 3)+pad)*math.sin(a), z)


SPECS += [('tome', 'pelvis', ring_point(COAT_ROWS, TOME_ANGLE, BELT_Z, .5)), ('topknot', 'head', TOPKNOT)]
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CLIPS = [('idle', 40, 20, True), ('advance', 32, 35, True), ('cut', 24, 35, False),
         ('conjure', 26, 35, False), ('recoil', 14, 35, False), ('fall', 36, 35, False)]


def palm(side):
    s = 1 if side == 'L' else -1
    h = HANDS[side]
    return add(h, (.35, s*.15, -1.0))


mats.HANDS.update({side: (palm(side), add(palm(side), (1.3, 0, -3.3))) for side in HANDS})


def CONNECTED_SKIN(name):
    return name in ('pelvis', 'torso') or name.startswith(('head_', 'shoulder_', 'arm_', 'leg_', 'hand_', 'foot_'))


def surface(name, rows, sides=36):
    p = Part(name)
    z0, z1 = rows[0][0], rows[-1][0]
    for z, cx, rx, ry in rows:
        for i in range(sides+1):
            a = math.tau*i/sides
            p.vertex((cx+rx*math.cos(a), ry*math.sin(a), z), 'fur', i/sides, (z-z0)/(z1-z0))
    w = sides+1
    for j in range(len(rows)-1):
        for i in range(sides):
            a = j*w+i
            p.faces.append((a, a+1, a+1+w, a+w))
    p.faces.append(tuple(reversed(range(sides))))
    p.faces.append(tuple((len(rows)-1)*w+i for i in range(sides)))
    return p


def shell(name, rows, a0, a1, thick, segs=24, flare=None):
    """Closed curved panel between angles a0..a1 (degrees, CCW from +X).

    Outer face samples the upper half of its atlas rect, inner face the lower.
    """
    p = Part(name)
    n = len(rows)
    grids = []
    for layer, (inset, vbase) in enumerate(((0, .5), (thick, 0))):
        grid = []
        for j, (z, cx, rx, ry) in enumerate(rows):
            row = []
            for i in range(segs+1):
                u = i/segs
                a = math.radians(a0+(a1-a0)*u)
                f = flare(u, j) if flare else 0
                row.append(p.vertex((cx+(rx+f-inset)*math.cos(a), (ry+f-inset)*math.sin(a), z), 'fur', u, vbase+.5*j/(n-1)))
            grid.append(row)
        grids.append(grid)
    o, q = grids
    for j in range(n-1):
        for i in range(segs):
            p.faces.append((o[j][i], o[j][i+1], o[j+1][i+1], o[j+1][i]))
            p.faces.append((q[j][i], q[j+1][i], q[j+1][i+1], q[j][i+1]))
        p.faces.append((o[j][0], o[j+1][0], q[j+1][0], q[j][0]))
        p.faces.append((o[j][segs], q[j][segs], q[j+1][segs], o[j+1][segs]))
    for i in range(segs):
        p.faces.append((o[n-1][i], o[n-1][i+1], q[n-1][i+1], q[n-1][i]))
        p.faces.append((o[0][i], q[0][i], q[0][i+1], o[0][i+1]))
    return p


def turned(p, centre, direction, degrees):
    q = axis(direction, math.radians(degrees))
    p.vertices = [add(centre, rotate(q, sub(v, centre))) for v in p.vertices]
    return p


def open_hand(s, side):
    """Open, tense casting hand with separated fingers (fused by the bake)."""
    sign = 1 if side == 'L' else -1
    c = palm(side)
    s.oval(f'hand_{side}_palm', c, (1.1, 1.35, 1.55), 'body', 20, 12)
    for i in range(4):
        off = (i-1.5)*.62
        base = add(c, (.25, sign*off, -1.2))
        pts = [(*base, .36), (*add(base, (.55, sign*off*.35, -1.35)), .33), (*add(base, (1.15, sign*off*.55, -2.4)), .28),
               (*add(base, (1.35, sign*off*.6, -3.0-.25*(1.5-abs(i-1.5)))), .16)]
        s.strand(f'hand_{side}_finger{i}', pts, 'body', 10, 3)
    s.strand(f'hand_{side}_thumb', [(*add(c, (.6, -sign*.7, .2)), .45), (*add(c, (1.5, -sign*1.3, -.6)), .36),
                                    (*add(c, (2.3, -sign*1.35, -1.4)), .2)], 'body', 10, 3)


def build_parts():
    s = Sculpt()
    # --- Connected anatomy ------------------------------------------------
    s.oval('pelvis', (0, 0, 28), (3.5, 4.6, 4.3))
    s.parts.append(rings('torso', [(27, 0, 3.5, 4.8), (31, 0, 3.1, 4.1), (35, -.4, 3.1, 4.2), (40, -.5, 3.6, 5.4),
                                   (44, -.3, 3.8, 6.2), (46, 0, 3, 5.6), (48, 0, 2, 2.4), (52, 0, 1.8, 1.8)]))
    s.parts.append(rings('head_cranium', [(50.4, 1, 1, 1.4), (51.3, 1, 1.9, 2), (52.7, .6, 2.5, 2.5), (54.5, .1, 2.9, 3.1),
                                          (56, .1, 2.95, 3.1), (58, -.1, 2.8, 2.8), (59.6, -.3, 2, 2.1), (60.2, -.4, .15, .2)]))
    for sign in (-1, 1):
        # Swept-back ears and a heavy, scowling brow.
        s.strand(f'head_ear_{sign}', [(-.4, sign*2.5, 55.6, 1.05), (-1.6, sign*4.3, 56.1, .82), (-3.6, sign*6.4, 57.2, .06)], 'body', 14, 4)
        s.strand(f'head_brow_{sign}', [(2.95, sign*.7, 56.2, .3), (2.82, sign*1.65, 56.62, .34), (2.25, sign*2.45, 56.95, .2)], 'body', 12)
        s.strand(f'head_cheek_{sign}', [(2.3, sign*1.9, 54.4, .45), (2.0, sign*2.4, 53.4, .3)], 'body', 10)
    for side, sign in (('L', 1), ('R', -1)):
        s.oval(f'shoulder_{side}', (0, sign*5.8, 45), (2.6, 2.6, 3))
        for limb in ('arm', 'leg'):
            points = [REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper', 'lower', 'end')]
            rs = (2.1, 1.5, 1.05) if limb == 'arm' else (2.35, 1.75, 1.25)
            s.strand(f'{limb}_{side}', [(*p, r) for p, r in zip(points, rs)], sides=18, samples=5)
        s.oval(f'foot_{side}', (1.8, sign*5.1, 1.7), (3.6, 1.85, 1.55), 'body', 24, 12)
        open_hand(s, side)
    # --- Face details -----------------------------------------------------
    for sign in (-1, 1):
        s.strand(f'detail_ear_{sign}', [(.15, sign*3.1, 55.7, .19), (-.9, sign*4.2, 56.1, .23), (-2.8, sign*5.8, 56.9, .04)], 'accent', 10)
        s.oval(f'detail_eye_socket_{sign}', (2.62, sign*1.62, 55.82), (.18, .7, .31), 'dark', 18, 10)
        s.oval(f'detail_iris_{sign}', (2.8, sign*1.62, 55.8), (.08, .3, .24), 'accent', 14, 8)
        s.oval(f'detail_lid_{sign}', (2.72, sign*1.62, 56.1), (.18, .74, .14), 'body', 16, 8)
        s.strand(f'detail_brow_{sign}', [(3.08, sign*.7, 56.42, .1), (2.94, sign*1.7, 56.84, .13), (2.34, sign*2.5, 57.08, .07)], 'dark', 8)
    s.strand('detail_mouth', [(3.1, -1.0, 52.95, .09), (3.45, 0, 52.72, .1), (3.1, 1.0, 52.95, .09)], 'dark', 10)
    # --- Hair: swept crest into a brass-bound topknot and a long tail ------
    tx, ty, tz = TOPKNOT
    for i in range(9):
        y = (i-4)*.34
        s.strand(f'hair_crest_{i}', [(2.0, y, 58.3-.3*abs(y), .34), (.6, y*1.05, 60.2, .5), (-.8, y*.8, 61.0, .5),
                                     (tx+.2, y*.4, tz, .4)], 'dark', 10, 4)
    s.oval('hair_topknot', (tx-.2, 0, tz+.5), (1.35, 1.2, 1.35), 'dark', 16, 10)
    s.strand('hairring', [(tx-.2+1.22*math.cos(math.tau*i/24), 1.1*math.sin(math.tau*i/24), tz-.15, .2)
                          for i in range(25)], 'bone', 6, 1)
    s.strand('hair_tail', [(tx-.9, 0, tz+1.7, .9), (-4.4, 0, 62.4, .85), (-6.0, 0, 59.2, .75), (-6.6, 0, 54.0, .6),
                           (-6.5, 0, 48.5, .38), (-6.0, 0, 44.2, .08)], 'dark', 12, 5)
    # --- Battle coat ----------------------------------------------------------
    s.parts.append(surface('coat', COAT_ROWS, 40))
    # Swallow-tailed skirt open at the front; lined in oxblood.
    for k, (a0, a1) in enumerate(((36, 172), (-172, -36))):
        s.parts.append(shell(f'skirt_{k}', SKIRT_ROWS, a0, a1, .32, 26,
                             lambda u, j: .25*math.sin(math.pi*u*5)**2*(1-j/4)))
    s.parts.append(shell('collar', COLLAR_ROWS, 42, 318, .3, 30))
    # Layered left pauldron, smaller right plate: an asymmetric caster's guard.
    for k, (c, r, tilt) in enumerate((((0, 6.6, 47.2), (3.8, 3.6, 1.1), 20), ((.05, 7.8, 45.9), (3.6, 3.35, 1.0), 32),
                                      ((.1, 8.9, 44.5), (3.3, 2.9, .9), 44))):
        turned(s.oval(f'pauldron_L_{k}', c, r, 'bone', 22, 12), c, (1, 0, 0), tilt)
    turned(s.oval('pauldron_R_0', (0, -6.9, 46.9), (3.2, 3.0, 1.0), 'bone', 22, 12), (0, -6.9, 46.9), (1, 0, 0), -24)
    # Forearm bracers with brass rings.
    for side, sign in (('L', 1), ('R', -1)):
        lo, en = REST[IDS[f'arm_{side}_lower']], REST[IDS[f'arm_{side}_end']]
        a, b = add(lo, mul(sub(en, lo), .3)), add(lo, mul(sub(en, lo), .86))
        s.strand(f'bracer_{side}', [(*a, 1.5), (*add(a, mul(sub(b, a), .5)), 1.42), (*b, 1.3)], 'cloth', 16, 3)
        for t, r in ((.0, 1.62), (1.0, 1.44)):
            p = add(a, mul(sub(b, a), t))
            d = unit(sub(b, a))
            s.strand(f'bracer_ring_{side}_{int(t)}', [(*sub(p, mul(d, .25)), r), (*add(p, mul(d, .25)), r)], 'bone', 16, 1)
    # Belt, buckle and chained grimoire.
    s.strand('belt', [(*ring_point(COAT_ROWS, 360*i/40, BELT_Z, .3), .5) for i in range(41)], 'cloth', 8, 1)
    bx, by, bz = ring_point(COAT_ROWS, 0, BELT_Z, .85)
    s.box('belt_buckle', (bx, by, bz), (.25, 1.0, .75), 'bone')
    top = ring_point(COAT_ROWS, TOME_ANGLE, BELT_Z-.4, .8)
    tome = (top[0]+.1, top[1]-1.7, 23.4)
    s.strand('tome_chain', [(*top, .13), (tome[0], tome[1]+.3, 26.2, .13), (tome[0], tome[1]+.3, 25.5, .13)], 'bone', 6, 3, ribbed=True)
    s.box('tome_cover', tome, (1.75, .62, 2.15), 'cloth')
    s.box('tome_page', (tome[0], tome[1], tome[2]), (1.84, .44, 2.05), 'cloth')
    for dx in (-1.6, 1.6):
        for dz in (-1.95, 1.95):
            s.oval(f'tome_corner_{dx}_{dz}', (tome[0]+dx, tome[1]-.62, tome[2]+dz), (.3, .12, .3), 'bone', 8, 6)
    s.box('tome_clasp', (tome[0]+1.8, tome[1], tome[2]), (.12, .5, .35), 'bone')
    parts = mats.repack(s.parts)
    for p in parts:
        p.vertices = [tuple(round(c, 6) for c in v) for v in p.vertices]
    return parts


def _cloth_weights(v, rows):
    x, y, z = v
    if z >= 28:
        if z < 35:
            t = (z-28)/7
            return [(IDS['pelvis'], 1-t), (IDS['spine'], t)]
        if z < 47:
            return [(IDS['spine'], 1)]
        t = max(0, min(1, (z-47)/5))
        return [(IDS['spine'], 1-.6*t), (IDS['neck'], .6*t)]
    a = max(0, min(1, (28-z)/22))**.8
    side = max(0, min(1, .5+y/6))
    ang = math.atan2(y/max(.1, _interp(rows, z, 3)), (x-_interp(rows, z, 1))/max(.1, _interp(rows, z, 2)))
    front = max(0, min(1, .5+.9*math.cos(ang)))
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
    if n.startswith('tome'):
        return [(IDS['tome'], 1)]
    if n.startswith(('hair_tail', 'hair_topknot', 'hairring')):
        return [(IDS['topknot'], 1)]
    if n.startswith(('head', 'detail', 'hair')):
        return [(IDS['head'], 1)]
    if n.startswith('collar'):
        return _cloth_weights(v, COLLAR_ROWS)
    if n.startswith(('coat', 'belt')):
        return _cloth_weights(v, COAT_ROWS)
    if n.startswith('skirt'):
        return _cloth_weights(v, SKIRT_ROWS)
    if n.startswith('pauldron'):
        side = n.split('_')[1]
        t = max(0, min(1, (abs(v[1])-4.5)/4))
        return [(IDS['spine'], 1-.75*t), (IDS[f'arm_{side}_upper'], .75*t)]
    if n.startswith('bracer'):
        side = n.split('_')[2] if n.startswith('bracer_ring') else n.split('_')[1]
        return [(IDS[f'arm_{side}_lower'], 1)]
    if n.startswith('shoulder_'):
        t = max(0, min(1, (abs(v[1])-4)/3))
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


def solve_leg(side, target, rotations):
    ids = [IDS[f'leg_{side}_{j}'] for j in ('upper', 'lower', 'end')]
    hip, knee, foot = [REST[i] for i in ids]
    a = math.dist(hip, knee)
    b = math.dist(knee, foot)
    distance = math.dist(target, hip)
    if not abs(a-b) < distance < a+b:
        raise ValueError(('unreachable battlemage foot', side, target, distance, a+b))
    direction = unit(sub(target, hip))
    along = (a*a-b*b+distance*distance)/(2*distance)
    pole = sub(knee, hip)
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


# Prone death: yaw onto the cell diagonal, then pitch face-down.
FALL_Q = qmul(axis((0, 0, 1), math.radians(38)), axis((0, 1, 0), math.radians(88)))
FALL_T = (-24.18, -16.65, 5.94)
FALL_LIFT = 2.0
FALL_ARM = -6
CUT_ARM = (-114, -14, -30, 30)


def smooth(x):
    x = max(0, min(1, x))
    return x*x*(3-2*x)


def guard(turn, k=1.0, phase=0.0):
    """Caster's ready guard: right palm raised before the chest, left hand low."""
    turn('arm_R_upper', (0, 1, 0), (-34+2*math.sin(phase))*k)
    turn('arm_R_upper', (1, 0, 0), 6*k)
    turn('arm_R_lower', (0, 1, 0), (-62+3*math.sin(phase+.7))*k)
    turn('arm_R_end', (0, 1, 0), 28*k)
    turn('arm_L_upper', (0, 1, 0), (-18+2*math.sin(phase+1.3))*k)
    turn('arm_L_upper', (1, 0, 0), 8*k)
    turn('arm_L_lower', (0, 1, 0), -34*k)
    turn('arm_L_end', (0, 1, 0), 18*k)


def pose(name, t):
    rot = [(0, 0, 0, 1) for _ in BONES]
    shift = [(0, 0, 0) for _ in BONES]

    def turn(b, d, deg):
        rot[IDS[b]] = qmul(rot[IDS[b]], axis(d, math.radians(deg)))
    phase = math.tau*t
    if name == 'idle':
        turn('spine', (0, 1, 0), 3+.6*math.sin(phase))
        turn('spine', (0, 0, 1), -6)
        turn('head', (0, 0, 1), 6+2*math.sin(phase))
        turn('head', (0, 1, 0), -2)
        guard(turn, 1, phase)
        turn('topknot', (0, 1, 0), 3*math.sin(phase))
        turn('tome', (1, 0, 0), 2*math.sin(phase+1))
    elif name == 'advance':
        bob = -.8+.3*math.cos(2*phase)
        for side, offset in (('L', 0), ('R', .5)):
            q = (t+offset) % 1
            if q < .6:
                dx, lift = 2-4*q/.6, 0
            else:
                u = (q-.6)/.4
                dx, lift = -2+4*u, 2*math.sin(math.pi*u)
            solve_leg(side, add(REST[IDS[f'leg_{side}_end']], (dx+.3, 0, lift-bob)), rot)
        shift[IDS['pelvis']] = (-.3, 0, bob)
        turn('spine', (0, 0, 1), 3*math.sin(phase))
        turn('spine', (0, 1, 0), 6)
        guard(turn, .8, phase*2)
        turn('topknot', (0, 1, 0), 7*math.sin(2*phase+.6))
        turn('topknot', (1, 0, 0), 4*math.cos(phase))
        turn('tome', (1, 0, 0), 10*math.sin(2*phase))
        turn('tome', (0, 1, 0), 6*math.cos(2*phase+.4))
    elif name == 'cut':
        # Cocked back, then a raking lunge: lead left foot steps out, the right
        # ember hand rakes far forward and across with clawed fingers, the left
        # arm is thrown back for balance. Peak pose sits on the middle frame.
        w = math.sin(math.pi*min(1, t/.4))**2 if t < .4 else 0
        h = math.exp(-((t-.52)/.16)**2)
        hs = smooth((t-.18)/.3)*(1-smooth((t-.74)/.24))
        lift = 1.6*(math.sin(math.pi*max(0, min(1, (t-.18)/.3)))+math.sin(math.pi*max(0, min(1, (t-.74)/.24))))
        guard(turn, 1-max(w, h, hs))
        turn('spine', (0, 0, 1), -24*w+30*h)
        turn('spine', (0, 1, 0), -6*w+20*h)
        turn('neck', (0, 0, 1), -10*h)
        turn('head', (0, 0, 1), -12*h)
        turn('head', (0, 1, 0), -10*h)
        uy, ux, ly, ey = CUT_ARM
        turn('arm_R_upper', (0, 1, 0), -40*w+uy*h)
        turn('arm_R_upper', (1, 0, 0), -55*w+ux*h)
        turn('arm_R_lower', (0, 1, 0), -95*w+ly*h)
        turn('arm_R_end', (0, 1, 0), 20*w+ey*h)
        turn('arm_L_upper', (0, 1, 0), 58*h)
        turn('arm_L_upper', (1, 0, 0), 30*h)
        turn('arm_L_lower', (0, 1, 0), -24*h)
        turn('topknot', (0, 1, 0), 18*h)
        turn('topknot', (0, 0, 1), -14*h)
        turn('tome', (1, 0, 0), 16*h)
        turn('tome', (0, 1, 0), 14*hs)
        pelvis = (-.4+3.6*hs, .6*hs, -1.0-2.4*hs)
        shift[IDS['pelvis']] = pelvis
        for side, foot in (('L', (2.2+5.2*hs, .8*hs, lift)), ('R', (-2.0-3.0*hs, -.5*hs, 0))):
            solve_leg(side, sub(add(REST[IDS[f'leg_{side}_end']], foot), pelvis), rot)
    elif name == 'conjure':
        h = min(1, 1.4*math.sin(math.pi*t))**2
        guard(turn, 1-h)
        turn('spine', (0, 1, 0), 10*h)
        turn('neck', (0, 1, 0), -4*h)
        turn('head', (0, 1, 0), -6*h)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), -84*h)
            turn(f'arm_{side}_upper', (1, 0, 0), -sign*10*h)
            turn(f'arm_{side}_lower', (0, 1, 0), -14*h)
            turn(f'arm_{side}_end', (0, 1, 0), -38*h)
        turn('topknot', (0, 1, 0), -8*h)
    elif name == 'recoil':
        p = math.sin(math.pi*t)**2
        guard(turn, 1-p)
        turn('spine', (0, 1, 0), -13*p)
        turn('head', (0, 0, 1), -12*p)
        turn('head', (0, 1, 0), -8*p)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), -48*p)
            turn(f'arm_{side}_upper', (1, 0, 0), -sign*12*p)
            turn(f'arm_{side}_lower', (0, 1, 0), -95*p)
        turn('topknot', (0, 1, 0), 14*p)
    elif name == 'fall':
        # Knees buckle, then the body pitches forward flat onto the floor
        # (laid on a diagonal to fit the cell): limp arms, ember hands down.
        k = smooth(t/.4)
        u = smooth((t-.26)/.62)
        guard(turn, 1-k)
        bend = k*(1-u)
        pelvis = (-2*bend, 0, -9*bend)
        shift[IDS['pelvis']] = pelvis
        for side in ('L', 'R'):
            solve_leg(side, sub(REST[IDS[f'leg_{side}_end']], pelvis), rot)
        turn('spine', (0, 1, 0), 30*bend+6*u)
        turn('neck', (0, 1, 0), -14*u)
        turn('head', (0, 0, 1), 70*u)
        turn('head', (0, 1, 0), 10*bend)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), -30*bend-FALL_ARM*u)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*16*u)
            turn(f'arm_{side}_lower', (0, 1, 0), -12*u)
            turn(f'arm_{side}_end', (0, 1, 0), 20*u)
        turn('topknot', (0, 0, 1), -40*u)
        turn('tome', (0, 1, 0), -30*u)
        fall_root = nlerp((0, 0, 0, 1), FALL_Q, u)
        rot[IDS['root']] = fall_root
        shift[IDS['root']] = add(mul(FALL_T, smooth(min(1, u*1.2))**.9), (0, 0, FALL_LIFT*math.sin(math.pi*u)))
    if name not in ('advance', 'fall', 'cut'):
        shift[IDS['pelvis']] = (-.4, 0, -1.0)
        for side, dx in (('L', 2.2), ('R', -2.0)):
            solve_leg(side, add(REST[IDS[f'leg_{side}_end']], (dx+.4, 0, 1.0)), rot)
    return [(*add(local, shift[i]), *rot[i], 1, 1, 1) for i, (n, p, local) in enumerate(BONES)]


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
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_dar_battlemage', material_path=SKIN)
    path = ROOT/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M33', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    shader=SHADER,
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/dar_battlemage/dar-battlemage-animated.blend')
    out = ROOT/'assets/monsters/dar_battlemage'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    print(importlib.import_module('tools.monster_models.dar_battlemage_animation').build()['sha256'])
