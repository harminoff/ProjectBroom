"""Original unicorn materials: a pearl-white coat painted with form, a gilded
spiral horn, gilded cloven-painted hooves, dark imploring eyes and a mane and
tail whose locks shade through pastel rainbow hues.

Brogue's prose says the mane and tail "shine with rainbow light" and the horn
glows; here those are paint only. The glyph's white is an identity cue. Under
the engine's flat bright light a white horse reads as a blob, so the coat is
painted with occlusion, lavender shadow, lit muscle masses and grey points.
The connected skin is painted from continuous rest-position coordinates, never
from source-part UV patches. Nothing here emits light or implies an effect.
"""
import colorsys
import math
from .rat import TILES
from .centaur_materials import hash3, vnoise, encode_png, mix, clamp

SIZE = 1024
ROLES = ('skin', 'horn', 'hoof', 'feather', 'mane_a', 'mane_b', 'mane_c', 'eye',
         'glint', 'lid', 'lash', 'coat', 'ear_inner')
RECTS = {n: (i % 4*256+8, i//4*256+8, i % 4*256+248, i//4*256+248) for i, n in enumerate(ROLES)}
MANE_PHASE = {'mane_a': .0, 'mane_b': .05, 'mane_c': .1}


def role(n):
    if n == 'horn':return 'horn'
    if n.startswith('hoof_'):return 'hoof'
    if n.startswith('feather_'):return 'feather'
    if n.startswith(('mane_lock', 'tail_lock')):
        return ('mane_a', 'mane_b', 'mane_c')[int(n.rsplit('lock', 1)[1]) % 3]
    if n.startswith('forelock_'):return ('mane_a', 'mane_b', 'mane_c')[int(n.split('_')[1]) % 3]
    if n.startswith('eye_glint'):return 'glint'
    if n.startswith('eye_'):return 'eye'
    if n.startswith('lid_'):return 'lid'
    if n.startswith('lash'):return 'lash'
    if n.startswith('ear_inner'):return 'ear_inner'
    if n.startswith('ear_'):return 'coat'
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


def noise2(u, v, scale): return vnoise(u*scale, v*scale, 7.3)


def hsv(h, s, v): return tuple(255*c for c in colorsys.hsv_to_rgb(h % 1, clamp(s), clamp(v)))


def shade(name, u, v):
    n = noise2(u, v, 23)+.5*noise2(u, v, 61)
    if name.startswith('mane'):
        # u runs root to tip, v round the lock: pearl roots shading through a
        # pastel rainbow, fine strand streaks, a sheen side and a shadow side.
        hue = MANE_PHASE[name]+.78*u+.04*noise2(u, v, 3)
        sat = .12+.5*clamp(u*1.4)**.8
        # Fine streaks, one broad sheen band shared by every lock, and a
        # shadowed inner face, so overlapping locks read as one hair mass.
        streak = math.sin(v*math.tau*14+u*3+2*noise2(u, v, 6))
        side = math.cos((v-.25)*math.tau)
        sheen = math.exp(-((u-.32)/.1)**2)*clamp(side)
        val = .86-.08*u+.035*streak+.1*side+.12*sheen
        c = hsv(hue, sat*(1-.25*clamp(side)), val)
        return tuple(x+5*n for x in c)
    if name == 'feather':
        streak = math.sin(v*math.tau*7+u*5+3*noise2(u, v, 5))
        c = mix((232, 230, 242), (206, 196, 232), clamp(u*1.2))
        return tuple(x+10*streak+5*n-14*(1-u)*clamp(-math.cos(v*math.tau)) for x in c)
    if name == 'horn':
        # Gilded ivory with the helical groove in step with the geometry.
        phase = 2*v*math.tau-u*4.25*math.tau
        ridge = math.cos(phase)
        groove = clamp(-ridge*1.4-.2)
        crest = clamp(ridge*1.6-.7)
        c = mix((238, 214, 150), (255, 246, 216), .35+.4*u)
        c = mix(c, (156, 112, 52), groove*.85)
        c = mix(c, (255, 252, 236), crest*.8)
        collar = clamp((.09-u)/.03)
        c = mix(c, (196, 150, 64), collar*.85)
        return tuple(x+6*n for x in c)
    if name == 'hoof':
        stri = math.sin(v*math.tau*22+2*noise2(u, v, 4))
        c = mix((230, 192, 104), (150, 106, 46), clamp((u-.35)*1.3))
        shine = math.exp(-((v-.12)/.07)**2)+math.exp(-((v-.88)/.07)**2)
        cleft = clamp(1-min(v, 1-v)/.022)*clamp((u-.3)*4)
        c = tuple(x+8*stri+6*n+40*shine*(1-u) for x in c)
        return mix(c, (70, 46, 22), cleft*.9)
    if name == 'eye':
        # Longitude u, latitude v: the outward pole is u=.29, v=.5.
        du, dv = (u-.29)*2.6, (v-.5)*1.9
        r = math.hypot(du, dv)
        iris = clamp((.62-r)/.08)
        rim = math.exp(-((r-.55)/.07)**2)
        pupil = clamp((.28-math.hypot(du*1.6, dv))/.06)
        c = mix((34, 24, 30), (72, 46, 74), iris)
        c = mix(c, (118, 92, 150), rim*.7*iris)
        c = mix(c, (12, 8, 16), pupil)
        return tuple(x+4*n for x in c)
    if name == 'glint':
        return (252, 252, 255)
    if name == 'lid':
        return tuple(x+6*n for x in (138, 128, 150))
    if name == 'lash':
        return tuple(x+4*n for x in (30, 24, 36))
    if name == 'coat':
        rim = clamp(abs(math.cos(v*math.tau))*1.2-.2)
        return tuple(x-26*rim-20*u+6*n for x in (240, 238, 246))
    if name == 'ear_inner':
        hairs = math.sin(v*math.tau*11+u*4)
        return tuple(x+8*hairs+6*n-30*(1-u) for x in (176, 150, 170))
    return (200, 200, 210)


def accessory_pixels():
    pixels = bytearray(SIZE*SIZE*3)
    for name, (x0, y0, x1, y1) in RECTS.items():
        for y in range(y0-8, y1+8):
            for x in range(x0-8, x1+8):
                u = clamp((x-x0)/(x1-x0))
                v = clamp((y-y0)/(y1-y0))
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3] = bytes(max(0, min(255, round(c))) for c in shade(name, u, v))
    return pixels


WHITE = (242, 243, 249)
SHADOW = (146, 150, 186)
DEEP = (96, 98, 136)
POINT = (170, 166, 190)
MUZZLE = (176, 160, 176)


def g(x, c, r): return math.exp(-((x-c)/r)**2)


def head_frame(point):
    from .unicorn_animation import POLL, D, F
    d = [a-b for a, b in zip(point, POLL)]
    return d[0]*D[0]+d[2]*D[2], d[0]*F[0]+d[2]*F[2], point[1]


def coat(point, normal):
    """Pearl-white coat with painted light, occlusion and anatomy."""
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    mottle = vnoise(x*.35, y*.35, z*.35)+.5*vnoise(x*.9+5, y*.9, z*.9)
    lam = clamp(.15*nx+.9*nz+.4)
    c = mix(SHADOW, WHITE, .08+.92*lam)
    # Barrel value gradient: bright back, lavender-grey lower flank.
    body = clamp((x+22)/3)*clamp((15-x)/3)*clamp((z-23)/3)
    flank = clamp((39-z)/11)*body
    c = mix(c, (122, 122, 170), .92*flank**1.1)
    # Lit anatomical masses: shoulder, forearm, haunch, gaskin, neck crest, jowl.
    lit = (g(x, 9.6, 3.2)*g(z, 33.5, 4.2)*clamp((ay-4.5)/2)
           + g(x, -15.5, 4.2)*g(z, 33.5, 4.6)*clamp((ay-4)/3)
           + g(x, 8.8, 1.8)*g(z, 21.5, 3.2)*clamp((ay-4.5)/1.5)
           + g(x, -11.5, 2.2)*g(z, 21.0, 3.4)*clamp((ay-5)/1.5)
           + g(x, -1, 7)*g(z, 34.5, 3)*clamp((ay-6.5)/2)*.6)
    # Painted occlusion: belly, inner legs, armpit, stifle fold, throat, groin.
    under = clamp(-nz*1.2)*clamp((31.5-z)/5)*body
    inner = clamp(-ny*math.copysign(1, y)*1.3)*clamp((30-z)/4)*clamp(1-ay/7.5)
    creases = (g(x-.2*(z-30), 5.4, 1.1)*clamp((z-25)/2)*clamp((37-z)/3)*clamp((ay-5)/1.5)      # triceps line
               + g(x, -9.2, 1.6)*g(z, 26.5, 2.4)*clamp((ay-5)/2)                               # flank/stifle fold
               + g(x+.2*(z-32), -20.6, .8)*clamp((37-z)/3)*clamp((z-24)/3)*clamp((ay-1.5)/2)*.9  # quarter groove
               + g(x, 6.0, 1.6)*g(z, 25.8, 2.0)*clamp((ay-3)/2)                                # armpit
               + g(x, 13.0, 1.8)*g(z, 30.0, 2.4)*clamp(1-ay/3.5)                              # chest groove
               + g(x, -20.4, 2.0)*g(z, 26.0, 3.5)*clamp(1-ay/3))                              # between the hind legs
    # The lower barrel turns away from the light: a broad soft gradient.
    lower = clamp((33.5-z)/7)*body*clamp((ay-2)/3)
    # Jugular groove down the lower neck side.
    neck = clamp((z-37)/3)*clamp((x-8)/3)*clamp((52-z)/3)
    jug = neck*g(x-.62*(z-44), 15.2, .8)*clamp((ay-2)/1.5)*.6
    chest = g(z, 36.5, 1.8)*g(x, 15.5, 2.2)*clamp(1-ay/5)
    # Shoulder and hip separation: the back edge of the shoulder blade and
    # the front edge of the haunch, down to elbow and stifle.
    sep = (g(x-.35*(z-30), 4.6, 1.3)*clamp((z-26)/2)*clamp((41-z)/2)*clamp((ay-3)/2)
           + g(x+.45*(z-30), -8.6, 1.4)*clamp((z-24)/2)*clamp((40-z)/2)*clamp((ay-3)/2))
    # Where the barrel meets the legs, and the upper leg tucked under it.
    joint = clamp((27.5-z)/2.5)*clamp((z-19)/3)*(1-clamp((ay-8)/1))
    dap = vnoise(x*.42+3, y*.42, z*.42)
    ring = clamp(1-abs(dap)/.12)*clamp((z-27)/4)*clamp((41-z)/3)*clamp((x+22)/3)*clamp((10-x)/4)*clamp((ay-4)/2)
    c = mix(c, SHADOW, clamp(.8*creases+.6*jug+.5*lower+.4*chest+.85*sep+.45*joint+.2*ring))
    c = mix(c, DEEP, clamp(.9*under+.7*inner))
    c = tuple(q+22*lit+5*mottle for q in c)
    # Soft grey points below knee and hock, deepening towards the fetlock.
    top = 17.0+1.0*vnoise(x*.7, y*.7, 3)
    points = clamp((top-z)/12)
    c = mix(c, (136, 132, 170), points*.85)
    c = mix(c, (104, 98, 132), clamp((7.5-z)/4)*.8)
    # Faint hair flow and a pearl sheen shifting between rose and blue.
    leg = clamp((26-z)/5)
    flow = math.sin(((z*2.9+ay*1.2)*(1-leg)+(x+ay)*3.1*leg)*2.6+4*vnoise(x*1.1, y*1.1, z*1.1))
    pearl = math.sin(nx*2.3+ny*1.7+nz*2.9+vnoise(x*.2, y*.2, z*.2)*3)
    c = (c[0]+1.6*flow+5*pearl, c[1]+1.6*flow, c[2]+1.6*flow-5*pearl+2)
    return c


def face(point, normal, c):
    """Head paint: dark eye rings, grey-lilac muzzle, nostrils, mouth and jaw shadow."""
    s, f, y = head_frame(point)
    if s < -3 or s > 15 or not -7 < f < 6 or point[2] < 38:
        return c
    ay = abs(y)
    head = clamp((s+2.5)/1.5)
    eye = math.exp(-((s-3.35)/1.35)**2-((f-1.2)/1.2)**2-((ay-2.7)/1.1)**2)
    c = mix(c, (118, 110, 138), eye*.72*head)
    muzzle = clamp((s-8.2)/2.2)
    c = mix(c, MUZZLE, muzzle*.85)
    pink = math.exp(-((s-11.4)/1.2)**2-((f-.6)/1.4)**2)
    c = mix(c, (196, 164, 182), pink*.35)
    nostril = math.exp(-((s-11.15)/.75)**2-((ay-1.35)/.42)**2-((f-1.1)/.9)**2)
    c = mix(c, (64, 50, 70), clamp(nostril*1.5)*.95)
    mouth = math.exp(-((s-12.25+.25*ay)/.22)**2)*clamp((1.2-f)/.6)*clamp((f+2.0)/.6)
    c = mix(c, (80, 66, 86), clamp(mouth)*.8)
    # Jaw and jowl edges, under-jaw occlusion, dished face shading.
    jowl = math.exp(-((math.hypot((s-3.0)/2.6, (f+1.6)/2.3)-1)/.14)**2)*clamp((ay-1.2)/1)*head
    under = clamp((-f-2.5)/1.5)*clamp((8-s)/2)*head
    dish = math.exp(-((s-6.5)/1.8)**2)*clamp((f-1.2)/.8)*clamp(1-ay/2)
    return mix(mix(c, SHADOW, clamp(.55*jowl+.25*dish)), DEEP, under*.55)


def pigment(point, normal):
    c = coat(point, normal)
    return face(point, normal, c)


def island(index):
    """16-pixel skin islands: the left half first, then the bottom-right quadrant."""
    if index < 8192:
        return (index % 64)*16, (index//64)*16
    k = index-8192
    return 1024+(k % 64)*16, 1024+(k//64)*16


def connected_atlas(parts, pixels=False):
    """Bake continuous rest-position pigment into padded per-triangle islands.

    Pigment is evaluated on a four-step barycentric lattice per triangle from
    interpolated rest positions and normals. Accessories keep the top-right
    quadrant; skin islands never enter it.
    """
    from .rat import Part
    body = parts[0]
    normal = body.normals()
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
            lattice = {}
            for i in range(steps+1):
                for j in range(steps+1-i):
                    b, c = i/steps, j/steps
                    a = 1-b-c
                    key = tuple(round(a*P[0][k]+b*P[1][k]+c*P[2][k], 5) for k in range(3))
                    nn = [a*N[0][k]+b*N[1][k]+c*N[2][k] for k in range(3)]
                    length = math.sqrt(sum(q*q for q in nn)) or 1
                    nkey = tuple(round(q/length, 4) for q in nn)
                    if (key, nkey) not in cache:
                        cache[key, nkey] = pigment(key, nkey)
                    lattice[i, j] = cache[key, nkey]
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
