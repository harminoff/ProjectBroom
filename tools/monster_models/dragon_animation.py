"""Original connected dragon, six purely cosmetic skeletal roles. No gameplay.

Brogue: "An ancient serpent of the world's deepest places, the dragon's immense
form belies its lightning-quick speed ... an undying furnace of white-hot flames
burns within its scaly hide." It claws, tail-whips and bites, and breathes
Brogue's dragonfire bolt. This is a compact winged quadruped that fits the
64-unit cell: a heavy four-legged body with a barrel chest, a thick S-curved
neck and a long horned head with a hinged lower jaw at +X, a coiled tail ending
in a blade, a ridge of dorsal spines, and two membrane wings folded high over
the back (bone arm, three two-jointed fingers, scalloped membranes). Source
colour cue: Brogue's glyph is green; the paint here is a warm crimson so the
creature separates from grey walls, with green eyes as the source nod.

Fire is three short teardrop parts parked inside the skull. Only the breathe
clip slides them out of the mouth; no clip uses bone scale. Every outcome
(breath bolt, damage, targets, range, burning, timing) belongs to Brogue: this
module only draws poses. +X forward, Z up, +Y left. No MODELDEF visualScale.
"""
import hashlib
import json
import math

from . import iqm, dragon_materials as materials
from .rat import ROOT, Part, add, sub, mul, unit, cross
from .skeletal import Rig, axis, qmul, inverse, rotate, between, assemble, sample_clips
from .pixie_animation import dot, clamp, smooth, window, lerp, r6, ortho, blob, tube, shell, slerp
from .imp_animation import Pose as _Pose

SKIN = materials.SKIN
MODEL = 'mod/BrogueDoom/models/monsters/50_dragon.iqm'
TAU = math.tau
SIDES = (('L', 1), ('R', -1))
SKIN_VOXEL_SIZE = .13
SKIN_FACE_BUDGET = 8000
DIAG_COLOURS = {'skin': (190, 40, 40), 'horn': (230, 215, 175), 'membrane': (150, 30, 40), 'bone': (110, 30, 30),
                'claw': (230, 220, 190), 'tooth': (250, 245, 225), 'eye': (170, 230, 40), 'jaw': (180, 60, 60),
                'spike': (120, 70, 40), 'tongue': (230, 90, 110), 'flame': (255, 170, 30)}


def CONNECTED_SKIN(name):
    return name.startswith('skin_')


# ---------------------------------------------------------------- skeleton
PELVIS, SPINE, CHEST = (-10., 0, 14.), (-2., 0, 14.5), (5.5, 0, 16.)
HEAD_DZ = materials.HEAD_DZ   # the head is authored at its original height, then raised on a taller S-neck
NECK0, NECK1, HEAD = (9.5, 0, 22.), (12.5, 0, 35.), (14.8, 0, 30.6+HEAD_DZ)
SNOUT = (28.6, 0, 29.6+HEAD_DZ)
JAW = (17.5, 0, 28.0+HEAD_DZ)
JAW_TIP = (26.5, 0, 27.3+HEAD_DZ)
MOUTH = (26.0, 0, 28.2+HEAD_DZ)           # where the breath leaves the open jaws (head rest frame)
FLAME_J = (0.6, 3.6, 6.6, 9.6)            # joint offsets of the four flame layers along the jet axis
FLAME_LEN = (14.0, 12.5, 7.5, 5.5)        # longest tongue of each layer
TUCK = (-4.5, 0., 15.0)                   # the flame stays parked inside the chest and belly (jet origin at rest)
FLAME = [(TUCK[0]+j, TUCK[1], TUCK[2]) for j in FLAME_J]
SHOULDER = {s: (7.5, s*7.8, 17.5) for _, s in SIDES}
ELBOW = {s: (4.0, s*10., 10.5) for _, s in SIDES}
WRISTF = {s: (9.5, s*9.5, 4.2) for _, s in SIDES}
TOEF = {s: (14.6, s*9.6, 1.0) for _, s in SIDES}
HIP = {s: (-10.5, s*7.5, 14.5) for _, s in SIDES}
KNEE = {s: (-5.5, s*10.5, 9.5) for _, s in SIDES}
HOCK = {s: (-13., s*10.5, 5.5) for _, s in SIDES}
BALL = {s: (-9.5, s*10.5, 1.5) for _, s in SIDES}
TOE = {s: (-5.5, s*10.5, 1.1) for _, s in SIDES}
TAIL = [(-15., 0, 13.5), (-20., 1.5, 11.5), (-23.5, 5.5, 9.5), (-24.5, 11.5, 8.), (-21.5, 16.5, 6.5), (-15.5, 18.5, 5.8)]
TAIL_END = (-11., 16.5, 5.6)
S0 = {s: (3.2, s*6.0, 22.) for _, s in SIDES}
ELB = {s: (-3., s*13., 29.5) for _, s in SIDES}
WRIST = {s: (-11., s*16.5, 32.) for _, s in SIDES}
FS = .85   # finger length factor: compact wings keep every pose inside the 64-unit cell
_FJ = {1: (-16.5, 18.5, 27.5), 2: (-17., 16., 24.), 3: (-15.5, 13., 21.5)}
_FT = {1: (-21., 20., 21.), 2: (-22., 16.5, 14.5), 3: (-19., 12., 10.)}
FJ = {f: {s: r6(lerp(WRIST[s], (_FJ[f][0], s*_FJ[f][1], _FJ[f][2]), FS)) for _, s in SIDES} for f in (1, 2, 3)}
FT = {f: {s: r6(lerp(WRIST[s], (_FT[f][0], s*_FT[f][1], _FT[f][2]), FS)) for _, s in SIDES} for f in (1, 2, 3)}
BODY_LINE = {s: [(2.5, s*4.6, 22.4), (-3.5, s*3.0, 19.6), (-9.5, s*3.2, 19.2)] for _, s in SIDES}

SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', PELVIS), ('spine', 'pelvis', SPINE), ('chest', 'spine', CHEST),
         ('neck_0', 'chest', NECK0), ('neck_1', 'neck_0', NECK1), ('head', 'neck_1', HEAD), ('jaw', 'head', JAW)]
for k, p in enumerate(FLAME):
    SPECS.append((f'flame_{k}', 'chest', p))
for side, s in SIDES:
    SPECS += [('arm_'+side, 'chest', SHOULDER[s]), ('fore_'+side, 'arm_'+side, ELBOW[s]),
              ('paw_'+side, 'fore_'+side, WRISTF[s]),
              ('thigh_'+side, 'pelvis', HIP[s]), ('shin_'+side, 'thigh_'+side, KNEE[s]),
              ('foot_'+side, 'shin_'+side, HOCK[s]), ('toes_'+side, 'foot_'+side, BALL[s]),
              ('wing_a_'+side, 'chest', S0[s]), ('wing_b_'+side, 'wing_a_'+side, ELB[s])]
    for f in (1, 2, 3):
        SPECS += [(f'f{f}a_'+side, 'wing_b_'+side, WRIST[s]), (f'f{f}b_'+side, f'f{f}a_'+side, FJ[f][s])]
for k, p in enumerate(TAIL):
    SPECS.append((f'tail_{k}', 'pelvis' if k == 0 else f'tail_{k-1}', p))
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, _, _) in enumerate(BONES)}
CLIPS = [('idle', 48, 24, True), ('stalk', 32, 30, True), ('breathe', 30, 30, False), ('lash', 28, 30, False),
         ('recoil', 14, 30, False), ('death', 40, 30, False)]


