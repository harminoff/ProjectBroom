"""Original lich: a desiccated sorcerer-king bound to the phylactery on his breast.

Cosmetic only. Brogue CE owns the lich's fire bolts, summoning, distance keeping,
its phylactery link, resurrection and every outcome; nothing here signals or
changes them. The source says "desiccated form of an ancient sorcerer",
"commands the obedience of the infernal planes" and "anchored to reality by a
phylactery that is always in his possession"; Brogue gives the lich and its
gem the same green lich light. The art answers with a gaunt, upright king in
a gold-trimmed royal cope and brocade stole, leathery mummified skin, a tall
spiked crown grown onto the skull, a thin forked beard, gold-ringed claws and
a caged green gem hung over the sternum that the left hand guards. Only the
gem and the eye pinpoints are fullbright (painted key + shader); nothing casts
light. Grounded and opaque.
"""
import hashlib
import json
import math
from . import iqm, lich_materials as mats
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips
from .revenant_animation import rings, ribbon, smooth, keys

SLUG = 'lich'
SKIN = 'graphics/BRGLICH.png'
MODEL = 'mod/BrogueDoom/models/monsters/40_lich.iqm'
SHADER = 'shaders/lich-phylactery.fp'
SKIN_FACE_BUDGET = 5600

SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 30)),
         ('spine', 'pelvis', (-.5, 0, 38)), ('chest', 'spine', (-.5, 0, 46)),
         ('neck', 'chest', (.4, 0, 51.5)), ('head', 'neck', (1.0, 0, 55)),
         ('jaw', 'head', (1.6, 0, 54.6))]
for side, sign in (('L', 1), ('R', -1)):
    for limb, parent, points in (
            ('arm', 'chest', [(0, 8.3, 49.5), (1.2, 11.2, 38.8), (3.0, 12.4, 28.5)]),
            ('leg', 'pelvis', [(0, 4.0, 29.5), (1.4, 4.8, 16), (0, 5.2, 3.2)])):
        for joint, (x, y, z) in zip(('upper', 'lower', 'end'), points):
            name = f'{limb}_{side}_{joint}'
            SPECS.append((name, parent, (x, sign*y, z)))
            parent = name

RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CLIPS = [('idle', 40, 20, True), ('stride', 32, 35, True), ('touch', 24, 35, False),
         ('incant', 26, 35, False), ('recoil', 14, 35, False), ('crumble', 36, 35, False)]
ANKLE = REST[IDS['leg_L_end']][2]

# Floor-length robe (z, cx, rx, ry); the back pools into a short train.
ROBE_ROWS = [(.6, -2.2, 10.2, 11.2), (4, -1.8, 9.2, 10.2), (12, -1.3, 7.6, 8.8), (20, -1.0, 6.5, 7.8),
             (28, -.8, 5.8, 7.3), (34, -.8, 5.5, 7.1), (40, -.8, 5.3, 7.7), (46, -.6, 5.0, 8.6),
             (49.5, -.3, 4.0, 7.2), (51.5, 0, 2.4, 3.4), (52.6, .2, 1.4, 2.0)]
# Open-fronted royal cope over the shoulders, its hem cut in points.
COPE_ROWS = [(38.5, -1.2, 7.4, 13.0), (42, -1.1, 7.6, 14.0), (45.5, -1.0, 7.4, 14.2), (48.5, -.9, 6.6, 12.6),
             (50.8, -.7, 5.0, 9.4), (52.4, -.4, 3.2, 5.2)]
GEM = (6.0, 0, 40.8)
CROWN_Z = 60.1


def CONNECTED_SKIN(name):
    return name == 'robe' or name.startswith('sleeve_')


def _interp(rows, z, k):
    if z <= rows[0][0]:
        return rows[0][k]
    for a, b in zip(rows, rows[1:]):
        if a[0] <= z <= b[0]:
            return a[k]+(b[k]-a[k])*(z-a[0])/(b[0]-a[0])
    return rows[-1][k]


def robe_at(z):
    return tuple(_interp(ROBE_ROWS, z, k) for k in (1, 2, 3))


def train(a, z):
    return 1+.42*max(0.0, -math.cos(a))**2*smooth(16, 0, z)+.035*math.sin(a*10+z*.04)*smooth(40, 8, z)


