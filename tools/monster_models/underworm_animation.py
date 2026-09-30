"""Original Project Broom underworm: a huge annulated burrowing worm, coiled to the cell.

Brogue facts (pinned Globals.c): "A strange and horrifying creature of the
earth's deepest places, larger than an ogre but capable of squeezing through
tiny openings. When hungry, the underworm will burrow behind the walls of a
cavern and lurk dormant and motionless -- often for months -- until (it) can
feel the telltale vibrations of nearby prey." It is large (80 HP, defense 40,
18-22 damage, moves at 150 and attacks at 200: slow), never sleeps, bleeds a
brown viscera (DF_WORM_BLOOD, wormColor 80/60/40) and its verbs are "slams",
"bites" and "tail-whips". Slowness, damage, burrowing, dormancy and blood are
Brogue-owned; nothing here selects targets, collides, rolls RNG or moves the
authoritative creature.

Art interpretation (not source facts): a thick fleshy worm, legless, made of
about thirty painted and lightly modelled annuli, coiled on the floor in one
and a quarter turns with a tapering tail tucked into the centre. The heavy
front third rears up out of the coil into a blunt, swollen head with a pale
saddle band (clitellum) behind it. The head faces +X with a round toothed
maw: a fleshy lip ring, a ring of long inward-pointing teeth, a smaller inner
ring around a dark throat, and a hinged lower jaw that opens wide. There are
no eyes, legs, scales or hair, so it cannot be mistaken for the naga's scaled
coil or the centipede's plated legs. Idle rests low, crawl ripples the body,
lunge rears up and drives the open maw forward low and wide, slam rears higher
and crashes the head to the floor, recoil snaps the head back and death slumps
the whole front flat and limp.

The 32-bone chain follows the centreline, so every pose is authored as a
centreline curve; bone orientations come from per-segment frames with the
world +Z as the up hint. Bone scales stay 1. Cosmetic geometry, pose and paint
only.
"""
import hashlib
import json
import math
from functools import lru_cache
from . import iqm, connected_skin
from .rat import ROOT, Part, tube, spline
from .rat import add, sub, mul  # noqa: F401 - blender_skeletal reads rigdata.sub/add
from .skeletal import Rig, axis, qmul, inverse, assemble, sample_clips

SKIN = 'graphics/BRGWORM.png'
MODEL = 'models/monsters/36_underworm.iqm'
SKIN_VOXEL_SIZE = .3
SKIN_FACE_BUDGET = 14000
TAU = math.tau


def CONNECTED_SKIN(name):
    return name.startswith('skin_')


def r6(x):
    return round(x, 6)


def unit(v):
    n = math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])
    return (v[0]/n, v[1]/n, v[2]/n) if n > 1e-12 else (0., 0., 1.)


def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def crs(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def dist(a, b): return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2)
def lerp(a, b, t): return tuple(x+(y-x)*t for x, y in zip(a, b))
def clamp(v, lo=0., hi=1.): return max(lo, min(hi, v))
def smooth(t): t = clamp(t); return t*t*(3-2*t)


# ------------------------------------------------------------------ rest centreline
TURNS = 1.44          # coil turns before the front rears up
SHIFT = -2.5          # whole design sits back so the armoured maw stays inside the cell
CX = -7.0+SHIFT
CY = 4.16
A0, A1 = 3.54, 17.04   # x semi-axis of the spiral at tail tip / coil end
B0, B1 = 4.71, 24.39   # y semi-axis
R0, R1 = 1.2, 7.8      # lateral radius at tail tip / coil end
RZ = .72              # vertical/lateral section ratio (a low, flat oval, not a tube)
COIL_N = 26
PITCH_COUNT = 30      # annuli between tail tip and head joint
BONE = 5.0            # chord length of every body bone

NECK_RAW = [  # (x, y, z, lateral radius): leaves the coil east along the floor, then rises and turns to face +X
    (-1.0, -20.4, 6.4, 8.0),
    (6.0, -18.6, 11.5, 8.4),
    (11.4, -13.6, 20.0, 8.9),
    (13.2, -7.6, 29.5, 9.3),
    (12.6, -2.4, 37.5, 9.7),
    (9.6, .6, 43.0, 10.0),
    (9.4, 2.0, 46.6, 10.3),
    (10.6, 2.4, 48.0, 10.4),
]