def Pose():
    return _Pose(RIG, IDS)


# ---------------------------------------------------------------- primitives
def xblob(name, center, radii, seg=28, rings=18, taper=None):
    """Blob with poles along X; radii are (x, y, z)."""
    return blob(name, center, (1, 0, 0), (0, 1, 0), radii, seg, rings, taper)


def leaf(name, base, tip, facing, width, thick, seg=16, rings=14, keep=.25):
    a0 = unit(sub(tip, base))
    f = ortho(facing, a0)
    w = cross(f, a0)
    half = math.dist(base, tip)/2
    return blob(name, lerp(base, tip, .5), a0, w, (half, width, thick), seg, rings,
                taper=lambda xi: keep+(1-keep)*clamp((1-xi)/1.3)**.7)


def sp(points, radii):
    return [(*r6(p), r) for p, r in zip(points, radii)]


# ---------------------------------------------------------------- anatomy
SKULL_C, SKULL_R = (18.0, 0, 31.2), (5.0, 4.5, 4.0)
SNOUT_SECTIONS = ((18.4, 3.1, 33.4, 27.3, 3.0), (22.0, 2.7, 32.1, 27.5, 3.6), (25.6, 2.2, 31.6, 27.7, 3.8),
                  (28.6, 1.6, 31.2, 28.0, 3.4))   # x, half width, top z, bottom z, superellipse power: a flat-topped wedge


def snout_lip(x):
    """(half width, bottom z) of the wedge snout at x."""
    for (x0, w0, t0, b0, _), (x1, w1, t1, b1, _) in zip(SNOUT_SECTIONS, SNOUT_SECTIONS[1:]):
        if x <= x1:
            f = clamp((x-x0)/(x1-x0))
            return w0+(w1-w0)*f, b0+(b1-b0)*f
    return SNOUT_SECTIONS[-1][1], SNOUT_SECTIONS[-1][3]


def wedge(name, sections, ring=28):
    """Closed lofted solid along +X; every section is a superellipse (half width, z range, power). UV unused."""
    p = Part(name)
    for x, hw, zt, zb, n in sections:
        zc, hh = (zt+zb)/2, (zt-zb)/2
        for j in range(ring):
            a = TAU*j/ring
            c, sn = math.cos(a), math.sin(a)
            p.vertices.append(r6((x, hw*math.copysign(abs(c)**(2/n), c), zc+hh*math.copysign(abs(sn)**(2/n), sn))))
            p.uv.append((0., 0.))
    for i in range(len(sections)-1):
        for j in range(ring):
            a = i*ring+j
            p.faces.append((a, i*ring+(j+1) % ring, (i+1)*ring+(j+1) % ring, (i+1)*ring+j))
    for end, rev in ((0, True), (len(sections)-1, False)):
        x, hw, zt, zb, n = sections[end]
        p.vertices.append((x, 0., round((zt+zb)/2, 6))); p.uv.append((0., 0.))
        cen = len(p.vertices)-1
        for j in range(ring):
            a, b = end*ring+j, end*ring+(j+1) % ring
            p.faces.append((cen, b, a) if rev else (cen, a, b))
    return p


def lift_head(parts, start):
    """Raise the head group (authored at design height) onto the taller neck."""
    for p in parts[start:]:
        p.vertices = [(x, y, round(z+HEAD_DZ, 6)) for x, y, z in p.vertices]


def build_head(parts):
    start = len(parts)
    parts.append(xblob('skin_skull', SKULL_C, SKULL_R, 36, 24))
    parts.append(wedge('skin_snout', SNOUT_SECTIONS))
    for side, s in SIDES:
        parts.append(xblob('skin_cheek_'+side, (20.2, s*3.3, 28.7), (2.5, 1.1, 1.2), 20, 12))
        parts.append(xblob('skin_nostril_'+side, (27.3, s*1.0, 31.5), (1.1, .65, .5), 14, 10))
        parts.append(tube('skin_nridge_'+side, [(27.0, s*1.0, 31.7, .5), (25.2, s*1.15, 32.1, .55), (23.4, s*1.3, 32.4, .42)], 10, 3))
        # Heavy bony brow overhanging the eye, running down to the snout.
        brow = [(16.4, s*3.2, 34.0, 1.1), (18.8, s*4.0, 33.7, 1.5), (21.0, s*3.4, 33.2, 1.3), (22.8, s*2.4, 32.6, .85), (24.2, s*1.7, 32.2, .4)]
        parts.append(tube('skin_brow_'+side, brow, 14, 3))
        # Main swept-back horn plus a smaller cheek horn, jaw spikes flaring back and a row of brow spines.
        horn = [(16.2, s*2.8, 34.6, 1.15), (13.5, s*3.8, 36.2, 1.0), (10.0, s*5.0, 37.0, .75), (6.5, s*6.4, 36.5, .48),
                (3.5, s*7.6, 35.0, .22), (1.5, s*8.3, 33.6, .02)]
        parts.append(tube('horn_'+side, horn, 14, 3))
        horn2 = [(15.5, s*3.9, 30.0, .7), (13.0, s*6.0, 29.8, .5), (10.8, s*7.4, 29.0, .25), (9.4, s*8.0, 28.2, .02)]
        parts.append(tube('horn2_'+side, horn2, 10, 3))
        spike = [(19.0, s*4.5, 28.6, .5), (17.8, s*6.0, 27.6, .3), (16.9, s*6.9, 26.9, .02)]
        parts.append(tube('horn3_'+side, spike, 8, 3))
        for k, (bx, by, bz) in enumerate(((17.6, 3.7, 35.0), (19.6, 4.0, 35.0), (21.4, 3.4, 34.3), (23.0, 2.5, 33.4))):
            d = unit((-.7, s*.35, .6))
            base = (bx, s*by, bz)
            parts.append(tube(f'horn4_{k}_'+side, [(*base, .42), (*r6(add(base, mul(d, .9))), .3), (*r6(add(base, mul(d, 2.0-.1*k))), .02)], 8, 2))
        for k, (bx, by, bz, ln) in enumerate(((20.2, 4.2, 28.4, 3.4), (18.8, 4.4, 29.4, 3.0), (17.4, 4.3, 30.6, 2.6))):
            d = unit((-.65, s*.6, -.1))
            base = (bx, s*by, bz)
            parts.append(tube(f'horn5_{k}_'+side, [(*base, .5), (*r6(add(base, mul(d, ln*.5))), .33), (*r6(add(base, mul(d, ln))), .02)], 8, 2))
        # Small narrow amber slits set flush under the brow: no bulging eyeball.
        f = unit((math.cos(math.radians(50)), s*math.sin(math.radians(50)), .12))
        lat = ortho(unit((0, s, .4)), f)
        up = unit(cross(lat, f))
        if up[2] < 0: up = mul(up, -1)
        c = (19.5, s*4.1, 32.0)
        parts.append(blob('eye_'+side, r6(c), f, up, (.32, .5, 1.15), 24, 14))
        parts.append(blob('lid_'+side, r6(add(c, add(mul(up, .42), mul(f, .04)))), f, up, (.34, .34, 1.3), 20, 10))
        # Lipless upper teeth overlapping the lower jaw, two long fangs.
        for k, x in enumerate((20.6, 22.2, 23.8, 25.3, 26.6, 27.7)):
            hw, zb = snout_lip(x)
            base = (x, s*hw*.92, zb+1.0)
            ln = 3.6 if k in (1, 4) else 2.4
            m1 = r6(add(base, (.05, s*.1, -.55*ln)))
            parts.append(tube(f'tooth_{k}_'+side, [(*r6(base), .4), (*m1, .29), (*r6(add(base, (.2, s*.18, -ln))), .01)], 8, 2))
    # Lower jaw (hinged), tongue and lower teeth ride on the jaw bone.
    parts.append(xblob('jaw', (22.6, 0, 27.3), (5.8, 2.2, 1.25), 28, 18, taper=lambda xi: .95-.3*(xi+1)/2))
    parts.append(xblob('tongue', (21.6, 0, 28.4), (3.4, .85, .4), 16, 10))
    for side, s in SIDES:
        for k, x in enumerate((21.0, 23.2, 25.4)):
            parts.append(tube(f'ltooth_{k}_'+side, [(x, s*1.7, 28.2, .26), (x+.05, s*1.65, 29.2, .2), (x+.15, s*1.6, 30.3, .01)], 6, 2))
    lift_head(parts, start)


