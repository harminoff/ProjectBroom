"""Original connected pixie, six purely cosmetic skeletal roles. No gameplay.

A tiny androgynous winged humanoid (Brogue gives either pronoun) with an
enlarged heart-shaped head, long swept ears, large lidded eyes, spiky pale hair,
a painted petal bodice, a flared petal skirt, a half collar, a vine belt with a
dust pouch and four insect-like membrane wings. +X forward, Z up, +Y left.

Flight, flitting, bolts, statuses, light and every outcome belong to Brogue.
The spell gesture is only a pose: nothing here spawns projectiles, particles,
lights or sparkles. The rest mesh keeps the documented 16-unit flight gap.
"""
import hashlib
import json
import math

from . import iqm, pixie_materials as materials
from .rat import ROOT, Part, add, sub, mul, unit, cross
from .skeletal import Rig, axis, qmul, inverse, rotate, between, assemble, sample_clips

SKIN = materials.SKIN
TAU = math.tau
SIDES = (('L', 1), ('R', -1))


def dot(a, b): return sum(x*y for x, y in zip(a, b))
def clamp(v, lo=0., hi=1.): return max(lo, min(hi, v))
def smooth(x): x = clamp(x); return x*x*(3-2*x)
def window(t, a, b): return smooth((t-a)/(b-a))
def lerp(a, b, t): return tuple(x+(y-x)*t for x, y in zip(a, b))
def r6(p): return tuple(round(c, 6) for c in p)


def ortho(v, n):
    """Unit component of v perpendicular to unit n."""
    return unit(sub(v, mul(n, dot(v, n))))


# ---------------------------------------------------------------- skeleton
SHOULDER = {s: (0.0, s*3.0, 35.3) for _, s in SIDES}
ELBOW = {s: (0.5, s*5.2, 31.4) for _, s in SIDES}
WRIST = {s: (1.3, s*6.5, 28.0) for _, s in SIDES}
HIP = {s: (0.0, s*1.6, 29.4) for _, s in SIDES}
KNEE = {s: (0.75, s*1.75, 24.0) for _, s in SIDES}
ANKLE = {s: (0.05, s*1.85, 19.3) for _, s in SIDES}
WING_F = {s: (-1.25, s*0.75, 35.0) for _, s in SIDES}
WING_H = {s: (-1.2, s*0.7, 33.2) for _, s in SIDES}
EAR = {s: (-0.3, s*2.75, 41.25) for _, s in SIDES}
EAR_TIP = {s: (-2.3, s*6.3, 44.3) for _, s in SIDES}


def hand_frame(s):
    """Forearm axis e, palm normal n (facing the body) and knuckle axis w (forward)."""
    e = unit(sub(WRIST[s], ELBOW[s]))
    n = ortho((0, -s, 0), e)
    w = unit(cross(n, e))
    if w[0] < 0: w = mul(w, -1)
    return e, n, w


def knuckle(s):
    e, n, w = hand_frame(s)
    return r6(add(WRIST[s], mul(e, 1.15)))


SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 29.8)), ('spine', 'pelvis', (0, 0, 31.6)),
         ('chest', 'spine', (0.1, 0, 34.0)), ('neck', 'chest', (0.1, 0, 36.2)), ('head', 'neck', (0.3, 0, 38.6)),
         ('hair', 'head', (-0.5, 0, 44.6))]
for side, s in SIDES:
    SPECS.append(('ear_'+side, 'head', EAR[s]))
SPECS += [('skirt_F', 'pelvis', (1.75, 0, 30.8)), ('skirt_B', 'pelvis', (-1.75, 0, 30.8)),
          ('skirt_L', 'pelvis', (0, 2.3, 30.8)), ('skirt_R', 'pelvis', (0, -2.3, 30.8))]
for side, s in SIDES:
    SPECS += [('arm_'+side, 'chest', SHOULDER[s]), ('forearm_'+side, 'arm_'+side, ELBOW[s]),
              ('hand_'+side, 'forearm_'+side, WRIST[s]), ('index_'+side, 'hand_'+side, knuckle(s)),
              ('fingers_'+side, 'hand_'+side, knuckle(s)),
              ('thigh_'+side, 'pelvis', HIP[s]), ('shin_'+side, 'thigh_'+side, KNEE[s]),
              ('foot_'+side, 'shin_'+side, ANKLE[s]),
              ('wingF_'+side, 'chest', WING_F[s]), ('wingH_'+side, 'chest', WING_H[s])]
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, _, _) in enumerate(BONES)}
CLIPS = [('idle', 48, 24, True), ('flit', 24, 30, True), ('poke', 24, 35, False),
         ('hex', 30, 35, False), ('flinch', 16, 35, False), ('fall', 40, 35, False)]


# ---------------------------------------------------------------- primitives
def blob(name, center, a0, a1, radii, seg=24, rings=16, taper=None, start=None):
    """Ellipsoid with poles along a0; a1/a2 span the equator; local UV (theta, latitude).

    taper(xi) scales the equatorial radii at normalised pole coordinate xi in -1..1.
    """
    a0 = unit(a0); a1 = ortho(a1, a0); a2 = cross(a0, a1)
    p = start or Part(name)
    base = len(p.vertices)
    def point(phi, theta):
        xi = math.sin(phi)
        k = taper(xi) if taper else 1.
        co = add(center, add(mul(a0, radii[0]*xi), add(mul(a1, radii[1]*math.cos(phi)*math.cos(theta)*k),
                                                       mul(a2, radii[2]*math.cos(phi)*math.sin(theta)*k))))
        return r6(co)
    p.vertices.append(point(-math.pi/2, 0)); p.uv.append((.5, 0.))
    for i in range(1, rings):
        phi = -math.pi/2+math.pi*i/rings
        for j in range(seg+1):
            p.vertices.append(point(phi, TAU*j/seg)); p.uv.append((j/seg, i/rings))
    p.vertices.append(point(math.pi/2, 0)); p.uv.append((.5, 1.))
    bottom, top = base, len(p.vertices)-1
    for j in range(seg):
        p.faces.append((bottom, base+1+j+1, base+1+j))
    for i in range(rings-2):
        for j in range(seg):
            a = base+1+i*(seg+1)+j
            p.faces.append((a, a+1, a+seg+2, a+seg+1))
    last = base+1+(rings-2)*(seg+1)
    for j in range(seg):
        p.faces.append((last+j, last+j+1, top))
    return p


