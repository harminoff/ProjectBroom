"""Original ogre shaman materials: aged olive skin with ash/ochre ritual paint,
gnarled wood, bleached relics, grey hair, fur-collared hide and sinew cord.

The skin is painted from continuous rest-position coordinates, never from the
source-part UV patches, so fused joints carry no colour seams. Paint is art
direction only; nothing here emits light or implies a gameplay effect.
"""
import math
import struct
import zlib
from .rat import TILES

SIZE = 1024
ROLES = ('skin', 'wood', 'cord', 'bone', 'tooth', 'hair', 'dark', 'iris',
         'feather', 'metal', 'mantle', 'fur', 'hide', 'leather')
RECTS = {n: (i % 4*256+8, i//4*256+8, i % 4*256+248, i//4*256+248) for i, n in enumerate(ROLES)}
ASH = (214, 208, 186)
OCHRE = (156, 58, 36)


def role(n):
    if n.startswith(('staff_binding', 'staff_lash', 'staff_cord', 'neck_cord', 'relic_braid_ring')):return 'cord'
    if n in ('mantle_tie', 'wrap_belt', 'wrap_pouch_cord', 'relic_hip_cord'):return 'cord'
    if n.startswith('staff'):return 'wood'
    if n.startswith(('relic_staff_orbit', 'relic_hip_orbits', 'eye_socket', 'eye_pupil', 'mouth')):return 'dark'
    if n.startswith('relic_staff_feather'):return 'feather'
    if n.startswith(('relic_earring', 'relic_beard')):return 'metal'
    if n.startswith('relic'):return 'bone'
    if n.startswith(('tusk', 'tooth', 'nail')):return 'tooth'
    if n.startswith('hair'):return 'hair'
    if n.startswith('eye_iris'):return 'iris'
    if n.startswith('mantle_fur'):return 'fur'
    if n.startswith('mantle'):return 'mantle'
    if n == 'wrap_pouch':return 'leather'
    if n.startswith('wrap'):return 'hide'
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


def noise2(u, v, scale):
    return vnoise(u*scale, v*scale, 7.3)


def mix(a, b, t): return tuple(x+(y-x)*t for x, y in zip(a, b))


def clamp(v, lo=0., hi=1.): return max(lo, min(hi, v))


def shade(name, u, v):
    n = noise2(u, v, 23)+.5*noise2(u, v, 61)
    if name == 'wood':
        # u runs along the shaft: long grain, bark ridges, dark knots, worn grip.
        grain = math.sin(v*math.tau*9+3*noise2(u, v, 7)*math.tau+u*4)
        ridge = max(0, math.sin(v*math.tau*5+u*31+2*noise2(u, v, 5)))**6
        base = mix((86, 70, 52), (122, 101, 74), .5+.35*grain)
        c = tuple(x-38*ridge+14*n for x in base)
        return c
    if name == 'cord':
        twist = math.sin((u*70+v*9)*math.tau)
        return tuple(x+14*twist+8*n for x in (138, 116, 82))
    if name == 'bone':
        crack = max(0, 1-abs(noise2(u, v, 9))*24)
        stain = clamp(.5+noise2(u, v, 4)*2)
        base = mix((222, 214, 190), (176, 160, 122), stain*.6)
        return tuple(x-60*crack+6*n for x in base)
    if name == 'tooth':
        return tuple(x-26*v+7*n for x in (214, 196, 150))
    if name == 'hair':
        streak = math.sin(v*math.tau*11+4*noise2(u, v, 6))
        return tuple(x+18*streak+10*n-22*u for x in (176, 174, 166))
    if name == 'iris':
        return tuple(x+6*n for x in (190, 170, 96))
    if name == 'feather':
        bar = math.sin(u*math.tau*6)
        vane = abs(v-.5)*2
        base = mix((36, 30, 28), (196, 190, 176), clamp(bar*2.5))
        return tuple(x*(1-.35*vane)+8*n for x in base)
    if name == 'metal':
        patina = clamp(.5+noise2(u, v, 8)*2.4)
        return tuple(x+8*n for x in mix((118, 88, 56), (88, 108, 90), patina*.7))
    if name == 'mantle':
        # Dark mossy hide: scars, stitched seam, ragged darker hem, fur yoke.
        base = mix((74, 70, 48), (52, 58, 40), clamp(.5+noise2(u, v, 5)*1.6))
        scratch = max(0, 1-abs(math.sin(u*43+v*19+3*noise2(u, v, 3)))*14)
        seam = max(0, 1-abs(u-.5)*60)*(math.sin(v*math.tau*28) > 0)
        hem = clamp((v-.8)/.16)
        yoke = clamp((.2-v)/.12)
        c = tuple(x+12*n-18*scratch-24*hem+30*seam for x in base)
        fur = tuple(x+22*math.sin(u*math.tau*55+6*noise2(u, v, 9))+10*n for x in (104, 96, 84))
        return mix(c, fur, yoke)
    if name == 'fur':
        tuft = math.sin(u*math.tau*40+v*math.tau*3+5*noise2(u, v, 8))
        return tuple(x+18*tuft+12*n for x in (112, 92, 68))
    if name == 'hide':
        stripe = math.sin(u*math.tau*7+2*noise2(u, v, 3))
        return tuple(x+12*n+9*stripe-12*v for x in (92, 70, 48))
    if name == 'leather':
        return tuple(x+12*n-10*v for x in (104, 72, 46))
    if name == 'dark':
        return tuple(x+4*n for x in (22, 16, 14))
    return tuple(x+8*n for x in (118, 124, 92))


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


def texture_bytes(): return encode_png(accessory_pixels(), SIZE, SIZE)


ARM = ((-1.5, 13.4, 48.2), (1.2, 17.6, 37.6), (9.2, 15.2, 32.6))


def along(point, a, b):
    d = [y-x for x, y in zip(a, b)]
    t = sum((p-x)*e for p, x, e in zip(point, a, d))/sum(e*e for e in d)
    return t


def pigment(point, normal):
    """Aged olive skin with painted ritual markings, from rest coordinates."""
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    mottle = vnoise(x*.35, y*.35, z*.35)+.5*vnoise(x*.9+11, y*.9, z*.9)
    belly = clamp((nx+.1)/.8)*math.exp(-((z-33)/8)**2)*clamp(1-ay/12)
    hump = clamp(-nx)*math.exp(-((z-46)/7)**2)
    color = mix((100, 108, 78), (128, 128, 94), belly*.8)
    color = mix(color, (80, 88, 62), hump*.75)
    # Warm weathered blotches break the green into an aged olive-brown hide.
    warm = clamp(.5+vnoise(x*.16+3, y*.16, z*.16)*1.8)
    color = mix(color, (112, 98, 70), warm*.45)
    # Form definition: shadowed undersides, lit upper planes.
    form = .8+.2*clamp(nz+.4)+.08*nx
    color = tuple(c*form+24*mottle for c in color)
    # Liver spots on crown, hump and hands.
    spot_zone = max(math.exp(-((z-63)/3)**2)*clamp(nz), hump, clamp((ay-13)/3)*clamp((36-z)/6))
    spots = clamp((vnoise(x*1.3, y*1.3, z*1.3)-.22)*6)*spot_zone
    color = mix(color, (84, 74, 48), spots*.65)
    creases = 0.
    face = clamp((x-8.5)/2)*clamp(1-ay/6.5)
    # Forehead lines, crow's feet, nose-root furrow, neck rings, belly fold.
    creases += face*math.exp(-((z-62.1)/1.6)**2)*max(0, math.sin(z*6.2))**8
    creases += math.exp(-((ay-4.3)/1.0)**2-((z-59)/1.4)**2)*clamp((x-9)/2)*max(0, math.sin(z*7+ay*3))**6
    creases += math.exp(-(y/.7)**2-((z-60.4)/.8)**2)*clamp((x-11)/1.5)
    creases += math.exp(-((z-53)/3)**2)*clamp((x-.5)/3)*clamp(1-ay/7)*max(0, math.sin(z*4.6+x))**6
    creases += math.exp(-((z-29.4)/.8)**2)*clamp((x+1)/4)*clamp(1-ay/10)*1.2
    creases += math.exp(-((z-23.5)/.9)**2)*clamp(1-abs(ay-6.5)/4)*clamp((x-2)/3)
    color = tuple(c-40*creases for c in color)
    # Sunken sockets, darker lips and ear hollows.
    socket = math.exp(-((ay-2.5)/1.6)**2-((z-59.2)/1.1)**2)*clamp((x-10)/2)
    lips = math.exp(-((z-55.2)/.7)**2)*clamp((x-11.5)/1.2)*clamp(1-ay/4)
    color = mix(color, (54, 48, 36), socket*.6)
    color = mix(color, (98, 70, 58), lips*.6)
    # Calloused soles, dark knuckles.
    color = mix(color, (82, 74, 56), clamp((1.2-z)/1.2))
    # Ritual paint: ash band across the eyes, ochre forehead dots,
    # a concentric ash-and-ochre eye sigil on the paunch, arm bands.
    ragged = .6*vnoise(x*2.1, y*2.1, z*2.1)
    band = clamp((1.05-abs(z-59.25)+ragged*.5)*3)*clamp((x-9.4)*1.5)*clamp((6.2-ay)*1.2)
    band *= 1-clamp((ay-2.5)**2/.9+((z-59.2)/.75)**2 < 1)
    dots = sum(math.exp(-((y/.55)**2+((z-zz)/.5)**2)*1.0) for zz in (61.9, 63.1, 64.2))*clamp((x-8)/2)
    front = clamp((nx-.35)/.4)
    # A weathered painted eye on the paunch: almond outline, ochre iris.
    half = 3.3*max(0, 1-(y/6.8)**2)
    dz = z-36.8
    edge = abs(abs(dz)-half) if abs(y) < 6.8 else 9
    sigil = front*clamp(1-edge/.45+ragged*.35)*clamp((6.9-abs(y))*2)
    iris = math.hypot(y, dz)
    ochre = front*clamp((2.15-iris)*1.6)*clamp((iris-.55)*3)
    sigil = max(sigil, front*clamp(1-abs(y)/.35)*clamp((dz+7.8)*.8)*clamp((-4.6-dz)*.8)*.8)
    arm_paint = 0.
    if ay > 9 and z > 28:
        a, b, c = [(p[0], math.copysign(p[1], y), p[2]) for p in ARM]
        t1, t2 = along(point, a, b), along(point, b, c)
        if 0 < t2 < 1:
            arm_paint = max(clamp(1-abs(t2-.42)/.07+ragged*.3), clamp(1-abs(t2-.66)/.05+ragged*.3))
        elif 0 < t1 < 1:
            arm_paint = clamp(1-abs(t1-.58)/.06+ragged*.3)
    ash = clamp(max(band, sigil, arm_paint))
    color = mix(color, ASH, ash*.88)
    color = mix(color, OCHRE, clamp(max(dots, ochre))*.9)
    return color


def connected_atlas(parts, pixels=False):
    """Bake continuous rest-position pigment into padded per-triangle islands.

    Pigment is evaluated on a four-step barycentric lattice per triangle from
    interpolated rest positions/normals, not merely at the cage vertices.
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
        cache = {}
    result = Part('Connected_skin')
    result.skin_weights = []
    result.skin_topology = []
    steps = 4
    for index, tri in enumerate(tris):
        x0 = (index % 64)*16
        y0 = (index//64)*16
        if pixels:
            P = [body.vertices[i] for i in tri]
            N = [normal[i] for i in tri]
            lattice = {}
            for i in range(steps+1):
                for j in range(steps+1-i):
                    b, c = i/steps, j/steps
                    a = 1-b-c
                    key = tuple(round(a*P[0][k]+b*P[1][k]+c*P[2][k], 5) for k in range(3))
                    if key not in cache:
                        nn = [a*N[0][k]+b*N[1][k]+c*N[2][k] for k in range(3)]
                        length = math.sqrt(sum(q*q for q in nn)) or 1
                        cache[key] = pigment(key, [q/length for q in nn])
                    lattice[i, j] = cache[key]
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
