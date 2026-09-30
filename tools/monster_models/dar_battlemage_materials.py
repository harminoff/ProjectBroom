"""Original dar battlemage paint: olive battle coat, oxblood lining, brass, embers.

Presentation-only diffuse art. Olive/brass echo Brogue's darMageColor glyph cue;
the ember eyes and hands paint the source description ("eyes glow like embers",
"hands radiate an occult heat"). Only pixels inside the ember key (ember_key()
and shaders/dar-battlemage-embers.fp) render fullbright: no world light, no
gameplay state and no change over time.
"""
import math
from .rat import TILES
from .dar_materials import encode_png, noise

SIZE = 1024
RECTS = {
    'coat': (8, 8, 504, 504),
    'skirt': (520, 8, 1016, 248),
    'collar': (520, 264, 760, 504),
    'armor': (776, 264, 1016, 504),
    'brass': (8, 520, 248, 760),
    'leather': (264, 520, 504, 760),
    'tome': (520, 520, 760, 760),
    'hair': (776, 520, 1016, 760),
    'bracer': (8, 776, 248, 1016),
    'lining': (264, 776, 504, 1016),
    'page': (520, 776, 632, 1016),
    'dark': (648, 776, 760, 1016),
    'ember': (776, 776, 888, 1016),
    'lid': (904, 776, 1016, 1016),
}
ROLES = tuple(RECTS)


def ember_key(rgb):
    """True where the shader renders fullbright (kept in sync with the .fp)."""
    r, g, b = (c/255 for c in rgb)
    return r > .86 and .3 < g < .86 and b < .34


def role(n):
    for prefix, r in (('coat', 'coat'), ('skirt', 'skirt'), ('collar', 'collar'),
                      ('pauldron', 'armor'), ('bracer_ring', 'brass'), ('bracer', 'bracer'),
                      ('belt_buckle', 'brass'), ('belt', 'leather'), ('boot', 'leather'),
                      ('tome_page', 'page'), ('tome_cover', 'tome'), ('hairring', 'brass'),
                      ('hair', 'hair'), ('detail_iris', 'ember'), ('detail_lid', 'lid'),
                      ('detail', 'dark')):
        if n.startswith(prefix):
            return r
    return 'brass'


def repack(parts):
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


def mul3(c, s):
    return tuple(x*s for x in c)


def add3(c, d):
    return tuple(x+d for x in c)


OLIVE = (82, 74, 36)
LINING = (112, 26, 22)
BRASS_DARK, BRASS_LIGHT = (112, 82, 30), (232, 194, 108)


def shade(name, u, v):
    n = noise(int(u*240), int(v*496))
    if name == 'coat':
        # u around (0 front), v waist (0) to shoulders (1).
        c = mul3(OLIVE, .72+.4*v)
        front = math.cos(math.tau*u)
        if front > .985:
            c = LINING                                   # oxblood placket
        elif front > .955:
            c = mix(BRASS_DARK, BRASS_LIGHT, .4)
        if .9 < front <= .955 and abs(((v*9) % 1)-.5) < .09:
            c = BRASS_LIGHT                              # studs
        # Quilted battle padding: painted diagonal stitch grooves.
        q = abs(((u*28+v*6) % 1)-.5)+abs(((u*28-v*6) % 1)-.5)
        if q < .12 and front <= .9:
            c = mul3(c, .72)
        if v < .05:
            c = mul3(c, .6)
        return clamp(add3(c, n*6))
    if name in ('skirt', 'collar'):
        # u across the panel; v: 0..0.5 inner lining, 0.5..1 outer face.
        if v < .5:
            return clamp(add3(mul3(LINING, .55+.55*(v/.5)), n*5))
        w = (v-.5)/.5
        c = mul3(OLIVE, .55+.5*w)
        if name == 'skirt':
            c = mul3(c, 1+.09*math.sin(math.tau*7*u))
        if u < .07 or u > .93 or w < .07 or (name == 'collar' and w > .86):
            c = mix(BRASS_DARK, BRASS_LIGHT, .55)
        elif name == 'skirt' and w < .12:
            c = LINING
        return clamp(add3(c, n*6))
    if name == 'armor':
        # Blackened steel plates, brass-rimmed, with a painted highlight pool.
        c = mix((22, 22, 24), (74, 70, 62), max(0, min(1, (v-.5)*2.2)))
        spot = math.exp(-((u-.3)/.12)**2-((v-.55)/.16)**2)
        c = mix(c, (150, 142, 124), .6*spot)
        if abs(v-.5) < .07:                      # plate edge (flattened equator)
            c = mix(BRASS_DARK, BRASS_LIGHT, .7)
        return clamp(add3(c, n*5))
    if name == 'brass':
        c = mix(BRASS_DARK, BRASS_LIGHT, .5+.5*math.sin(math.tau*(u*1.3+v*.6)))
        spot = math.exp(-((u-.3)/.14)**2-((v-.35)/.2)**2)
        return clamp(add3(mix(c, (236, 214, 160), .5*spot), n*6))
    if name == 'leather':
        return clamp(add3(mul3((58, 40, 32), .8+.3*math.sin(math.tau*v)), n*6))
    if name == 'bracer':
        c = mul3((66, 44, 34), .75+.35*math.sin(math.pi*v))
        if abs(((u*6) % 1)-.5) < .05:
            c = mul3(c, .6)
        return clamp(add3(c, n*6))
    if name == 'tome':
        c = mul3((92, 22, 26), .7+.35*math.sin(math.pi*u)*math.sin(math.pi*v))
        # Original tooled sigil: a square within a circle (not a real script).
        r = math.hypot(u-.5, v-.5)
        m = max(abs(u-.5), abs(v-.5))
        if abs(r-.26) < .025 or .14 < m < .17:
            c = BRASS_LIGHT
        return clamp(add3(c, n*5))
    if name == 'page':
        return clamp(add3((206, 190, 150), n*10+8*math.sin(v*140)))
    if name == 'hair':
        c = mul3((34, 22, 26), .8+.25*math.sin(math.tau*6*v)+.1*math.sin(u*70))
        c = mix(c, (90, 30, 28), .35*max(0, math.sin(math.tau*v)))
        return clamp(add3(c, n*6))
    if name == 'lining':
        return clamp(add3(LINING, n*6))
    if name == 'ember':
        r = math.hypot(u-.5, v-.5)*2
        return clamp(mix((255, 214, 80), (255, 128, 30), min(1, r)))
    return {'dark': (20, 14, 18), 'lid': (120, 104, 118)}[name]