def cope_point(deg, j, inset=0.0, rows=COPE_ROWS):
    z, cx, rx, ry = rows[j]
    a = math.radians(deg)
    return (cx+(rx-inset)*math.cos(a), (ry-inset)*math.sin(a), z)


def cope_hem(u):
    """Pointed, tattered hem (shared with the paint so the frayed edge follows it)."""
    return mats.cope_hem(u)


def cope():
    """Closed, thick open-front cope between 42 and 318 degrees."""
    p = Part('cope')
    segs, n = 44, len(COPE_ROWS)
    a0, a1 = 44, 316
    grids = []
    for inset in (0.0, .45):
        grid = []
        for j in range(n):
            row = []
            for i in range(segs+1):
                u = i/segs
                deg = a0+(a1-a0)*u
                x, y, z = cope_point(deg, j, inset)
                if j == 0:
                    z += cope_hem(u)
                row.append(p.vertex((x, y, z), 'fur', u, j/(n-1)))
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


def claw_hand(s, side, wrist, ringed=True):
    """Long desiccated hand hanging from the wrist: palm, four hooked fingers,
    long dark nails, a thumb and gold rings on two fingers."""
    sign = 1 if side == 'L' else -1
    wx, wy, wz = wrist
    s.oval(f'hand_{side}_palm', (wx+.5, wy, wz-2.2), (1.35, .8, 2.0), 'body', 14, 10)
    for i in range(4):
        dx = (i-1.5)*.7
        base = (wx+.5+dx, wy+sign*.1, wz-3.8)
        mid = (base[0]+.5+.15*dx, base[1], base[2]-2.4)
        tip = (base[0]+1.3+.2*dx, base[1]-sign*.2, base[2]-4.5-.3*(1.5-abs(i-1.5)))
        s.strand(f'hand_{side}_finger{i}', [(*base, .36), (*mid, .3), (*tip, .22)], 'body', 8, 3)
        s.strand(f'nail_{side}_{i}', [(*tip, .2), (tip[0]+.6, tip[1], tip[2]-1.1, .14), (tip[0]+.1, tip[1], tip[2]-2.2, .02)], 'dark', 6, 2)
        if ringed and i in (1, 2):
            c = add(base, (.18, 0, -1.0))
            s.strand(f'ring_{side}_{i}', [(c[0]+.42*math.cos(math.tau*k/12), c[1]+.42*math.sin(math.tau*k/12), c[2], .15)
                                          for k in range(13)], 'bone', 4, 1)
    thumb = (wx+1.1, wy-sign*.7, wz-2.4)
    s.strand(f'hand_{side}_thumb', [(*thumb, .4), (thumb[0]+1.2, thumb[1]-sign*.4, thumb[2]-1.6, .3),
                                    (thumb[0]+1.6, thumb[1]-sign*.4, thumb[2]-3.0, .2)], 'body', 8, 3)
    s.strand(f'nail_{side}_thumb', [(thumb[0]+1.6, thumb[1]-sign*.4, thumb[2]-3.0, .19), (thumb[0]+1.9, thumb[1]-sign*.4, thumb[2]-4.0, .1),
                                    (thumb[0]+1.4, thumb[1]-sign*.4, thumb[2]-4.8, .02)], 'dark', 6, 2)


