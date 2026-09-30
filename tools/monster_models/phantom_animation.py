"""Original phantom: a hovering, legless apparition of mournful rage. Cosmetic only.

Brogue CE owns invisibility, flight, flitting, web immunity, ectoplasm droplets
and every outcome. This model only defines how the phantom looks while the
frontend displays it: an additive, fullbright outline figure whose gaunt
torso pours into a ragged ectoplasm tail, with streaming hair, long claws and
hanging droplets. No visibility rule, collision, AI, RNG or timing.
"""
import hashlib
import json
import math
from . import iqm, phantom_materials as mats
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit, cross, spline
from .skeletal import Rig, axis, qmul, assemble, sample_clips

SKIN = 'graphics/BRGPHANT.png'
MODEL = 'mod/BrogueDoom/models/monsters/43_phantom.iqm'
SKIN_VOXEL_SIZE = .2
SKIN_FACE_BUDGET = 7200

SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (-.8, 0, 29)),
         ('spine', 'pelvis', (-.3, 0, 36)), ('chest', 'spine', (.2, 0, 44)),
         ('neck', 'chest', (.9, 0, 50.5)), ('head', 'neck', (1.8, 0, 54.5)),
         ('jaw', 'head', (2.0, 0, 55.6)),
         ('hair_0', 'head', (-.9, 0, 58.6)), ('hair_1', 'hair_0', (-6, 0, 55.5)),
         ('hair_2', 'hair_1', (-11, 0, 50.5))]
TAIL = [(-1.5, 0, 24), (-3.2, 0, 18), (-6, 0, 12.5), (-9.5, 0, 8.5), (-13.5, 0, 6)]
parent = 'pelvis'
for i, p in enumerate(TAIL):
    SPECS.append((f'tail_{i}', parent, p))
    parent = f'tail_{i}'
ARM = [(.3, 7, 47.5), (2.2, 10.8, 39), (5.5, 12, 31.5)]
for side, sign in (('L', 1), ('R', -1)):
    parent = 'chest'
    for joint, (x, y, z) in zip(('upper', 'lower', 'end'), ARM):
        SPECS.append((f'arm_{side}_{joint}', parent, (x, sign*y, z)))
        parent = f'arm_{side}_{joint}'

RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
HOVER = 1.5
DROP, PELVIS, SPINE, CHEST, HEAD = 18, 40, 30, 12, 22
HAIR = (-75, -20, -10)
TAIL_FLAT = (34, -5, -6, -5, -2)
ARM_OUT, ARM_FWD, ELBOW = 90, -20, -10
CLIPS = [('idle', 40, 20, True), ('drift', 32, 35, True), ('lunge', 24, 35, False),
         ('wail', 26, 35, False), ('recoil', 14, 35, False), ('dissipate', 36, 35, False)]


def CONNECTED_SKIN(name):
    return name.startswith(('body', 'head', 'neck', 'shoulder_', 'arm_', 'hand_'))


def sweep(name, controls, sides=28, samples=4, fold=None):
    """Closed tube of elliptical sections (x, y, z, forward radius, side radius)."""
    p = Part(name)
    rows = spline(controls, samples)
    prev = None
    for i, row in enumerate(rows):
        c = row[:3]
        tangent = unit(sub(rows[min(i+1, len(rows)-1)][:3], rows[max(0, i-1)][:3]))
        ref = prev if prev is not None else (1, 0, 0)
        n = unit(sub(ref, mul(tangent, sum(a*b for a, b in zip(ref, tangent)))))
        prev = n
        b = unit(cross(tangent, n))
        for j in range(sides):
            a = math.tau*j/sides
            k = fold(a, c) if fold else 1
            rx, ry = max(.02, row[3])*k, max(.02, row[4])*k
            p.vertex(add(c, add(mul(n, rx*math.cos(a)), mul(b, ry*math.sin(a)))), 'fur', j/sides, i/(len(rows)-1))
    for i in range(len(rows)-1):
        for j in range(sides):
            a, b2 = i*sides+j, i*sides+(j+1) % sides
            p.faces.append((a, b2, b2+sides, a+sides))
    first = p.vertex(rows[0][:3], 'fur', .5, 0)
    last = p.vertex(rows[-1][:3], 'fur', .5, 1)
    top = (len(rows)-1)*sides
    for j in range(sides):
        p.faces.append((first, (j+1) % sides, j))
        p.faces.append((last, top+j, top+(j+1) % sides))
    return p