def dorsal_points():
    """(base, direction, length) for spines from the back of the skull along the neck, back and tail."""
    out = []
    # Neck: offset the neck spline (up/back side).
    neck_pts = [(14.0, 46.0), (12.9, 42.5), (11.6, 38.0), (10.4, 33.0), (9.2, 28.0), (8.0, 22.5)]
    for k, (x, z) in enumerate(neck_pts):
        out.append(((x, 0, z), unit((-.55, 0, .85)), 2.7-.14*k))
    for x in (3.5, .5, -2.5, -5.5, -8.5, -11.5):
        out.append(((x, 0, torso_top(x)-.5), unit((-.45, 0, .9)), 3.0-.1*abs(x)*.12))
    tail_tops = [(-15.3, 0, 16.3), (-17.5, .8, 15.0), (-20.3, 1.9, 13.6), (-22.8, 4.3, 12.0), (-24.6, 8.6, 10.7)]
    for k, p in enumerate(tail_tops):
        out.append((p, unit((-.5, -.1, .85)), 2.5-.32*k))
    return out


def torso_top(x):
    best = 0.
    for c, r in TORSO_BLOBS:
        q = 1-((x-c[0])/r[0])**2
        if q > 0: best = max(best, c[2]+r[2]*math.sqrt(q))
    return best


TORSO_BLOBS = [((-10.5, 0, 14.5), (6.6, 7.0, 6.2)), ((-2.5, 0, 14.0), (6.8, 6.8, 6.3)), ((5.5, 0, 16.0), (7.2, 7.4, 7.4))]


def build_body(parts):
    for (c, r), name in zip(TORSO_BLOBS, ('skin_hip', 'skin_belly', 'skin_chest')):
        parts.append(xblob(name, c, r, 34, 22))
    neck = [(7.5, 0, 18.5, 4.7), (9.5, 0, 22.5, 4.4), (10.8, 0, 28.5, 4.0), (12.3, 0, 35.0, 3.7), (14.0, 0, 40.5, 3.6),
            (15.9, 0, 44.0, 3.6)]
    parts.append(tube('skin_neck', neck, 22, 3))
    tail = [(-12.5, 0, 14.0, 4.6), (*TAIL[0], 4.0), (*TAIL[1], 3.2), (*TAIL[2], 2.6), (*TAIL[3], 2.0), (*TAIL[4], 1.45),
            (*TAIL[5], 1.0), (*TAIL_END, .6)]
    parts.append(tube('skin_tail', tail, 16, 3))
    a0 = unit(sub(TAIL_END, TAIL[5]))
    tip = add(TAIL_END, mul(a0, 5.0))
    parts.append(leaf('tail_blade', add(TAIL_END, mul(a0, -.3)), tip, (0, 0, 1), 2.1, .3, 20, 14, .12))
    for side, s in SIDES:
        parts.append(xblob('skin_wshoulder_'+side, (3.2, s*5.4, 22.0), (3.4, 2.8, 3.0), 20, 14))
        sh, el, wr = SHOULDER[s], ELBOW[s], WRISTF[s]
        parts.append(xblob('skin_shoulder_'+side, (7.2, s*7.6, 16.8), (3.4, 2.6, 4.6), 22, 14))
        parts.append(tube('skin_arm_'+side, [(6.6, s*7.0, 18.6, 3.5), (*sh, 3.4), (*lerp(sh, el, .5), 2.9), (*el, 2.25),
                                              (*lerp(el, wr, .5), 1.95), (*wr, 1.75)], 18, 3))
        ball, tip = (12.0, s*9.6, 1.7), TOEF[s]
        parts.append(tube('skin_paw_'+side, [(*wr, 1.75), (10.8, s*9.6, 2.6, 1.8), (*ball, 1.4), (13.0, s*9.6, 1.3, 1.1)], 14, 3))
        for k in (-1, 0, 1):
            y = s*(9.6+k*1.55)
            parts.append(tube(f'skin_toe_{k+1}_'+side, [(12.0, s*(9.6+k*.6), 2.0, .95), (13.5, y, 1.4, .8),
                                                        (14.8+.1*(k == 0), s*(9.6+k*2.1), .9, .55)], 8, 2))
            parts.append(tube(f'claw_{k+1}_'+side, [(14.6, s*(9.6+k*2.1), 1.1, .42), (16.1, s*(9.6+k*2.4), .9, .3),
                                                    (17.2, s*(9.6+k*2.6), .5, .02)], 8, 3))
        hp, kn, hk, bl, to = HIP[s], KNEE[s], HOCK[s], BALL[s], TOE[s]
        parts.append(xblob('skin_haunch_'+side, (-9.2, s*8.0, 13.4), (4.6, 3.2, 5.6), 24, 16))
        parts.append(tube('skin_leg_'+side, [(-10.0, s*7.5, 15.0, 3.9), (*hp, 3.7), (*lerp(hp, kn, .55), 3.0), (*kn, 2.45),
                                              (*lerp(kn, hk, .5), 1.8), (*hk, 1.5)], 20, 3))
        parts.append(tube('skin_foot_'+side, [(*hk, 1.5), (-11.4, s*10.5, 3.4, 1.4), (*bl, 1.3), (-7.4, s*10.5, 1.4, 1.1),
                                               (*to, .7)], 14, 3))
        for k in (-1, 0, 1):
            y = s*(10.5+k*1.5)
            parts.append(tube(f'skin_htoe_{k+1}_'+side, [(-9.0, s*(10.5+k*.6), 2.0, .95), (-7.0, y, 1.4, .8),
                                                         (-5.6+.1*(k == 0), s*(10.5+k*2.0), .95, .55)], 8, 2))
            parts.append(tube(f'claw_h{k+1}_'+side, [(-5.6, s*(10.5+k*2.0), 1.1, .42), (-4.1, s*(10.5+k*2.3), .9, .3),
                                                     (-3.1, s*(10.5+k*2.5), .5, .02)], 8, 3))
    for k, (base, d, length) in enumerate(dorsal_points()):
        tip = add(base, mul(d, length))
        parts.append(tube(f'spine_{k}', [(*r6(add(base, mul(d, -.5))), .78-.02*k*0), (*r6(add(base, mul(d, length*.5))), .5),
                                         (*r6(tip), .02)], 8, 3))


