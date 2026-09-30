"""Original connected fury, six purely cosmetic skeletal roles. No gameplay.

Brogue: "A creature of inchoate rage made flesh, the fury's moist wings beat
loudly in the darkness." Brogue gives only that, a dark red glyph, flight and
sleeplessness. The avian avenger read is an art interpretation of the
classical Furies: a gaunt, ashen, wild-haired winged woman with bleeding eye
sockets, a snarling mouth, long black-nailed hands, a feathered breast and
mantle that flows over the shoulders into the wings, feathered hips, scaled
bird legs with hooked talons and two great feather wings painted wet. It is
deliberately unlike the vampire bat: feathered wings on separate back bones,
a humanoid torso and head, and bird feet. +X forward, Z up, +Y left.

Flight, sleeplessness, pack behaviour, damage, turns and every outcome belong
to Brogue. The rest mesh hovers with an art-chosen gap below the talons.
"""
import hashlib
import json
import math

from . import iqm, fury_materials as materials
from .rat import ROOT, Part, add, sub, mul, unit, cross
from .skeletal import Rig, axis, qmul, inverse, rotate, assemble, sample_clips
from .pixie_animation import dot, clamp, smooth, window, lerp, r6, ortho, blob, tube, shell, slerp
from .imp_animation import Pose, sharp_chain, quantise, leaf

SKIN = materials.SKIN
MODEL = 'mod/BrogueDoom/models/monsters/46_fury.iqm'
TAU = math.tau
SIDES = (('L', 1), ('R', -1))
SKIN_VOXEL_SIZE = .12
SKIN_FACE_BUDGET = 7900
DIAG_COLOURS = {'skin_leg': (150, 130, 100), 'skin_foot': (150, 130, 100), 'skin': (178, 158, 166), 'eye': (255, 50, 30),
                'hair': (30, 8, 12), 'primary': (110, 10, 20), 'secondary': (90, 8, 16), 'tertial': (90, 8, 16),
                'covert': (130, 20, 30), 'scapular': (70, 8, 16), 'mantle': (80, 10, 20), 'wing_arm': (70, 8, 14), 'legfeather': (60, 6, 14), 'tailfeather': (80, 8, 16),
                'nail': (20, 10, 10), 'talon': (20, 10, 10), 'toe': (150, 130, 100), 'brow': (40, 20, 24)}


def CONNECTED_SKIN(name):
    return name.startswith('skin_')


# ---------------------------------------------------------------- skeleton
PELVIS, SPINE, CHEST, NECK, HEAD = (0.1, 0, 25.6), (0.2, 0, 29.2), (0.4, 0, 33.2), (0.6, 0, 37.8), (1.0, 0, 40.2)
HAIR, HAIR2, TAILB = (-0.9, 0, 45.2), (-3.4, 0, 40.2), (-1.8, 0, 25.0)
SHOULDER = {s: (0.2, s*3.8, 37.2) for _, s in SIDES}
ELBOW = {s: (-0.4, s*5.9, 31.8) for _, s in SIDES}
WRIST = {s: (1.0, s*6.5, 26.8) for _, s in SIDES}
HIP = {s: (0.1, s*2.1, 25.0) for _, s in SIDES}
KNEE = {s: (2.5, s*2.5, 19.8) for _, s in SIDES}
HOCK = {s: (-0.9, s*2.6, 14.0) for _, s in SIDES}
BALL = {s: (0.8, s*2.7, 10.2) for _, s in SIDES}
EAR = {s: (0.2, s*2.2, 43.0) for _, s in SIDES}
EAR_TIP = {s: (-1.9, s*3.9, 44.4) for _, s in SIDES}
WING1 = {s: (-1.8, s*1.5, 37.2) for _, s in SIDES}
WING2 = {s: (-3.4, s*8.0, 41.0) for _, s in SIDES}
WING3 = {s: (-4.0, s*14.2, 39.4) for _, s in SIDES}
WTIP = {s: (-4.6, s*18.4, 37.6) for _, s in SIDES}


def hand_frame(s):
    e = unit(sub(WRIST[s], ELBOW[s]))
    n = ortho((0, -s, 0), e)
    w = unit(cross(n, e))
    if w[0] < 0: w = mul(w, -1)
    return e, n, w


def knuckle(s):
    return r6(add(WRIST[s], mul(hand_frame(s)[0], 1.6)))


SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', PELVIS), ('spine', 'pelvis', SPINE), ('chest', 'spine', CHEST),
         ('neck', 'chest', NECK), ('head', 'neck', HEAD), ('hair', 'head', HAIR), ('hair2', 'hair', HAIR2),
         ('tail', 'pelvis', TAILB)]
for side, s in SIDES:
    SPECS.append(('ear_'+side, 'head', EAR[s]))
for side, s in SIDES:
    SPECS += [('arm_'+side, 'chest', SHOULDER[s]), ('forearm_'+side, 'arm_'+side, ELBOW[s]),
              ('hand_'+side, 'forearm_'+side, WRIST[s]), ('claws_'+side, 'hand_'+side, knuckle(s)),
              ('thigh_'+side, 'pelvis', HIP[s]), ('shin_'+side, 'thigh_'+side, KNEE[s]),
              ('foot_'+side, 'shin_'+side, HOCK[s]), ('toes_'+side, 'foot_'+side, BALL[s]),
              ('wing1_'+side, 'chest', WING1[s]), ('wing2_'+side, 'wing1_'+side, WING2[s]),
              ('wing3_'+side, 'wing2_'+side, WING3[s])]
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, _, _) in enumerate(BONES)}
CLIPS = [('idle', 36, 24, True), ('fly', 24, 30, True), ('drub', 24, 30, False),
         ('lash', 24, 30, False), ('recoil', 12, 30, False), ('death', 36, 30, False)]


def P_(): return Pose(RIG, IDS)