def build_parts():
    s = Sculpt()
    s.parts.append(rings('robe', ROBE_ROWS, 48, train))
    for side, sign in (('L', 1), ('R', -1)):
        pts = [REST[IDS[f'arm_{side}_{j}']] for j in ('upper', 'lower', 'end')]
        cuff = add(pts[2], (.3, sign*.15, -1.1))
        s.strand(f'sleeve_{side}', [(*pts[0], 2.6), (*pts[1], 2.5), (*add(pts[2], (0, 0, 2.0)), 3.1), (*cuff, 3.7)], 'cloth', 20, 5)
        claw_hand(s, side, add(pts[2], (.2, 0, .4)))
    s.parts.append(cope())
    # Brocade stole down the robe front, flaring toward the hem.
    path, widths = [], []
    for j in range(25):
        z = 45.5-44.3*j/24
        cx, rx, ry = robe_at(z)
        path.append(((cx+rx*train(0, z)+.32, 0, z), (1, 0, 0)))
        widths.append(4.6+2.6*smooth(40, 2, z))
    s.parts.append(ribbon('stole', path, widths, .36))
    # Gold torc at the throat and a gold hem band.
    s.strand('torc', [(.4+2.7*math.cos(math.tau*k/28), 3.0*math.sin(math.tau*k/28), 51.6, .5) for k in range(29)], 'bone', 6, 1)
    # --- Head: mummified skin drawn over the skull -----------------------------
    s.strand('neck', [(.2, 0, 50.5, 1.45), (.8, 0, 53.0, 1.3), (1.4, 0, 55.0, 1.4)], 'body', 12, 3)
    s.oval('head_cranium', (.5, 0, 58.2), (3.3, 2.8, 3.3), 'body', 18, 12)
    s.oval('head_face', (2.3, 0, 56.4), (1.9, 2.15, 2.3), 'body', 20, 12)
    s.strand('head_brow', [(2.8, -2.4, 58.5, .5), (3.75, -1.2, 58.35, .62), (3.95, 0, 58.0, .5),
                           (3.75, 1.2, 58.35, .62), (2.8, 2.4, 58.5, .5)], 'body', 10, 4)
    for sign in (-1, 1):
        s.strand(f'head_cheek_{sign}', [(1.6, sign*2.5, 56.6, .55), (3.0, sign*2.05, 56.2, .55), (3.7, sign*1.3, 55.9, .32)], 'body', 8, 3)
        s.oval(f'head_ear_{sign}', (-.1, sign*2.85, 56.9), (.7, .35, 1.25), 'body', 10, 6)
        s.oval(f'socket_{sign}', (3.55, sign*1.12, 57.3), (.55, .72, .56), 'dark', 12, 6)
        s.oval(f'glow_eye_{sign}', (3.98, sign*1.08, 57.25), (.16, .24, .2), 'glow', 8, 6)
    s.oval('cavity_nose', (4.05, 0, 56.1), (.3, .34, .62), 'dark', 10, 6)
    s.oval('jaw', (2.3, 0, 54.0), (1.65, 1.85, 1.2), 'body', 18, 10)
    s.oval('cavity_mouth', (3.55, 0, 54.95), (.5, 1.25, .42), 'dark', 12, 6)
    for i in range(8):
        y = (i-3.5)*.32
        x = 4.02-.07*abs(i-3.5)**1.5
        s.strand(f'tooth_up{i}', [(x, y, 55.35, .15), (x+.02, y, 54.8, .1)], 'bone', 4, 2)
        s.strand(f'tooth_lo{i}', [(x-.1, y, 54.35, .13), (x-.08, y, 54.85, .08)], 'bone', 4, 2)
    # Thin forked beard of dry strands, ending above the phylactery.
    for i in range(9):
        y = (i-4)*.34
        fork = 1 if y > 0 else -1
        end = 45.4+.5*abs(i-4)/4
        s.strand(f'beard_{i}', [(3.5-.05*abs(i-4), y, 53.2, .3), (4.3, y*1.15, 50.5, .28), (4.9, y*1.2+fork*.35, 47.8, .2),
                                (5.2, y*1.1+fork*.8, end, .05)], 'accent', 5, 3)
    # Spiked crown grown onto the skull: a band and nine points, tallest in front.
    cx, rx, ry = .5, 3.18, 2.72
    s.strand('crown_band', [(cx+rx*math.cos(math.tau*k/32), ry*math.sin(math.tau*k/32), CROWN_Z-.35*math.cos(math.tau*k/32), .52)
                            for k in range(33)], 'bone', 8, 1)
    for k in range(9):
        deg = (k-4)*30
        a = math.radians(deg)
        h = 6.4-1.05*abs(k-4)**1.15
        base = (cx+rx*math.cos(a), ry*math.sin(a), CROWN_Z+.2-.35*math.cos(a))
        out = (math.cos(a), math.sin(a), 0)
        s.strand(f'crown_spike_{k}', [(*base, .62), (*add(base, add(mul(out, .45), (0, 0, h*.5))), .4),
                                      (*add(base, add(mul(out, 1.0), (0, 0, h))), .04)], 'bone', 6, 3)
    # Phylactery: a green gem in a gold reliquary cage on a chain at the sternum.
    gx, gy, gz = GEM
    s.oval('gem', GEM, (1.2, 1.55, 2.3), 'glow', 8, 6)
    for k in range(4):
        a = math.tau*k/4+math.pi/4
        s.strand(f'cage_{k}', [(gx+1.32*math.cos(a)*.85, 1.65*math.sin(a)*.9, gz+2.3, .16),
                               (gx+1.32*math.cos(a), 1.72*math.sin(a), gz, .18),
                               (gx+1.32*math.cos(a)*.85, 1.65*math.sin(a)*.9, gz-2.3, .16)], 'bone', 6, 3)
    s.oval('cage_cap', (gx-.1, 0, gz+2.6), (.9, 1.1, .55), 'bone', 12, 6)
    s.strand('cage_finial', [(gx, 0, gz-2.2, .6), (gx, 0, gz-3.2, .3), (gx, 0, gz-3.9, .03)], 'bone', 8, 2)
    for sign in (-1, 1):
        s.strand(f'chain_{sign}', [(gx-.2, 0, gz+2.9, .16), (4.6, sign*1.9, 45.5, .16), (3.2, sign*2.8, 49.2, .16),
                                   (1.0, sign*3.1, 51.2, .16)], 'bone', 5, 4, ribbed=True)
    for p in s.parts:
        p.vertices = [tuple(round(c, 6) for c in v) for v in p.vertices]
    return s.parts


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