def tube(name, controls, sides=12, samples=3):
    """Parallel-transported swept tube with local UV (along, around); x/y/z/radius rows."""
    from .rat import spline
    p = Part(name)
    rows = spline(controls, samples)
    previous = None
    for i, row in enumerate(rows):
        c, radius = row[:3], max(.012, row[3])
        tangent = unit(sub(rows[min(i+1, len(rows)-1)][:3], rows[max(0, i-1)][:3]))
        if previous is None:
            n = unit(cross(tangent, (0, 0, 1) if abs(tangent[2]) < .9 else (0, 1, 0)))
        else:
            n = ortho(previous, tangent)
        previous = n
        b = unit(cross(tangent, n))
        for j in range(sides+1):
            angle = TAU*j/sides
            p.vertices.append(r6(add(c, add(mul(n, radius*math.cos(angle)), mul(b, radius*math.sin(angle))))))
            p.uv.append((i/(len(rows)-1), j/sides))
    for i in range(len(rows)-1):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+1, a+sides+2, a+sides+1))
    for end, reverse in ((0, True), (len(rows)-1, False)):
        p.vertices.append(r6(rows[end][:3])); p.uv.append((end/(len(rows)-1), .5))
        center = len(p.vertices)-1
        for j in range(sides):
            a = end*(sides+1)+j
            p.faces.append((center, a+1, a) if reverse else (center, a, a+1))
    return p


def shell(name, surface, nu, nv, thickness):
    """Closed thin double-sided sheet. surface(u,v) -> (point, outward normal).

    The front sheet faces the given normal; the back sheet sits `thickness`
    behind it; a rim closes the boundary. UV is the sheet parameter.
    """
    p = Part(name)
    grid = [[surface(i/nu, j/nv) for j in range(nv+1)] for i in range(nu+1)]
    for side in (0, 1):
        for i in range(nu+1):
            for j in range(nv+1):
                point, normal = grid[i][j]
                p.vertices.append(r6(point if side == 0 else sub(point, mul(normal, thickness))))
                p.uv.append((i/nu, j/nv))
    stride = (nu+1)*(nv+1)
    def idx(side, i, j): return side*stride+i*(nv+1)+j
    def oriented(face, hint):
        a, b, c = (p.vertices[k] for k in face[:3])
        n = cross(sub(b, a), sub(c, a))
        if dot(n, n) < 1e-14 and len(face) == 4:
            a, c, d = (p.vertices[k] for k in (face[0], face[2], face[3]))
            n = cross(sub(c, a), sub(d, a))
        return face if dot(n, hint) >= 0 else tuple(reversed(face))
    for side in (0, 1):
        for i in range(nu):
            for j in range(nv):
                face = (idx(side, i, j), idx(side, i+1, j), idx(side, i+1, j+1), idx(side, i, j+1))
                normal = grid[i][j][1] if side == 0 else mul(grid[i][j][1], -1)
                p.faces.append(oriented(face, normal))
    # Rim: outward hint is the in-sheet direction leaving the boundary.
    for i in range(nu):
        for j, inner in ((0, 1), (nv, nv-1)):
            hint = sub(grid[i][j][0], grid[i][inner][0])
            p.faces.append(oriented((idx(0, i, j), idx(0, i+1, j), idx(1, i+1, j), idx(1, i, j)), hint))
    for j in range(nv):
        for i, inner in ((0, 1), (nu, nu-1)):
            hint = sub(grid[i][j][0], grid[inner][j][0])
            p.faces.append(oriented((idx(0, i, j), idx(0, i, j+1), idx(1, i, j+1), idx(1, i, j)), hint))
    return p


# ---------------------------------------------------------------- anatomy
HEAD_C, HEAD_R = (-0.2, 0, 41.6), (3.3, 3.15, 3.45)
FACE_C, FACE_R = (0.8, 0, 40.0), (2.2, 2.55, 2.3)
CHIN_C, CHIN_R = (1.85, 0, 38.35), (1.0, 1.05, 0.85)
CAP_C, CAP_R = (-0.55, 0, 42.2), (3.36, 3.32, 3.25)


def head_surface_x(y, z):
    """Frontmost rest skin X of the cranium/face ellipsoids at (y, z)."""
    best = -9.
    for c, r in ((HEAD_C, HEAD_R), (FACE_C, FACE_R), (CHIN_C, CHIN_R)):
        q = 1-((y-c[1])/r[1])**2-((z-c[2])/r[2])**2
        if q > 0: best = max(best, c[0]+r[0]*math.sqrt(q))
    return best


def eye_frame(s):
    f = unit((math.cos(math.radians(21)), s*math.sin(math.radians(21)), .06))
    up = ortho((0, 0, 1), f)
    lateral = cross(up, f)  # points outward for the left eye, inward-negative handled by s
    if dot(lateral, (0, s, 0)) < 0: lateral = mul(lateral, -1)
    surface = (head_surface_x(s*1.5, 41.0), s*1.5, 41.0)
    center = sub(surface, mul(f, .3))
    return center, f, up, lateral


EYE_R = (.64, .86, .95)   # depth, vertical, lateral


def build_face(parts):
    for side, s in SIDES:
        c, f, up, lat = eye_frame(s)
        parts.append(blob('eye_'+side, c, f, up, EYE_R, 28, 18))
        # Upper lid: a skin shell over the top third of the eyeball, tilted up at
        # the outer corner (an upswept, sly almond); the lash line rides its rim.
        tilt = axis(f, math.radians(-9*s))
        lid_up = rotate(tilt, up)
        lid_c = add(c, add(mul(lid_up, .82), mul(f, .03)))
        parts.append(blob('lid_'+side, lid_c, f, lid_up, (.7, .54, 1.05), 24, 14))
        lash = []
        for k in range(-7, 8):
            l = k/7*.97
            h = .86
            for step in range(172):
                hh = -.86+step*.01
                qe = 1-(l/EYE_R[2])**2-(hh/EYE_R[1])**2
                if qe <= 0: continue
                de = EYE_R[0]*math.sqrt(qe)
                # lid local coordinates
                off = sub(add(mul(lat, l), mul(up, hh)), sub(lid_c, c))
                ll, lh, ld = dot(off, lat), dot(off, lid_up), dot(off, f)+de
                ql = 1-(ll/1.05)**2-(lh/.54)**2-(ld/.7)**2
                if ql >= 0: h = hh; break
            qe = max(0., 1-(l/EYE_R[2])**2-(h/EYE_R[1])**2)
            de = EYE_R[0]*math.sqrt(qe)+.05
            radius = .13*(1-.55*abs(k/7)**3)
            lash.append((*add(c, add(mul(lat, l), add(mul(up, h), mul(f, de)))), radius))
        # Outer flick: the lash line sweeps up and back past the corner.
        tip = lash[-1][:3] if s > 0 else lash[0][:3]
        flick = [(*add(tip, add(mul(lat, .28), add(mul(up, .16), mul(f, -.12)))), .09),
                 (*add(tip, add(mul(lat, .55), add(mul(up, .38), mul(f, -.3)))), .03)]
        lash = lash+flick if s > 0 else list(reversed(flick))+lash
        parts.append(tube('lash_'+side, [r6(x[:3])+(round(x[3], 6),) for x in lash], 8, 2))
        # Brows: the left one arched high, the right one lower and angled: mischief.
        raise_ = .32 if s > 0 else 0.
        brow = []
        for k, (y, z, r) in enumerate(((.55, 42.35, .15), (1.1, 42.72, .17), (1.75, 42.98, .15), (2.35, 43.02, .09))):
            z += raise_*math.sin(math.pi*k/3) if s > 0 else -.05*k
            x = head_surface_x(y, z)+.06
            brow.append((x, s*y, z, r))
        parts.append(tube('brow_'+side, brow, 8, 3))