def rest_controls():
    pts = []
    for i in range(COIL_N):
        u = i/(COIL_N-1)
        th = TAU*TURNS*(u-1)-math.pi/2      # the coil ends at its south side heading +X
        a = A0+(A1-A0)*u
        b = B0+(B1-B0)*u
        r = R0+(R1-R0)*u**1.43
        pts.append((r6(CX+a*math.cos(th)), r6(CY+b*math.sin(th)), r6(RZ*r+.08), r6(r)))
    return pts+list(NECK)

NECK = [(x+SHIFT, y, z, r) for x, y, z, r in NECK_RAW]


NECK0 = COIL_N        # index of the first free neck control


def resample(rows, step=.5):
    """Uniform-arc resample of (x, y, z, r) rows."""
    arcs = [0.]
    for a, b in zip(rows, rows[1:]):
        arcs.append(arcs[-1]+dist(a, b))
    out = []
    n = int(arcs[-1]/step)
    j = 0
    for k in range(n+1):
        s = k*step
        while j < len(rows)-2 and arcs[j+1] < s:
            j += 1
        span = arcs[j+1]-arcs[j]
        t = (s-arcs[j])/span if span > 1e-12 else 0.
        out.append(lerp(rows[j], rows[j+1], t))
    return out


def extend(dense, length=70., step=.5, direction=None):
    """Straight run beyond the final sample (so bone walks never run off the end)."""
    d = unit(direction if direction is not None else sub(dense[-1][:3], dense[-2][:3]))
    last = dense[-1]
    return dense+[(last[0]+d[0]*step*k, last[1]+d[1]*step*k, last[2]+d[2]*step*k, last[3])
                  for k in range(1, int(length/step)+1)]


def centreline(controls, step=.5):
    return resample(spline(controls, 12), step)


def walk(points, count, chord):
    """Place count joints after points[0]; each is exactly `chord` from the previous."""
    joints = [tuple(points[0][:3])]
    i = 0
    for _ in range(count):
        cur = joints[-1]
        while dist(points[i+1][:3], cur) < chord:
            i += 1
        a, b = points[i][:3], points[i+1][:3]
        d = sub(b, a)
        f = sub(a, cur)
        qa, qb, qc = dot(d, d), 2*dot(f, d), dot(f, f)-chord*chord
        t = clamp((-qb+math.sqrt(max(0., qb*qb-4*qa*qc)))/(2*qa))
        joints.append(tuple(a[k]+d[k]*t for k in range(3)))
    return joints


REST_CONTROLS = rest_controls()
REST_DENSE = centreline(REST_CONTROLS)


def bone_count(dense, chord):
    """Chords needed for the walk to reach the end of the curve (head joint sits just past it)."""
    pts = extend(dense)
    cur, i, n = pts[0][:3], 0, 0
    while i < len(dense)-2:
        while dist(pts[i+1][:3], cur) < chord:
            i += 1
        a, b = pts[i][:3], pts[i+1][:3]
        d = sub(b, a)
        f = sub(a, cur)
        qa, qb, qc = dot(d, d), 2*dot(f, d), dot(f, f)-chord*chord
        t = clamp((-qb+math.sqrt(max(0., qb*qb-4*qa*qc)))/(2*qa))
        cur = tuple(a[k]+d[k]*t for k in range(3))
        n += 1
    return n


BODY_BONES = bone_count(REST_DENSE, BONE)
REST_JOINTS = walk(extend(REST_DENSE), BODY_BONES, BONE)
REST_JOINTS = [tuple(r6(c) for c in p) for p in REST_JOINTS]
HEAD = REST_JOINTS[-1]

# ------------------------------------------------------------------ rig
PETAL_AZ = (45., 135., 225., 315.)       # four armoured jaw petals around the mouth
RIM = (12.6, 8.6)                          # mouth rim semi-axes (y, z)
HINGE_X = 7.4                              # rim plane, in front of the head joint
NAMES = ['root']+[f'seg_{i}' for i in range(1, BODY_BONES)]+['head']
SPECS = [(n, None if i == 0 else NAMES[i-1], REST_JOINTS[i]) for i, n in enumerate(NAMES)]
for _k, _az in enumerate(PETAL_AZ):
    _a = math.radians(_az)
    SPECS.append((f'petal_{_k}', 'head', (r6(HEAD[0]+HINGE_X), r6(HEAD[1]+RIM[0]*math.cos(_a)), r6(HEAD[2]+RIM[1]*math.sin(_a)))))
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
HEAD_ID = IDS['head']
PETAL_IDS = [IDS[f'petal_{k}'] for k in range(4)]
CHAIN = [IDS[n] for n in NAMES]
CLIPS = [('idle', 40, 20, True), ('crawl', 28, 24, True), ('lunge', 25, 35, False),
         ('slam', 29, 35, False), ('recoil', 15, 35, False), ('collapse', 37, 35, False)]

