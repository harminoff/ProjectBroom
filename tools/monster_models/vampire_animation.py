"""Original vampire: a gaunt, stooped aristocrat whose cloak is a folded bat wing.

Cosmetic only. Brogue CE owns the vampire's bites and draining, blinking,
discord, bat summoning, fleeing, the blood burst on death and every outcome;
nothing here signals or changes them. The source says he "lives a solitary
life deep underground, consuming any warm-blooded creature", that he "buries
his fangs in" his prey, and that he "spreads his cloak and bursts into a cloud
of bats". The art answers with a bloodless, bald predator with long swept bat
ears and two long fangs, a tailored oxblood frock coat with a blood-flecked
white lace jabot and silver buttons, and a low-collared leathery cloak whose
hem is cut into bat-wing scallops between raised ribs. The cloak's edges
follow the hands, so the spread pose opens it like wings. No tall opera
collar and no medallion. Nothing emits light. Grounded and opaque.
"""
import hashlib
import json
import math
from . import iqm, vampire_materials as mats
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips
from .revenant_animation import rings, smooth, keys

SLUG = 'vampire'
SKIN = 'graphics/BRGVAMP.png'
MODEL = 'mod/BrogueDoom/models/monsters/53_vampire.iqm'
SKIN_FACE_BUDGET = 5200

SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 31)),
         ('spine', 'pelvis', (-.6, 0, 39)), ('chest', 'spine', (-.6, 0, 47)),
         ('neck', 'chest', (1.2, 0, 52.2)), ('head', 'neck', (2.6, 0, 55.6)),
         ('jaw', 'head', (3.6, 0, 54.8))]
for side, sign in (('L', 1), ('R', -1)):
    for limb, parent, points in (
            ('arm', 'chest', [(0, 7.0, 50.2), (1.0, 9.0, 38.6), (2.6, 10.0, 27.4)]),
            ('leg', 'pelvis', [(0, 4.1, 30.5), (1.6, 4.7, 16.8), (0, 5.0, 3.4)])):
        for joint, (x, y, z) in zip(('upper', 'lower', 'end'), points):
            name = f'{limb}_{side}_{joint}'
            SPECS.append((name, parent, (x, sign*y, z)))
            parent = name

RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CLIPS = [('idle', 40, 20, True), ('prowl', 32, 35, True), ('bite', 24, 35, False),
         ('spread', 26, 35, False), ('recoil', 14, 35, False), ('collapse', 36, 35, False)]
ANKLE = REST[IDS['leg_L_end']][2]

COAT_ROWS = [(24.5, -.2, 4.4, 5.4), (29, -.2, 4.2, 5.2), (34, -.4, 3.7, 4.6), (39, -.6, 3.9, 5.2),
             (44, -.6, 4.3, 6.2), (48, -.4, 4.0, 6.6), (50.5, -.1, 3.0, 4.6), (52.2, .5, 1.7, 2.0)]
SKIRT_ROWS = [(12.5, -.4, 6.6, 7.2), (18, -.3, 5.6, 6.3), (24, -.2, 4.7, 5.6), (29, -.2, 4.4, 5.3)]
CLOAK_ROWS = [(9.5, -4.2, 8.6, 12.6), (18, -3.6, 8.0, 12.0), (28, -3.0, 7.2, 11.4), (38, -2.4, 6.6, 11.0),
              (45, -1.9, 6.2, 11.0), (49.5, -1.4, 5.4, 9.8), (52.3, -.9, 3.8, 6.6)]
CLOAK_A = (98, 262)
CLOAK_SCALLOPS = 6


def CONNECTED_SKIN(name):
    return name in ('coat', 'pelvis') or name.startswith(('sleeve_', 'leg_', 'boot_'))


def _interp(rows, z, k):
    if z <= rows[0][0]:
        return rows[0][k]
    for a, b in zip(rows, rows[1:]):
        if a[0] <= z <= b[0]:
            return a[k]+(b[k]-a[k])*(z-a[0])/(b[0]-a[0])
    return rows[-1][k]


