"""Rigid-object kit shared by the immobile relic creatures (phylactery,
eldritch totem, mirrored totem and phoenix egg). Presentation only.

Every piece is a closed rigid mesh weighted 1.0 to one bone, as in the goblin
and ogre totems, so there is no connected skin or cage bake. The kit provides
lathes (optionally twisted, faceted or cut into closed wedge shards), swept
tubes, extruded plates, a 4x4 painted atlas whose right column is reserved for
fullbright keys, and world-space rigid placement for floor-settled deaths.
Brogue CE owns every summon, reflection, hatching and regeneration outcome.
"""
import hashlib
import json
import math
import numpy as np
from .rat import ROOT, Part, add, sub, mul, cross, unit
from .skeletal import Rig, axis, assemble, sample_clips, qmul, rotate, inverse
from .toad_materials import png
from . import iqm

SIZE = 1024
CELL = 256
PAD = 12
GLOW_U = .75  # atlas column 3 (u >= 0.75) holds only fullbright roles
FLOOR = .1    # rest and settled pieces stay above the 0.07 automatic lift


def r6(p):
    return tuple(round(x, 6) + 0.0 for x in p)


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


class Piece(Part):
    """Part with local 0..1 UVs, optional faceted (per-triangle) normals."""

    def normals(self):
        if not getattr(self, 'flat', False):
            return super().normals()
        out = [(0, 0, 1)]*len(self.vertices)
        V = self.vertices
        for f in self.faces:
            n = unit(cross(sub(V[f[1]], V[f[0]]), sub(V[f[2]], V[f[0]])))
            for i in f:
                out[i] = n
        return out


def _finish(p, flat=False):
    """Triangulate, drop degenerate triangles and optionally unweld facets."""
    V = [r6(v) for v in p.vertices]
    tris = []
    for f in p.faces:
        for i in range(1, len(f)-1):
            a, b, c = f[0], f[i], f[i+1]
            if sum(x*x for x in cross(sub(V[b], V[a]), sub(V[c], V[a]))) > 1e-10:
                tris.append((a, b, c))
    if flat:
        nv, nuv, nf = [], [], []
        for t in tris:
            nf.append(tuple(range(len(nv), len(nv)+3)))
            nv += [V[i] for i in t]; nuv += [p.uv[i] for i in t]
        p.vertices, p.uv, p.faces = nv, nuv, nf
    else:
        p.vertices, p.faces = V, tris
    p.flat = flat
    return p


def _face(p, idx, want):
    V = p.vertices
    n = cross(sub(V[idx[1]], V[idx[0]]), sub(V[idx[2]], V[idx[0]]))
    p.faces.append(tuple(idx) if dot(n, want) >= 0 else tuple(reversed(idx)))


def lathe(name, profile, sides=16, *, center=(0, 0, 0), sx=1, sy=1, phase=0,
          twist=None, a0=0.0, a1=math.tau, flat=False, caps=True, wobble=None):
    """Surface of revolution, profile (r,z) bottom to top; u around, v up.
    `wobble(j, i)` optionally scales each ring vertex's radius (seam-safe
    when it depends on j modulo sides).

    A partial sweep (a1-a0 < tau) is closed by two planar wedge faces so a
    cut shard is watertight when it separates from its neighbours.
    """
    p = Piece(name)
    lengths = [0.0]
    for (r, z), (R, Z) in zip(profile, profile[1:]):
        lengths.append(lengths[-1]+math.hypot(R-r, Z-z))
    total = lengths[-1] or 1
    full = abs(a1-a0-math.tau) < 1e-9
    rows = []
    for i, (r, z) in enumerate(profile):
        row = []
        off = phase+(twist(i, z) if twist else 0)
        for j in range(sides+1):
            a = a0+(a1-a0)*j/sides+off
            row.append(len(p.vertices))
            rr = r*(wobble(j % sides if full else j, i) if wobble else 1)
            p.vertices.append((center[0]+sx*rr*math.cos(a), center[1]+sy*rr*math.sin(a), center[2]+z))
            p.uv.append((j/sides, lengths[i]/total))
        rows.append(row)
    for i in range(len(profile)-1):
        for j in range(sides):
            a, b = rows[i][j], rows[i][j+1]
            c, d = rows[i+1][j+1], rows[i+1][j]
            p.faces.append((a, b, c)); p.faces.append((a, c, d))
    if caps:
        for end, row, (r, z) in ((0, rows[0], profile[0]), (1, rows[-1], profile[-1])):
            if r < 1e-9:
                continue
            c = len(p.vertices); p.vertices.append(add(center, (0, 0, z))); p.uv.append((.5, float(end)))
            for j in range(sides):
                _face(p, (c, row[j], row[j+1]), (0, 0, 1 if end else -1))
    if not full:
        for k, a in ((0, a0), (sides, a1)):
            off = phase
            want = (math.sin(a+off), -math.cos(a+off), 0) if k == 0 else (-math.sin(a+off), math.cos(a+off), 0)
            axis_ids = []
            for i, (r, z) in enumerate(profile):
                axis_ids.append(len(p.vertices)); p.vertices.append(add(center, (0, 0, z)))
                p.uv.append((.5, lengths[i]/total))
            for i in range(len(profile)-1):
                quad = (axis_ids[i], rows[i][k], rows[i+1][k], axis_ids[i+1])
                _face(p, quad[:3], want); _face(p, (quad[0], quad[2], quad[3]), want)
    return _finish(p, flat)