def cap_point(az, el, lift=0.):
    a, e = math.radians(az), math.radians(el)
    d = (math.cos(e)*math.cos(a), math.cos(e)*math.sin(a), math.sin(e))
    k = 1+lift/3.3
    return add(CAP_C, (CAP_R[0]*d[0]*k, CAP_R[1]*d[1]*k, CAP_R[2]*d[2]*k))


# Tousled pixie cut: (azimuth, elevation, azimuth drift, elevation drift, end lift, root radius).
# Locks follow the scalp and rise off it; nape locks stay low so a lying head rests on its cap.
LOCKS = [(0, 52, 6, 44, 2.3, .7), (24, 48, 14, 40, 2.1, .66), (-22, 50, -12, 42, 2.2, .66),
         (48, 40, 30, 34, 1.9, .62), (-50, 42, -30, 34, 2.0, .62), (78, 30, 40, 22, 1.5, .58),
         (-80, 30, -40, 22, 1.6, .58), (104, 24, 40, 12, 1.3, .55), (-106, 24, -40, 12, 1.3, .55),
         (12, 74, 10, 40, 2.4, .66), (-14, 76, -10, 38, 2.3, .66), (40, 66, 26, 36, 2.0, .6),
         (-42, 68, -26, 36, 2.0, .6), (70, 56, 36, 30, 1.7, .56), (-72, 58, -36, 30, 1.7, .56),
         (150, 40, 14, -26, .5, .48), (-150, 40, -14, -26, .5, .48), (180, 46, 0, -30, .45, .5),
         (128, 34, 24, -18, .6, .46), (-128, 34, -24, -18, .6, .46), (164, 70, 8, -24, .9, .5), (-164, 70, -8, -24, .9, .5),
         (140, 58, 18, -34, .45, .52), (-140, 58, -18, -34, .45, .52), (196, 56, 10, -34, .4, .5), (166, 30, 4, -22, .35, .44),
         (-166, 30, -4, -22, .35, .44), (112, 50, 26, -26, .55, .5), (-112, 50, -26, -26, .55, .5)]


def build_hair(parts):
    parts.append(blob('hair_cap', CAP_C, (0, 0, 1), (1, 0, 0), (CAP_R[2], CAP_R[0], CAP_R[1]), 32, 20))
    for k, (az, el, daz, dele, lift, radius) in enumerate(LOCKS):
        pts = []
        for i, (f, r) in enumerate(((0, 1.), (.3, .92), (.6, .7), (.85, .42), (1., .08))):
            flick = lift*(f**1.6)
            pts.append((*r6(cap_point(az+daz*f, el+dele*f, -.35+.35*min(1, f*4)+flick)), round(radius*r, 6)))
        parts.append(tube(f'hair_lock_{k}', pts, 9, 3))
    # A side-swept fringe: three locks crossing the forehead toward the pixie's right.
    for k, (y0, z0, dy, dz, radius) in enumerate(((.9, 44.2, -2.4, -.8, .5), (.2, 44.4, -1.9, -.5, .46), (1.6, 43.9, -1.9, -.9, .4))):
        pts = []
        for i, f in enumerate((0, .35, .7, 1.)):
            y, z = y0+dy*f, z0+dz*f
            pts.append((round(head_surface_x(y, z)+.05+.28*min(1, f*3), 6), round(y, 6), round(z, 6),
                        round(radius*(1-.8*f**1.5), 6)))
        pts[0] = (round(pts[0][0]-.45, 6),)+pts[0][1:]
        parts.append(tube(f'hair_fringe_{k}', pts, 9, 3))


def ear(s):
    base, tip = EAR[s], EAR_TIP[s]
    a0 = unit(sub(tip, base))
    facing = ortho((1, s*.35, 0), a0)
    width = cross(facing, a0)
    center = lerp(base, tip, .5)
    half = math.dist(base, tip)/2+.3
    return blob('skin_ear_'+('L' if s > 0 else 'R'), center, a0, width, (half, 1.05, .34), 20, 18,
                taper=lambda xi: .22+.78*clamp((1-xi)/1.25)**.8)


def build_body(parts):
    parts.append(blob('skin_cranium', HEAD_C, (0, 0, 1), (1, 0, 0), (HEAD_R[2], HEAD_R[0], HEAD_R[1]), 36, 24))
    parts.append(blob('skin_face', FACE_C, (0, 0, 1), (1, 0, 0), (FACE_R[2], FACE_R[0], FACE_R[1]), 32, 20))
    parts.append(blob('skin_chin', CHIN_C, (0, 0, 1), (1, 0, 0), (CHIN_R[2], CHIN_R[0], CHIN_R[1]), 24, 14))
    nose_x = head_surface_x(0, 40.55)
    parts.append(blob('skin_nose', (nose_x-.05, 0, 40.55), (.55, 0, -.83), (0, 1, 0), (.5, .34, .4), 18, 12))
    for side, s in SIDES:
        parts.append(ear(s))
    parts.append(tube('skin_neck', [(0.1, 0, 35.2, 1.05), (0.2, 0, 36.9, .9), (0.45, 0, 38.6, .95)], 20, 3))
    parts.append(blob('skin_pelvis', (0, 0, 29.9), (0, 0, 1), (1, 0, 0), (1.7, 1.75, 2.3), 32, 20))
    parts.append(blob('skin_belly', (0.15, 0, 31.7), (0, 0, 1), (1, 0, 0), (1.6, 1.5, 1.85), 32, 20))
    parts.append(blob('skin_chest', (0.15, 0, 34.2), (0, 0, 1), (1, 0, 0), (1.95, 1.7, 2.4), 32, 20))
    for side, s in SIDES:
        parts.append(blob('skin_shoulder_'+side, (0, s*2.72, 35.25), (0, 0, 1), (1, 0, 0), (.95, 1.0, 1.05), 20, 14))
        parts.append(blob('skin_trapezius_'+side, (-0.25, s*1.55, 35.65), (0, 0, 1), (1, 0, 0), (.75, .95, 1.3), 20, 14))
        sh, el, wr = SHOULDER[s], ELBOW[s], WRIST[s]
        parts.append(tube('skin_arm_'+side, [(-0.05, s*2.4, 35.5, .86), (*sh, .82), (0.25, s*4.1, 33.35, .76),
                                             (*el, .62), (0.9, s*5.85, 29.7, .62), (*wr, .43)], 18, 3))
        e, n, w = hand_frame(s)
        parts.append(blob('skin_palm_'+side, add(wr, mul(e, .6)), e, w, (.72, .56, .3), 18, 12))
        parts.append(tube('skin_leg_'+side, [(0, s*1.3, 30.3, 1.2), (0.1, s*1.6, 28.8, 1.36), (0.5, s*1.7, 26.2, 1.1),
                                             (*KNEE[s], .86), (0.55, s*1.8, 22.3, .93), (0.2, s*1.84, 20.5, .66),
                                             (*ANKLE[s], .47)], 20, 3))
        parts.append(tube('skin_foot_'+side, [(0.0, s*1.85, 19.8, .5), (0.2, s*1.87, 18.6, .56), (0.55, s*1.9, 17.3, .42),
                                              (0.95, s*1.9, 16.25, .17)], 16, 3))