# ------------------------------------------------------------------ frames and quaternions


def frame_axes(direction, up=(0., 0., 1.)):
    t = unit(direction)
    if abs(dot(t, up)) > .985:
        up = (1., 0., 0.)
    left = unit(crs(up, t))
    return t, left, crs(t, left)


def quat_from_axes(x, y, z):
    m00, m10, m20 = x
    m01, m11, m21 = y
    m02, m12, m22 = z
    tr = m00+m11+m22
    if tr > 0:
        s = math.sqrt(tr+1)*2
        q = ((m21-m12)/s, (m02-m20)/s, (m10-m01)/s, .25*s)
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1+m00-m11-m22)*2
        q = (.25*s, (m01+m10)/s, (m02+m20)/s, (m21-m12)/s)
    elif m11 > m22:
        s = math.sqrt(1+m11-m00-m22)*2
        q = ((m01+m10)/s, .25*s, (m12+m21)/s, (m02-m20)/s)
    else:
        s = math.sqrt(1+m22-m00-m11)*2
        q = ((m02+m20)/s, (m12+m21)/s, .25*s, (m10-m01)/s)
    n = math.sqrt(sum(c*c for c in q))
    q = tuple(c/n for c in q)
    return q if q[3] >= 0 else tuple(-c for c in q)


def bone_quats(joints):
    return [quat_from_axes(*frame_axes(sub(joints[i+1], joints[i]))) for i in range(len(joints)-1)]


REST_QUATS = bone_quats(REST_JOINTS)
REST_LOCAL = [tuple(local) for _, _, local in BONES]


def norm_q(q):
    return q if q[3] >= 0 else tuple(-c for c in q)


def nlerp(a, b, t):
    if sum(x*y for x, y in zip(a, b)) < 0:
        b = tuple(-x for x in b)
    q = tuple(x+(y-x)*t for x, y in zip(a, b))
    n = math.sqrt(sum(c*c for c in q))
    return tuple(c/n for c in q)


BLEND = (0., 0., .12, .25)   # last bones turn slightly toward the head


def frames_from(joints, head, jaw_deg):
    """Bone frame rows from a pose joint chain, an absolute head orientation (pitch down, yaw, deg) and jaw angle."""
    quats = bone_quats(joints)
    world = [qmul(q, inverse(r)) for q, r in zip(quats, REST_QUATS)]
    pitch, yaw, roll = (tuple(head)+(0.,))[:3]
    head_q = qmul(axis((0, 0, 1), math.radians(yaw)), qmul(axis((0, 1, 0), math.radians(pitch)),
                                                          axis((1, 0, 0), math.radians(roll))))
    k = len(world)
    for j, w in enumerate(BLEND):
        world[k-len(BLEND)+j] = nlerp(world[k-len(BLEND)+j], head_q, w)
    world.append(head_q)
    f = [[*local, 0, 0, 0, 1, 1, 1, 1] for local in REST_LOCAL]
    f[0][0:3] = list(joints[0])
    for i, q in enumerate(world):
        parent = qmul(inverse(world[i-1]), q) if i else q
        f[i][3:7] = norm_q(parent)
    for k, az in enumerate(PETAL_AZ):
        a = math.radians(az)
        tangent = (0., -RIM[1]*math.sin(a), RIM[0]*math.cos(a))
        open_deg = jaw_deg*(1+.16*math.sin(k*2.3+.7))
        f[PETAL_IDS[k]][3:7] = axis(tangent, math.radians(open_deg))       # positive angle opens outward
    return f


# ------------------------------------------------------------------ geometry
def section_frame(direction):
    t, left, up = frame_axes(direction)
    return t, left, up


HEAD_EXT = 16.
SEGMENT = REST_DENSE                                   # tail tip to the end of the neck curve
S_ARC = [0.]
for _a, _b in zip(SEGMENT, SEGMENT[1:]):
    S_ARC.append(S_ARC[-1]+dist(_a, _b))


def _arc_at_joint():
    # arc position of the head joint on the rest curve (nearest sample)
    best = min(range(len(SEGMENT)), key=lambda i: dist(SEGMENT[i][:3], HEAD))
    return S_ARC[best]


S_HEAD = _arc_at_joint()
S_TOT = S_HEAD+HEAD_EXT
PITCH = S_HEAD/PITCH_COUNT
CLITELLUM = (.56, .655)         # fraction of S_HEAD