def cloak_hem(u):
    """Deep bat-wing scallops between hanging rib points (shared with the paint)."""
    return mats.cloak_hem(u)


def shell(name, rows, a0, a1, thick, segs, hem=None):
    """Closed, thick curved panel between angles a0..a1 (degrees CCW from +X)."""
    p = Part(name)
    n = len(rows)
    grids = []
    for inset in (0.0, thick):
        grid = []
        for j, (z, cx, rx, ry) in enumerate(rows):
            row = []
            for i in range(segs+1):
                u = i/segs
                a = math.radians(a0+(a1-a0)*u)
                zz = z+(hem(u) if hem and j == 0 else 0)
                row.append(p.vertex((cx+(rx-inset)*math.cos(a), (ry-inset)*math.sin(a), zz), 'fur', u, j/(n-1)))
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


def cloak_point(u, z, pad=0.0):
    a = math.radians(CLOAK_A[0]+(CLOAK_A[1]-CLOAK_A[0])*u)
    cx, rx, ry = (_interp(CLOAK_ROWS, z, k) for k in (1, 2, 3))
    return (cx+(rx+pad)*math.cos(a), (ry+pad)*math.sin(a), z)


def flatten(part, a, b, normal, k):
    """Squash a tube toward the plane through its axis a->b with this normal."""
    d = sub(b, a)
    out = []
    for v in part.vertices:
        t = max(0, min(1, sum(x*y for x, y in zip(sub(v, a), d))/sum(x*x for x in d)))
        c = add(a, mul(d, t))
        off = sub(v, c)
        h = sum(x*y for x, y in zip(off, normal))
        out.append(sub(v, mul(normal, h*(1-k))))
    part.vertices = out


def claw_hand(s, side, wrist):
    """Long pale hand: palm, four long jointed fingers with black hooked nails."""
    sign = 1 if side == 'L' else -1
    wx, wy, wz = wrist
    s.oval(f'hand_{side}_palm', (wx+.4, wy, wz-2.0), (1.3, .75, 1.9), 'body', 14, 10)
    for i in range(4):
        dx = (i-1.5)*.68
        base = (wx+.4+dx, wy+sign*.05, wz-3.6)
        # Hooked, half-curled claws: the tips turn in toward the palm.
        mid = (base[0]+.9+.1*dx, base[1]-sign*.35, base[2]-2.4)
        tip = (base[0]+1.3+.2*dx, base[1]-sign*1.3, base[2]-4.2-.3*(1.5-abs(i-1.5)))
        s.strand(f'hand_{side}_finger{i}', [(*base, .34), (*mid, .28), (*tip, .2)], 'body', 7, 3)
        s.strand(f'nail_{side}_{i}', [(*tip, .19), (tip[0]+.7, tip[1], tip[2]-1.2, .13), (tip[0]+.2, tip[1], tip[2]-2.4, .02)], 'dark', 6, 2)
    thumb = (wx+1.0, wy-sign*.7, wz-2.2)
    s.strand(f'hand_{side}_thumb', [(*thumb, .38), (thumb[0]+1.3, thumb[1]-sign*.4, thumb[2]-1.6, .28),
                                    (thumb[0]+1.8, thumb[1]-sign*.4, thumb[2]-3.0, .19)], 'body', 7, 3)
    s.strand(f'nail_{side}_thumb', [(thumb[0]+1.8, thumb[1]-sign*.4, thumb[2]-3.0, .18), (thumb[0]+2.1, thumb[1]-sign*.4, thumb[2]-4.0, .1),
                                    (thumb[0]+1.6, thumb[1]-sign*.4, thumb[2]-4.9, .02)], 'dark', 6, 2)


