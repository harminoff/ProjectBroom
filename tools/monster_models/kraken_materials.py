"""Original kraken paint: rust-maroon cephalopod skin for the engine's flat light.

Brogue's kraken glyph colour (100, 55, 55) is an identity cue, not literal body
paint and not a power. The dorsal skin is a deep maroon-to-rust mottle with
dark chromatophore flecks and pale reticulation; every arm and tentacle has a
continuous pale peach sucker (oral) band bordered by a dark margin line. Value
structure is painted, not lit: top light, underside and junction occlusion,
transverse arm wrinkles, warty papillae with shadowed rims, dark eye rings and
wet specular pools. Eyes (gold with a horizontal bar pupil), the parrot beak
and the sucker cups live in the accessory quadrant. Nothing emits light.

The connected skin is painted per triangle from rest positions and a limb
centreline index, so pigment runs continuously through fused junctions. The
atlas helpers are reused read-only by the tentacle horror.
"""
import math
from .centaur_materials import vnoise, encode_png, mix, clamp, hash3
from .rat import Part
from . import kraken_animation as shape

SKIN = shape.SKIN
TAU = math.tau


def unit(v):
    n = math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])
    return (v[0]/n, v[1]/n, v[2]/n) if n > 1e-12 else (0., 0., 1.)


def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def smooth(t): t = clamp(t); return t*t*(3-2*t)
def scale(c, k): return tuple(x*k for x in c)


KEY = unit((.35, .30, .88))
EYE = unit((.75, .45, .35))
HALF = unit(tuple(a+b for a, b in zip(KEY, EYE)))


# ------------------------------------------------------------------ limb index
class LimbIndex:
    """Nearest swept-limb row for a rest-position point (spatial hash)."""

    def __init__(self, limbs, cell=4.):
        self.cell = cell
        self.grid = {}
        self.limbs = limbs
        for index, limb in enumerate(limbs):
            for row in limb.rows:
                key = tuple(int(math.floor(c/cell)) for c in row['c'])
                self.grid.setdefault(key, []).append((index, row))
        self.big = [(i, row) for i, limb in enumerate(limbs) for row in limb.rows if row['r'] > cell*.9]

    def query(self, p):
        key = tuple(int(math.floor(c/self.cell)) for c in p)
        best = None
        candidates = list(self.big)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    candidates += self.grid.get((key[0]+dx, key[1]+dy, key[2]+dz), ())
        for index, row in candidates:
            d = (p[0]-row['c'][0], p[1]-row['c'][1], p[2]-row['c'][2])
            along = dot(d, row['T'])
            perp = (d[0]-along*row['T'][0], d[1]-along*row['T'][1], d[2]-along*row['T'][2])
            radial = math.sqrt(dot(perp, perp))
            sdf = radial-row['r']+abs(along)*.6
            if best is None or sdf < best[0]:
                best = (sdf, index, row, perp, radial)
        if best is None:
            return None
        sdf, index, row, perp, radial = best
        dirn = unit(perp) if radial > 1e-6 else row['V']
        return dict(sdf=sdf, limb=self.limbs[index], row=row, cosv=dot(dirn, row['V']),
                    sinl=dot(dirn, row['L']), ratio=radial/max(.05, row['r']))


# ------------------------------------------------------------------ textures
def worley(p, size, salt):
    """Distance to the nearest jittered feature (in cell units) and its id hash."""
    x, y, z = p[0]/size, p[1]/size, p[2]/size
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    best = (9., 0.)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                cx, cy, cz = ix+dx, iy+dy, iz+dz
                fx = cx+hash3(cx, cy, cz+salt)
                fy = cy+hash3(cx+salt, cy, cz)
                fz = cz+hash3(cx, cy+salt, cz)
                d = math.sqrt((x-fx)**2+(y-fy)**2+(z-fz)**2)
                if d < best[0]:
                    best = (d, hash3(cx+7, cy+salt, cz+3))
    return best


