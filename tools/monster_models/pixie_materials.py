"""Original pixie materials. No gameplay meaning; nothing emits light.

2048-square atlas. The connected skin is painted per triangle from continuous
rest positions, normals and bone-weight fractions (left half, 16-pixel islands),
so the face, bodice and limbs carry no source-part colour seams. Accessories
use the top-right quadrant (sixteen 256-pixel role cells); the two wing
membranes share the bottom-right quadrant at higher resolution.

Paint is designed for the engine's flat bright light: baked top light and
occlusion, strong value contrast between pale skin, dark eyes and lashes,
violet eyelids, a deep teal petal bodice, violet petals and pale pearly wings.
The pearly wing iridescence and mixed petal hues nod to the grey glyph colour's
large per-channel random variance and dancing flag; they are art choices.
"""
import math
import struct
import zlib

SKIN = 'graphics/BRGPIXIE.png'
SIZE = 2048
ROLES = ('eye', 'lid', 'lash', 'brow', 'hair', 'hair_cap', 'finger', 'petal_outer',
         'petal_inner', 'collar', 'belt', 'pouch', 'pouch_rim', 'wing_root', 'skin', 'spare')
RECTS = {n: (1024+i % 4*256+8, i//4*256+8, 1024+i % 4*256+248, i//4*256+248) for i, n in enumerate(ROLES)}
RECTS['wing_F'] = (1032, 1032, 2040, 1528)
RECTS['wing_H'] = (1032, 1544, 2040, 2040)
SKIN_ISLANDS = 8192


def role(n):
    if n.startswith('eye_'): return 'eye'
    if n.startswith('lid_'): return 'lid'
    if n.startswith('lash_'): return 'lash'
    if n.startswith('brow_'): return 'brow'
    if n == 'hair_cap': return 'hair_cap'
    if n.startswith('hair_'): return 'hair'
    if n.startswith(('finger_', 'thumb_')): return 'finger'
    if n.startswith('skirt_petal_'): return 'petal_outer' if int(n.split('_')[-1]) % 2 == 0 else 'petal_inner'
    if n.startswith('collar'): return 'collar'
    if n.startswith(('belt', 'pouch_tie')): return 'belt'
    if n == 'pouch_rim': return 'pouch_rim'
    if n == 'pouch': return 'pouch'
    if n.startswith('wing_root'): return 'wing_root'
    if n.startswith('wing_F'): return 'wing_F'
    if n.startswith('wing_H'): return 'wing_H'
    return 'skin'


def repack(parts):
    for p in parts:
        x0, y0, x1, y1 = RECTS[role(p.name)]
        p.uv = [(round((x0+u*(x1-x0))/SIZE, 7), round(1-(y0+v*(y1-y0))/SIZE, 7)) for u, v in p.uv]
    return parts


def local_uv(name, uv):
    x0, y0, x1, y1 = RECTS[role(name)]
    return ((uv[0]*SIZE-x0)/(x1-x0), ((1-uv[1])*SIZE-y0)/(y1-y0))


# ---------------------------------------------------------------- helpers
def hash3(x, y, z):
    h = (x*374761393+y*668265263+z*1274126177) & 0xffffffff
    h = ((h ^ (h >> 13))*1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 1023)/1023


def vnoise(x, y, z):
    """Smooth deterministic value noise in -0.5..0.5."""
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x-ix, y-iy, z-iz
    fx, fy, fz = fx*fx*(3-2*fx), fy*fy*(3-2*fy), fz*fz*(3-2*fz)
    total = 0.
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (fx if dx else 1-fx)*(fy if dy else 1-fy)*(fz if dz else 1-fz)
                total += w*hash3(ix+dx, iy+dy, iz+dz)
    return total-.5


def mix(a, b, t): return tuple(x+(y-x)*t for x, y in zip(a, b))
def clamp(v, lo=0., hi=1.): return max(lo, min(hi, v))
def smooth(x): x = clamp(x); return x*x*(3-2*x)
def scale(c, k): return tuple(x*k for x in c)
def gauss(d, r): return math.exp(-(d/r)**2)


def encode_png(pixels, width, height):
    def chunk(k, d): return struct.pack('>I', len(d))+k+d+struct.pack('>I', zlib.crc32(k+d) & 0xffffffff)
    raw = b''.join(b'\0'+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))+chunk(b'IEND', b''))