def build_parts():
    s = Sculpt()
    # --- Connected body: fitted coat, sleeves, breeches and boots -------------
    s.parts.append(rings('coat', COAT_ROWS, 36))
    s.oval('pelvis', (0, 0, 29.5), (3.9, 4.9, 3.6), 'body', 20, 10)
    for side, sign in (('L', 1), ('R', -1)):
        arm = [REST[IDS[f'arm_{side}_{j}']] for j in ('upper', 'lower', 'end')]
        s.strand(f'sleeve_{side}', [(-.2, sign*5.0, 50.4, 2.1), (*arm[0], 2.0), (*arm[1], 1.55), (*add(arm[2], (0, 0, 1.2)), 1.35), (*arm[2], 1.45)], 'cloth', 16, 5)
        leg = [REST[IDS[f'leg_{side}_{j}']] for j in ('upper', 'lower', 'end')]
        s.strand(f'leg_{side}', [(*leg[0], 2.8), (*add(leg[0], mul(sub(leg[1], leg[0]), .5)), 2.4), (*leg[1], 2.05),
                                 (*add(leg[1], (0, 0, -1.5)), 2.3), (*add(leg[2], (0, 0, -.6)), 1.8)], 'cloth', 16, 4)
        s.oval(f'boot_{side}', (2.2, sign*5.0, 1.8), (4.2, 1.75, 1.55), 'body', 20, 10)
        claw_hand(s, side, add(arm[2], (.1, 0, 0)))
    # Coat tails split at the front, hanging to the calves.
    for k, (a0, a1) in enumerate(((34, 178), (-178, -34))):
        s.parts.append(shell(f'skirt_{k}', SKIRT_ROWS, a0, a1, .3, 22))
    # Low turned-down collar, lace jabot and silver buttons.
    s.parts.append(shell('collar', [(49.2, .1, 3.4, 5.2), (51.2, .3, 2.9, 3.8), (52.6, .6, 2.3, 2.7)], 40, 320, .3, 26))
    # Frilled lace jabot cascading from the throat.
    s.parts.append(rings('jabot', [(45.2, 4.75, .35, 1.2), (46.4, 4.95, .62, 2.05), (48.0, 4.85, .62, 1.9),
                                   (49.6, 4.6, .55, 1.45), (51.0, 4.2, .42, .95)], 28,
                         lambda a, z: 1+.22*math.sin(a*12+z*2.1)))
    for i in range(5):
        z = 43-3.3*i
        s.oval(f'button_{i}', (_interp(COAT_ROWS, z, 1)+_interp(COAT_ROWS, z, 2)+.15, 1.0, z), (.3, .42, .42), 'bone', 8, 6)
    # --- Cloak: leathery, low-collared, bat-wing hem and ribs ------------------
    s.parts.append(shell('cloak', CLOAK_ROWS, CLOAK_A[0], CLOAK_A[1], .4, 48, cloak_hem))
    for k in range(1, CLOAK_SCALLOPS):
        u = k/CLOAK_SCALLOPS
        pts = []
        for j in range(9):
            t = j/8
            z = 51-(51-9.6)*t
            uu = .5+(u-.5)*smooth(0, .35, t)**.6
            pts.append((*cloak_point(uu, z, .2), .2-.12*t))
        s.strand(f'rib_{k}', pts, 'bone', 5, 2)
    s.strand('clasp_chain', [(4.0, 4.6, 49.0, .16), (5.0, 2.3, 48.0, .16), (5.3, 0, 47.7, .16), (5.0, -2.3, 48.0, .16),
                             (4.0, -4.6, 49.0, .16)], 'bone', 5, 4, ribbed=True)
    for sign in (-1, 1):
        s.oval(f'clasp_{sign}', (3.6, sign*5.2, 49.4), (.35, .9, .9), 'bone', 12, 6)
    # --- Head: bald, gaunt, bat-eared, with long upper fangs --------------------
    s.strand('neck', [(.8, 0, 50.0, 1.35), (1.8, 0, 53.2, 1.2), (2.8, 0, 55.4, 1.3)], 'body', 12, 3)
    s.oval('head_cranium', (1.5, 0, 59.0), (4.2, 2.45, 3.35), 'body', 20, 12)
    s.oval('head_face', (3.9, 0, 56.4), (1.8, 1.75, 2.3), 'body', 18, 10)
    s.strand('head_brow', [(4.2, -2.1, 58.2, .38), (5.2, -1.0, 58.0, .48), (5.45, 0, 57.4, .42),
                           (5.2, 1.0, 58.0, .48), (4.2, 2.1, 58.2, .38)], 'body', 10, 4)
    s.strand('head_nose', [(5.5, 0, 57.5, .26), (6.25, 0, 56.4, .27), (6.5, 0, 55.6, .1)], 'body', 8, 3)
    for sign in (-1, 1):
        s.strand(f'head_cheek_{sign}', [(3.0, sign*2.3, 56.6, .42), (4.6, sign*1.85, 56.3, .38), (5.3, sign*1.15, 56.0, .18)], 'body', 8, 3)
        # Long, swept, pointed bat ears: broad, flattened and cupped forward.
        ear = s.strand(f'head_ear_{sign}', [(1.9, sign*2.3, 57.4, 1.25), (.7, sign*3.9, 58.6, 1.2), (-.7, sign*5.4, 59.2, .75),
                                            (-2.2, sign*6.6, 59.8, .05)], 'body', 12, 4)
        flatten(ear, (1.9, sign*2.3, 57.4), (-2.2, sign*6.6, 59.8), unit((.55, sign*.75, -.35)), .38)
        s.oval(f'socket_{sign}', (5.05, sign*1.0, 57.05), (.45, .62, .42), 'dark', 12, 6)
        s.oval(f'iris_{sign}', (5.42, sign*.95, 57.02), (.12, .2, .16), 'glow', 8, 4)
    s.oval('jaw', (4.1, 0, 54.2), (1.5, 1.45, 1.0), 'body', 16, 8)
    s.oval('mouth', (5.35, 0, 54.95), (.45, 1.05, .32), 'dark', 12, 6)
    for sign in (-1, 1):
        s.strand(f'fang_{sign}', [(5.55, sign*.55, 55.25, .22), (5.6, sign*.52, 54.3, .14), (5.5, sign*.5, 53.4, .02)], 'bone', 6, 2)
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


