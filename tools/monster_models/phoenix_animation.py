"""Original rigid-and-flowing phoenix, six purely cosmetic skeletal roles. No gameplay.

Brogue (Globals.c): "This legendary bird shines with a brilliant light, and its
wings crackle and pop like embers as they beat the air. When it dies, legend has
it that an egg will form and a newborn phoenix will rise from its ashes." The
glyph is `phoenixColor` (red with a large random green component, so a dancing
red-orange-yellow flame colour), it flies, is immune to fire and carries
PHOENIX_LIGHT; attack verbs are pecks, scratches and claws; it dies as
DF_ASH_BLOOD. Everything about flight, fire immunity, the egg, damage, turns
and RNG stays with Brogue CE. This file only draws.

Art (original interpretation): a majestic hawk-bodied fire bird with a hooked
gold beak and forward-facing eyes on +X, a burning crest, scaled talons, broad
raised wings whose solid crimson-to-gold flight feathers end in fullbright flame
tongues, and a long flowing tail of flame plumes. Flame parts are fullbright
(atlas column u >= 0.75, phoenix-fire.fp); body plumage is lit with a wide warm
value range so it still reads under flat engine light. The phoenix egg
(`phoenix_egg_animation.py`) is a separate creature and is not modelled here;
the death clip ends on the floor in a heap of embers and ash (hidden ash and
ember chunks that scatter out of the torso) around the fallen, splayed bird.

Rig: rigid pieces and smoothly weighted flame ribbons (no connected skin, so no
cage bake). +X forward, Z up, +Y left. Unit bone scales throughout.
"""
import hashlib
import json
import math

from . import iqm, phoenix_materials as materials
from .rat import ROOT, add, sub, mul, unit, cross
from .skeletal import Rig, axis, qmul, inverse, rotate, assemble, sample_clips
from .pixie_animation import blob, tube, shell, ortho, lerp, clamp, r6
from .relic_kit import slerp

SKIN = 'graphics/BRGPHNX.png'
MODEL = 'mod/BrogueDoom/models/monsters/65_phoenix.iqm'
SHADER = 'shaders/phoenix-fire.fp'
ATLAS = materials.ATLAS
TAU = math.tau
SIDES = (('L', 1), ('R', -1))
FLOOR = .1

# ---------------------------------------------------------------- skeleton
PELVIS, CHEST, NECK, HEAD = (-4.0, 0, 27.0), (3.5, 0, 34.0), (7.0, 0, 39.0), (10.0, 0, 43.5)
JAW = (12.4, 0, 43.2)
CREST1, CREST2 = (8.0, 0, 47.5), (4.5, 0, 53.0)
TAIL1, TAIL2, TAIL3 = (-6.5, 0, 25.0), (-13.5, 0, 16.5), (-19.5, 0, 9.5)
SHOULDER = {s: (1.5, s*3.5, 36.5) for _, s in SIDES}
# Full-span wing: the arm rises out and back from the shoulder; the flight
# feathers fan from wrist and hand so the tips reach about +-30 in Y.
ELBOW = {s: (-1.0, s*8.5, 40.0) for _, s in SIDES}
WRIST = {s: (-2.0, s*12.8, 43.8) for _, s in SIDES}
HAND = {s: (-1.5, s*15.0, 46.5) for _, s in SIDES}
HIP = {s: (-0.5, s*3.4, 27.5) for _, s in SIDES}
ANKLE = {s: (2.0, s*3.6, 19.3) for _, s in SIDES}

# The wing fan lies in a plane that faces forward (normal N) and leans back,
# so the gameplay camera sees the wing face on rather than its leading edge.
N_WING = unit((0.72, 0, 0.69))
E_UP = unit((-0.69, 0, 0.72))
TONGUE_THETA = {'a': 30., 'b': 56., 'c': 82.}
TORSO_C = (-0.3, 0, 30.6)
TORSO_A0 = unit((0.79, 0, 0.61))
TORSO_R = (11.5, 5.5, 5.2)
TORSO_A1 = ortho((0, 0, 1), TORSO_A0)
TORSO_A2 = cross(TORSO_A0, TORSO_A1)


def fan(s, theta):
    """Direction in the wing-fan plane: theta 0 = straight out, 90 = up."""
    a = math.radians(theta)
    return unit(add(mul((0, s, 0), math.cos(a)), mul(E_UP, math.sin(a))))


def torso_point(xi, psi, scale=1.0):
    q = math.sqrt(max(0., 1-xi*xi))
    p = add(TORSO_C, add(mul(TORSO_A0, TORSO_R[0]*xi*scale),
                         add(mul(TORSO_A1, TORSO_R[1]*q*math.cos(psi)*scale), mul(TORSO_A2, TORSO_R[2]*q*math.sin(psi)*scale))))
    out = unit(add(mul(TORSO_A0, xi/TORSO_R[0]), add(mul(TORSO_A1, q*math.cos(psi)/TORSO_R[1]), mul(TORSO_A2, q*math.sin(psi)/TORSO_R[2]))))
    return p, out


def tongue_bone_point(s, g):
    return r6(add(HAND[s], mul(fan(s, TONGUE_THETA[g]), 5.2)))


LUMP_BONES = 10
RING = 8
# Spreaders: a tiny disc or dome hidden in the torso at rest whose vertices are
# blended between a centre bone and eight ring bones. Only bone translations
# change, so the death spreads it into a big ash pool and two ember mounds.
# name, rest axis along the torso, rest radius and half-height, target offset
# and radii on the floor, ring z, apex z, centre-weight exponent.
SPREADS = (('pool', -1.0, 2.4, .5, (-1.0, 0.0), (15.5, 11.5), .8, .8, 1.0),
           ('mound_a', -4.0, 2.2, 1.3, (-19.0, 6.0), (7.0, 6.2), .9, 7.6, 1.5),
           ('mound_b', 3.0, 2.0, 1.2, (16.0, -9.0), (5.0, 4.5), .9, 5.2, 1.5))