def swell(s):
    """Radius factor along the body: shallow annulus grooves, a saddle band, a collar behind the head."""
    p = (s/PITCH) % 1.
    d = min(p, 1-p)
    f = 1-.065*math.exp(-(d/.15)**2)
    frac = s/S_HEAD
    if CLITELLUM[0] < frac < CLITELLUM[1]:
        f *= 1+.05*math.sin(math.pi*(frac-CLITELLUM[0])/(CLITELLUM[1]-CLITELLUM[0]))
    f *= 1+.05*math.exp(-((s-(S_HEAD-14.))/3.)**2)
    return f


def body_part(sides=28):
    """The single swept, annulated body tube: low oval section, closed ends."""
    p = Part('skin_body')
    step = 2                                         # every second dense sample
    idx = [i for i in range(0, len(SEGMENT), step) if S_ARC[i] <= S_HEAD+3.5]
    rows = []
    for i in idx:
        c = SEGMENT[i]
        j0, j1 = max(0, i-1), min(len(SEGMENT)-1, i+1)
        t, left, up = frame_axes(sub(SEGMENT[j1][:3], SEGMENT[j0][:3]))
        radius = c[3]*swell(S_ARC[i])
        if c[2] <= RZ*c[3]+.4:                       # floor-lying section: rest exactly on the floor
            c = (c[0], c[1], RZ*radius+.08, c[3])
        rows.append((c, left, up, radius))
    for c, left, up, r in rows:
        for j in range(sides+1):
            a = TAU*j/sides
            co = tuple(c[k]+left[k]*r*math.cos(a)+up[k]*r*RZ*math.sin(a) for k in range(3))
            p.vertices.append(tuple(r6(x) for x in co))
            p.uv.append((.3, .5))
    for i in range(len(rows)-1):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+1, a+sides+2, a+sides+1))
    for end, reverse in ((0, True), (len(rows)-1, False)):
        centre = len(p.vertices)
        p.vertices.append(tuple(r6(x) for x in rows[end][0][:3]))
        p.uv.append((.3, .5))
        for j in range(sides):
            a = end*(sides+1)+j
            p.faces.append((centre, a+1, a) if reverse else (centre, a, a+1))
    return p


def ellipsoid(name, c, r, seg=28, rings=16):
    from .rat import ellipsoid as e
    p = e(name, c, r, 'fur', seg, rings)
    p.vertices = [tuple(r6(x) for x in v) for v in p.vertices]
    p.uv = [(.3, .5)]*len(p.vertices)
    return p


FLAT_REAR, FLAT_FRONT = .86, .66            # head is flattened: wider than tall, widest at the mouth
HEAD_PROFILE = [(-6., 10.2), (-2., 10.6), (2., 11.6), (5.6, 12.8), (8., 13.4), (9.2, 12.8), (9.6, 11.6),
                (8.8, 10.4), (7., 8.8), (5.6, 6.6), (5., 3.2)]      # (x from head joint, radius): flared, funnel-mouthed
FUNNEL_X = 4.6                               # x of the funnel floor
RIBS = 10
RIB_AMP = .17


def flat(x):
    return FLAT_REAR+(FLAT_FRONT-FLAT_REAR)*smooth((x+6.)/14.)


def orient(part):
    """Flip faces if the part encloses negative volume (outward winding)."""
    vol = 0.
    for a, b, c in part.triangles():
        vol += dot(part.vertices[a], crs(part.vertices[b], part.vertices[c]))
    if vol < 0:
        part.faces = [tuple(reversed(f)) for f in part.faces]
    return part


def head_part(sides=36):
    """Flared, ridged, flattened head with a funnel mouth: no smooth dome."""
    prof = spline([(x, rho) for x, rho in HEAD_PROFILE], 3)
    p = Part('skin_head')
    for x, rho in prof:
        rib = smooth((x+6.)/4.)
        for j in range(sides+1):
            a = TAU*j/sides
            k = 1+RIB_AMP*rib*max(0., math.cos(RIBS*a))**2
            p.vertices.append((r6(HEAD[0]+x), r6(HEAD[1]+rho*k*math.cos(a)), r6(HEAD[2]+rho*k*flat(x)*math.sin(a))))
            p.uv.append((.3, .5))
    n = len(prof)
    for i in range(n-1):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+1, a+sides+2, a+sides+1))
    for end, reverse in ((0, True), (n-1, False)):
        c = len(p.vertices)
        p.vertices.append((r6(HEAD[0]+prof[end][0]), r6(HEAD[1]), r6(HEAD[2])))
        p.uv.append((.3, .5))
        for j in range(sides):
            a = end*(sides+1)+j
            p.faces.append((c, a+1, a) if reverse else (c, a, a+1))
    return orient(p)


