"""Original centaur materials: a dun horse coat with dark points, a dorsal
stripe and a dark crest where it turns into tanned human skin at the waist, a
lacquered recurve bow with horn tips, a tooled leather quiver, arrows with
barred fletching, dark hooves, mane and tail.

The connected skin is painted from continuous rest-position coordinates and a
continuous per-vertex "human" fraction (the summed weight of the human bones),
never from source-part UV patches, so the join carries no colour seams. The
glyph's tan is an identity cue for the coat, not whole-body paint. Nothing here
emits light or implies a gameplay effect.
"""
import math
import struct
import zlib
from .rat import TILES

SIZE = 1024
ROLES = ('skin', 'bow', 'horn', 'cord', 'shaft', 'metal', 'feather', 'leather',
         'trim', 'hoof', 'tail', 'hair', 'dark', 'iris', 'white', 'beard')
RECTS = {n: (i % 4*256+8, i//4*256+8, i % 4*256+248, i//4*256+248) for i, n in enumerate(ROLES)}
HUMAN_BONES = ('waist', 'chest', 'neck', 'head', 'arm_L_upper', 'arm_L_lower', 'arm_L_end',
               'arm_R_upper', 'arm_R_lower', 'arm_R_end')


def role(n):
    if n.startswith(('bow_wrap', 'bow_string', 'hair_tie', 'bracer_lace')):return 'cord'
    if n == 'bow_grip':return 'cord'
    if n == 'bow_arrow_rest':return 'leather'
    if n.startswith('bow_horn') or n.endswith('_nock'):return 'horn'
    if n.startswith('bow'):return 'bow'
    if n.endswith('_shaft'):return 'shaft'
    if n.endswith('_head') or n == 'strap_buckle':return 'metal'
    if '_vane' in n:return 'feather'
    if n.startswith('quiver_band'):return 'trim'
    if n.startswith(('quiver', 'strap', 'bracer')):return 'leather'
    if n.startswith('hoof'):return 'hoof'
    if n.startswith(('feather_', 'tail_lock', 'mane_')):return 'tail'
    if n in ('hair_cap', 'hair_beard'):return 'beard'
    if n.startswith('hair'):return 'hair'
    if n.startswith(('eye_socket', 'eye_pupil')):return 'dark'
    if n.startswith('eye_white'):return 'white'
    if n.startswith('eye_iris'):return 'iris'
    return 'skin'


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


def noise2(u, v, scale): return vnoise(u*scale, v*scale, 7.3)
def mix(a, b, t): return tuple(x+(y-x)*t for x, y in zip(a, b))
def clamp(v, lo=0., hi=1.): return max(lo, min(hi, v))


def shade(name, u, v):
    n = noise2(u, v, 23)+.5*noise2(u, v, 61)
    if name == 'bow':
        # u runs along the limb: lacquered laminations, sinew back, painted bands.
        lam = math.sin(v*math.tau*6+2*noise2(u, v, 5))
        base = mix((78, 40, 26), (108, 60, 36), .5+.4*lam)
        band = max(0, math.sin(u*math.tau*9))**30
        c = tuple(x+10*n for x in base)
        return mix(c, (196, 160, 90), band*.8)
    if name == 'horn':
        streak = math.sin(v*math.tau*3+u*9+3*noise2(u, v, 4))
        return tuple(x+14*streak+8*n-20*u for x in (214, 200, 164))
    if name == 'cord':
        twist = math.sin((u*60+v*8)*math.tau)
        return tuple(x+16*twist+8*n for x in (178, 162, 124))
    if name == 'shaft':
        grain = math.sin(v*math.tau*5+u*40+2*noise2(u, v, 6))
        return tuple(x+10*grain+8*n for x in (186, 152, 104))
    if name == 'metal':
        rust = clamp(.5+noise2(u, v, 7)*2.2)
        return tuple(x+10*n for x in mix((120, 124, 130), (112, 78, 52), rust*.45))
    if name == 'feather':
        bar = math.sin(u*math.tau*5+.6*noise2(u, v, 5))
        vane = abs(v-.5)*2
        base = mix((222, 218, 206), (58, 48, 42), clamp(bar*2.2))
        base = mix(base, (168, 58, 40), clamp((u-.82)*8))
        return tuple(x*(1-.25*vane)+8*n for x in base)
    if name == 'leather':
        tool = max(0, 1-abs(math.sin(u*math.tau*8+math.sin(v*math.tau*4)*1.2))*10)
        stitch = (abs(v-.08) < .018 or abs(v-.92) < .018)*(math.sin(u*math.tau*70) > .2)
        base = mix((104, 68, 40), (126, 86, 52), clamp(.5+noise2(u, v, 5)*1.8))
        return tuple(x+10*n-22*tool+50*stitch for x in base)
    if name == 'trim':
        zig = abs(((u*12+v*1.5) % 1)-.5)*2
        stripe = clamp(1-abs(v-.5-.28*(zig-.5))*8)
        return tuple(x+8*n for x in mix((150, 60, 38), (210, 186, 130), stripe))
    if name == 'hoof':
        stri = math.sin(u*math.tau*26+2*noise2(u, v, 4))
        return tuple(x+7*stri+6*n+10*(1-v) for x in (52, 46, 44))
    if name == 'tail':
        streak = math.sin(v*math.tau*13+5*noise2(u, v, 5))
        return tuple(x+12*streak+8*n for x in (44, 34, 30))
    if name == 'hair':
        # Strand parts: v runs round the lock, so streaks follow each lock.
        streak = math.sin(v*math.tau*9+u*5+3*noise2(u, v, 6))
        return tuple(x+9*streak+7*n-10*u for x in (72, 50, 36))
    if name == 'beard':
        # Shells: u is longitude, so fine lines radiate from the pole
        # (the crown for the scalp, the chin point for the beard).
        fibre = math.sin(u*math.tau*46+4*noise2(u, v, 9))
        speck = noise2(u, v, 90)
        return tuple(x+10*fibre+14*speck+6*n for x in (70, 49, 35))
    if name == 'iris':
        r = abs(v-.5)*2
        return tuple(x-30*r+6*n for x in (110, 72, 38))
    if name == 'white':
        return tuple(x+5*n for x in (204, 194, 176))
    if name == 'dark':
        return tuple(x+4*n for x in (26, 20, 18))
    # Accessory skin (fingers, eyelids): matches the painted tan.
    return tuple(x+6*n-10*v for x in (150, 98, 68))


def accessory_pixels():
    pixels = bytearray(SIZE*SIZE*3)
    for name, (x0, y0, x1, y1) in RECTS.items():
        for y in range(y0-8, y1+8):
            for x in range(x0-8, x1+8):
                u = clamp((x-x0)/(x1-x0))
                v = clamp((y-y0)/(y1-y0))
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3] = bytes(max(0, min(255, round(c))) for c in shade(name, u, v))
    return pixels


def encode_png(pixels, width, height):
    def chunk(k, d): return struct.pack('>I', len(d))+k+d+struct.pack('>I', zlib.crc32(k+d) & 0xffffffff)
    raw = b''.join(b'\0'+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))+chunk(b'IEND', b''))