# ---------------------------------------------------------------- anatomy
HEAD_C, HEAD_R = (0.6, 0, 43.4), (2.6, 2.3, 2.9)
FACE_C, FACE_R = (1.6, 0, 42.0), (1.9, 1.85, 2.5)
CHIN_C, CHIN_R = (2.65, 0, 39.9), (.85, .95, .8)
EYE_Y, EYE_Z = 1.0, 42.9
MOUTH = (3.4, 40.75, 1.05)


def head_surface_x(y, z):
    best = -9.
    for c, r in ((HEAD_C, HEAD_R), (FACE_C, FACE_R), (CHIN_C, CHIN_R)):
        q = 1-((y-c[1])/r[1])**2-((z-c[2])/r[2])**2
        if q > 0: best = max(best, c[0]+r[0]*math.sqrt(q))
    return best


def zblob(name, center, radii, seg=28, rings=18, taper=None):
    return blob(name, center, (0, 0, 1), (1, 0, 0), (radii[2], radii[0], radii[1]), seg, rings, taper)


def build_head(parts):
    parts.append(zblob('skin_cranium', HEAD_C, HEAD_R, 34, 22))
    parts.append(zblob('skin_face', FACE_C, FACE_R, 32, 20))
    parts.append(zblob('skin_chin', CHIN_C, CHIN_R, 22, 14))
    nx = head_surface_x(0, 42.1)
    parts.append(blob('skin_nose', (nx-.15, 0, 42.1), (.5, 0, -.87), (0, 1, 0), (.8, .38, .42), 18, 12))
    for side, s in SIDES:
        parts.append(leaf('skin_ear_'+side, EAR[s], EAR_TIP[s], (1, s*.5, .3), .8, .22, 16, 14))
        f = unit((math.cos(math.radians(14)), s*math.sin(math.radians(14)), 0))
        up = ortho((0, 0, 1), f)
        c = sub((head_surface_x(s*EYE_Y, EYE_Z), s*EYE_Y, EYE_Z), mul(f, .32))
        parts.append(blob('eye_'+side, r6(c), f, up, (.5, .5, .62), 24, 16))
        # Heavy frowning brow: low and pinched toward the nose.
        pts = []
        for k, (y, z, r) in enumerate(((.25, 43.25, .3), (.8, 43.6, .34), (1.45, 43.9, .3), (1.95, 43.95, .18))):
            pts.append((round(head_surface_x(y, z)+.02, 6), round(s*y, 6), z, r))
        parts.append(tube('brow_'+side, pts, 10, 3))
        # Two upper fangs at the snarl.
        y = .55
        bx = head_surface_x(s*y, 41.0)
        parts.append(tube('tooth_'+side, [(bx-.2, s*y, 41.1, .16), (bx+.02, s*y, 40.7, .12), (bx+.05, s*y, 40.25, .01)], 8, 2))


CAP_C, CAP_R = (0.3, 0, 43.9), (2.75, 2.45, 2.85)


def cap_point(az, el, lift=0.):
    a, e = math.radians(az), math.radians(el)
    d = (math.cos(e)*math.cos(a), math.cos(e)*math.sin(a), math.sin(e))
    k = 1+lift/2.8
    return add(CAP_C, (CAP_R[0]*d[0]*k, CAP_R[1]*d[1]*k, CAP_R[2]*d[2]*k))


# Wild long hair: (azimuth, elevation, fall length, lateral flare, curl, radius).
LOCKS = [(20, 62, 11, .6, 1.0, .5), (-20, 62, 11, -.6, 1.2, .5), (50, 50, 12, 1.4, .8, .48), (-50, 50, 12, -1.4, .9, .48),
         (80, 40, 12, 2.2, 1.1, .46), (-80, 40, 12, -2.2, 1.0, .46), (110, 34, 13, 2.4, .9, .5), (-110, 34, 13, -2.4, .9, .5),
         (140, 30, 14, 1.8, 1.2, .52), (-140, 30, 14, -1.8, 1.2, .52), (165, 28, 14, .8, 1.0, .55), (-165, 28, 14, -.8, 1.1, .55),
         (180, 50, 13, 0, .9, .55), (130, 60, 12, 1.2, 1.3, .5), (-130, 60, 12, -1.2, 1.3, .5), (160, 70, 11, .5, 1.0, .5),
         (-160, 70, 11, -.5, 1.0, .5), (95, 58, 11, 2.6, 1.4, .44), (-95, 58, 11, -2.6, 1.4, .44), (0, 80, 10, 0, 1.5, .5),
         (35, 30, 9, 1.8, 1.2, .38), (-35, 30, 9, -1.8, 1.2, .38)]


def build_hair(parts):
    parts.append(blob('hair_cap', CAP_C, (0, 0, 1), (1, 0, 0), (CAP_R[2], CAP_R[0], CAP_R[1]), 30, 18))
    for k, (az, el, fall, flare, curl_, radius) in enumerate(LOCKS):
        root = cap_point(az, el, -.25)
        side = math.sin(math.radians(az))
        pts = []
        for i, f in enumerate((0, .12, .3, .5, .7, .85, 1.)):
            # Sweep back off the scalp, then fall behind the shoulders with a writhing wave.
            back = -1.2*min(1, f*4)-3.2*f
            wave = curl_*.9*math.sin(f*TAU*1.1+k)*f
            p = add(root, (back+(.8 if abs(az) < 60 else 0)*f, side*(1.4*min(1, f*3))+flare*f+wave, -fall*f**1.2+1.2*min(1, f*4)))
            if i == 0: p = sub(p, mul(unit(sub(p, CAP_C)), .3))
            pts.append((*r6(p), round(radius*(1.1-.95*f**1.3), 6)))
        parts.append(tube(f'hair_lock_{k}', pts, 8, 3))