def build_hands(parts):
    for side, s in SIDES:
        e, n, w = hand_frame(s)
        for k, (off, length) in enumerate(((.33, 1.3), (0., 1.42), (-.33, 1.22))):
            b = add(WRIST[s], add(mul(e, 1.08), add(mul(w, off), mul(n, .04))))
            pts = [(*sub(b, mul(e, .45)), .21), (*b, .2),
                   (*add(b, add(mul(e, length*.45), mul(n, .1))), .18),
                   (*add(b, add(mul(e, length*.82), mul(n, .32))), .15),
                   (*add(b, add(mul(e, length), mul(n, .58))), .08)]
            name = ('finger_index_' if k == 0 else f'finger_{k}_')+side
            parts.append(tube(name, [r6(p[:3])+(p[3],) for p in pts], 9, 2))
        b = add(WRIST[s], add(mul(e, .38), add(mul(w, .42), mul(n, .12))))
        pts = [(*sub(b, mul(w, .3)), .23), (*b, .22), (*add(b, add(mul(w, .38), add(mul(e, .32), mul(n, .12)))), .19),
               (*add(b, add(mul(w, .58), add(mul(e, .7), mul(n, .32)))), .14),
               (*add(b, add(mul(w, .62), add(mul(e, .95), mul(n, .5)))), .07)]
        parts.append(tube('thumb_'+side, [r6(p[:3])+(p[3],) for p in pts], 9, 2))


WAIST_Z = 31.1
SKIRT_BASE = (1.55, 1.9)
SKIRT_TIP = (3.35, 3.85)
SKIRT_DROP = 5.5


def skirt_radius(t):
    k = math.sin(t*math.pi/2)**.9
    return tuple(a+(b-a)*k for a, b in zip(SKIRT_BASE, SKIRT_TIP))


def build_clothes(parts):
    # Ten overlapping pointed petals in two alternating layers.
    for k in range(10):
        outer = k % 2 == 0
        center = math.radians(k*36)
        half = math.radians(31 if outer else 27)
        length = 1. if outer else .88
        lift = .14 if outer else 0.
        def surface(u, v, center=center, half=half, length=length, lift=lift):
            t = u*length
            sn = v*2-1
            width = half*(.35+.65*math.sin(math.pi*(.18+.82*t/length))**.85)
            theta = center+sn*width
            rx, ry = skirt_radius(t)
            bulge = .24*(1-sn*sn)*math.sin(math.pi*u)+.38*t**3+lift
            z = WAIST_Z-SKIRT_DROP*t+.3*t*t
            point = (.05+(rx+bulge)*math.cos(theta), (ry+bulge)*math.sin(theta), z)
            normal = unit((math.cos(theta)/(rx+bulge), math.sin(theta)/(ry+bulge), .35))
            return point, normal
        parts.append(shell(f'skirt_petal_{k}', surface, 10, 6, .08))
    # A half collar of five small upturned petals (none behind the neck).
    for k, deg in enumerate((-100, -50, 0, 50, 100)):
        center = math.radians(deg)
        def surface(u, v, center=center):
            sn = v*2-1
            width = math.radians(29)*(.45+.55*math.sin(math.pi*(.15+.85*u))**.8)
            theta = center+sn*width
            r = 1.3+1.45*u+.16*(1-sn*sn)*math.sin(math.pi*u)
            z = 35.5+1.35*u-.35*u*u
            point = (.15+r*math.cos(theta)*.95, r*math.sin(theta)*1.18, z)
            normal = unit((math.cos(theta), math.sin(theta), -.7))
            return point, normal
        parts.append(shell(f'collar_petal_{k}', surface, 6, 5, .07))
    # Twisted vine belt.
    belt = []
    for i in range(49):
        a = TAU*i/48
        belt.append((.05+1.63*math.cos(a), 1.99*math.sin(a), WAIST_Z+.03*math.sin(3*a), .24))
    p = tube('belt_vine', [r6(q[:3])+(q[3],) for q in belt], 10, 2)
    parts.append(p)
    # Dust pouch hanging at the left hip, tied to the belt.
    parts.append(blob('pouch', (0.75, 2.62, 29.95), (0.1, .35, 1), (1, 0, 0), (.72, .5, .56), 18, 12))
    parts.append(blob('pouch_rim', (0.75, 2.66, 30.6), (0.1, .35, 1), (1, 0, 0), (.16, .45, .38), 16, 8))
    parts.append(tube('pouch_tie', [(0.75, 1.95, WAIST_Z, .1), (0.8, 2.45, 30.85, .09), (0.78, 2.66, 30.62, .08)], 6, 2))


WING_SPECS = {  # length, max chord, leading fraction, span direction, facing
    'F': (17.0, 6.4, .3, (-.35, .8, .5), (1, .42, .08)),
    'H': (11.5, 5.2, .38, (-.35, .85, -.42), (1, .42, -.05)),
}


def wing_frame(kind, s):
    L, chord, lead, d, face = WING_SPECS[kind]
    n0 = unit((face[0], s*face[1], face[2]))
    span = ortho((d[0], s*d[1], d[2]), n0)
    c = unit(cross(n0, span))
    trailing = (0, s, -1) if kind == 'F' else (0, -s, -1)
    if dot(c, trailing) < 0: c = mul(c, -1)
    return span, c, n0


def build_wing(kind, s):
    L, chord, lead, _, _ = WING_SPECS[kind]
    root = WING_F[s] if kind == 'F' else WING_H[s]
    span, c, n0 = wing_frame(kind, s)
    start = add(root, mul(span, .25))
    def surface(u, v):
        t = u
        shape = max(.06, math.sin(math.pi*(.03+.97*t)**.8))**.62
        if kind == 'H': shape = max(.07, math.sin(math.pi*(.03+.97*t)**.72))**.55
        w = max(.32, chord*shape)
        b = -lead*w+v*w
        camber = .38*math.sin(math.pi*u)*math.sin(math.pi*v)
        point = add(start, add(mul(span, (L-.25)*t), add(mul(c, b), mul(n0, camber+.04))))
        return point, n0
    p = shell(f'wing_{kind}_'+('L' if s > 0 else 'R'), surface, 18, 8, .09)
    knob = blob(f'wing_root_{kind}_'+('L' if s > 0 else 'R'), add(root, mul(span, .15)), span, c, (.62, .42, .34), 14, 10)
    return [p, knob]