ASH_COUNT = LUMP_BONES+len(SPREADS)*(RING+1)
_ASH_AXIS = [-7.5, -4.5, -1.5, 1.5, 4.5, 7.5, -3.0, 0.0, 3.0, 6.0]+[sp[1] for sp in SPREADS for _ in range(RING+1)]
_ASH_SIDE = [0, 0, 0, 0, 0, 0, 1.7, -1.7, 1.7, -1.7]+[0]*(len(SPREADS)*(RING+1))
ASH_CENTERS = [r6(add(add(TORSO_C, mul(TORSO_A0, _ASH_AXIS[k])), mul(TORSO_A2, _ASH_SIDE[k]))) for k in range(ASH_COUNT)]

SPECS = [('root', None, (0, 0, 0)), ('body', 'root', PELVIS), ('chest', 'body', CHEST), ('neck', 'chest', NECK),
         ('head', 'neck', HEAD), ('jaw', 'head', JAW), ('crest1', 'head', CREST1), ('crest2', 'crest1', CREST2),
         ('tail1', 'body', TAIL1), ('tail2', 'tail1', TAIL2), ('tail3', 'tail2', TAIL3)]
for side, s in SIDES:
    SPECS += [('wing1_'+side, 'chest', SHOULDER[s]), ('wing2_'+side, 'wing1_'+side, ELBOW[s]),
              ('wing3_'+side, 'wing2_'+side, WRIST[s]), ('wing4_'+side, 'wing3_'+side, HAND[s])]
    SPECS += [('tongue_%s_%s' % (g, side), 'wing4_'+side, tongue_bone_point(s, g)) for g in 'abc']
    SPECS += [('leg_'+side, 'body', HIP[s]), ('foot_'+side, 'leg_'+side, ANKLE[s])]
SPECS += [('ash_%d' % k, 'body', ASH_CENTERS[k]) for k in range(ASH_COUNT)]
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, _, _) in enumerate(BONES)}
CLIPS = [('idle', 36, 24, True), ('fly', 24, 30, True), ('claw', 18, 30, False),
         ('peck', 20, 30, False), ('recoil', 12, 30, False), ('death', 30, 30, False)]
DURATIONS = [0, 0]+[math.ceil(c[1]*35/c[2]) for c in CLIPS[2:]]


# ---------------------------------------------------------------- weights
def quant(w):
    """Quantise a {bone: weight} map to 1e-6 with the last weight the exact remainder."""
    items = sorted((b, x) for b, x in w.items() if x > 1e-9)
    total = math.fsum(x for _, x in items)
    items = [(b, x/total) for b, x in items]
    out = [(b, round(x, 6)) for b, x in items[:-1]]
    out.append((items[-1][0], round(1-math.fsum(x for _, x in out), 6)))
    return [(b, x) for b, x in out if x > 0] or [(items[-1][0], 1.0)]


def chain(point, names):
    ids = [IDS[n] for n in names]
    return {b: w for b, w in RIG.chain_weights(point, ids)}


def blend(a, b, m):
    out = {}
    for k, v in a.items():
        out[k] = out.get(k, 0)+v*(1-m)
    for k, v in b.items():
        out[k] = out.get(k, 0)+v*m
    return out


def put(parts, part, role, weights):
    """Assign atlas role and skin weights. `weights` is a bone name, or a
    function (vertex, raw_uv) -> {bone: weight}."""
    raw = list(part.uv)
    if isinstance(weights, str):
        rows = [[(IDS[weights], 1.0)]]*len(part.vertices)
    else:
        rows = [quant(weights(v, u)) for v, u in zip(part.vertices, raw)]
    ATLAS.map(part, role)
    part.skin_weights = rows
    parts.append(part)
    return part


# ---------------------------------------------------------------- primitives
def ribbon(name, root, d, nrm, L, W, prof, amp=0., curl=0., phase=0., ripple=0., nu=12, nv=4, thick=.12):
    """Thin closed double-sided ribbon along d (a curved flame tongue or feather);
    U runs root->tip, V across."""
    d = unit(d); nrm = ortho(nrm, d); side = unit(cross(nrm, d))

    def surface(u, v):
        a = (v-.5)*2
        w = W*.5*prof(u)*(1+ripple*math.sin(TAU*(1.4*u+a*.15)+phase)*u)
        c = add(root, mul(d, L*u))
        c = add(c, mul(side, amp*math.sin(TAU*.7*u+phase)*u))
        c = add(c, mul(nrm, curl*u*u))
        return add(c, mul(side, a*w)), nrm
    return shell(name, surface, nu, nv, thick)


def flame_prof(r0=.35):
    def f(u):
        x = (u-.32)/(.68 if u > .32 else .32)
        return max(.05, (1-x*x)**.75, r0*(1-u)**2)
    return f


def feather_prof(tip=.55):
    def f(u):
        return max(.06, clamp(u/.12)**.5*(1-clamp((u-tip)/(1-tip)))**.62)
    return f


def lump(name, center, radii, seed, sides=14, rings=8, bump=.02):
    """Smooth, low, soft ash mound (a flattened ellipsoid with a barely perceptible undulation)."""
    p = blob(name, center, (0, 0, 1), (1, 0, 0), (radii[2], radii[0], radii[1]), sides, rings)
    p.vertices = [r6(add(center, mul(sub(v, center), 1+bump*math.sin(seed*3.1+i*1.7)+bump*.6*math.cos(seed*1.3+i*2.9))))
                  for i, v in enumerate(p.vertices)]
    return p