def build_body(parts):
    parts.append(tube('skin_neck', [(0.3, 0, 36.2, 1.4), (0.6, 0, 38.2, 1.08), (0.9, 0, 40.0, 1.05), (1.3, 0, 41.2, 1.2)], 18, 3))
    parts.append(zblob('skin_chest', (0.3, 0, 33.9), (2.1, 3.2, 2.9), 32, 20))
    for side, s in SIDES:
        parts.append(zblob('skin_breast_'+side, (1.55, s*1.25, 33.6), (1.1, 1.15, 1.05), 18, 12))
    parts.append(zblob('skin_belly', (0.3, 0, 29.8), (1.55, 2.1, 2.5), 30, 18))
    parts.append(zblob('skin_pelvis', (0.1, 0, 26.3), (1.95, 2.8, 2.1), 30, 18))
    for side, s in SIDES:
        parts.append(zblob('skin_trap_'+side, (-0.2, s*1.8, 36.6), (1.0, 1.25, 1.2), 18, 12))
        parts.append(zblob('skin_shoulder_'+side, (0.2, s*3.55, 36.9), (1.1, 1.1, 1.15), 18, 12))
        sh, el, wr = SHOULDER[s], ELBOW[s], WRIST[s]
        parts.append(tube('skin_arm_'+side, [(0.1, s*3.1, 37.5, .95), (*sh, .9), (*lerp(sh, el, .5), .76), (*el, .6),
                                             (*lerp(el, wr, .4), .66), (*lerp(el, wr, .8), .5), (*wr, .42)], 18, 3))
        e, n, w = hand_frame(s)
        parts.append(blob('skin_palm_'+side, r6(add(wr, mul(e, .9))), e, w, (1.0, .78, .32), 18, 12))
        hp, kn, hk, bl = HIP[s], KNEE[s], HOCK[s], BALL[s]
        parts.append(tube('skin_leg_'+side, [(0.0, s*1.6, 26.4, 1.7), (*hp, 1.7), (1.6, s*2.4, 21.8, 1.35), (*kn, .9),
                                             (0.9, s*2.55, 17.0, .6), (*hk, .5)], 18, 3))
        parts.append(tube('skin_foot_'+side, [(*hk, .5), (-0.1, s*2.65, 12.2, .38), (*bl, .5), (1.2, s*2.7, 9.8, .42)], 14, 3))


def build_hands_feet(parts):
    for side, s in SIDES:
        e, n, w = hand_frame(s)
        kn = knuckle(s)
        for k, (off, length) in enumerate(((.5, 2.3), (.17, 2.6), (-.17, 2.5), (-.5, 2.1))):
            b = add(kn, mul(w, off))
            mid = add(b, add(mul(e, length*.55), mul(n, .3)))
            end = add(b, add(mul(e, length), mul(n, .75)))
            parts.append(tube(f'finger_{k}_'+side, [r6(sub(b, mul(e, .5)))+(.22,), r6(b)+(.22,), r6(mid)+(.19,), r6(end)+(.16,)], 8, 2))
            tip = add(end, add(mul(e, 1.0), mul(n, 1.0)))
            parts.append(tube(f'nail_{k}_'+side, [r6(sub(end, mul(e, .15)))+(.18,), r6(add(end, add(mul(e, .55), mul(n, .3))))+(.13,),
                                                  r6(tip)+(.012,)], 8, 3))
        b = add(WRIST[s], add(mul(e, .5), add(mul(w, .55), mul(n, .1))))
        t1 = add(b, add(mul(w, .55), add(mul(e, .55), mul(n, .3))))
        t2 = add(t1, add(mul(w, .2), add(mul(e, .5), mul(n, .5))))
        parts.append(tube('thumb_'+side, [r6(sub(b, mul(w, .3)))+(.24,), r6(b)+(.22,), r6(t1)+(.18,), r6(t2)+(.14,)], 8, 2))
        parts.append(tube('nail_thumb_'+side, [r6(sub(t2, mul(e, .1)))+(.14,), r6(add(t2, add(mul(e, .4), mul(n, .3))))+(.09,),
                                               r6(add(t2, add(mul(e, .7), mul(n, .7))))+(.01,)], 8, 3))
        # Bird foot: three forward toes and a hind toe, each with a hooked talon.
        bl = BALL[s]
        for k, ang in enumerate((-28, 0, 28, 180)):
            a = math.radians(ang)
            d = (math.cos(a), s*math.sin(a)*(1 if ang != 180 else 0)+(s*.15 if ang == 180 else 0), 0)
            L = 1.9 if ang == 180 else 3.0 if ang == 0 else 2.6
            p0 = add(bl, mul(d, .3))
            p1 = add(bl, add(mul(d, L*.55), (0, 0, -.35)))
            p2 = add(bl, add(mul(d, L), (0, 0, -.95)))
            parts.append(tube(f'toe_{k}_'+side, [r6(sub(p0, mul(d, .5)))+(.34,), r6(p0)+(.32,), r6(p1)+(.27,), r6(p2)+(.22,)], 9, 2))
            t1 = add(p2, add(mul(d, .55), (0, 0, -.35)))
            t2 = add(p2, add(mul(d, .6), (0, 0, -1.25)))
            parts.append(tube(f'talon_{k}_'+side, [r6(sub(p2, mul(d, .1)))+(.25,), r6(t1)+(.17,), r6(t2)+(.012,)], 8, 3))