def robe_weights(v, upper=('pelvis', 'spine', 'chest', 'neck'), arm_from=8.0, arm_to=12.5):
    x, y, z = v
    if z >= 30:
        rows = chain((-.6, 0, min(z, 52)), list(upper))
        side = 'L' if y > 0 else 'R'
        t = smooth(arm_from, arm_to, abs(y))*smooth(40, 48, z)*.85
        return _normalize([(b, w*(1-t)) for b, w in rows]+[(IDS[f'arm_{side}_upper'], t)])
    # Skirt: the front drapes over the thighs and knees; the back and train
    # hang from the pelvis to the heels, so kneeling never swings them through the floor.
    a = smooth(30, 4, z)**.8
    share_l = max(0, min(1, .5+y/7))
    cx, rx, ry = robe_at(z)
    ang = math.atan2(y/ry, (x-cx)/rx)
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
    if n.startswith(('jaw', 'tooth_lo')):
        return [(IDS['jaw'], 1)]
    if n.startswith('beard'):
        t = smooth(52.5, 46, v[2])
        return _normalize([(IDS['jaw'], 1-t), (IDS['chest'], t)])
    if n.startswith(('head', 'socket', 'glow', 'cavity', 'tooth', 'crown')):
        return [(IDS['head'], 1)]
    if n == 'neck':
        return _normalize(chain(v, ['chest', 'neck', 'head']))
    if n.startswith(('gem', 'cage', 'chain', 'torc')):
        return [(IDS['chest'], 1)]
    if n in ('robe', 'stole'):
        return robe_weights(v)
    if n == 'cope':
        return robe_weights(v, ('spine', 'chest', 'neck'), 7.5, 13.0)
    if n.startswith('sleeve_'):
        return _normalize(chain(v, ['chest', f'arm_{side}_upper', f'arm_{side}_lower', f'arm_{side}_end']))
    if n.startswith(('hand_', 'nail_', 'ring_')):
        return [(IDS[f'arm_{side}_end'], 1)]
    raise KeyError(n)


def solve_leg(side, target, rot, hip_shift):
    """Two-link leg IK in the (unrotated, shifted) pelvis frame."""
    ids = [IDS[f'leg_{side}_{j}'] for j in ('upper', 'lower', 'end')]
    hip, knee, foot = [REST[i] for i in ids]
    target = sub(target, hip_shift)
    a, b, dist = math.dist(hip, knee), math.dist(knee, foot), math.dist(target, hip)
    if not abs(a-b) < dist < a+b:
        raise ValueError(('unreachable lich foot', side, target, dist, a+b))
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


