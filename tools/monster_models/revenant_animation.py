"""Original revenant: a massive hooded grave-specter that stalks without fear.

Cosmetic only. Brogue CE owns its immunity to weapons, its slow movement, every
attack and all outcomes; nothing here signals or changes them. The source says
"unholy specter", "stalks the deep places of the earth" and "impervious to
conventional attacks": the art answers with a heavy, broad-shouldered burial
shroud whose hem drags grave earth, a deep cowl framing a bone-pale skull, and
large bony hands. It is grounded (no flight flag) and fully opaque.
"""
import hashlib
import json
import math
from . import iqm, revenant_materials as mats
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit, cross
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips

SKIN = 'graphics/BRGREVNT.png'
MODEL = 'mod/BrogueDoom/models/monsters/47_revenant.iqm'
SKIN_FACE_BUDGET = 6400

SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 30)),
         ('spine', 'pelvis', (-1.0, 0, 38)), ('chest', 'spine', (-.5, 0, 46)),
         ('neck', 'chest', (3.0, 0, 51)), ('head', 'neck', (5.2, 0, 54)),
         ('jaw', 'head', (6.0, 0, 52.6))]
for side, sign in (('L', 1), ('R', -1)):
    for limb, parent, points in (
            ('arm', 'chest', [(.5, 13, 50), (2.5, 16.5, 38.5), (5.5, 17, 27.5)]),
            ('leg', 'pelvis', [(0, 4.5, 29.5), (1.6, 5.5, 16), (0, 6, 3.2)])):
        for joint, (x, y, z) in zip(('upper', 'lower', 'end'), points):
            name = f'{limb}_{side}_{joint}'
            SPECS.append((name, parent, (x, sign*y, z)))
            parent = name

RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CLIPS = [('idle', 40, 20, True), ('stalk', 32, 35, True), ('smash', 24, 35, False),
         ('rend', 26, 35, False), ('recoil', 14, 35, False), ('fall', 36, 35, False)]
ANKLE = REST[IDS['leg_L_end']][2]


def CONNECTED_SKIN(name):
    return name.startswith(('shroud', 'mantle', 'hood', 'sleeve_'))


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x-a)/(b-a)))
    return t*t*(3-2*t)


def rings(name, rows, sides, radius=None, lift=None):
    """Closed surface of horizontal elliptical rows (z, cx, rx, ry)."""
    p = Part(name)
    for j, (z, cx, rx, ry) in enumerate(rows):
        for i in range(sides):
            a = math.tau*i/sides
            k = radius(a, z) if radius else 1
            zz = z+(lift(a) if lift and j == 0 else 0)
            p.vertex((cx+rx*k*math.cos(a), ry*k*math.sin(a), zz), 'fur', i/sides, j/(len(rows)-1))
    for j in range(len(rows)-1):
        for i in range(sides):
            a, b = j*sides+i, j*sides+(i+1) % sides
            p.faces.append((a, b, b+sides, a+sides))
    bottom = p.vertex((rows[0][1], 0, rows[0][0]), 'fur', .5, 0)
    top = p.vertex((rows[-1][1], 0, rows[-1][0]), 'fur', .5, 1)
    last = (len(rows)-1)*sides
    for i in range(sides):
        p.faces.append((bottom, (i+1) % sides, i))
        p.faces.append((top, last+i, last+(i+1) % sides))
    return p


