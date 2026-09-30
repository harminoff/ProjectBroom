"""Original connected imp, six purely cosmetic skeletal roles. No gameplay.

Brogue: "This trickster demon moves with astonishing speed and delights in
stealing from $HISHER enemies and blinking away." A cunning, wiry thief-demon
in a predatory crouch: sharp swept-back horns, swept ears, narrow slanted
heavy-lidded slit-pupil eyes under a hard V brow, a sly sharp-toothed smirk,
shoulder and elbow spurs, a spiked spine ridge, long arms hanging low with
spread ivory claws, digitigrade goat legs and a whip tail curling up behind in
an S to a spade tip. Posed and weighted at design scale; export bakes a uniform
SCALE into the rest pose, geometry and clip translations (unit bone scales, no
MODELDEF visualScale), presenting it about 46.4 units tall. +X forward, Z up,
+Y left.

Speed, theft, fleeing, blinking, targets, damage and every outcome belong to
Brogue. The snatch clip is a cosmetic two-handed grab; it does not assert that
an item was stolen, and no clip fakes a blink or moves the imp off its cell.
"""
import hashlib
import json
import math

from . import iqm, imp_materials as materials
from .rat import ROOT, Part, add, sub, mul, unit, cross
from .skeletal import Rig, axis, qmul, inverse, rotate, between, assemble, sample_clips
from .pixie_animation import (dot, clamp, smooth, window, lerp, r6, ortho, blob, tube, frame_quat, slerp)

SKIN = materials.SKIN
MODEL = 'mod/BrogueDoom/models/monsters/45_imp.iqm'
TAU = math.tau
SIDES = (('L', 1), ('R', -1))
SKIN_VOXEL_SIZE = .11
SKIN_FACE_BUDGET = 7900
SCALE = 1.15   # baked into the exported rest pose, geometry and clips
DIAG_COLOURS = {'skin_leg': (60, 30, 45), 'skin_foot': (40, 20, 30), 'skin': (190, 50, 80), 'horn': (230, 215, 175),
                'spur': (230, 215, 175), 'spike': (200, 180, 150), 'lid': (120, 24, 50),
                'eye': (255, 200, 40), 'claw': (240, 235, 210), 'toe_claw': (240, 235, 210), 'finger': (190, 80, 110),
                'thumb': (190, 80, 110), 'tooth': (255, 255, 255)}


def CONNECTED_SKIN(name):
    return name.startswith('skin_')


# ---------------------------------------------------------------- skeleton
PELVIS, SPINE, CHEST, NECK, HEAD = (0.2, 0, 18.9), (0.6, 0, 22.2), (1.0, 0, 25.6), (1.2, 0, 28.4), (2.3, 0, 30.8)
SHOULDER = {s: (0.3, s*4.1, 28.1) for _, s in SIDES}
ELBOW = {s: (-0.6, s*6.4, 22.7) for _, s in SIDES}
WRIST = {s: (1.3, s*7.0, 17.4) for _, s in SIDES}
HIP = {s: (0.2, s*2.2, 18.2) for _, s in SIDES}
KNEE = {s: (2.8, s*2.8, 12.6) for _, s in SIDES}
HOCK = {s: (-1.5, s*2.9, 6.0) for _, s in SIDES}
BALL = {s: (0.9, s*3.0, 1.15) for _, s in SIDES}
TOE = {s: (3.1, s*3.0, .6) for _, s in SIDES}
EAR = {s: (1.6, s*3.0, 33.6) for _, s in SIDES}
EAR_TIP = {s: (-2.6, s*8.2, 35.3) for _, s in SIDES}
TAIL = [(-2.0, 0, 18.9), (-5.6, 0, 17.0), (-9.2, 0, 16.8), (-11.9, 0, 18.8), (-12.9, 0, 22.2)]
TAIL_END = (-12.3, 0, 25.6)


def hand_frame(s):
    """Forearm axis e, palm normal n (toward the body) and knuckle axis w (forward)."""
    e = unit(sub(WRIST[s], ELBOW[s]))
    n = ortho((0, -s, 0), e)
    w = unit(cross(n, e))
    if w[0] < 0: w = mul(w, -1)
    return e, n, w


def knuckle(s):
    return r6(add(WRIST[s], mul(hand_frame(s)[0], 1.7)))


SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', PELVIS), ('spine', 'pelvis', SPINE), ('chest', 'spine', CHEST),
         ('neck', 'chest', NECK), ('head', 'neck', HEAD)]
for side, s in SIDES:
    SPECS.append(('ear_'+side, 'head', EAR[s]))
for side, s in SIDES:
    SPECS += [('arm_'+side, 'chest', SHOULDER[s]), ('forearm_'+side, 'arm_'+side, ELBOW[s]),
              ('hand_'+side, 'forearm_'+side, WRIST[s]), ('claws_'+side, 'hand_'+side, knuckle(s)),
              ('thigh_'+side, 'pelvis', HIP[s]), ('shin_'+side, 'thigh_'+side, KNEE[s]),
              ('foot_'+side, 'shin_'+side, HOCK[s]), ('toes_'+side, 'foot_'+side, BALL[s])]
for k, p in enumerate(TAIL):
    SPECS.append((f'tail_{k}', 'pelvis' if k == 0 else f'tail_{k-1}', p))
D_RIG = Rig.from_world(SPECS)   # design-unit authoring rig (posing and weights)
BONES, D_REST = D_RIG.bones, D_RIG.rest
IDS = {n: i for i, (n, _, _) in enumerate(BONES)}
CLIPS = [('idle', 48, 24, True), ('walk', 24, 30, True), ('slice', 24, 30, False),
         ('snatch', 24, 30, False), ('recoil', 12, 30, False), ('death', 32, 30, False)]