def shell(name, profile, sides, a0, a1, centre, inner_scale=.88, inner=False):
    """One wedge of a thick lathe shell (an eggshell plate or cap).

    The outer piece carries the outer skin plus its rim and meridian edges;
    `inner=True` returns the matching inner skin (scaled toward `centre`)
    as a separate piece so it can take its own atlas role."""
    p = Piece(name)
    lengths = [0.0]
    for (r, z), (R, Z) in zip(profile, profile[1:]):
        lengths.append(lengths[-1]+math.hypot(R-r, Z-z))
    total = lengths[-1] or 1

    def ring(i, scale):
        r, z = profile[i]; row = []
        for j in range(sides+1):
            a = a0+(a1-a0)*j/sides
            pt = (r*math.cos(a), r*math.sin(a), z)
            if scale != 1:
                pt = add(centre, mul(sub(pt, centre), scale))
            row.append(len(p.vertices)); p.vertices.append(pt); p.uv.append((j/sides, lengths[i]/total))
        return row
    if inner:
        rows = [ring(i, inner_scale) for i in range(len(profile))]
        for i in range(len(profile)-1):
            for j in range(sides):
                a, b, c, d = rows[i][j], rows[i][j+1], rows[i+1][j+1], rows[i+1][j]
                p.faces.append((a, c, b)); p.faces.append((a, d, c))
        return _finish(p)
    outer = [ring(i, 1) for i in range(len(profile))]
    for i in range(len(profile)-1):
        for j in range(sides):
            a, b, c, d = outer[i][j], outer[i][j+1], outer[i+1][j+1], outer[i+1][j]
            p.faces.append((a, b, c)); p.faces.append((a, c, d))
    inner_rows = [ring(i, inner_scale) for i in range(len(profile))]
    last = len(profile)-1
    for i, nxt in ((0, 1), (last, last-1)):
        for j in range(sides):
            want = sub(p.vertices[outer[i][j]], p.vertices[outer[nxt][j]])
            quad = (outer[i][j], outer[i][j+1], inner_rows[i][j+1], inner_rows[i][j])
            _face(p, quad[:3], want); _face(p, (quad[0], quad[2], quad[3]), want)
    for j, a, sign in ((0, a0, -1), (sides, a1, 1)):
        want = (-sign*math.sin(a), sign*math.cos(a), 0)
        for i in range(last):
            quad = (outer[i][j], outer[i+1][j], inner_rows[i+1][j], inner_rows[i][j])
            _face(p, quad[:3], want); _face(p, (quad[0], quad[2], quad[3]), want)
    return _finish(p)


def ellipsoid(name, center, radii, segments=16, rings=10, flat=False):
    profile = [(math.sin(math.pi*i/rings), -math.cos(math.pi*i/rings)) for i in range(rings+1)]
    p = lathe(name, [(r, z*radii[2]) for r, z in profile], segments, center=center,
              sx=radii[0], sy=radii[1], flat=flat)
    return p