def drape(v, rows, upper=('pelvis', 'spine', 'chest', 'neck')):
    """Coat-style weights: torso chain above the hips; skirts over the legs."""
    x, y, z = v
    if z >= 30:
        return _normalize(chain((-.6, 0, min(z, 52)), list(upper)))
    a = smooth(30, 6, z)**.8
    share_l = max(0, min(1, .5+y/6))
    cx, rx, ry = (_interp(rows, z, k) for k in (1, 2, 3))
    ang = math.atan2(y/ry, (x-cx)/rx)
    front = max(0, min(1, .5+.9*math.cos(ang)))
    a = a+(1-a)*front*.6*min(1, (30-z)/4)
    out = [(IDS['pelvis'], 1-a)]
    for s, share in (('L', share_l), ('R', 1-share_l)):
        if share <= 0:
            continue
        ids = [IDS[f'leg_{s}_{j}'] for j in ('upper', 'lower', 'end')]
        zz = max(REST[ids[2]][2], min(REST[ids[0]][2], z))
        ref = (REST[ids[0]][0]+(REST[ids[1]][0]-REST[ids[0]][0])*max(0, min(1, (30.5-zz)/13.7)), REST[ids[0]][1], zz)
        for b, w in RIG.chain_weights(ref, ids):
            out.append((b, a*share*front*w))
        out.append((ids[2], a*share*(1-front)))
    return _normalize(out)


