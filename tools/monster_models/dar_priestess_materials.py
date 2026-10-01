"""Original dar priestess paint: teal vestments, cream stole, gold and bronze relics.

Presentation-only diffuse art. Colours are artistic interpretation; the teal
vestments echo Brogue's darPriestessColor glyph cue without implying any power.
Painted value contrast, fold occlusion and metal highlight pools stand in for
form that the engine's flat sector light would otherwise hide. No emission.
"""
import math
from .rat import TILES
from .dar_materials import encode_png, noise

SIZE = 1024
# Accessory quadrant rectangles (pixels, top-left origin), 16px gutters.
RECTS = {
    'robe': (8, 8, 504, 504),
    'stole': (520, 8, 632, 504),
    'mantle': (648, 8, 1016, 248),
    'sleeve': (648, 264, 1016, 504),
    'gold': (8, 520, 248, 760),
    'gem': (264, 520, 376, 760),
    'glass': (392, 520, 504, 760),
    'hair': (520, 520, 760, 760),
    'wood': (776, 520, 1016, 760),
    'steel': (8, 776, 248, 1016),
    'bronze': (264, 776, 504, 1016),
    'ivory': (520, 776, 632, 1016),
    'leather': (648, 776, 760, 1016),
    'dark': (776, 776, 832, 1016),
    'iris': (848, 776, 904, 1016),
    'lid': (920, 776, 960, 1016),
    'lip': (976, 776, 1016, 1016),
}
ROLES = tuple(RECTS)


def role(n):
    for prefix, r in (('robe', 'robe'), ('stole', 'stole'), ('mantle', 'mantle'), ('sleeve', 'sleeve'),
                      ('hairbrow', 'hair'), ('hair', 'hair'), ('staff_shaft', 'wood'),
                      ('sickle_blade', 'steel'), ('sickle_grip', 'leather'),
                      ('gem', 'gem'), ('glass', 'glass'), ('bell', 'bronze'), ('ivory', 'ivory'),
                      ('detail_lid', 'lid'), ('detail_lip', 'lip'), ('detail_iris', 'iris'),
                      ('detail', 'dark')):
        if n.startswith(prefix):
            return r
    return 'gold'


def repack(parts):
    """Map each accessory's source tile coordinates into its role rectangle."""
    for p in parts:
        rect = RECTS[role(p.name)]
        mapped = []
        for u, v in p.uv:
            x, y = u*1024, (1-v)*1024
            r = next(r for r in TILES.values() if r[0]-.01 <= x <= r[2]+.01 and r[1]-.01 <= y <= r[3]+.01)
            a, b = (x-r[0])/(r[2]-r[0]), (y-r[1])/(r[3]-r[1])
            mapped.append(((rect[0]+a*(rect[2]-rect[0]))/SIZE, 1-(rect[1]+b*(rect[3]-rect[1]))/SIZE))
        p.uv = mapped
    return parts


def clamp(c):
    return tuple(max(0, min(255, round(x))) for x in c)


def mix(a, b, t):
    return tuple(x+(y-x)*t for x, y in zip(a, b))


def emblem(u, v):
    """Original priestess sign: a crescent cradling a disc. Returns 0..1 ink."""
    r = math.hypot(u, v)
    disc = 1 if r < .23 else 0
    crescent = 1 if (.42 < math.hypot(u, v+.08) < .62 and v < .12) else 0
    return max(disc, crescent)