def sweep(name, rows, sides=12, u=.882):
    """rows: (centre, across_unit, thick_unit, half_width, half_thick, v) -> closed swept oval solid."""
    p = Part(name)
    for c, t, nn, w, th, v in rows:
        for j in range(sides+1):
            a = TAU*j/sides
            p.vertices.append(tuple(r6(c[k]+t[k]*w*math.cos(a)+nn[k]*th*math.sin(a)) for k in range(3)))
            p.uv.append((r6(u+.036*j/sides), r6(v)))
    for i in range(len(rows)-1):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+1, a+sides+2, a+sides+1))
    for end, reverse in ((0, True), (len(rows)-1, False)):
        c = len(p.vertices)
        p.vertices.append(tuple(r6(x) for x in rows[end][0]))
        p.uv.append((r6(u+.018), r6(rows[end][5])))
        for j in range(sides):
            a = end*(sides+1)+j
            p.faces.append((c, a+1, a) if reverse else (c, a, a+1))
    return orient(p)


def torus(name, x, ry, rz, r, rings=36, sides=10, u=.882):
    """Closed collar ring around the head axis (elliptical), tube radius r."""
    p = Part(name)
    for i in range(rings+1):
        psi = TAU*i/rings
        cy, cz = ry*math.cos(psi), rz*math.sin(psi)
        n = unit((0., math.cos(psi)*rz, math.sin(psi)*ry))
        for j in range(sides+1):
            a = TAU*j/sides
            p.vertices.append((r6(HEAD[0]+x+r*.85*math.sin(a)), r6(HEAD[1]+cy+n[1]*r*math.cos(a)),
                               r6(HEAD[2]+cz+n[2]*r*math.cos(a))))
            p.uv.append((r6(u+.036*j/sides), r6(.3+.5*(1-math.cos(psi*2))/2)))
    for i in range(rings):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+1, a+sides+2, a+sides+1))
    return orient(p)


def rim_point(az_deg, shrink=1., dx=0.):
    a = math.radians(az_deg)
    return (HEAD[0]+HINGE_X+dx, HEAD[1]+RIM[0]*shrink*math.cos(a), HEAD[2]+RIM[1]*shrink*math.sin(a))


def petal_path(k, s):
    """Centre of petal k at fraction s: forward from the rim, curling inward like an iris."""
    return rim_point(PETAL_AZ[k], 1-.5*s**1.3, 6.0*s)


def fang(name, base, toward, length, r0):
    d = unit(toward)
    mid = tuple(base[k]+d[k]*length*.5 for k in range(3))
    tip = tuple(base[k]+d[k]*length for k in range(3))
    part = tube(name, [(*(r6(c) for c in base), r0), (*(r6(c) for c in mid), r0*.62), (*(r6(c) for c in tip), .05)],
                'fur', 8, 2)
    part.vertices = [tuple(r6(x) for x in v) for v in part.vertices]
    part.uv = [(.86, r6(.06+.9*clamp(dot(sub(v, base), d)/length))) for v in part.vertices]
    return part


def hook(name, base, radial, length, r0):
    """Sharp hooked ivory tooth curling inward from a petal, tapered cone with a dark root (palette v)."""
    pts = [base]
    d1 = unit((.55, 0., 0.))
    inward = tuple(-c for c in radial)
    p1 = tuple(base[m]+length*.42*(.5*d1[m]*1.8+.25*inward[m]) for m in range(3))
    p2 = tuple(p1[m]+length*.36*(.35*(1., 0., 0.)[m]+.7*inward[m]) for m in range(3))
    p3 = tuple(p2[m]+length*.30*(-.25*(1., 0., 0.)[m]+.95*inward[m]) for m in range(3))
    ctrl = [(*(r6(c) for c in q), r) for q, r in ((base, r0), (p1, r0*.78), (p2, r0*.42), (p3, .04))]
    part = tube(name, ctrl, 'fur', 8, 2)
    part.vertices = [tuple(r6(x) for x in v) for v in part.vertices]
    chord = sub(p3, base)
    span = math.sqrt(dot(chord, chord))
    part.uv = [(.86, r6(.04+.92*clamp(dot(sub(v, base), chord)/(span*span)))) for v in part.vertices]
    return part