def finish(color, n, occlusion=1., gloss=1., top=.3):
    """Painted top light, occlusion and wet specular for flat engine light."""
    light = .92*(1-top)+top*clamp(.5+.6*n[2])+.10*dot(n, KEY)
    c = scale(color, light*occlusion)
    h = max(0., dot(n, HALF))
    spec = gloss*(.55*h**34+.10*h**6)
    return tuple(x+(255-x)*spec for x in c)


DEEP = (44, 10, 14)
RED = (104, 27, 25)
RUST = (168, 64, 40)
PALE = (236, 184, 158)
PALE_SH = (190, 124, 106)
EDGE = (38, 9, 12)
EYE_RING = (32, 8, 10)

INDEX = None


def index():
    global INDEX
    if INDEX is None:
        INDEX = LimbIndex([shape.MANTLE]+shape.LIMBS)
    return INDEX


def head_sdf(p):
    c, r = shape.HEAD_C, shape.HEAD_R
    q = ((p[0]-c[0])/r[0], (p[1]-c[1])/r[1], (p[2]-c[2])/r[2])
    return (math.sqrt(dot(q, q))-1)*min(r)


def dorsal(p, n, fine=1.):
    m = vnoise(p[0]*.21, p[1]*.21, p[2]*.21)+.55*vnoise(p[0]*.6, p[1]*.6, p[2]*.6)
    base = mix(DEEP, RED, clamp(.5+1.3*m))
    # Broad dark chromatophore blotches break up large flat surfaces.
    blotch = vnoise(p[0]*.13+5, p[1]*.13, p[2]*.13)
    base = mix(base, DEEP, .6*smooth((blotch-.06)/.18))
    net = abs(vnoise(p[0]*.45+3, p[1]*.45, p[2]*.45))
    base = mix(base, RUST, .55*smooth((.05-net)/.05))
    fleck, h = worley(p, .9*fine, 11)
    if fleck < .24 and h > .35:
        base = mix(base, DEEP, .75*smooth((.24-fleck)/.12))
    return base


def warts(p, n, color, size=1.7, height=.55):
    d, h = worley(p, size, 29)
    if d < .36 and h > .25:
        k = smooth((.36-d)/.2)
        up = clamp(.5+.8*n[2])
        return mix(color, mix(RUST, PALE, .35) if up > .4 else EDGE, height*k)
    return color


def limb_paint(p, n, q):
    limb, row = q['limb'], q['row']
    cosv = q['cosv']
    ventral = smooth((cosv-.12)/.42)
    arc, s = row['arc'], row['s']
    back = dorsal(p, n)
    ring = .5+.5*math.cos(arc*TAU/1.15)
    back = scale(back, 1-.18*ring**6*(1-ventral))
    back = mix(back, DEEP, .35*smooth((s-.72)/.25))
    belly = mix(PALE_SH, PALE, clamp(.55+.45*cosv+.4*vnoise(p[0]*.8, p[1]*.8, p[2]*.8)))
    # Painted pits between the sucker cups keep the oral band from reading flat.
    belly = scale(belly, 1-.16*(.5+.5*math.cos(arc*TAU/(1.2*max(.5, row['r'])))))
    c = mix(back, belly, ventral)
    edge = math.exp(-((cosv-.10)/.075)**2)
    c = mix(c, EDGE, .55*edge)
    occ = 1-.42*(1-smooth((arc-limb.exit)/3.5))
    if limb.name == 'mantle':
        return None
    return c, occ


def mantle_paint(p, n, q):
    cosv = q['cosv']
    c = dorsal(p, n, 1.3)
    # Longitudinal dark streaks and a paler front belly on the mantle.
    streak = abs(math.sin(math.atan2(q['sinl'], cosv)*4.5+vnoise(p[0]*.3, p[1]*.3, p[2]*.3)*3))
    c = scale(c, 1-.22*smooth((.25-streak)/.25))
    c = mix(c, mix(PALE_SH, RUST, .55), .35*smooth((cosv-.45)/.5))
    c = warts(p, n, c, 1.9, .85)
    tip = q['row']['s']
    c = mix(c, DEEP, .3*smooth((tip-.8)/.2))
    return c