def _catmull(points, samples):
    if samples <= 1 or len(points) < 3:
        return [tuple(p) for p in points]
    out = []
    P = [points[0]]+list(points)+[points[-1]]
    for i in range(1, len(P)-2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for s in range(samples):
            t = s/samples
            out.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    out.append(tuple(points[-1]))
    return out


def tube(name, points, sides=8, samples=3, caps=True, flat=False):
    """Swept tube through (x,y,z,radius) controls with transported frames."""
    pts = _catmull(points, samples)
    p = Piece(name)
    centers = [q[:3] for q in pts]
    tangents = []
    for i in range(len(centers)):
        a = centers[max(0, i-1)]; b = centers[min(len(centers)-1, i+1)]
        tangents.append(unit(sub(b, a)))
    t0 = tangents[0]
    ref = (0, 0, 1) if abs(t0[2]) < .9 else (1, 0, 0)
    n = unit(cross(ref, t0))
    lengths = [0.0]
    for a, b in zip(centers, centers[1:]):
        lengths.append(lengths[-1]+math.dist(a, b))
    total = lengths[-1] or 1
    rows = []
    for i, (c, t) in enumerate(zip(centers, tangents)):
        n = unit(sub(n, mul(t, dot(n, t))))
        b = cross(t, n)
        row = []
        for j in range(sides+1):
            a = math.tau*j/sides
            d = add(mul(n, math.cos(a)), mul(b, math.sin(a)))
            row.append(len(p.vertices)); p.vertices.append(add(c, mul(d, pts[i][3])))
            p.uv.append((j/sides, lengths[i]/total))
        rows.append(row)
    for i in range(len(rows)-1):
        for j in range(sides):
            a, b_, c, d = rows[i][j], rows[i][j+1], rows[i+1][j+1], rows[i+1][j]
            p.faces.append((a, b_, c)); p.faces.append((a, c, d))
    if caps:
        for end, row, c, t in ((0, rows[0], centers[0], tangents[0]), (1, rows[-1], centers[-1], tangents[-1])):
            if pts[-1 if end else 0][3] < 1e-6:
                continue
            k = len(p.vertices); p.vertices.append(c); p.uv.append((.5, float(end)))
            want = t if end else mul(t, -1)
            for j in range(sides):
                _face(p, (k, row[j], row[j+1]), want)
    return _finish(p, flat)


def _ear_clip(outline):
    def orient(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    remaining = list(range(len(outline))); tris = []
    while len(remaining) > 3:
        for k, b in enumerate(remaining):
            a, c = remaining[k-1], remaining[(k+1) % len(remaining)]
            A, B, C = (outline[i] for i in (a, b, c))
            if orient(A, B, C) <= 1e-10:
                continue
            if any(all(orient(U, W, outline[j]) >= -1e-10 for U, W in ((A, B), (B, C), (C, A)))
                   for j in remaining if j not in (a, b, c)):
                continue
            tris.append((a, b, c)); remaining.pop(k); break
        else:
            raise ValueError('cannot triangulate outline')
    tris.append(tuple(remaining))
    return tris


def plate(name, outline, thickness, origin, ax_u, ax_v, flat=True, taper=1.0, uv_box=None):
    """Extruded polygon in the plane origin + a*ax_u + b*ax_v.

    `taper` shrinks the back face toward the outline centroid, giving blades
    and shards a bevelled edge instead of a flat slab side."""
    area = sum(a*B-A*b for (a, b), (A, B) in zip(outline, outline[1:]+outline[:1]))
    if area < 0:
        outline = list(reversed(outline))
    ax_u, ax_v = unit(ax_u), unit(ax_v)
    nrm = unit(cross(ax_u, ax_v))
    lo_a = min(a for a, b in outline); hi_a = max(a for a, b in outline)
    lo_b = min(b for a, b in outline); hi_b = max(b for a, b in outline)
    if uv_box:
        lo_a, hi_a, lo_b, hi_b = uv_box
    ca = sum(a for a, b in outline)/len(outline); cb = sum(b for a, b in outline)/len(outline)
    p = Piece(name); n = len(outline)
    for side, k in ((1, 1.0), (-1, taper)):
        for a, b in outline:
            a2, b2 = ca+(a-ca)*k, cb+(b-cb)*k
            pos = add(origin, add(add(mul(ax_u, a2), mul(ax_v, b2)), mul(nrm, side*thickness/2)))
            p.vertices.append(pos); p.uv.append(((a-lo_a)/(hi_a-lo_a), (b-lo_b)/(hi_b-lo_b)))
    tris = _ear_clip(outline)
    for t in tris:
        _face(p, t, nrm); _face(p, tuple(i+n for i in t), mul(nrm, -1))
    for i in range(n):
        j = (i+1) % n
        (a, b), (A, B) = outline[i], outline[j]
        want = add(mul(ax_u, B-b), mul(ax_v, -(A-a)))
        _face(p, (i, j, j+n), want); _face(p, (i, j+n, i+n), want)
    return _finish(p, flat)


def transform(p, q=(0, 0, 0, 1), t=(0, 0, 0), pivot=(0, 0, 0)):
    p.vertices = [r6(add(add(rotate(q, sub(v, pivot)), pivot), t)) for v in p.vertices]
    return p


class Atlas:
    """4x4 grid of 256 px cells; column 3 (u >= 0.75) is the fullbright key."""

    def __init__(self, roles):
        self.roles = roles  # name -> (col,row)
        for name, (c, r) in roles.items():
            if not (0 <= c < 4 and 0 <= r < 4):
                raise ValueError(name)

    def glow(self, role):
        return self.roles[role][0] == 3

    def map(self, part, role):
        c, r = self.roles[role]
        x0, y0 = c*CELL+PAD, r*CELL+PAD; span = CELL-2*PAD
        part.uv = [((x0+u*span)/SIZE, 1-(y0+(1-v)*span)/SIZE) for u, v in part.uv]
        part.role = role
        return part

    def paint(self, pigment):
        image = np.zeros((SIZE, SIZE, 3), dtype=np.float64)
        span = CELL-2*PAD
        for name, (c, r) in sorted(self.roles.items()):
            x = np.arange(c*CELL, (c+1)*CELL); y = np.arange(r*CELL, (r+1)*CELL)
            U = np.clip((x-(c*CELL+PAD)+.5)/span, 0, 1)
            V = 1-np.clip((y-(r*CELL+PAD)+.5)/span, 0, 1)
            UU, VV = np.meshgrid(U, V)
            rgb = pigment(name, UU, VV)
            for k in range(3):
                image[r*CELL:(r+1)*CELL, c*CELL:(c+1)*CELL, k] = rgb[k]
        data = np.clip(np.round(image), 0, 255).astype(np.uint8)
        return png(bytearray(data.tobytes()), SIZE, SIZE)


def hash2(ix, iy, seed=0):
    h = (np.asarray(ix, dtype=np.int64)*374761393+np.asarray(iy, dtype=np.int64)*668265263+seed*2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13))*1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF)/65535.0*2-1