def glitter(u, v, density, seed, size=.5):
    """Sparse bright specks on a cell grid in (u, v) given in cell units."""
    iu, iv = math.floor(u), math.floor(v)
    best = 0.
    for du in (-1, 0, 1):
        for dv in (-1, 0, 1):
            cu, cv = iu+du, iv+dv
            if hash3(cu, cv, seed) > density: continue
            px, py = cu+hash3(cu, cv, seed+1), cv+hash3(cu, cv, seed+2)
            d = math.hypot(u-px, v-py)
            best = max(best, clamp(1-d/size)**2)
    return best


# ---------------------------------------------------------------- palette
PALE = (236, 212, 222)
SHADE = (150, 112, 146)
ROSE = (226, 128, 150)
LILAC = (132, 82, 170)
EYESHADOW = (98, 52, 132)
TEAL = (26, 104, 100)
TEAL_DEEP = (12, 52, 58)
VIOLET = (92, 44, 126)
GOLD = (232, 196, 96)
INK = (34, 14, 40)


# ---------------------------------------------------------------- accessories
def shade(name, u, v):
    if name == 'eye':
        # Latitude v: 0 back pole .. 1 front pole. u: 0 = up.
        if v > .885:
            c = (14, 10, 24)
        elif v > .69:
            k = (v-.69)/.195
            c = mix((22, 88, 52), (112, 222, 104), k**.8)
            c = mix(c, (190, 246, 150), .45*smooth((k-.55)/.3)*(1-smooth((k-.92)/.08)))
            ray = .5+.5*math.sin(u*math.tau*22)
            c = scale(c, .86+.14*ray)
            c = mix(c, (10, 36, 22), smooth((.73-v)/.04))
        else:
            c = (238, 234, 242)
            c = mix(c, (156, 142, 176), .7*smooth((.5-min(u, 1-u))/.35)*0+.55*smooth(1-min(u, 1-u)*4))
        glint = gauss(math.hypot((u-.9)*3.2, v-.84), .035)+.7*gauss(math.hypot((u-.42)*3.2, v-.75), .02)
        return mix(c, (255, 255, 255), clamp(glint*1.4))
    if name == 'lid':
        return mix((164, 104, 184), EYESHADOW, smooth((.62-v)/.4))
    if name == 'lash':
        return INK
    if name == 'brow':
        return scale((96, 64, 112), .85+.25*math.sin(u*38+v*6))
    if name in ('hair', 'hair_cap'):
        strand = math.sin((v if name == 'hair' else u)*math.tau*(7 if name == 'hair' else 30)
                          + 5*vnoise(u*6, v*6, 3))
        if name == 'hair':
            t = u
            c = mix((150, 128, 196), (236, 230, 250), smooth(t*1.6))
            c = mix(c, (212, 248, 255), .45*smooth((t-.7)/.3))
        else:
            c = mix((176, 156, 214), (236, 230, 250), smooth((v-.2)/.5))
            c = scale(c, .92+.16*vnoise(u*40, v*12, 5))
        return scale(c, .9+.1*strand)
    if name == 'finger':
        c = mix(PALE, SHADE, .25*(.5-.5*math.cos(v*math.tau)))
        return mix(c, ROSE, .6*smooth((u-.7)/.25))
    if name in ('petal_outer', 'petal_inner'):
        across = abs(v*2-1)
        if name == 'petal_outer':
            c = mix((70, 26, 104), (176, 76, 192), smooth(u*1.3))
            c = mix(c, (238, 178, 236), smooth((across-.72)/.28)*.8+smooth((u-.82)/.18)*.55)
        else:
            c = mix((30, 30, 92), (86, 96, 196), smooth(u*1.3))
            c = mix(c, (170, 196, 246), smooth((across-.75)/.25)*.7+smooth((u-.85)/.15)*.4)
        vein = gauss(across, .045)*(.4+.6*u)
        side = gauss(abs(across-.45-.25*u), .04)*smooth(u*3)*.6
        c = scale(c, 1-.35*vein-.2*side)
        c = scale(c, .78+.22*smooth(u*4))
        return mix(c, (255, 255, 255), .9*glitter(u*18, v*8, .18, 11, .35))
    if name == 'collar':
        across = abs(v*2-1)
        c = mix((196, 120, 196), (250, 226, 246), smooth(u*1.6))
        c = mix(c, (170, 80, 160), gauss(across, .07)*.55)
        c = mix(c, (255, 244, 255), smooth((across-.8)/.2)*.5)
        return scale(c, .8+.2*smooth(u*3))
    if name == 'belt':
        twist = math.sin(math.tau*(u*16+v))
        c = mix((34, 78, 34), (104, 160, 62), .5+.5*twist)
        return scale(c, .75+.25*smooth(1-abs(twist)))
    if name == 'pouch':
        c = mix((70, 40, 22), (150, 98, 54), smooth(v*1.2))
        stitch = gauss(abs(math.sin(math.pi*(u*2))), .08)*(math.sin(v*80) > 0)
        return scale(c, 1-.4*stitch)
    if name == 'pouch_rim':
        c = mix((150, 110, 40), GOLD, .5+.5*math.sin(u*math.tau*9))
        return mix(c, (255, 250, 220), glitter(u*30, v*10, .35, 21, .4))
    if name == 'wing_root':
        return mix((150, 120, 200), (226, 214, 246), v)
    return PALE