# ---------------------------------------------------------------- anatomy
HEAD_C = (10.2, 0, 44.2)
HEAD_R = (4.3, 3.2, 3.1)   # along X, along Z, along Y


def build_head(parts):
    put(parts, blob('head', HEAD_C, (1, 0, 0), (0, 0, 1), HEAD_R, 26, 16), 'body', 'head')
    put(parts, blob('cheek_ruff', (8.4, 0, 42.0), (0, 0, 1), (1, 0, 0), (2.6, 3.1, 3.3), 20, 12), 'body', 'head')
    # Heavy hooked hawk beak: deep at the cere, long hook curving well below the
    # lower jaw; the short lower mandible sits on its own bone.
    put(parts, tube('beak_upper', [(12.4, 0, 44.9, 1.7), (14.2, 0, 45.0, 1.3), (16.2, 0, 44.2, .82),
                                   (17.9, 0, 42.4, .48), (18.2, 0, 39.6, .07)], 12, 4), 'beak', 'head')
    put(parts, tube('beak_lower', [(12.5, 0, 42.6, 1.0), (14.4, 0, 42.3, .8), (16.0, 0, 42.1, .5),
                                   (16.9, 0, 42.0, .12)], 10, 3), 'beak', 'jaw')
    put(parts, tube('cere_ridge', [(12.5, 0, 46.55, .6), (14.1, 0, 46.5, .5), (15.5, 0, 45.6, .18)], 8, 3), 'beak', 'head')
    for side, s in SIDES:
        n = unit((.78, s*.62, .05))
        lat = unit((-n[1]*s, n[0]*s, 0.))          # outward along the face
        slant = unit(add(mul(lat, math.cos(math.radians(24))), (0, 0, math.sin(math.radians(24)))))
        c = (12.6, s*2.35, 45.0)
        # Angry brow: outer end high, inner end low, over a sunk dark socket
        # holding a narrow, slanted, glowing slit.
        put(parts, blob('socket_'+side, r6(sub(c, mul(n, .35))), n, slant, (.5, 2.3, 1.35), 18, 12), 'talon', 'head')
        put(parts, blob('eye_'+side, r6(add(c, mul(n, .1))), n, slant, (.42, 2.0, .62), 18, 12), 'eye', 'head')
        # Flat, angular brow wedge sloping down toward the beak (V-scowl), set behind
        # the eye plane so the slit stays visible from the front.
        outer, inner = (11.3, s*4.1, 47.0), (11.6, s*.5, 46.0)
        put(parts, ribbon('brow_'+side, r6(outer), unit(sub(inner, outer)), (.45, 0, .89), 3.9, 2.3,
                          lambda u: max(.3, 1-.65*u), nu=6, nv=3, thick=.5), 'brow', 'head')
        # Nostril bump on the cere.
        put(parts, blob('cere_'+side, (13.5, s*.95, 44.7), (1, 0, 0), (0, 0, 1), (.8, .6, .55), 10, 6), 'beak', 'head')


def build_neck_and_torso(parts):
    put(parts, blob('torso', TORSO_C, TORSO_A0, TORSO_A1, TORSO_R, 30, 20), 'body', 'body')
    put(parts, blob('breast', (4.6, 0, 34.4), TORSO_A0, TORSO_A1, (5.0, 5.7, 5.5), 26, 16), 'body', 'chest')
    put(parts, tube('neck', [(4.6, 0, 36.0, 3.6), (6.6, 0, 39.0, 2.9), (8.6, 0, 42.0, 2.6), (9.4, 0, 43.4, 2.7)], 16, 3), 'body',
        lambda v, u: chain(v, ('chest', 'neck', 'head')))
    # Overlapping breast, back and flank feathers in staggered rows, tips down and back.
    rows = ((.92, 6), (.78, 9), (.62, 11), (.46, 12), (.30, 12), (.14, 12), (-.02, 12), (-.2, 11), (-.38, 10), (-.56, 9), (-.74, 7))
    for r, (xi, count) in enumerate(rows):
        for k in range(count):
            psi = TAU*(k+.5*(r % 2))/count
            p, out = torso_point(xi, psi, .985)
            d = unit(add(mul(TORSO_A0, -.86), mul(out, .34)))
            L = 5.6+1.6*math.sin(r*1.3+k*.9)*.3+(.7 if math.cos(psi) < -.2 else 0)
            f = ribbon('plumage_%02d_%02d' % (r, k), r6(p), d, out, L, 3.4, feather_prof(.6), amp=0., curl=.5, nu=7, nv=3, thick=.1)
            put(parts, f, 'feather', 'chest' if xi > .3 else 'body')
    # Neck ruff: a collar of feathers around the base of the neck.
    for k in range(12):
        a = TAU*k/12
        root = (5.3+.6*math.cos(a), 2.9*math.sin(a), 38.2+.8*math.cos(a))
        out = unit((.3*math.cos(a)+.35, math.sin(a), .5+.6*math.cos(a)))
        d = unit(add(mul(out, .5), (0, 0, -.7)))
        put(parts, ribbon('ruff_%02d' % k, r6(root), d, out, 4.2, 3.0, feather_prof(.6), curl=.4, nu=7, nv=3, thick=.1), 'feather',
            lambda v, u: chain(v, ('chest', 'neck')))