# ---------------------------------------------------------------- feathers
def vane(name, root, d, nrm, L, W, droop=.6, asym=0., tip=.5):
    """A closed, thin, slightly cambered feather: u root..tip, v across (0.5 = shaft).

    tip is where the vane starts to taper; later tapers give broader, overlapping
    feathers with a softer trailing edge."""
    d = unit(d); nrm = ortho(nrm, d); side = unit(cross(nrm, d))
    def surface(u, v):
        prof = clamp(u/.12)**.5*(1-clamp((u-tip)/(1-tip)))**(.75 if tip <= .5 else .55)
        across = (v-.5)*2
        k = 1+asym*(1 if across < 0 else -1)*.45
        off = across*W*.5*max(.08, prof)*k
        bend = -droop*u*u+.18*(1-across*across)*prof
        return add(root, add(mul(d, L*u), add(mul(side, off), mul(nrm, bend)))), nrm
    return shell(name, surface, 10, 4, .07)


def wing_frame(s):
    span1 = unit(sub(WING2[s], WING1[s]))
    back = unit((-1, 0, -.25))
    return back


def wing_normal(span, back):
    n = unit(cross(span, back))
    return n if n[2] > 0 else mul(n, -1)


def build_wing(parts, side, s):
    # Feathers hang back and down from the wing arm, so the gameplay (front) view
    # sees the wing surface rather than its leading edge.
    back = unit((-.62, 0, -1))
    arm = [(*WING1[s], .95), (*lerp(WING1[s], WING2[s], .5), .78), (*WING2[s], .62), (*lerp(WING2[s], WING3[s], .5), .5),
           (*WING3[s], .44), (*lerp(WING3[s], WTIP[s], .5), .32), (*WTIP[s], .16)]
    parts.append(tube('wing_arm_'+side, [r6(p[:3])+(p[3],) for p in arm], 12, 3))
    # Primaries fan from the hand in a tight, broad, overlapping fan: inner ones
    # trail back, outer ones continue the span.
    span3 = unit(sub(WTIP[s], WING3[s]))
    nrm3 = wing_normal(span3, back)
    for k in range(7):
        f = k/6
        root = lerp(WING3[s], WTIP[s], .1+.9*f)
        theta = math.radians(24+48*f**1.1)
        d = add(mul(ortho(back, span3), math.cos(theta)), mul(span3, math.sin(theta)))
        L = (9.4, 9.8, 10.1, 10.3, 10.1, 9.6, 8.8)[k]
        parts.append(vane(f'primary_{k}_'+side, r6(add(root, mul(nrm3, .07*k-.25))), d, nrm3, L, 4.2, .9, .3, .66))
    span2 = unit(sub(WING3[s], WING2[s]))
    nrm2 = wing_normal(span2, back)
    for k in range(6):
        f = k/5
        root = lerp(WING2[s], WING3[s], .05+.9*f)
        d = add(mul(ortho(back, span2), 1), mul(span2, .12+.12*f))
        parts.append(vane(f'secondary_{k}_'+side, r6(add(root, mul(nrm2, -.06*k-.1))), d, nrm2, 9.4-.25*k, 4.2, .7, .15, .64))
    span1 = unit(sub(WING2[s], WING1[s]))
    nrm1 = wing_normal(span1, back)
    for k, f in enumerate((.42, .68, .94)):
        root = lerp(WING1[s], WING2[s], f)
        d = add(mul(ortho(back, span1), 1), mul(span1, -.1+.1*k))
        parts.append(vane(f'tertial_{k}_'+side, r6(add(root, mul(nrm1, -.1-.05*k))), d, nrm1, 6.4+1.3*k, 3.6, .6, 0., .6))
    # Coverts overlap the feather roots along all three wing bones.
    for bone, a, b, n0, count, L in (('1', WING1[s], WING2[s], nrm1, 3, 3.6), ('2', WING2[s], WING3[s], nrm2, 5, 4.4),
                                      ('3', WING3[s], WTIP[s], nrm3, 3, 4.0)):
        span = unit(sub(b, a))
        for k in range(count):
            root = lerp(a, b, (k+.5)/count)
            d = add(ortho(back, span), mul(span, .35))
            parts.append(vane(f'covert_{bone}{k}_'+side, r6(add(root, mul(n0, .38))), d, n0, L, 2.8, .4, 0., .58))
    # Scapulars: overlapping feathers from the upper back and shoulder that sweep
    # out over the wing root, so the wing grows out of the body with no visible joint.
    span = unit(sub(WING2[s], WING1[s]))
    n0 = unit(add(nrm1, (-.8, 0, .2)))
    for k in range(5):
        f = k/4
        root = (round(-.9-1.0*f, 6), round(s*(.7+2.9*f), 6), round(38.6-.9*f, 6))
        d = add(mul(span, .75), mul(back, .55+.2*f))
        parts.append(vane(f'scapular_{k}_'+side, root, d, n0, 5.8-.5*f, 2.8, .25, 0., .55))


# Rows from a neck ruff down to a V point on the sternum; the back rows meet the scapulars.
MANTLE_ROWS = ((38.5, tuple(range(-160, 161, 20))), (37.0, (-55, -30, -8, 14, 36, 58, 125, 150, 180, 210, 235)),
               (35.5, tuple(range(-120, 121, 20))), (33.8, tuple(range(-90, 91, 18))), (32.1, tuple(range(-72, 73, 24))),
               (30.9, (-30, -10, 10, 30)))


def chest_surface(a, z):
    """Point and outward normal on the rest chest (with breasts) at azimuth a (degrees) and height z."""
    q = max(.05, 1-((z-33.9)/2.9)**2)
    rx, ry = max(1.2, 2.1*math.sqrt(q)), max(1.3, 3.2*math.sqrt(q))
    ar = math.radians(a)
    bust = .55*math.exp(-((abs(a)-24)/22)**2)*math.exp(-((z-33.6)/1.2)**2)
    p = (0.3+(rx+bust)*math.cos(ar), (ry+bust*.4)*math.sin(ar), z)
    return p, unit((math.cos(ar)/rx, math.sin(ar)/ry, .25))


