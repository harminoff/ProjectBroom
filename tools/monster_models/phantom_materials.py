"""Original phantom paint: a violet ectoplasm apparition read through its outline.

Presentation-only. Brogue's ectoplasm glyph colour (45, 20, 55) is an identity
cue: the violet body, pale lilac face and near-white ectoplasm droplets are
artistic interpretation. The runtime draws this skin additively and fullbright
(see shaders/phantom-veil.fp), so painted value is opacity: black eye sockets
and mouth read as holes, the dim interior lets the rim shader outline the
silhouette, and the chest core and droplets glow brightest. No world light,
visibility rule, simulation input or RNG.

Every triangle of every part gets its own padded 16px island, painted per texel
from its rest-space position and smooth normal, so the fused cage and its
accessories share one continuous pigment field. Islands are laid out in Morton
order of their centroids so mipmaps average spatial neighbours, not speckle.
"""
import math
import struct
import zlib

SIZE = 2048
CELL = 16
GRID = SIZE//CELL


def encode_png(pixels, width, height):
    def chunk(k, d):
        return struct.pack('>I', len(d))+k+d+struct.pack('>I', zlib.crc32(k+d) & 0xffffffff)
    raw = b''.join(b'\0'+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))+chunk(b'IEND', b''))


def _spread(v, bits):
    out = 0
    for i in range(bits):
        out |= ((v >> i) & 1) << (3*i)
    return out


def _cell(k):
    """2D Morton decode of island index k into a GRID x GRID layout."""
    x = y = 0
    for i in range(7):
        x |= ((k >> (2*i)) & 1) << i
        y |= ((k >> (2*i+1)) & 1) << i
    return x, y


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x-a)/(b-a)))
    return t*t*(3-2*t)


def cavity(part):
    """Per-vertex concavity from the welded 1-ring, relaxed twice (0 = flat)."""
    keys = [tuple(round(c, 5) for c in v) for v in part.vertices]
    index = {}
    for k in keys:
        index.setdefault(k, len(index))
    points = [None]*len(index)
    for k, i in index.items():
        points[i] = k
    ring = [set() for _ in points]
    for tri in part.triangles():
        ids = [index[keys[i]] for i in tri]
        for a in ids:
            for b in ids:
                if a != b:
                    ring[a].add(b)
    normals = part.normals()
    normal_of = [None]*len(points)
    for k, n in zip(keys, normals):
        normal_of[index[k]] = n
    value = []
    for i, p in enumerate(points):
        if not ring[i]:
            value.append(0.0)
            continue
        n = normal_of[i]
        nb = sorted(ring[i])
        edge = math.fsum(math.dist(p, points[j]) for j in nb)/len(nb)
        d = math.fsum(sum((points[j][a]-p[a])*n[a] for a in range(3)) for j in nb)/len(nb)
        value.append(max(-1.0, min(1.0, d/max(edge, 1e-6))))
    for _ in range(2):
        value = [(value[i]+math.fsum(value[j] for j in sorted(ring[i]))/max(1, len(ring[i])))/2 for i in range(len(points))]
    return [value[index[k]] for k in keys], normals


def bake(parts, weights, pigment, pixels=False):
    """Rebuild every part as per-triangle islands; optionally paint the atlas.

    Returns new parts carrying explicit skin weights (cage weights/topology are
    kept; accessories use weights()). pigment(point, normal, part_name, cav).
    """
    from .rat import Part
    tris = []
    info = []
    for pi, p in enumerate(parts):
        cav, normals = cavity(p) if pixels else (None, p.normals())
        info.append((cav, normals))
        for t in p.triangles():
            tris.append((pi, t))
    if len(tris) > GRID*GRID:
        raise ValueError(f'{len(tris)} triangles exceed the {GRID*GRID} island atlas')
    lo = [min(p.vertices[i][a] for p in parts for i in range(len(p.vertices))) for a in range(3)]
    hi = [max(p.vertices[i][a] for p in parts for i in range(len(p.vertices))) for a in range(3)]
    def key(item):
        pi, t = item[1]
        c = [math.fsum(parts[pi].vertices[i][a] for i in t)/3 for a in range(3)]
        q = [min(1023, int(1023*(c[a]-lo[a])/max(1e-9, hi[a]-lo[a]))) for a in range(3)]
        return (_spread(q[0], 10) | _spread(q[1], 10) << 1 | _spread(q[2], 10) << 2, item[0])
    order = [i for i, _ in sorted(enumerate(tris), key=key)]
    slot = {tri_index: k for k, tri_index in enumerate(order)}
    out = []
    for pi, p in enumerate(parts):
        q = Part(p.name)
        q.skin_weights = []
        cage = hasattr(p, 'skin_weights')
        if cage:
            q.skin_topology = []
        out.append(q)
    buffer = bytearray(SIZE*SIZE*3) if pixels else None
    for tri_index, (pi, t) in enumerate(tris):
        p, q = parts[pi], out[pi]
        cx, cy = _cell(slot[tri_index])
        x0, y0 = cx*CELL, cy*CELL
        base = len(q.vertices)
        for i, (dx, dy) in zip(t, ((2, 2), (14, 2), (2, 14))):
            q.vertices.append(p.vertices[i])
            q.uv.append(((x0+dx)/SIZE, 1-(y0+dy)/SIZE))
            if hasattr(p, 'skin_weights'):
                q.skin_weights.append(p.skin_weights[i])
                q.skin_topology.append(p.skin_topology[i])
            else:
                q.skin_weights.append(weights(p, p.vertices[i], p.uv[i]))
        q.faces.append((base, base+1, base+2))
        if pixels:
            cav, normals = info[pi]
            P = [p.vertices[i] for i in t]
            N = [normals[i] for i in t]
            C = [cav[i] for i in t]
            for dy in range(CELL):
                c = (dy+.5-2)/12
                for dx in range(CELL):
                    b = (dx+.5-2)/12
                    wa, wb, wc = max(0.0, 1-b-c), max(0.0, b), max(0.0, c)
                    s = wa+wb+wc
                    wa, wb, wc = wa/s, wb/s, wc/s
                    point = tuple(wa*P[0][k]+wb*P[1][k]+wc*P[2][k] for k in range(3))
                    n = tuple(wa*N[0][k]+wb*N[1][k]+wc*N[2][k] for k in range(3))
                    ln = math.sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2]) or 1.0
                    rgb = pigment(point, (n[0]/ln, n[1]/ln, n[2]/ln), p.name, wa*C[0]+wb*C[1]+wc*C[2])
                    o = ((y0+dy)*SIZE+x0+dx)*3
                    buffer[o:o+3] = bytes(max(0, min(255, round(v))) for v in rgb)
    if pixels:
        return encode_png(buffer, SIZE, SIZE)
    return out