def wing_shade(kind, u, v):
    """u: root 0 .. tip 1 along the span; v: leading edge 0 .. trailing edge 1."""
    # Iridescent pearl: gold at the root, cyan through the middle, violet-magenta out.
    hue = u*.9+.25*v+.12*vnoise(u*5, v*4, 9 if kind == 'F' else 19)
    stops = ((0., (238, 214, 146)), (.28, (190, 236, 226)), (.55, (164, 214, 248)), (.8, (206, 168, 246)), (1.1, (238, 150, 222)))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if hue <= b:
            c = mix(ca, cb, clamp((hue-a)/(b-a)))
            break
    else:
        c = stops[-1][1]
    # Veins fan from the root with a gentle wave; staggered cross veins make
    # irregular cells, each brightening toward its middle (pearly membrane).
    veins = (.13, .29, .46, .63, .79) if kind == 'F' else (.17, .37, .57, .77)
    lines = [0.]+[x+.014*math.sin(u*9+k*1.7) for k, x in enumerate(veins)]+[1.]
    band = max(k for k in range(len(lines)-1) if v >= lines[k] or k == 0)
    lo, hi = lines[band], lines[band+1]
    f = clamp((v-lo)/max(1e-6, hi-lo))
    dv = min(v-lo, hi-v)
    crosses = [.2+.75*(n+.15+hash3(band, n, 7 if kind == 'F' else 17)*.7)/2.4 for n in range(2)]
    du = min(abs(u-(c+.09*(f-.5)*(1 if band % 2 else -1))) for c in crosses)
    cell = smooth(dv/.07)*smooth(du/.05)
    c = scale(c, .8+.24*cell)
    width = .011+.013*(1-u)
    vein = max(smooth(1-dv/width) if band > 0 or v > width else 0., .8*smooth(1-du/.0075))
    costa = smooth(1-v/(.045+.02*(1-u)))
    margin = smooth((v-.93)/.05)+smooth((u-.95)/.04)
    c = mix(c, (58, 30, 82), clamp(max(vein*.85, costa*.95, margin*.9)))
    # A dark violet eye-spot ringed in pale gold near the forewing tip.
    if kind == 'F':
        d = math.hypot((u-.8)*1.6, (v-.52)*1.0)
        c = mix(c, (238, 220, 150), gauss(abs(d-.085), .018))
        c = mix(c, (70, 26, 96), smooth(1-d/.07))
    else:
        d = math.hypot((u-.68)*1.4, (v-.5))
        c = mix(c, (88, 40, 120), .75*smooth(1-d/.06))
    return mix(c, (255, 255, 255), .95*glitter(u*60, v*18, .16, 31 if kind == 'F' else 41, .45))


def accessory_pixels(buffer):
    for name, (x0, y0, x1, y1) in RECTS.items():
        pad = 8
        wing = name.startswith('wing_') and name != 'wing_root'
        for y in range(y0-pad, y1+pad):
            if y < 0 or y >= SIZE: continue
            for x in range(x0-pad, x1+pad):
                if x < 1024 or x >= SIZE: continue
                u = clamp((x-x0)/(x1-x0))
                v = clamp((y-y0)/(y1-y0))
                c = wing_shade(name[-1], u, v) if wing else shade(name, u, v)
                o = (y*SIZE+x)*3
                buffer[o:o+3] = bytes(max(0, min(255, round(q))) for q in c)