def cloak_weights(v):
    """Back of the cloak hangs from the shoulders; its edges ride the arms, so
    raising the arms opens the cloak like a wing."""
    x, y, z = v
    cx = _interp(CLOAK_ROWS, z, 1)
    rx, ry = _interp(CLOAK_ROWS, z, 2), _interp(CLOAK_ROWS, z, 3)
    ang = math.degrees(math.atan2(y/ry, (x-cx)/rx)) % 360
    f = min(1.0, abs(ang-180)/82)
    side = 'L' if y > 0 else 'R'
    arm = smooth(.25, .95, f)*smooth(53, 47, z)*(.35+.65*smooth(12, 26, z))
    base = drape(v, CLOAK_ROWS, ('spine', 'chest', 'neck'))
    hand = REST[IDS[f'arm_{side}_end']]
    top = REST[IDS[f'arm_{side}_upper']]
    t = max(0, min(1, (top[2]-z)/(top[2]-hand[2])))
    ref = add(top, mul(sub(hand, top), t))
    along = chain(ref, [f'arm_{side}_upper', f'arm_{side}_lower', f'arm_{side}_end'])
    if z < hand[2]:
        along = [(IDS[f'arm_{side}_end'], 1)]
    return _normalize([(b, w*(1-arm)) for b, w in base]+[(b, w*arm) for b, w in along])


def weights(part, v, uv):
    n = part.name
    side = 'L' if v[1] > 0 else 'R'
    if n.startswith(('jaw', 'mouth')):
        return [(IDS['jaw'], 1)]
    if n.startswith(('head', 'socket', 'iris', 'fang')):
        return [(IDS['head'], 1)]
    if n == 'neck':
        return _normalize(chain(v, ['chest', 'neck', 'head']))
    if n.startswith(('jabot', 'collar', 'clasp')):
        return _normalize(chain(v, ['spine', 'chest', 'neck']))
    if n.startswith(('coat', 'button', 'skirt')):
        return drape(v, SKIRT_ROWS if v[2] < 29 else COAT_ROWS)
    if n.startswith(('cloak', 'rib_')):
        return cloak_weights(v)
    if n == 'pelvis':
        return [(IDS['pelvis'], 1)]
    if n.startswith('sleeve_'):
        return _normalize(chain(v, ['chest', f'arm_{side}_upper', f'arm_{side}_lower', f'arm_{side}_end']))
    if n.startswith('leg_'):
        return _normalize(chain(v, ['pelvis', f'leg_{side}_upper', f'leg_{side}_lower', f'leg_{side}_end']))
    if n.startswith('boot_'):
        return [(IDS[f'leg_{side}_end'], 1)]
    if n.startswith(('hand_', 'nail_')):
        return [(IDS[f'arm_{side}_end'], 1)]
    raise KeyError(n)


def solve_leg(side, target, rot, hip_shift):
    """Two-link leg IK in the (unrotated, shifted) pelvis frame."""
    ids = [IDS[f'leg_{side}_{j}'] for j in ('upper', 'lower', 'end')]
    hip, knee, foot = [REST[i] for i in ids]
    target = sub(target, hip_shift)
    a, b, dist = math.dist(hip, knee), math.dist(knee, foot), math.dist(target, hip)
    if not abs(a-b) < dist < a+b:
        raise ValueError(('unreachable vampire foot', side, target, dist, a+b))
    direction = unit(sub(target, hip))
    along = (a*a-b*b+dist*dist)/(2*dist)
    # Fixed forward, slightly outward knee pole: the rest leg is nearly
    # straight, so a pole taken from it flips and knocks the knees inward.
    pole = (1.0, (1 if side == 'L' else -1)*.18, 0.0)
    bend = unit(sub(pole, mul(direction, sum(x*y for x, y in zip(pole, direction)))))
    nk = add(hip, add(mul(direction, along), mul(bend, math.sqrt(max(0, a*a-along*along)))))
    upper = between(sub(knee, hip), sub(nk, hip))
    lower = between(sub(foot, knee), sub(target, nk))
    rot[ids[0]] = upper
    rot[ids[1]] = qmul(inverse(upper), lower)
    rot[ids[2]] = inverse(lower)