# ---------------------------------------------------------------- anatomy
HEAD_C, HEAD_R = (2.4, 0, 33.4), (3.4, 3.3, 3.5)
FACE_C, FACE_R = (4.1, 0, 31.9), (2.3, 2.7, 2.0)
CHIN_C, CHIN_R = (4.5, 0, 29.95), (1.3, 1.45, 1.0)
EYE_Y, EYE_Z = 1.6, 33.2
MOUTH = (6.1, 30.9, 2.0)   # front x, centre z, half width
SMIRK = (.1, .5)   # slope and raised-corner lift (the imp's left corner curls up)


def head_surface_x(y, z):
    best = -9.
    for c, r in ((HEAD_C, HEAD_R), (FACE_C, FACE_R), (CHIN_C, CHIN_R)):
        q = 1-((y-c[1])/r[1])**2-((z-c[2])/r[2])**2
        if q > 0: best = max(best, c[0]+r[0]*math.sqrt(q))
    return best


def zblob(name, center, radii, seg=28, rings=18, taper=None):
    """Blob with poles along Z; radii given as (x, y, z)."""
    return blob(name, center, (0, 0, 1), (1, 0, 0), (radii[2], radii[0], radii[1]), seg, rings, taper)


def leaf(name, base, tip, facing, width, thick, seg=20, rings=18):
    a0 = unit(sub(tip, base))
    f = ortho(facing, a0)
    w = cross(f, a0)
    half = math.dist(base, tip)/2+.3
    return blob(name, lerp(base, tip, .5), a0, w, (half, width, thick), seg, rings,
                taper=lambda xi: .2+.8*clamp((1-xi)/1.3)**.7)


def build_head(parts):
    parts.append(zblob('skin_cranium', HEAD_C, HEAD_R, 36, 24))
    parts.append(zblob('skin_face', FACE_C, FACE_R, 32, 20))
    parts.append(zblob('skin_chin', CHIN_C, CHIN_R, 24, 14))
    nx = head_surface_x(0, 32.45)
    parts.append(blob('skin_nose', (nx-.1, 0, 32.45), (.75, 0, .66), (0, 1, 0), (.72, .55, .45), 18, 12))
    for side, s in SIDES:
        # Hard V brow ridges pinched low toward the nose.
        inner, outer = (.35, 33.75), (2.75, 35.0)
        pts = []
        for f in (0, .35, .7, 1.):
            y, z = lerp(inner, outer, f)
            pts.append((round(head_surface_x(y, z)-.12, 6), round(s*y, 6), round(z, 6), round(.7-.26*f, 6)))
        parts.append(tube('skin_brow_'+side, pts, 14, 3))
        parts.append(leaf('skin_ear_'+side, EAR[s], EAR_TIP[s], (1, s*.2, .35), 1.7, .34))
        # Sharp horns swept hard back, seated in the cranium.
        horn = [(2.0, 1.5, 35.2, 1.05), (1.5, 2.1, 37.1, .86), (.1, 2.8, 38.8, .63), (-2.0, 3.3, 39.9, .43),
                (-4.3, 3.6, 40.3, .25), (-6.5, 3.7, 40.0, .1), (-8.1, 3.6, 39.4, .01)]
        parts.append(tube('horn_'+side, [(x, s*y, z, r) for x, y, z, r in horn], 14, 3))
        # Narrow slanted eyes (outer corners up) under heavy upper lids.
        f = unit((math.cos(math.radians(18)), s*math.sin(math.radians(18)), .04))
        lat = ortho(unit((0, s, .42)), f)
        up = unit(cross(lat, f))
        if up[2] < 0: up = mul(up, -1)
        c = sub((head_surface_x(s*EYE_Y, EYE_Z), s*EYE_Y, EYE_Z), mul(f, .3))
        parts.append(blob('eye_'+side, r6(c), f, up, (.55, .6, .88), 28, 18))
        parts.append(blob('lid_'+side, r6(add(c, add(mul(up, .34), mul(f, .1)))), f, up, (.6, .4, 1.0), 24, 14))
        parts.append(blob('lid_low_'+side, r6(add(c, add(mul(up, -.52), mul(f, .06)))), f, up, (.52, .2, .86), 20, 10))
    # Sharp teeth bared only at the raised (left) corner of the smirk, one fang at the other.
    for k, (y, length) in enumerate(((.75, .55), (1.15, .75), (1.55, .55), (-.9, .45))):
        z = smirk_z(y)+.02
        bx = head_surface_x(y, z)
        name = f'tooth_{k}_'+('L' if y > 0 else 'R')
        parts.append(tube(name, [(round(bx-.3, 6), y, round(z+.1, 6), .17), (round(bx-.02, 6), y, round(z-.1, 6), .13),
                                 (round(bx+.02, 6), y, round(z-length, 6), .01)], 8, 2))


def smirk_z(y):
    """Mouth line height: gently sloped, curled up at the imp's left corner."""
    mx, z0, half = MOUTH
    t = y/half
    return z0+SMIRK[0]*t+SMIRK[1]*max(0., t)**2


def torso_back_x(z):
    best = 9.
    for c, r in (((1.0, 0, 25.3), (2.4, 3.5, 3.1)), ((1.2, 0, 21.8), (1.9, 2.3, 2.5)), ((0.3, 0, 18.9), (2.2, 2.8, 2.1))):
        q = 1-((z-c[2])/r[2])**2
        if q > 0: best = min(best, c[0]-r[0]*math.sqrt(q))
    if z > 27.2:
        best = min(best, (0.9-1.55)+((1.5-1.35)-(0.9-1.55))*clamp((z-26.8)/1.9))
    return best