def petal_parts(k):
    az = math.radians(PETAL_AZ[k])
    radial = unit((0., math.cos(az), math.sin(az)))
    rows, ridge = [], []
    for i in range(9):
        s = i/8
        c = petal_path(k, s)
        d = unit(sub(petal_path(k, min(1., s+.02)), petal_path(k, max(0., s-.02))))
        across = unit(crs(d, radial))
        thick = unit(crs(across, d))
        w = 5.4*(1-.8*s**1.1)+.2
        th = 1.5*(1-.6*s)+.3
        rows.append((c, across, thick, w, th, .05+.9*s))
        if i < 8:
            rc = tuple(c[m]+thick[m]*(th+.15) for m in range(3))
            ridge.append((rc, across, thick, .5*(1-.5*s)+.15, .85*(1-.5*s)+.15, .05+.9*s))
    parts = [sweep(f'petal_{k}', rows), sweep(f'petal_{k}_ridge', ridge, sides=6)]
    for i, (s, size) in enumerate(((.55, 4.4), (.78, 4.8), (.97, 4.0))):
        c = petal_path(k, s)
        base = tuple(c[m]-radial[m]*.9 for m in range(3))
        parts.append(hook(f'tooth_p{k}_{i}', base, radial, size, 1.3))
    return parts


def cap_parts():
    """Overlapping chitin plates closing the back of the head (solid armoured cap seen from behind)."""
    parts = []
    for k, (x, rx, ry, rz) in enumerate(((-12.8, 5.0, 12.8, 10.6), (-16.0, 4.2, 11.0, 9.0), (-18.6, 3.4, 8.6, 7.2))):
        c = (HEAD[0]+x, HEAD[1], HEAD[2])
        p = ellipsoid(f'cap_{k}', c, (rx, ry, rz), 28, 12)
        p.uv = [(r6(.882+.036*((math.atan2(v[2]-c[2], v[1]-c[1])/TAU) % 1.)),
                 r6(.18+.7*(1-clamp(math.hypot((v[1]-c[1])/ry, (v[2]-c[2])/rz))*.8-.22*k))) for v in p.vertices]
        parts.append(p)
    return parts


def ellipsoid(name, c, r, seg=28, rings=16):
    from .rat import ellipsoid as e
    p = e(name, c, r, 'fur', seg, rings)
    p.vertices = [tuple(r6(x) for x in v) for v in p.vertices]
    p.uv = [(.3, .5)]*len(p.vertices)
    return p


def head_teeth():
    parts = []
    for i in range(10):
        a = math.radians(18+36*i)
        y, z = 9.3*math.cos(a), 9.3*.68*math.sin(a)
        base = (HEAD[0]+7.4, HEAD[1]+y, HEAD[2]+z)
        radial = unit((0., y, z/.68))
        toward = (.7, -.7*radial[1], -.7*radial[2]*.7)
        parts.append(fang(f'tooth_h{i}', base, toward, 3.4, .85))
    return parts


def build_parts():
    parts = [body_part(), head_part()]
    throat = ellipsoid('throat', (HEAD[0]+FUNNEL_X+.6, HEAD[1], HEAD[2]), (1.2, 7.4, 4.9), 26, 14)
    throat.uv = [(.98, r6(.04+.9*clamp(math.hypot((v[1]-HEAD[1])/7.4, (v[2]-HEAD[2])/4.9)))) for v in throat.vertices]
    parts.append(throat)
    for k, (x, ry, r) in enumerate(((-2.4, 13.3, 2.8), (-6.4, 12.5, 2.7), (-10.2, 11.8, 2.5))):
        parts.append(torus(f'collar_{k}', x, ry, ry*flat(x)*.96, r))
    for k in range(4):
        parts.extend(petal_parts(k))
    parts.extend(cap_parts())
    parts.extend(head_teeth())
    return parts


def qweights(pairs):
    """Quantize to 1e-6, giving the largest weight the exact remainder, so Blender's Python agrees."""
    total = math.fsum(w for b, w in pairs)
    q = [(b, round(w/total, 6)) for b, w in pairs]
    k = max(range(len(q)), key=lambda i: q[i][1])
    q[k] = (q[k][0], round(1-math.fsum(w for i, (b, w) in enumerate(q) if i != k), 6))
    return q


def weights(p, v, u):
    n = p.name
    if n.startswith('petal_'):
        return [(PETAL_IDS[int(n[6])], 1)]
    if n.startswith('tooth_p'):
        return [(PETAL_IDS[int(n[7])], 1)]
    if n.startswith(('skin_head', 'collar_', 'cap_', 'throat', 'tooth_h')):
        return [(HEAD_ID, 1)]
    return qweights(RIG.chain_weights(v, CHAIN))