def head_paint(p, n):
    c = dorsal(p, n, 1.1)
    c = warts(p, n, c, 1.6, .6)
    under = smooth((-n[2]-.2)/.5)
    c = mix(c, PALE_SH, .5*under*smooth((p[0]-4)/6))
    for side in (1, -1):
        e = shape.eye_centre(side)
        d = math.sqrt((p[0]-e[0])**2+(p[1]-e[1])**2+(p[2]-e[2])**2)
        c = mix(c, EYE_RING, .85*smooth((6.4-d)/1.8))
        c = mix(c, RUST, .35*math.exp(-((d-6.9)/.45)**2))
    return c


def pigment(p, n):
    q = index().query(p)
    hs = head_sdf(p)
    occ = 1.
    vent = 0.
    if q is not None and q['limb'].name != 'mantle' and q['sdf'] < hs+.4:
        c, occ = limb_paint(p, n, q)
        vent = smooth((q['cosv']-.12)/.42)
        if q['sdf'] > hs-.8:  # blend into the head near the crown
            w = smooth((q['sdf']-hs+.8)/1.2)
            c = mix(c, head_paint(p, n), w*.6)
            occ *= 1-.25*w
    elif q is not None and q['limb'].name == 'mantle' and q['sdf'] < hs+.6:
        c = mantle_paint(p, n, q)
        occ = 1-.35*smooth((q['row']['arc']-6)/-4)
    else:
        c = head_paint(p, n)
        # Buccal crown and lips: paler, fleshy, occluded towards the beak.
        cr = shape.crown(2.4, 0.)
        d = math.sqrt((p[0]-cr[0])**2+(p[1]-cr[1])**2+(p[2]-cr[2])**2)
        c = mix(c, PALE_SH, .6*smooth((6.5-d)/2.5))
        occ = 1-.45*smooth((3.2-d)/2)
    # Underside occlusion spares the pale sucker bands: the gameplay camera
    # looks up at raised arms, and their suckers must still read.
    under = smooth((-n[2]-.35)/.5)
    occ *= 1-.30*under*(1-.8*vent)
    return finish(c, n, occ, top=.3*(1-.6*vent))


# ------------------------------------------------------------------ accessories
def strip_color(y, u):
    if abs(y-600) <= 30:   # sucker cup: dark pit, pink inner lip, cream rim, pale skirt
        keys = ((0, (58, 14, 20)), (.3, (120, 40, 44)), (.52, (206, 122, 118)), (.78, (246, 222, 198)), (1, (222, 164, 144)))
    elif abs(y-680) <= 30 or abs(y-760) <= 30:   # beak: amber base to glossy black hook
        keys = ((0, (138, 88, 42)), (.35, (96, 56, 28)), (.6, (46, 28, 18)), (1, (18, 13, 11)))
    else:
        return None
    for (u0, a), (u1, b) in zip(keys, keys[1:]):
        if u <= u1:
            return mix(a, b, (u-u0)/(u1-u0))
    return keys[-1][1]


def eye_color(dx, dy):
    r = math.hypot(dx, dy)
    if r > 1:
        return (22, 10, 8)
    if r > .93:
        return (38, 22, 10)
    angle = math.atan2(dy, dx)
    fiber = .82+.18*math.sin(angle*46+3*vnoise(dx*6, dy*6, 1.3))
    iris = mix((246, 196, 70), (170, 98, 20), smooth((r-.35)/.55))
    c = scale(iris, fiber)
    if (abs(dx)/.58)**4+(abs(dy)/.17)**4 < 1:
        c = (8, 6, 6)
    elif (abs(dx)/.64)**4+(abs(dy)/.23)**4 < 1:
        c = mix(c, (60, 30, 8), .6)
    if dy < -.5:
        c = scale(c, 1-.45*smooth((-dy-.5)/.35))
    for gx, gy, gr in ((-.36, -.42, .11), (.3, .5, .05)):
        if math.hypot(dx-gx, dy-gy) < gr:
            c = (255, 250, 238)
    return c