def body_fold(a, c):
    # Vertical ectoplasm drapery below the waist; smooth gaunt chest above.
    z = c[2]
    t = max(0, min(1, (31-z)/6))*max(0, min(1, (z-5)/6))
    return 1+.16*t*math.sin(a*7+z*.18)+.06*t*math.sin(a*13)


def build_parts():
    s = Sculpt()
    s.parts.append(sweep('body', [
        (1.0, 0, 51.4, 1.3, 1.5), (.4, 0, 48.6, 2.6, 5.6), (.3, 0, 45, 3.5, 5.5),
        (-.1, 0, 40.5, 3.1, 4.7), (-.5, 0, 35.5, 2.2, 3.3), (-.9, 0, 30.5, 2.8, 4.6),
        (-1.6, 0, 25, 3.9, 6.2), (-3.2, 0, 18.5, 3.4, 5.0), (-6, 0, 12.8, 2.5, 3.4),
        (-9.5, 0, 8.8, 1.7, 2.2), (-13.5, 0, 6.3, 1.0, 1.2), (-16.8, 0, 5.4, .3, .3)], 32, 4, body_fold))
    s.strand('neck', [(.7, 0, 49.5, 1.45), (1.4, 0, 52.5, 1.3), (2.0, 0, 55, 1.4)], 'body', 16, 3)
    # Elongated gaunt skull, hollow cheeks, and a long dropped jaw.
    s.oval('head_cranium', (1.7, 0, 58.2), (2.8, 2.45, 3.3), 'body', 28, 18)
    s.oval('head_face', (3.2, 0, 56.4), (1.5, 2.0, 2.3), 'body', 24, 14)
    s.oval('head_jaw', (3.1, 0, 53.7), (1.35, 1.35, 1.9), 'body', 22, 14)
    for sign in (-1, 1):
        # Brows pulled down at the centre (rage); cheekbones gaunt.
        s.strand(f'head_brow_{sign}', [(4.35, sign*.35, 57.9, .42), (4.3, sign*1.3, 58.5, .5), (3.6, sign*2.4, 59.1, .34)], 'body', 12, 3)
        s.strand(f'head_cheek_{sign}', [(3.2, sign*2.1, 56.2, .5), (4.1, sign*1.6, 55.6, .42), (4.2, sign*1.0, 54.9, .25)], 'body', 12, 3)
        s.oval(f'shoulder_{sign}', (.2, sign*6.2, 47.6), (2.1, 2.3, 1.9), 'body', 20, 12)
    s.strand('head_nose', [(4.3, 0, 57.4, .32), (4.75, 0, 56.1, .38), (4.55, 0, 55.6, .2)], 'body', 12, 3)
    for side, sign in (('L', 1), ('R', -1)):
        pts = [REST[IDS[f'arm_{side}_{j}']] for j in ('upper', 'lower', 'end')]
        s.strand(f'arm_{side}', [(*pts[0], 1.25), (*pts[1], .95), (*pts[2], .72)], 'body', 16, 5)
        s.oval(f'arm_{side}_elbow', pts[1], (1.0, 1.0, 1.1), 'body', 16, 10)
        s.oval(f'hand_{side}_palm', (6.3, sign*12.2, 30.8), (1.8, 1.2, .9), 'body', 18, 10)
        for i in range(4):
            y = sign*(11.2+i*.72)
            tip = (11.2-abs(i-1.4)*.7, y+sign*.25, 27.3)
            s.strand(f'hand_{side}_finger{i}', [(7.2, y, 30.1, .34), (9.2, y+sign*.15, 29.5, .3), (*tip, .22)], 'body', 10, 4)
            s.strand(f'claw_{side}_{i}', [(tip[0]-.15, tip[1], tip[2]+.05, .23), (tip[0]+1.4, tip[1]+sign*.1, tip[2]-1.2, .14),
                                           (tip[0]+2.0, tip[1]+sign*.15, tip[2]-2.6, .02)], 'bone', 8, 4)
        s.strand(f'hand_{side}_thumb', [(6.2, sign*11.1, 30.6, .4), (7.6, sign*10.2, 30.0, .3), (8.8, sign*10.1, 29.0, .21)], 'body', 10, 3)
        s.strand(f'claw_{side}_thumb', [(8.7, sign*10.1, 29.05, .21), (9.8, sign*10.0, 28.1, .12), (10.2, sign*10.1, 26.9, .02)], 'bone', 8, 4)
        # Forearm tatters hang like torn sleeves of ectoplasm.
        for i, (t, length) in enumerate(((.25, 7.5), (.55, 9.5), (.85, 6.5))):
            a = add(pts[1], mul(sub(pts[2], pts[1]), t))
            root = add(a, (-.6, sign*.4, -.5))
            s.strand(f'tatter_arm_{side}_{i}', [(*root, .5), (root[0]-1.8, root[1]+sign*.6, root[2]-length*.5, .38),
                                                 (root[0]-3.2, root[1]+sign*.2, root[2]-length, .04)], 'cloth', 8, 4)
        s.oval(f'drop_{side}', (13.3, sign*12.0, 23.0), (.5, .5, .72), 'glow', 12, 8)
        s.strand(f'drop_{side}_neck', [(13.3, sign*12.0, 23.6, .36), (13.25, sign*12.0, 24.5, .03)], 'glow', 8, 3)
    # Streaming hair: five tendrils swept back from the crown.
    for i in range(5):
        y = (i-2)*1.0
        droop = 1.2*abs(i-2)
        s.strand(f'hair_{i}', [(-.2, y*.8, 60.4-.3*abs(i-2), .6), (-4.8, y*1.5, 58.2-droop*.5, .5),
                               (-9.8, y*2.2, 53.2-droop, .34), (-14.2, y*2.8, 48-droop*1.3, .05)], 'accent', 8, 5)
    # Ragged ectoplasm tatters trailing from the sides and back of the flare.
    for i in range(6):
        a = math.radians(95+i*34)
        cx, cy = -1.8+4.0*math.cos(a), 6.4*math.sin(a)
        length = 11+3*((i*5) % 3)
        s.strand(f'tatter_skirt_{i}', [(cx, cy, 25.5, .6), (cx-3+.6*math.cos(a), cy*1.15, 25.5-length*.5, .5),
                                       (cx-6.5, cy*1.1, 25.5-length, .04)], 'cloth', 8, 4)
    # Hanging ectoplasm droplets beneath the tail.
    for i, (x, z, r) in enumerate(((-6.5, 8.2, .75), (-11, 3.9, .6), (-15.6, 3.2, .45))):
        s.oval(f'drop_tail_{i}', (x, 0, z), (r, r, r*1.35), 'glow', 12, 8)
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
        s = (t-.7)/.3*.5
        if j+1 == len(ids)-1:
            s = (t-.7)/.3
        return [(ids[j], 1-s), (ids[j+1], s)]
    if t < .3 and j > 0:
        s = (.3-t)/.3*.5
        return [(ids[j-1], s), (ids[j], 1-s)]
    return [(ids[j], 1)]