SPINE_SPIKES = (28.6, 27.3, 26.0, 24.7, 23.4, 22.0, 20.6)


def build_spurs(parts):
    for side, s in SIDES:
        parts.append(tube('spur_shoulder_'+side, [(0.3, s*4.2, 28.6, .5), (-0.2, s*4.9, 29.9, .32), (-0.9, s*5.5, 31.2, .01)], 10, 3))
        parts.append(tube('spur_elbow_'+side, [(-0.4, s*6.45, 22.9, .45), (-1.8, s*6.7, 23.2, .28), (-3.3, s*7.0, 23.7, .01)], 10, 3))
    for k, z in enumerate(SPINE_SPIKES):
        x = torso_back_x(z)
        L = 1.5-.08*k
        d = unit((-1, 0, .6))
        parts.append(tube(f'spike_{k}', [(round(x+.45, 6), 0, z, .42), (round(x-.1, 6), 0, round(z+.2, 6), .3),
                                        (*r6(add((x, 0, z), mul(d, L))), .01)], 8, 3))


def build_body(parts):
    parts.append(tube('skin_neck', [(0.9, 0, 26.8, 1.55), (1.5, 0, 28.7, 1.35), (2.2, 0, 30.6, 1.45), (2.7, 0, 31.8, 1.5)], 20, 3))
    parts.append(zblob('skin_chest', (1.0, 0, 25.3), (2.4, 3.5, 3.1), 32, 20))
    parts.append(zblob('skin_belly', (1.2, 0, 21.8), (1.9, 2.3, 2.5), 32, 20))
    parts.append(zblob('skin_pelvis', (0.3, 0, 18.9), (2.2, 2.8, 2.1), 32, 20))
    for side, s in SIDES:
        parts.append(zblob('skin_trap_'+side, (0.1, s*2.0, 27.6), (1.1, 1.3, 1.3), 20, 14))
        parts.append(zblob('skin_shoulder_'+side, (0.3, s*3.8, 27.9), (1.2, 1.2, 1.25), 20, 14))
        sh, el, wr = SHOULDER[s], ELBOW[s], WRIST[s]
        parts.append(tube('skin_arm_'+side, [(0.2, s*3.3, 28.5, 1.0), (*sh, .95), (*lerp(sh, el, .5), .8), (*el, .64),
                                             (*lerp(el, wr, .4), .74), (*lerp(el, wr, .8), .54), (*wr, .45)], 18, 3))
        e, n, w = hand_frame(s)
        parts.append(blob('skin_palm_'+side, r6(add(wr, mul(e, .95))), e, w, (1.05, .82, .36), 18, 12))
        hp, kn, hk, bl, to = HIP[s], KNEE[s], HOCK[s], BALL[s], TOE[s]
        parts.append(tube('skin_leg_'+side, [(0.1, s*1.7, 19.6, 1.75), (*hp, 1.75), (1.8, s*2.6, 15.0, 1.45), (*kn, 1.0),
                                             (1.3, s*2.85, 10.0, .8), (0., s*2.9, 7.6, .66), (*hk, .6)], 20, 3))
        parts.append(tube('skin_foot_'+side, [(*hk, .6), (-0.3, s*2.95, 3.6, .52), (*bl, .66), (2.2, s*3.0, .78, .55),
                                              (*to, .34)], 16, 3))
    tail = [(-0.6, 0, 19.6, 1.3), (-2.0, 0, 18.9, 1.0), (-3.8, 0, 17.7, .8), (-5.6, 0, 17.0, .66), (-7.4, 0, 16.7, .58),
            (-9.2, 0, 16.8, .5), (-10.8, 0, 17.5, .45), (-11.9, 0, 18.8, .42), (-12.7, 0, 20.4, .38), (-12.9, 0, 22.2, .35),
            (-12.8, 0, 23.9, .32), (-12.4, 0, 25.3, .3)]
    parts.append(tube('skin_tail', tail, 14, 3))
    a0 = unit((.25, 0, 1))
    parts.append(blob('skin_spade', (-12.05, 0, 27.0), a0, ortho((1, 0, 0), a0), (2.0, 1.55, .34), 22, 16,
                      taper=lambda xi: max(.1, math.sin(math.pi*clamp((xi+1)/2)**.62))))


def build_hands(parts):
    for side, s in SIDES:
        e, n, w = hand_frame(s)
        kn = knuckle(s)
        for k, (off, length) in enumerate(((.55, 2.0), (0., 2.3), (-.55, 1.9))):
            b = add(kn, mul(w, off))
            ef = unit(add(e, mul(w, off*.55)))   # fingers fan apart
            mid = add(b, add(mul(ef, length*.55), mul(n, .2)))
            end = add(b, add(mul(ef, length), mul(n, .55)))
            parts.append(tube(f'finger_{k}_'+side, [r6(sub(b, mul(e, .5)))+(.3,), r6(b)+(.3,), r6(mid)+(.26,), r6(end)+(.22,)], 9, 2))
            tip = add(end, add(mul(ef, 1.35), mul(n, 1.05)))
            parts.append(tube(f'claw_{k}_'+side, [r6(sub(end, mul(ef, .15)))+(.24,), r6(add(end, add(mul(ef, .7), mul(n, .3))))+(.17,),
                                                   r6(tip)+(.015,)], 10, 3))
        b = add(WRIST[s], add(mul(e, .5), add(mul(w, .62), mul(n, .1))))
        t1 = add(b, add(mul(w, .6), add(mul(e, .55), mul(n, .3))))
        t2 = add(t1, add(mul(w, .25), add(mul(e, .55), mul(n, .55))))
        parts.append(tube('thumb_'+side, [r6(sub(b, mul(w, .3)))+(.3,), r6(b)+(.28,), r6(t1)+(.22,), r6(t2)+(.16,)], 9, 2))
        parts.append(tube('claw_thumb_'+side, [r6(sub(t2, mul(e, .1)))+(.17,), r6(add(t2, add(mul(e, .45), mul(n, .3))))+(.11,),
                                               r6(add(t2, add(mul(e, .75), mul(n, .75))))+(.01,)], 8, 3))
        # Three blunt toe claws on each hoof-like foot.
        to = TOE[s]
        for k, off in enumerate((-.42, 0, .42)):
            base = (to[0]-.35, to[1]+s*off, .72)
            parts.append(tube(f'toe_claw_{k}_'+side, [base+(.26,), (to[0]+.45, to[1]+s*off*1.1, .55, .18),
                                                     (to[0]+1.05, to[1]+s*off*1.15, .26, .02)], 8, 2))


