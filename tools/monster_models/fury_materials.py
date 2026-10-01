"""Original fury materials. No gameplay meaning; nothing emits light.

2048-square atlas. The connected skin (left half) is painted per triangle from
continuous rest positions, normals and bone-weight fractions by the imp's
generic island baker. Accessories use the right half: small role cells at the
top, and four 512-pixel feather cells at the bottom.

Brogue gives the fury a dark red glyph and "moist wings" that "beat loudly in
the darkness". The paint answers with near-black crimson feathers carrying
painted wet specular streaks along each shaft, against ashen grey-mauve skin,
blood-dark eye sockets and bright painted red eyes, so the winged silhouette
and the face both separate under the engine's flat light. The red is an art
cue from the glyph colour, not a literal material claim; nothing glows.
"""
import math

from .pixie_materials import hash3, vnoise, mix, clamp, smooth, scale, gauss
from .imp_materials import bake_atlas, encode_png

SKIN = 'graphics/BRGFURY.png'
SIZE = 2048
SMALL = ('eye', 'hair', 'wing_arm', 'finger', 'nail', 'toe', 'talon', 'tooth', 'brow', 'hair_cap')
RECTS = {n: (1024+i % 4*256+8, i//4*256+8, 1024+i % 4*256+248, i//4*256+248) for i, n in enumerate(SMALL)}
BIG = ('primary', 'secondary', 'covert', 'leg_feather')
for i, n in enumerate(BIG):
    RECTS[n] = (1024+i % 2*512+8, 1024+i//2*512+8, 1024+i % 2*512+504, 1024+i//2*512+504)

ASH = (178, 158, 166)
ASH_HI = (230, 216, 220)
ASH_LO = (74, 52, 66)
BLOOD = (120, 8, 18)
CRIMSON = (96, 6, 16)
BLACKRED = (26, 3, 8)
WET = (255, 160, 150)
SCALE = (158, 132, 96)
INK = (14, 3, 6)


def role(n):
    if n.startswith('eye_'): return 'eye'
    if n == 'hair_cap': return 'hair_cap'
    if n.startswith('hair'): return 'hair'
    if n.startswith('wing_arm'): return 'wing_arm'
    if n.startswith(('finger_', 'thumb_')): return 'finger'
    if n.startswith('nail_'): return 'nail'
    if n.startswith('toe_'): return 'toe'
    if n.startswith('talon_'): return 'talon'
    if n.startswith('tooth_'): return 'tooth'
    if n.startswith('brow_'): return 'brow'
    if n.startswith('primary_'): return 'primary'
    if n.startswith(('secondary_', 'tertial_')): return 'secondary'
    if n.startswith(('covert_', 'scapular_', 'mantle')): return 'covert'
    if n.startswith(('legfeather_', 'tailfeather_')): return 'leg_feather'
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


def feather(kind, u, v):
    """u: root 0 .. tip 1; v: across the vane 0..1 (0.5 = shaft).

    Near-black crimson at the root and the covered inner vane, grading to lit red
    only along the exposed edge and tip, so flat light cannot flatten the wing
    into one saturated red."""
    across = abs(v*2-1)
    seed = {'primary': 3, 'secondary': 5, 'covert': 7, 'leg_feather': 9}[kind]
    lit = max(smooth((u-.55)/.35), .8*smooth((across-.6)/.3)*smooth((u-.2)/.3))
    base = mix(BLACKRED, (58, 4, 12), smooth(u*1.6))
    base = mix(base, (172, 22, 34), lit*(.9 if kind != 'covert' else .65))
    # Barbs: fine diagonal striations sweeping toward the tip.
    barb = .5+.5*math.sin((u*38-across*14)+2*vnoise(u*6, v*6, seed))
    c = scale(base, .74+.3*barb)
    # Clumped moist vane: a few dark splits near the edge (sparser than before).
    split = smooth((across-.62)/.25)*smooth(hash3(int(u*11), seed, 1)-.55)
    c = mix(c, INK, .6*split)
    c = mix(c, INK, .45*smooth((across-.9)/.08)*(1-lit))
    # Shaft: dark root, pale crimson toward the tip.
    shaft = gauss(across, .05+.04*(1-u))
    c = mix(c, mix((60, 10, 16), (176, 60, 64), smooth((u-.2)/.5)), .75*shaft)
    # Painted wet specular streaks and droplets (moist wings), strongest where lit.
    streak = gauss(across-.28-.1*math.sin(u*5+seed), .07)*smooth((u-.25)/.3)*smooth((.95-u)/.2)
    c = mix(c, WET, (.18+.3*lit)*streak)
    drop = gauss(math.hypot((u-.66)*3, across-.45), .12)
    c = mix(c, (255, 214, 206), .5*drop*lit*(hash3(seed, 2, 3) > .3))
    return scale(c, .6+.4*smooth(u*2.5))


def shade(name, u, v):
    if name == 'eye':
        if v > .8:
            k = (v-.8)/.2
            c = mix((255, 60, 30), (255, 236, 190), smooth((k-.35)/.5))
            return c
        if v > .62:
            return mix((120, 0, 6), (255, 40, 24), smooth((v-.62)/.18))
        return (40, 0, 4)
    if name == 'hair':
        strand = math.sin(v*math.tau*9+6*vnoise(u*5, v*5, 2))
        c = mix((12, 3, 6), (46, 8, 16), smooth(u*1.2))
        c = mix(c, (120, 60, 70), .22*gauss(math.cos(v*math.tau)-.75, .12))
        return scale(c, .85+.15*strand)
    if name == 'wing_arm':
        c = mix(CRIMSON, BLACKRED, .5+.5*math.cos(v*math.tau))
        knot = gauss(abs(math.sin(u*math.pi*9)), .2)
        c = scale(c, .8+.25*knot)
        return mix(c, WET, .3*gauss(abs(v-.25), .05))
    if name == 'hair_cap':
        # Blob parameters: u around, v pole to pole; strands run pole-ward.
        strand = math.sin(u*math.tau*34+5*vnoise(u*8, v*3, 4))
        c = mix((14, 3, 6), (40, 8, 14), smooth(v))
        return scale(c, .85+.18*strand)
    if name == 'finger':
        c = mix(ASH, ASH_LO, .4*smooth(u*1.3))
        return scale(c, .85+.18*gauss(abs(math.sin(u*math.pi*2.5)), .15))
    if name in ('nail', 'talon'):
        c = mix((60, 40, 36), (18, 10, 10), smooth((u-.1)/.4))
        top = .5+.5*math.cos(v*math.tau)
        return mix(c, (230, 210, 200), .55*top**6*smooth(u*2))
    if name == 'toe':
        ring = gauss(abs(math.sin(u*math.pi*5)), .18)
        c = mix(SCALE, (86, 70, 52), .35+.4*ring)
        return scale(c, .9+.1*math.cos(v*math.tau))
    if name == 'tooth':
        return (236, 226, 200)
    if name == 'brow':
        return mix((40, 22, 28), (70, 44, 52), v)
    if name in BIG:
        return feather(name, u, v)
    return (128, 128, 128)


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


def skin_pigment(point, normal, m):
    from .fury_animation import EYE_Y, EYE_Z, MOUTH
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    light = clamp(.48+.32*nz+.26*nx)
    c = mix(ASH_LO, ASH, light**.9)
    c = mix(c, ASH_HI, .5*smooth((nz*.7+nx*.5-.6)/.25))
    # Veined, bruised skin: faint dark mottling and violet veins.
    vein = gauss(abs(vnoise(x*1.3, y*1.3, z*.9)), .03)
    c = mix(c, (92, 50, 84), .35*vein)
    if m['leg']+m['foot'] > .3:
        leg = m['leg']+m['foot']
        # Scaled avian shins and feet below the knee; feathered thighs are separate.
        below = smooth((19.6-z)/.8)
        rows = gauss(abs(math.sin(z*3.2)), .22)*smooth((nx+.3)/.4)
        s = mix(SCALE, (96, 76, 56), .5*rows)
        s = scale(s, .75+.35*light)
        c = mix(c, s, below*smooth((leg-.35)/.3))
        c = mix(c, (40, 6, 14), (1-below)*smooth((leg-.35)/.3)*.85)
    if m['torso'] > .3 and m['head'] < .4 and m['arm'] < .5:
        # Dark feather scales under the breast plumage and over the hips (no cloth).
        top = 37.4-.3*ay
        breast = smooth((top-z)/.3)*smooth((z-30.6-.5*math.sin(ay*2.2+x))/.35)
        hips = smooth((27.4+.5*math.sin(ay*3.1+x*1.3)-z)/.25)*smooth((z-22.5)/.4)
        plume = max(breast, hips)
        if plume > 0:
            row = (z*1.6+.5*math.floor((math.atan2(y, x)*3.2) % 2))
            fr = row-math.floor(row)
            cc = mix((24, 3, 8), (92, 10, 20), smooth(fr*1.3)*light)
            cc = mix(cc, (10, 1, 3), .7*smooth((fr-.85)/.12))
            c = mix(c, cc, plume)
        # Ribs and sternum on the bare midriff.
        mid = (1-plume)*smooth((nx-.1)/.4)
        c = mix(c, ASH_LO, .45*mid*gauss(abs(math.sin((z-28)*2.4)), .3)*smooth((ay-.9)/.4))
        c = mix(c, ASH_LO, .45*mid*gauss(y, .22))
    if m['arm'] > .4:
        c = mix(c, (56, 30, 46), .35*gauss(abs(math.sin(z*1.1+ay*.8)), .1))
        c = mix(c, ASH_LO, .3*smooth((m['hand']-.2)/.5))
    if m['head'] > .5:
        c = face_paint(point, normal, m, c)
    return c


def face_paint(point, normal, m, c):
    from .fury_animation import EYE_Y, EYE_Z, MOUTH
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    front = smooth((nx-.1)/.45)
    if m['ear'] > .3:
        return mix(c, (140, 70, 84), .5*front)
    # Deep, blood-dark sockets and weeping streaks of blood (an art choice).
    socket = gauss(math.hypot((ay-EYE_Y)/1.25, (z-EYE_Z)/.95), 1.)*front
    c = mix(c, (34, 4, 10), .9*socket)
    streak = gauss(ay-EYE_Y-.05*math.sin(z*3), .16)*smooth((EYE_Z-.5-z)/.3)*smooth((z-(EYE_Z-3.2))/.6)*front
    c = mix(c, BLOOD, .8*streak)
    # Gaunt cheek hollows and a lit cheekbone.
    c = mix(c, ASH_LO, .45*gauss(math.hypot(ay-1.35, z-EYE_Z+1.7), .55)*front)
    c = mix(c, ASH_HI, .35*gauss(math.hypot(ay-1.6, z-EYE_Z+.95), .35)*front)
    # Open snarling mouth: black lips, dark cavity, painted upper and lower teeth.
    mx, mz, half = MOUTH
    if nx > .1 and ay < half+.3:
        t = ay/half
        open_ = .5*(1-t*t)+.05
        d = z-mz-.12*t*t
        inside = smooth((open_-abs(d))/.06)*smooth((half-ay)/.15)
        tooth = abs(math.sin(ay*6.5+.4))
        teeth = (smooth((d-open_*.35)/.05)+smooth((-d-open_*.45)/.05))*smooth((tooth-.2)/.12)
        c = mix(c, mix((24, 2, 6), (232, 220, 196), clamp(teeth)*.9), inside)
        c = mix(c, (20, 4, 8), .85*gauss(abs(d)-open_, .08)*smooth((half+.25-ay)/.2))
    return c


FRACTIONS = {'head': ('head', 'ear_L', 'ear_R'), 'ear': ('ear_L', 'ear_R'),
             'arm': ('arm_L', 'forearm_L', 'hand_L', 'arm_R', 'forearm_R', 'hand_R'),
             'hand': ('hand_L', 'hand_R'),
             'leg': ('thigh_L', 'shin_L', 'foot_L', 'toes_L', 'thigh_R', 'shin_R', 'foot_R', 'toes_R'),
             'foot': ('foot_L', 'toes_L', 'foot_R', 'toes_R'), 'torso': ('pelvis', 'spine', 'chest', 'neck')}


def connected_atlas(parts, pixels=False):
    from .fury_animation import IDS
    return bake_atlas(parts, IDS, FRACTIONS, skin_pigment, accessory_pixels, pixels, origin=(-20, -20, 0))
