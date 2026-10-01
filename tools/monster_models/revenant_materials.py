"""Original revenant paint: a heavy grave-shroud, pale skull and bone hands.

Presentation-only. Brogue's ectoplasm glyph colour (45, 20, 55) is an identity
cue: the bruised violet-grey shroud, its pale ectoplasm stains and the grave-earth
hem are artistic interpretation, not a new power. Nothing emits light. The
engine's flat sector light hides sculpted form, so value contrast is painted:
top light, fold and hood occlusion, a near-black hood interior framing the
bone-pale skull, and specular pools on bone.

Every triangle of every part gets its own padded 16px island, painted per texel
from its rest-space position and smooth normal (islands in Morton order).
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
    for prefix, r in (('skull_socket', 'dark'), ('skull_nose', 'dark'), ('skull_tooth', 'tooth'),
                      ('skull', 'bone'), ('hand', 'bone'), ('nail', 'nail'),
                      ('rag_hem', 'hem'), ('bind', 'bind'), ('rag', 'cloth'), ('pupil', 'pupil')):
        if name.startswith(prefix):
            return r
    return 'cloth'


ROLES = ('cloth', 'bone', 'dark', 'tooth', 'nail', 'hem', 'bind', 'pupil')
HOOD = (5.2, 0.0, 55.2)
LINEN = (100, 90, 88)
SHADE = (18, 14, 20)
EARTH = (46, 36, 28)
ROT = (50, 52, 38)
STAIN = (128, 104, 150)
BONE = (148, 134, 114)


def mix(a, b, t):
    return tuple(x+(y-x)*t for x, y in zip(a, b))


def vnoise(x, y, z):
    """Smooth deterministic value noise in [0, 1]."""
    xi, yi, zi = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x-xi, y-yi, z-zi
    fx, fy, fz = fx*fx*(3-2*fx), fy*fy*(3-2*fy), fz*fz*(3-2*fz)
    def h(a, b, c):
        n = math.sin(a*127.1+b*311.7+c*74.7)*43758.5453
        return n-math.floor(n)
    out = 0.0
    for dx, wx in ((0, 1-fx), (1, fx)):
        for dy, wy in ((0, 1-fy), (1, fy)):
            for dz, wz in ((0, 1-fz), (1, fz)):
                out += wx*wy*wz*h(xi+dx, yi+dy, zi+dz)
    return out


def light(normal):
    # Painted top-front key and a darker underside: form under flat light.
    return .74+.34*max(-.6, normal[2]*.75+normal[0]*.25)


def cloth(point, normal, cav, hem=0.0):
    x, y, z = point
    d = math.dist(point, HOOD)
    toward = sum((HOOD[i]-point[i])*normal[i] for i in range(3))/max(d, 1e-6)
    if d < 6.0 and toward > .1 and z > 50.5:
        # Cowl interior: near-black so the skull emerges from shadow.
        depth = smooth(6.0, 4.0, d)*smooth(.1, .5, toward)
        return mix((20, 15, 22), (3, 2, 4), depth)
    ang = math.atan2(y, x+1)
    # Strong painted folds: sharpened stripes with deep troughs.
    # Irregular folds: noise-warped, varying in depth along their length.
    warp = 2.2*vnoise(ang*1.3, z*.07, 4.1)
    f = math.sin(ang*7+warp+z*.05)+.45*math.sin(ang*15+1.7*warp+1.3)
    f *= .45+.75*vnoise(ang*2.1, z*.12, 9.3)
    f = max(-1, min(1, f*.8))
    c = mix(SHADE, LINEN, .6+.34*math.copysign(abs(f)**.8, f))
    c = tuple(v*(1+.07*math.sin(z*7.1+ang*23)*math.sin(ang*31)) for v in c)
    # Rot blotches and grave earth that darkens toward the shredded hem.
    rot = smooth(.55, .8, vnoise(x*.28, y*.28, z*.22))
    c = mix(c, ROT, .6*rot)
    c = mix(c, EARTH, .85*smooth(30, 11, z)+.15*hem)
    # Dull ectoplasm stains, short and blotchy rather than stripes.
    stain = smooth(.66, .86, vnoise(x*.5+3, y*.5, z*.18))*smooth(18, 30, z)*smooth(52, 40, z)
    c = mix(c, STAIN, .45*stain)
    c = tuple(v*light(normal) for v in c)
    # Frayed convex edges catch light; folds, armpits and overlaps sink.
    edge = max(0.0, -cav)*1.4
    occl = max(0.0, cav)*3.4+.4*smooth(0, -.9, normal[2])
    return tuple(min(255, v*max(.22, 1-occl)*(1+edge)) for v in c)


def hem(point, normal, cav):
    x, y, z = point
    c = cloth(point, normal, cav, 1.0)
    # Strips fade into darkness toward their tips: the specter dissolves.
    fade = smooth(15, 2, z)
    return mix(c, (8, 6, 10), .85*fade)


def binding(point, normal, cav):
    x, y, z = point
    c = mix((110, 98, 86), (66, 58, 52), vnoise(x*.6, y*.6, z*.6))
    c = mix(c, EARTH, .6*smooth(30, 16, z))
    c = tuple(v*light(normal)*(1+.12*math.sin(z*11+x*5)) for v in c)
    return tuple(v*max(.3, 1-max(0.0, cav)*3) for v in c)


def bone(point, normal, cav, name):
    x, y, z = point
    c = BONE
    if name.startswith('skull'):
        # Deep in the cowl: the upper skull falls into shadow, the jaw is lit.
        # The cowl's shadow falls across the brow and crown.
        shadow = max(smooth(7.2, 4.2, x), .8*smooth(55.6, 58.2, z))
        c = mix(c, (52, 44, 42), shadow)
        hollow = math.exp(-((abs(y)-1.8)/.8)**2-((z-54.1)/.9)**2)*smooth(6.2, 8.2, x)
        c = mix(c, (58, 48, 44), .65*hollow)
        # Thin wandering cracks, not speckle.
        crack = smooth(.94, .995, 1-abs(math.sin(y*1.9+z*1.1+.9*math.sin(z*3.3+y))))
        crack *= smooth(.3, .6, vnoise(y*.9, z*.9, 1.7))
        c = mix(c, (30, 24, 22), .85*crack)
    elif name.startswith('hand'):
        knuckle = abs(math.sin(z*2.4))**4
        c = mix(c, (52, 44, 38), .6*knuckle)
        c = mix(c, (92, 80, 66), .55+.2*math.sin(x*3+y*5))
    spec = max(0.0, normal[2]*.6+normal[0]*.5)**6
    c = mix(tuple(v*light(normal) for v in c), (210, 200, 180), .35*spec)
    occl = max(0.0, cav)*3.2+.3*smooth(.1, -.8, normal[2])
    return tuple(v*max(.3, 1-occl) for v in c)


def pigment(point, normal, name, cav):
    r = role(name)
    if r == 'cloth':
        return cloth(point, normal, cav)
    if r == 'hem':
        return hem(point, normal, cav)
    if r == 'bind':
        return binding(point, normal, cav)
    if r == 'bone':
        return bone(point, normal, cav, name)
    if r == 'dark':
        return (8, 6, 9)
    if r == 'tooth':
        return mix((110, 98, 76), (160, 148, 118), max(0, normal[0]))
    if r == 'nail':
        return mix((22, 16, 16), (70, 58, 54), max(0, normal[2]*.5+normal[0]*.5))
    return (120, 150, 190)