def build_parts():
    parts = []
    build_body(parts)
    build_head(parts)
    build_hands(parts)
    build_spurs(parts)
    return materials.repack(parts)


# ---------------------------------------------------------------- weights
def sharp_chain(point, chain, k=.22, ids=None, rest=None):
    """Rigid segments that blend only near each joint."""
    ids_ = [(ids or IDS)[b] for b in chain]
    rest = rest or D_REST
    best = None
    for m, (a, b) in enumerate(zip(ids_, ids_[1:])):
        start, end = rest[a], rest[b]
        d = sub(end, start)
        t = clamp(dot(sub(point, start), d)/dot(d, d))
        distance = math.dist(point, add(start, mul(d, t)))
        if best is None or distance < best[0]-1e-9:
            best = (distance, m, t)
    _, m, t = best
    a, b = ids_[m], ids_[m+1]
    if m == len(ids_)-2 and t >= 1:
        return [(b, 1.)]
    wb = .5*smooth((t-(1-k))/k)
    out = {a: 1-wb, b: wb}
    if m > 0 and t < k:
        wp = .5*smooth((k-t)/k)
        out = {ids_[m-1]: wp, a: (1-wp)*(1-wb), b: (1-wp)*wb}
    return [(i, w) for i, w in out.items() if w > 1e-9]


def quantise(raw):
    """Quantised to 1e-6; the last influence takes the exact complement."""
    raw = sorted(raw, key=lambda x: (-x[1], x[0]))[:4]
    total = math.fsum(w for _, w in raw)
    raw = [(b, w/total) for b, w in raw]
    if len(raw) == 1:
        return [(raw[0][0], 1)]
    out = [(b, round(w, 6)) for b, w in raw[:-1]]
    rest = 1.-math.fsum(w for _, w in out)
    result = [(b, w) for b, w in out if w > 0]+([(raw[-1][0], rest)] if rest > 0 else [])
    return [(result[0][0], 1)] if len(result) == 1 else result


TORSO = ('pelvis', 'spine', 'chest', 'neck')


def raw_weights(part, v, uv):
    n = part.name
    side = n[-1]
    if n.startswith(('skin_cranium', 'skin_face', 'skin_chin', 'skin_nose', 'skin_brow', 'horn_', 'eye_', 'lid_', 'tooth_')):
        return [(IDS['head'], 1.)]
    if n.startswith('skin_ear'):
        s = 1 if side == 'L' else -1
        d = sub(EAR_TIP[s], EAR[s])
        t = clamp(dot(sub(v, EAR[s]), d)/dot(d, d))
        w = smooth((t-.1)/.4)
        return [(IDS['head'], 1-w), (IDS['ear_'+side], w)] if w > 0 else [(IDS['head'], 1.)]
    if n == 'skin_neck':
        return sharp_chain(v, ('chest', 'neck', 'head'), .35)
    if n.startswith(('skin_chest', 'skin_belly', 'skin_pelvis', 'skin_trap')):
        return D_RIG.chain_weights(v, [IDS[b] for b in TORSO])
    if n.startswith('skin_shoulder'):
        return sharp_chain(v, ('chest', 'arm_'+side, 'forearm_'+side), .3)
    if n.startswith('skin_arm'):
        return sharp_chain(v, ('chest', 'arm_'+side, 'forearm_'+side, 'hand_'+side), .22)
    if n.startswith(('skin_palm', 'thumb_', 'claw_thumb_')):
        return [(IDS['hand_'+side], 1.)]
    if n.startswith(('finger_', 'claw_')):
        return [(IDS['claws_'+side], 1.)]
    if n.startswith('skin_leg'):
        return sharp_chain(v, ('pelvis', 'thigh_'+side, 'shin_'+side, 'foot_'+side), .22)
    if n.startswith('skin_foot'):
        return sharp_chain(v, ('shin_'+side, 'foot_'+side, 'toes_'+side), .25)
    if n.startswith('toe_claw'):
        return [(IDS['toes_'+side], 1.)]
    if n == 'skin_tail':
        if v[0] > -1.2:
            return D_RIG.chain_weights(v, [IDS['spine'], IDS['pelvis']])
        return sharp_chain(v, ('pelvis', 'tail_0', 'tail_1', 'tail_2', 'tail_3', 'tail_4'), .35)
    if n.startswith('spur_shoulder'):
        return [(IDS['arm_'+side], 1.)]
    if n.startswith('spur_elbow'):
        return [(IDS['forearm_'+side], 1.)]
    if n.startswith('spike_'):
        z = SPINE_SPIKES[int(n.split('_')[1])]
        return [(IDS['neck' if z > 28.2 else 'chest' if z > 24.2 else 'spine' if z > 20.9 else 'pelvis'], 1.)]
    if n == 'skin_spade':
        return [(IDS['tail_4'], 1.)]
    raise ValueError('No weights for '+n)