def build_plumage(parts):
    # A feathered breast and mantle in overlapping rows, the back rows running into the wings.
    for r, (z, angles) in enumerate(MANTLE_ROWS):
        for k, a in enumerate(angles):
            p, out = chest_surface(a, z-(.7*math.exp(-(a/40)**2) if r >= 3 else 0))
            if z > 36.5: p = add(p, mul(out, -.3))
            d = unit(add((0, 0, -1), mul(out, .32)))
            L = (3.2, 3.4, 3.6, 3.3, 2.7, 2.4)[r]
            parts.append(vane(f'mantle_{r}{k:02d}', r6(add(p, mul(out, -.2))), d, out, L, 2.1, .05, 0., .55))
    for side, s in SIDES:
        # Ragged feathered hips: overlapping feathers hanging over each thigh.
        for k, ang in enumerate((-70, -30, 10, 50, 90, 130)):
            a = math.radians(ang)
            out = (math.cos(a), s*math.sin(a), 0)
            root = add((HIP[s][0], HIP[s][1]*.9, 26.4+.25*(k % 2)), mul(out, 1.45))
            d = add((.3, 0, -1), mul(out, .1))
            parts.append(vane(f'legfeather_{k}_'+side, r6(root), d, out, 7.2-.35*abs(k-2), 2.4, .1))
    for k, ang in enumerate((-30, -15, 0, 15, 30)):
        a = math.radians(ang)
        d = (-math.cos(a)*.75, math.sin(a)*.75, -.66)
        parts.append(vane(f'tailfeather_{k}', r6(add(TAILB, (0, math.sin(a)*.6, .3+.08*abs(ang)/15))), d, (-.6, 0, .8),
                          8.0-.5*abs(ang)/15, 2.4, .5))


def build_parts():
    parts = []
    build_body(parts)
    build_head(parts)
    build_hair(parts)
    build_hands_feet(parts)
    for side, s in SIDES:
        build_wing(parts, side, s)
    build_plumage(parts)
    return materials.repack(parts)


# ---------------------------------------------------------------- weights
TORSO = ('pelvis', 'spine', 'chest', 'neck')


def chain(v, names, k=.22):
    return sharp_chain(v, names, k, IDS, REST)


def raw_weights(part, v, uv):
    n = part.name
    side = n[-1]
    if n.startswith(('skin_cranium', 'skin_face', 'skin_chin', 'skin_nose', 'eye_', 'brow_', 'tooth_', 'hair_cap')):
        return [(IDS['head'], 1.)]
    if n.startswith('hair_lock'):
        t = materials.local_uv(n, uv)[0]
        a, b = smooth(t/.45), smooth((t-.45)/.5)
        out = [(IDS['head'], 1-a), (IDS['hair'], a*(1-b)), (IDS['hair2'], a*b)]
        return [x for x in out if x[1] > 1e-9]
    if n.startswith('skin_ear'):
        s = 1 if side == 'L' else -1
        d = sub(EAR_TIP[s], EAR[s])
        t = clamp(dot(sub(v, EAR[s]), d)/dot(d, d))
        w = smooth((t-.15)/.45)
        return [(IDS['head'], 1-w), (IDS['ear_'+side], w)] if w > 0 else [(IDS['head'], 1.)]
    if n == 'skin_neck':
        return chain(v, ('chest', 'neck', 'head'), .35)
    if n.startswith(('skin_chest', 'skin_breast', 'skin_belly', 'skin_pelvis', 'skin_trap')):
        return RIG.chain_weights(v, [IDS[b] for b in TORSO])
    if n.startswith('skin_shoulder'):
        return chain(v, ('chest', 'arm_'+side, 'forearm_'+side), .3)
    if n.startswith('skin_arm'):
        return chain(v, ('chest', 'arm_'+side, 'forearm_'+side, 'hand_'+side))
    if n.startswith(('skin_palm', 'thumb_', 'nail_thumb')):
        return [(IDS['hand_'+side], 1.)]
    if n.startswith(('finger_', 'nail_')):
        return [(IDS['claws_'+side], 1.)]
    if n.startswith('skin_leg'):
        return chain(v, ('pelvis', 'thigh_'+side, 'shin_'+side, 'foot_'+side))
    if n.startswith('skin_foot'):
        return chain(v, ('shin_'+side, 'foot_'+side, 'toes_'+side), .25)
    if n.startswith(('toe_', 'talon_')):
        return [(IDS['toes_'+side], 1.)]
    if n.startswith('scapular'):
        t = materials.local_uv(n, uv)[0]
        w = smooth((t-.1)/.6)
        return [(IDS['chest'], 1-w), (IDS['wing1_'+side], w)] if w > 0 else [(IDS['chest'], 1.)]
    if n.startswith('mantle'):
        return [(IDS['chest'], 1.)]
    if n.startswith('wing_arm'):
        return chain(v, ('wing1_'+side, 'wing2_'+side, 'wing3_'+side), .25)
    if n.startswith('primary') or n.startswith('covert_3'):
        return [(IDS['wing3_'+side], 1.)]
    if n.startswith('secondary') or n.startswith('covert_2'):
        return [(IDS['wing2_'+side], 1.)]
    if n.startswith(('tertial', 'covert_1')):
        return [(IDS['wing1_'+side], 1.)]
    if n.startswith('legfeather'):
        return [(IDS['thigh_'+side], 1.)]
    if n.startswith('tailfeather'):
        return [(IDS['tail'], 1.)]
    raise ValueError('No weights for '+n)


def weights(part, v, uv):
    return quantise(raw_weights(part, v, uv))


# ---------------------------------------------------------------- posing
IDENT = (0., 0., 0., 1.)


def curl(P, side, degrees):
    s = 1 if side == 'L' else -1
    e, n, w = hand_frame(s)
    P.turn('claws_'+side, cross(e, n), degrees)


def chest_point(P, p):
    loc, q = P.world()[IDS['chest']]
    return add(loc, rotate(q, sub(p, REST[IDS['chest']])))


