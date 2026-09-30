"""Original Project Broom kraken: a rearing deep-water cephalopod. Presentation only.

Brogue facts (pinned Globals.c): "This tentacled nightmare will emerge from the
subterranean waters to ensnare and devour any creature foolish enough to set
foot into $HISHER lake." It is large; its tokens are MA_SEIZES,
MONST_SUBMERGES, MONST_RESTRICTED_TO_LIQUID, MONST_IMMUNE_TO_WATER, MONST_FLITS,
MONST_FLEES_NEAR_DEATH and MONST_NEVER_SLEEPS; its attack verbs are "slaps",
"smites" and "batters" and it is "devouring" prey. Everything else here - eight
arms and two clubbed feeding tentacles, the mantle, the paired golden eyes, the
parrot beak, the sucker rows and every size - is art interpretation. Seizing,
submersion, visibility, liquid restriction, movement and all outcomes remain
Brogue-owned. There is no collision, AI, RNG or autonomous grabbing.

Deep water: the frontend draws an opaque surface 24 units above the bed and
places this proxy on the bed (only the eel is lifted). The head, eyes, beak,
mantle, the two rising arms and both feeding tentacles are authored above that
line so a surfaced kraken still reads; floor arms stay below it.

This module also carries a small tentacle toolkit (swept limbs with a sucker
side, attached sucker cups, a direction-chain pose solver) that the tentacle
horror imports read-only. It never changes shared modules.
"""
import hashlib
import json
import math
from . import iqm, connected_skin
from .rat import ROOT, Part, spline, ellipsoid, tube
from .rat import add, sub, mul  # noqa: F401 - blender_skeletal reads rigdata.sub/add
from .skeletal import Rig, axis, between, inverse, qmul, rotate, assemble, sample_clips

TAU = math.tau
SKIN = 'graphics/BRGKRAK.png'
MODEL = 'models/monsters/39_kraken.iqm'
SKIN_VOXEL_SIZE = .2
SKIN_FACE_BUDGET = 11000


def CONNECTED_SKIN(name):
    return name.startswith('skin_')