def build_parts():
    parts = []
    build_body(parts)
    build_face(parts)
    build_hair(parts)
    build_hands(parts)
    build_clothes(parts)
    for side, s in SIDES:
        parts += build_wing('F', s)+build_wing('H', s)
    return materials.repack(parts)


# ---------------------------------------------------------------- weights
def sharp_chain(point, chain, k=.22):
    """Rigid segments that blend only near each joint."""
    ids = [IDS[b] for b in chain]
    best = None
    for m, (a, b) in enumerate(zip(ids, ids[1:])):
        start, end = REST[a], REST[b]
        d = sub(end, start)
        t = clamp(dot(sub(point, start), d)/dot(d, d))
        distance = math.dist(point, add(start, mul(d, t)))
        if best is None or distance < best[0]-1e-9:
            best = (distance, m, t)
    _, m, t = best
    a, b = ids[m], ids[m+1]
    if m == len(ids)-2 and t >= 1:
        return [(b, 1.)]
    wb = .5*smooth((t-(1-k))/k)
    out = {a: 1-wb, b: wb}
    if m > 0 and t < k:
        wp = .5*smooth((k-t)/k)
        out = {ids[m-1]: wp, a: (1-wp)*(1-wb), b: (1-wp)*wb}
    return [(i, w) for i, w in out.items() if w > 1e-9]


TORSO = ('pelvis', 'spine', 'chest', 'neck')


def torso_weights(v):
    return RIG.chain_weights(v, [IDS[b] for b in TORSO])


def skirt_weights(v, t):
    theta = math.atan2(v[1]/SKIRT_TIP[1], (v[0]-.05)/SKIRT_TIP[0]) % TAU
    order = ('skirt_F', 'skirt_L', 'skirt_B', 'skirt_R')
    q = theta/(math.pi/2)
    i = int(q) % 4
    f = q-int(q)
    share = smooth((t+.05)/.5)
    out = {}
    for b, w in torso_weights(v):
        out[b] = out.get(b, 0)+w*(1-share)
    out[IDS[order[i]]] = out.get(IDS[order[i]], 0)+share*(1-f)
    out[IDS[order[(i+1) % 4]]] = out.get(IDS[order[(i+1) % 4]], 0)+share*f
    return sorted(((b, w) for b, w in out.items() if w > 1e-9), key=lambda x: -x[1])[:4]


def raw_weights(part, v, uv):
    n = part.name
    side = n[-1]
    if n.startswith(('skin_cranium', 'skin_face', 'skin_chin', 'skin_nose', 'eye_', 'lid_', 'lash_', 'brow_',
                     'hair_cap', 'hair_fringe')):
        return [(IDS['head'], 1.)]
    if n.startswith('hair_lock'):
        t = materials.local_uv(n, uv)[0]
        return [(IDS['head'], 1-.75*smooth(t)), (IDS['hair'], .75*smooth(t))] if t > 0 else [(IDS['head'], 1.)]
    if n.startswith('skin_ear'):
        s = 1 if side == 'L' else -1
        d = sub(EAR_TIP[s], EAR[s])
        t = clamp(dot(sub(v, EAR[s]), d)/dot(d, d))
        w = smooth((t-.12)/.45)
        return [(IDS['head'], 1-w), (IDS['ear_'+side], w)] if w > 0 else [(IDS['head'], 1.)]
    if n == 'skin_neck':
        return sharp_chain(v, ('chest', 'neck', 'head'), .35)
    if n.startswith(('skin_pelvis', 'skin_belly', 'skin_chest', 'skin_trapezius', 'belt', 'pouch')):
        return torso_weights(v)
    if n.startswith('collar'):
        return [(IDS['chest'], 1.)]
    if n.startswith('skin_shoulder'):
        return sharp_chain(v, ('chest', 'arm_'+side, 'forearm_'+side), .3)
    if n.startswith('skin_arm'):
        return sharp_chain(v, ('chest', 'arm_'+side, 'forearm_'+side, 'hand_'+side), .22)
    if n.startswith(('skin_palm', 'thumb')):
        return [(IDS['hand_'+side], 1.)]
    if n.startswith('finger_index'):
        return [(IDS['index_'+side], 1.)]
    if n.startswith('finger_'):
        return [(IDS['fingers_'+side], 1.)]
    if n.startswith('skin_leg'):
        return sharp_chain(v, ('pelvis', 'thigh_'+side, 'shin_'+side, 'foot_'+side), .22)
    if n.startswith('skin_foot'):
        return [(IDS['foot_'+side], 1.)]
    if n.startswith('skirt_petal'):
        return skirt_weights(v, clamp((WAIST_Z-v[2])/SKIRT_DROP))
    if n.startswith(('wing_F', 'wing_root_F')):
        return [(IDS['wingF_'+side], 1.)]
    if n.startswith(('wing_H', 'wing_root_H')):
        return [(IDS['wingH_'+side], 1.)]
    raise ValueError('No weights for '+n)


def weights(part, v, uv):
    """Quantised to 1e-6; the last influence takes the exact complement."""
    raw = raw_weights(part, v, uv)
    if len(raw) == 1:
        return [(raw[0][0], 1)]
    out = [(b, round(w, 6)) for b, w in raw[:-1]]
    rest = 1.
    for b, w in out:
        rest -= w
    result = [(b, w) for b, w in out if w > 0]+([(raw[-1][0], rest)] if rest > 0 else [])
    return [(result[0][0], 1)] if len(result) == 1 else result


# ---------------------------------------------------------------- posing
IDENT = (0., 0., 0., 1.)


class Pose:
    def __init__(self):
        self.rot = [IDENT for _ in BONES]
        self.shift = [(0., 0., 0.) for _ in BONES]

    def turn(self, bone, direction, degrees):
        i = IDS[bone]
        self.rot[i] = qmul(axis(direction, math.radians(degrees)), self.rot[i])

    def frame(self):
        return [(*add(local, self.shift[i]), *self.rot[i], 1, 1, 1) for i, (_, _, local) in enumerate(BONES)]

    def world(self):
        return RIG.matrices(self.frame())

    def point(self, bone, rest_point):
        loc, q = self.world()[IDS[bone]]
        return add(loc, rotate(q, sub(rest_point, REST[IDS[bone]])))

    def aim(self, bone, child_rest, target_dir):
        """Rotate bone so its rest direction toward child_rest points along target_dir (world)."""
        i = IDS[bone]
        world = self.world()
        parent = BONES[i][1]
        pq = world[parent][1] if parent >= 0 else IDENT
        current = rotate(qmul(pq, self.rot[i]), sub(child_rest, REST[i]))
        delta = between(current, target_dir)
        w = qmul(delta, qmul(pq, self.rot[i]))
        self.rot[i] = qmul(inverse(pq), w)

    def pivot_root(self, q, pivot, offset=(0, 0, 0)):
        """Rotate the whole body by q about a rest pivot, then translate."""
        self.rot[0] = q
        self.shift[0] = add(sub(pivot, rotate(q, pivot)), offset)

    def reach(self, side, target, pole, blend=1.):
        """Two-bone arm IK toward a world wrist target (blended from the current pose)."""
        s = 1 if side == 'L' else -1
        world = self.world()
        shoulder = world[IDS['arm_'+side]][0]
        current = self.point('hand_'+side, WRIST[s])
        target = lerp(current, target, blend)
        l1, l2 = math.dist(SHOULDER[s], ELBOW[s]), math.dist(ELBOW[s], WRIST[s])
        d = min(math.dist(shoulder, target), l1+l2-1e-3)
        to = unit(sub(target, shoulder))
        a = (l1*l1+d*d-l2*l2)/(2*l1*d)
        bend = ortho(pole, to)
        elbow = add(shoulder, add(mul(to, l1*a), mul(bend, l1*math.sqrt(max(0., 1-a*a)))))
        self.aim('arm_'+side, ELBOW[s], sub(elbow, shoulder))
        self.aim('forearm_'+side, WRIST[s], sub(add(shoulder, mul(to, d)), elbow))


