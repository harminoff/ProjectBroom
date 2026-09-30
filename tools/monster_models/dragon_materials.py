"""Original dragon materials. No gameplay meaning; nothing emits light.

2048-square atlas. The connected skin is painted per triangle from continuous
rest positions, normals and bone-weight fractions (left half, 16-pixel islands
in spatial order), so body, neck, legs and tail carry no source-part seams.
Accessories use the right half: the wing membrane gets a large 496-pixel cell
shared by all six panels (u along the finger, v across), everything else a
256-pixel role cell.

Paint targets the engine's flat bright light: baked top light and occlusion,
painted overlapping scales (a 3D cell pattern with dark seams, per-scale tint
and a lit dome), pale ochre ventral plates on the throat, belly and tail
underside, a darker dorsal band, and thin ember-orange cracks between the
chest and flank scales (the furnace within, painted only). Deep crimson is a
deliberate departure from Brogue's green glyph so the creature separates from
grey walls; the green survives as the eyes. Wing membranes are lighter,
warmer and veined so they read against the dark body. Brogue's own light and
fire stay Brogue's; nothing here glows.
"""
import math

from .pixie_materials import hash3, vnoise, encode_png, mix, clamp, smooth, scale, gauss

SKIN = 'graphics/BRGDRGN.png'
SIZE = 2048
ROLES = ('eye', 'horn', 'claw', 'tooth', 'lid', 'spike', 'jaw', 'tongue', 'bone', 'flame', 'blade', 'flick')
RECTS = {n: (1536+i % 2*256+8, i//2*256+8, 1536+i % 2*256+248, i//2*256+248) for i, n in enumerate(ROLES)}
RECTS['membrane'] = (1032, 8, 1528, 504)
SKIN_ISLANDS = 8192
HEAD_DZ = 13.0   # head raised on a taller S-neck; head_paint works in design height

# ---------------------------------------------------------------- palette
# Brogue's dragonColor is (20, 80, 15)% green with green blood: an emerald / forest dragon, dark dorsal band,
# brighter flanks, pale yellow-ochre belly plates, ivory horns and claws, amber eyes. Only the fire is orange.
SCALE_LO = (10, 40, 20)
SCALE_MID = (34, 112, 46)
SCALE_HI = (150, 214, 96)
FLANK = (70, 170, 66)
DORSAL = (12, 46, 24)
DEEP = (6, 26, 14)
BLACKGREEN = (4, 16, 9)
SEAM = (6, 24, 13)
BELLY = (236, 208, 118)
BELLY_LO = (150, 118, 52)
IVORY = (238, 224, 182)
INK = (12, 6, 4)
EMBER = (255, 150, 56)
CRIMSON = SCALE_MID       # legacy names kept for the shared accessory shaders
CRIMSON_HI = SCALE_HI


def role(n):
    if n.startswith('eye_'): return 'eye'
    if n.startswith('lid_'): return 'lid'
    if n.startswith(('horn_', 'horn2_', 'horn3_', 'horn4_', 'horn5_')): return 'horn'
    if n.startswith(('tooth_', 'ltooth_')): return 'tooth'
    if n.startswith('claw_'): return 'claw'
    if n.startswith('spine_'): return 'spike'
    if n == 'tail_blade': return 'blade'
    if n == 'jaw': return 'jaw'
    if n == 'tongue': return 'tongue'
    if n.startswith(('wing_arm', 'wing_knob', 'finger_')): return 'bone'
    if n.startswith('membrane_'): return 'membrane'
    if n.startswith('flame_'): return 'flick' if len(n.split('_')[1]) == 2 and n.split('_')[1][1] != 's' else 'flame'
    return 'skin'


def repack(parts):
    for p in parts:
        r = role(p.name)
        if r == 'skin': continue
        x0, y0, x1, y1 = RECTS[r]
        p.uv = [(round((x0+u*(x1-x0))/SIZE, 7), round(1-(y0+v*(y1-y0))/SIZE, 7)) for u, v in p.uv]
    return parts


def local_uv(name, uv):
    x0, y0, x1, y1 = RECTS[role(name)]
    return ((uv[0]*SIZE-x0)/(x1-x0), ((1-uv[1])*SIZE-y0)/(y1-y0))


# ---------------------------------------------------------------- accessories
def ridge(u, freq): return .5+.5*math.sin(u*freq)


def shade(name, u, v):
    """u, v are the part's own tube/blob parameters (tube: u along, v around; blob: u around, v pole to pole)."""
    if name == 'eye':
        # Green source nod: bright yellow-green iris, hot at the centre, dark limbus, vertical slit pupil.
        if v > .6:
            lateral = math.sin(math.pi*v)*abs(math.sin(math.tau*u))
            k = (v-.6)/.4
            c = mix((150, 84, 6), (255, 214, 60), k**.7)
            c = mix(c, (255, 246, 170), .5*smooth((k-.7)/.25))
            c = scale(c, .9+.1*math.sin(u*math.tau*18))
            if v > .78 and lateral < .13: return INK
            c = mix(c, (52, 26, 2), smooth((.68-v)/.06))
            glint = gauss(math.hypot((u-.92)*3, v-.86), .04)
            return mix(c, (255, 255, 240), clamp(glint*1.3))
        return (30, 30, 10)
    if name == 'lid':
        rim = gauss(min(abs(u-.5), 1), .12)*smooth((v-.45)/.2)
        c = mix((40, 110, 44), (18, 60, 26), smooth((.8-v)/.4))
        c = mix(c, (150, 210, 96), .28*gauss(min(u, 1-u), .12)*smooth((v-.5)/.3))
        return mix(c, (4, 12, 6), .9*rim)
    if name == 'horn':
        r = ridge(u, 58)
        c = mix((28, 30, 14), (128, 110, 60), smooth((u-.02)/.2))
        c = mix(c, IVORY, smooth((u-.2)/.45))
        c = scale(c, .8+.2*r*(1-u*.5))
        top = .5+.5*math.cos(v*math.tau)
        return mix(c, (255, 250, 232), .35*top**6*smooth((u-.2)/.3))
    if name == 'claw':
        c = mix((50, 30, 26), (222, 210, 178), smooth((u-.1)/.6))
        top = .5+.5*math.cos(v*math.tau)
        return mix(c, (255, 250, 232), .4*top**5*smooth(u*2))
    if name == 'tooth':
        return mix((252, 248, 228), (196, 172, 130), smooth((u-.5)/.5)*.4)
    if name == 'spike':
        c = mix((20, 60, 30), (210, 196, 120), smooth((u-.05)/.7)**1.2)
        c = mix(c, (248, 236, 190), smooth((u-.8)/.2)*.7)
        return scale(c, .86+.14*ridge(u, 30))
    if name == 'blade':
        # Tail blade: dark burgundy shading to a pale, ridged edge.
        edge = abs(math.cos(u*math.pi*2))
        c = mix((14, 50, 26), (150, 200, 96), smooth(v)*.7+.3*edge)
        return mix(c, (240, 232, 180), .35*smooth((v-.85)/.15))
    if name == 'jaw':
        return jaw_paint(u, v)
    if name == 'tongue':
        c = mix((150, 34, 60), (236, 96, 112), .5+.5*math.sin(u*math.tau))
        return mix(c, (96, 12, 34), .6*gauss(min(abs(u-.25), 1)-.0, .07))
    if name == 'bone':
        # Wing bones: dark oxblood with a lit ridge on top and pale knuckle bands at the joints.
        top = .5+.5*math.cos(v*math.tau)
        c = mix((22, 70, 34), (104, 168, 76), .6*top**2)
        c = scale(c, .85+.15*ridge(u, 44))
        knob = gauss(min(u, 1-u), .06)
        return mix(c, (226, 214, 160), .5*knob)
    if name == 'flame':
        # Jet core streak / sparks: white-yellow near the root, gold, then an orange-red tip.
        c = mix((255, 255, 232), (255, 196, 54), smooth(v/.7))
        c = mix(c, (236, 72, 14), smooth((v-.78)/.22))
        return scale(c, .95+.08*math.sin(u*math.tau*3))
    if name == 'flick':
        # Flame tongue: white-yellow root, orange body, deep red flickering tip.
        c = mix((255, 246, 176), (255, 138, 28), smooth(v/.5))
        return mix(c, (156, 20, 10), smooth((v-.55)/.45)*.95)
    if name == 'membrane':
        return membrane_paint(u, v)
    return (128, 128, 128)


def jaw_paint(u, v):
    """Lower jaw (poles along X). u: 0 = +Y, .25 = up, .5 = -Y, .75 = down; v: back -> tip."""
    up = math.sin(u*math.tau)
    if up > .12:
        # Inner mouth: dark gum with a paler pink floor near the throat.
        c = mix((92, 12, 26), (206, 70, 78), (1-v)**1.3*.8)
        return mix(c, (52, 4, 14), smooth((v-.7)/.3)*.6)
    # Outer scales, pale ochre chin plates underneath.
    under = smooth((-up-.15)/.7)
    plate = 1-abs(math.sin(v*math.pi*7))
    c = mix(SCALE_MID, DEEP, .3)
    belly = mix(BELLY, BELLY_LO, (1-plate)**1.4)
    c = mix(c, belly, under)
    lip = gauss(abs(up), .16)*.55
    return mix(c, INK, lip*.8)


def membrane_paint(u, v):
    """Wing membrane panel: u root -> trailing edge, v finger a -> finger b. Light warm olive/jade, veined, lighter than the body."""
    edge_bone = gauss(min(v, 1-v), .06)
    c = mix((156, 176, 72), (206, 214, 108), smooth(u*1.1)*.55+.3*math.sin(math.pi*v))
    c = mix(c, (64, 98, 42), smooth((.22-u)/.22)*.8)
    # Capillary veins fan from the root, two families crossing each other.
    vein = gauss(math.sin(math.tau*(v*2.5+u*.6)), .09)*.6+gauss(math.sin(math.tau*(v*4.0-u*.5)), .06)*.35
    c = mix(c, (72, 108, 44), clamp(vein)*.7*smooth((u-.05)/.2))
    c = mix(c, (44, 78, 34), edge_bone*.75)
    c = mix(c, (30, 56, 26), smooth((u-.93)/.07)*.9)
    speck = vnoise(u*14, v*14, 3.3)
    return scale(c, .92+.16*speck)


def accessory_pixels(buffer):
    for name, (x0, y0, x1, y1) in RECTS.items():
        pad = 8
        for y in range(y0-pad, y1+pad):
            for x in range(x0-pad, x1+pad):
                if x < 1024 or x >= SIZE or y < 0 or y >= SIZE: continue
                u = clamp((x-x0)/(x1-x0)); v = clamp((y-y0)/(y1-y0))
                c = shade(name, u, v)
                o = (y*SIZE+x)*3
                buffer[o:o+3] = bytes(max(0, min(255, round(q))) for q in c)


# ---------------------------------------------------------------- skin
def worley(x, y, z):
    """Nearest and second-nearest jittered feature distances plus the nearest cell's random id."""
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x-ix, y-iy, z-iz
    ox, oy, oz = (0 if fx < .5 else 1), (0 if fy < .5 else 1), (0 if fz < .5 else 1)
    f1 = f2 = 9.
    cid = 0.
    for dx in (ox-1, ox):
        for dy in (oy-1, oy):
            for dz in (oz-1, oz):
                cx, cy, cz = ix+dx, iy+dy, iz+dz
                px = cx+.15+.7*hash3(cx, cy, cz)
                py = cy+.15+.7*hash3(cx+101, cy, cz+7)
                pz = cz+.15+.7*hash3(cx, cy+57, cz+13)
                d = math.sqrt((x-px)**2+(y-py)**2+(z-pz)**2)
                if d < f1:
                    f2 = f1; f1 = d; cid = hash3(cx+9, cy+3, cz+31)
                elif d < f2:
                    f2 = d
    return f1, f2, cid


AXIS = [((-11., 16.5, 5.6), (0, 0, 1)), ((-15.5, 18.5, 5.8), (0, 0, 1)), ((-21.5, 16.5, 6.5), (0, 0, 1)),
        ((-24.5, 11.5, 8.), (0, 0, 1)), ((-23.5, 5.5, 9.5), (0, 0, 1)), ((-20., 1.5, 11.5), (0, 0, 1)),
        ((-15., 0., 13.5), (0, 0, 1)), ((-10., 0., 14.), (0, 0, 1)), ((-2., 0., 14.5), (0, 0, 1)), ((5.5, 0., 16.), (0, 0, 1)),
        ((9.5, 0., 22.), (-.5, 0, .87)), ((12.5, 0., 35.), (-.85, 0, .53)), ((14.8, 0., 43.6), (-1, 0, .15))]
_ARC = [0.]
for _a, _b in zip(AXIS, AXIS[1:]):
    _ARC.append(_ARC[-1]+math.dist(_a[0], _b[0]))


def axis_coords(p):
    """Arclength s from the tail tip and the dorsal direction at the nearest point of the body centreline."""
    best = None
    for i, ((a, da), (b, db)) in enumerate(zip(AXIS, AXIS[1:])):
        d = tuple(q-r for q, r in zip(b, a))
        L = sum(q*q for q in d)
        t = clamp(sum((pq-aq)*dq for pq, aq, dq in zip(p, a, d))/L)
        c = tuple(aq+dq*t for aq, dq in zip(a, d))
        dist = math.dist(p, c)
        if best is None or dist < best[0]: best = (dist, i, t, da, db)
    dist, i, t, da, db = best
    dv = tuple(q+(r-q)*t for q, r in zip(da, db))
    n = math.sqrt(sum(q*q for q in dv))
    return _ARC[i]+(_ARC[i+1]-_ARC[i])*t, tuple(q/n for q in dv), dist


def scale_rows(s, c, length, width, tint_key):
    """Directional overlapping scales: rows run across the body, each scale's exposed edge (lit rim) faces the tail
    and its base is shadowed by the row before it. Returns (lit, rim, shadow, side, tint)."""
    r = math.floor(s/length)
    fs = s/length-r
    cc = c/width+.5*(r % 2)
    col = math.floor(cc)
    fc = cc-col
    t = clamp(fs+.3*(2*fc-1)**2*.5)
    lit = 1-smooth(t*1.05)
    rim = gauss(t-.1, .09)
    shadow = smooth((t-.86)/.12)
    side = smooth((abs(2*fc-1)-.78)/.2)
    return lit, rim, shadow, side, hash3(r, col, tint_key)


def skin_pigment(point, normal, m):
    """m: bone-weight fractions (head, neck, torso, fleg, hleg, paw, tail)."""
    x, y, z = point
    nx, ny, nz = normal
    limb = m['fleg']+m['hleg']
    body = m['torso']+m['neck']+m['tail']
    s0, dors, dist = axis_coords(point)
    dn = nx*dors[0]+ny*dors[1]+nz*dors[2]
    ang = math.atan2(ny, dn)          # 0 = dorsal, +-pi/2 = flank, pi = belly (around the body axis)
    dorsal_amount = smooth((math.cos(ang)-.5)/.4)
    light = clamp(.4+.34*nz+.26*nx)
    c = mix(SCALE_LO, SCALE_MID, light**.8)
    if m['head'] > .5:
        s, cc_, length, width = x, math.atan2(ny, nz)*2.2, .6, .62
    elif limb > .5:
        s, cc_, length, width = -z, math.atan2(ny*(1 if y >= 0 else -1), nx)*1.7, .7, .68
    else:
        s, cc_ = s0, ang*4.6
        length = (1.0+.7*dorsal_amount)*(1-.42*m['tail'])
        width = length*1.05
    lit, rim, shadow, side, tint = scale_rows(s, cc_, length, width, 7)
    # Brighter flanks, dark dorsal band, lit tops.
    flank = gauss(abs(ang)-1.3, .55)*smooth((body-.4)/.3)
    c = mix(c, FLANK, .6*flank)
    c = mix(c, SCALE_HI, .5*smooth((nz*.7+nx*.4-.45)/.35))
    c = mix(c, DORSAL, .72*dorsal_amount*smooth((body-.4)/.3))
    c = scale(c, (.56+.78*lit)*(.86+.28*tint))
    c = mix(c, SCALE_HI, .5*rim*(.45+.55*light))
    c = mix(c, SEAM, .8*shadow+.3*side)
    if body > .45:
        vent = smooth((-dn-.1)/.5)*smooth((body-.45)/.3)
        band = (s0/1.7) % 1.0
        plate = smooth(1-min(band, 1-band)*2/.2)
        pale = mix(BELLY, BELLY_LO, band**1.5*.9)
        pale = scale(pale, .8+.28*(1-plate*.6)+.1*(tint-.5))
        pale = mix(pale, SEAM, .6*gauss(min(band, 1-band), .07))
        c = mix(c, pale, vent)
    if limb > .4:
        c = mix(c, DEEP, .5*smooth((m['paw']-.25)/.5)*smooth((4.5-z)/3))
        c = mix(c, SCALE_HI, .14*smooth((nx-.3)/.4)*smooth((limb-.4)/.3))
        c = mix(c, BLACKGREEN, .45*smooth((3.2-z)/2.2))
    # Occlusion under the body and inside the legs.
    ao = smooth((-nz-.15)/.6)*smooth((16-z)/9)
    c = mix(c, BLACKGREEN, .5*ao*(1-.7*smooth((-dn-.2)/.4)*(body > .45)))
    if m['tail'] > .5:
        c = mix(c, DEEP, .5*smooth((-x-16)/9))
    if m['head'] > .5:
        c = head_paint(point, normal, m, c, light)
    return c


def head_paint(point, normal, m, c, light):
    x, y, z = point
    z -= HEAD_DZ     # the head is painted at its design height
    nx, ny, nz = normal
    ay = abs(y)
    # Lit crown and snout ridge; dark sockets, brow and mouth roof; pale yellow-green cheek plates.
    top = smooth((nz-.15)/.35)*smooth((x-14)/2)
    c = mix(c, DORSAL, .7*top)          # darker green on the top of the head so the face value reads
    ridge_hi = gauss(ay, .55)*smooth((nz-.35)/.4)*smooth((x-19)/2)
    c = mix(c, SCALE_HI, .22*ridge_hi)
    c = mix(c, (150, 196, 76), .3*gauss(math.hypot(ay-3.2, z-30.2), 1.6)*smooth(.5-abs(nz)*.3))
    socket = gauss(math.hypot(ay-4.2, (z-32.35)/1.3), 1.0)
    c = mix(c, DEEP, .7*socket)
    brow = gauss(math.hypot(x-19, z-34.3), 2.4)*gauss(ay-3, 1.1)
    c = mix(c, BLACKGREEN, .45*brow*smooth((nz+.1)/.4))
    roof = smooth((-nz-.35)/.35)*smooth((x-17)/2)*smooth((29.2-z)/1.2)
    c = mix(c, (80, 22, 26), .85*roof)
    lip = gauss(z-28.1, .28)*smooth((ay-.3)/.6)*smooth((x-19.5)/1.5)*smooth((28.6-z+.5)/.6)
    c = mix(c, INK, .6*lip*smooth((abs(ny)-.3)/.4))
    for sg in (1, -1):
        c = mix(c, INK, .95*gauss(math.hypot(x-26.4, y-sg*1.0, z-30.6), .6))
    c = mix(c, (176, 210, 96), .3*gauss(math.hypot(x-20.4, ay-3.6, z-28.5), 1.5)*smooth((ay-2.8)/.6))
    for sg in (1, -1):
        c = mix(c, (10, 10, 4), .8*gauss(math.hypot(x-16.2, y-sg*2.8, z-34.5), 1.3))
    return c


def island(index):
    return (index % 64)*16, (index//64)*16


def bake_atlas(parts, ids, fraction_groups, pigment, accessories, pixels, origin=(-40, -40, -2)):
    from .imp_materials import bake_atlas as generic
    return generic(parts, ids, fraction_groups, pigment, accessories, pixels, origin)


FRACTIONS = {'head': ('head',), 'neck': ('neck_0', 'neck_1'), 'torso': ('pelvis', 'spine', 'chest'),
             'fleg': ('arm_L', 'fore_L', 'paw_L', 'arm_R', 'fore_R', 'paw_R'),
             'hleg': ('thigh_L', 'shin_L', 'foot_L', 'toes_L', 'thigh_R', 'shin_R', 'foot_R', 'toes_R'),
             'paw': ('paw_L', 'paw_R', 'toes_L', 'toes_R'),
             'tail': ('tail_0', 'tail_1', 'tail_2', 'tail_3', 'tail_4', 'tail_5')}


def connected_atlas(parts, pixels=False):
    from .dragon_animation import IDS
    return bake_atlas(parts, IDS, FRACTIONS, skin_pigment, accessory_pixels, pixels)
