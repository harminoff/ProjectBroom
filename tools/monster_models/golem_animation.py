"""Original carved-stone golem built from rigid, bevelled and chipped segments.

Presentation only. Brogue CE owns the golem's statue dormancy, reflection,
negation death, lack of regeneration, health, timing and every attack outcome.
Nothing here feeds data back to the simulation, and no debris actor collides.

The module doubles as a small reusable stone kit for later statue creatures:

- ``carved_block`` / ``stone_core``: rounded-box and ball segments with
  deterministic edge chips, hewn face irregularity and painting attributes;
- ``layout_islands``: area-proportional quad islands for per-pixel painting;
- ``two_bone`` / ``frame_from_world`` / ``matrix_quat``: world-space rigid
  posing with explicit bend poles, converted to the shared local frame format;
- ``settle``: rest a rigid piece on the floor for rubble poses.

``golem_materials.paint_atlas`` paints the matching stone texture.
"""
import hashlib
import json
import math
from . import iqm, golem_materials
from .rat import ROOT, Part, add, sub, mul, unit, cross
from .skeletal import Rig, axis, inverse, qmul, rotate, assemble, sample_clips

SKIN = 'graphics/BRGGOLEM.png'
MODEL = 'mod/BrogueDoom/models/monsters/49_golem.iqm'


def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]


def lerp(a, b, t): return tuple(x+(y-x)*t for x, y in zip(a, b))


def smooth(t):
    t = max(0.0, min(1.0, t)); return t*t*(3-2*t)


def window(t, a, b): return smooth((t-a)/(b-a))


# ----------------------------------------------------------------- noise
def _hash(ix, iy, iz, seed):
    h = (ix*374761393 + iy*668265263 + iz*1440662683 + seed*2654435761) & 0xffffffff
    h = ((h ^ (h >> 13))*1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffff)/65535.0


def value_noise(p, seed=0):
    """Deterministic smooth value noise in [0, 1]. Authoring pattern only."""
    x, y, z = p; ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x-ix, y-iy, z-iz
    sx, sy, sz = fx*fx*(3-2*fx), fy*fy*(3-2*fy), fz*fz*(3-2*fz)
    def c(dx, dy, dz): return _hash(ix+dx, iy+dy, iz+dz, seed)
    x00 = c(0, 0, 0)+(c(1, 0, 0)-c(0, 0, 0))*sx; x10 = c(0, 1, 0)+(c(1, 1, 0)-c(0, 1, 0))*sx
    x01 = c(0, 0, 1)+(c(1, 0, 1)-c(0, 0, 1))*sx; x11 = c(0, 1, 1)+(c(1, 1, 1)-c(0, 1, 1))*sx
    y0 = x00+(x10-x00)*sy; y1 = x01+(x11-x01)*sy
    return y0+(y1-y0)*sz


# -------------------------------------------------------------- rotations
def euler(rx=0, ry=0, rz=0):
    """Rotation matrix columns from degrees, applied X then Y then Z."""
    def m(q): return [rotate(q, e) for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1))]
    q = qmul(axis((0, 0, 1), math.radians(rz)), qmul(axis((0, 1, 0), math.radians(ry)), axis((1, 0, 0), math.radians(rx))))
    return m(q)


def matrix_quat(cols):
    """Quaternion (x, y, z, w) for a rotation matrix given as three columns."""
    (m00, m10, m20), (m01, m11, m21), (m02, m12, m22) = cols
    trace = m00+m11+m22
    if trace > 0:
        s = math.sqrt(trace+1)*2; q = ((m21-m12)/s, (m02-m20)/s, (m10-m01)/s, s/4)
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1+m00-m11-m22)*2; q = (s/4, (m01+m10)/s, (m02+m20)/s, (m21-m12)/s)
    elif m11 > m22:
        s = math.sqrt(1+m11-m00-m22)*2; q = ((m01+m10)/s, s/4, (m12+m21)/s, (m02-m20)/s)
    else:
        s = math.sqrt(1+m22-m00-m11)*2; q = ((m02+m20)/s, (m12+m21)/s, s/4, (m10-m01)/s)
    n = math.sqrt(sum(c*c for c in q)); q = tuple(c/n for c in q)
    return q if q[3] >= 0 else tuple(-c for c in q)


def frame_rotation(d0, p0, d1, p1):
    """Rotation taking direction d0 with pole p0 onto d1 with pole p1 (controlled twist)."""
    def basis(d, p):
        d = unit(d); n = unit(sub(p, mul(d, dot(p, d)))); return d, n, cross(d, n)
    a, b = basis(d0, p0), basis(d1, p1)
    cols = []
    for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        coords = [dot(e, v) for v in a]
        cols.append(tuple(sum(coords[k]*b[k][i] for k in range(3)) for i in range(3)))
    return matrix_quat(cols)


def slerp(a, b, t):
    d = sum(x*y for x, y in zip(a, b))
    if d < 0: b = tuple(-x for x in b); d = -d
    if d > .9995:
        q = tuple(x+(y-x)*t for x, y in zip(a, b))
    else:
        th = math.acos(d); s = math.sin(th)
        q = tuple((math.sin((1-t)*th)*x+math.sin(t*th)*y)/s for x, y in zip(a, b))
    n = math.sqrt(sum(c*c for c in q)); return tuple(c/n for c in q)