def line_points(a, b, f): return lerp(a, b, f)


def wing_chain(kind, s):
    return {1: [WRIST[s], FJ[1][s], FT[1][s]], 2: [WRIST[s], FJ[2][s], FT[2][s]], 3: [WRIST[s], FJ[3][s], FT[3][s]],
            'B': BODY_LINE[s]}[kind]


def on_chain(pts, f):
    """Point at arclength fraction f along a polyline."""
    lengths = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = math.fsum(lengths)
    d = clamp(f)*total
    for a, b, l in zip(pts, pts[1:], lengths):
        if d <= l+1e-12: return lerp(a, b, d/l if l else 0.)
        d -= l
    return pts[-1]


PANELS = ((1, 2), (2, 3), (3, 'B'))
SCALLOP = .3
WAVE = .35


def panel_rr(v): return 1-SCALLOP*math.sin(math.pi*v)


PANEL_ROOT = .08   # panels start slightly out from the wrist so the root edge is never a single point


def panel_f(u, v): return PANEL_ROOT+(1-PANEL_ROOT)*u*panel_rr(clamp(v))


def panel_point(pa, pb, u, v, s, k):
    f = panel_f(u, v)
    a = on_chain(pa, f)
    b = on_chain(pb, f)
    p = lerp(a, b, v)
    # Slight leathery ripple between the fingers, fading at the root and rim.
    wave = WAVE*math.sin(math.pi*v)*math.sin(math.pi*min(1, u*1.05))*(.6+.4*math.cos(u*9+k))
    return add(p, (0, s*wave*.35, wave))


def build_wings(parts):
    for side, s in SIDES:
        arm = [(*r6(add(S0[s], (.6, -s*.6, -1.4))), 1.65), (*ELB[s], 1.15), (*WRIST[s], .95)]
        parts.append(tube('wing_arm_'+side, arm, 12, 3))
        parts.append(xblob('wing_knob_'+side, WRIST[s], (1.15, 1.15, 1.15), 14, 10))
        for f in (1, 2, 3):
            chain = [(*WRIST[s], .68), (*FJ[f][s], .48), (*FT[f][s], .1)]
            parts.append(tube(f'finger_{f}_'+side, chain, 8, 3))
        for k, (a, b) in enumerate(PANELS):
            pa, pb = wing_chain(a, s), wing_chain(b, s)
            def surface(u, v, pa=pa, pb=pb, k=k, s=s):
                p = panel_point(pa, pb, u, v, s, k)
                n = unit(cross(sub(on_chain(pa, .5), WRIST[s]), sub(on_chain(pb, .5), on_chain(pa, .5))))
                out = unit((-.2, s*.55, .35))
                if dot(n, out) < 0: n = mul(n, -1)
                return p, n
            parts.append(shell(f'membrane_{k}_'+side, surface, 10, 10, .22))
        W = WRIST[s]
        th = [(*r6(add(W, (-.4, s*.4, -.1))), .7), (*r6(add(W, (2.6, s*1.2, 2.2))), .55), (*r6(add(W, (5.0, s*2.0, 2.0))), .3),
              (*r6(add(W, (6.6, s*2.4, .4))), .02)]
        parts.append(tube('claw_thumb_'+side, th, 8, 3))


# Layered tongues streaming forward and fanning outward: (layer, name suffix, azimuth deg, tilt deg, length, radius).
FLAME_TONGUES = ((0, '', 0, 0, 14.0, 2.3), (0, 'a', 45, 9, 9.5, 1.7), (0, 'b', 135, 9, 9.5, 1.7), (0, 'c', 225, 9, 9.5, 1.7),
                 (0, 'd', 315, 9, 9.5, 1.7),
                 (1, '', 90, 6, 12.5, 1.7), (1, 'a', 0, 16, 9.5, 1.6), (1, 'b', 72, 16, 9.0, 1.6), (1, 'c', 144, 16, 9.5, 1.6),
                 (1, 'd', 216, 16, 9.0, 1.6), (1, 'e', 288, 16, 9.5, 1.6),
                 (2, 'a', 30, 33, 7.5, 1.4), (2, 'b', 90, 33, 7.0, 1.4), (2, 'c', 150, 33, 7.5, 1.4), (2, 'd', 210, 33, 7.0, 1.4),
                 (2, 'e', 270, 33, 7.5, 1.4), (2, 'f', 330, 33, 7.0, 1.4),
                 (3, 'a', 0, 48, 5.5, 1.0), (3, 'b', 60, 48, 5.0, 1.0), (3, 'c', 120, 48, 5.5, 1.0), (3, 'd', 180, 48, 5.0, 1.0),
                 (3, 'e', 240, 48, 5.5, 1.0), (3, 'f', 300, 48, 5.0, 1.0))
# Ember sparks drifting ahead of the jet, on the last layer: (x ahead of the mouth, y, z).
FLAME_SPARKS = ((12.5, 2.6, 1.2), (13.6, -2.2, -1.6), (14.6, 1.0, -2.0), (11.6, -3.1, 2.3), (13.9, -.8, 2.6), (14.4, -1.7, .4))


def build_flames(parts):
    """Layered flame tongues plus sparks, jet axis +X, parked inside the chest; breathe slides them out of the mouth."""
    start = len(parts)
    for k, suffix, az, tilt, length, radius in FLAME_TONGUES:
        d = (math.cos(math.radians(tilt)), math.sin(math.radians(tilt))*math.cos(math.radians(az)),
             math.sin(math.radians(tilt))*math.sin(math.radians(az)))
        base = (FLAME_J[k], 0., 0.)
        tip = add(base, mul(d, length))
        parts.append(leaf(f'flame_{k}{suffix}', base, tip, (0, 1, 0), radius, radius, 14, 10, .12 if not suffix else .2))
    for i, (x, y, z) in enumerate(FLAME_SPARKS):
        parts.append(xblob(f'flame_3s{i}', (x, y, z), (.5, .32, .32), 10, 6))
    for p in parts[start:]:
        p.vertices = [(round(x+TUCK[0], 6), round(y+TUCK[1], 6), round(z+TUCK[2], 6)) for x, y, z in p.vertices]


def build_parts():
    parts = []
    build_body(parts)
    build_head(parts)
    build_wings(parts)
    build_flames(parts)
    return materials.repack(parts)


# ---------------------------------------------------------------- weights
def seg_weights(point, segs, k=.22):
    """segs: [(bone, a, b), ...] in chain order. Rigid segments that blend only near each joint."""
    best = None
    for m, (bone, a, b) in enumerate(segs):
        d = sub(b, a)
        t = clamp(dot(sub(point, a), d)/dot(d, d))
        dist = math.dist(point, add(a, mul(d, t)))
        if best is None or dist < best[0]-1e-9:
            best = (dist, m, t)
    _, m, t = best
    out = {IDS[segs[m][0]]: 1.}
    if m < len(segs)-1 and t > 1-k:
        w = .5*smooth((t-(1-k))/k)
        out = {IDS[segs[m][0]]: 1-w, IDS[segs[m+1][0]]: w}
    elif m > 0 and t < k:
        w = .5*smooth((k-t)/k)
        out = {IDS[segs[m-1][0]]: w, IDS[segs[m][0]]: 1-w}
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