def body_weights(v):
    up = ['pelvis', 'spine', 'chest', 'neck', 'head']
    down = ['pelvis']+[f'tail_{i}' for i in range(len(TAIL))]
    return chain(v, down) if v[2] < REST[IDS['pelvis']][2]-.5 else chain(v, up)


def weights(part, v, uv):
    n = part.name
    if n.startswith(('hair_',)):
        return _normalize(chain(v, ['head', 'hair_0', 'hair_1', 'hair_2']))
    if n.startswith('head') or n == 'neck' and v[2] > 53.5:
        if n == 'head_jaw' or (n.startswith(('head_face', 'head_cheek')) and v[2] < 55.0 and v[0] > 2.2):
            return [(IDS['jaw'], 1)]
        return [(IDS['head'], 1)]
    if n == 'neck':
        return _normalize(chain(v, ['chest', 'neck', 'head']))
    if n.startswith('shoulder_'):
        side = 'L' if v[1] > 0 else 'R'
        t = max(0, min(1, (abs(v[1])-4.5)/3))
        return _normalize([(IDS['chest'], 1-t), (IDS[f'arm_{side}_upper'], t)])
    if n.startswith(('arm_', 'hand_', 'claw_', 'tatter_arm_', 'drop_L', 'drop_R')):
        side = 'L' if v[1] > 0 else 'R'
        if n.startswith(('hand_', 'claw_', 'drop_')):
            return [(IDS[f'arm_{side}_end'], 1)]
        if n.startswith('tatter_arm_'):
            root = part.vertices[0]
            return _normalize(chain(root, [f'arm_{side}_upper', f'arm_{side}_lower', f'arm_{side}_end']))
        return _normalize(chain(v, ['chest', f'arm_{side}_upper', f'arm_{side}_lower', f'arm_{side}_end']))
    if n.startswith('tatter_skirt'):
        return _normalize(chain(v, ['pelvis']+[f'tail_{i}' for i in range(3)]))
    if n.startswith('drop_tail'):
        i = int(n[-1])
        return [(IDS[f'tail_{(2, 3, 4)[i]}'], 1)]
    return _normalize(body_weights(v))