def hood(name='hood', centre=(5.2, 0, 55.2), radii=(5.1, 4.7, 5.7), thickness=.75, opening=50):
    """Thick open-front cowl: outer and inner shells stitched along their rims."""
    p = Part(name)
    cols, rows_ = 30, 16
    grids = []
    for layer, off in ((0, 0), (1, -thickness)):
        grid = []
        for j in range(rows_):
            th = math.radians(-38+(88+38)*j/(rows_-1))
            row = []
            for i in range(cols):
                ph = math.radians(opening+(360-2*opening)*i/(cols-1))
                rx, ry, rz = (r+off for r in radii)
                # Peaked crown swept back, and a brim that projects forward.
                peak = max(0, math.sin(th))**5
                brim = max(0, math.cos(ph))**2*2.0
                x = centre[0]+rx*math.cos(th)*math.cos(ph)-2.4*peak+brim
                y = centre[1]+ry*math.cos(th)*math.sin(ph)
                z = centre[2]+rz*math.sin(th)+1.6*peak
                row.append(p.vertex((x, y, z), 'fur', i/(cols-1), j/(rows_-1)))
            grid.append(row)
        grids.append(grid)
    o, n = grids
    for j in range(rows_-1):
        for i in range(cols-1):
            p.faces.append((o[j][i], o[j][i+1], o[j+1][i+1], o[j+1][i]))
            p.faces.append((n[j][i], n[j+1][i], n[j+1][i+1], n[j][i+1]))
    for i in range(cols-1):
        p.faces.append((o[0][i], n[0][i], n[0][i+1], o[0][i+1]))
        p.faces.append((o[-1][i], o[-1][i+1], n[-1][i+1], n[-1][i]))
    for j in range(rows_-1):
        p.faces.append((o[j][0], o[j+1][0], n[j+1][0], n[j][0]))
        p.faces.append((o[j][-1], n[j][-1], n[j+1][-1], o[j+1][-1]))
    return p


def fold(a, z):
    # Heavy vertical folds that deepen toward the shredded lower shroud.
    t = smooth(46, 12, z)
    return 1+t*(.08*math.sin(a*9+z*.05)+.04*math.sin(a*17+1.3))


def torn(a):
    return 2.6*max(0, math.sin(a*6+.7))**2+1.2*max(0, math.sin(a*13+2))**2


def mantle_hem(a):
    return 3.4*max(0, math.sin(a*6+.4))**3+1.1*max(0, math.sin(a*15+1))**2


SHROUD_ROWS = [(13, -.8, 6.4, 8.6), (20, -.9, 6.6, 8.9), (28, -1.1, 6.8, 9.2), (35, -1.4, 7.4, 10.2),
               (42, -1.2, 8.0, 12.0), (47, -.4, 7.8, 13.2), (51, .8, 6.4, 12.0), (53.5, 1.6, 4.4, 7.5),
               (55.2, 2.3, 2.6, 4.2)]


def shroud_at(z):
    """Interpolated (cx, rx, ry) of the shroud cage at height z."""
    rows = SHROUD_ROWS
    z = max(rows[0][0], min(rows[-1][0], z))
    for (z0, *a), (z1, *b) in zip(rows, rows[1:]):
        if z <= z1:
            t = (z-z0)/(z1-z0)
            return tuple(x+(y-x)*t for x, y in zip(a, b))
    return tuple(rows[-1][1:])


def ribbon(name, path, widths, thickness, tile='paw'):
    """Closed flat strip: path of (point, outward normal); width runs across."""
    p = Part(name)
    n = len(path)
    for i, ((c, out), w) in enumerate(zip(path, widths)):
        tangent = unit(sub(path[min(i+1, n-1)][0], path[max(i-1, 0)][0]))
        out = unit(sub(out, mul(tangent, sum(a*b for a, b in zip(out, tangent)))))
        across = unit(cross(tangent, out))
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p.vertex(add(c, add(mul(out, sx*thickness/2), mul(across, sy*max(.03, w)/2))), tile, i/(n-1), (sy+1)/2)
    for i in range(n-1):
        for k in range(4):
            a, b = i*4+k, i*4+(k+1) % 4
            p.faces.append((a, b, b+4, a+4))
    p.faces.append((3, 2, 1, 0))
    last = (n-1)*4
    p.faces.append((last, last+1, last+2, last+3))
    return p