def axis_segs():
    segs = [('pelvis', PELVIS, SPINE), ('spine', SPINE, CHEST), ('chest', CHEST, NECK0), ('neck_0', NECK0, NECK1),
            ('neck_1', NECK1, HEAD), ('head', HEAD, SNOUT)]
    return segs


def tail_segs():
    pts = TAIL+[TAIL_END]
    return [('pelvis', PELVIS, TAIL[0])]+[(f'tail_{k}', pts[k], pts[k+1]) for k in range(6)]


def leg_segs(side):
    s = 1 if side == 'L' else -1
    return {'arm': [('chest', CHEST, SHOULDER[s]), ('arm_'+side, SHOULDER[s], ELBOW[s]), ('fore_'+side, ELBOW[s], WRISTF[s]),
                    ('paw_'+side, WRISTF[s], TOEF[s])],
            'leg': [('pelvis', PELVIS, HIP[s]), ('thigh_'+side, HIP[s], KNEE[s]), ('shin_'+side, KNEE[s], HOCK[s]),
                    ('foot_'+side, HOCK[s], BALL[s]), ('toes_'+side, BALL[s], TOE[s])],
            'wing': [('wing_a_'+side, S0[s], ELB[s]), ('wing_b_'+side, ELB[s], WRIST[s])]}


def finger_segs(f, side):
    s = 1 if side == 'L' else -1
    return [(f'f{f}a_'+side, WRIST[s], FJ[f][s]), (f'f{f}b_'+side, FJ[f][s], FT[f][s])]


def nearest_bone(point, segs):
    def distance(sg):
        d = sub(sg[2], sg[1])
        return math.dist(point, add(sg[1], mul(d, clamp(dot(sub(point, sg[1]), d)/dot(d, d)))))
    return min(segs, key=distance)[0]


def chain_fraction_weights(names, cuts, f, k=.12):
    """Fraction f along a chain whose bone boundaries lie at cuts (ascending)."""
    out = {}
    for i, name in enumerate(names):
        lo = cuts[i-1] if i > 0 else -1
        hi = cuts[i] if i < len(cuts) else 2
        w = smooth((f-lo+k)/(2*k)) if i > 0 else 1.
        w *= 1-smooth((f-hi+k)/(2*k)) if i < len(cuts) else 1.
        out[IDS[name]] = w
    return [(i, w) for i, w in out.items() if w > 1e-9]


def finger_frac(f, side, sgn):
    s = 1 if side == 'L' else -1
    l1 = math.dist(WRIST[s], FJ[f][s])
    l2 = math.dist(FJ[f][s], FT[f][s])
    return l1/(l1+l2)


def membrane_weights(name, uv):
    k, side = int(name.split('_')[1]), name[-1]
    s = 1 if side == 'L' else -1
    u, v = materials.local_uv(name, uv)
    f = clamp(panel_f(u, v))
    a, b = PANELS[k]

    def chain(kind):
        if kind == 'B':
            return chain_fraction_weights(['chest', 'spine', 'pelvis'], [.4, .75], f, .18)
        cut = finger_frac(kind, side, s)
        return chain_fraction_weights([f'f{kind}a_'+side, f'f{kind}b_'+side], [cut], f, .1)
    acc = {}
    for i, w in chain(a):
        acc[i] = acc.get(i, 0)+(1-v)*w
    for i, w in chain(b):
        acc[i] = acc.get(i, 0)+v*w
    return [(i, w) for i, w in acc.items() if w > 1e-9]


TORSO = ('pelvis', 'spine', 'chest', 'neck_0')


def raw_weights(part, v, uv):
    n = part.name
    side = n[-1]
    if n.startswith(('skin_skull', 'skin_snout', 'skin_cheek', 'skin_nostril', 'skin_nridge', 'skin_brow', 'horn_', 'horn2_', 'horn3_', 'horn4_', 'horn5_',
                     'eye_', 'lid_', 'tooth_')):
        return [(IDS['head'], 1.)]
    if n in ('jaw', 'tongue') or n.startswith('ltooth_'):
        return [(IDS['jaw'], 1.)]
    if n.startswith('flame_'):
        return [(IDS['flame_'+n.split('_')[1][0]], 1.)]
    if n == 'skin_neck':
        return seg_weights(v, [('chest', CHEST, NECK0), ('neck_0', NECK0, NECK1), ('neck_1', NECK1, HEAD), ('head', HEAD, SNOUT)], .3)
    if n in ('skin_hip', 'skin_belly', 'skin_chest'):
        return RIG.chain_weights(v, [IDS[b] for b in TORSO])
    if n.startswith('skin_wshoulder'):
        return seg_weights(v, [('chest', CHEST, S0[1 if side == 'L' else -1]), *leg_segs(side)['wing']], .3)
    if n.startswith('claw_thumb'):
        return [(IDS['wing_b_'+side], 1.)]
    if n.startswith('skin_shoulder'):
        return seg_weights(v, leg_segs(side)['arm'][:3], .3)
    if n.startswith(('skin_arm', 'skin_paw', 'skin_toe_')):
        return seg_weights(v, leg_segs(side)['arm'], .22)
    if n.startswith(('claw_1', 'claw_2', 'claw_0')):
        return [(IDS['paw_'+side], 1.)]
    if n.startswith(('skin_haunch', 'skin_leg', 'skin_foot', 'skin_htoe')):
        if n.startswith('skin_haunch'):
            return seg_weights(v, leg_segs(side)['leg'][:3], .3)
        return seg_weights(v, leg_segs(side)['leg'], .22)
    if n.startswith('claw_h'):
        return [(IDS['toes_'+side], 1.)]
    if n == 'skin_tail':
        if v[0] > -10.5:
            return RIG.chain_weights(v, [IDS['spine'], IDS['pelvis']])
        return seg_weights(v, tail_segs(), .35)
    if n == 'tail_blade':
        return [(IDS['tail_5'], 1.)]
    if n.startswith('spine_'):
        k = int(n.split('_')[1])
        base = dorsal_points()[k][0]
        segs = axis_segs()+[s for s in tail_segs() if s[0].startswith('tail')]
        return [(IDS[nearest_bone(base, segs)], 1.)]
    if n.startswith('wing_arm'):
        return seg_weights(v, leg_segs(side)['wing'], .2)
    if n.startswith('wing_knob'):
        return [(IDS['wing_b_'+side], 1.)]
    if n.startswith('finger_'):
        return seg_weights(v, finger_segs(int(n.split('_')[1]), side), .2)
    if n.startswith('membrane_'):
        return membrane_weights(n, uv)
    raise ValueError('No weights for '+n)


def weights(part, v, uv):
    return quantise(raw_weights(part, v, uv))


# ---------------------------------------------------------------- posing
IDENT = (0., 0., 0., 1.)
WING_ORDER = ('wing_a', 'wing_b', 'f1a', 'f1b', 'f2a', 'f2b', 'f3a', 'f3b')
WING_CHILD = {'wing_a': ELB[1], 'wing_b': WRIST[1], 'f1a': FJ[1][1], 'f1b': FT[1][1], 'f2a': FJ[2][1], 'f2b': FT[2][1],
              'f3a': FJ[3][1], 'f3b': FT[3][1]}
WING_START = {'wing_a': S0[1], 'wing_b': ELB[1], 'f1a': WRIST[1], 'f1b': FJ[1][1], 'f2a': WRIST[1], 'f2b': FJ[2][1],
              'f3a': WRIST[1], 'f3b': FJ[3][1]}