def vnoise(U, V, fu, fv, seed=0):
    """Smooth value noise in -1..1, deterministic."""
    x = U*fu; y = V*fv
    ix = np.floor(x).astype(np.int64); iy = np.floor(y).astype(np.int64)
    fx = x-ix; fy = y-iy
    sx = fx*fx*(3-2*fx); sy = fy*fy*(3-2*fy)
    a = hash2(ix, iy, seed); b = hash2(ix+1, iy, seed)
    c = hash2(ix, iy+1, seed); d = hash2(ix+1, iy+1, seed)
    return (a*(1-sx)+b*sx)*(1-sy)+(c*(1-sx)+d*sx)*sy


def fbm(U, V, f, seed=0, octaves=3):
    total = 0; amp = 1; norm = 0
    for o in range(octaves):
        total = total+amp*vnoise(U, V, f*2**o, f*2**o, seed+o*17); norm += amp; amp *= .5
    return total/norm


def mix(a, b, t):
    t = np.clip(t, 0, 1)
    return [a[k]*(1-t)+b[k]*t for k in range(3)]


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t*t*(3-2*t)


def slerp(a, b, t):
    d = dot(a, b)
    if d < 0:
        b = tuple(-x for x in b); d = -d
    if d > .9995:
        q = tuple(x+(y-x)*t for x, y in zip(a, b))
    else:
        th = math.acos(d); s = math.sin(th)
        q = tuple((x*math.sin((1-t)*th)+y*math.sin(t*th))/s for x, y in zip(a, b))
    n = math.sqrt(dot(q, q))
    return tuple(x/n for x in q)