def build_parts():
    s = Sculpt()
    s.parts.append(rings('shroud', SHROUD_ROWS, 44, fold, lambda a: 1.2*torn(a)))
    # A torn over-layer of wrappings ending in a ragged edge at the thighs.
    s.parts.append(rings('shroud_layer', [(17, -1.0, 7.2, 9.6), (23, -1.0, 7.3, 9.7), (31, -1.2, 7.4, 10.0),
                                          (35, -1.4, 7.6, 10.4)], 40, fold, torn))
    # Mantle mass rises high and broad behind the lowered, forward-thrust head.
    s.parts.append(rings('mantle', [
        (42.5, -2.0, 9.2, 15.2), (46.5, -1.8, 9.6, 16.6), (50.5, -1.8, 9.2, 17.2),
        (55, -2.4, 7.6, 15.0), (58.5, -3.0, 5.6, 10.5), (61, -3.4, 3.0, 5.0)], 40, None, mantle_hem))
    s.parts.append(hood())
    for side, sign in (('L', 1), ('R', -1)):
        pts = [REST[IDS[f'arm_{side}_{j}']] for j in ('upper', 'lower', 'end')]
        cuff = add(pts[2], (.2, sign*.1, -.8))
        s.strand(f'sleeve_{side}', [(*pts[0], 3.1), (*pts[1], 2.55), (*add(pts[2], (0, 0, 1.5)), 2.9), (*cuff, 3.5)], 'cloth', 20, 5)
        # Aged bone hand hanging from the cuff: palm, four long fingers ending
        # in hooked talons, and a hooked thumb.
        s.oval(f'hand_{side}_palm', (5.3, sign*15.9, 26.4), (1.5, 1.45, 2.5), 'bone', 14, 10)
        for i in range(4):
            y = sign*(15.0+i*.62)
            s.strand(f'hand_{side}_finger{i}', [(5.5, y, 24.6, .5), (6.8, y+sign*.1, 22.4, .42),
                                                (6.9, y+sign*.15, 20.4, .34), (6.1, y+sign*.2, 18.9, .27)], 'bone', 8, 3)
            s.strand(f'nail_{side}_{i}', [(6.1, y+sign*.2, 19.0, .28), (5.6, y+sign*.2, 16.9, .22),
                                          (4.4, y+sign*.2, 15.7, .12), (3.3, y+sign*.2, 16.1, .02)], 'dark', 6, 2)
        s.strand(f'hand_{side}_thumb', [(6.0, sign*14.4, 26.2, .55), (7.3, sign*13.9, 24.6, .42), (7.6, sign*14.1, 23.0, .3)], 'bone', 8, 3)
        s.strand(f'nail_{side}_thumb', [(7.6, sign*14.1, 23.1, .3), (7.6, sign*14.2, 21.3, .2), (6.7, sign*14.3, 20.1, .1),
                                        (5.8, sign*14.4, 20.4, .02)], 'dark', 6, 2)
        # Torn rags hanging from the cuff.
        for i, (dy, length) in enumerate(((-1.6, 6.5), (1.4, 8.5))):
            root = add(cuff, (-1.6, sign*dy, -1.2))
            s.strand(f'rag_{side}_{i}', [(*root, .7), (root[0]-.8, root[1], root[2]-length*.5, .55), (root[0]-1.4, root[1]+sign*.3, root[2]-length, .06)], 'cloth', 8, 3)
    # Shredded lower shroud: two rings of torn strips that taper and fade out
    # before the floor, hiding the legs; the specter has no visible feet.
    for ring, (count, inset, top) in enumerate(((20, .15, 15.5), (16, -.9, 14.5))):
        for i in range(count):
            a = math.tau*(i+.5*ring)/count
            h = ((i*7+ring*3) % 5)/4
            end = 1.4+5.5*h
            cx, rx, ry = shroud_at(top)
            path, widths = [], []
            for j in range(6):
                t = j/5
                z = top+(end-top)*t
                flare = 1+.12*t+.04*math.sin(i*1.7)
                sway = .5*math.sin(i*2.3+t*3)*t
                ang = a+.06*sway
                c = (cx+(rx+inset)*flare*math.cos(ang), (ry+inset)*flare*math.sin(ang), z)
                path.append((c, (math.cos(ang)/rx, math.sin(ang)/ry, 0)))
                widths.append((2.5 if ring == 0 else 2.2)*(1-.85*t**1.4))
            s.parts.append(ribbon(f'rag_hem_{ring}_{i}', path, widths, .32))
    # Binding strips wound diagonally across the torso wrappings.
    for i, (a0, turns, z0, z1) in enumerate(((.3, .95, 21, 33), (2.5, .9, 27, 40), (4.1, .85, 34, 45.5), (1.2, .8, 18, 26))):
        path, widths = [], []
        for j in range(33):
            t = j/32
            a = a0+math.tau*turns*t
            z = z0+(z1-z0)*t
            cx, rx, ry = shroud_at(z)
            pad = .42 if z > 17 else .9
            path.append(((cx+(rx+pad)*math.cos(a), (ry+pad)*math.sin(a), z), (math.cos(a)/rx, math.sin(a)/ry, 0)))
            widths.append(1.5)
        s.parts.append(ribbon(f'bind_{i}', path, widths, .36))
    # Skull deep in the cowl: cranium, maxilla, long mandible, brow and cheeks.
    s.oval('skull_cranium', (2.8, 0, 61.6), (3.3, 3.0, 3.6), 'bone', 20, 12)
    s.oval('skull_face', (4.5, 0, 59.4), (1.8, 2.3, 2.2), 'bone', 18, 10)
    s.oval('skull_jaw', (4.3, 0, 56.5), (1.75, 1.85, 1.75), 'bone', 16, 10)
    s.strand('skull_chin', [(5.5, -1.0, 55.6, .55), (5.95, 0, 55.2, .62), (5.5, 1.0, 55.6, .55)], 'bone', 8, 3)
    s.strand('skull_brow', [(5.0, -2.6, 61.6, .5), (5.95, -1.4, 61.25, .66), (6.25, 0, 60.75, .6), (5.95, 1.4, 61.25, .66), (5.0, 2.6, 61.6, .5)], 'bone', 10, 4)
    for sign in (-1, 1):
        s.strand(f'skull_cheek_{sign}', [(3.6, sign*2.7, 59.9, .45), (5.2, sign*2.2, 59.6, .5), (5.9, sign*1.3, 59.2, .3)], 'bone', 8, 3)
        s.oval(f'skull_socket_{sign}', (5.8, sign*1.3, 60.3), (.6, .95, .66), 'dark', 14, 8)
        s.oval(f'pupil_{sign}', (6.2, sign*1.25, 60.25), (.1, .14, .14), 'glow', 6, 4)
    s.oval('skull_nose', (6.3, 0, 59.2), (.32, .42, .6), 'dark', 10, 6)
    for i in range(8):
        y = (i-3.5)*.42
        s.strand(f'skull_tooth_up{i}', [(6.02-.06*abs(i-3.5), y, 58.35, .19), (6.05-.06*abs(i-3.5), y, 57.6, .12)], 'bone', 6, 2)
        s.strand(f'skull_tooth_lo{i}', [(5.9-.07*abs(i-3.5), y, 56.4, .17), (5.95-.07*abs(i-3.5), y, 57.3, .1)], 'bone', 6, 2)
    for p in s.parts:
        if p.name.startswith(('hand_', 'nail_')):
            sign = 1 if p.vertices[0][1] > 0 else -1
            p.vertices = [add(v, (1.0, sign*1.2, -2.0)) for v in p.vertices]
        elif p.name.startswith(('skull', 'pupil')):
            p.vertices = [add(v, SKULL_SHIFT) for v in p.vertices]
        p.vertices = [tuple(round(c, 6) for c in v) for v in p.vertices]
    return s.parts