def guard(turn, k=1.0, phase=0.0):
    """Left claw cupped under the phylactery, guarding it against the chest."""
    turn('arm_L_upper', (0, 1, 0), (20+1.5*math.sin(phase))*k)
    turn('arm_L_upper', (1, 0, 0), -10*k)
    turn('arm_L_lower', (0, 1, 0), (-90+2*math.sin(phase+.6))*k)
    turn('arm_L_lower', (0, 0, 1), -10*k)
    turn('arm_L_lower', (1, 0, 0), -40*k)
    turn('arm_L_end', (0, 1, 0), 10*k)


def pose(name, t):
    rot = [(0, 0, 0, 1) for _ in BONES]
    pelvis = [0.0, 0.0, 0.0]
    feet = {s: list(REST[IDS[f'leg_{s}_end']]) for s in ('L', 'R')}

    def turn(b, d, deg):
        rot[IDS[b]] = qmul(rot[IDS[b]], axis(d, math.radians(deg)))
    phase = math.tau*t
    if name == 'idle':
        breathe = math.sin(phase)
        pelvis[2] = -.2+.2*math.cos(phase)
        turn('spine', (0, 1, 0), 3+1.0*breathe)
        turn('chest', (0, 1, 0), -2+1.0*breathe)
        turn('head', (0, 0, 1), 7*math.sin(phase))
        turn('head', (0, 1, 0), 4+2*math.sin(2*phase))
        turn('jaw', (0, 1, 0), 3+3*max(0, math.sin(2*phase)))
        guard(turn, 1, phase)
        turn('arm_R_upper', (0, 1, 0), -10+2*math.sin(phase+1))
        turn('arm_R_upper', (1, 0, 0), -4)
        turn('arm_R_lower', (0, 1, 0), -18+3*math.sin(phase+1.4))
        turn('arm_R_end', (0, 1, 0), -12+4*math.sin(phase+2))
    elif name == 'stride':
        # A slow, stately stride; the robe hides the legs, the gem hand stays raised.
        for side, offset in (('L', 0), ('R', .5)):
            q = (t+offset) % 1
            if q < .6:
                dx, lift = 3.5-7*q/.6, 0
            else:
                u = (q-.6)/.4
                dx, lift = -3.5+7*u, 2.4*math.sin(math.pi*u)
            feet[side][0] += dx
            feet[side][2] += lift
        pelvis[1] = .6*math.sin(phase)
        pelvis[2] = -.8+.5*math.cos(2*phase)
        turn('spine', (0, 1, 0), 6)
        turn('spine', (0, 0, 1), 4*math.sin(phase))
        turn('head', (0, 0, 1), -3*math.sin(phase))
        guard(turn, 1, phase)
        turn('arm_R_upper', (0, 1, 0), -8-12*math.cos(phase))
        turn('arm_R_lower', (0, 1, 0), -16-6*math.cos(phase))
    elif name == 'touch':
        # Middle frame: a deep lunge, the right claw thrust out low to touch,
        # the left hand clutching the gem back to the chest.
        k = keys(t, [(0, 0), (.22, .25), (.5, 1), (.78, .55), (1, 0)])
        wind = keys(t, [(0, 0), (.22, 1), (.5, 0), (1, 0)])
        pelvis[0] = 2.2*k-1.0*wind
        pelvis[2] = -4.2*k
        feet['L'][0] += 7.5*k
        feet['R'][0] -= 2.5*k
        turn('spine', (0, 1, 0), TOUCH[0]*k-8*wind)
        turn('spine', (0, 0, 1), -16*k+10*wind)
        turn('chest', (0, 1, 0), TOUCH[1]*k)
        turn('neck', (0, 1, 0), -14*k)
        turn('head', (0, 1, 0), -16*k)
        turn('jaw', (0, 1, 0), 3+20*k)
        guard(turn, 1)
        turn('arm_R_upper', (0, 1, 0), 34*wind+TOUCH[2]*k)
        turn('arm_R_upper', (1, 0, 0), -26*wind-TOUCH[3]*k)
        turn('arm_R_lower', (0, 1, 0), -30*wind-6*k)
        turn('arm_R_end', (0, 1, 0), 30*wind-TOUCH[4]*k)
    elif name == 'incant':
        # Middle frame: arms flung wide and low, head thrown back, jaw agape:
        # "rasps a terrifying incantation".
        h = keys(t, [(0, 0), (.5, 1), (.8, .85), (1, 0)])
        pelvis[2] = -2.0*h
        pelvis[0] = -1.0*h
        pelvis[1] = -3.6*h
        turn('spine', (0, 1, 0), -8*h)
        # Yaw the torso so both flung arms open across the oblique and front views.
        turn('spine', (0, 0, 1), INCANT_YAW*h)
        turn('chest', (0, 1, 0), -8*h)
        turn('neck', (0, 1, 0), -10*h)
        turn('neck', (0, 0, 1), -.5*INCANT_YAW*h)
        turn('head', (0, 1, 0), -22*h)
        turn('jaw', (0, 1, 0), 3+26*h)
        guard(turn, 1-h)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), INCANT[0]*h)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*INCANT[1]*h)
            turn(f'arm_{side}_lower', (0, 1, 0), INCANT[2]*h)
            turn(f'arm_{side}_end', (1, 0, 0), sign*INCANT[3]*h)
    elif name == 'recoil':
        r = math.sin(math.pi*t)**2
        pelvis[0] = -1.8*r
        pelvis[2] = -1.4*r
        turn('spine', (0, 1, 0), -12*r)
        turn('chest', (0, 1, 0), -6*r)
        turn('head', (0, 1, 0), -18*r)
        turn('head', (0, 0, 1), 12*r)
        turn('jaw', (0, 1, 0), 3+14*r)
        guard(turn, 1-.4*r)
        turn('arm_R_upper', (0, 1, 0), -40*r)
        turn('arm_R_upper', (1, 0, 0), -24*r)
        turn('arm_R_lower', (0, 1, 0), -50*r)
    elif name == 'crumble':
        # The legs give way (middle frame: sagging mid-collapse), it lands
        # kneeling and pitches face-down, the crowned head on the floor.
        sag = keys(t, [(0, 0), (.5, .55), (.85, 1), (1, 1)])
        fold = keys(t, [(0, 0), (.3, 0), (1, 1)])
        pelvis[0] = -FALL_BACK*sag
        pelvis[2] = -FALL_DROP*sag
        for s in ('L', 'R'):
            feet[s][0] += FEET_FWD*sag
        guard(turn, 1-fold)
        turn('spine', (0, 1, 0), FALL_SPINE*fold)
        turn('chest', (0, 1, 0), FALL_CHEST*fold)
        turn('neck', (0, 1, 0), 8*fold)
        turn('head', (0, 1, 0), FALL_HEAD*fold)
        turn('head', (0, 0, 1), 24*fold)
        turn('jaw', (0, 1, 0), 3+16*fold)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), FALL_ARM*fold)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*FALL_SPREAD*fold)
            turn(f'arm_{side}_lower', (0, 1, 0), FALL_ELBOW*fold)
            turn(f'arm_{side}_end', (0, 1, 0), 55*min(1, 1.5*fold))
    for s in ('L', 'R'):
        solve_leg(s, tuple(feet[s]), rot, tuple(pelvis))
    frame = []
    for i, (n, p, local) in enumerate(BONES):
        loc = add(local, tuple(pelvis)) if n == 'pelvis' else local
        frame.append((*loc, *rot[i], 1, 1, 1))
    return frame


TOUCH = (24, 10, -78, 6, 26)
INCANT = (-22, 28, -30, 30)
INCANT_YAW = 20
FALL_BACK, FALL_DROP, FEET_FWD = 7, 21, 16
FALL_SPINE, FALL_CHEST, FALL_HEAD = 82, 26, 18
FALL_ARM, FALL_SPREAD, FALL_ELBOW = -30, 34, -30


def _connected():
    from .connected_skin import attach
    return attach(SLUG, build_parts(), weights)


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
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_lich', material_path=SKIN)
    path = ROOT/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M40', format='IQM v2', runtimeModel=MODEL, sha256=hashlib.sha256(data).hexdigest(),
                    skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(), shader=SHADER,
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/lich/lich-animated.blend')
    out = ROOT/'assets/monsters/lich'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    print(importlib.import_module('tools.monster_models.lich_animation').build()['sha256'])