def geometry():
    parts = connected_skin.attach('underworm', build_parts(), weights)
    from . import underworm_materials as m
    for p in parts:
        if p.name == 'Connected_skin':
            p.uv = m.pigment_uv(p.vertices)
    return assemble(parts, weights)


# ------------------------------------------------------------------ poses
# Neck control curves (x, y, z) for controls NECK0.. of the centreline, the head nod
# (pitch down deg, yaw deg) and the jaw angle. Radii always stay at their rest values.
def neck(*points):
    return [(p[0]+SHIFT, p[1], p[2]) for p in points]


KEYS = {
    'rest': dict(neck=[n[:3] for n in NECK], nod=(0., 0., 0.), jaw=48., shove=0.),
    # rear up and back, petals loosened
    'rear': dict(neck=neck((-1.0, -20.4, 6.4), (4.4, -17., 13.), (7., -11., 23.), (7.2, -5., 33.), (5.4, -.4, 42.),
                           (3.6, 2.4, 49.), (4.4, 3.6, 53.4), (7.6, 3.6, 54.4)),
                 nod=(-14., 0., 0.), jaw=60., shove=-1.0),
    # swan-necked strike: the neck arches behind, the head is thrown low and forward, petals flung open
    'strike': dict(neck=neck((-1.0, -20.4, 6.4), (5.6, -20.2, 10.), (11.2, -17.6, 17.4), (14., -12.6, 27.),
                             (12.8, -8., 34.), (10.6, -4.4, 32.6), (10., -1.4, 26.), (10.6, -.2, 21.)),
                   nod=(12., 0., 0.), jaw=64., shove=1.0),
    # rears higher, then crashes the head down to the floor and to the left
    'rear2': dict(neck=neck((-1.0, -20.4, 6.4), (3.6, -17., 14.), (5.2, -11., 25.), (5., -5., 36.), (3.4, -.4, 46.),
                            (2.6, 3., 53.), (4., 4.2, 57.), (7., 4., 57.6)),
                  nod=(-22., -6., 0.), jaw=56., shove=-1.6),
    'slam': dict(neck=neck((-1.0, -20.4, 6.4), (5.8, -18., 10.4), (11.6, -12.4, 19.), (14.4, -6., 27.),
                           (12.6, 0., 29.), (11.6, 5., 24.), (11., 9., 19.8), (10.6, 11.5, 15.9)),
                 nod=(34., 10., 0.), jaw=56., shove=1.2),
    # struck: head snaps back, up and away
    'flinch': dict(neck=neck((-1.0, -20.4, 6.4), (4., -17., 12.), (8., -11., 22.), (9.4, -5., 32.), (8.6, .4, 40.),
                             (8., 4., 45.), (7.4, 6., 46.4), (9., 6.6, 46.4)),
                   nod=(-20., 22., 0.), jaw=52., shove=-.8),
    # limp: the neck lies along the floor, runs north beside the coil, head lolls on its side, petals slack
    'dead': dict(neck=neck((2., -20.6, 7.2), (11., -22., 7.4), (18., -19., 7.5), (19.4, -11., 7.6), (15.4, -3., 7.9),
                           (11., 1.4, 8.4), (11.4, 4.6, 9.4), (11.6, 6.4, 10.2)),
                 nod=(14., 85., 0.), jaw=22., shove=0.),
}


def key_blend(a, b, t):
    ka, kb = KEYS[a], KEYS[b]
    return dict(neck=[lerp(x, y, t) for x, y in zip(ka['neck'], kb['neck'])],
                nod=lerp(ka['nod'], kb['nod'], t), jaw=ka['jaw']+(kb['jaw']-ka['jaw'])*t,
                shove=ka['shove']+(kb['shove']-ka['shove'])*t)


def timeline(keys, t):
    """keys: [(time, name)...]; smooth blend between neighbouring keys."""
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t <= t1:
            return key_blend(a, b, smooth((t-t0)/(t1-t0)) if t1 > t0 else 1.)
    return key_blend(keys[-1][1], keys[-1][1], 0.)


NECK_W = [k/(len(NECK)-1) for k in range(len(NECK))]     # 0 at the coil end, 1 at the head