SKULL_SHIFT = (1.6, 0, -5.3)


def _normalize(rows):
    acc = {}
    for b, w in rows:
        if w > 1e-7:
            acc[b] = acc.get(b, 0)+w
    rows = sorted(acc.items(), key=lambda r: (-r[1], r[0]))[:4]
    total = math.fsum(w for b, w in rows)
    q = [(b, round(w/total, 6)) for b, w in rows]
    q[-1] = (q[-1][0], round(1-math.fsum(w for b, w in q[:-1]), 6))
    return sorted(q, key=lambda r: r[0])


def chain(point, names):
    """Joint-centred blend along a parent-to-child chain of bone names."""
    ids = [IDS[n] for n in names]
    best = None
    for j in range(len(ids)-1):
        a, b = REST[ids[j]], REST[ids[j+1]]
        d = sub(b, a)
        t = max(0, min(1, sum(x*y for x, y in zip(sub(point, a), d))/sum(x*x for x in d)))
        dist = math.dist(point, add(a, mul(d, t)))
        if best is None or dist < best[0]-1e-9:
            best = (dist, j, t)
    _, j, t = best
    if t > .7 and j+1 < len(ids):
        s = (t-.7)/.3*(1 if j+1 == len(ids)-1 else .5)
        return [(ids[j], 1-s), (ids[j+1], s)]
    if t < .3 and j > 0:
        s = (.3-t)/.3*.5
        return [(ids[j-1], s), (ids[j], 1-s)]
    return [(ids[j], 1)]