# ------------------------------------------------------------ stone kit
def _samples(h, r, step):
    inner = h-r; k = max(1, round(2*inner/step))
    return [-h, -h+.3*r]+[-inner+2*inner*i/k for i in range(k+1)]+[h-.3*r, h]


FACES = ((0, 1, 1, 2), (0, -1, 2, 1), (1, 1, 2, 0), (1, -1, 0, 2), (2, 1, 0, 1), (2, -1, 1, 0))


def carved_block(name, bone, center, half, rot=None, bevel=None, chip=1.0, rough=.22, seed=0,
                 shape=None, role='stone', step=3.2, pillow=.14, hewn=.09):
    """Rounded, chipped stone block. ``shape`` maps local (x,y,z) -> (x,y,z).

    Every quad keeps its own four vertices so it can receive its own painted
    island; ``Part.normals`` welds coincident positions for smooth bevels.
    Painting attributes: normalized local box position, edge proximity and
    chip depth per vertex.
    """
    cols = rot or euler()
    r = bevel if bevel is not None else min(half)*.38
    r = min(r, min(half)*.98)
    samples = [_samples(h, r, step) for h in half]
    p = Part(name); p.bone = bone; p.role = role; p.seed = seed
    p.box = (tuple(center), cols, tuple(half)); p.local = []; p.edge = []; p.chip = []
    for fa, sign, ua, va in FACES:
        grid = {}
        for i, su in enumerate(samples[ua]):
            for j, sv in enumerate(samples[va]):
                q = [0.0, 0.0, 0.0]; q[fa] = sign*half[fa]; q[ua] = su; q[va] = sv
                c = [max(-(h-r), min(h-r, x)) for x, h in zip(q, half)]
                d = sub(q, c); dl = math.sqrt(dot(d, d))
                out = unit(d) if dl > 1e-9 else tuple(float(k == fa)*sign for k in range(3))
                local = add(c, mul(out, r))
                # Edge proximity: bevel zone of either in-face axis.
                e = max(max(0.0, min(1.0, (abs(q[k])-(half[k]-2.2*r))/(2.2*r))) for k in (ua, va))
                n1 = value_noise(mul(q, .42), seed*7+1)
                n2 = value_noise(mul(q, .13), seed*7+2)
                depth = chip*r*.95*e**1.4*max(0.0, min(1.0, (n1-.5)*4.5))
                bump = rough*(n2-.5)*2+rough*.5*(value_noise(mul(q, .55), seed*7+3)-.5)
                # Pillowed faces and low-frequency hewn planes: carved masses, not boxes.
                swell = 1.0
                for k in (ua, va): swell *= max(0.0, 1-(q[k]/half[k])**2)
                bump += pillow*min(half)*swell+hewn*min(half)*(value_noise(add(mul(q, .07), (seed*3.1, 0, 0)), seed*7+4)-.5)*2
                local = add(local, mul(out, bump-depth))
                if shape: local = shape(local)
                world = add(center, add(mul(cols[0], local[0]), add(mul(cols[1], local[1]), mul(cols[2], local[2]))))
                grid[i, j] = (world, tuple(x/h for x, h in zip(q, half)), e, depth/(r+1e-9))
        for i in range(len(samples[ua])-1):
            for j in range(len(samples[va])-1):
                base = len(p.vertices)
                for key in ((i, j), (i+1, j), (i+1, j+1), (i, j+1)):
                    world, local, e, depth = grid[key]
                    p.vertices.append(world); p.uv.append((0.0, 0.0))
                    p.local.append(local); p.edge.append(e); p.chip.append(depth)
                p.faces.append((base, base+1, base+2, base+3))
    return p


def stone_core(name, bone, center, radius, seed=0, role='core', n=4):
    """Dark ball joint filling the gap between two rigid stone segments."""
    p = Part(name); p.bone = bone; p.role = role; p.seed = seed
    p.box = (tuple(center), euler(), (radius,)*3); p.local = []; p.edge = []; p.chip = []
    ticks = [-1+2*i/n for i in range(n+1)]
    for fa, sign, ua, va in FACES:
        for i in range(n):
            for j in range(n):
                base = len(p.vertices)
                for a, b in ((i, j), (i+1, j), (i+1, j+1), (i, j+1)):
                    q = [0.0, 0.0, 0.0]; q[fa] = sign; q[ua] = ticks[a]; q[va] = ticks[b]
                    d = unit(q); bump = 1+.06*(value_noise(mul(d, 3.1), seed)-.5)
                    p.vertices.append(add(center, mul(d, radius*bump))); p.uv.append((0.0, 0.0))
                    p.local.append(d); p.edge.append(0.0); p.chip.append(0.0)
                p.faces.append((base, base+1, base+2, base+3))
    return p


def along(start, end, pole=(1, 0, 0)):
    """Block frame whose local Z runs from start to end; X faces the pole."""
    z = unit(sub(end, start)); x = unit(sub(pole, mul(z, dot(pole, z)))); return [x, cross(z, x), z]