WING_FOLD = {n: unit(sub(WING_CHILD[n], WING_START[n])) for n in WING_ORDER}
WING_MANTLE = {'wing_a': (-.12, .5, .86), 'wing_b': (-.5, .7, .5), 'f1a': (-.45, .62, .64), 'f1b': (-.55, .6, .58),
               'f2a': (-.6, .45, .66), 'f2b': (-.65, .4, .64), 'f3a': (-.66, .28, .69), 'f3b': (-.7, .22, .68)}
WING_RAISED = {'wing_a': (-.12, .38, .92), 'wing_b': (-.3, .55, .78), 'f1a': (-.4, .78, .48), 'f1b': (-.5, .74, .44),
               'f2a': (-.62, .6, .5), 'f2b': (-.66, .5, .56), 'f3a': (-.78, .4, .48), 'f3b': (-.8, .3, .52)}
WING_DROOP = {'wing_a': (-.1, .78, -.6), 'wing_b': (-.42, .88, -.22), 'f1a': (-.86, .5, -.12), 'f1b': (-.93, .34, -.08),
              'f2a': (-.92, .34, -.14), 'f2b': (-.96, .22, -.1), 'f3a': (-.97, .16, -.16), 'f3b': (-.98, .08, -.14)}


def roty(v, deg):
    return rotate(axis((0, 1, 0), math.radians(deg)), v)


def mirror(d, s):
    return (d[0], s*d[1], d[2])


def wings(P, target=None, amount=0., other=None, mix2=0., blend=1.):
    """Aim both wings: fold blended toward target by amount, then toward other by mix2 (chest-local, left-side coordinates)."""
    if target is None: target = WING_FOLD
    for side, s in SIDES:
        q = P.world()[IDS['chest']][1]
        for name in WING_ORDER:
            d = lerp(WING_FOLD[name], target[name], amount)
            if other is not None: d = lerp(d, other[name], mix2)
            P.aim(f'{name}_{side}', WING_CHILD[name] if s == 1 else mirror(WING_CHILD[name], -1), rotate(P.world()[IDS['chest']][1], mirror(unit(d), s)), blend)


CLAW_F = {s: (17.2, s*9.6, .5) for _, s in SIDES}     # tip of the middle fore claw at rest
CLAW_H = {s: (-3.1, s*10.5, .5) for _, s in SIDES}    # tip of the middle hind claw at rest
CLAW_FLOOR = .3
PALM_F = {s: ((12.0, s*9.6, .3), (10.8, s*9.6, .8)) for _, s in SIDES}     # underside of the fore paw at rest
PALM_H = {s: ((-9.5, s*10.5, .2), (-7.4, s*10.5, .3)) for _, s in SIDES}      # underside of the hind foot at rest
SOLE = .1


def level_roll(P, bone, child_rest):
    """Roll a limb bone about its own axis so its rest lateral axis (Y) is horizontal: the paw sits flat and no toe dips."""
    i = IDS[bone]
    world = P.world()
    loc, q = world[i]
    a = unit(rotate(q, sub(child_rest, P.rig.rest[i])))
    lat = rotate(q, (0, 1, 0))
    lat = sub(lat, mul(a, dot(lat, a)))
    n = math.sqrt(dot(lat, lat))
    if n < 1e-6: return
    lat = mul(lat, 1/n)
    target = unit(cross(a, (0, 0, 1)))
    if dot(target, lat) < 0: target = mul(target, -1)
    ang = math.atan2(dot(cross(lat, target), a), dot(lat, target))
    pq = world[P.rig.bones[i][1]][1]
    P.rot[i] = qmul(inverse(pq), qmul(axis(a, ang), qmul(pq, P.rot[i])))


def plant_hind(P, side, ball, pitch=0., toe_pitch=0., blend=1.):
    s = 1 if side == 'L' else -1
    hock = add(ball, roty(sub(HOCK[s], BALL[s]), pitch))
    P.reach('thigh_'+side, 'shin_'+side, HOCK[s], hock, (1, s*.12, 0), blend)
    P.aim('foot_'+side, BALL[s], sub(ball, P.point('foot_'+side, HOCK[s])), blend)
    if blend >= 1: level_roll(P, 'foot_'+side, BALL[s])
    for _ in range(12):
        P.aim('toes_'+side, TOE[s], roty(sub(TOE[s], BALL[s]), toe_pitch), blend)
        if blend >= 1: level_roll(P, 'toes_'+side, TOE[s])
        if blend < 1 or ball[2] > 4: break
        dip = min(min(P.point('foot_'+side, q)[2] for q in PALM_H[s]), P.point('toes_'+side, CLAW_H[s])[2])
        if dip >= SOLE: break
        ball = (ball[0], ball[1], ball[2]+SOLE-dip)
        hock = add(ball, roty(sub(HOCK[s], BALL[s]), pitch))
        P.reach('thigh_'+side, 'shin_'+side, HOCK[s], hock, (1, s*.12, 0), blend)
        P.aim('foot_'+side, BALL[s], sub(ball, P.point('foot_'+side, HOCK[s])), blend)
        level_roll(P, 'foot_'+side, BALL[s])


def plant_front(P, side, tip, pitch=0., pole=None, blend=1.):
    s = 1 if side == 'L' else -1
    for _ in range(14):
        wrist = sub(tip, roty(sub(TOEF[s], WRISTF[s]), pitch))
        P.reach('arm_'+side, 'fore_'+side, WRISTF[s], wrist, pole or (-1, s*.4, .15), blend)
        P.aim('paw_'+side, TOEF[s], sub(tip, P.point('fore_'+side, WRISTF[s])), blend)
        if blend >= 1: level_roll(P, 'paw_'+side, TOEF[s])
        if blend < 1 or tip[2] > 4: break
        dip = min(P.point('paw_'+side, q)[2] for q in PALM_F[s]+(CLAW_F[s],))
        if dip >= SOLE: break
        tip = (tip[0], tip[1], tip[2]+SOLE-dip)


def feet(P, spread=1., front=(0., 0.), hind=(0., 0.), lift=None, blend=1., fpitch=0.):
    """Plant all four paws at their rest spots (optionally spread); lift = {(side, 'f'|'h'): (dx, dy, dz)} offsets."""
    lift = lift or {}
    for side, s in SIDES:
        t = TOEF[s]
        off = lift.get((side, 'f'), (0., 0., 0.))
        plant_front(P, side, (t[0]+front[0]+off[0], s*abs(t[1])*spread+off[1], t[2]+off[2]), fpitch, None, blend)
        b = BALL[s]
        off = lift.get((side, 'h'), (0., 0., 0.))
        plant_hind(P, side, (b[0]+hind[0]+off[0], s*abs(b[1])*spread+off[1], b[2]+off[2]), 0., 0., blend)


def tail_wave(P, sway, curl=0., phase=0., lag=.7, lift=0.):
    for k in range(6):
        P.turn(f'tail_{k}', (0, 0, 1), sway*(.6+.16*k)*math.sin(phase-k*lag)-curl*(1.0 if k < 4 else .6))
        P.turn(f'tail_{k}', (0, 1, 0), lift*(.5 if k < 3 else 1.)+.35*sway*math.sin(phase-k*lag+1.3))


TAIL_R = (4.0, 3.2, 2.6, 2.0, 1.45, 1.0, .6)