# ------------------------------------------------------------------ helpers
# Explicit arithmetic (no float sum()) so Blender's Python and the system
# Python agree bit for bit on everything that feeds the bake fingerprint.
def r6(v): return tuple(round(c, 6) for c in v)
def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def norm(a): return math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])
def crs(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def lerp(a, b, t): return tuple(x+(y-x)*t for x, y in zip(a, b))
def clamp(v, lo=0., hi=1.): return max(lo, min(hi, v))
def smooth(t): t = clamp(t); return t*t*(3-2*t)
def bell(t): t = clamp(t); return math.sin(math.pi*t)**2


def unit(a):
    n = norm(a)
    return (a[0]/n, a[1]/n, a[2]/n) if n > 1e-12 else (0., 0., 1.)


def quantize(raw):
    """Merge, normalise with fsum and round to 1e-6; the last weight takes the remainder."""
    merged = {}
    for b, w in raw:
        if w > 1e-9:
            merged[b] = merged.get(b, 0.)+w
    items = sorted(merged.items())
    if len(items) == 1:
        return [(items[0][0], 1)]
    total = math.fsum(w for _, w in items)
    out = [(b, round(w/total, 6)) for b, w in items[:-1]]
    out = [(b, w) for b, w in out if w > 0]
    rest = round(1-math.fsum(w for _, w in out), 6)
    if rest > 0:
        out.append((items[-1][0], rest))
    return [(out[0][0], 1)] if len(out) == 1 else out


class Limb:
    """A swept tentacle. Controls are (x, y, z, vx, vy, vz, radius); v points to
    the sucker (oral) side and is re-projected perpendicular to the tangent, so
    the sucker line never twists. Bones run from the body exit to the tip."""

    def __init__(self, name, controls, bones=9, sides=18, samples=6, exit=0., parent='head',
                 flatten=.13, ridges=0, ridge_depth=0., cup_span=(.1, .96), cup_rows=2, cup_scale=.34,
                 cup_filter=None, prefix='skin_', cup_spacing=1.):
        self.name, self.parent, self.sides, self.flatten = name, parent, sides, flatten
        self.ridges, self.ridge_depth = ridges, ridge_depth
        self.prefix = prefix
        self.cup_spacing = cup_spacing
        rows = spline([tuple(c) for c in controls], samples)
        centers = [r6(r[:3]) for r in rows]
        arcs = [0.]
        for a, b in zip(centers, centers[1:]):
            arcs.append(arcs[-1]+norm(sub(b, a)))
        self.length = arcs[-1]
        self.rows = []
        previous = None
        for i, (c, row) in enumerate(zip(centers, rows)):
            T = unit(sub(centers[min(i+1, len(centers)-1)], centers[max(i-1, 0)]))
            ref = row[3:6]
            V = sub(ref, mul(T, dot(ref, T)))
            V = unit(V) if norm(V) > 1e-4 else previous
            previous = V
            self.rows.append(dict(c=c, T=T, V=V, L=unit(crs(T, V)), arc=arcs[i], s=arcs[i]/self.length,
                                  r=max(.05, row[6])))
        self.exit = exit
        end = .955*self.length
        self.bone_arcs = [exit+(end-exit)*k/(bones-1) for k in range(bones)]
        self.bone_names = [f'{name}_{k}' for k in range(bones)]
        self.bone_points = [r6(self.at(a)['c']) for a in self.bone_arcs]
        self.cup_span, self.cup_rows, self.cup_scale, self.cup_filter = cup_span, cup_rows, cup_scale, cup_filter

    def at(self, arc):
        rows = self.rows
        if arc <= 0:
            return rows[0]
        if arc >= self.length:
            return rows[-1]
        lo, hi = 0, len(rows)-1
        while hi-lo > 1:
            mid = (lo+hi)//2
            if rows[mid]['arc'] <= arc:
                lo = mid
            else:
                hi = mid
        a, b = rows[lo], rows[hi]
        t = (arc-a['arc'])/(b['arc']-a['arc'])
        T = unit(lerp(a['T'], b['T'], t))
        V = unit(sub(lerp(a['V'], b['V'], t), mul(T, dot(lerp(a['V'], b['V'], t), T))))
        return dict(c=lerp(a['c'], b['c'], t), T=T, V=V, L=unit(crs(T, V)), arc=arc, s=arc/self.length,
                    r=a['r']+(b['r']-a['r'])*t)

    def bones_near(self, arc):
        """Bone names whose segments cover arc (used to seat cups on their own limb)."""
        j = max([k for k, a in enumerate(self.bone_arcs) if a <= arc] or [0])
        return {self.bone_names[k] for k in range(max(0, j-1), min(len(self.bone_names), j+3))}

    def section(self, angle):
        """Radius factor: a flatter oral face and optional longitudinal ridges."""
        c = math.cos(angle)
        f = 1-self.flatten*max(0., c)**3
        if self.ridges:
            f *= 1+self.ridge_depth*math.cos(self.ridges*angle)
        return f

    def part(self):
        p = Part(self.prefix+self.name)
        S = self.sides
        for row in self.rows:
            for j in range(S+1):
                a = TAU*(j % S)/S
                d = add(mul(row['V'], math.cos(a)), mul(row['L'], math.sin(a)))
                p.vertices.append(r6(add(row['c'], mul(d, row['r']*self.section(a)))))
                p.uv.append((round(row['s'], 6), round(j/S, 6)))
        for i in range(len(self.rows)-1):
            for j in range(S):
                a = i*(S+1)+j
                p.faces.append((a, a+1, a+S+2, a+S+1))
        for end, reverse in ((0, True), (len(self.rows)-1, False)):
            centre = len(p.vertices)
            p.vertices.append(self.rows[end]['c'])
            p.uv.append((round(self.rows[end]['s'], 6), .5))
            for j in range(S):
                a = end*(S+1)+j
                p.faces.append((centre, a+1, a) if reverse else (centre, a, a+1))
        return p

    def cups(self):
        """Sucker cup placements (centre, normal, tangent, size) on the oral side."""
        out = []
        arc = max(self.exit+2.0, self.cup_span[0]*self.length)  # clear of the fused root web
        k = 0
        while arc < self.cup_span[1]*self.length:
            row = self.at(arc)
            r = row['r']
            if r < .38:
                break
            double = self.cup_rows == 2 and r > .8
            angle = (.52 if k % 2 else -.52) if double else 0.
            d = unit(add(mul(row['V'], math.cos(angle)), mul(row['L'], math.sin(angle))))
            size = self.cup_scale*r*(.82 if double else 1.)
            centre = add(row['c'], mul(d, r*self.section(angle)-.18*size))
            if self.cup_filter is None or self.cup_filter(centre, d, row):
                out.append((r6(centre), d, row['T'], size, arc))
            arc += self.cup_spacing*max(.34, (.62 if double else 1.05)*r*self.cup_scale/.34)
            k += 1
        return out


def cup_part(name, centre, n, tangent, size, uv_strip):
    """A small sucker cup: skirt, raised pale rim and a dark pit (30 triangles)."""
    e1 = unit(sub(tangent, mul(n, dot(tangent, n))))
    e2 = crs(n, e1)
    p = Part(name)
    S = 6
    rings = ((1.0, -.30, 1.), (.98, .30, .78), (.60, .22, .52))
    for radius, height, u in rings:
        for j in range(S):
            a = TAU*j/S
            d = add(mul(e1, math.cos(a)), mul(e2, math.sin(a)))
            p.vertices.append(r6(add(centre, add(mul(d, radius*size), mul(n, height*size)))))
            p.uv.append(uv_strip(u))
    p.vertices.append(r6(add(centre, mul(n, -.12*size))))
    p.uv.append(uv_strip(0.))
    for k in range(2):
        for j in range(S):
            a, b = k*S+j, k*S+(j+1) % S
            p.faces.append((a, b, b+S, a+S))
    pit = 3*S
    for j in range(S):
        p.faces.append((2*S+j, 2*S+(j+1) % S, pit))
    return p


def floor_spiral(limb, root, heading, curl, lift=0., drop_rate=.85):
    """Bone targets for a limp limb: slide down to the floor from root, then run
    along heading (radians) with a tightening curl (radians/unit at the tip)."""
    pts = [root]
    cur = root
    theta = heading
    n = len(limb.bone_arcs)
    for k in range(1, n):
        ds = limb.bone_arcs[k]-limb.bone_arcs[k-1]
        theta += curl*(k/(n-1))**1.6*ds
        floor = limb.floor_z[k]+lift
        dz = -min(ds*drop_rate, max(0., cur[2]-floor))
        h = math.sqrt(max(0., ds*ds-dz*dz))
        cur = (cur[0]+h*math.cos(theta), cur[1]+h*math.sin(theta), cur[2]+dz)
        pts.append(cur)
    return pts


class Chains:
    """Rig wrapper: limbs, pose frames and the direction-chain solver."""

    def __init__(self, specs, limbs):
        self.rig = Rig.from_world(specs)
        self.bones, self.rest = self.rig.bones, self.rig.rest
        self.ids = {n: i for i, (n, p, v) in enumerate(self.bones)}
        self.limbs = limbs
        for limb in limbs:
            limb.ids = [self.ids[b] for b in limb.bone_names]
            cup = limb.cup_scale*.35
            # The rest centreline bows between bones (curled tips); a flat chord
            # would push that bow through the floor, so add each segment's sag.
            sag = [chord_sag(limb, a, b) for a, b in zip(limb.bone_arcs, limb.bone_arcs[1:])]+[0.]
            limb.floor_z = [limb.at(a)['r']*1.08+cup+.6+max(sag[k], sag[k-1] if k else 0.)
                            for k, a in enumerate(limb.bone_arcs)]

    def frame(self):
        return [[*local, 0., 0., 0., 1., 1, 1, 1] for _, _, local in self.bones]

    def turn(self, f, bone, direction, degrees):
        i = self.ids[bone]
        f[i][3:7] = list(qmul(tuple(f[i][3:7]), axis(direction, math.radians(degrees))))

    def move(self, f, bone, delta):
        i = self.ids[bone]
        f[i][0:3] = list(add(tuple(f[i][0:3]), delta))

    def root_of(self, world, f, limb):
        ploc, pq = world[self.ids[limb.parent]]
        return add(ploc, rotate(pq, tuple(f[limb.ids[0]][:3])))

    def aim(self, f, world, ids, parent, targets, floor=None, tip=None):
        """Point each bone at the next target; lengths and unit scales are kept.

        tip is the rest offset from the last bone to the limb's tip; it keeps
        the final segment continuing the curve instead of hanging rigidly."""
        ploc, qp = world[parent]
        loc = add(ploc, rotate(qp, tuple(f[ids[0]][:3])))
        desired = None
        for j in range(len(ids)-1):
            want = targets[j+1]
            if floor is not None:
                want = (want[0], want[1], max(want[2], floor[j+1]))
            rest = sub(self.rest[ids[j+1]], self.rest[ids[j]])
            desired = unit(sub(want, loc))
            if floor is not None:
                desired = supported(loc, desired, norm(rest), floor[j+1])
            qw = qmul(between(rotate(qp, rest), desired), qp)
            f[ids[j]][3:7] = list(qmul(inverse(qp), qw))
            loc = add(loc, rotate(qw, rest))
            qp = qw
        f[ids[-1]][3:7] = [0., 0., 0., 1.]
        if tip is not None and desired is not None and floor is not None:
            span = norm(tip)
            ahead = supported(loc, rotate(qp, unit(tip)), span, floor[-1]*.8)
            qw = qmul(between(rotate(qp, tip), mul(ahead, span)), qp)
            f[ids[-1]][3:7] = list(qmul(inverse(qp), qw))

    def aim_limb(self, f, world, limb, targets, floor=True, margin=0.):
        self.aim(f, world, limb.ids, self.ids[limb.parent], targets, [z+margin for z in limb.floor_z] if floor else None,
                 sub(limb.rows[-1]['c'], limb.bone_points[-1]))


def chord_sag(limb, a, b):
    """Largest distance of the rest centreline from the bone chord a..b (plus the tip)."""
    p, q = limb.at(a)['c'], limb.at(b if b < limb.bone_arcs[-1] else limb.length)['c']
    d = unit(sub(q, p))
    worst = 0.
    for row in limb.rows:
        if a <= row['arc'] <= (b if b < limb.bone_arcs[-1] else limb.length):
            o = sub(row['c'], p)
            worst = max(worst, norm(sub(o, mul(d, dot(o, d)))))
    return worst


def supported(loc, desired, span, floor):
    """Tilt a segment direction up just enough that its end stays above floor."""
    if loc[2]+desired[2]*span >= floor:
        return desired
    dz = clamp(floor-loc[2], -span, span)
    flat = (desired[0], desired[1], 0.)
    flat = unit(flat) if norm(flat) > 1e-6 else (1., 0., 0.)
    h = math.sqrt(max(0., span*span-dz*dz))
    return unit(add(mul(flat, h), (0., 0., dz)))


def relative(shape, root):
    d = sub(root, shape[0])
    return [add(p, d) for p in shape]


def blend_shapes(keys, t):
    """keys: [(time, shape), ...] sorted; smoothstep between neighbours."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t <= t1:
            w = smooth((t-t0)/(t1-t0))
            return [lerp(p, q, w) for p, q in zip(a, b)]
    return keys[-1][1]


def resample(limb, controls):
    """Bone targets along a control polyline (x, y, z) starting at the exit bone."""
    pts = spline([tuple(c) for c in controls], 8)
    arcs = [0.]
    for a, b in zip(pts, pts[1:]):
        arcs.append(arcs[-1]+norm(sub(b, a)))
    out = []
    for k, arc in enumerate(limb.bone_arcs):
        d = arc-limb.bone_arcs[0]
        if d >= arcs[-1]:
            tail = unit(sub(pts[-1], pts[-2]))
            out.append(add(pts[-1], mul(tail, d-arcs[-1])))
            continue
        i = max(j for j in range(len(arcs)) if arcs[j] <= d)
        t = (d-arcs[i])/max(1e-9, arcs[i+1]-arcs[i])
        out.append(lerp(pts[i], pts[i+1], t))
    return out


def osc(phase, x):
    """sin(x) re-based so a looping clip starts exactly at the rest pose."""
    return math.sin(x)-math.sin(x-phase)


def wiggle(shape, amp, phase, wave=.75, power=1.3, vertical=.6, lateral_only=False, start=None):
    """Travelling wave offsets; with start, offsets are zero at phase == start."""
    chord = sub(shape[-1], shape[0])
    side = unit(crs(chord, (0, 0, 1))) if norm(crs(chord, (0, 0, 1))) > 1e-6 else (0., 1., 0.)
    up = unit(crs(side, chord))
    n = len(shape)-1
    out = []
    for j, p in enumerate(shape):
        w = amp*(j/n)**power
        a, b = math.sin(phase-wave*j), math.cos(phase-wave*j)
        if start is not None:
            a, b = a-math.sin(start-wave*j), b-math.cos(start-wave*j)
        o = mul(side, w*a)
        if not lateral_only:
            o = add(o, mul(up, vertical*w*b))
        out.append(add(p, o))
    return out


def iqm_bytes(v, n, uv, t, w, bones, clips, bounds, label, skin):
    return iqm.encode(v, n, uv, t, w, bones, clips, bounds, mesh_label=label, material_path=skin)


# ------------------------------------------------------------------ anatomy
HEAD_C = (4., 0., 26.)
HEAD_R = (10.5, 11.5, 9.5)
CROWN = (11.5, 0., 20.)
A = unit((1., 0., -.5))          # crown axis: the mouth faces forward and down
U = unit((.5, 0., 1.))           # crown "up", perpendicular to A
Y = (0., 1., 0.)
EYE_R = 3.8


def crown(a, u, y=0.):
    return add(CROWN, add(mul(A, a), add(mul(U, u), mul(Y, y))))


def rad(deg, side):
    t = math.radians(deg)
    return add(mul(U, math.cos(t)), mul(Y, side*math.sin(t)))


# Eyes face the player (+X) from the front corners of the head, above the arm crown.
def eye_centre(side): return (11.0, side*8.2, 30.5)
def eye_gaze(side): return unit((.84, side*.52, .12))


def arm_radius(s, r0=3.1, tip=.5, power=1.15):
    return tip+(r0-tip)*(1-s)**power


def arm_controls(deg, side, path, refs, r0=3.1, tip=.5, power=1.15, club=None):
    """Root inside the head, exit at the crown ring, then the authored path."""
    rd = rad(deg, side)
    pts = [add(crown(-1.0, 0.), mul(rd, 2.5)), add(crown(2.2, 0.), mul(rd, 5.2))]
    pts += [(x, side*y, z) for x, y, z in path]
    arcs = [0.]
    for a, b in zip(pts, pts[1:]):
        arcs.append(arcs[-1]+norm(sub(b, a)))
    out = []
    for p, arc, ref in zip(pts, arcs, refs):
        s = arc/arcs[-1]
        r = arm_radius(s, r0, tip, power)
        if club:
            r += club[0]*bell((s-club[1])/club[2])
        out.append((*r6(p), ref[0], side*ref[1], ref[2], round(r, 6)))
    return out, arcs[1]


def not_floor_facing(centre, n, row):
    """Cups pressed against the floor are hidden; keep the visible ones."""
    return not (n[2] < -.45 and centre[2] < row['r']+2.2)


LIMB_SPECS = []
for _side, _tag in ((1, 'L'), (-1, 'R')):
    LIMB_SPECS += [
        # Rising arms flank the face (never across it) and curl forward at the tip.
        (f'riser_{_tag}', 35, _side,
         [(17, 10, 23.5), (18.5, 15.5, 27), (17.5, 19, 32.5), (15, 20, 38.5), (13, 18.5, 43), (15.5, 16.5, 45.5),
          (18.5, 16, 43.5), (19, 15.5, 40)],
         # Suckers face back and in toward the head: from the front the rising
         # arms show dark maroon backs with a pale inner edge, framing the face.
         [(-1, -.3, -.3), (-1, -.3, -.2), (-.8, -.5, -.2), (-.5, -.8, 0), (-.3, -.9, .1), (-.3, -.9, 0),
          (-.2, -.8, -.4), (-.2, -.3, -.9), (.3, 0, -1), (.9, 0, -.3)],
         dict(r0=3.8, power=1.5)),
        (f'club_{_tag}', 62, _side,
         [(15, 12, 22), (12, 18.5, 25), (7, 23.5, 29.5), (2, 25.5, 35), (-1.5, 24.5, 40.5), (-1, 21.5, 45),
          (2.5, 19.5, 46.5), (5.5, 20.5, 44.5), (6, 22.5, 41)],
         [(1, -.5, 0), (1, -.5, 0), (.8, -.6, 0), (.6, -.8, .1), (.5, -.8, .2), (.6, -.7, .2), (.8, -.5, .2),
          (1, -.3, -.3), (.8, 0, -.8), (0, 0, -1), (-.8, 0, -.6)],
         dict(r0=2.8, tip=.45, power=1.5, club=(1.3, .66, .30))),
        # Heavy floor arms sprawl and coil in S-curves round the low body.
        (f'side_{_tag}', 88, _side,
         [(14, 11, 13.5), (13.5, 16.5, 7.5), (15, 21, 5), (20, 23.5, 4.6), (24.5, 21.5, 4.4), (26.5, 18.5, 4.4),
          (23.5, 16, 4.8), (21, 17, 6.5)],
         [(.3, -.5, -.5), (0, .3, -1), (0, .3, -1), (0, .2, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1), (.3, .6, -.4),
          (.8, .8, 0), (.6, .6, .6)],
         dict(r0=4.2, power=1.6)),
        (f'rear_{_tag}', 118, _side,
         [(8.5, 10.5, 12), (2.5, 14.5, 6.5), (-5, 17.5, 4.8), (-12, 21, 4.5), (-19, 22.5, 4.4), (-24.5, 19, 4.4),
          (-25, 13.5, 4.5), (-21, 11, 5.5), (-18, 13, 7.5)],
         [(.3, -.6, -.5), (0, .2, -1), (0, .2, -1), (0, .1, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1), (.3, -.4, -.8),
          (.8, -.4, -.3), (.9, .3, .2), (.4, .4, .8)],
         dict(r0=4.0, power=1.6)),
        (f'front_{_tag}', 152, _side,
         [(15.5, 4, 9.5), (19.5, 5.5, 5.5), (23.5, 5, 4.5), (26.5, 6.5, 4.4), (27.5, 10, 4.5), (25.5, 11.5, 5.5),
          (23.5, 10, 7.5)],
         [(.3, -.8, -.3), (0, -.3, -1), (0, -.2, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1), (-.5, -.6, -.4),
          (-.8, -.2, .4), (-.4, .2, .9)],
         dict(r0=3.6, power=1.6)),
    ]
for _spec in LIMB_SPECS:
    assert len(_spec[4]) == len(_spec[3])+2, _spec[0]


def make_limbs():
    limbs = []
    for name, deg, side, path, refs, kw in LIMB_SPECS:
        controls, exit_arc = arm_controls(deg, side, path, refs, **kw)
        limbs.append(Limb(name, controls, bones=9, sides=18, samples=6, exit=exit_arc,
                          cup_filter=not_floor_facing, cup_rows=2, cup_spacing=1.25))
    return limbs


# A low mantle that leans well back behind and above the head.
MANTLE = Limb('mantle', [(2, 0, 29, 1, 0, 0, 10.2), (-3, 0, 34.5, 1, 0, 0, 12.0), (-9, 0, 40, 1, 0, 0, 12.2),
                         (-15, 0, 44.5, 1, 0, 0, 10.5), (-19.5, 0, 48, 1, 0, 0, 7.5), (-22, 0, 50.3, 1, 0, 0, 3.8),
                         (-22.6, 0, 51, 1, 0, 0, .6)],
              bones=4, sides=40, samples=6, exit=6.0, flatten=.04, ridges=9, ridge_depth=.03, cup_rows=0)
LIMBS = make_limbs()
MANTLE_BONES = ['mantle_0', 'mantle_1', 'mantle_2', 'mantle_3']
SPECS = [('root', None, (0., 0., 0.)), ('head', 'root', (4., 0., 23.)), ('beak', 'head', r6(crown(1.2, -.9)))]
for _k, _p in enumerate(MANTLE.bone_points):
    SPECS.append((MANTLE_BONES[_k], 'head' if _k == 0 else MANTLE_BONES[_k-1], _p))
for _limb in LIMBS:
    for _k, (_n, _p) in enumerate(zip(_limb.bone_names, _limb.bone_points)):
        SPECS.append((_n, _limb.parent if _k == 0 else _limb.bone_names[_k-1], _p))
KIT = Chains(SPECS, LIMBS)
RIG, BONES, REST, IDS = KIT.rig, KIT.bones, KIT.rest, KIT.ids
MANTLE.ids = [IDS[b] for b in MANTLE_BONES]
MANTLE.floor_z = [MANTLE.at(a)['r']*1.02+.6 for a in MANTLE.bone_arcs]
BY_NAME = {l.name: l for l in LIMBS}
CLIPS = [('idle', 40, 20, True), ('surge', 32, 35, True), ('slap', 25, 35, False),
         ('seize', 29, 35, False), ('recoil', 15, 35, False), ('sink', 37, 35, False)]


def accessory_strip(y):
    """Accessory-quadrant UV on a 1-D painted strip (see kraken_materials)."""
    return lambda u: (round(.02+.96*clamp(u), 6), round(1-y/1024, 6))


def build_eye(side):
    c, g = eye_centre(side), eye_gaze(side)
    p = ellipsoid(f'eye_{"L" if side > 0 else "R"}', c, (EYE_R,)*3, 'fur', 28, 16)
    e1 = unit(crs(g, (0, 0, 1)))
    e2 = crs(e1, g)
    uv = []
    for v in p.vertices:
        o = sub(v, c)
        a, b, f = dot(o, e1)/EYE_R, dot(o, e2)/EYE_R, dot(o, g)/EYE_R
        if f < 0:   # behind the equator: fold onto the dark limbal edge
            m = math.hypot(a, b) or 1
            a, b = a/m, b/m
        # Eye disc occupies accessory pixels 0..512 in both axes.
        uv.append((round((256+238*a*side)/1024, 6), round(1-(256-238*b)/1024, 6)))
    p.uv = uv
    p.vertices = [r6(v) for v in p.vertices]
    return p


def build_beak():
    parts = []
    for name, y, rows in (('beak_upper', 680, [(1.5, .6, 2.1), (3.2, .8, 1.8), (4.8, .4, 1.25), (5.9, -.5, .75),
                                               (6.2, -1.6, .4), (5.8, -2.4, .12)]),
                          ('beak_lower', 760, [(1.6, -1.5, 1.7), (3.2, -1.9, 1.3), (4.4, -1.8, .75), (4.9, -1.2, .3),
                                               (4.9, -.8, .08)])):
        # A heavy parrot beak, scaled up to read from the front at distance.
        rows = [(1.5+(a-1.5)*1.45, u*1.45, r*1.4) for a, u, r in rows]
        p = tube(name, [(*crown(a, u), r) for a, u, r in rows], 'fur', 14, 4)
        # Painted strip: amber base to a glossy black hooked tip.
        base = crown(rows[0][0], rows[0][1])
        span = norm(sub(crown(rows[-1][0], rows[-1][1]), base))
        strip = accessory_strip(y)
        p.uv = [strip(norm(sub(v, base))/span) for v in p.vertices]
        p.vertices = [r6(v) for v in p.vertices]
        parts.append(p)
    return parts


def build_parts():
    parts = []
    head = ellipsoid('skin_head', HEAD_C, HEAD_R, 'fur', 40, 22)
    parts.append(head)
    parts.append(ellipsoid('skin_buccal', crown(-.8, 0.), (3.8, 4.2, 3.8), 'fur', 24, 14))
    for k in range(8):
        d = rad(22.5+45*k, 1)
        parts.append(ellipsoid(f'skin_lip_{k}', add(crown(2.4, 0.), mul(d, 3.4)), (1.7, 1.7, 1.7), 'fur', 14, 8))
    for side, tag in ((1, 'L'), (-1, 'R')):
        parts.append(ellipsoid(f'skin_bulge_{tag}', (9.3, side*7.2, 30.0), (5.0, 4.3, 5.0), 'fur', 26, 14))
        parts.append(ellipsoid(f'skin_lid_{tag}', (11.0, side*8.0, 34.4), (4.4, 3.6, 1.9), 'fur', 22, 12))
        parts.append(ellipsoid(f'skin_low_{tag}', (11.8, side*8.6, 27.0), (3.8, 3.2, 1.4), 'fur', 20, 10))
    parts.append(MANTLE.part())
    for limb in LIMBS:
        parts.append(limb.part())
    for p in parts:
        p.vertices = [r6(v) for v in p.vertices]
        p.uv = [(round(u, 6), round(v, 6)) for u, v in p.uv]
    parts += [build_eye(1), build_eye(-1)]
    parts += build_beak()
    strip = accessory_strip(600)
    for limb in LIMBS:
        for k, (centre, n, tangent, size, arc) in enumerate(limb.cups()):
            cup = cup_part(f'cup_{limb.name}_{k}', centre, n, tangent, size, strip)
            cup.anchor = centre
            cup.bones = limb.bones_near(arc)
            parts.append(cup)
    return parts


def limb_weights(limb, arc, v):
    raw = RIG.chain_weights(v, limb.ids)
    blend = smooth((arc-(limb.exit-1.6))/2.4)
    out = [(IDS[limb.parent], 1-blend)]+[(b, w*blend) for b, w in raw]
    return quantize(out)


def weights(part, v, uv):
    n = part.name
    if n == 'skin_mantle':
        return quantize(RIG.chain_weights(v, [IDS['head']]+MANTLE.ids))
    if n.startswith('skin_') and n[5:] in BY_NAME:
        limb = BY_NAME[n[5:]]
        return limb_weights(limb, uv[0]*limb.length, v)
    if n == 'beak_lower':
        return [(IDS['beak'], 1)]
    if n.startswith('cup_'):
        # Preview-only fallback; geometry() replaces cup weights with the
        # nearest baked skin vertex's normalised weights.
        limb = BY_NAME[n[4:].rsplit('_', 1)[0]]
        return quantize(RIG.chain_weights(v, limb.ids))
    return [(IDS['head'], 1)]


_GEOMETRY = {}


def point_triangle(p, a, b, c):
    """Distance from p to triangle abc (Ericson's closest-point regions)."""
    sub = lambda u, v: (u[0]-v[0], u[1]-v[1], u[2]-v[2])
    dot = lambda u, v: u[0]*v[0]+u[1]*v[1]+u[2]*v[2]
    ab, ac, ap = sub(b, a), sub(c, a), sub(p, a)
    d1, d2 = dot(ab, ap), dot(ac, ap)
    if d1 <= 0 and d2 <= 0:
        return math.dist(p, a)
    bp = sub(p, b)
    d3, d4 = dot(ab, bp), dot(ac, bp)
    if d3 >= 0 and d4 <= d3:
        return math.dist(p, b)
    cp = sub(p, c)
    d5, d6 = dot(ab, cp), dot(ac, cp)
    if d6 >= 0 and d5 <= d6:
        return math.dist(p, c)
    vc, vb, va = d1*d4-d3*d2, d5*d2-d1*d6, d3*d6-d5*d4
    if vc <= 0 and d1 >= 0 and d3 <= 0:
        t = d1/(d1-d3)
        return math.dist(p, tuple(x+t*y for x, y in zip(a, ab)))
    if vb <= 0 and d2 >= 0 and d6 <= 0:
        t = d2/(d2-d6)
        return math.dist(p, tuple(x+t*y for x, y in zip(a, ac)))
    if va <= 0 and d4-d3 >= 0 and d5-d6 >= 0:
        t = (d4-d3)/((d4-d3)+(d5-d6))
        return math.dist(p, tuple(x+t*(y-x) for x, y in zip(b, c)))
    den = 1/(va+vb+vc)
    v, w = vb*den, vc*den
    return math.dist(p, tuple(x+v*y+w*z for x, y, z in zip(a, ab, ac)))


def closest_bary(p, a, b, c):
    """Distance from p to triangle abc and barycentric weights of the closest point."""
    ab, ac, ap = sub(b, a), sub(c, a), sub(p, a)
    d1, d2 = dot(ab, ap), dot(ac, ap)
    if d1 <= 0 and d2 <= 0:
        return norm(ap), (1., 0., 0.)
    bp = sub(p, b)
    d3, d4 = dot(ab, bp), dot(ac, bp)
    if d3 >= 0 and d4 <= d3:
        return norm(bp), (0., 1., 0.)
    cp = sub(p, c)
    d5, d6 = dot(ab, cp), dot(ac, cp)
    if d6 >= 0 and d5 <= d6:
        return norm(cp), (0., 0., 1.)
    vc, vb, va = d1*d4-d3*d2, d5*d2-d1*d6, d3*d6-d5*d4
    if vc <= 0 and d1 >= 0 and d3 <= 0:
        t = d1/(d1-d3)
        bary = (1-t, t, 0.)
    elif vb <= 0 and d2 >= 0 and d6 <= 0:
        t = d2/(d2-d6)
        bary = (1-t, 0., t)
    elif va <= 0 and d4-d3 >= 0 and d5-d6 >= 0:
        t = (d4-d3)/((d4-d3)+(d5-d6))
        bary = (0., 1-t, t)
    else:
        den = 1/(va+vb+vc)
        bary = (1-(vb+vc)*den, vb*den, vc*den)
    q = add(mul(a, bary[0]), add(mul(b, bary[1]), mul(c, bary[2])))
    return norm(sub(p, q)), bary


def attach_cups(parts, names=None):
    """Seat cups on the baked skin: drop any the fused root web has buried and
    give the rest the skin's own weights, interpolated at the closest point of
    the closest skin triangle driven by the cup's limb segment (so a coiled
    tip's neighbouring turn, closer in space but moving differently, is never
    used). The four strongest influences are kept and renormalised."""
    skin = parts[0]
    tri_cells = {}
    key = lambda p: tuple(int(math.floor(c/2)) for c in p)
    for t in skin.triangles():
        corners = tuple(skin.vertices[i] for i in t)
        weights = tuple(skin.skin_weights[i] for i in t)
        for k in {key(c) for c in corners}:
            tri_cells.setdefault(k, []).append((corners, weights))
    near = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)]
    kept = [skin]
    for p in parts[1:]:
        if not p.name.startswith('cup_'):
            kept.append(p)
            continue
        k0 = key(p.anchor)
        candidates = [t for d in near for t in tri_cells.get((k0[0]+d[0], k0[1]+d[1], k0[2]+d[2]), ())]
        surface = min((point_triangle(p.anchor, *c) for c, w in candidates), default=9.)
        if surface > .3:
            continue
        best = None
        for corners, weights in candidates:
            if names is not None and not any(
                    names[max(w, key=lambda x: (x[1], -x[0]))[0]] in p.bones for w in weights):
                continue
            dist, bary = closest_bary(p.anchor, *corners)
            if best is None or dist < best[0]:
                best = (dist, bary, weights)
        if best is None:
            continue
        dist, bary, weights = best
        blend = {}
        for f, w in zip(bary, weights):
            for bone, x in w:
                blend[bone] = blend.get(bone, 0.)+f*x
        top = sorted(blend.items(), key=lambda x: (-x[1], x[0]))[:4]
        p.anchor_distance, p.surface_distance = dist, surface
        p.skin_weights = [quantize(top)]*len(p.vertices)
        kept.append(p)
    parts[:] = kept