COAT = (150, 102, 56)
BELLY = (178, 140, 94)
POINTS = (34, 25, 21)
STRIPE = (46, 32, 23)
SKIN = (156, 100, 76)       # warm tan, distinct from the golden coat
SKIN_WARM = (136, 84, 64)


def coat(point, normal):
    """Dun horse coat: dorsal stripe, dark points, muscle form and hair flow."""
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    mottle = vnoise(x*.3, y*.3, z*.3)+.5*vnoise(x*.8+5, y*.8, z*.8)
    # Countershading: paler belly and inner legs, richer upper flanks.
    under = clamp(-nz*1.3)*clamp((34-z)/10)
    c = mix(COAT, BELLY, under*.7)
    upper = clamp(nz)*clamp((z-36)/8)
    c = mix(c, (128, 82, 42), upper*.55)
    # Muscle form: lit shoulder, barrel, haunch and croup masses; shadowed
    # triceps line, flank fold, elbow pit, chest groove and quarter groove.
    lit = (math.exp(-((x-10.5)/3.2)**2-((z-35.5)/4.5)**2)*clamp((ay-5)/3)*clamp((43-z)/3)
           + math.exp(-((x+18.5)/4.5)**2-((z-35)/5)**2)*clamp((ay-4)/4)
           + math.exp(-((x+2)/7)**2-((z-36)/3.5)**2)*clamp((ay-7)/3)*.6
           + math.exp(-((x+19)/5)**2-((z-41)/3)**2)*clamp(nz+.3)*.7)
    shadow = (math.exp(-((x-5.8+.25*(z-33))/1.6)**2)*clamp((z-26)/3)*clamp((40-z)/3)*clamp((ay-6)/2)*.45
              + math.exp(-((x+11.5)/2.2)**2-((z-27)/4)**2)*clamp((ay-6)/3)
              + math.exp(-((x-7.5)/1.8)**2-((z-27.5)/3)**2)*clamp((ay-4)/3)
              + math.exp(-((x-14)/2)**2-((z-29)/3)**2)*clamp(1-ay/4)
              + math.exp(-((x+23.2+.18*(z-32))/.9)**2)*clamp((38-z)/4)*clamp((z-24)/3)*clamp((ay-2)/2)*.8)
    ribs = max(0, math.sin(x*1.15+.4))**6*clamp((ay-8)/2)*clamp((z-27)/4)*clamp((37-z)/4)*clamp((x+10)/4)*clamp((10-x)/4)
    c = tuple(q*(.84+.16*clamp(nz+.5))+18*mottle+26*lit-34*shadow-10*ribs for q in c)
    # Hair flow: fine lines running back along the body and down the legs.
    leg = clamp((27-z)/5)
    body_q = z*2.9+ay*1.2
    leg_q = (x+ay)*3.1
    flow = math.sin((body_q*(1-leg)+leg_q*leg)*2.6+4*vnoise(x*1.1, y*1.1, z*1.1))
    flow *= .5+vnoise(x*.9+3, y*.9, z*.9)
    c = tuple(q+2.4*flow for q in c)
    # Dorsal (eel) stripe from the withers crest along the spine into the tail.
    along = clamp((9-x)/3)
    width = 1.45+.3*vnoise(x*.6, 0, z*.6)
    stripe = along*clamp((width-ay)/.5)*clamp((nz-.25)*3)
    c = mix(c, STRIPE, stripe*.9)
    # Darker dun shading over the upper withers, where the rider emerges.
    withers = clamp((z-42)/3)*clamp((x-6)/3)
    c = mix(c, (100, 66, 40), withers*.55)
    # Shoulder bar (dun marking) crossing the withers.
    bar = math.exp(-((x-9.6+.12*(z-40))/1.0)**2)*clamp((z-37)/4)*clamp((46-z)/2)*clamp(ay/3)
    c = mix(c, (92, 62, 38), bar*.55)
    # Dark points: stockings to above knee and hock, with a soft transition.
    fore = x > -4
    top = (19.0 if fore else 18.5)+1.2*vnoise(x*.8, y*.8, 3)
    points = clamp((top-z)/3.5)
    zebra = clamp((z-top)/1.5)*clamp((top+7-z)/3)*max(0, math.sin(z*1.9+x*.25))**3*clamp((ay-3)/2)
    c = mix(c, (84, 56, 36), zebra*.4)
    c = mix(c, POINTS, points*.94)
    coronet = math.exp(-((z-2.7)/.5)**2)
    return mix(c, (80, 64, 52), coronet*.5)