def layout_islands(parts, size=2048, pad=2):
    """Area-proportional shelf packing: one padded rectangle per quad.

    Density is the largest value that still fits, so texel density is uniform
    across the whole statue. Deterministic: order is (height, index).
    """
    quads = []
    for pi, p in enumerate(parts):
        for fi, f in enumerate(p.faces):
            a, b, c, d = (p.vertices[i] for i in f)
            w = (math.dist(a, b)+math.dist(d, c))/2; h = (math.dist(a, d)+math.dist(b, c))/2
            quads.append((pi, fi, w, h))

    def pack(density):
        rects = [(max(3, round(w*density)), max(3, round(h*density)), k) for k, (_, _, w, h) in enumerate(quads)]
        order = sorted(range(len(rects)), key=lambda k: (-rects[k][1], k))
        x = y = row = 0; placed = {}
        for k in order:
            rw, rh = rects[k][0]+2*pad, rects[k][1]+2*pad
            if x+rw > size: x = 0; y += row; row = 0
            if y+rh > size: return None
            placed[k] = (x+pad, y+pad, rects[k][0], rects[k][1]); x += rw; row = max(row, rh)
        return placed
    low, high = 1.0, 64.0
    for _ in range(24):
        mid = (low+high)/2
        if pack(mid): low = mid
        else: high = mid
    placed = pack(low)
    islands = []
    for k, (pi, fi, _, _) in enumerate(quads):
        x0, y0, w, h = placed[k]; p = parts[pi]; f = p.faces[fi]
        corners = ((x0, y0), (x0+w-1, y0), (x0+w-1, y0+h-1), (x0, y0+h-1))
        for i, (cx, cy) in zip(f, corners): p.uv[i] = ((cx+.5)/size, 1-(cy+.5)/size)
        islands.append((pi, fi, x0, y0, w, h))
    return islands, low


# -------------------------------------------------------------- skeleton
SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 31)), ('waist', 'pelvis', (0, 0, 36)),
         ('chest', 'waist', (-1, 0, 46)), ('head', 'chest', (3, 0, 73.2))]
ARM = {'upper': (-1, 19.5, 62), 'lower': (-2.5, 21.3, 46.5), 'end': (4, 22.2, 31)}
LEG = {'upper': (0, 8.5, 30), 'lower': (3.5, 9.5, 17), 'end': (.5, 9.8, 5.5)}
for side, sign in (('L', 1), ('R', -1)):
    SPECS.append((f'pauldron_{side}', 'chest', (-1, sign*18, 68)))
    parent = 'chest'
    for joint in ('upper', 'lower', 'end'):
        x, y, z = ARM[joint]; SPECS.append((f'arm_{side}_{joint}', parent, (x, sign*y, z))); parent = f'arm_{side}_{joint}'
    parent = 'pelvis'
    for joint in ('upper', 'lower', 'end'):
        x, y, z = LEG[joint]; SPECS.append((f'leg_{side}_{joint}', parent, (x, sign*y, z))); parent = f'leg_{side}_{joint}'
A_RIG = Rig.from_world(SPECS); A_REST = A_RIG.rest
# Poses are authored at A_RIG scale; the exported statue is uniformly scaled so
# the whole silhouette, including raised fists, reads in the gameplay camera.
SCALE = .86
RIG = Rig.from_world([(n, p, mul(v, SCALE)) for n, p, v in SPECS]); BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
PARENT = [p for n, p, v in BONES]
CLIPS = [('idle', 48, 16, True), ('stomp', 36, 30, True), ('smash', 31, 30, False),
         ('backhand', 29, 30, False), ('recoil', 15, 30, False), ('crumble', 45, 30, False)]
A_FEET = {s: A_REST[IDS[f'leg_{s}_end']] for s in 'LR'}
FEET = {s: REST[IDS[f'leg_{s}_end']] for s in 'LR'}