def curl_axis(side):
    s = 1 if side == 'L' else -1
    e, n, w = hand_frame(s)
    ax = cross(e, n)  # rotating e about e x n by + moves e toward n (palm)
    return ax


def curl(P, side, index, others):
    ax = curl_axis(side)
    P.turn('index_'+side, ax, index)
    P.turn('fingers_'+side, ax, others)


def flare(P, bone, outward, degrees):
    P.turn(bone, cross((0, 0, -1), outward), degrees)


SKIRT_DIRS = {'skirt_F': (1, 0, 0), 'skirt_B': (-1, 0, 0), 'skirt_L': (0, 1, 0), 'skirt_R': (0, -1, 0)}


def wings(P, beat, sweep, flap, spread=0., lift=0., lag=.9, hind_scale=.8):
    """Wing beats: sweep folds each wing back about the vertical, flap lifts it."""
    for side, s in SIDES:
        for kind, phase, scale in (('F', 0., 1.), ('H', -lag, hind_scale)):
            b = f'wing{kind}_'+side
            back = sweep*scale*(.5+.5*math.sin(beat+phase))-spread
            up = flap*scale*math.sin(beat+phase+.7)+lift
            P.turn(b, (0, 0, 1), s*back)
            P.turn(b, (1, 0, 0), s*up)


def attitude(P, a):
    """Shared sassy carry: right hand on the hip, left hand loose, right leg tucked.

    Every clip starts and ends here so actions never pop out of the hover.
    """
    if a <= 0: return
    P.turn('arm_L', (1, 0, 0), 10*a)
    P.turn('forearm_L', (0, 1, 0), -22*a)
    curl(P, 'L', 12*a, 22*a)
    P.turn('thigh_L', (0, 1, 0), 3*a)
    P.turn('shin_L', (0, 1, 0), 9*a)
    P.turn('thigh_R', (0, 1, 0), -20*a)
    P.turn('shin_R', (0, 1, 0), 62*a)
    P.turn('foot_R', (0, 1, 0), 10*a)
    pelvis = P.world()[IDS['pelvis']]
    hip = add(pelvis[0], rotate(pelvis[1], sub((-.35, -2.95, 32.0), REST[IDS['pelvis']])))
    P.reach('R', hip, rotate(pelvis[1], (-.55, -1, .15)), a)
    forearm = P.world()[IDS['forearm_R']][1]
    rest_dir = rotate(forearm, sub(knuckle(-1), WRIST[-1]))
    P.aim('hand_R', knuckle(-1), unit(lerp(rest_dir, rotate(pelvis[1], (.55, .35, -1)), a)))
    curl(P, 'R', 20*a, 30*a)


def base_pose(name, t):
    P = Pose()
    ph = TAU*t
    if name == 'idle':
        beat = TAU*8*t
        P.shift[0] = (.25*math.sin(ph), .45*math.sin(ph+.5), .8*math.sin(ph)+.16*math.sin(beat))
        P.turn('chest', (1, 0, 0), 3*math.sin(ph))
        P.turn('head', (1, 0, 0), 7*math.sin(ph+.4))
        P.turn('head', (0, 0, 1), 6*math.sin(ph))
        P.turn('hair', (0, 1, 0), 3*math.sin(beat))
        attitude(P, 1.)
        for side, s in SIDES:
            P.turn('ear_'+side, (0, 1, 0), 4*math.sin(2*ph+s))
            P.turn('shin_'+side, (0, 1, 0), 6*math.sin(ph+s*1.2))
        P.turn('arm_L', (1, 0, 0), 5*math.sin(ph))
        P.turn('forearm_L', (0, 1, 0), -8*math.sin(ph+1))
        P.turn('thigh_L', (0, 1, 0), 5*math.sin(ph))
        P.turn('thigh_R', (0, 1, 0), -4*math.sin(ph))
        curl(P, 'L', 6*math.sin(ph), 8*math.sin(ph+.5))
        for bone, d in SKIRT_DIRS.items():
            flare(P, bone, d, 2.5*math.sin(beat+(1 if 'F' in bone or 'B' in bone else 0)))
        wings(P, beat, 30, 13)
    elif name == 'flit':
        beat = TAU*6*t
        q = axis((0, 1, 0), math.radians(20))
        P.pivot_root(q, REST[IDS['pelvis']], (.8*math.sin(2*ph), 1.6*math.sin(ph), 1.1*math.sin(2*ph+.6)))
        P.turn('pelvis', (1, 0, 0), -6*math.sin(ph))
        P.turn('head', (0, 1, 0), -15)
        P.turn('head', (1, 0, 0), 6*math.sin(ph))
        P.turn('hair', (0, 1, 0), -10+3*math.sin(beat))
        for side, s in SIDES:
            P.turn('ear_'+side, (0, 1, 0), -12)
            P.turn('arm_'+side, (0, 1, 0), 28+6*math.sin(2*ph))
            P.turn('arm_'+side, (1, 0, 0), s*-4)
            P.turn('forearm_'+side, (0, 1, 0), -18)
            P.turn('thigh_'+side, (0, 1, 0), 14+9*math.sin(2*ph+s*1.3))
            P.turn('shin_'+side, (0, 1, 0), 32+12*math.sin(2*ph+s*1.3+1))
            P.turn('foot_'+side, (0, 1, 0), 12)
            curl(P, side, 8, 14)
        flare(P, 'skirt_B', (-1, 0, 0), 14+4*math.sin(beat))
        flare(P, 'skirt_F', (1, 0, 0), -6)
        flare(P, 'skirt_L', (0, 1, 0), 5*math.sin(beat+1))
        flare(P, 'skirt_R', (0, -1, 0), 5*math.sin(beat+2))
        wings(P, beat, 46, 24)
    return P