def weights(part, v, uv):
    return quantise(raw_weights(part, v, uv))


# ---------------------------------------------------------------- posing
IDENT = (0., 0., 0., 1.)


class Pose:
    """Generic bone pose over a Rig (shared read-only by the fury)."""
    def __init__(self, rig=None, ids=None):
        self.rig = rig or D_RIG
        self.ids = ids or IDS
        self.rot = [IDENT for _ in self.rig.bones]
        self.shift = [(0., 0., 0.) for _ in self.rig.bones]

    def turn(self, bone, direction, degrees):
        i = self.ids[bone]
        self.rot[i] = qmul(axis(direction, math.radians(degrees)), self.rot[i])

    def frame(self):
        return [(*add(local, self.shift[i]), *self.rot[i], 1, 1, 1) for i, (_, _, local) in enumerate(self.rig.bones)]

    def world(self):
        return self.rig.matrices(self.frame())

    def point(self, bone, rest_point):
        loc, q = self.world()[self.ids[bone]]
        return add(loc, rotate(q, sub(rest_point, self.rig.rest[self.ids[bone]])))

    def aim(self, bone, child_rest, target_dir, blend=1.):
        i = self.ids[bone]
        world = self.world()
        parent = self.rig.bones[i][1]
        pq = world[parent][1] if parent >= 0 else IDENT
        current = rotate(qmul(pq, self.rot[i]), sub(child_rest, self.rig.rest[i]))
        delta = between(current, target_dir)
        if blend < 1: delta = slerp(IDENT, delta, blend)
        self.rot[i] = qmul(inverse(pq), qmul(delta, qmul(pq, self.rot[i])))

    def place_root(self, q, pivot, target):
        """Rotate the whole body by q so the rest point pivot lands at target."""
        self.rot[0] = q
        self.shift[0] = sub(target, rotate(q, pivot))

    def reach(self, upper, lower, end_rest, target, pole, blend=1.):
        """Two-bone IK: the end_rest point of `lower` toward a world target."""
        world = self.world()
        root = world[self.ids[upper]][0]
        current = self.point(lower, end_rest)
        target = lerp(current, target, blend)
        mid_rest = self.rig.rest[self.ids[lower]]
        l1 = math.dist(self.rig.rest[self.ids[upper]], mid_rest)
        l2 = math.dist(mid_rest, end_rest)
        d = max(abs(l1-l2)+1e-3, min(math.dist(root, target), l1+l2-1e-3))
        to = unit(sub(target, root))
        a = (l1*l1+d*d-l2*l2)/(2*l1*d)
        bend = ortho(pole, to)
        mid = add(root, add(mul(to, l1*a), mul(bend, l1*math.sqrt(max(0., 1-a*a)))))
        self.aim(upper, mid_rest, sub(mid, root))
        self.aim(lower, end_rest, sub(add(root, mul(to, d)), mid))


def roty(v, deg):
    return rotate(axis((0, 1, 0), math.radians(deg)), v)


def plant(P, side, ball, pitch=0., toe_pitch=0., blend=1.):
    """Digitigrade leg IK: ball of the foot to a world target, knee forward."""
    s = 1 if side == 'L' else -1
    hock = add(ball, roty(sub(HOCK[s], BALL[s]), pitch))
    P.reach('thigh_'+side, 'shin_'+side, HOCK[s], hock, (1, s*.12, 0), blend)
    P.aim('foot_'+side, BALL[s], sub(ball, P.point('foot_'+side, HOCK[s])), blend)
    P.aim('toes_'+side, TOE[s], roty(sub(TOE[s], BALL[s]), toe_pitch), blend)


def curl(P, side, degrees):
    s = 1 if side == 'L' else -1
    e, n, w = hand_frame(s)
    P.turn('claws_'+side, cross(e, n), degrees)


def tail_wave(P, amp_side, amp_up, phase, lift=0., k_lag=.75, straighten=0.):
    for k in range(5):
        P.turn(f'tail_{k}', (0, 0, 1), amp_side*math.sin(phase-k*k_lag))
        P.turn(f'tail_{k}', (0, 1, 0), -amp_up*math.sin(phase-k*k_lag+1.2)+lift*(1 if k < 3 else .5)+straighten*(1 if k >= 2 else -.3))


def chest_point(P, p):
    loc, q = P.world()[IDS['chest']]
    return add(loc, rotate(q, sub(p, D_REST[IDS['chest']])))


def carry(P, a, ph=0.):
    """Shared predatory crouch: torso pitched forward, head level and watching,
    long arms hanging low and forward with the claws spread and ready.

    Every action starts and ends here so nothing pops out of the idle."""
    if a <= 0: return
    P.turn('spine', (0, 1, 0), 16*a)
    P.turn('chest', (0, 1, 0), 14*a)
    P.turn('neck', (0, 1, 0), -17*a)
    P.turn('head', (0, 1, 0), -15*a)
    pelvis = P.world()[IDS['pelvis']][0]
    for side, s in SIDES:
        target = add(pelvis, (5.2, s*6.6, -6.4+.35*math.sin(ph+s)))
        P.reach('arm_'+side, 'forearm_'+side, WRIST[s], target, (-1, s*.9, .25), a)
        loc, q = P.world()[IDS['forearm_'+side]]
        P.aim('hand_'+side, knuckle(s), unit(lerp(rotate(q, sub(knuckle(s), WRIST[s])), (.6, s*.3, -.75), a)))
        curl(P, side, -22*a)


def stance(P, a=1.):
    for side, s in SIDES:
        plant(P, side, BALL[s], 0, 0, a)


CROUCH = (-.6, 0, -2.7)