def tail_guard(P, floor=.35):
    """Tilt tail segments up (a deterministic sweep from the root) until every tail joint clears the floor by its radius."""
    for k in range(6):
        child = TAIL[k+1] if k < 5 else TAIL_END
        for _ in range(60):
            a = P.point(f'tail_{k}', TAIL[k])
            b = P.point(f'tail_{k}', child)
            if b[2] >= TAIL_R[k+1]+floor: break
            d = unit(sub(b, a))
            P.aim(f'tail_{k}', child, unit((d[0], d[1], d[2]+.05)))
    blade = add(TAIL_END, mul(unit(sub(TAIL_END, TAIL[5])), 5.))
    for _ in range(60):
        if P.point('tail_5', blade)[2] >= 1.3: break
        a = P.point('tail_5', TAIL[5]); d = unit(sub(P.point('tail_5', TAIL_END), a))
        P.aim('tail_5', TAIL_END, unit((d[0], d[1], d[2]+.05)))


def mouth(P, degrees):
    P.turn('jaw', (0, 1, 0), degrees)


def flames(P, amount, t=0., stagger=(0., .1, .2, .3)):
    """Bring the parked flame layers to the open jaws: each layer slides out along the head axis (longer tongues start
    deeper inside the head so the jet grows out of the mouth), oriented with the head. amount 0 leaves them in the chest."""
    if amount <= 0: return
    world = P.world()
    cl, cq = world[IDS['chest']]
    hl, hq = world[IDS['head']]
    mouth = add(hl, rotate(hq, sub(MOUTH, REST[IDS['head']])))
    rel = qmul(inverse(cq), hq)
    for k in range(4):
        a = smooth((amount-stagger[k])/(1-stagger[k]))
        if a <= 0: continue
        i = IDS[f'flame_{k}']
        off = FLAME_J[k]*a-FLAME_LEN[k]*(1-a)
        flick = a*(.3+.1*k)
        target = add(mouth, rotate(hq, (off, flick*math.sin(TAU*6*t+2.1*k), flick*math.cos(TAU*5*t+k))))
        P.shift[i] = sub(rotate(inverse(cq), sub(target, cl)), BONES[i][2])
        P.rot[i] = rel


IDLE_NECK = (-3., -3., 12.)     # the neck holds the head high; the head looks forward and slightly down
MANTLE_K = 1.0
BREATH_SHIFT = -10.
BREATH_NECK = (-30., 110., -70.)


def idle_body(P, ph, wing_amount=0.):
    """Breathing, cocked scanning head and swaying tail; feet are planted afterwards by the caller."""
    P.shift[0] = (0., 0., .3*math.sin(ph))
    P.turn('spine', (0, 1, 0), 1.3*math.sin(ph))
    P.turn('chest', (0, 1, 0), 1.6*math.sin(ph+.3))
    P.turn('neck_0', (0, 1, 0), IDLE_NECK[0]+2*math.sin(ph+.6))
    P.turn('neck_1', (0, 1, 0), IDLE_NECK[1]+2*math.sin(ph+.9))
    P.turn('head', (0, 1, 0), IDLE_NECK[2]+2*math.sin(ph+1.2))
    P.turn('neck_0', (0, 0, 1), 4*math.sin(ph))
    P.turn('neck_1', (0, 0, 1), 6*math.sin(ph))
    P.turn('head', (0, 0, 1), 12*math.sin(ph))
    P.turn('head', (1, 0, 0), 4*math.sin(ph+2.1))
    mouth(P, 3+2.5*math.sin(2*ph))
    tail_wave(P, 8, 0., 2*ph, .7)
    P.turn('tail_5', (0, 1, 0), -10*max(0., math.sin(3*ph))**4)


def idle_pose(t):
    P = Pose()
    ph = TAU*t
    idle_body(P, ph)
    twitch = .07+.05*math.sin(ph+.5)+.35*max(0., math.sin(3*ph+1))**6
    wings(P, WING_RAISED, twitch)
    feet(P)
    tail_guard(P)
    return P


STRIDE = 3.4
DUTY = .75
GAIT = {('L', 'f'): 0., ('R', 'h'): .25, ('R', 'f'): .5, ('L', 'h'): .75}


def gait_targets(t):
    """Foot offsets (dx, dy, dz) for a lateral-sequence walk: three paws always planted, one swings."""
    out = {}
    for key, off in GAIT.items():
        f = (t+off) % 1
        if f < DUTY:
            u = f/DUTY
            out[key] = (STRIDE*(1-2*u), 0., 0.)
        else:
            u = (f-DUTY)/(1-DUTY)
            out[key] = (-STRIDE+2*STRIDE*smooth(u), 0., 4.2*math.sin(math.pi*u))
    return out


def stalk_pose(t):
    P = Pose()
    ph = TAU*t
    idle_body(P, 0.)
    P.shift[0] = (0., .6*math.sin(ph), .5*abs(math.sin(ph))-.2)
    P.turn('pelvis', (0, 0, 1), 6*math.sin(ph))
    P.turn('spine', (0, 0, 1), -4*math.sin(ph))
    P.turn('chest', (0, 0, 1), -8*math.sin(ph))
    P.turn('pelvis', (1, 0, 0), 3*math.sin(2*ph))
    P.turn('neck_0', (0, 1, 0), 6)
    P.turn('neck_1', (0, 1, 0), 4)
    P.turn('head', (0, 1, 0), -8+3*math.sin(2*ph))
    P.turn('head', (0, 0, 1), 14*math.sin(ph+1.2)-4*math.sin(ph))
    mouth(P, 4+2*math.sin(4*ph))
    tail_wave(P, 12, 0., ph, .8)
    wings(P, WING_RAISED, .04+.03*math.sin(2*ph))
    feet(P, 1., (0., 0.), (0., 0.), gait_targets(t))
    tail_guard(P)
    return P


def breathe_pose(t):
    """Fire breath: the dragon hunkers back and low, wings mantled wide, then the neck thrusts the open jaws
    forward and the flame pieces slide out. Key pose at the middle frame. The breath itself is Brogue's bolt."""
    P = Pose()
    idle_body(P, 0.)
    coil = window(t, .0, .32)*(1-window(t, .7, 1.))
    rear = window(t, .0, .26)*(1-window(t, .32, .46))
    fire = window(t, .3, .46)*(1-window(t, .6, .74))
    jet = window(t, .33, .45)*(1-window(t, .62, .72))
    P.shift[0] = add(P.shift[0], (BREATH_SHIFT*coil, 0., -3.4*coil))
    P.turn('pelvis', (0, 1, 0), -4*coil)
    P.turn('spine', (0, 1, 0), 3*coil)
    P.turn('chest', (0, 1, 0), 3*coil)
    P.turn('neck_0', (0, 1, 0), -12*rear+BREATH_NECK[0]*fire)
    P.turn('neck_1', (0, 1, 0), -10*rear+BREATH_NECK[1]*fire)
    P.turn('head', (0, 1, 0), 14*rear+BREATH_NECK[2]*fire)
    P.turn('head', (0, 0, 1), -8*fire)
    mouth(P, 9*rear+34*fire)
    flames(P, jet, t)
    tail_wave(P, 6*(1-coil), 72*coil, TAU*t, .7, lift=6*coil)
    wings(P, WING_RAISED, .07)
    wings(P, WING_RAISED, .07, WING_MANTLE, MANTLE_K*coil)
    feet(P, 1.+.18*coil, (.5*coil, 0.), (-3.2*coil, 0.), None, 1., -16*coil)
    tail_guard(P)
    return P