def wings(P, up, sweep=0., fold=0., hand=0., twist=0.):
    """up: flap elevation at the shoulder; sweep: backward about Z; fold: elbow
    and wrist bend (upstroke tuck); hand: extra wrist flick; twist: feather pitch."""
    for side, s in SIDES:
        P.turn('wing1_'+side, (1, 0, 0), s*up)
        P.turn('wing1_'+side, (0, 0, 1), s*sweep)
        P.turn('wing1_'+side, (0, 1, 0), twist)
        P.turn('wing2_'+side, (1, 0, 0), -s*fold)
        P.turn('wing2_'+side, (0, 0, 1), s*fold*.5)
        P.turn('wing3_'+side, (1, 0, 0), -s*(fold*.8+hand))
        P.turn('wing3_'+side, (0, 0, 1), s*fold*.6)


def beat_wings(P, beat, amp=36., lift=14., sweep=0., tuck=34.):
    up = lift+amp*math.sin(beat)
    fold = tuck*max(0., math.cos(beat))**1.5
    wings(P, up, sweep+6*math.cos(beat), fold, -14*math.sin(beat+.6), 8*math.cos(beat))


def legs(P, a_thigh, a_shin, a_foot, a_toes, spread=0.):
    for side, s in SIDES:
        P.turn('thigh_'+side, (0, 1, 0), -a_thigh)
        P.turn('thigh_'+side, (1, 0, 0), s*spread)
        P.turn('shin_'+side, (0, 1, 0), a_shin)
        P.turn('foot_'+side, (0, 1, 0), -a_foot)
        P.turn('toes_'+side, (0, 1, 0), a_toes)


def ready(P, a, ph=0.):
    """Shared hovering carry: clawed hands raised before the chest, legs tucked."""
    if a <= 0: return
    for side, s in SIDES:
        # Claws raised to the shoulders, palms forward: a menacing, open-handed threat.
        target = chest_point(P, (3.4, s*7.2, 35.2+.4*math.sin(ph+s)))
        P.reach('arm_'+side, 'forearm_'+side, WRIST[s], target, (-.4, s*1, -.9), a)
        loc, q = P.world()[IDS['forearm_'+side]]
        P.aim('hand_'+side, knuckle(s), unit(lerp(rotate(q, sub(knuckle(s), WRIST[s])), (.25, s*.35, 1), a)))
        curl(P, side, 22*a)
    legs(P, 22*a, 18*a, 10*a, 24*a, 4*a)


def idle_pose(t):
    P = P_()
    ph = TAU*t
    beat = TAU*2*t+math.pi+.35   # frame 0 (all turnaround views) shows the wings spread
    P.shift[0] = (.4*math.cos(ph), .5*math.sin(ph+.4), 1.1*math.sin(beat+2.3))
    P.turn('pelvis', (0, 1, 0), 4)
    P.turn('chest', (0, 1, 0), 3*math.sin(beat+2.6))
    P.turn('neck', (0, 1, 0), -6)
    P.turn('head', (0, 0, 1), 14*math.cos(ph)-4)
    P.turn('head', (1, 0, 0), 6*math.sin(ph+1))
    ready(P, 1., beat)
    for side, s in SIDES:
        curl(P, side, 14*math.sin(TAU*3*t+s))
        P.turn('thigh_'+side, (0, 1, 0), -6*math.sin(beat+s))
        P.turn('toes_'+side, (0, 1, 0), 10*math.sin(beat+1.5))
    P.turn('hair', (0, 1, 0), 8*math.sin(beat+1.2))
    P.turn('hair', (1, 0, 0), 5*math.sin(ph))
    P.turn('hair2', (0, 1, 0), 12*math.sin(beat+.2))
    P.turn('tail', (0, 1, 0), 8*math.sin(beat+1.6))
    beat_wings(P, beat, 38, 16)
    return P


def fly_pose(t):
    P = P_()
    ph = TAU*t
    beat = TAU*2*t
    q = axis((0, 1, 0), math.radians(34))
    P.place_root(q, PELVIS, add(PELVIS, (1.0+.6*math.cos(ph), .6*math.sin(ph), -1.5+1.2*math.sin(beat+2.3)+.8*math.cos(ph))))
    P.turn('neck', (0, 1, 0), -24)
    P.turn('pelvis', (1, 0, 0), 7*math.cos(ph))
    P.turn('head', (0, 0, 1), 10*math.cos(ph))
    P.turn('head', (0, 1, 0), -14)
    for side, s in SIDES:
        P.turn('arm_'+side, (0, 1, 0), 40+6*math.sin(beat))
        P.turn('arm_'+side, (1, 0, 0), s*-10)
        P.turn('forearm_'+side, (0, 1, 0), 18)
        curl(P, side, 30)
    legs(P, -34+4*math.sin(beat)+6*math.cos(ph), 40-8*math.cos(ph), 22, 30, 3)
    P.turn('hair', (0, 1, 0), -38+6*math.sin(beat))
    P.turn('hair2', (0, 1, 0), -20+10*math.sin(beat+.5))
    P.turn('tail', (0, 1, 0), -20)
    beat_wings(P, beat, 44, 14, 8, 30)
    return P