def idle_pose(t):
    P = Pose()
    ph = TAU*t
    P.shift[0] = add(CROUCH, (.3*math.sin(ph), .6*math.sin(ph), .3*math.sin(2*ph)))
    P.turn('pelvis', (1, 0, 0), 3*math.sin(ph))
    carry(P, 1., ph)
    P.turn('chest', (0, 1, 0), 2*math.sin(2*ph))
    # Slow, sly scanning with a cocked head.
    P.turn('head', (0, 0, 1), 22*math.sin(ph))
    P.turn('head', (1, 0, 0), 9*math.sin(ph+.8)-4)
    twitch = max(0., math.sin(3*ph))**8
    P.turn('ear_L', (1, 0, 0), 12*twitch)
    P.turn('ear_R', (1, 0, 0), -6*max(0., math.sin(2*ph+1))**6)
    for side, s in SIDES:
        curl(P, side, 16*math.sin(TAU*3*t+s*1.3))
    tail_wave(P, 10, 5, ph*2, lift=8)
    P.turn('tail_4', (0, 1, 0), -14*max(0., math.sin(4*ph))**4)
    stance(P)
    return P


STRIDE = 4.2


def walk_pose(t):
    P = Pose()
    ph = TAU*t
    q = axis((0, 1, 0), math.radians(16))
    P.place_root(q, PELVIS, add(PELVIS, (.4, .45*math.sin(ph), -1.6+.8*abs(math.cos(ph)))))
    P.turn('pelvis', (0, 0, 1), 7*math.sin(ph))
    P.turn('chest', (0, 0, 1), -12*math.sin(ph))
    P.turn('neck', (0, 1, 0), -12)
    P.turn('head', (0, 1, 0), -8+3*math.sin(2*ph))
    P.turn('ear_L', (0, 1, 0), -14); P.turn('ear_R', (0, 1, 0), -14)
    for side, s in SIDES:
        f = (t+(0 if s > 0 else .5)) % 1
        if f < .5:
            u = f/.5
            ball = (BALL[s][0]+STRIDE*(1-2*u), BALL[s][1], BALL[s][2])
            pitch, toe = 0, 0
        else:
            u = (f-.5)/.5
            ball = (BALL[s][0]-STRIDE+2*STRIDE*smooth(u), BALL[s][1], BALL[s][2]+3.6*math.sin(math.pi*u))
            pitch, toe = -38*math.sin(math.pi*u), -30*math.sin(math.pi*u)
        plant(P, side, ball, pitch, toe)
        swing = math.sin(ph+(math.pi if s > 0 else 0))
        P.turn('arm_'+side, (0, 1, 0), -38*swing-10)
        P.turn('arm_'+side, (1, 0, 0), s*-8)
        P.turn('forearm_'+side, (0, 1, 0), -30-15*swing)
        curl(P, side, 30)
    tail_wave(P, 10, 4, 2*ph, lift=0, straighten=10)
    return P


def slice_pose(t):
    """Attack ("slices"): wind up with the right claw high behind the head, then a
    leaping lunge whose middle frame rakes the claws far out across the front."""
    P = Pose()
    wind = window(t, .04, .3)*(1-window(t, .34, .44))
    strike = window(t, .34, .44)*(1-window(t, .62, .95))
    rest = 1-max(wind, strike)
    yaw = -22*wind+30*strike
    pitch = -8*wind+28*strike
    q = qmul(axis((0, 0, 1), math.radians(yaw)), axis((0, 1, 0), math.radians(pitch)))
    P.place_root(q, PELVIS, add(add(PELVIS, lerp((0, 0, 0), CROUCH, rest)), (-1.4*wind+6.0*strike, 1.2*strike, -1.6*wind-2.4*strike)))
    carry(P, rest)
    P.turn('neck', (0, 1, 0), -14*strike)
    P.turn('head', (0, 1, 0), -12*strike+8*wind)
    P.turn('head', (0, 0, 1), -10*strike)
    for e, sgn in (('ear_L', 1), ('ear_R', -1)):
        P.turn(e, (0, 1, 0), -24*strike)
    # Right arm: cocked high behind the head, then flung forward and out, claws splayed.
    high = chest_point(P, (-1.8, -7.0, 30.0))
    rake = chest_point(P, (13.5, -9.0, 25.0))
    amount = wind+strike
    if amount > 1e-6:
        P.reach('arm_R', 'forearm_R', WRIST[-1], lerp(high, rake, strike/amount), (-.6, -.5, -1), min(1., amount))
        loc, fq = P.world()[IDS['forearm_R']]
        P.aim('hand_R', knuckle(-1), rotate(fq, sub(knuckle(-1), WRIST[-1])))
    curl(P, 'R', 25*rest-35*strike+10*wind)
    # Left arm swings back and up for balance.
    back = chest_point(P, (-6.5, 6.5, 24.0))
    if amount > 1e-6:
        P.reach('arm_L', 'forearm_L', WRIST[1], lerp(chest_point(P, (4.0, 5.0, 24.0)), back, strike/amount), (1, .5, -.3), min(1., amount))
    curl(P, 'L', 25*rest+20*strike)
    # Lunge: right foot steps far forward, left leg stretched behind.
    plant(P, 'R', lerp(BALL[-1], (7.5, -3.6, 1.15), strike), 0, 0)
    plant(P, 'L', lerp(BALL[1], (-1.8, 3.4, 1.15), strike), 22*strike, 0)
    # Tail whips up into a tall curl.
    tail_wave(P, 8*rest, 3*rest, 4*math.pi*t, lift=26*strike+8*wind)
    P.turn('tail_3', (0, 1, 0), -18*strike)
    return P