def shroud_weights(v, upper=('pelvis', 'spine', 'chest', 'neck')):
    x, y, z = v
    if z >= 30:
        rows = chain((-.6, 0, z), list(upper))
        side = 'L' if y > 0 else 'R'
        t = smooth(8.5, 12.5, abs(y))*smooth(44, 50, z)*.85
        return _normalize([(b, w*(1-t)) for b, w in rows]+[(IDS[f'arm_{side}_upper'], t)])
    # Skirt: front cloth drapes over the thighs and knees; the back hangs from
    # the pelvis to the heels, so kneeling never swings it through the floor.
    a = smooth(30, 4, z)**.8
    share_l = max(0, min(1, .5+y/7))
    ang = math.atan2(y/9.0, (x+.5)/6.8)
    front = max(0, min(1, .5+.9*math.cos(ang)))
    a = a+(1-a)*front*.65*min(1, (30-z)/4)
    out = [(IDS['pelvis'], 1-a)]
    for s, share in (('L', share_l), ('R', 1-share_l)):
        if share <= 0:
            continue
        ids = [IDS[f'leg_{s}_{j}'] for j in ('upper', 'lower', 'end')]
        zz = max(REST[ids[2]][2], min(REST[ids[0]][2], z))
        ref = (REST[ids[0]][0]+(REST[ids[1]][0]-REST[ids[0]][0])*max(0, min(1, (29.5-zz)/13.5)), REST[ids[0]][1], zz)
        for b, w in RIG.chain_weights(ref, ids):
            out.append((b, a*share*front*w))
        out.append((ids[2], a*share*(1-front)))
    return _normalize(out)


def weights(part, v, uv):
    n = part.name
    side = 'L' if v[1] > 0 else 'R'
    if n.startswith(('skull', 'pupil')):
        if n.startswith(('skull_jaw', 'skull_chin', 'skull_tooth_lo')):
            return [(IDS['jaw'], 1)]
        return [(IDS['head'], 1)]
    if n == 'hood':
        t = smooth(52.5, 55.5, v[2])
        return _normalize([(IDS['neck'], 1-t), (IDS['head'], t)])
    if n.startswith(('shroud', 'rag_hem', 'bind_')):
        return shroud_weights(v)
    if n.startswith('mantle'):
        return shroud_weights(v, ['pelvis', 'spine', 'chest'])
    if n.startswith('sleeve_'):
        return _normalize(chain(v, ['chest', f'arm_{side}_upper', f'arm_{side}_lower', f'arm_{side}_end']))
    if n.startswith(('hand_', 'nail_', 'rag_')):
        return [(IDS[f'arm_{side}_end'], 1)]
    raise KeyError(n)


def solve_leg(side, target, rot, hip_shift):
    """Two-link leg IK in the (unrotated, shifted) pelvis frame."""
    ids = [IDS[f'leg_{side}_{j}'] for j in ('upper', 'lower', 'end')]
    hip, knee, foot = [REST[i] for i in ids]
    target = sub(target, hip_shift)
    a, b, dist = math.dist(hip, knee), math.dist(knee, foot), math.dist(target, hip)
    if not abs(a-b) < dist < a+b:
        raise ValueError(('unreachable revenant foot', side, target, dist, a+b))
    direction = unit(sub(target, hip))
    along = (a*a-b*b+dist*dist)/(2*dist)
    pole = sub(knee, hip)
    bend = unit(sub(pole, mul(direction, sum(x*y for x, y in zip(pole, direction)))))
    nk = add(hip, add(mul(direction, along), mul(bend, math.sqrt(max(0, a*a-along*along)))))
    upper = between(sub(knee, hip), sub(nk, hip))
    lower = between(sub(foot, knee), sub(target, nk))
    rot[ids[0]] = upper
    rot[ids[1]] = qmul(inverse(upper), lower)
    rot[ids[2]] = inverse(lower)