def skin_parts():
    parts = connected_skin.attach('kraken', build_parts(), weights)
    parts[0].skin_weights = [[tuple(x) for x in w] for w in parts[0].skin_weights]
    attach_cups(parts, [b[0] for b in BONES])
    return parts


def geometry():
    if 'g' not in _GEOMETRY:
        from . import kraken_materials as materials
        _GEOMETRY['g'] = assemble(materials.connected_atlas(skin_parts()), weights)
    return _GEOMETRY['g']


# ------------------------------------------------------------------ poses
def shapes():
    """Key target shapes (bone positions) per limb, relative to the rest root."""
    if hasattr(shapes, 'cache'):
        return shapes.cache
    S = {}
    for limb in LIMBS:
        side = 1 if limb.name.endswith('_L') else -1
        kind = limb.name.split('_')[0]
        b0 = limb.bone_points[0]

        def path(pts, b0=b0, side=side, limb=limb):
            return resample(limb, [b0]+[(x, side*y, z) for x, y, z in pts])
        d = {'rest': list(limb.bone_points)}
        if kind == 'riser':
            d['high'] = path([(17, 10, 27), (15, 14, 34), (11, 15.5, 41), (6, 15, 46), (2.5, 12.5, 48), (1.5, 9.5, 46)])
            # Middle-frame slap: a whip that swings wide, cracks forward and hooks its tip.
            d['lash'] = path([(19.5, 13, 27), (23.5, 20, 31), (28, 21.5, 27.5), (30, 17, 22.5), (29.5, 11, 19.5), (27, 7, 20),
                              (25.5, 6, 23.5), (26.5, 8, 26)])
            d['overhead'] = path([(17, 9, 27), (16.5, 12, 35), (13, 13, 42), (8, 12, 47), (4, 9.5, 49), (3, 6.5, 46.5)])
            d['grab'] = path([(19, 9, 24), (24, 9, 26), (27.5, 6.5, 24), (27.5, 3, 19), (24.5, 1, 16), (22, 2, 18)])
            d['flinch'] = path([(15, 11, 27), (12, 15.5, 33), (8, 18, 39), (3.5, 18.5, 43), (0, 16.5, 45), (-1, 13.5, 43)])
        elif kind == 'club':
            d['cock'] = path([(13, 13, 24), (8, 18, 30), (2, 21, 36), (-4, 21.5, 41), (-8, 19.5, 45), (-8, 15.5, 48),
                              (-4, 13.5, 48.5)])
            d['grab'] = path([(17, 11, 24), (20, 14, 31), (23.5, 14, 36), (27, 11, 34), (28.5, 7.5, 28), (28, 4.5, 21),
                              (26, 2.2, 15.5), (23.5, 1.5, 13), (21.5, 3, 14.5)])
            d['drag'] = path([(16, 10, 23), (18, 14, 29), (20.5, 15, 33), (23, 12, 32), (24, 8, 27), (23, 5, 21),
                              (20.5, 2.5, 17), (18, 1.5, 15.5), (16.5, 3, 17.5)])
            d['flare'] = path([(14, 14, 23), (10, 20, 28), (6, 24, 34), (1.5, 26, 39.5), (-2.5, 25.5, 44), (-4.5, 22.5, 47),
                               (-3, 19.5, 49), (.5, 18.5, 48)])
            d['flinch'] = path([(12, 13, 25), (7, 18, 31), (1, 21, 37), (-5, 21, 41), (-9, 18.5, 44), (-10, 14.5, 45),
                                (-8, 12, 47)])
        S[limb.name] = d
    shapes.cache = S
    return S