def build_legs(parts):
    for side, s in SIDES:
        leg, foot = 'leg_'+side, 'foot_'+side
        put(parts, blob('thigh_'+side, (-.2, s*3.6, 26.0), (0, 0, 1), (1, 0, 0), (3.0, 2.6, 2.8), 16, 10), 'body', leg)
        for k in range(4):   # feathered "trousers"
            root = (-1.0+.7*k, s*(3.9+.2*k), 27.2-.4*k)
            put(parts, ribbon('trouser_%d_%s' % (k, side), r6(root), (.15, .1*s, -1), (1, s*.6, 0), 6.0-.3*k, 3.0, feather_prof(.55),
                              curl=.3, nu=6, nv=3, thick=.1), 'feather', leg)
        put(parts, tube('tarsus_'+side, [(-.2, s*3.5, 25.6, 1.35), (1.0, s*3.6, 22.4, .95), (2.0, s*3.65, 19.6, .75)], 10, 3), 'leg',
            lambda v, u: chain(v, (leg, foot)))
        base = (2.0, s*3.65, 19.3)
        for k, ang in enumerate((-30, 0, 30, 180)):
            a = math.radians(ang)
            dv = (math.cos(a), s*math.sin(a)*(1 if ang != 180 else .2), 0)
            L = 2.6 if ang == 180 else 5.0 if ang == 0 else 4.4
            p1 = add(base, add(mul(dv, L*.55), (0, 0, -.9)))
            p2 = add(base, add(mul(dv, L), (0, 0, -1.9)))
            put(parts, tube('toe_%d_%s' % (k, side), [r6(add(base, mul(dv, .3)))+(.7,), r6(p1)+(.55,), r6(p2)+(.42,)], 8, 3), 'leg', foot)
            t1 = add(p2, add(mul(dv, .9), (0, 0, -.5)))
            t2 = add(p2, add(mul(dv, 1.0), (0, 0, -2.0)))
            put(parts, tube('talon_%d_%s' % (k, side), [r6(sub(p2, mul(dv, .2)))+(.45,), r6(t1)+(.32,), r6(t2)+(.04,)], 8, 3), 'talon', foot)


def build_crest(parts):
    """A burning crest of flame plumes swept back from the crown."""
    for k in range(-2, 3):
        root = (9.4-.4*abs(k), k*.85, 47.0)
        d = unit((-.5-.06*abs(k), k*.2, .82))
        L = 13.5-2.2*abs(k)
        put(parts, ribbon('crest_%d' % (k+2), r6(root), d, (.9, 0, .2), L, 4.4-.5*abs(k), flame_prof(.4), amp=1.4, curl=-1.0,
                          phase=k*.8, ripple=.18, nu=12, nv=4), 'plume',
            lambda v, u: chain(v, ('head', 'crest1', 'crest2')))


def build_tail(parts):
    """A long flowing tail of flame plumes, streaming down and back."""
    for k in range(-3, 4):
        root = (-7.0-.3*abs(k), k*1.05, 25.4)
        d = unit((-.5, k*.11, -.86))
        L = (27.0, 25.0, 25.5, 28.5, 25.5, 25.0, 27.0)[k+3]
        put(parts, ribbon('tail_plume_%d' % (k+3), r6(root), d, (.85, 0, -.5), L, 5.2-.5*abs(k), flame_prof(.5), amp=3.4, curl=-1.6,
                          phase=k*1.1, ripple=.16, nu=16, nv=4), 'plume',
            lambda v, u: chain(v, ('body', 'tail1', 'tail2', 'tail3')))
    # Short solid rump feathers lit like the body.
    for k in range(-2, 3):
        root = (-6.0, k*1.5, 27.6)
        d = unit((-.75, k*.16, -.45))
        put(parts, ribbon('rump_%d' % (k+2), r6(root), d, (.3, 0, .95), 9.5-.8*abs(k), 3.8, feather_prof(.55), curl=.6, nu=8, nv=3), 'feather',
            lambda v, u: chain(v, ('body', 'tail1', 'tail2')))


def wing_anchor(s, f):
    """Point along shoulder->elbow->wrist->hand for f in 0..3."""
    pts = [SHOULDER[s], ELBOW[s], WRIST[s], HAND[s]]
    i = min(2, int(f)); return lerp(pts[i], pts[i+1], f-i)


def wing_weights(s, side):
    names = tuple('wing%d_%s' % (i, side) for i in (1, 2, 3, 4))
    return names


def arm_theta(s):
    """Direction angle of the arm inside the fan plane."""
    d = unit(sub(HAND[s], SHOULDER[s]))
    return math.degrees(math.atan2(sum(d[i]*E_UP[i] for i in range(3)), d[1]*s))