def keys(t, frames):
    """Smoothstep interpolation through (time, value) keys."""
    for (t0, a), (t1, b) in zip(frames, frames[1:]):
        if t <= t1:
            return a+(b-a)*smooth(t0, t1, t)
    return frames[-1][1]


def pose(name, t):
    rot = [(0, 0, 0, 1) for _ in BONES]
    pelvis = [0.0, 0.0, 0.0]
    feet = {s: list(REST[IDS[f'leg_{s}_end']]) for s in ('L', 'R')}

    def turn(b, d, deg):
        rot[IDS[b]] = qmul(rot[IDS[b]], axis(d, math.radians(deg)))
    phase = math.tau*t
    if name == 'idle':
        breathe = math.sin(phase)
        pelvis[2] = -.35+.35*math.cos(phase)
        turn('spine', (0, 1, 0), 2+1.5*breathe)
        turn('chest', (0, 1, 0), 1.5*breathe)
        turn('neck', (0, 1, 0), -2)
        turn('head', (0, 0, 1), 9*math.sin(phase))
        turn('head', (0, 1, 0), 3*math.sin(2*phase))
        turn('jaw', (0, 1, 0), 2+2*math.sin(2*phase))
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), 2.5*math.sin(phase+sign))
            turn(f'arm_{side}_end', (0, 1, 0), -6+5*math.sin(phase+sign*1.3))
    elif name == 'stalk':
        # Slow, heavy, relentless plod: long planted stance, deep bob.
        for side, offset in (('L', 0), ('R', .5)):
            q = (t+offset) % 1
            if q < .6:
                dx, lift = 4.5-9*q/.6, 0
            else:
                u = (q-.6)/.4
                dx, lift = -4.5+9*u, 3*math.sin(math.pi*u)
            feet[side][0] += dx
            feet[side][2] += lift
            turn(f'arm_{side}_upper', (0, 1, 0), -14*math.cos(phase+offset*math.tau+math.pi))
            turn(f'arm_{side}_lower', (0, 1, 0), -6-4*math.cos(phase+offset*math.tau+math.pi))
        pelvis[1] = .9*math.sin(phase)
        pelvis[2] = -1.1+.9*math.cos(2*phase)
        turn('spine', (0, 1, 0), 14)
        turn('spine', (0, 0, 1), 5*math.sin(phase))
        turn('chest', (1, 0, 0), -4*math.sin(phase))
        turn('neck', (0, 1, 0), -6)
        turn('head', (0, 0, 1), -4*math.sin(phase))
    elif name == 'smash':
        # Middle frame: both fists raised over the cowl; then a crushing slam.
        up = keys(t, [(0, 0), (.5, 1), (.72, 0), (1, 0)])
        down = keys(t, [(0, 0), (.5, 0), (.72, 1), (1, 0)])
        pelvis[2] = -1*up-3.2*down
        turn('spine', (0, 1, 0), -10*up+7*down)
        turn('chest', (0, 1, 0), -6*up+10*down)
        turn('neck', (0, 1, 0), -8*up+6*down)
        turn('head', (0, 1, 0), -12*up+8*down)
        turn('jaw', (0, 1, 0), 2+14*up+6*down)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (1, 0, 0), sign*(-14*up-6*down))
            turn(f'arm_{side}_upper', (0, 1, 0), -162*up-22*down)
            turn(f'arm_{side}_lower', (0, 1, 0), -22*up-12*down-100*math.sin(math.pi*up)**.7)
            turn(f'arm_{side}_end', (0, 1, 0), -25*up+20*down)
    elif name == 'rend':
        # Middle frame: hunched low, both claws raking forward at waist height.
        k = keys(t, [(0, 0), (.25, .35), (.5, 1), (.75, .6), (1, 0)])
        wind = keys(t, [(0, 0), (.25, 1), (.5, 0), (1, 0)])
        pelvis[0] = -2*k
        pelvis[2] = -3.5*k
        feet['R'][0] += 3*k
        turn('spine', (0, 1, 0), -6*wind+16*k)
        turn('spine', (0, 0, 1), 14*wind-10*k)
        turn('chest', (0, 1, 0), 8*k)
        turn('neck', (0, 1, 0), -10*k)
        turn('head', (0, 1, 0), -14*k)
        turn('jaw', (0, 1, 0), 2+18*k)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), 22*wind-30*k)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*(18*wind-8*k))
            turn(f'arm_{side}_lower', (0, 1, 0), -18*wind-6*k)
            turn(f'arm_{side}_end', (0, 1, 0), -35*k)
    elif name == 'recoil':
        r = math.sin(math.pi*t)**2
        pelvis[0] = -1.8*r
        pelvis[2] = -1.2*r
        turn('spine', (0, 1, 0), -13*r)
        turn('chest', (0, 1, 0), -6*r)
        turn('head', (0, 1, 0), -20*r)
        turn('head', (0, 0, 1), 10*r)
        turn('jaw', (0, 1, 0), 2+12*r)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), -32*r)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*17*r)
            turn(f'arm_{side}_lower', (0, 1, 0), -24*r)
    elif name == 'fall':
        # The legs give way and slide forward under the shroud (middle frame:
        # sagging mid-collapse); it lands seated and folds face-down over them.
        sag = keys(t, [(0, 0), (.5, .55), (.85, 1), (1, 1)])
        fold = keys(t, [(0, 0), (.3, 0), (1, 1)])
        pelvis[0] = -FALL_BACK*sag
        pelvis[2] = -FALL_DROP*sag
        for s in ('L', 'R'):
            feet[s][0] += FEET_FWD*sag
        turn('spine', (0, 1, 0), FALL_SPINE*fold)
        turn('chest', (0, 1, 0), FALL_CHEST*fold)
        turn('neck', (0, 1, 0), 10*fold)
        turn('head', (0, 1, 0), FALL_HEAD*fold)
        turn('head', (0, 0, 1), 16*fold)
        turn('jaw', (0, 1, 0), 2+12*fold)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), FALL_ARM*fold)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*FALL_SPREAD*fold)
            turn(f'arm_{side}_lower', (0, 1, 0), FALL_ELBOW*fold)
            turn(f'arm_{side}_end', (0, 1, 0), 20*fold)
    for s in ('L', 'R'):
        solve_leg(s, tuple(feet[s]), rot, tuple(pelvis))
    frame = []
    for i, (n, p, local) in enumerate(BONES):
        loc = add(local, tuple(pelvis)) if n == 'pelvis' else local
        frame.append((*loc, *rot[i], 1, 1, 1))
    return frame


FALL_BACK, FALL_DROP, FEET_FWD = 7, 21, 16
FALL_SPINE, FALL_CHEST, FALL_HEAD = 85, 30, 20
FALL_ARM, FALL_SPREAD, FALL_ELBOW = 0, 20, -50


def _connected():
    from .connected_skin import attach
    return attach('revenant', build_parts(), weights)


def geometry():
    parts = mats.bake(_connected(), weights, mats.pigment)
    return assemble(parts, weights)


def matrices(frame):
    return RIG.matrices(frame)


def deform(v, w, frame):
    return RIG.deform(v, w, frame)


def animation_data(v, w):
    return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    return mats.bake(_connected(), weights, mats.pigment, True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_revenant', material_path=SKIN)
    path = ROOT/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M47', format='IQM v2', runtimeModel=MODEL, sha256=hashlib.sha256(data).hexdigest(),
                    skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/revenant/revenant-animated.blend')
    out = ROOT/'assets/monsters/revenant'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    print(importlib.import_module('tools.monster_models.revenant_animation').build()['sha256'])