def drub_pose(t):
    """Attack ("drubs"): rear up with wings high, then a diving strike whose middle
    frame drives both talons and both clawed hands forward under raised wings."""
    P = P_()
    rear = window(t, .04, .3)*(1-window(t, .34, .44))
    dive = window(t, .34, .44)*(1-window(t, .64, .95))
    rest = 1-max(rear, dive)
    q = axis((0, 1, 0), math.radians(-22*rear+30*dive))
    P.place_root(q, PELVIS, add(PELVIS, (-2.0*rear+5.0*dive, 0, 2.2*rear-1.8*dive)))
    P.turn('neck', (0, 1, 0), 8*rear-18*dive)
    P.turn('head', (0, 1, 0), 10*rear-16*dive)
    ready(P, rest, 0)
    for side, s in SIDES:
        high = chest_point(P, (-.5, s*6.0, 44.0))
        rake = chest_point(P, (13.0, s*4.2, 27.0))
        amount = rear+dive
        if amount > 1e-6:
            P.reach('arm_'+side, 'forearm_'+side, WRIST[s], lerp(high, rake, dive/amount), (-1, s*.6, -.2), min(1., amount))
            loc, fq = P.world()[IDS['forearm_'+side]]
            P.aim('hand_'+side, knuckle(s), rotate(fq, sub(knuckle(s), WRIST[s])), min(1., amount))
        curl(P, side, 35*rest+20*rear-30*dive)
    # Legs: drawn up under the body, then thrust forward, talons open.
    legs(P, 22*rest+60*rear+84*dive, 18*rest+80*rear+10*dive, 10*rest+20*rear-30*dive, 24*rest+40*rear-40*dive, 4+6*dive)
    P.turn('hair', (0, 1, 0), 20*rear-30*dive)
    P.turn('hair2', (0, 1, 0), -24*dive)
    P.turn('tail', (0, 1, 0), 10*rear-25*dive)
    beat = TAU*1.5*t
    base = 16+38*math.sin(TAU*t*0)
    up = (16+30*math.sin(beat))*rest+62*rear+70*dive
    wings(P, up, 20*dive-6*rear, 10*rest+6*rear, -8*dive, 0)
    return P


def lash_pose(t):
    """Alternate attack ("flagellates", "castigates"): the wings swing back, then
    whip forward around the prey in a loud buffet while a clawed hand lashes down."""
    P = P_()
    wind = window(t, .04, .3)*(1-window(t, .34, .44))
    whip = window(t, .34, .44)*(1-window(t, .64, .95))
    rest = 1-max(wind, whip)
    q = qmul(axis((0, 0, 1), math.radians(-20*wind+18*whip)), axis((0, 1, 0), math.radians(-10*wind+18*whip)))
    P.place_root(q, PELVIS, add(PELVIS, (-1.6*wind+3.0*whip, 0, 1.6*wind+.6*whip)))
    P.turn('neck', (0, 1, 0), -14*whip)
    P.turn('head', (0, 1, 0), -10*whip)
    P.turn('head', (1, 0, 0), 8*whip)
    ready(P, rest, 0)
    over = chest_point(P, (-1.0, -5.0, 46.0))
    down = chest_point(P, (11.0, -3.0, 26.0))
    amount = wind+whip
    if amount > 1e-6:
        P.reach('arm_R', 'forearm_R', WRIST[-1], lerp(over, down, whip/amount), (-1, -.5, .3), min(1., amount))
        P.reach('arm_L', 'forearm_L', WRIST[1], lerp(chest_point(P, (-3, 7.5, 32)), chest_point(P, (4.2, 5.6, 30)), whip/amount),
                (-1, .6, -.3), min(1., amount))
    curl(P, 'R', 35*rest-20*wind+50*whip)
    curl(P, 'L', 35*rest+10*whip)
    legs(P, 22*rest+10*wind-6*whip, 18*rest+20*wind+30*whip, 10*rest, 24*rest+30*whip, 4)
    P.turn('hair', (0, 1, 0), 18*wind-28*whip)
    P.turn('hair', (1, 0, 0), -14*whip)
    P.turn('hair2', (0, 1, 0), -20*whip)
    beat = TAU*1.5*t
    up = (16+30*math.sin(beat))*rest+40*wind+2*whip
    wings(P, up, 34*wind-78*whip, 6*rest+10*wind+18*whip, -14*whip, 0)
    return P


def recoil_pose(t):
    P = P_()
    p = math.sin(math.pi*t)**1.3
    shake = math.sin(TAU*2.5*t)*math.sin(math.pi*t)
    q = qmul(axis((1, 0, 0), math.radians(10*shake)), axis((0, 1, 0), math.radians(-26*p)))
    P.place_root(q, PELVIS, add(PELVIS, (-3.0*p, .5*shake, 1.2*p)))
    ready(P, 1-min(1, 1.4*p))
    P.turn('chest', (0, 1, 0), -10*p)
    P.turn('head', (0, 1, 0), -20*p)
    P.turn('head', (0, 0, 1), 18*shake)
    for side, s in SIDES:
        guard = chest_point(P, (3.6, s*3.0, 40.0))
        P.reach('arm_'+side, 'forearm_'+side, WRIST[s], guard, (-.3, s, -.8), min(1., 1.4*p))
        curl(P, side, 50*p)
    legs(P, 50*p, 30*p, -10*p, 30*p, 6*p)
    P.turn('hair', (0, 1, 0), 30*p)
    P.turn('hair2', (0, 1, 0), 20*p)
    wings(P, 16+54*p, -16*p, 30*p, 18*p, 0)
    return P


# Death: convulse, crumple, fall and land prone with the wings splayed on the floor.
PRONE_Q = axis((0, 1, 0), math.radians(90))
PRONE_PELVIS = (-6.0, .4, 3.35)
_FINAL = []