def authoring_parts():
    parts = []; B = lambda *a, **k: parts.append(carved_block(*a, **k)); C = lambda *a, **k: parts.append(stone_core(*a, **k))
    # Pelvis girdle with a hanging front fauld and a rear plate.
    B('pelvis_block', 'pelvis', (-.5, 0, 30.6), (8.6, 12.6, 4.7), bevel=2.6, seed=1,
      shape=lambda v: (v[0], v[1]*(1-.05*(v[2]/4.7)), v[2]))
    B('pelvis_fauld', 'pelvis', (8.3, 0, 25.6), (1.6, 6.2, 5.2), rot=euler(0, -9, 0), seed=2, pillow=.5,
      shape=lambda v: (v[0], v[1]*(1-.18*max(0, -v[2]/5.2)), v[2]))
    B('pelvis_rear', 'pelvis', (-8.6, 0, 27.2), (1.5, 7.2, 4.0), rot=euler(0, 8, 0), seed=3, pillow=.4)
    # Two stacked abdominal drums: a readable seam between segments.
    C('core_waist', 'waist', (0, 0, 38.5), 6.4, seed=4)
    B('waist_lower', 'waist', (0, 0, 37.7), (7.0, 10.0, 2.5), bevel=1.6, seed=5)
    B('waist_upper', 'waist', (.4, 0, 42.4), (7.8, 11.3, 2.6), bevel=1.6, seed=6)
    # Top-heavy wedge chest that leans forward, with pillowed pectoral masses.
    def chest(v):
        x, y, z = v; t = (z/13.2+1)/2
        return (x*(.84+.16*t)+2.2*t*t, y*(.70+.30*t), z)
    B('chest_block', 'chest', (-1.8, 0, 58.6), (11.0, 17.4, 13.2), bevel=4.2, seed=7, chip=1.2, shape=chest, hewn=.06)
    for s in (1, -1):
        B(f'chest_pec_{s}', 'chest', (9.2, s*7.6, 62.0), (2.8, 7.2, 6.2), rot=euler(s*4, 10, s*14), seed=8+s,
          pillow=.55, shape=lambda v: (v[0], v[1], v[2]-.35*max(0, v[1]*s)*(1+v[2]/6.2)*.5))
        B(f'chest_flank_{s}', 'chest', (1.0, s*14.4, 52.5), (6.0, 2.4, 4.8), rot=euler(s*-8, 0, 0), seed=12+s, pillow=.4)
    B('chest_collar', 'chest', (-.4, 0, 71.2), (8.2, 12.4, 2.0), bevel=1.6, seed=10)
    for i, z in enumerate((65, 58, 51)):
        B(f'chest_spine_{i}', 'chest', (-13.2+.4*i, 0, z), (1.8, 3.3-.3*i, 2.8), seed=20+i, pillow=.4)
    # Small, rounded head sunk forward between the shoulders under a heavy brow.
    C('core_neck', 'head', (2.5, 0, 70.5), 4.8, seed=24)
    B('head_cranium', 'head', (3.2, 0, 74.4), (5.2, 5.4, 4.6), bevel=4.0, seed=25, pillow=.25,
      shape=lambda v: (v[0], v[1]*(1-.16*max(0, v[2]/4.6)), v[2]))
    # Stern carved face: heavy overhanging brow, deep sockets, hard squared jaw.
    B('head_brow', 'head', (7.4, 0, 76.1), (2.4, 6.1, 1.6), rot=euler(0, 12, 0), bevel=1.3, seed=26, pillow=.3,
      shape=lambda v: (v[0]-.14*v[1]*v[1]/6.1-.6*max(0, v[2]/1.6), v[1], v[2]))
    B('head_jaw', 'head', (5.3, 0, 69.8), (4.0, 5.0, 2.3), bevel=1.4, seed=27, pillow=.15,
      shape=lambda v: (v[0]+.4*max(0, -v[2]/2.3), v[1]*(1-.10*(v[0]/4.0)), v[2]))
    B('head_nose', 'head', (8.8, 0, 73.6), (1.2, 1.05, 2.2), rot=euler(0, 12, 0), bevel=.6, seed=28, chip=.5,
      shape=lambda v: (v[0], v[1]*(.55+.45*(v[2]+2.2)/4.4), v[2]))
    for s in (1, -1):
        B(f'head_eye_{s}', 'head', (8.3, s*2.95, 74.7), (.7, 1.35, .78), bevel=.6, seed=29+s, chip=0, role='void', pillow=0, hewn=0)
    for side, s in (('L', 1), ('R', -1)):
        k = 40 if side == 'L' else 60
        # Boulder pauldron with a stacked cap; separate bone so it can fall.
        B(f'pauldron_{side}', f'pauldron_{side}', (-1, s*19.2, 68.0), (9.2, 8.0, 6.6), rot=euler(s*-13, 0, 0),
          bevel=4.6, seed=k, chip=1.5, rough=.4, hewn=.14)
        B(f'pauldron_cap_{side}', f'pauldron_{side}', (-.6, s*17.6, 74.4), (6.0, 5.4, 2.1), rot=euler(s*-15, 0, 0),
          bevel=1.8, seed=k+1, pillow=.35)
        sh, el, wr = (tuple(A_REST[IDS[f'arm_{side}_{j}']]) for j in ('upper', 'lower', 'end'))
        C(f'core_shoulder_{side}', f'arm_{side}_upper', add(sh, (0, 0, -1)), 5.6, seed=k+2)
        B(f'upperarm_{side}', f'arm_{side}_upper', lerp(sh, el, .48), (5.1, 4.9, 7.4), rot=along(sh, el),
          seed=k+3, shape=lambda v: (v[0]*(1+.06*v[2]/7.4), v[1]*(1+.06*v[2]/7.4), v[2]))
        C(f'core_elbow_{side}', f'arm_{side}_lower', el, 4.5, seed=k+4)
        B(f'forearm_{side}', f'arm_{side}_lower', lerp(el, wr, .5), (6.0, 5.6, 7.3), rot=along(el, wr),
          seed=k+5, shape=lambda v: (v[0]*(1-.1*v[2]/7.3), v[1]*(1-.1*v[2]/7.3), v[2]))
        B(f'forearm_band_{side}', f'arm_{side}_lower', lerp(el, wr, .8), (6.7, 6.3, 1.3), rot=along(el, wr),
          bevel=1.0, seed=k+6, pillow=.2)
        C(f'core_wrist_{side}', f'arm_{side}_end', wr, 3.8, seed=k+7)
        # Huge fist: boulder palm, two rows of rounded curled-finger knuckles, thumb inside.
        B(f'fist_{side}', f'arm_{side}_end', (4.6, s*22.6, 24.2), (6.0, 5.7, 6.6), bevel=2.8, seed=k+8, chip=1.2)
        for i, dy in enumerate((-3.9, -1.3, 1.3, 3.9)):
            B(f'knuckle_{side}_{i}', f'arm_{side}_end', (10.0-.25*abs(dy), s*22.6+dy, 20.2), (2.2, 1.35, 2.1),
              bevel=1.1, seed=k+9+i, chip=.6, pillow=.2)
            B(f'finger_{side}_{i}', f'arm_{side}_end', (10.3-.25*abs(dy), s*22.6+dy, 25.4), (1.8, 1.25, 2.6),
              bevel=1.0, seed=k+30+i, chip=.5, pillow=.2)
        B(f'thumb_{side}', f'arm_{side}_end', (8.2, s*17.2, 26.2), (3.3, 1.7, 2.2), rot=euler(0, 25, 0), bevel=1.2, seed=k+14)
        hp, kn, an = (tuple(A_REST[IDS[f'leg_{side}_{j}']]) for j in ('upper', 'lower', 'end'))
        C(f'core_hip_{side}', f'leg_{side}_upper', hp, 5.2, seed=k+15)
        B(f'thigh_{side}', f'leg_{side}_upper', lerp(hp, kn, .47), (6.3, 6.0, 6.0), rot=along(hp, kn),
          seed=k+16, shape=lambda v: (v[0]*(1-.08*v[2]/6), v[1]*(1-.08*v[2]/6), v[2]))
        C(f'core_knee_{side}', f'leg_{side}_lower', kn, 4.7, seed=k+17)
        B(f'kneecap_{side}', f'leg_{side}_lower', add(kn, (4.4, 0, .2)), (1.8, 3.6, 3.1), bevel=1.2, seed=k+18, pillow=.3)
        B(f'shin_{side}', f'leg_{side}_lower', lerp(kn, an, .5), (5.3, 5.1, 5.0), rot=along(kn, an),
          seed=k+19, shape=lambda v: (v[0]*(1+.12*v[2]/5), v[1]*(1+.12*v[2]/5), v[2]))
        C(f'core_ankle_{side}', f'leg_{side}_end', add(an, (0, 0, .3)), 3.9, seed=k+20)
        B(f'foot_{side}', f'leg_{side}_end', (3.0, s*10.0, 2.8), (8.0, 5.6, 2.3), bevel=1.6, seed=k+21, rough=.08,
          pillow=0, hewn=.03, shape=lambda v: (v[0], v[1]*(1-.1*max(0, v[0]/8)), v[2]))
        for i, dy in enumerate((-3.6, 0, 3.6)):
            B(f'toe_{side}_{i}', f'leg_{side}_end', (11.4, s*10+dy, 1.85), (1.7, 1.6, 1.4), bevel=1.0, seed=k+22+i,
              rough=.06, pillow=0, hewn=.02)
    for p in parts:
        if p.bone == 'head':
            # Enlarge and lift the head so it reads above the pauldrons.
            pivot = (3, 0, 71); lift = lambda v: add(add(pivot, mul(sub(v, pivot), 1.12)), (0, 0, 2.2))
            p.vertices = [lift(v) for v in p.vertices]
            c, cols, half = p.box; p.box = (lift(c), cols, mul(half, 1.12))
    for p in parts:
        # Rigid stone rests above the floor at every vertex; the lowest face sits at 0.3.
        assert min(v[2] for v in p.vertices) > .2, p.name
    return parts