def skin(point, normal):
    """Tanned human skin with anatomical shading."""
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    mottle = vnoise(x*.45, y*.45, z*.45)+.4*vnoise(x*1.2+9, y*1.2, z*1.2)
    warm = clamp(.5+vnoise(x*.2+2, y*.2, z*.2)*1.6)
    c = mix(SKIN, SKIN_WARM, warm*.4)
    form = .82+.18*clamp(nz+.5)+.06*clamp(nx)
    c = tuple(q*form+14*mottle for q in c)
    creases = 0.
    front = clamp((nx-.2)/.5)
    side = clamp((ay-4.5)/1.5)*clamp(1-abs(nx)*1.2)
    # Pectoral underline and its soft shadow, sternum groove, abdominal
    # segments, oblique line, and ribs on the flanks under the arms.
    creases += front*math.exp(-((z-54.4+.08*ay**2)/.7)**2)*clamp((ay-.6)/1.2)*clamp((7-ay)/2)*1.2
    creases += front*math.exp(-((z-53.6+.08*ay**2)/1.4)**2)*clamp((ay-1)/1.2)*clamp((6.5-ay)/2)*.5
    creases += front*math.exp(-(y/.5)**2)*clamp((z-47)/2)*clamp((59-z)/2)*.7
    for zz in (51.8, 49.6):
        creases += front*math.exp(-((z-zz)/.45)**2)*clamp((3.2-ay)/1)*.55
    creases += front*math.exp(-((ay-4.2+.25*(z-48))/.55)**2)*clamp((z-44.5)/2)*clamp((52-z)/2)*.6
    creases += side*max(0, math.sin(z*2.3+ay*.6))**8*clamp((z-50)/1.5)*clamp((56.5-z)/1.5)*.8
    # Collarbones and pectoral tops catch light; eye sockets deepen, brows lit.
    collar = front*math.exp(-((z-60.6+.25*ay)/.6)**2)*clamp((ay-1)/1.5)*clamp((8-ay)/2)
    pec_lit = front*math.exp(-((z-57.4)/1.4)**2-((ay-3.8)/2.2)**2)
    socket = math.exp(-((ay-1.45)/1.0)**2-((z-70.3)/.8)**2)*clamp((x-16.5)/1.2)
    brow = math.exp(-((z-71.6)/.35)**2)*clamp((x-17.2)/.8)*clamp((3.2-ay)/1)
    lips = math.exp(-((z-67.45)/.35)**2)*clamp((x-18.2)/.8)*clamp(1-ay/1.6)
    c = tuple(q-22*creases+12*collar+12*pec_lit+10*brow for q in c)
    c = mix(c, (100, 62, 46), socket*.6)
    c = mix(c, (146, 82, 68), lips*.7)
    # Stubble shadow on cheeks and upper lip, blending into the beard.
    stubble = clamp((x-15)/1.5)*clamp((68.6-z)/1.2)*clamp((z-64)/1)*clamp((ay-.5)/1)
    return mix(c, (96, 70, 56), stubble*.45)