def build_wing(parts, side, s):
    names = wing_weights(s, side)
    parts_before = len(parts)
    put(parts, tube('wing_arm_'+side, [r6(SHOULDER[s])+(1.0,), r6(ELBOW[s])+(.8,), r6(WRIST[s])+(.6,), r6(HAND[s])+(.4,)], 10, 4), 'talon',
        lambda v, u: chain(v, names))

    def rigid(root):
        w = chain(root, names)
        return lambda v, u: w
    nrm = N_WING
    ta = arm_theta(s)
    # Solid feathers, lit crimson -> gold. Scapulars over the shoulder.
    for k in range(6):
        f = k/5
        root = add(wing_anchor(s, .1+.8*f), mul(nrm, -.15*k))
        theta = 112+30*(1-f)
        put(parts, ribbon('scapular_%d_%s' % (k, side), r6(root), fan(s, theta), nrm, 10.5-.8*f, 4.0, feather_prof(.55), curl=.9, nu=8, nv=3),
            'feather', rigid(root))
    # Inner secondaries fan up and back from the forearm.
    for k in range(6):
        f = k/5
        root = add(wing_anchor(s, 1+1.2*f), mul(nrm, -.08*k-.1))
        theta = 106-46*f
        L = (17.0, 17.8, 18.0, 17.6, 16.6, 15.2)[k]
        put(parts, ribbon('secondary_%d_%s' % (k, side), r6(root), fan(s, theta), nrm, L, 6.4, feather_prof(.6), amp=.5*(-1)**k, curl=1.6,
                          phase=k, nu=10, nv=3), 'feather', rigid(root))
    # Outer trailing feathers hang out and forward-down from the forearm and
    # wrist, filling the wing below its leading edge and cupping it forward.
    for k in range(6):
        f = k/5
        root = add(wing_anchor(s, 1.2+1.5*f), mul(nrm, .2+.05*k))
        theta = 16-40*f
        L = (13.0, 13.4, 13.4, 12.8, 11.8, 10.6)[k]
        put(parts, ribbon('trailing_%d_%s' % (k, side), r6(root), fan(s, theta), nrm, L, 4.4, feather_prof(.55), amp=.4*(-1)**k, curl=1.9,
                          phase=k*1.3, nu=10, nv=3), 'feather', rigid(root))
    # Leading edge: overlapping marginal feathers running along the arm.
    for k in range(12):
        f = .15+2.7*k/11
        root = add(wing_anchor(s, f), mul(nrm, 1.5+.05*(k % 2)))
        put(parts, ribbon('marginal_%d_%s' % (k, side), r6(root), fan(s, ta+14+4*(k % 3)), nrm, 8.2+.5*(k % 3), 4.4, feather_prof(.5), curl=.8,
                          nu=8, nv=3), 'feather', rigid(root))
    for band, (f0, f1, count, theta0, theta1, L) in enumerate(((.2, .9, 4, 112, 92, 6.2), (1.1, 1.9, 5, 98, 64, 6.8), (2.1, 2.9, 4, 72, 48, 6.2))):
        for k in range(count):
            f = k/(count-1)
            root = add(wing_anchor(s, f0+(f1-f0)*f), mul(nrm, .32+.08*band))
            put(parts, ribbon('covert_%d%d_%s' % (band, k, side), r6(root), fan(s, theta0+(theta1-theta0)*f), nrm, L, 3.7, feather_prof(.6),
                              curl=.5, nu=7, nv=3), 'feather', rigid(root))
    # Primaries: fullbright licking flame tongues fanned from wrist and hand.
    lengths = (12.6, 13.2, 13.7, 14.2, 14.4, 14.4, 14.0, 13.4, 12.6)
    for k in range(9):
        f = k/8
        theta = 20+66*f**1.05
        root = add(lerp(HAND[s], WRIST[s], f*.9), mul(nrm, .1))
        g = 'a' if k < 3 else 'b' if k < 6 else 'c'
        tb = IDS['tongue_%s_%s' % (g, side)]
        base = chain(root, names)

        def wts(v, u, base=base, tb=tb):
            m = clamp((u[0]-.28)/.5); m = m*m*(3-2*m)
            return blend(base, {tb: 1.0}, m)
        put(parts, ribbon('primary_%d_%s' % (k, side), r6(root), fan(s, theta), nrm, lengths[k], 5.6-.2*k, flame_prof(.32),
                          amp=(1.2+.3*k)*(-1)**k*.6, curl=2.2+.2*k, phase=k*.9+(0 if s > 0 else 1.3), ripple=.2, nu=14, nv=4), 'flame', wts)
    # Flame licks burning along the top of the leading edge.
    for k, (f, dth, L) in enumerate(((1.0, 40, 7.5), (1.6, 44, 8.5), (2.2, 48, 9.0), (2.7, 42, 7.5))):
        root = add(wing_anchor(s, f), mul(nrm, .75))
        tb = IDS['tongue_%s_%s' % ('c' if k < 2 else 'b', side)]
        base = chain(root, names)

        def wts(v, u, base=base, tb=tb):
            m = clamp((u[0]-.2)/.6); m = m*m*(3-2*m)
            return blend(base, {tb: 1.0}, m*.6)
        put(parts, ribbon('lick_%d_%s' % (k, side), r6(root), fan(s, ta+dth), nrm, L, 3.0, flame_prof(.3),
                          amp=1.0, curl=1.0, phase=k*1.7, ripple=.2, nu=10, nv=3), 'flame', wts)
    # Sparks: crackling embers shed near the primaries.
    for k, (g, theta, dist) in enumerate((('a', 26, 8.5), ('b', 54, 10.5), ('c', 84, 11.0))):
        c = add(HAND[s], mul(fan(s, theta), dist))
        put(parts, blob('spark_%d_%s' % (k, side), r6(c), (0, 0, 1), (1, 0, 0), (.9, .9, .9), 8, 5), 'ember', 'tongue_%s_%s' % (g, side))
    return len(parts)-parts_before


def _inside(p, limit=.9):
    """Keep a hidden chunk inside the torso ellipsoid at rest."""
    def norm(x):
        d = sub(x, TORSO_C)
        return math.sqrt(sum((sum(d[i]*ax[i] for i in range(3))/r)**2 for ax, r in zip((TORSO_A0, TORSO_A1, TORSO_A2), TORSO_R)))
    c = p.vertices
    center = tuple(math.fsum(v[i] for v in c)/len(c) for i in range(3))
    worst = max(norm(v) for v in c)
    if worst > limit:
        k = limit/worst
        p.vertices = [r6(add(center, mul(sub(v, center), k))) for v in c]
        worst2 = max(norm(v) for v in p.vertices)
        if worst2 > limit:   # centre itself is off-axis: pull it toward the torso centre too
            p.vertices = [r6(add(TORSO_C, mul(sub(v, TORSO_C), limit/worst2))) for v in p.vertices]
    return p