def snatch_pose(t):
    """Alternate attack: a low diving two-handed grab, then a gleeful clutch.
    Cosmetic only: it does not claim that Brogue's theft happened."""
    P = Pose()
    coil = window(t, .04, .28)*(1-window(t, .32, .44))
    dive = window(t, .32, .44)*(1-window(t, .6, .72))
    clutch = window(t, .6, .72)*(1-window(t, .8, .97))
    rest = 1-max(coil, dive, clutch)
    pitch = 14*coil+42*dive+6*clutch
    q = axis((0, 1, 0), math.radians(pitch))
    P.place_root(q, PELVIS, add(add(PELVIS, lerp((0, 0, 0), CROUCH, rest)),
                                (-1.8*coil+6.5*dive+1.0*clutch, 0, -3.0*coil-3.6*dive-1.2*clutch)))
    carry(P, rest)
    P.turn('neck', (0, 1, 0), -30*dive+6*coil-10*clutch)
    P.turn('head', (0, 1, 0), -20*dive+10*clutch)
    P.turn('head', (1, 0, 0), 14*clutch*math.sin(TAU*3*t))
    for side, s in SIDES:
        P.turn('ear_'+side, (0, 1, 0), -30*dive+10*coil)
        low = chest_point(P, (-1.5, s*5.5, 18.5))
        grab = chest_point(P, (14.5, s*6.2, 21.0))
        hug = chest_point(P, (3.6, s*1.2, 24.5))
        amount = coil+dive+clutch
        if amount > 1e-6:
            target = (low if coil >= max(dive, clutch) else grab if dive >= clutch else hug)
            if coil > 0 and dive > 0: target = lerp(low, grab, dive/(coil+dive))
            if dive > 0 and clutch > 0: target = lerp(grab, hug, clutch/(dive+clutch))
            P.reach('arm_'+side, 'forearm_'+side, WRIST[s], target, (-.4, s*1, -.6) if dive > .3 else (-1, s*.6, -.2), min(1., amount))
            loc, fq = P.world()[IDS['forearm_'+side]]
            P.aim('hand_'+side, knuckle(s), rotate(fq, sub(knuckle(s), WRIST[s])), min(1., amount))
        curl(P, side, 25*rest+10*coil-40*dive+70*clutch)
        plant(P, side, lerp(BALL[s], (BALL[s][0]+2.2, BALL[s][1]*1.15, BALL[s][2]), dive), 26*dive, 0)
    tail_wave(P, 10*rest+14*clutch, 4, 2*TAU*t, lift=6*coil+30*dive+14*clutch)
    return P


def recoil_pose(t):
    P = Pose()
    p = math.sin(math.pi*t)**1.3
    shake = math.sin(TAU*2.5*t)*math.sin(math.pi*t)
    q = qmul(axis((1, 0, 0), math.radians(8*shake)), axis((0, 1, 0), math.radians(-20*p)))
    P.place_root(q, PELVIS, add(add(PELVIS, lerp((0, 0, 0), CROUCH, 1-p*.6)), (-2.6*p, .4*shake, .4*p)))
    carry(P, 1-min(1, 1.5*p))
    P.turn('chest', (0, 1, 0), -10*p)
    P.turn('neck', (0, 1, 0), -12*p)
    P.turn('head', (0, 1, 0), -18*p)
    P.turn('head', (0, 0, 1), 20*shake)
    for side, s in SIDES:
        P.turn('ear_'+side, (0, 1, 0), 40*p)
        P.turn('ear_'+side, (1, 0, 0), -s*20*p)
        guard = chest_point(P, (3.0, s*6.5, 31.5))
        P.reach('arm_'+side, 'forearm_'+side, WRIST[s], guard, (-.3, s, -.8), min(1., 1.4*p))
        curl(P, side, 25*(1-p)-30*p)
        plant(P, side, BALL[s])
    tail_wave(P, 6, 6, TAU*2*t, lift=20*p)
    return P


# Death: stagger, topple forward, land prone and go limp along the +X axis.
PRONE_Q = axis((0, 1, 0), math.radians(90))
PRONE_PELVIS = (-3.4, 0.6, 3.15)
_FINAL = []


def prone_final():
    """The settled limp pose, built once from world-space segment directions."""
    if _FINAL: return _FINAL[0]
    P = Pose()
    P.place_root(qmul(axis((1, 0, 0), math.radians(-6)), PRONE_Q), PELVIS, PRONE_PELVIS)
    P.turn('spine', (0, 1, 0), -12)
    P.turn('chest', (0, 1, 0), -9)
    P.turn('chest', (1, 0, 0), 4)
    # Head on its cheek, ears flopped (angles from a floor-contact search).
    P.turn('head', (0, 1, 0), -8)
    P.turn('head', (0, 0, 1), 30)
    P.turn('ear_L', (1, 0, 0), -70)
    P.turn('ear_R', (1, 0, 0), -40)
    # Arms flop out along the floor: one flung forward past the head, one back by the hip.
    P.aim('arm_L', ELBOW[1], (.55, .82, -.16)); P.aim('forearm_L', WRIST[1], (.85, .5, -.08)); P.aim('hand_L', knuckle(1), (.93, .3, .2))
    P.aim('arm_R', ELBOW[-1], (-.3, -.93, -.2)); P.aim('forearm_R', WRIST[-1], (-.8, -.58, -.05)); P.aim('hand_R', knuckle(-1), (-.9, -.2, -.35))
    curl(P, 'L', 12); curl(P, 'R', 8)
    # Legs splay behind, one knee drawn up to the side.
    P.aim('thigh_L', KNEE[1], (-.55, .8, -.18)); P.aim('shin_L', HOCK[1], (-.92, -.3, -.02)); P.aim('foot_L', BALL[1], (-.95, .2, .12))
    P.aim('thigh_R', KNEE[-1], (-.97, -.22, -.1)); P.aim('shin_R', HOCK[-1], (-.9, -.43, .02)); P.aim('foot_R', BALL[-1], (-.9, -.35, .18))
    P.aim('toes_L', TOE[1], (-.85, .1, -.3)); P.aim('toes_R', TOE[-1], (-.8, -.2, -.25))
    # Tail drops off the rump and lies in a loose curve on the floor.
    for k, d in enumerate(((-.5, .3, -.8), (-.9, .42, -.12), (-.75, .66, 0.), (-.2, .98, 0.), (.4, .92, 0.))):
        P.aim(f'tail_{k}', TAIL[k+1] if k < 4 else TAIL_END, d)
    _FINAL.append(P.rot[:])
    return P.rot