# ---------------------------------------------------------------- skin
def skin_pigment(point, normal, m):
    """m: dict of continuous bone fractions (head, arm, leg, torso, hand, foot, ear)."""
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    light = clamp(.62+.26*nz+.22*nx)
    c = mix(SHADE, PALE, light**.8)
    # Warm rosy joints and extremities.
    if m['head'] < .5:
        knee = gauss(math.hypot(x-.9, ay-1.75, z-24.0), 1.0)*clamp(nx*1.5)
        elbow = gauss(math.hypot(x-.35, ay-5.25, z-31.3), .8)
        toe = smooth((18.2-z)/1.6)*m['foot']
        c = mix(c, ROSE, .45*knee+.3*elbow+.5*toe)
        # Leaf anklets: a dark vine ring with three tiny leaves.
        ring = gauss(z-19.95-.12*math.sin(math.atan2(y, x)*3), .12)*m['leg']
        c = mix(c, (38, 96, 46), .9*ring)
    else:
        c = face_paint(point, normal, m, c)
    # Petal bodice over the torso.
    if m['torso'] > .35 and m['head'] < .4:
        neck = 35.35+.8*smooth((ay-1.3)/.9)-.45*smooth(x/1.6)*gauss(ay, 1.2)
        body = smooth((m['torso']-.45)/.25)*smooth((neck-z)/.18)*smooth((z-29.0)/.3)
        body *= 1-smooth((m['arm']-.3)/.25)
        if body > 0:
            c = mix(c, bodice(point, normal), body)
    return c


def bodice(point, normal):
    x, y, z = point
    nx, ny, nz = normal
    theta = math.atan2(y, x-.1)
    arc = theta*2.0
    row = math.floor((36.4-z)/.78)
    local_z = (36.4-z)/.78-row
    shift = .5*(row % 2)
    col = math.floor(arc/.72+shift)
    local_u = arc/.72+shift-col
    du = (local_u-.5)*2
    dv = local_z
    inside = du*du+(dv*1.2)**2
    edge = smooth((inside-.55)/.4)
    iri = .5+.5*math.sin(theta*2.3+z*.9+1.3*vnoise(x*2, y*2, z*2))
    base = mix(TEAL, (40, 88, 132), iri*.55)
    base = mix(base, (54, 130, 104), smooth(dv)*.35)
    c = mix(base, TEAL_DEEP, edge*.8)
    c = mix(c, (126, 204, 176), gauss(dv-.9, .1)*(1-edge)*.6)
    c = mix(c, TEAL_DEEP, .35*gauss(du, .12)*(1-edge))
    # A gold thread seam down the front.
    seam = gauss(y, .09)*smooth(nx*2)
    c = mix(c, GOLD, .85*seam)
    light = clamp(.66+.24*nz+.2*nx)
    return scale(c, .7+.45*light)


def face_paint(point, normal, m, c):
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    front = smooth((nx-.15)/.5)
    if m['ear'] > .3:
        return mix(c, ROSE, .5*front*smooth((m['ear']-.3)/.4))
    # Blush and nose tip.
    c = mix(c, ROSE, .55*gauss(math.hypot(ay-1.85, z-39.95), .72)*front)
    c = mix(c, ROSE, .45*gauss(math.hypot(y, z-40.45), .45)*smooth((x-2.9)/.3))
    # Violet eyeshadow sweeping up and out from the eyes, darker at the outer corner.
    ex, ez = ay-1.45, z-41.3
    shadow = gauss(math.hypot(ex/1.35, ez/.95), 1.)*front
    wing = gauss(math.hypot((ay-2.45)/.55, (z-41.6)/.35), 1.)
    c = mix(c, LILAC, .55*shadow)
    c = mix(c, EYESHADOW, .7*wing*smooth((nx+.2)/.5))
    # A soft line under each eye.
    c = mix(c, (150, 96, 150), .45*gauss(math.hypot((ay-1.5)/.75, (z-40.2)/.12), 1.)*front)
    # Mischievous smirk: a dark curve, lifted at the left corner, over a rosy lower lip.
    if -1.15 < y < 1.15 and z < 39.9 and nx > .2:
        mouth = 39.18+.3*(y/1.)**2+.1*y
        d = z-mouth
        line = gauss(d, .075)*smooth((1.1-ay)/.15)
        lip = gauss(d+.24, .12)*smooth((.72-ay)/.25)
        dimple = gauss(math.hypot(ay-1.08, d-.1), .1)
        c = mix(c, (220, 110, 138), .75*lip)
        c = mix(c, (60, 20, 48), .9*max(line, dimple))
    # Silver glitter freckles high on the cheekbones.
    fr = glitter(y*4.5, z*4.5, .5, 61, .4)*gauss(math.hypot(ay-1.9, z-40.5), .9)*front
    c = mix(c, (255, 255, 255), .95*fr)
    # Shadow under the chin onto the neck is handled by the baked light.
    return c