def body(f, name, t):
    """Head, beak and mantle; returns nothing (mantle aimed separately in sink)."""
    phase = TAU*t
    K = KIT
    if name == 'idle':
        K.move(f, 'head', (0, 0, .6*osc(phase, phase)))
        K.turn(f, 'head', (0, 1, 0), 1.5*osc(phase, phase+.5))
        for k, b in enumerate(MANTLE_BONES[:3]):
            K.turn(f, b, (0, 1, 0), (3+k)*osc(phase, phase-.6*(k+1)))
            K.turn(f, b, (1, 0, 0), 1.5*osc(phase, phase-.6*(k+1)+1))
        K.turn(f, 'beak', (0, 1, 0), 8*math.sin(phase)**2)
    elif name == 'surge':
        K.move(f, 'head', (1.0*osc(phase, phase), 0, 1.6*osc(phase, phase+.4)))
        K.turn(f, 'head', (0, 1, 0), 4*osc(phase, phase))
        for k, b in enumerate(MANTLE_BONES[:3]):
            K.turn(f, b, (0, 1, 0), (5+2*k)*osc(phase, phase-.7*(k+1)))
        K.turn(f, 'beak', (0, 1, 0), 12*math.sin(phase/2)**2)
    elif name == 'slap':
        wind, strike = bell(t/.56), bell((t-.2)/.72)
        # Rear back, then (middle frame) the whole body lunges and the mantle
        # pitches forward over the striking arms.
        K.move(f, 'head', (-2.0*wind+5.0*strike, 0, 1.5*wind-3.0*strike))
        K.turn(f, 'head', (0, 1, 0), -6*wind+26*strike)
        for k, b in enumerate(MANTLE_BONES[:3]):
            K.turn(f, b, (0, 1, 0), -3*wind+11*strike)
        K.turn(f, 'beak', (0, 1, 0), 30*strike)
    elif name == 'seize':
        cock, grab = bell(t/.5), bell((t-.24)/.62)
        K.move(f, 'head', (-2.0*cock+4.0*grab, 0, 1.5*cock-2.5*grab))
        K.turn(f, 'head', (0, 1, 0), -5*cock+21*grab)
        for k, b in enumerate(MANTLE_BONES[:3]):
            K.turn(f, b, (0, 1, 0), -3*cock+9*grab)
        K.turn(f, 'beak', (0, 1, 0), 38*grab)
    elif name == 'recoil':
        p = bell(t)
        K.move(f, 'head', (-2.6*p, 0, 1.2*p))
        K.turn(f, 'head', (0, 1, 0), -6*p)
        K.turn(f, 'head', (1, 0, 0), 5*p)
        for k, b in enumerate(MANTLE_BONES[:3]):
            K.turn(f, b, (0, 1, 0), -3*p)
        K.turn(f, 'beak', (0, 1, 0), -3*p)
    elif name == 'sink':
        q = sink_curve(t)
        K.move(f, 'head', (2.0*q, -1.5*q, -11.5*q))
        K.turn(f, 'head', (0, 0, 1), 18*q)
        K.turn(f, 'head', (1, 0, 0), -18*q)
        K.turn(f, 'head', (0, 1, 0), -48*q)
        K.turn(f, 'beak', (0, 1, 0), 22*bell(t/.8))
    elif name != 'rest':
        raise ValueError(name)