def prone_final():
    if _FINAL: return _FINAL[0]
    P = P_()
    P.place_root(qmul(axis((1, 0, 0), math.radians(5)), PRONE_Q), PELVIS, PRONE_PELVIS)
    P.turn('spine', (0, 1, 0), -20)
    P.turn('chest', (0, 1, 0), -6)
    # Head down on its cheek (angles from a floor-contact search).
    P.turn('neck', (0, 1, 0), 46); P.turn('neck', (1, 0, 0), 15)
    P.turn('head', (0, 1, 0), 24)
    P.turn('head', (0, 0, 1), -50)
    # Hair spills sideways across the floor (angles found by a floor-contact search).
    P.turn('hair', (0, 1, 0), 40); P.turn('hair', (1, 0, 0), 120); P.turn('hair2', (1, 0, 0), 30)
    P.aim('arm_L', ELBOW[1], (.6, .72, -.42)); P.aim('forearm_L', WRIST[1], (.9, .42, -.2)); P.aim('hand_L', knuckle(1), (.95, .2, .12))
    P.aim('arm_R', ELBOW[-1], (.2, -.92, -.42)); P.aim('forearm_R', WRIST[-1], (.75, -.64, -.2)); P.aim('hand_R', knuckle(-1), (.88, -.4, .24))
    curl(P, 'L', 18); curl(P, 'R', 12)
    P.aim('thigh_L', KNEE[1], (-.97, .22, .04)); P.aim('shin_L', HOCK[1], (-.97, .12, .08)); P.aim('foot_L', BALL[1], (-.9, .25, .3))
    P.aim('thigh_R', KNEE[-1], (-.93, -.34, .04)); P.aim('shin_R', HOCK[-1], (-.96, -.25, .06)); P.aim('foot_R', BALL[-1], (-.85, -.35, .35))
    P.aim('toes_L', (2.6, 2.7, 9.2), (-.6, .3, .75)); P.aim('toes_R', (2.6, -2.7, 9.2), (-.5, -.3, .8))
    P.aim('tail', (-5.6, 0, 20.0), (-.9, 0, -.15))
    for side, s in SIDES:
        P.aim('wing1_'+side, WING2[s], (-.2, s*.9, -.5))
        P.aim('wing2_'+side, WING3[s], (-.45*(1 if s > 0 else .3), s*.9, -.26))
        P.aim('wing3_'+side, WTIP[s], (-.6*(1 if s > 0 else .2), s*.8, -.1))
    _FINAL.append(P.rot[:])
    return P.rot


PROBES = None


def probes():
    global PROBES
    if PROBES is None:
        pts = []
        for side, s in SIDES:
            e, n, w = hand_frame(s)
            pts += [('claws_'+side, add(knuckle(s), add(mul(e, 3.6), mul(n, 1.8)))), ('toes_'+side, add(BALL[s], (3.3, 0, -2.2))),
                    ('toes_'+side, add(BALL[s], (-2.4, 0, -2.2))), ('wing3_'+side, add(WTIP[s], (-4, s*8, -3))),
                    ('wing3_'+side, add(WTIP[s], (-8, s*2, -3))), ('wing2_'+side, add(WING3[s], (-8.5, 0, -3)))]
        pts += [('head', (3.2, 0, 40)), ('hair2', (-5.6, 0, 34)), ('tail', (-7.5, 0, 20.5))]
        PROBES = pts
    return PROBES


def ground_guard(P, amount, floor=.6):
    if amount <= 0: return
    low = min(P.point(b, p)[2] for b, p in probes())
    if low < floor:
        P.shift[0] = add(P.shift[0], (0, 0, (floor-low)*amount))


def death_pose(t):
    P = P_()
    jolt = window(t, 0, .07)*(1-window(t, .1, .2))
    u = clamp((t-.12)/.56)
    fall = smooth(u)
    drop = u**1.6
    settle = window(t, .62, .9)
    bounce = .8*math.sin(math.pi*clamp((t-.68)/.14))*(1-settle)
    q = slerp(axis((0, 1, 0), math.radians(-18*jolt)), qmul(axis((1, 0, 0), math.radians(5)), PRONE_Q), fall)
    target = add(lerp(lerp(PELVIS, (3.0, .3, 22.0), smooth(u*1.8)), PRONE_PELVIS, drop), (0, 0, bounce))
    P.place_root(q, PELVIS, target)
    ready(P, 1-window(t, 0, .1))
    P.turn('chest', (0, 1, 0), -18*jolt)
    P.turn('head', (0, 1, 0), -30*jolt)
    for side, s in SIDES:
        P.turn('arm_'+side, (1, 0, 0), s*-60*jolt)
        P.turn('arm_'+side, (0, 1, 0), -40*math.sin(math.pi*u))
        curl(P, side, -30*jolt)
    legs(P, 30*math.sin(math.pi*u), 40*math.sin(math.pi*u), 0, -20*jolt, 0)
    # Wings: snap up in the spasm, then fail and trail upward as the body drops.
    wings(P, 70*jolt+60*math.sin(math.pi*u)*(1-fall*.5), -20*math.sin(math.pi*u), 40*math.sin(math.pi*u), 20*math.sin(math.pi*u), 0)
    P.turn('hair', (0, 1, 0), 30*math.sin(math.pi*u))
    final = prone_final()
    limp = smooth(clamp((t-.34)/.4))*.75+settle*.25
    for i in range(1, len(BONES)):
        P.rot[i] = slerp(P.rot[i], final[i], limp)
    ground_guard(P, 1-window(t, .8, .97), .4)
    return P


def pose(name, t):
    fn = {'idle': idle_pose, 'fly': fly_pose, 'drub': drub_pose, 'lash': lash_pose,
          'recoil': recoil_pose, 'death': death_pose}[name]
    return fn(t).frame()


# ---------------------------------------------------------------- export
def geometry():
    from .connected_skin import attach
    parts = attach('fury', build_parts(), weights)
    return assemble(materials.connected_atlas(parts), weights)


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from .connected_skin import attach
    return materials.connected_atlas(attach('fury', build_parts(), weights), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_fury', material_path=SKIN)
    path = ROOT/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M46', format='IQM v2', runtimeModel=MODEL,
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/fury/fury-animated.blend')
    out = ROOT/'assets/monsters/fury'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Re-import under the package name so connected_skin finds CONNECTED_SKIN.
    import importlib
    print(importlib.import_module('tools.monster_models.fury_animation').build()['sha256'])