def build_parts():
    """Exported parts: authoring parts uniformly scaled (rigid, so exact)."""
    parts = authoring_parts()
    for p in parts:
        p.vertices = [mul(v, SCALE) for v in p.vertices]
        c, cols, half = p.box; p.box = (mul(c, SCALE), cols, mul(half, SCALE))
    return parts


def weights(part, v, uv): return [(IDS[part.bone], 1)]


# ------------------------------------------------------------------ posing
def world_rest():
    return [(tuple(A_REST[i]), (0.0, 0.0, 0.0, 1.0)) for i in range(len(BONES))]


def frame_from_world(world):
    frame = []
    for i, (name, parent, local) in enumerate(BONES):
        loc, q = world[i]; loc = mul(loc, SCALE)
        if parent < 0: frame.append((*loc, *q, 1, 1, 1)); continue
        ploc, pq = world[parent]; ploc = mul(ploc, SCALE); inv = inverse(pq)
        frame.append((*rotate(inv, sub(loc, ploc)), *qmul(inv, q), 1, 1, 1))
    return frame


def two_bone(world, names, target, bend, end_q=None, reach=None):
    """Analytic IK in world space. ``bend``: direction the middle joint moves toward.

    Planted limbs (reach=None) must reach exactly; free arms pass ``reach`` to
    clamp an over-long target to that fraction of full extension.
    """
    ids = [IDS[n] for n in names]; a0, b0, c0 = (A_REST[i] for i in ids)
    root = world[ids[0]][0]; a = math.dist(a0, b0); b = math.dist(b0, c0); d = math.dist(root, target)
    if reach is not None and d > reach*(a+b):
        target = add(root, mul(unit(sub(target, root)), reach*(a+b))); d = reach*(a+b)
    if not abs(a-b)+1e-6 < d < a+b-1e-6: raise ValueError(('unreachable golem limb', names, target, d, a+b))
    direction = unit(sub(target, root)); along_d = (a*a-b*b+d*d)/(2*d)
    n = unit(sub(bend, mul(direction, dot(bend, direction))))
    mid = add(root, add(mul(direction, along_d), mul(n, math.sqrt(max(0.0, a*a-along_d*along_d)))))
    rest_dir = unit(sub(c0, a0)); rest_bend = sub(b0, add(a0, mul(rest_dir, dot(sub(b0, a0), rest_dir))))
    qa = frame_rotation(sub(b0, a0), rest_bend, sub(mid, root), n)
    qb = frame_rotation(sub(c0, b0), rest_bend, sub(target, mid), n)
    world[ids[0]] = (root, qa); world[ids[1]] = (mid, qb)
    world[ids[2]] = (tuple(target), end_q if end_q is not None else qb)