def accessory_pixels(size=1024):
    pixels = bytearray(size*size*3)
    for y in range(size):
        for x in range(size):
            c = None
            if x < 512 and y < 512:
                c = eye_color((x-256)/238, (y-256)/238)
            else:
                c = strip_color(y, clamp((x/1024-.02)/.96))
            if c is not None:
                o = (y*size+x)*3
                pixels[o:o+3] = bytes(max(0, min(255, round(v))) for v in c)
    return pixels


# ------------------------------------------------------------------ atlas
def island(index):
    """16-pixel skin islands: the left half first, then the bottom-right quadrant."""
    if index < 8192:
        return (index % 64)*16, (index//64)*16
    k = index-8192
    return 1024+(k % 64)*16, 1024+(k//64)*16


def connected_atlas(parts, pixels=False, pigment_fn=None, accessory_fn=None, steps=4):
    """Bake continuous rest-position pigment into padded per-triangle islands.

    Accessories keep the top-right quadrant; skin islands never enter it."""
    pigment_fn = pigment_fn or pigment
    accessory_fn = accessory_fn or accessory_pixels
    body = parts[0]
    normal = body.normals()
    tris = list(body.triangles())
    assert len(tris) <= 12288, len(tris)
    if pixels:
        buffer = bytearray(2048*2048*3)
        accessory = accessory_fn()
        for y in range(1024):
            buffer[(y*2048+1024)*3:(y*2048+2048)*3] = accessory[y*3072:(y+1)*3072]
        cache = {}
    result = Part('Connected_skin')
    result.skin_weights = []
    result.skin_topology = []
    for index_, tri in enumerate(tris):
        x0, y0 = island(index_)
        if pixels:
            P = [body.vertices[i] for i in tri]
            N = [normal[i] for i in tri]
            lattice = {}
            for i in range(steps+1):
                for j in range(steps+1-i):
                    b, c = i/steps, j/steps
                    a = 1-b-c
                    key = tuple(round(a*P[0][k]+b*P[1][k]+c*P[2][k], 5) for k in range(3))
                    nn = [a*N[0][k]+b*N[1][k]+c*N[2][k] for k in range(3)]
                    nkey = tuple(round(q, 4) for q in unit(nn))
                    if (key, nkey) not in cache:
                        cache[key, nkey] = pigment_fn(key, nkey)
                    lattice[i, j] = cache[key, nkey]
            for dy in range(16):
                for dx in range(16):
                    bi = clamp((dx-2)/12)*steps
                    cj = clamp((dy-2)/12)*steps
                    if bi+cj > steps:
                        k_ = steps/(bi+cj)
                        bi, cj = bi*k_, cj*k_
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
                    offset = ((y0+dy)*2048+x0+dx)*3
                    buffer[offset:offset+3] = bytes(max(0, min(255, round(q))) for q in color)
        base = len(result.vertices)
        for i, (dx, dy) in zip(tri, ((2, 2), (14, 2), (2, 14))):
            result.vertices.append(body.vertices[i])
            result.uv.append(((x0+dx)/2048, 1-(y0+dy)/2048))
            result.skin_weights.append(body.skin_weights[i])
            result.skin_topology.append(body.skin_topology[i])
        result.faces.append((base, base+1, base+2))
    if pixels:
        return encode_png(buffer, 2048, 2048)
    for p in parts[1:]:
        p.uv = [(.5+u*.5, .5+v*.5) for u, v in p.uv]
    return [result]+parts[1:]