def pose(name, t):
    rot = [(0, 0, 0, 1) for _ in BONES]
    shift = [(0, 0, 0) for _ in BONES]

    def turn(b, d, deg):
        rot[IDS[b]] = qmul(rot[IDS[b]], axis(d, math.radians(deg)))

    def move(b, d):
        shift[IDS[b]] = add(shift[IDS[b]], d)
    phase = math.tau*t
    ramp = math.sin(math.pi*t)**2
    move('pelvis', (0, 0, HOVER))
    if name == 'idle':
        move('pelvis', (0, 0, 1.1*math.sin(phase)))
        turn('pelvis', (0, 1, 0), 2*math.sin(phase+.6))
        for i in range(len(TAIL)):
            turn(f'tail_{i}', (0, 0, 1), 6*math.sin(phase-.9*i))
            turn(f'tail_{i}', (0, 1, 0), 3*math.sin(phase-.9*i+1))
        for i in range(3):
            turn(f'hair_{i}', (0, 1, 0), 4*math.sin(phase-.8*i))
            turn(f'hair_{i}', (0, 0, 1), 5*math.sin(phase-.8*i+.5))
        turn('head', (0, 0, 1), 6*math.sin(phase))
        turn('jaw', (0, 1, 0), 4+3*math.sin(phase*2))
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), -8+5*math.sin(phase+sign))
            turn(f'arm_{side}_lower', (0, 1, 0), -10+4*math.sin(phase+sign+.7))
    elif name == 'drift':
        weave = math.sin(phase)
        move('pelvis', (0, 1.6*weave, .8*math.sin(2*phase)))
        turn('pelvis', (0, 1, 0), 18)
        turn('pelvis', (1, 0, 0), -6*weave)
        turn('chest', (0, 1, 0), 4)
        turn('head', (0, 1, 0), -16)
        for i in range(len(TAIL)):
            turn(f'tail_{i}', (0, 1, 0), 9+3*math.sin(phase-.9*i))
            turn(f'tail_{i}', (0, 0, 1), 9*math.sin(phase-1.1*i))
        for i in range(3):
            turn(f'hair_{i}', (0, 1, 0), 10+6*math.sin(phase*2-.8*i))
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), 18+8*math.sin(phase+sign))
            turn(f'arm_{side}_upper', (1, 0, 0), sign*12)
            turn(f'arm_{side}_lower', (0, 1, 0), 8)
        turn('jaw', (0, 1, 0), 6)
    elif name == 'lunge':
        wind = math.sin(math.pi*min(1, t/.3))**2*(t < .3)
        hit = math.sin(math.pi*min(1, max(0, (t-.15)/.7)))**1.5
        move('pelvis', (-2*wind-3.5*hit, 0, 1.2*wind))
        turn('pelvis', (0, 1, 0), -10*wind+22*hit)
        turn('chest', (0, 1, 0), 8*hit)
        turn('neck', (0, 1, 0), -18*hit)
        turn('head', (0, 1, 0), -16*hit)
        turn('jaw', (0, 1, 0), 5+30*hit)
        for i in range(len(TAIL)):
            turn(f'tail_{i}', (0, 1, 0), 4*hit+4*wind)
        for i in range(3):
            turn(f'hair_{i}', (0, 1, 0), 14*hit)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (1, 0, 0), sign*(18*wind-6*hit))
            turn(f'arm_{side}_upper', (0, 1, 0), 25*wind-92*hit)
            turn(f'arm_{side}_lower', (0, 1, 0), -30*wind+18*hit)
            turn(f'arm_{side}_end', (0, 1, 0), 8*hit)
    elif name == 'wail':
        rise = math.sin(math.pi*min(1, t/.95))**1.4
        move('pelvis', (-1.5*rise, 0, 4*rise))
        turn('pelvis', (0, 1, 0), -12*rise)
        turn('chest', (0, 1, 0), -10*rise)
        turn('neck', (0, 1, 0), -14*rise)
        turn('head', (0, 1, 0), -18*rise)
        turn('jaw', (0, 1, 0), 5+38*rise)
        for i in range(len(TAIL)):
            turn(f'tail_{i}', (0, 1, 0), -10*rise)
            turn(f'tail_{i}', (0, 0, 1), 8*rise*math.sin(1.5*i))
        for i in range(3):
            turn(f'hair_{i}', (0, 1, 0), -22*rise)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (1, 0, 0), sign*122*rise)
            turn(f'arm_{side}_upper', (0, 1, 0), -10*rise)
            turn(f'arm_{side}_lower', (1, 0, 0), sign*-18*rise)
            turn(f'arm_{side}_end', (1, 0, 0), sign*-20*rise)
    elif name == 'recoil':
        move('pelvis', (-3.5*ramp, 0, 1.5*ramp))
        turn('pelvis', (0, 1, 0), -22*ramp)
        turn('chest', (0, 1, 0), -10*ramp)
        turn('head', (0, 1, 0), -24*ramp)
        turn('head', (0, 0, 1), 12*ramp)
        turn('jaw', (0, 1, 0), 5+20*ramp)
        for i in range(len(TAIL)):
            turn(f'tail_{i}', (0, 1, 0), -4*ramp)
        for i in range(3):
            turn(f'hair_{i}', (0, 1, 0), -18*ramp)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (0, 1, 0), -55*ramp)
            turn(f'arm_{side}_upper', (1, 0, 0), sign*25*ramp)
            turn(f'arm_{side}_lower', (0, 1, 0), -25*ramp)
    elif name == 'dissipate':
        # A last rising wail, then the ectoplasm slumps into a low floor heap:
        # the tail pools flat, the torso folds over it and the arms spill out.
        early = math.sin(math.pi*min(1, t/.4))**2*(t < .4)
        s = max(0, min(1, (t-.2)/.72))
        s = s*s*(3-2*s)
        move('pelvis', (-1*s, 0, 2.5*early-DROP*s))
        turn('pelvis', (0, 1, 0), -10*early+PELVIS*s)
        turn('spine', (0, 1, 0), SPINE*s)
        turn('chest', (0, 1, 0), -8*early+CHEST*s)
        turn('neck', (0, 1, 0), 10*s)
        turn('head', (0, 1, 0), -20*early+HEAD*s)
        turn('head', (0, 0, 1), 16*s)
        turn('jaw', (0, 1, 0), 5+30*early+10*s)
        for i in range(len(TAIL)):
            turn(f'tail_{i}', (0, 1, 0), TAIL_FLAT[i]*s-6*early)
            turn(f'tail_{i}', (0, 0, 1), 22*s)
        for i in range(3):
            turn(f'hair_{i}', (0, 1, 0), -20*early+HAIR[i]*s)
        for side, sign in (('L', 1), ('R', -1)):
            turn(f'arm_{side}_upper', (1, 0, 0), sign*max(82*early, ARM_OUT*s))
            turn(f'arm_{side}_upper', (0, 1, 0), ARM_FWD*s)
            turn(f'arm_{side}_lower', (1, 0, 0), sign*(-15*early+ELBOW*s))
            turn(f'arm_{side}_end', (1, 0, 0), sign*25*s)
    return [(*add(local, shift[i]), *rot[i], 1, 1, 1) for i, (n, p, local) in enumerate(BONES)]


def _connected():
    from .connected_skin import attach
    return attach('phantom', build_parts(), weights)


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
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_phantom', material_path=SKIN)
    path = ROOT/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M43', format='IQM v2', runtimeModel=MODEL, sha256=hashlib.sha256(data).hexdigest(),
                    skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/phantom/phantom-animated.blend')
    out = ROOT/'assets/monsters/phantom'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    print(importlib.import_module('tools.monster_models.phantom_animation').build()['sha256'])