def fk(frame):
    return [tuple(x) for x in A_RIG.matrices(frame)]


def body_frame(rot=None, shift=None):
    rot = rot or {}; shift = shift or {}
    return [(*add(local, shift.get(n, (0, 0, 0))), *rot.get(n, (0, 0, 0, 1)), 1, 1, 1) for n, p, local in A_RIG.bones]


def settle(part_vertices, pivot, q, xy, floor=.35):
    """World pivot location that rests rotated rigid vertices on the floor at ``xy``."""
    moved = [rotate(q, sub(v, pivot)) for v in part_vertices]
    cx = sum(v[0] for v in moved)/len(moved); cy = sum(v[1] for v in moved)/len(moved)
    return (xy[0]-cx, xy[1]-cy, floor-min(v[2] for v in moved))


_PIECES = None


def pieces():
    """Rest vertices per bone, for settling rubble in the crumble clip."""
    global _PIECES
    if _PIECES is None:
        _PIECES = {}
        for p in authoring_parts(): _PIECES.setdefault(p.bone, []).extend(p.vertices)
    return _PIECES


def Q(x=0, y=0, z=0):
    return qmul(axis((0, 0, 1), math.radians(z)), qmul(axis((0, 1, 0), math.radians(y)), axis((1, 0, 0), math.radians(x))))


# Final rubble: every rigid piece lies on the floor inside the cell. Rotations
# are authored; floor contact is solved from the actual piece vertices.
RUBBLE = {
    'leg_L_end': ((2.5, 10.5), Q(0, 0, 7)), 'leg_R_end': ((2.0, -10.5), Q(0, 0, -5)),
    'leg_L_upper': ((5, 11), Q(8, -88, 12)), 'leg_R_upper': ((5, -11.5), Q(-6, -86, -9)),
    'leg_L_lower': ((20, 12.5), Q(0, -90, -8)), 'leg_R_lower': ((20.5, -12), Q(0, -92, 10)),
    'pelvis': ((12, 0), Q(0, -14, 4)), 'waist': ((3, -.5), Q(4, -88, 6)),
    'chest': ((-15, 0), Q(0, -90, 2)), 'head': ((21.5, .5), Q(20, 96, -25)),
    'pauldron_L': ((-15, 22), Q(-78, 12, 8)), 'pauldron_R': ((-16, -21.5), Q(82, -8, -6)),
    'arm_L_upper': ((-9, 23.2), Q(0, -90, 0)), 'arm_R_upper': ((-10, -23.2), Q(0, -90, 0)),
    'arm_L_lower': ((6, 23.3), Q(0, -90, 4)), 'arm_R_lower': ((5, -23.3), Q(0, -88, -4)),
    'arm_L_end': ((20.5, 23), Q(0, -90, 8)), 'arm_R_end': ((19.5, -23), Q(0, -86, -6)),
}
# Rubble on top of other rubble rests at this extra height (authored stacking).
STACK = {'leg_L_upper': 3.0, 'leg_R_upper': 3.0, 'pelvis': 5.0, 'pauldron_L': 2.0, 'pauldron_R': 2.0}
# (start, end) of each piece's fall inside the crumble clip.
TIMING = {'leg_L_end': (.10, .40), 'leg_R_end': (.10, .40), 'leg_L_lower': (.30, .66), 'leg_R_lower': (.28, .64),
          'leg_L_upper': (.30, .70), 'leg_R_upper': (.30, .70), 'pelvis': (.26, .72), 'waist': (.30, .76),
          'chest': (.36, .88), 'head': (.22, .62), 'pauldron_L': (.28, .64), 'pauldron_R': (.34, .70),
          'arm_L_upper': (.40, .78), 'arm_R_upper': (.42, .80), 'arm_L_lower': (.36, .74), 'arm_R_lower': (.38, .76),
          'arm_L_end': (.34, .72), 'arm_R_end': (.36, .74)}


def rubble_world():
    world = world_rest(); P = pieces()
    for name, (xy, q) in RUBBLE.items():
        i = IDS[name]; loc = settle(P.get(name, [A_REST[i]]), A_REST[i], q, xy, .35+STACK.get(name, 0))
        world[i] = (tuple(loc), q)
    return world


_RUBBLE = None


def kneel_world(s):
    """First crumble stage: knees buckle and the statue sags onto its heels."""
    body = body_frame({'pelvis': Q(0, 10*s, 0), 'chest': Q(0, 16*s, 0), 'head': Q(0, 18*s, 0)},
                      {'pelvis': (-3*s, 0, -9*s)})
    world = fk(body)
    for side, sign in (('L', 1), ('R', -1)):
        arm_rest(world, side, (0, sign*1.5*s, -2*s))
        two_bone(world, [f'leg_{side}_upper', f'leg_{side}_lower', f'leg_{side}_end'], A_FEET[side], (1, 0, 0), (0, 0, 0, 1))
    return world