def poke_pose(t):
    P = Pose()
    wind = window(t, .06, .36)*(1-window(t, .38, .5))
    strike = window(t, .38, .5)*(1-window(t, .64, .96))
    q = axis((0, 1, 0), math.radians(-9*wind+24*strike))
    P.pivot_root(q, REST[IDS['pelvis']], (-1.6*wind+6.2*strike, .6*strike, .8*wind-1.6*strike))
    P.turn('head', (0, 1, 0), 4*wind-14*strike)
    P.turn('head', (1, 0, 0), -4*strike)
    P.turn('hair', (0, 1, 0), -12*strike)
    attitude(P, 1-max(wind, strike))
    for side, s in SIDES:
        P.turn('ear_'+side, (0, 1, 0), -14*strike)
        P.turn('thigh_'+side, (0, 1, 0), -10*wind+22*strike+(6*strike if s < 0 else 0))
        P.turn('shin_'+side, (0, 1, 0), 18*wind+42*strike)
        P.turn('foot_'+side, (0, 1, 0), 14*strike)
    flare(P, 'skirt_B', (-1, 0, 0), 12*strike)
    flare(P, 'skirt_F', (1, 0, 0), 8*wind-6*strike)
    # Left arm swings back for balance.
    P.turn('arm_L', (0, 1, 0), 30*strike-8*wind)
    P.turn('arm_L', (1, 0, 0), 18*strike)
    P.turn('forearm_L', (0, 1, 0), -20*strike-10*wind)
    curl(P, 'L', 20*strike, 30*strike)
    # Right arm: cocked back beside the shoulder, then a straight jab with the index finger.
    chest = P.world()[IDS['chest']]
    def chest_point(p): return add(chest[0], rotate(chest[1], sub(p, REST[IDS['chest']])))
    cocked = chest_point((-1.8, -4.6, 33.2))
    jab = chest_point((10.2, -2.6, 35.2))
    if wind+strike > 1e-6:
        target = lerp(cocked, jab, strike/(wind+strike))
        P.reach('R', target, rotate(chest[1], (-1, -.6, -.4)), min(1., wind+strike))
        if strike > 1e-6:
            P.aim('hand_R', knuckle(-1), lerp(rotate(qmul(P.world()[IDS['forearm_R']][1], IDENT),
                                                      sub(knuckle(-1), WRIST[-1])),
                                               rotate(chest[1], (1, .05, .06)), strike))
    curl(P, 'R', -10*strike, 30*wind+70*strike)
    beat = TAU*4*t
    wings(P, beat, 26*(1-strike), 16*(1-strike), spread=-34*strike, lift=6*wind)
    return P


def hex_pose(t):
    P = Pose()
    gather = window(t, .04, .3)*(1-window(t, .36, .47))
    fling = window(t, .36, .47)*(1-window(t, .7, .97))
    wiggle = window(t, .47, .52)*(1-window(t, .66, .72))
    q = axis((0, 1, 0), math.radians(10*gather-11*fling))
    P.pivot_root(q, REST[IDS['pelvis']], (-1.0*gather+1.2*fling, 0, -.4*gather+1.6*fling))
    P.turn('head', (0, 1, 0), 10*gather-12*fling)
    P.turn('head', (1, 0, 0), 12*fling)
    P.turn('hair', (0, 1, 0), 10*fling)
    attitude(P, 1-max(gather, fling))
    chest = P.world()[IDS['chest']]
    def chest_point(p): return add(chest[0], rotate(chest[1], sub(p, REST[IDS['chest']])))
    for side, s in SIDES:
        P.turn('ear_'+side, (0, 1, 0), 10*fling)
        P.turn('thigh_'+side, (0, 1, 0), -34*gather+8*fling)
        P.turn('shin_'+side, (0, 1, 0), 58*gather+14*fling)
        P.turn('foot_'+side, (0, 1, 0), 10*fling)
        cupped = chest_point((3.2, s*.75, 32.4))
        flung = chest_point((5.6, s*7.8, 38.6))
        amount = gather+fling
        if amount > 1e-6:
            target = lerp(cupped, flung, fling/amount)
            pole = rotate(chest[1], (-.4, s*.6, -1)) if fling > gather else rotate(chest[1], (-.3, s*1, -.3))
            P.reach(side, target, pole, min(1., amount))
        curl(P, side, 35*gather-24*fling+14*wiggle*math.sin(TAU*6*t+s),
             55*gather-30*fling+18*wiggle*math.sin(TAU*6*t+s+1.3))
        flare(P, 'skirt_'+side, (0, s, 0), 8*fling)
    flare(P, 'skirt_F', (1, 0, 0), 6*fling)
    flare(P, 'skirt_B', (-1, 0, 0), 6*fling)
    beat = TAU*5*t
    wings(P, beat, 22*(1-fling), 12*(1-fling), spread=14*fling, lift=-6*gather+14*fling)
    for side, s in SIDES:
        P.turn('wingF_'+side, (0, 0, 1), s*38*gather)
        P.turn('wingH_'+side, (0, 0, 1), s*30*gather)
    return P


def flinch_pose(t):
    P = Pose()
    p = math.sin(math.pi*t)**1.4
    shake = math.sin(TAU*3*t)*math.sin(math.pi*t)
    q = qmul(axis((1, 0, 0), math.radians(10*p)), axis((0, 1, 0), math.radians(-24*p)))
    P.pivot_root(q, REST[IDS['pelvis']], (-3.2*p, .9*p+.4*shake, 1.1*p))
    P.turn('chest', (0, 1, 0), 6*p)
    P.turn('head', (0, 1, 0), 15*p)
    P.turn('head', (0, 0, 1), 10*shake)
    P.turn('hair', (0, 1, 0), 18*p)
    attitude(P, 1-min(1, 1.6*p))
    chest = P.world()[IDS['chest']]
    for side, s in SIDES:
        P.turn('ear_'+side, (0, 1, 0), 22*p)
        guard = add(chest[0], rotate(chest[1], sub((2.4, s*1.6, 36.2), REST[IDS['chest']])))
        P.reach(side, guard, rotate(chest[1], (-.2, s, -1)), .8*p)
        curl(P, side, 40*p, 60*p)
        P.turn('thigh_'+side, (0, 1, 0), -32*p)
        P.turn('shin_'+side, (0, 1, 0), 52*p)
        P.turn('foot_'+side, (0, 1, 0), 18*p)
    flare(P, 'skirt_F', (1, 0, 0), 22*p)
    flare(P, 'skirt_L', (0, 1, 0), 10*p)
    flare(P, 'skirt_R', (0, -1, 0), 10*p)
    beat = TAU*2*t
    wings(P, beat, 14*(1-p), 8*(1-p), spread=-8*p, lift=-34*p)
    for side, s in SIDES:
        P.turn('wingF_'+side, (0, 0, 1), s*24*p)
    return P


def mat_quat(m):
    """Rotation matrix (rows) to quaternion (x, y, z, w)."""
    (a, b, c), (d, e, f), (g, h, i) = m
    tr = a+e+i
    if tr > 0:
        s = math.sqrt(tr+1)*2
        return ((h-f)/s, (c-g)/s, (d-b)/s, .25*s)
    if a > e and a > i:
        s = math.sqrt(1+a-e-i)*2
        return (.25*s, (b+d)/s, (c+g)/s, (h-f)/s)
    if e > i:
        s = math.sqrt(1+e-a-i)*2
        return ((b+d)/s, .25*s, (f+h)/s, (c-g)/s)
    s = math.sqrt(1+i-a-e)*2
    return ((c+g)/s, (f+h)/s, .25*s, (d-b)/s)