def pigment(point, normal, human):
    """Blend coat and skin by the continuous human-bone fraction and a hairline."""
    x, y, z = point
    nx, ny, nz = normal
    ragged = .12*vnoise(x*1.3, y*1.3, z*1.3)
    # Hair runs a little higher up the back than on the belly.
    back = clamp((-nx-.1)/.6)
    t = clamp((human-.5+ragged-.18*back)/.22)
    t = t*t*(3-2*t)
    c = mix(coat(point, normal), skin(point, normal), t)
    # A dark crest of longer hair where the coat meets the waist, heaviest over
    # the back, with fine streaks just below the hairline.
    crest = math.exp(-((t-.3)/.2)**2)*(.45+.55*back)
    c = mix(c, (60, 41, 28), crest*.6)
    fringe = math.exp(-((t-.35)/.22)**2)
    streak = max(0, math.sin(x*9.3+y*7.1+z*2.1+4*vnoise(x*2, y*2, z*2)))**4
    return tuple(q-24*fringe*streak for q in c)


def island(index):
    """16-pixel skin islands: the left half first, then the bottom-right quadrant."""
    if index < 8192:
        return (index % 64)*16, (index//64)*16
    k = index-8192
    return 1024+(k % 64)*16, 1024+(k//64)*16


def connected_atlas(parts, pixels=False):
    """Bake continuous rest-position pigment into padded per-triangle islands.

    Pigment is evaluated on a four-step barycentric lattice per triangle from
    interpolated rest positions, normals and human fractions. Accessories keep
    the top-right quadrant; skin islands never enter it.
    """
    from .rat import Part
    from .centaur_animation import IDS
    human_ids = {IDS[b] for b in HUMAN_BONES}
    body = parts[0]
    normal = body.normals()
    human = [sum(w for b, w in row if b in human_ids) for row in body.skin_weights]
    tris = list(body.triangles())
    assert len(tris) <= 12288
    if pixels:
        buffer = bytearray(2048*2048*3)
        accessory = accessory_pixels()
        for y in range(1024):
            buffer[(y*2048+1024)*3:(y*2048+2048)*3] = accessory[y*3072:(y+1)*3072]
        cache = {}
    result = Part('Connected_skin')
    result.skin_weights = []
    result.skin_topology = []
    steps = 4
    for index, tri in enumerate(tris):
        x0, y0 = island(index)
        if pixels:
            P = [body.vertices[i] for i in tri]
            N = [normal[i] for i in tri]
            H = [human[i] for i in tri]
            lattice = {}
            for i in range(steps+1):
                for j in range(steps+1-i):
                    b, c = i/steps, j/steps
                    a = 1-b-c
                    key = tuple(round(a*P[0][k]+b*P[1][k]+c*P[2][k], 5) for k in range(3))
                    h = round(a*H[0]+b*H[1]+c*H[2], 5)
                    if (key, h) not in cache:
                        nn = [a*N[0][k]+b*N[1][k]+c*N[2][k] for k in range(3)]
                        length = math.sqrt(sum(q*q for q in nn)) or 1
                        cache[key, h] = pigment(key, [q/length for q in nn], h)
                    lattice[i, j] = cache[key, h]
            for dy in range(16):
                for dx in range(16):
                    bi = clamp((dx-2)/12)*steps
                    cj = clamp((dy-2)/12)*steps
                    if bi+cj > steps:
                        scale = steps/(bi+cj)
                        bi, cj = bi*scale, cj*scale
                    i, j = min(int(bi), steps-1), min(int(cj), steps-1)
                    fi, fj = bi-i, cj-j
                    if i+j >= steps:
                        i, j = (i-1, j) if i > 0 else (i, j-1)
                        fi, fj = bi-i, cj-j
                    if fi+fj <= 1:
                        c00, c10, c01 = lattice[i, j], lattice[i+1, j], lattice[i, j+1]
                        color = [c00[k]+(c10[k]-c00[k])*fi+(c01[k]-c00[k])*fj for k in range(3)]
                    else:
                        c11, c10, c01 = lattice[i+1, j+1] if (i+1, j+1) in lattice else lattice[i+1, j], lattice[i+1, j], lattice[i, j+1]
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
    if pixels:return encode_png(buffer, 2048, 2048)
    for p in parts[1:]:p.uv = [(.5+u*.5, .5+v*.5) for u, v in p.uv]
    return [result]+parts[1:]