def build_ash(parts):
    """Ash and ember chunks hidden inside the torso; they scatter in the death."""
    n = 0
    for k in range(LUMP_BONES):   # one large, flat, smooth mound per bone
        r = 3.4+.3*(k % 3)
        kind = 'ember' if k in (2, 7) else 'ash'
        put(parts, _inside(lump('%s_%d_0' % (kind, k), ASH_CENTERS[k], (r, r*.92, r*.55), k*7)), kind, 'ash_%d' % k)
        n += 1
    # Spreaders (see SPREADS).
    for i, (nm, axis_, r0, r0z, off, rad, zr, za, pw) in enumerate(SPREADS):
        base = LUMP_BONES+i*(RING+1)
        c = ASH_CENTERS[base]
        part = blob('ash_%s' % nm, c, (0, 0, 1), (1, 0, 0), (r0z, r0, r0), 18, 9)
        _inside(part, .88)

        def wts(v, u, c=c, base=base, r0=r0, pw=pw):
            o = sub(v, c)
            rho = min(1.0, math.hypot(o[0], o[1])/r0)**pw
            pos = (math.atan2(o[1], o[0]) % TAU)/(TAU/RING)
            i0 = int(pos) % RING; fr = pos-int(pos)
            bid = lambda idx: IDS['ash_%d' % idx]
            out = {bid(base): 1-rho}
            a_, b_ = bid(base+1+i0), bid(base+1+(i0+1) % RING)
            out[a_] = out.get(a_, 0)+rho*(1-fr)
            out[b_] = out.get(b_, 0)+rho*fr
            return out
        put(parts, part, 'ash', wts)
        n += 1
    return n


def build_parts():
    parts = []
    build_head(parts)
    build_neck_and_torso(parts)
    build_legs(parts)
    build_crest(parts)
    build_tail(parts)
    for side, s in SIDES:
        build_wing(parts, side, s)
    build_ash(parts)
    return parts


_GEOM = None


def geometry():
    global _GEOM
    if _GEOM is None:
        parts = build_parts()
        _GEOM = assemble(parts, None)
    return _GEOM


# ---------------------------------------------------------------- posing
def qx(d): return axis((1, 0, 0), math.radians(d))
def qy(d): return axis((0, 1, 0), math.radians(d))
def qz(d): return axis((0, 0, 1), math.radians(d))


def env(t):
    """0 at both ends, 1 at the middle frame."""
    return math.sin(math.pi*t)**2


def window(t, a, b):
    x = clamp((t-a)/(b-a))
    return x*x*(3-2*x)


class Pose:
    def __init__(self):
        self.f = [[*local, 0, 0, 0, 1, 1, 1, 1] for _, _, local in BONES]

    def rot(self, bone, q):
        row = self.f[IDS[bone]]
        row[3:7] = qmul(q, tuple(row[3:7]))

    def move(self, bone, d):
        row = self.f[IDS[bone]]
        for i in range(3):
            row[i] += d[i]

    def rows(self):
        return [tuple(r) for r in self.f]


def wing_pose(P, roll, pitch=0., sweep=0., lag=(0., 0., 0.), fold=0., sway=(0., 0., 0.), bend=(0., 0., 0.)):
    """Both wings; roll>0 raises the tips, pitch>0 leans the fan forward, sweep>0
    sweeps forward. lag adds elbow/wrist/hand roll; sway/bend flex the tongue groups."""
    for side, s in SIDES:
        P.rot('wing1_'+side, qmul(qz(-s*sweep), qmul(qy(pitch), qx(s*roll))))
        P.rot('wing2_'+side, qx(s*lag[0]))
        P.rot('wing3_'+side, qx(s*lag[1]))
        P.rot('wing4_'+side, qx(s*lag[2]))
        for i, g in enumerate('abc'):
            n = axis(N_WING, math.radians(sway[i]*s))
            across = unit(cross(N_WING, fan(s, TONGUE_THETA[g])))
            P.rot('tongue_%s_%s' % (g, side), qmul(n, axis(across, math.radians(bend[i]))))


def tail_pose(P, pitch=0., yaw=0., lag=.8, phase=0.):
    for i, b in enumerate(('tail1', 'tail2', 'tail3')):
        P.rot(b, qmul(qz(yaw*(1+.3*i)*math.sin(phase-lag*i)), qy(pitch*(1-.15*i)+.0)))


def legs_pose(P, hip=0., foot=0., spread=0.):
    for side, s in SIDES:
        P.rot('leg_'+side, qmul(qz(s*spread), qy(hip)))
        P.rot('foot_'+side, qy(foot))


def head_pose(P, neck=0., head=0., jaw=0., crest=0.):
    P.rot('neck', qy(neck)); P.rot('head', qy(head)); P.rot('jaw', qy(jaw))
    P.rot('crest1', qy(crest)); P.rot('crest2', qy(crest*.8))


def idle_pose(t):
    P = Pose(); a = TAU*t
    P.move('body', (0, 0, .9*math.sin(a+.7)))
    P.rot('chest', qy(1.6*math.sin(a+.4)))
    wing_pose(P, roll=-4+8*math.sin(a), pitch=5+4*math.sin(a+.5), sweep=2*math.sin(a+.3),
              lag=(3*math.sin(a-.6), 5*math.sin(a-1.2), 7*math.sin(a-1.8)),
              sway=tuple(9*math.sin(2*a-.9*i) for i in range(3)), bend=tuple(6*math.sin(2*a-1.4*i+.5) for i in range(3)))
    tail_pose(P, pitch=4*math.sin(a-.5), yaw=7, phase=a)
    legs_pose(P, hip=-5+4*math.sin(a+.9), foot=3*math.sin(a+.2))
    head_pose(P, neck=1.5*math.sin(a+.2), head=2*math.sin(a+.6), crest=5*math.sin(2*a))
    return P.rows()