def role(name):
    if name.startswith('drop'):
        return 'glow'
    if name.startswith('claw'):
        return 'claw'
    if name.startswith('hair'):
        return 'hair'
    if name.startswith('tatter'):
        return 'tatter'
    return 'body'


ROLES = ('body', 'glow', 'claw', 'hair', 'tatter')

VIOLET = (104, 62, 158)
LILAC = (206, 184, 246)
CORE = (236, 214, 255)


def mix(a, b, t):
    return tuple(x+(y-x)*t for x, y in zip(a, b))


def _ellipse(dy, dz, ry, rz, tilt):
    ca, sa = math.cos(tilt), math.sin(tilt)
    u, v = dy*ca+dz*sa, -dy*sa+dz*ca
    return (u/ry)**2+(v/rz)**2


def face(point, normal):
    """Painted holes (0 = hole, 1 = open) and bright socket rims on the face."""
    x, y, z = point
    front = smooth(2.6, 4.2, x)*smooth(-.2, .5, normal[0])
    if front <= 0:
        return 1.0, 0.0
    hole = 1.0
    rim = 0.0
    # Rage-slanted sockets: inner corners pulled down toward the nose.
    for s in (-1, 1):
        e = _ellipse(y-s*1.3, z-57.55, .95, .62, s*.38)
        hole = min(hole, smooth(.55, 1.05, e))
        rim = max(rim, math.exp(-((e-1.35)/.35)**2))
    # Long mournful mouth: a tall open oval whose corners sag.
    m = _ellipse(y, z-53.9, .78+.12*smooth(52.6, 54.6, z), 1.55, 0)
    hole = min(hole, smooth(.6, 1.1, m))
    rim = max(rim, .7*math.exp(-((m-1.4)/.4)**2))
    nose = math.exp(-(y/.35)**2-((z-55.9)/.45)**2)
    hole = min(hole, 1-.55*nose)
    return 1-(1-hole)*front, rim*front


def pigment(point, normal, name, cav):
    x, y, z = point
    r = role(name)
    up = normal[2]
    if r == 'glow':
        # Ectoplasm droplets: near-white core fading to violet at the rim.
        return mix(VIOLET, CORE, .6+.4*max(0, up*.5+.5))
    if r == 'claw':
        return mix(LILAC, CORE, .5)
    if r == 'hair':
        # Dark roots so tendrils behind the skull never veil the face in
        # additive view; luminous only where they stream past the outline.
        t = smooth(-2.5, -10, x)
        return mix((22, 10, 38), mix(VIOLET, LILAC, .45), t*(1-.45*smooth(-11, -15, x)))
    if r == 'tatter':
        # Torn ectoplasm: dim where it leaves the body, glowing mid-strip.
        root = smooth(30, 22, z) if z > 12 else 1
        return mix((20, 10, 34), mix(VIOLET, LILAC, .2), .12+.4*root*smooth(4, 12, z))
    # Fused body: dim translucent violet with a luminous chest core and face.
    fade = .32+.68*smooth(4, 30, z)
    ang = math.atan2(y, x+1.5)
    flow = 1+.2*math.sin(ang*9+z*.35)*smooth(32, 20, z)
    c = mix((58, 30, 96), VIOLET, fade*flow)
    core = math.exp(-((x-1.6)/3.2)**2-(y/3.4)**2-((z-43.5)/5.2)**2)
    c = mix(c, CORE, .75*core)
    ribs = 0.0
    if 36.5 < z < 47 and x > 0:
        ribs = abs(math.sin((z-36.5)*math.pi/1.7))**10*smooth(0.3, 2.4, abs(y))*smooth(6.5, 3.5, abs(y))
    c = mix(c, LILAC, .45*ribs)
    head = smooth(51.5, 53.5, z)
    if head:
        # Only the face mask is bright; the back of the skull stays dim so
        # it cannot fill the painted sockets when seen through the head.
        mask = smooth(1.8, 3.9, x)*smooth(-.2, .55, normal[0])
        skull = mix(mix((40, 20, 70), VIOLET, .5), LILAC, mask)
        c = mix(c, skull, head)
        hole, rim = face(point, normal)
        c = mix(c, CORE, .8*rim)
        c = tuple(v*hole for v in c)
    # Hands brighten toward the claws.
    reach = smooth(7, 12, x)*smooth(9, 11, abs(y))*smooth(35, 30, z)
    c = mix(c, LILAC, .55*reach)
    # Painted occlusion keeps folds, armpits and the neck readable when flat-lit.
    occl = max(0.0, cav)*2.2+.35*smooth(.2, -.8, up)*(1-head)
    return tuple(v*max(.25, 1-occl) for v in c)