def controls_for(state, phase=None, ripple=0.):
    """Full centreline controls: the coil follows REST, the neck follows the key state.

    ripple lifts a travelling wave along the body (crawl/idle breathing); the lift is never negative.
    """
    pts = list(REST_CONTROLS)
    for k, (x, y, z) in enumerate(state['neck']):
        pts[NECK0+k] = (x, y, z, pts[NECK0+k][3])
    if state['shove']:
        for k in range(8):                                # the last coil quarter-turn heaves along the exit heading
            i = COIL_N-1-k
            x, y, z, r = pts[i]
            pts[i] = (x+state['shove']*smooth(1-k/8), y, z, r)
    if ripple:
        for i in range(len(pts)):
            u = i/(len(pts)-1)
            x, y, z, r = pts[i]
            wave = .5+.5*math.sin(TAU*(phase-u*2.6))
            pts[i] = (x, y, z+ripple*wave*(.3+.7*u)*(1.-.5*(i >= NECK0)), r)
    return pts


def joints_for(controls):
    return walk(extend(centreline(controls)), BODY_BONES, BONE)


def sway(state, t, lateral, lift, along, cycles=1., phase=0.):
    """Wave the raised neck: state neck points move by w*(along, lateral, lift). Phase 0 is exactly rest."""
    a, b = math.sin(TAU*cycles*t+phase), 1-math.cos(TAU*cycles*t+phase)
    state['neck'] = [(x+along*w*a, y+lateral*w*math.sin(TAU*cycles*t+phase+.9)-lateral*w*math.sin(phase+.9),
                      z+lift*w*b*.5-lift*w*(1-math.cos(phase))*.5) for (x, y, z), w in zip(state['neck'], NECK_W)]


def pose(name, t):
    ripple = 0.
    phase = None
    if name == 'rest':
        state = key_blend('rest', 'rest', 0.)
    elif name == 'idle':
        state = key_blend('rest', 'rest', 0.)
        sway(state, t, .9, .8, .3)
        state['jaw'] = 48.+4.*math.sin(TAU*t)
        state['nod'] = (1.5*math.sin(TAU*t), 2.4*math.sin(TAU*t), 0.)
        ripple, phase = .7, t
        ripple *= math.sin(math.pi*t)**2                 # zero at t = 0 and 1: idle frame 0 is exactly the rest pose
    elif name == 'crawl':
        state = key_blend('rest', 'strike', .05)
        sway(state, t, 1.3, 1.3, .2)
        state['jaw'] = 52.+6*math.sin(TAU*t*2+.5)
        state['nod'] = (state['nod'][0]+3*math.sin(TAU*t*2), 4*math.sin(TAU*t+1.), 0.)
        state['shove'] = .8*math.sin(TAU*t)
        ripple, phase = 2.6, t
    elif name == 'lunge':
        state = timeline([(0, 'rest'), (.30, 'rear'), (.46, 'strike'), (.60, 'strike'), (.80, 'rear'), (1, 'rest')], t)
    elif name == 'slam':
        state = timeline([(0, 'rest'), (.32, 'rear2'), (.48, 'slam'), (.62, 'slam'), (.82, 'rear'), (1, 'rest')], t)
    elif name == 'recoil':
        state = timeline([(0, 'rest'), (.5, 'flinch'), (1, 'rest')], t)
    elif name == 'collapse':
        q = smooth(clamp(t/.72))
        state = key_blend('rest', 'dead', q)
        # the head lurches up a little as the neck gives way, then drops
        bump = math.sin(math.pi*clamp(t/.72))*.5
        state['neck'] = [(x, y, z+bump*w**2*4.5) for (x, y, z), w in zip(state['neck'], NECK_W)]
        state['nod'] = lerp(KEYS['rest']['nod'], KEYS['dead']['nod'], smooth(clamp((t-.36)/.45)))      # the head turns over after the neck gives way
        state['jaw'] = 48.+(22.-48.)*smooth(clamp((t-.2)/.4))
    else:
        raise ValueError(name)
    joints = joints_for(controls_for(state, phase, ripple))
    return frames_from(joints, state['nod'], state['jaw'])


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from . import underworm_materials as materials
    return materials.texture_bytes()


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, t, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, t, w, BONES, clips, bounds, mesh_label='Project_Broom_underworm', material_path=SKIN)
    path = ROOT/'mod/BrogueDoom'/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M36', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(t), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/underworm/underworm-animated.blend')
    out = ROOT/'assets/monsters/underworm'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    result = importlib.import_module('tools.monster_models.underworm_animation').build()
    print({k: result[k] for k in ('sha256', 'dimensions', 'vertices', 'triangles', 'boneCount')})