def arm_rest(world, side, offset=(0, 0, 0), bend=(-1, 0, 0), end_q=None):
    sign = 1 if side == 'L' else -1; names = [f'arm_{side}_{j}' for j in ('upper', 'lower', 'end')]
    ch = world[IDS['chest']]; ids = [IDS[n] for n in names]
    # Wrist target follows the chest like a hanging arm, plus an offset.
    target = add(ch[0], rotate(ch[1], sub(A_REST[ids[2]], A_REST[IDS['chest']])))
    world[ids[0]] = (add(ch[0], rotate(ch[1], sub(A_REST[ids[0]], A_REST[IDS['chest']]))), world[ids[0]][1])
    two_bone(world, names, add(target, offset), rotate(ch[1], bend), end_q, reach=.985)


def attach_pauldrons(world, lift=(0, 0, 0), roll=0):
    ch = world[IDS['chest']]
    for side, sign in (('L', 1), ('R', -1)):
        i = IDS[f'pauldron_{side}']
        world[i] = (add(add(ch[0], rotate(ch[1], sub(A_REST[i], A_REST[IDS['chest']]))), lift if side == 'L' else (lift[0], -lift[1], lift[2])),
                    qmul(ch[1], Q(sign*roll, 0, 0)))


SMASH_WRIST = (25.0, 7.5, 12.0)
SWEEP_WRIST = (19.0, -26.5, 56.0)
STANCE = 3.0