def stoop(turn, k=1.0, phase=0.0):
    """Predatory carriage: shoulders hunched, head thrust forward, claws half-raised."""
    turn('spine', (0, 1, 0), (STOOP[0]+.8*math.sin(phase))*k)
    turn('chest', (0, 1, 0), STOOP[1]*k)
    turn('neck', (0, 1, 0), STOOP[2]*k)
    turn('head', (0, 1, 0), -STOOP[3]*k)
    for side, sign in (('L', 1), ('R', -1)):
        turn(f'arm_{side}_upper', (0, 1, 0), (STOOP[4]+2*math.sin(phase+sign))*k)
        turn(f'arm_{side}_upper', (1, 0, 0), sign*STOOP[5]*k)
        turn(f'arm_{side}_lower', (0, 1, 0), (STOOP[6]+3*math.sin(phase+sign*1.3))*k)
        turn(f'arm_{side}_lower', (0, 0, 1), -sign*STOOP[7]*k)
        turn(f'arm_{side}_end', (0, 1, 0), (STOOP[8]+4*math.sin(phase+sign*.7))*k)


def pose(name, t):
    rot = [(0, 0, 0, 1) for _ in BONES]
    pelvis = [0.0, 0.0, 0.0]
    feet = {s: list(REST[IDS[f'leg_{s}_end']]) for s in ('L', 'R')}

    def turn(b, d, deg):
        rot[IDS[b]] = qmul(rot[IDS[b]], axis(d, math.radians(deg)))
    phase = math.tau*t
    if name == 'idle':
        pelvis[2] = -.9+.25*math.cos(phase)
        feet['L'][0] += 2.0
        feet['R'][0] -= 1.5
        stoop(turn, 1, phase)
        turn('head', (0, 0, 1), 14*math.sin(phase))
        turn('head', (1, 0, 0), 5*math.sin(2*phase))
        turn('jaw', (0, 1, 0), 2+2*max(0, math.sin(2*phase)))
    elif name == 'prowl':
        for side, offset in (('L', 0), ('R', .5)):
            q = (t+offset) % 1
            if q < .6:
                dx, lift = 4.5-9*q/.6, 0
            else:
                u = (q-.6)/.4
                dx, lift = -4.5+9*u, 3.0*math.sin(math.pi*u)
            feet[side][0] += dx
            feet[side][1] += (1 if side == 'L' else -1)*(.6+.5*lift/3)
            feet[side][2] += lift
        pelvis[1] = .5*math.sin(phase)
        pelvis[2] = -1.5+.5*math.cos(2*phase)
        stoop(turn, 1, phase)
        turn('spine', (0, 1, 0), 6)
        turn('spine', (0, 0, 1), 5*math.sin(phase))
        turn('head', (0, 0, 1), -5*math.sin(phase))
        for side, off in (('L', 0), ('R', math.pi)):
            turn(f'arm_{side}_upper', (0, 1, 0), -9*math.cos(phase+off))
    elif name == 'bite':
        # Middle frame: a low lunge, claws seizing forward, head darting in with
        # the jaw wide to "bury his fangs".
        k = keys(t, [(0, 0), (.24, .3), (.5, 1), (.78, .5), (1, 0)])
        wind = keys(t, [(0, 0), (.24, 1), (.5, 0), (1, 0)])
        stoop(turn, 1)
        pelvis[0] = BITE[0]*k-1.5*wind
        pelvis[2] = -BITE[1]*k-1.0*wind
        feet['L'][0] += 8*k
        feet['R'][0] -= 3*k
        turn('spine', (0, 1, 0), BITE[2]*k-10*wind)
        turn('chest', (0, 1, 0), 8*k)
        turn('neck', (0, 1, 0), 10*k-8*wind)
        turn('head', (0, 1, 0), -BITE[3]*k+10*wind)
        turn('jaw', (0, 1, 0), 2+30*k+6*wind)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), 30*wind-BITE[4]*k)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*(22*wind+BITE[5]*k))
            turn(f'arm_{side}_lower', (0, 1, 0), -20*wind+30*k)
            turn(f'arm_{side}_end', (0, 1, 0), -30*k)
    elif name == 'spread':
        # Middle frame: "spreads his cloak": arms thrown wide and low, the cloak
        # opened like a pair of wings, head thrust forward hissing.
        h = keys(t, [(0, 0), (.5, 1), (.8, .8), (1, 0)])
        stoop(turn, 1-h)
        pelvis[2] = -2.2*h
        pelvis[0] = -.8*h
        feet['L'][0] += 2.5*h
        feet['R'][0] -= 2.5*h
        turn('spine', (0, 1, 0), 14*h)
        turn('chest', (0, 1, 0), -4*h)
        turn('neck', (0, 1, 0), 10*h)
        turn('head', (0, 1, 0), -20*h)
        turn('jaw', (0, 1, 0), 2+26*h)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), SPREAD[0]*h)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*SPREAD[1]*h)
            turn(f'arm_{side}_lower', (0, 1, 0), SPREAD[2]*h)
            turn(f'arm_{side}_end', (0, 1, 0), SPREAD[3]*h)
    elif name == 'recoil':
        r = math.sin(math.pi*t)**2
        stoop(turn, 1-r)
        pelvis[0] = -2.0*r
        pelvis[2] = -1.6*r
        turn('spine', (0, 1, 0), -12*r)
        turn('head', (0, 1, 0), -14*r)
        turn('head', (0, 0, 1), -16*r)
        turn('jaw', (0, 1, 0), 2+22*r)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), 24*r)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*22*r)
            turn(f'arm_{side}_lower', (0, 1, 0), -30*r)
    elif name == 'collapse':
        # The knees give way (middle frame: sagging, clutching), then he pitches
        # face-down with the cloak spread over him.
        sag = keys(t, [(0, 0), (.5, .55), (.85, 1), (1, 1)])
        fold = keys(t, [(0, 0), (.3, 0), (1, 1)])
        stoop(turn, 1-fold)
        pelvis[0] = -FALL_BACK*sag
        pelvis[2] = -FALL_DROP*sag
        for s in ('L', 'R'):
            feet[s][0] += FEET_FWD*sag
        turn('spine', (0, 1, 0), FALL_SPINE*fold)
        turn('chest', (0, 1, 0), FALL_CHEST*fold)
        turn('neck', (0, 1, 0), 6*fold)
        turn('head', (0, 1, 0), FALL_HEAD*fold)
        turn('head', (0, 0, 1), -28*fold)
        turn('jaw', (0, 1, 0), 2+18*fold)
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


STOOP = (14, 10, 14, 26, 8, -4, -100, 70, 36)
BITE = (1.5, 5.5, 24, 10, 46, 8)
SPREAD = (-22, 54, -36, -10)
FALL_BACK, FALL_DROP, FEET_FWD = 7, 17.4, 15
FALL_SPINE, FALL_CHEST, FALL_HEAD = 88, 26, 14
FALL_ARM, FALL_SPREAD, FALL_ELBOW = -30, 16, -30


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
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_vampire', material_path=SKIN)
    path = ROOT/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M53', format='IQM v2', runtimeModel=MODEL, sha256=hashlib.sha256(data).hexdigest(),
                    skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/vampire/vampire-animated.blend')
    out = ROOT/'assets/monsters/vampire'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    print(importlib.import_module('tools.monster_models.vampire_animation').build()['sha256'])