def sink_curve(t):
    # Most of the fall happens by the middle frame; then the body settles.
    return smooth(t/.62)*.9+.1*smooth((t-.5)/.5)


def limb_targets(limb, name, t, root, world):
    S = shapes()[limb.name]
    kind = limb.name.split('_')[0]
    side = 1 if limb.name.endswith('_L') else -1
    k = LIMBS.index(limb)
    phase = TAU*t
    rest = relative(S['rest'], root)
    # Strike shapes are authored in cell space; only the root follows the body,
    # so a lunge cannot carry a blow outside the cell.
    rel = lambda key: [root]+S[key][1:]
    floor = kind in ('side', 'rear', 'front')
    if name in ('idle', 'surge'):
        amp = (1.6 if floor else 2.6)*(1.7 if name == 'surge' else 1.)
        return wiggle(rest, amp, phase+1.3*k, power=2.4 if floor else 1.3, lateral_only=floor, start=1.3*k)
    if name == 'slap':
        if kind == 'riser' and side < 0:   # the arm on the camera-lateral side whips
            return blend_shapes([(0, rest), (.28, rel('high')), (.5, rel('lash')), (.62, rel('lash')), (1, rest)], t)
        if kind == 'riser':
            return blend_shapes([(0, rest), (.3, rel('high')), (.5, rel('overhead')), (.66, rel('overhead')), (1, rest)], t)
        if kind == 'club':
            return blend_shapes([(0, rest), (.3, rel('flare')), (.5, rel('flare')), (1, rest)], t)
        return wiggle(rest, 1.3*bell(t), .8*k+1, power=2.6, lateral_only=True)
    if name == 'seize':
        if kind == 'club':
            return blend_shapes([(0, rest), (.26, rel('cock')), (.5, rel('grab')), (.7, rel('drag')), (1, rest)], t)
        if kind == 'riser':
            return blend_shapes([(0, rest), (.3, rel('high')), (.5, rel('grab')), (.72, rel('grab')), (1, rest)], t)
        return wiggle(rest, 1.2*bell(t), .8*k+2, power=2.6, lateral_only=True)
    if name == 'recoil':
        if kind in ('riser', 'club'):
            return blend_shapes([(0, rest), (.5, rel('flinch')), (1, rest)], t)
        return wiggle(rest, 2.4*bell(t), .8*k, power=2.2, lateral_only=True)
    if name == 'sink':
        dead = dead_shape(limb, root)
        return blend_shapes([(0, rest), (.62, dead), (1, dead)], t)
    raise ValueError(name)