class Relic:
    """Rig, weighted pieces, clip sampling and runtime export for one relic."""

    def __init__(self, slug, work_id, number, skin, specs, clips, atlas, scale=1.0):
        self.slug, self.work_id, self.number, self.skin = slug, work_id, number, skin
        # Size lives in the exported geometry itself (no registry visualScale).
        self.scale = scale
        specs = [(n, p, r6(mul(v, scale))) for n, p, v in specs]
        self.rig = Rig.from_world(specs); self.bones, self.rest = self.rig.bones, self.rig.rest
        self.ids = {name: i for i, (name, _, _) in enumerate(self.bones)}
        self.clips = clips; self.atlas = atlas
        self._geometry = None; self._by_bone = None
        self.model = 'mod/BrogueDoom/models/monsters/%02d_%s.iqm' % (number, slug)

    # -- geometry -------------------------------------------------------
    def put(self, parts, piece, role, bone):
        self.atlas.map(piece, role)
        piece.bone = self.ids[bone]
        piece.skin_weights = [[(self.ids[bone], 1)]]*len(piece.vertices)
        parts.append(piece)
        return piece

    def geometry(self, build_parts):
        if self._geometry is None:
            parts = []
            build_parts(self, parts)
            if self.scale != 1.0:
                for part in parts:
                    part.vertices = [r6(mul(v, self.scale)) for v in part.vertices]
            self._geometry = assemble(parts, lambda p, v, u: [(0, 1)])
        return self._geometry

    def descendants(self, bone):
        out = {bone}
        for i, (_, parent, _) in enumerate(self.bones):
            if parent in out:
                out.add(i)
        return out

    def bone_points(self, bone):
        """Rest vertices of the rigid group a bone carries (with descendants)."""
        if self._by_bone is None:
            parts = self._geometry[0]
            self._by_bone = {}
            for p in parts:
                self._by_bone.setdefault(p.bone, []).extend(p.vertices)
        pts = []
        for b in sorted(self.descendants(bone)):
            pts += self._by_bone.get(b, [])
        return pts

    # -- posing ---------------------------------------------------------
    def rest_frame(self):
        return [[*local, 0, 0, 0, 1, 1, 1, 1] for _, _, local in self.bones]

    def world_min_z(self, frame, bone):
        tf = self.rig.matrices(frame)
        loc, q = tf[bone]; pivot = self.rest[bone]
        pts = self.bone_points(bone)
        # descendants may have their own motion; evaluate each exactly
        low = math.inf
        for b in sorted(self.descendants(bone)):
            l2, q2 = tf[b]; pv = self.rest[b]
            for v in self._by_bone.get(b, []):
                low = min(low, l2[2]+rotate(q2, sub(v, pv))[2])
        return low

    def settle(self, frame, bone, floor=FLOOR, lift_only=False):
        """Move a root-child bone vertically so its lowest point meets floor."""
        if isinstance(bone, str):
            bone = self.ids[bone]
        if self.bones[bone][1] != 0:
            raise ValueError('settle expects a root child: '+self.bones[bone][0])
        low = self.world_min_z(frame, bone)
        dz = floor-low
        if lift_only and dz <= 0:
            return
        frame[bone][2] += dz

    def fall(self, frame, bone, s, q_end, xy_end, floor=FLOOR, hop=0.0, final=None):
        """Rigid fall of a root child from rest to a floor-settled placement."""
        if isinstance(bone, str):
            bone = self.ids[bone]
        rest = self.bones[bone][2]
        if final is None:
            probe = self.rest_frame(); probe[bone][3:7] = q_end
            probe[bone][0], probe[bone][1] = xy_end
            self.settle(probe, bone, floor)
            final = tuple(probe[bone][:3])
        frame[bone][3:7] = slerp((0, 0, 0, 1), q_end, s)
        frame[bone][0] = rest[0]+(final[0]-rest[0])*s
        frame[bone][1] = rest[1]+(final[1]-rest[1])*s
        frame[bone][2] = rest[2]+(final[2]-rest[2])*s+hop*math.sin(math.pi*s)
        self.settle(frame, bone, floor, lift_only=True)

    def placement(self, bone, q, xy, floor=FLOOR, contact=None):
        """Cached floor-settled location for a root child rotated by q whose
        rest-space `contact` point (default: its pivot) lands over xy."""
        i = self.ids[bone] if isinstance(bone, str) else bone
        contact = tuple(contact) if contact else tuple(self.rest[i])
        key = ('place', i, tuple(q), tuple(xy), floor, contact)
        cache = self.__dict__.setdefault('_cache', {})
        if key not in cache:
            probe = self.rest_frame(); probe[i][3:7] = q
            off = rotate(q, sub(contact, self.rest[i]))
            probe[i][0], probe[i][1] = xy[0]-off[0], xy[1]-off[1]
            self.settle(probe, i, floor)
            cache[key] = tuple(r6(probe[i][:3]))
        return cache[key]

    def lean(self, bone, axis_dir, pivot, floor=FLOOR, lo=60.0, hi=178.0, pre=(0, 0, 0, 1), post=(0, 0, 0, 1), contact=None):
        """Rotation about axis_dir whose lowest point just meets the floor
        while the rest-space `contact` point (default: the bone pivot) is held
        at world `pivot`: a piece leaning from a ledge down to the ground.
        Returns (quaternion, bone location)."""
        i = self.ids[bone] if isinstance(bone, str) else bone
        contact = tuple(contact) if contact else tuple(self.rest[i])
        key = ('lean', i, tuple(axis_dir), tuple(pivot), floor, lo, hi, tuple(pre), tuple(post), contact)
        cache = self.__dict__.setdefault('_cache', {})

        def place(deg):
            q = qmul(post, qmul(axis(axis_dir, math.radians(deg)), pre))
            loc = sub(tuple(pivot), rotate(q, sub(contact, self.rest[i])))
            return q, loc
        if key not in cache:
            def low(deg):
                probe = self.rest_frame()
                q, loc = place(deg)
                probe[i][3:7] = q; probe[i][:3] = list(loc)
                return self.world_min_z(probe, i)-floor
            a, b = lo, hi
            if low(a) < 0 or low(b) > 0:
                raise ValueError('lean has no floor contact in range: '+self.bones[i][0])
            for _ in range(48):
                m = (a+b)/2
                a, b = (m, b) if low(m) > 0 else (a, m)
            q, loc = place(round(b, 6))
            cache[key] = (q, tuple(r6(loc)))
        return cache[key]

    def group(self, frame, bones, q=(0, 0, 0, 1), pivot=(0, 0, 0), t=(0, 0, 0)):
        """Apply one outer rigid transform to several root-child bones."""
        for name in bones:
            i = self.ids[name]
            if self.bones[i][1] != 0:
                raise ValueError('group expects root children: '+name)
            loc = tuple(frame[i][:3]); qb = tuple(frame[i][3:7])
            frame[i][3:7] = qmul(q, qb)
            frame[i][:3] = add(add(pivot, rotate(q, sub(loc, pivot))), t)

    def turn(self, frame, bone, degrees, direction):
        frame[self.ids[bone]][3:7] = axis(direction, math.radians(degrees))

    def turn_q(self, frame, bone, q):
        frame[self.ids[bone]][3:7] = q

    def move(self, frame, bone, d):
        i = self.ids[bone]
        frame[i][0] += d[0]; frame[i][1] += d[1]; frame[i][2] += d[2]

    # -- export ---------------------------------------------------------
    def animation(self, pose, v, w):
        return sample_clips(self.rig, self.clips, pose, v, w)

    def export(self, geometry, animation, texture, extra=None):
        skin = texture(); (ROOT/'mod/BrogueDoom'/self.skin).write_bytes(skin)
        parts, v, n, uv, t, w = geometry()
        clips, bounds = animation(v, w)
        symbol = 'MK_'+self.slug.upper()
        data = iqm.encode(v, n, uv, t, w, self.bones, clips, bounds,
                          mesh_label='Project_Broom_'+self.slug, material_path=self.skin)
        path = ROOT/self.model; path.write_bytes(data)
        out = ROOT/'assets/monsters'/self.slug; out.mkdir(exist_ok=True)
        manifest = dict(schemaVersion=1, workId=self.work_id, format='IQM v2',
                        runtimeModel=self.model, sha256=hashlib.sha256(data).hexdigest(), skin=self.skin,
                        skinSha256=hashlib.sha256(skin).hexdigest(),
                        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                        parts=len(parts), vertices=len(v), triangles=len(t), boneCount=len(self.bones),
                        bones=[dict(name=nm, parent=p, local=loc) for nm, p, loc in self.bones],
                        clips=[{k: x for k, x in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                        poseBounds=bounds,
                        authoringSource='assets/monsters/%s/%s-animated.blend' % (self.slug, self.slug.replace('_', '-')))
        if extra:
            manifest.update(extra)
        (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
        return manifest


# Standard clip timing: action roles are sampled first/middle/last by the
# gallery, so each action's key pose sits on its middle frame.
CLIP_TIMING = dict(idle=(40, 20, True), rest=(20, 20, True), attack=(18, 30, False),
                   alt=(20, 30, False), hit=(12, 30, False), death=(30, 30, False))


def clip_specs(names):
    keys = ('idle', 'rest', 'attack', 'alt', 'hit', 'death')
    return [(name,)+CLIP_TIMING[k] for name, k in zip(names, keys)]


def durations(clips):
    return [0, 0]+[math.ceil(c[1]*35/c[2]) for c in clips[2:]]


class RelicChecks:
    """Shared assertions for the relic creature tests (mixin for TestCase).

    Subclasses set: model (module), symbol, shader (path under mod/BrogueDoom),
    glow_roles, and implement their own signature and key-pose tests."""
    model = None
    symbol = None
    shader = None

    @classmethod
    def setUpClass(cls):
        m = cls.model
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = m.geometry()
        cls.clips, cls.bounds = m.animation_data(cls.v, cls.w)
        cls.clip = {c['name']: c for c in cls.clips}
        cls.rest_v = cls.v

    def posed(self, clip, frame):
        return self.model.deform(self.v, self.w, self.clip[clip]['frames'][frame])

    def bone_points(self, verts, bone):
        out = []; i = 0; b = self.model.IDS[bone]
        for p in self.parts:
            if p.bone == b:
                out += verts[i:i+len(p.vertices)]
            i += len(p.vertices)
        return out

    def part_points(self, verts, prefix):
        out = []; i = 0
        for p in self.parts:
            if p.name.startswith(prefix):
                out += verts[i:i+len(p.vertices)]
            i += len(p.vertices)
        return out

    def test_profile_timing_and_no_visual_scale(self):
        from .skeletal_registry import find
        row = find(self.symbol)
        m = self.model
        self.assertEqual(row['clips'], [c[0] for c in m.CLIPS])
        self.assertEqual(row['walkFrames'], m.CLIPS[1][1])
        self.assertEqual(row['durations'], m.DURATIONS)
        for c, d in zip(m.CLIPS[2:], row['durations'][2:]):
            self.assertGreaterEqual(d, math.ceil(c[1]*35/c[2]))
        self.assertEqual(row['module'], m.__name__.rsplit('.', 1)[1])
        self.assertEqual('mod/BrogueDoom/models/monsters/'+row['model'], m.MODEL)
        self.assertEqual(row['skin'], m.SKIN)
        self.assertNotIn('visualScale', row)
        self.assertTrue((ROOT/row['report']).is_file())
        self.assertTrue(row['traits'])
        self.assertEqual(row['ownedFiles'], ['mod/BrogueDoom/'+self.shader])
        self.assertEqual([c['name'] for c in self.clips], row['clips'])
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])

    def test_gldefs_binds_presentation_only_shader(self):
        from .skeletal_registry import PENDING
        snippet = PENDING/(self.symbol+'.gldefs')
        text = snippet.read_text() if snippet.is_file() else (ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        block = text[text.index('material "%s"' % self.model.SKIN):]
        self.assertIn('shader "%s"' % self.shader, block[:block.index('}')])
        source = (ROOT/'mod/BrogueDoom'/self.shader).read_text()
        self.assertIn('material.Bright', source)
        for forbidden in ('uLightLevel', 'random', 'AddLight', 'timer'):
            self.assertNotIn(forbidden, source)

    def test_rigid_single_bone_pieces_and_atlas_columns(self):
        atlas = self.model.R.atlas
        for p in self.parts:
            self.assertEqual(len({tuple(x) for x in p.skin_weights}), 1, p.name)
            self.assertEqual(p.skin_weights[0], [(p.bone, 1)])
            us = [u for u, v in p.uv]
            if atlas.glow(p.role):
                self.assertGreaterEqual(min(us), GLOW_U, p.name)
            else:
                self.assertLess(max(us), GLOW_U, p.name)
        self.assertTrue(all(0 < u < 1 and 0 < v < 1 for u, v in self.uv))
        used = {p.bone for p in self.parts}
        self.assertEqual(used, set(range(len(self.model.BONES))) - ({0} - used))

    def test_centred_clearance_and_no_floor_compensation(self):
        root = self.model.pose('rest', 0)[0]
        for c in self.clips:
            for f in c['frames']:
                self.assertEqual(tuple(f[0]), tuple(root), c['name'])
        for b in self.bounds:
            self.assertTrue(all(-32 < x < 32 for x in (b[0], b[1], b[3], b[4])), b)
            self.assertGreaterEqual(b[2], .07)
            self.assertLess(b[5], 72)  # oblique gallery camera crops above ~72

    def test_loops_close_rest_is_static_and_unit_scales(self):
        m = self.model
        rest = m.pose('rest', 0)
        self.assertTrue(all(f == rest for f in self.clip[m.CLIPS[1][0]]['frames']))
        for name, *_ in m.CLIPS[:2]:
            a = m.deform(self.v, self.w, m.pose(name, 0)); b = m.deform(self.v, self.w, m.pose(name, 1))
            self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-9)
        for name, *_ in m.CLIPS[2:5]:
            a = m.deform(self.v, self.w, m.pose(name, 0)); b = m.deform(self.v, self.w, m.pose(name, 1))
            self.assertLess(max(math.dist(x, y) for x, y in zip(a, self.v)), 1e-9, name)
            self.assertLess(max(math.dist(x, y) for x, y in zip(b, self.v)), 1e-9, name)
        for c in self.clips:
            for f in c['frames']:
                for row in f:
                    self.assertEqual(tuple(row[7:]), (1, 1, 1))
                    self.assertAlmostEqual(sum(x*x for x in row[3:7]), 1)

    def test_rigid_triangles_keep_area(self):
        def area(v, t):
            a, b, c = t
            return math.sqrt(sum(x*x for x in cross(sub(v[b], v[a]), sub(v[c], v[a]))))
        original = [area(self.v, t) for t in self.tri]
        self.assertGreater(min(original), 1e-6)
        for c in self.clips:
            for f in (c['frames'][len(c['frames'])//2], c['frames'][-1]):
                posed = self.model.deform(self.v, self.w, f)
                self.assertLess(max(abs(area(posed, t)-a) for t, a in zip(self.tri, original)), 1e-7)

    def test_action_key_pose_on_middle_frame(self):
        m = self.model
        for name, count, *_ in m.CLIPS[2:5]:
            frames = self.clip[name]['frames']
            moves = [max(math.dist(a, b) for a, b in zip(m.deform(self.v, self.w, f), self.v)) for f in frames]
            mid = count//2
            self.assertGreaterEqual(moves[mid], .9*max(moves), name)

    def test_runtime_bytes_match_source(self):
        import hashlib, json
        from . import iqm
        m = self.model
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, m.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_'+self.symbol[3:].lower(), material_path=m.SKIN)
        self.assertEqual(data, (ROOT/m.MODEL).read_bytes())
        skin = m.texture_bytes()
        self.assertEqual(skin, (ROOT/'mod/BrogueDoom'/m.SKIN).read_bytes())
        manifest = json.loads((ROOT/'assets/monsters'/m.R.slug/'animation.json').read_text())
        self.assertEqual(manifest['sha256'], hashlib.sha256(data).hexdigest())
        self.assertEqual(manifest['skinSha256'], hashlib.sha256(skin).hexdigest())