def shade(name, u, v):
    n = noise(int(u*240), int(v*496))
    if name == 'robe':
        # u: around (0 front), v: hem (0) to collar (1).
        teal = (28, 96, 100)
        folds = max(0, min(1, (.62-v)/.5))
        f = .055*math.sin(math.tau*9*u+.6)+.028*math.sin(math.tau*17*u)
        c = mul3(teal, 1+folds*f*7.5)
        c = mul3(c, .62+.5*min(1, v/.8))           # painted floor occlusion
        c = mul3(c, 1-.13*math.cos(math.tau*u)**2*(math.cos(math.tau*u) < 0))  # cooler back
        if abs(v-.62) < .012:
            c = mul3(c, .55)                          # girdle shadow
        if v < .075:                                  # gold hem band with diamonds
            band = (.012 < v < .03) or (.058 < v < .07)
            d = abs(((u*48) % 1)-.5)*2 + abs((v-.045)/.014)
            c = (176, 136, 52) if band or d < .55 else (16, 46, 50)
        return clamp(add3(c, n*6))
    if name == 'mantle':
        # u around, v bottom edge (0) to collar (1).
        base = (20, 70, 76)
        c = mul3(base, .82+.35*v+.06*math.sin(math.tau*12*u))
        if v < .09:
            c = (190, 150, 60) if v > .03 else (120, 88, 34)
        if v > .93:
            c = (182, 142, 56)
        return clamp(add3(c, n*5))
    if name == 'sleeve':
        # u along the arm (0 shoulder), v around.
        c = mul3((26, 90, 94), .72+.34*(1-u)+.08*math.sin(math.tau*5*v))
        if u > .86:
            c = (188, 148, 58) if u < .95 else (122, 90, 36)
        return clamp(add3(c, n*5))
    if name == 'stole':
        # u across the strip, v top (0) to bottom (1).
        c = (214, 204, 178)
        c = mul3(c, .9+.1*math.sin(math.pi*u))
        if u < .13 or u > .87:
            c = (186, 144, 56)
        elif .8 < v < .95:
            ink = emblem((u-.5)*2.4, (v-.875)/.06)
            if ink:
                c = (22, 96, 100)
        elif int(v*40) % 4 == 0 and abs(u-.5) < .12:
            c = (40, 110, 112)
        if v > .975:
            c = (150, 116, 44)
        return clamp(add3(c, n*4))
    if name == 'gold':
        c = mix((122, 86, 30), (236, 204, 118), .5+.5*math.sin(math.tau*(u*1.5+v*.5)))
        spot = math.exp(-((u-.3)/.12)**2-((v-.35)/.2)**2)
        return clamp(add3(mix(c, (255, 240, 190), .6*spot), n*6))
    if name == 'bronze':
        c = mix((92, 52, 24), (190, 126, 64), .5+.5*math.sin(math.tau*(u*1.2+v*.7)))
        return clamp(add3(c, n*6))
    if name == 'gem':
        c = mix((12, 80, 84), (92, 214, 204), max(0, 1-math.hypot(u-.35, v-.35)*1.6))
        return clamp(c)
    if name == 'glass':
        c = mix((30, 110, 112), (170, 236, 226), max(0, 1-math.hypot(u-.3, v-.5)*2))
        return clamp(c)
    if name == 'hair':
        # Silver-white strands; u along the strand, v around it.
        c = mul3((206, 208, 218), .8+.12*math.sin(math.tau*7*v)+.08*math.sin(u*90+v*11))
        c = mul3(c, .78+.22*min(1, u*3))
        return clamp(add3(c, n*8))
    if name == 'wood':
        # Ebony shaft with gold bands; u along the shaft (0 at foot).
        c = mul3((46, 32, 30), .85+.25*math.sin(math.tau*v))
        for band in (.08, .47, .56, .9):
            if abs(u-band) < .012:
                c = (194, 152, 62)
        return clamp(add3(c, n*5))
    if name == 'steel':
        # u across the blade: 0 is the inner cutting edge. A painted bright
        # bevel and a dark spine keep the crescent readable at distance.
        if u < .3:
            return clamp(mix((252, 253, 255), (214, 224, 230), u/.3))
        if u > .88:
            return clamp((58, 64, 72))
        c = mix((118, 130, 140), (196, 206, 214), .5+.5*math.sin(math.tau*v*1.5))
        return clamp(add3(c, n*4))
    if name == 'ivory':
        return clamp(add3(mul3((222, 210, 180), .8+.2*math.sin(math.tau*v)), n*6))
    if name == 'leather':
        return clamp(add3((58, 40, 34), n*6+6*math.sin(u*60)))
    return {'dark': (22, 18, 28), 'iris': (132, 206, 198), 'lid': (150, 144, 162),
            'lip': (122, 86, 108)}[name]


def mul3(c, s):
    return tuple(x*s for x in c)


def add3(c, d):
    return tuple(x+d for x in c)


def accessory_pixels():
    pixels = bytearray(SIZE*SIZE*3)
    for name, (x0, y0, x1, y1) in RECTS.items():
        for y in range(y0-8, y1+8):
            for x in range(x0-8, x1+8):
                u = max(0, min(1, (x-x0)/(x1-x0)))
                v = max(0, min(1, (y-y0)/(y1-y0)))
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3] = bytes(shade(name, u, v))
    return pixels


def pigment(point, normal):
    """Continuous rest-position pigment for the fused anatomy (never part UVs)."""
    x, y, z = point
    form = .78+.2*max(-.5, normal[0]*.4+normal[1]*-.2+normal[2]*.7)
    base = (160, 154, 172)
    if z < 26:
        base = (44, 50, 60)                           # dark hose under the robe
    if z < 3.4:
        base = (70, 56, 40)                           # soft leather slippers
    c = tuple(ch*form+2*math.sin(x*.9+y*.7+z*.6) for ch in base)
    # Painted eye-crease occlusion and cheek warmth (not sculpted light).
    crease = 10*math.exp(-((z-55.3)/.6)**2-((abs(y)-1.7)/.6)**2)*max(0, min(1, x/4))
    c = tuple(ch-crease for ch in c)
    if z > 50:
        cheek = 8*math.exp(-((z-54.6)/.8)**2-((abs(y)-1.9)/.7)**2)*max(0, min(1, x/3))
        c = (c[0]+cheek, c[1], c[2]+cheek*.4)
    # Original teal devotional mark: a vertical line and dot on the forehead.
    if x > 2.1 and z > 50:
        line = math.exp(-(y/.3)**2)*(56.9 < z < 58.9)
        dot = math.exp(-(y/.34)**2-((z-56.5)/.26)**2)
        ink = max(line, dot)
        c = mix(c, (24, 104, 108), min(1, ink*1.1))
    return c


def connected_atlas(parts, pixels=False):
    """Bake continuous rest-position pigment into per-triangle padded islands.

    Same layout as the dar family: skin triangles in the left half; the
    accessory atlas in the top-right quadrant.
    """
    from .rat import Part
    body = parts[0]
    normal = body.normals()
    tris = list(body.triangles())
    assert len(tris) < 8192
    if pixels:
        buffer = bytearray(2048*2048*3)
        accessory = accessory_pixels()
        for y in range(1024):
            buffer[(y*2048+1024)*3:(y*2048+2048)*3] = accessory[y*3072:(y+1)*3072]
        colors = [pigment(v, n) for v, n in zip(body.vertices, normal)]
    result = Part('Connected_skin')
    result.skin_weights = []
    result.skin_topology = []
    for index, tri in enumerate(tris):
        x0 = (index % 64)*16
        y0 = (index//64)*16
        if pixels:
            color = [colors[i] for i in tri]
            for dy in range(16):
                for dx in range(16):
                    b = (dx-2)/12
                    c = (dy-2)/12
                    a = 1-b-c
                    offset = ((y0+dy)*2048+x0+dx)*3
                    buffer[offset:offset+3] = bytes(max(0, min(255, round(a*color[0][k]+b*color[1][k]+c*color[2][k]))) for k in range(3))
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