DEAD = {  # heading (degrees), curl (radians per unit at the tip)
    'riser': (42, .20), 'club': (72, .30), 'side': (95, .17), 'rear': (150, .20), 'front': (38, .24)}


def dead_shape(limb, root):
    kind = limb.name.split('_')[0]
    side = 1 if limb.name.endswith('_L') else -1
    heading, curl = DEAD[kind]
    return floor_spiral(limb, root, side*math.radians(heading), side*curl)


def pose(name, t):
    f = KIT.frame()
    body(f, name, t)
    world = RIG.matrices(f)
    if name == 'sink':
        q = sink_curve(t)
        m0 = KIT.root_of(world, f, MANTLE)
        hq = world[IDS['head']][1]
        # The mantle follows the tipped head, then slumps a little further so
        # the head/mantle junction never folds sharply.
        rest = [add(m0, rotate(hq, sub(p, MANTLE.bone_points[0]))) for p in MANTLE.bone_points]
        lying = [m0]
        heading = unit((-.55, -.8, 0.))
        for k in range(1, 4):
            ds = MANTLE.bone_arcs[k]-MANTLE.bone_arcs[k-1]
            lying.append(add(lying[-1], mul(unit(add(heading, (0, 0, -.5+.25*k))), ds)))
        targets = [lerp(a, b, .45*q) for a, b in zip(rest, lying)]
        KIT.aim(f, world, MANTLE.ids, IDS['head'], targets, MANTLE.floor_z)
        world = RIG.matrices(f)
    for limb in LIMBS:
        root = KIT.root_of(world, f, limb)
        # Falling limbs bend hard across several bones; keep a little extra support.
        KIT.aim_limb(f, world, limb, limb_targets(limb, name, t, root, world), margin=.5 if name == 'sink' else 0.)
    return [tuple(r) for r in f]


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from . import kraken_materials as materials
    return materials.connected_atlas(skin_parts(), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm_bytes(v, n, uv, tr, w, BONES, clips, bounds, 'Project_Broom_kraken', SKIN)
    path = ROOT/'mod/BrogueDoom'/MODEL
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M39', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/kraken/kraken-animated.blend')
    out = ROOT/'assets/monsters/kraken'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Import by package name so connected_skin sees this module's CONNECTED_SKIN hook.
    import importlib
    result = importlib.import_module('tools.monster_models.kraken_animation').build()
    print({k: result[k] for k in ('sha256', 'dimensions', 'vertices', 'triangles', 'boneCount')})