def accessory_pixels():
    pixels = bytearray(SIZE*SIZE*3)
    for name, (x0, y0, x1, y1) in RECTS.items():
        for y in range(y0-8, y1+8):
            for x in range(x0-8, x1+8):
                u = max(0, min(1, (x-x0)/(x1-x0)))
                v = max(0, min(1, (y-y0)/(y1-y0)))
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3] = bytes(shade(name, u, v))
    return pixels


# Rest palm centre and fingertip centre per hand; set by the generator module.
HANDS = {}


def pigment(point, normal):
    """Continuous rest-position pigment for the fused anatomy (never part UVs)."""
    x, y, z = point
    form = .78+.2*max(-.5, normal[0]*.4+normal[1]*-.2+normal[2]*.7)
    base = (156, 148, 166)
    if z < 31:
        base = (42, 40, 46)                                   # dark trousers
    if z < 10.5:
        base = (46, 34, 28)                                   # boots
        if z > 9.3:
            base = (150, 112, 50)                             # brass boot band
    c = tuple(ch*form+2*math.sin(x*.9+y*.7+z*.6) for ch in base)
    if 10.5 <= z < 31:
        # Pressed trouser crease and knee wear: painted value, not geometry.
        crease = math.exp(-((abs(y)-4.3)/.55)**2)*max(0, min(1, x/1.5))
        knee = math.exp(-((z-15.5)/2.2)**2)*max(0, min(1, x/2))
        c = mix(c, (92, 86, 96), .45*crease+.3*knee)
    if z > 50:
        # Shaved scalp sides: cool stubble shadow below the swept crest.
        stub = max(0, min(1, (z-56.4)/1.5))*max(0, min(1, (abs(y)-1.6)))*max(0, min(1, (1.5-x)/1.5))
        c = mix(c, (86, 78, 98), .55*stub)
        # Soot around the eyes and a faint heat blush beneath them.
        soot = math.exp(-((z-55.85)/.75)**2-((abs(y)-1.65)/.95)**2)*max(0, min(1, (x-1)/1.5))
        c = mix(c, (52, 40, 50), .75*soot)
        heat = math.exp(-((z-54.75)/.45)**2-((abs(y)-1.7)/.7)**2)*max(0, min(1, (x-1.5)/1.2))
        c = mix(c, (150, 84, 70), .45*heat)
    # Hands radiate occult heat: charred skin crazed with ember veins, fully
    # ember toward the fingertips. Only these ember tones meet ember_key().
    for centre, tip in HANDS.values():
        d = math.dist(point, centre)
        if d < 4.8:
            span = sum((t-b)**2 for t, b in zip(tip, centre))
            along = max(0, min(1, sum((a-b)*(t-b) for a, b, t in zip(point, centre, tip))/span))
            wrist = max(0, min(1, (4.8-d)/1.2))
            vein = abs(math.sin(x*2.6+z*1.9)*math.sin(y*2.9-z*1.5+x))
            skin = mix(c, (64, 30, 26), wrist)
            if along > .45 or vein < .3:
                c = mix(skin, mix((255, 120, 34), (255, 206, 92), along), wrist)
            else:
                c = mix(skin, (150, 58, 30), .4*wrist)
    return c


def connected_atlas(parts, pixels=False):
    """Continuous pigment baked into per-triangle padded islands (dar layout)."""
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