def lash_pose(t):
    """Tail-whip, claw and bite (Brogue: the dragon hits everything adjacent): the body coils to the right, then
    yaws hard left with the head snapping sideways, one forepaw raking high and the tail sweeping wide."""
    P = Pose()
    idle_body(P, 0.)
    wind = window(t, .04, .34)*(1-window(t, .38, .5))
    strike = window(t, .34, .48)*(1-window(t, .62, .86))
    coil = max(wind, strike)
    P.shift[0] = add(P.shift[0], (-3.0*coil, 1.0*wind-2.4*strike, -2.6*coil))
    P.turn('pelvis', (0, 0, 1), 8*wind+14*strike)
    P.turn('spine', (0, 0, 1), 6*wind-20*strike)
    P.turn('chest', (0, 0, 1), 14*wind-34*strike)
    P.turn('spine', (0, 1, 0), 5*coil)
    P.turn('chest', (0, 1, 0), 6*coil)
    P.turn('neck_0', (0, 0, 1), 8*wind-16*strike)
    P.turn('neck_1', (0, 0, 1), 6*wind-16*strike)
    P.turn('neck_0', (0, 1, 0), -8*wind+10*strike)
    P.turn('neck_1', (0, 1, 0), -6*wind+8*strike)
    P.turn('head', (0, 1, 0), 8*wind-14*strike)
    P.turn('head', (0, 0, 1), 8*wind-14*strike)
    mouth(P, 6*wind+34*strike)
    tail_wave(P, 3*(1-coil), 40*wind, 2*TAU*t, .7)
    P.turn('tail_0', (0, 0, 1), -34*strike)
    for k, extra in enumerate((0, 14, 14, 16, 16, 16)):
        P.turn(f'tail_{k}', (0, 0, 1), extra*strike)
    wings(P, WING_RAISED, .07)
    wings(P, WING_RAISED, .07, WING_MANTLE, .3*wind+.05*strike)
    lift = {('R', 'f'): (6.5*strike, -8.5*strike, 12.5*strike), ('L', 'f'): (0., 1.5*strike, 0.)}
    feet(P, 1.+.14*coil, (0., 0.), (-1.6*coil, 0.), lift, 1., -16*coil)
    tail_guard(P)
    return P


def recoil_pose(t):
    P = Pose()
    idle_body(P, 0.)
    p = math.sin(math.pi*t)**1.3
    shake = math.sin(TAU*2.5*t)*math.sin(math.pi*t)
    P.shift[0] = add(P.shift[0], (-1.5*p, .5*shake, .8*p))
    P.turn('pelvis', (0, 1, 0), -7*p)
    P.turn('chest', (0, 1, 0), -12*p)
    P.turn('neck_0', (0, 1, 0), -22*p)
    P.turn('neck_1', (0, 1, 0), -16*p)
    P.turn('head', (0, 1, 0), 10*p)
    P.turn('head', (0, 0, 1), 18*shake)
    mouth(P, 30*p)
    tail_wave(P, 4, 0., TAU*2*t, .7, lift=16*p)
    wings(P, WING_RAISED, .07)
    wings(P, WING_RAISED, .07, WING_MANTLE, .95*p)
    feet(P, 1.+.05*p, (0., 0.), (0., 0.))
    tail_guard(P)
    return P


_FINAL = []
NECK_DEATH = ((.1, .3, -.42), (-.4, .4, .1), (-.4, .65, .2))


def death_final():
    """The settled corpse, built once: belly on the floor, legs splayed, neck laid forward, jaw slack, wings draped."""
    if _FINAL: return _FINAL[0]
    P = Pose()
    P.shift[0] = (1.0, 0., -6.9)
    P.turn('spine', (0, 1, 0), 4)
    P.turn('chest', (0, 1, 0), 6)
    P.aim('neck_0', NECK1, NECK_DEATH[0])
    P.aim('neck_1', HEAD, NECK_DEATH[1])
    P.aim('head', SNOUT, NECK_DEATH[2])
    level_roll(P, 'head', SNOUT)
    P.turn('head', (1, 0, 0), 12)
    mouth(P, 12)
    tail_wave(P, 0, 26., 0., .7)
    wings(P, WING_DROOP, 1.)
    for side, s in SIDES:
        plant_front(P, side, (12.0, s*(20. if s > 0 else 17.), 3.0), 0., (-.2, s*.5, 1.))
        plant_hind(P, side, (-13.5, s*(17. if s > 0 else 20.), 2.6), 0., 0.)
    tail_guard(P)
    _FINAL.append((P.rot[:], P.shift[0]))
    return _FINAL[0]


def death_pose(t):
    """Reel and roar, then collapse onto the belly and lie limp; the last quarter is the static corpse."""
    P = Pose()
    jolt = window(t, 0, .1)*(1-window(t, .12, .26))
    u = clamp((t-.12)/.56)
    limp = smooth(u)
    idle_body(P, 0.)
    P.turn('spine', (0, 1, 0), -10*jolt)
    P.turn('chest', (0, 1, 0), -12*jolt)
    P.turn('neck_0', (0, 1, 0), -14*jolt)
    P.turn('head', (0, 1, 0), 16*jolt)
    mouth(P, 36*jolt)
    P.shift[0] = add(P.shift[0], (-.5*jolt, 0., 1.2*jolt))
    wings(P, WING_RAISED, .07)
    wings(P, WING_RAISED, .07, WING_MANTLE, .5*jolt)
    tail_wave(P, 4*(1-limp), 10*jolt, 0., .7, lift=10*jolt)
    hold = 1-window(t, .16, .42)
    feet(P, 1., (0., 0.), (0., 0.), None, hold)
    rot, shift = death_final()
    for i in range(1, len(BONES)):
        late = BONES[i][0] in ('neck_0', 'neck_1', 'head', 'jaw')
        P.rot[i] = slerp(P.rot[i], rot[i], limp**3.2 if late else limp)
    P.rot[0] = IDENT
    bounce = .9*math.sin(math.pi*clamp((t-.62)/.14))*(1-smooth((t-.62)/.3))
    P.shift[0] = add(lerp(P.shift[0], shift, limp**1.4), (-6.4*math.sin(math.pi*limp), -3.6*math.sin(math.pi*limp), bounce))
    for k in range(3):
        P.shift[IDS[f'flame_{k}']] = (0., 0., 0.)
    return P


def pose(name, t):
    return {'idle': idle_pose, 'stalk': stalk_pose, 'breathe': breathe_pose, 'lash': lash_pose, 'recoil': recoil_pose,
            'death': death_pose}[name](t).frame()


# ---------------------------------------------------------------- export
def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def geometry():
    from .connected_skin import attach
    parts = attach('dragon', build_parts(), weights)
    return assemble(materials.connected_atlas(parts), weights)


def texture_bytes():
    from .connected_skin import attach
    return materials.connected_atlas(attach('dragon', build_parts(), weights), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_dragon', material_path=SKIN)
    path = ROOT/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M50', format='IQM v2', runtimeModel=MODEL,
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/dragon/dragon-animated.blend')
    out = ROOT/'assets/monsters/dragon'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Re-import under the package name so connected_skin finds CONNECTED_SKIN.
    import importlib
    print(importlib.import_module('tools.monster_models.dragon_animation').build()['sha256'])