def island(index):
    return (index % 64)*16, (index//64)*16


FRACTIONS = {'head': ('head', 'hair', 'ear_L', 'ear_R'), 'ear': ('ear_L', 'ear_R'),
             'arm': ('arm_L', 'forearm_L', 'hand_L', 'arm_R', 'forearm_R', 'hand_R'),
             'hand': ('hand_L', 'hand_R'),
             'leg': ('thigh_L', 'shin_L', 'foot_L', 'thigh_R', 'shin_R', 'foot_R'),
             'foot': ('foot_L', 'foot_R'), 'torso': ('pelvis', 'spine', 'chest', 'neck')}


def connected_atlas(parts, pixels=False):
    """Bake continuous rest pigment into padded per-triangle 16-pixel islands."""
    from .rat import Part
    from .pixie_animation import IDS
    body = parts[0]
    normal = body.normals()
    groups = {k: {IDS[b] for b in v} for k, v in FRACTIONS.items()}
    fractions = [{k: sum(w for b, w in row if b in ids) for k, ids in groups.items()} for row in body.skin_weights]
    tris = list(body.triangles())
    assert len(tris) <= SKIN_ISLANDS, len(tris)
    # Spatial (Morton) island order: atlas neighbours are surface neighbours, so
    # mipmapped island borders blend similar colours instead of speckling.
    def morton(t):
        c = [sum(body.vertices[i][k] for i in t)/3 for k in range(3)]
        q = [max(0, min(1023, int((c[0]+20)*8))), max(0, min(1023, int((c[1]+20)*8))), max(0, min(1023, int((c[2]-10)*8)))]
        code = 0
        for bit in range(10):
            for k in range(3):
                code |= ((q[k] >> bit) & 1) << (3*bit+k)
        return code, t
    tris = [t for _, t in sorted(morton(t) for t in tris)]
    if pixels:
        buffer = bytearray(SIZE*SIZE*3)
        accessory_pixels(buffer)
        cache = {}
    result = Part('Connected_skin')
    result.skin_weights = []
    result.skin_topology = []
    steps = 6
    for index, tri in enumerate(tris):
        x0, y0 = island(index)
        if pixels:
            P = [body.vertices[i] for i in tri]
            N = [normal[i] for i in tri]
            F = [fractions[i] for i in tri]
            lattice = {}
            for i in range(steps+1):
                for j in range(steps+1-i):
                    b, c = i/steps, j/steps
                    a = 1-b-c
                    key = tuple(round(a*P[0][k]+b*P[1][k]+c*P[2][k], 5) for k in range(3))
                    frac = {k: round(a*F[0][k]+b*F[1][k]+c*F[2][k], 4) for k in groups}
                    ck = (key, tuple(frac.values()))
                    if ck not in cache:
                        nn = [a*N[0][k]+b*N[1][k]+c*N[2][k] for k in range(3)]
                        length = math.sqrt(sum(q*q for q in nn)) or 1
                        cache[ck] = skin_pigment(key, [q/length for q in nn], frac)
                    lattice[i, j] = cache[ck]
            for dy in range(16):
                for dx in range(16):
                    bi = clamp((dx-2)/12)*steps
                    cj = clamp((dy-2)/12)*steps
                    if bi+cj > steps:
                        k = steps/(bi+cj)
                        bi, cj = bi*k, cj*k
                    i, j = min(int(bi), steps-1), min(int(cj), steps-1)
                    fi, fj = bi-i, cj-j
                    if i+j >= steps:
                        i, j = (i-1, j) if i > 0 else (i, j-1)
                        fi, fj = bi-i, cj-j
                    if fi+fj <= 1:
                        c00, c10, c01 = lattice[i, j], lattice[i+1, j], lattice[i, j+1]
                        color = [c00[k]+(c10[k]-c00[k])*fi+(c01[k]-c00[k])*fj for k in range(3)]
                    else:
                        c11 = lattice[i+1, j+1] if (i+1, j+1) in lattice else lattice[i+1, j]
                        c10, c01 = lattice[i+1, j], lattice[i, j+1]
                        gi, gj = 1-fi, 1-fj
                        color = [c11[k]+(c01[k]-c11[k])*gi+(c10[k]-c11[k])*gj for k in range(3)]
                    o = ((y0+dy)*SIZE+x0+dx)*3
                    buffer[o:o+3] = bytes(max(0, min(255, round(q))) for q in color)
        base = len(result.vertices)
        for i, (dx, dy) in zip(tri, ((2, 2), (14, 2), (2, 14))):
            result.vertices.append(body.vertices[i])
            result.uv.append(((x0+dx)/SIZE, 1-(y0+dy)/SIZE))
            result.skin_weights.append(body.skin_weights[i])
            result.skin_topology.append(body.skin_topology[i])
        result.faces.append((base, base+1, base+2))
    if pixels:
        return encode_png(buffer, SIZE, SIZE)
    return [result]+parts[1:]