def frame_quat(src, dst):
    """Rotation taking orthonormal frame src (3 vectors) onto dst."""
    m = [[sum(dst[k][r]*src[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
    return mat_quat(m)


def slerp(a, b, t):
    d = dot(a, b)
    if d < 0: b, d = tuple(-x for x in b), -d
    if d > .9995:
        return unit4(tuple(x+(y-x)*t for x, y in zip(a, b)))
    th = math.acos(d)
    sa, sb = math.sin((1-t)*th)/math.sin(th), math.sin(t*th)/math.sin(th)
    return tuple(sa*x+sb*y for x, y in zip(a, b))


def unit4(q):
    n = math.sqrt(sum(x*x for x in q))
    return tuple(x/n for x in q)


# Lying on its back along the cell's Y axis, head toward +Y, face up: body X -> world Z, body Z -> world Y.
FALL_Q = frame_quat(((1, 0, 0), (0, 1, 0), (0, 0, 1)), ((0, 0, 1), (1, 0, 0), (0, 1, 0)))
FALL_PELVIS = (0.4, -3.6, 2.15)


def limp(P, amount):
    """Final limp arrangement in body terms (applied with the fall rotation)."""
    a = amount
    P.turn('neck', (0, 1, 0), 18*a)
    P.turn('head', (0, 1, 0), 12*a)
    P.turn('head', (0, 0, 1), 26*a)
    P.turn('head', (1, 0, 0), -10*a)
    P.turn('hair', (0, 1, 0), 18*a)
    P.turn('ear_L', (0, 1, 0), 50*a)
    P.turn('ear_R', (0, 1, 0), 30*a)
    P.turn('ear_L', (1, 0, 0), -10*a)
    P.turn('ear_R', (1, 0, 0), 12*a)
    # Arms fall back onto the floor, one flung up beside the head, one across the hip.
    P.turn('arm_L', (0, 1, 0), 16*a)
    P.turn('arm_L', (1, 0, 0), 80*a)
    P.turn('forearm_L', (0, 1, 0), -28*a)
    P.turn('arm_R', (0, 1, 0), 12*a)
    P.turn('arm_R', (1, 0, 0), 20*a)
    P.turn('forearm_R', (0, 1, 0), -8*a)
    curl(P, 'L', 26*a, 34*a)
    curl(P, 'R', 18*a, 26*a)
    # Legs: hips extend so heels rest on the floor; one knee drawn up and fallen outward.
    P.turn('thigh_L', (0, 1, 0), 2*a)
    P.turn('thigh_L', (1, 0, 0), 8*a)
    P.turn('shin_L', (0, 1, 0), 6*a)
    P.turn('thigh_R', (0, 1, 0), -26*a)
    P.turn('thigh_R', (1, 0, 0), -24*a)
    P.turn('shin_R', (0, 1, 0), 52*a)
    P.turn('foot_L', (0, 1, 0), -10*a)
    P.turn('foot_R', (0, 1, 0), -18*a)
    flare(P, 'skirt_B', (-1, 0, 0), -40*a)
    flare(P, 'skirt_F', (1, 0, 0), -14*a)
    flare(P, 'skirt_L', (0, 1, 0), 6*a)
    flare(P, 'skirt_R', (0, -1, 0), 6*a)


# Stilled wings lie splayed flat on the floor (body X is up), fore toward the head, hind toward the feet.
FALL_WINGS = {('F', 'L'): (58, .6), ('F', 'R'): (36, .5), ('H', 'L'): (128, 2.8), ('H', 'R'): (142, 2.9)}


def flat_wing_q(kind, side):
    s = 1 if side == 'L' else -1
    span, c, n0 = wing_frame(kind, s)
    angle, droop = FALL_WINGS[kind, side]
    a, dr = math.radians(angle), math.radians(droop)
    ds = unit((-math.sin(dr), s*math.sin(a)*math.cos(dr), math.cos(a)*math.cos(dr)))
    nn = ortho((1, 0, 0), ds)
    h = 1 if dot(cross(span, c), n0) > 0 else -1
    return frame_quat((span, c, n0), (ds, mul(unit(cross(nn, ds)), h), nn))


def fall_pose(t):
    P = Pose()
    jolt = window(t, 0, .1)*(1-window(t, .1, .3))
    u = clamp((t-.18)/.52)
    rot = smooth(u)
    drop = u*u
    settle = window(t, .62, .9)
    bounce = .7*math.sin(math.pi*clamp((t-.7)/.14))*(1-settle)
    q = slerp(IDENT, FALL_Q, rot)
    pelvis = REST[IDS['pelvis']]
    target = add(lerp(pelvis, FALL_PELVIS, drop), (0, 0, bounce))
    P.rot[0] = q
    P.shift[0] = sub(target, rotate(q, pelvis))
    attitude(P, 1-window(t, 0, .1))
    # Jolt: a stiff spasm, arms flung and head thrown back, before going limp.
    P.turn('chest', (0, 1, 0), -10*jolt)
    P.turn('head', (0, 1, 0), -18*jolt)
    for side, s in SIDES:
        P.turn('arm_'+side, (1, 0, 0), s*-40*jolt)
        curl(P, side, -12*jolt, -18*jolt)
        P.turn('thigh_'+side, (0, 1, 0), 10*jolt)
    wings(P, 0, 0, 0, spread=-12*jolt*0, lift=16*jolt)
    limp(P, smooth(clamp((t-.22)/.55)*.7+settle*.3))
    # Wings still and flatten as the body lands.
    flat = smooth(clamp((t-.3)/.45))
    for kind in ('F', 'H'):
        for side, s in SIDES:
            i = IDS[f'wing{kind}_'+side]
            P.rot[i] = slerp(P.rot[i], flat_wing_q(kind, side), flat)
    return P


def pose(name, t):
    if name in ('idle', 'flit'): P = base_pose(name, t)
    elif name == 'poke': P = poke_pose(t)
    elif name == 'hex': P = hex_pose(t)
    elif name == 'flinch': P = flinch_pose(t)
    else: P = fall_pose(t)
    return P.frame()


# ---------------------------------------------------------------- export
def geometry():
    from .connected_skin import attach
    parts = attach('pixie', build_parts(), weights)
    return assemble(materials.connected_atlas(parts), weights)


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from .connected_skin import attach
    return materials.connected_atlas(attach('pixie', build_parts(), weights), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_pixie', material_path=SKIN)
    path = ROOT/'mod/BrogueDoom/models/monsters/42_pixie.iqm'
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M42', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/pixie/pixie-animated.blend')
    out = ROOT/'assets/monsters/pixie'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    print(build()['sha256'])