def fly_pose(t):
    P = Pose(); a = TAU*t
    down = math.sin(a)
    P.move('body', (0, 0, -2.0*down))
    P.rot('body', qy(-3*math.sin(a-.5)))
    P.rot('chest', qy(-2*math.sin(a-.4)))
    wing_pose(P, roll=-19+31*math.cos(a), pitch=8*math.sin(a+.6), sweep=28-8*math.cos(a+.4),
              lag=(-11*math.sin(a), -17*math.sin(a), -21*math.sin(a)),
              sway=tuple(14*math.sin(a-.8*i-.7) for i in range(3)), bend=tuple(12*math.sin(a-.9*i-1.1) for i in range(3)))
    tail_pose(P, pitch=-9+7*math.sin(a-.7), yaw=9, lag=1.0, phase=a-.4)
    legs_pose(P, hip=-14+5*math.sin(a+.4), foot=-6+4*math.sin(a))
    head_pose(P, neck=-2*math.sin(a+.6), head=2*math.sin(a+.9), crest=-8+4*math.sin(a-.3))
    return P.rows()


def claw_pose(t):
    """Wings mantled wide and low, talons thrust forward, beak open."""
    P = Pose(); p = env(t)
    P.move('body', (3.5*p, 0, -3.0*p))
    P.rot('body', qy(20*p))
    P.rot('chest', qy(6*p))
    wing_pose(P, roll=-64*p+6*math.sin(t*TAU*2)*p, pitch=14*p, sweep=44*math.sqrt(p), lag=(-10*p, -14*p, -12*p),
              sway=(-14*p, -6*p, 8*p), bend=(10*p, 12*p, 14*p))
    tail_pose(P, pitch=-22*p, yaw=6, phase=t*TAU*2)
    legs_pose(P, hip=-84*p+ -14*(1-p)*0, foot=-14*p, spread=7*p)
    head_pose(P, neck=14*p, head=10*p, jaw=36*p, crest=16*p)
    return P.rows()


def peck_pose(t):
    """Neck and head strike forward and down, beak wide, wings half-mantled."""
    P = Pose(); p = env(t)
    P.move('body', (1.0*p, 0, -2.0*p))
    P.rot('body', qy(14*p))
    P.rot('chest', qy(10*p))
    wing_pose(P, roll=-30*p, pitch=6*p, sweep=32*math.sqrt(p), lag=(-6*p, -9*p, -9*p), sway=(-8*p, 0, 8*p), bend=(6*p, 8*p, 10*p))
    tail_pose(P, pitch=-12*p, yaw=5, phase=t*TAU)
    legs_pose(P, hip=-40*p, foot=-14*p)
    head_pose(P, neck=26*p, head=22*p, jaw=34*p*window(t, .15, .45), crest=12*p)
    return P.rows()


def recoil_pose(t):
    P = Pose(); p = env(t); w = math.sin(t*TAU*3)*p
    P.move('body', (-2.0*p, 0, 1.5*p))
    P.rot('body', qy(-16*p))
    wing_pose(P, roll=24*p, pitch=-8*p, sweep=-14*p, lag=(6*p, 8*p, 8*p), sway=(18*p*(1 if w >= 0 else -1), 0, -10*w), bend=(-10*p, -12*p, -14*p))
    tail_pose(P, pitch=14*p, yaw=6, phase=t*TAU*3)
    legs_pose(P, hip=-14*p+4*w, foot=-4*p)
    head_pose(P, neck=-12*p, head=-12*p, jaw=14*p, crest=-16*p)
    return P.rows()


# Death: the bird flares, folds and drops onto the floor; the ash and ember
# chunks hidden in its torso scatter out into a heap on and around the husk.
HUSK_LUMPS = (6, 7, 8)   # these three ride on top of the husk (z relative to its centre)
ASH_REL = [(-19.0, 6.0, 8.2), (-15.5, 9.5, 2.5), (-22.0, 2.0, 2.5), (16.0, -9.0, 6.0), (19.5, -7.0, 2.5),
           (8.0, -12.5, 2.5), (-6.0, 1.0, 6.6), (1.0, -1.0, 7.0), (6.0, 1.5, 6.4), (20.0, 3.0, 2.5)]


def spread_target(k):
    """Offset from the husk centre (dx, dy, absolute z) of a spreader bone."""
    i, j = divmod(k-LUMP_BONES, RING+1)
    nm, axis_, r0, r0z, off, rad, zr, za, pw = SPREADS[i]
    if j == 0:
        return (off[0], off[1], za)
    ang = TAU*(j-1)/RING
    return (off[0]+rad[0]*math.cos(ang), off[1]+rad[1]*math.sin(ang), zr)


def flare_bones(P, t, s1):
    """The burst: wings thrown up, head back, beak wide, flames flaring."""
    P.move('body', (0, 0, 6.0*math.sin(math.pi*window(t, 0, .34))))
    P.rot('body', qy(-6*s1))
    wing_pose(P, roll=34*s1, pitch=-6*s1, sweep=-6*s1, lag=(-6*s1, -8*s1, -10*s1),
              sway=(26*s1, -18*s1, 12*s1), bend=(24*s1, 20*s1, 16*s1))
    tail_pose(P, pitch=10*s1, yaw=10*s1, phase=t*TAU*3)
    legs_pose(P, hip=28*s1*0-24*s1, foot=-10*s1)
    head_pose(P, neck=-32*s1, head=-24*s1, jaw=46*s1, crest=14*s1)