def death_pose(t):
    P = Pose()
    jolt = window(t, 0, .08)*(1-window(t, .1, .22))
    u = clamp((t-.12)/.56)
    fall = smooth(u)
    drop = u*u
    settle = window(t, .6, .9)
    bounce = .9*math.sin(math.pi*clamp((t-.68)/.14))*(1-settle)
    tilt = qmul(axis((1, 0, 0), math.radians(-6)), PRONE_Q)
    q = slerp(axis((0, 1, 0), math.radians(-12*jolt)), tilt, fall)
    start = add(PELVIS, lerp((0, 0, 0), CROUCH, 1-window(t, 0, .1)))
    target = add(lerp(lerp(start, (6.0, .3, 12.0), smooth(u*1.6)), PRONE_PELVIS, drop), (0, 0, bounce))
    P.place_root(q, PELVIS, target)
    carry(P, 1-window(t, 0, .1))
    P.turn('chest', (0, 1, 0), -16*jolt)
    P.turn('head', (0, 1, 0), -26*jolt)
    for side, s in SIDES:
        # Arms fling up in the jolt, then trail as the body pitches over.
        P.turn('arm_'+side, (1, 0, 0), s*-50*jolt)
        P.turn('arm_'+side, (0, 1, 0), -60*jolt-40*math.sin(math.pi*u))
        P.turn('thigh_'+side, (0, 1, 0), 30*math.sin(math.pi*u))
        P.turn('shin_'+side, (0, 1, 0), -40*math.sin(math.pi*u))
        P.turn('ear_'+side, (0, 1, 0), -30*jolt)
        curl(P, side, -30*jolt)
    tail_wave(P, 0, 0, 0, lift=24*jolt)
    hold = 1-window(t, .3, .55)
    for side, s in SIDES:
        plant(P, side, BALL[s], 0, 0, hold)
    final = prone_final()
    limp = smooth(clamp((t-.3)/.45))*.75+settle*.25
    for i in range(1, len(BONES)):
        P.rot[i] = slerp(P.rot[i], final[i], limp)
    ground_guard(P, 1-window(t, .8, .97), .35)
    return P


def claw_tip(s, off=0.):
    e, n, w = hand_frame(s)
    ef = unit(add(e, mul(w, off*.55)))
    return add(add(knuckle(s), mul(w, off)), add(mul(ef, 3.5), mul(n, 1.6)))


PROBES = ([('toes_'+s, add(TOE[k], (1.05, 0, -.4))) for s, k in SIDES]+[('toes_'+s, BALL[k]) for s, k in SIDES]
          + [('foot_'+s, HOCK[k]) for s, k in SIDES]+[('claws_'+s, claw_tip(k, o)) for s, k in SIDES for o in (-.55, 0, .55)]
          + [('head', (6.2, 0, 31.0)), ('head', (-4.8, 4.6, 40.5)), ('head', (-4.8, -4.6, 40.5)), ('tail_4', TAIL_END)])


def ground_guard(P, amount, floor=.9):
    """While still falling, lift the whole body so no probe dips below the floor.

    Fades to zero before the settled pose, which must rest on the floor itself."""
    if amount <= 0: return
    low = min(P.point(b, p)[2] for b, p in PROBES)
    if low < floor:
        P.shift[0] = add(P.shift[0], (0, 0, (floor-low)*amount))


def design_pose(name, t):
    fn = {'idle': idle_pose, 'walk': walk_pose, 'slice': slice_pose, 'snatch': snatch_pose,
          'recoil': recoil_pose, 'death': death_pose}[name]
    return fn(t).frame()


def pose(name, t):
    """Exported frame: the design pose with every translation scaled by SCALE."""
    return [(*mul(row[:3], SCALE), *row[3:]) for row in design_pose(name, t)]


# Exported (scaled) skeleton: uniform scale of every rest position; rotations and
# unit bone scales are unchanged, so deform(SCALE*v, pose) == SCALE*design deform.
RIG = Rig.from_world([(n, p, mul(pt, SCALE)) for n, p, pt in SPECS])
BONES, REST = RIG.bones, RIG.rest


# ---------------------------------------------------------------- export
def geometry():
    """Weights and atlas are computed at design scale, then every vertex is scaled."""
    from .connected_skin import attach
    parts = attach('imp', build_parts(), weights)
    parts, v, n, uv, tr, w = assemble(materials.connected_atlas(parts), weights)
    for p in parts:
        p.vertices = [mul(q, SCALE) for q in p.vertices]
    return parts, [mul(q, SCALE) for q in v], n, uv, tr, w


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from .connected_skin import attach
    return materials.connected_atlas(attach('imp', build_parts(), weights), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_imp', material_path=SKIN)
    path = ROOT/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M45', format='IQM v2', runtimeModel=MODEL,
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/imp/imp-animated.blend')
    out = ROOT/'assets/monsters/imp'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Re-import under the package name so connected_skin finds CONNECTED_SKIN.
    import importlib
    print(importlib.import_module('tools.monster_models.imp_animation').build()['sha256'])