def pose(name, t):
    global _RUBBLE
    phase = math.tau*t
    if name == 'idle':
        # A statue's slow grinding weight shift, not breathing.
        body = body_frame({'waist': Q(.6*math.sin(phase), 0, 0), 'chest': Q(0, .8*math.sin(phase), 1.2*math.sin(phase)),
                           'head': Q(0, 0, 4*math.sin(phase))}, {'pelvis': (0, .5*math.sin(phase), 0)})
        world = fk(body)
        for side in 'LR':
            arm_rest(world, side, (.6*math.sin(phase+(0 if side == 'L' else 1)), 0, .4*math.cos(phase)))
            two_bone(world, [f'leg_{side}_upper', f'leg_{side}_lower', f'leg_{side}_end'], A_FEET[side], (1, 0, 0), (0, 0, 0, 1))
    elif name == 'stomp':
        sway = math.sin(phase)
        bob = -1.1*abs(math.cos(phase))
        body = body_frame({'pelvis': Q(-3*sway, 0, 4*math.cos(phase)), 'chest': Q(2*sway, 3, -6*math.cos(phase)),
                           'head': Q(-1.5*sway, 0, 3*math.cos(phase))}, {'pelvis': (0, 1.6*sway, bob)})
        world = fk(body)
        for side, offset in (('L', 0), ('R', .5)):
            q = (t+offset) % 1
            if q < .6: dx = 4.5-9.0*q/.6; lift = 0.0; pitch = 0.0
            else:
                u = (q-.6)/.4; dx = -4.5+9*smooth(u); lift = 4.2*math.sin(math.pi*u); pitch = -9*math.sin(math.pi*u)
            foot = add(A_FEET[side], (dx, 0, lift))
            two_bone(world, [f'leg_{side}_upper', f'leg_{side}_lower', f'leg_{side}_end'], foot, (1, 0, 0), Q(0, pitch, 0))
            swing = -math.cos(phase+offset*math.tau)
            arm_rest(world, side, (5.5*swing, 0, 1.2*abs(swing)))
        attach_pauldrons(world)
    elif name == 'smash':
        # Double fists raised over the head in the windup (t=.3); the middle frame
        # holds a deep forward-lunging slam with both fists driven to the floor.
        up = window(t, .04, .28)*(1-window(t, .33, .44))
        slam = window(t, .33, .44)*(1-window(t, .66, 1.0))
        body = body_frame({'waist': Q(0, -6*up+13*slam, 0), 'chest': Q(0, -10*up+19*slam, 0),
                           'head': Q(0, -8*up-14*slam, 0), 'pelvis': Q(0, 10*slam, 0)},
                          {'pelvis': (-.8*up+1.5*slam, 0, -.6*up-9.5*slam)})
        world = fk(body)
        ch = world[IDS['chest']]
        attach_pauldrons(world, (0, 0, 2.2*up), 10*up)
        for side, sign in (('L', 1), ('R', -1)):
            names = [f'arm_{side}_{j}' for j in ('upper', 'lower', 'end')]
            ids = [IDS[n] for n in names]
            shoulder = add(add(ch[0], rotate(ch[1], sub(A_REST[ids[0]], A_REST[IDS['chest']]))), (0, -sign*1.0*up, 2.6*up))
            world[ids[0]] = (shoulder, world[ids[0]][1])
            hang = add(ch[0], rotate(ch[1], sub(A_REST[ids[2]], A_REST[IDS['chest']])))
            apex = (5.0, sign*7.0, 80.0); strike = (SMASH_WRIST[0], sign*SMASH_WRIST[1], SMASH_WRIST[2])
            target = lerp(lerp(hang, apex, up), strike, slam)
            bend = unit(lerp(lerp((-1, 0, 0), (-.2, sign*1, .1), up), (-.3, sign*.5, 1), slam))
            two_bone(world, names, target, bend, frame_rotation((0, 0, -1), (1, 0, 0), (.55, 0, -.83), (1, 0, .5)) if slam > .5 else None, reach=.985)
        for side in 'LR':
            two_bone(world, [f'leg_{side}_upper', f'leg_{side}_lower', f'leg_{side}_end'], A_FEET[side], (1, 0, 0), (0, 0, 0, 1))
    elif name == 'backhand':
        # Cocked across the chest at t=.25; the middle frame holds a wide horizontal
        # sweep: right arm straight out at shoulder height, torso twisted ~45 degrees,
        # left shoulder pulled back and the stance widened.
        wind = window(t, .04, .26)*(1-window(t, .32, .45))
        sweep = window(t, .32, .45)*(1-window(t, .66, 1.0))
        body = body_frame({'waist': Q(0, 0, 10*wind-20*sweep), 'chest': Q(-4*wind+4*sweep, -6*wind+2*sweep, 16*wind-26*sweep),
                           'head': Q(0, -4*wind, -12*wind+18*sweep)}, {'pelvis': (0, 1.2*wind-1.0*sweep, -1.0*wind-3.0*sweep)})
        world = fk(body)
        attach_pauldrons(world, (0, 0, 1.4*wind), 6*wind)
        ch = world[IDS['chest']]
        names = ['arm_R_upper', 'arm_R_lower', 'arm_R_end']; ids = [IDS[n] for n in names]
        shoulder = add(add(ch[0], rotate(ch[1], sub(A_REST[ids[0]], A_REST[IDS['chest']]))), (0, 0, 2.0*wind))
        world[ids[0]] = (shoulder, world[ids[0]][1])
        hang = add(ch[0], rotate(ch[1], sub(A_REST[ids[2]], A_REST[IDS['chest']])))
        cocked = (6.0, 11.0, 72.0)
        target = lerp(lerp(hang, cocked, wind), SWEEP_WRIST, sweep)
        bend = unit(lerp(lerp((-1, 0, 0), (-.2, -1, .8), wind), (-.3, -.1, -1), sweep))
        two_bone(world, names, target, bend, reach=.995)
        arm_rest(world, 'L', (-8*sweep-3*wind, -3.5*wind+1.5*sweep, 3*wind+2*sweep))
        for side, sign in (('L', 1), ('R', -1)):
            foot = add(A_FEET[side], (sign*1.5*sweep, sign*STANCE*sweep, 0))
            two_bone(world, [f'leg_{side}_upper', f'leg_{side}_lower', f'leg_{side}_end'], foot, (1, sign*.3, 0), Q(0, 0, sign*10*sweep))
    elif name == 'recoil':
        k = math.sin(math.pi*t)**2
        body = body_frame({'waist': Q(3*k, -5*k, 0), 'chest': Q(3*k, -10*k, -6*k), 'head': Q(-6*k, -14*k, 8*k)},
                          {'pelvis': (-2.0*k, 0, -1.2*k)})
        world = fk(body)
        attach_pauldrons(world, (-1.0*k, 0, 1.6*k), -6*k)
        for side, sign in (('L', 1), ('R', -1)):
            arm_rest(world, side, (-6*k, sign*.8*k, 5*k))
            two_bone(world, [f'leg_{side}_upper', f'leg_{side}_lower', f'leg_{side}_end'], A_FEET[side], (1, 0, 0), (0, 0, 0, 1))
    elif name == 'crumble':
        if _RUBBLE is None: _RUBBLE = rubble_world()
        kneel = kneel_world(window(t, 0, .34))
        world = [None]*len(BONES)
        for i, (bone, parent, local) in enumerate(BONES):
            start, end = TIMING.get(bone, (0, 1)) if bone != 'root' else (0, 1)
            if bone == 'root': world[i] = kneel[i]; continue
            u = max(0.0, min(1.0, (t-start)/(end-start)))
            fall = u*u  # accelerating drop
            spin = smooth(u)
            a_loc, a_q = kneel[i]; b_loc, b_q = _RUBBLE[i]
            # Pieces tip outward before dropping: a small arc keeps them apart.
            loc = (a_loc[0]+(b_loc[0]-a_loc[0])*spin, a_loc[1]+(b_loc[1]-a_loc[1])*spin,
                   a_loc[2]+(b_loc[2]-a_loc[2])*fall+1.5*math.sin(math.pi*u))
            world[i] = (loc, slerp(a_q, b_q, spin))
        return frame_from_world(world)
    return frame_from_world(world)


# ------------------------------------------------------------------ export
def geometry():
    parts = build_parts(); layout_islands(parts)
    return assemble(parts, weights)


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes(parts=None):
    if parts is None: parts = build_parts(); layout_islands(parts)
    return golem_materials.paint_atlas(parts)


def build():
    parts, v, n, uv, tr, w = geometry()
    image, spec = golem_materials.paint(parts)
    skin = golem_materials.encode_png(image.tobytes(), golem_materials.SIZE, golem_materials.SIZE)
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    supplemental = {}
    for name, data in golem_materials.surface_maps(parts, spec=spec).items():
        (ROOT/'mod/BrogueDoom'/name).write_bytes(data); supplemental[name] = hashlib.sha256(data).hexdigest()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_golem', material_path=SKIN)
    path = ROOT/MODEL; path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M49', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
        supplementalMaps=supplemental, parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
        bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
        clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds, authoringSource='assets/monsters/golem/golem-animated.blend')
    out = ROOT/'assets/monsters/golem'; out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n'); return manifest


if __name__ == '__main__':
    # Re-import by package name so every consumer sees one module instance.
    import importlib
    print(importlib.import_module('tools.monster_models.golem_animation').build()['sha256'])