def world_targets():
    """World rotations of the collapsed husk: torso flat on the floor, neck and
    head laid forward, crest and tail flat behind, legs folded back, wings
    splayed and drooping onto the floor with their fans lying flat."""
    q = {'body': qy(42), 'chest': qy(46), 'neck': qy(68), 'head': qy(62), 'jaw': qy(74),
         'crest1': qy(-48), 'crest2': qy(-52),
         'tail1': qmul(qz(10), qy(44)), 'tail2': qmul(qz(-14), qy(52)), 'tail3': qmul(qz(12), qy(58))}
    for side, s in SIDES:
        wing = qmul(qz(s*52), qmul(qy(-50), qx(s*-50)))
        for n in '1234':
            q['wing%s_%s' % (n, side)] = wing
        for g_ in 'abc':
            q['tongue_%s_%s' % (g_, side)] = qmul(wing, axis(N_WING, math.radians(s*{'a': 12, 'b': 0, 'c': -12}[g_])))
        q['leg_'+side] = qmul(qz(s*14), qy(98))
        q['foot_'+side] = qmul(qz(s*14), qy(-4))
    return q


_FINAL = None


def final_locals():
    """Local rotations that realise world_targets(), parents first."""
    global _FINAL
    if _FINAL is None:
        targets = world_targets()
        world = {-1: (0, 0, 0, 1), 0: (0, 0, 0, 1)}
        out = {}
        for i, (name, parent, _) in enumerate(BONES):
            if i == 0 or name.startswith('ash_'):
                continue
            tq = targets[name]
            out[name] = qmul(inverse(world[parent]), tq)
            world[i] = tq
        _FINAL = out
    return _FINAL


def death_frame(t):
    s1 = window(t, 0, .2)
    s2 = window(t, .16, .72)
    P = Pose()
    flare_bones(P, t, s1*(1-s2))
    final = final_locals()
    for name, qf in final.items():
        row = P.f[IDS[name]]
        row[3:7] = slerp(tuple(row[3:7]), qf, s2)
    P.move('body', (5.0*s2, 0, 0))
    return P


_BIRD = None


def bird_vertices():
    """Indices of every non-ash vertex."""
    global _BIRD
    if _BIRD is None:
        parts, v, n, uv, tri, w = geometry()
        ash = {IDS['ash_%d' % k] for k in range(ASH_COUNT)}
        _BIRD = [i for i, row in enumerate(w) if row[0][0] not in ash]
    return _BIRD


_DROP = None


def death_final_drop():
    """Root drop that puts the fully collapsed husk exactly on the floor."""
    global _DROP
    if _DROP is None:
        parts, v, n, uv, tri, w = geometry()
        pts = RIG.deform(v, w, death_frame(1.0).rows())
        _DROP = min(pts[i][2] for i in bird_vertices())-FLOOR
    return _DROP


def death_pose(t):
    P = death_frame(t)
    parts, v, n, uv, tri, w = geometry()
    rows = [list(r) for r in P.rows()]
    drop = death_final_drop()*window(t, .1, .78)**1.6
    rows[0][2] -= drop
    pts = RIG.deform(v, w, [tuple(r) for r in rows])
    low = min(pts[i][2] for i in bird_vertices())
    if low < FLOOR:
        rows[0][2] += FLOOR-low
    tf = RIG.matrices([tuple(r) for r in rows])
    pl, pq = tf[IDS['body']]
    center = add(pl, rotate(pq, sub(TORSO_C, PELVIS)))
    s3 = window(t, .12, .8)
    s4 = window(t, .3, .9)
    for k in range(ASH_COUNT):
        b = IDS['ash_%d' % k]
        w_rest = add(pl, rotate(pq, BONES[b][2]))
        if k < LUMP_BONES:
            dx, dy, z = ASH_REL[k]
            sk = s3
        else:
            dx, dy, z = spread_target(k)
            sk = s4
        target = (center[0]+dx, center[1]+dy, center[2]+z-2.0 if k in HUSK_LUMPS else z)
        wpos = lerp(w_rest, target, sk)
        if k < LUMP_BONES:
            wpos = (wpos[0], wpos[1], wpos[2]+7.0*math.sin(math.pi*sk)*(1-sk*.3))
        rows[b][0:3] = list(rotate(inverse(pq), sub(wpos, pl)))
        rows[b][3:7] = list(slerp((0, 0, 0, 1), inverse(pq), sk))
    return [tuple(r) for r in rows]


HOVER = 3.4   # constant root lift so the trailing tail never needs automatic floor compensation


def pose(name, t):
    if name == 'death':
        return death_pose(t)
    rows = {'idle': idle_pose, 'fly': fly_pose, 'claw': claw_pose, 'peck': peck_pose, 'recoil': recoil_pose}[name](t)
    rows[0] = (rows[0][0], rows[0][1], rows[0][2]+HOVER)+tuple(rows[0][3:])
    return rows


# ---------------------------------------------------------------- export
def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)
def texture_bytes(): return materials.texture_bytes()


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tri, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tri, w, BONES, clips, bounds, mesh_label='Project_Broom_phoenix', material_path=SKIN)
    (ROOT/MODEL).write_bytes(data)
    out = ROOT/'assets/monsters/phoenix'
    out.mkdir(exist_ok=True)
    manifest = dict(schemaVersion=1, workId='BRG-M65', format='IQM v2', runtimeModel=MODEL,
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tri), boneCount=len(BONES),
                    bones=[dict(name=nm, parent=p, local=loc) for nm, p, loc in BONES],
                    clips=[{k: x for k, x in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/phoenix/phoenix-animated.blend')
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    from tools.monster_models import phoenix_animation as module
    print(module.build()['sha256'])
