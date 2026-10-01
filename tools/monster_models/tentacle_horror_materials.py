"""Original tentacle horror paint: bruised violet flesh for the engine's flat light.

Brogue gives the horror a purple glyph (75, 25, 85) and purple blood
(DF_PURPLE_BLOOD); both are identity cues, not literal whole-body paint and not
powers. The flesh is deep aubergine with mauve muscle crowns, raised magenta
veins and near-black occlusion in the braid grooves where the trunk's four
tentacles twist together. Tentacle undersides are a paler raw pink with pale
sucker cups. The sucking maw is a wet crimson pit ringed with ivory hooks.
Nothing emits light; the value range is painted wide on purpose.

The paint reuses the kraken's per-triangle atlas and limb index read-only.
"""
import math
from .centaur_materials import vnoise, mix, clamp
from .kraken_materials import LimbIndex, worley, finish, smooth, scale, connected_atlas as _atlas
from . import tentacle_horror_animation as shape

SKIN = shape.SKIN
TAU = math.tau

BRUISE = (14, 3, 18)
DEEP = (40, 10, 50)
PURPLE = (98, 34, 112)
MAUVE = (150, 78, 158)
VEIN = (214, 92, 204)
VEIN_EDGE = (22, 5, 30)
PINK = (248, 192, 216)
PINK_SH = (216, 140, 178)
LIP = (138, 30, 70)

TRUNK = None
LIMBS = None


def indices():
    global TRUNK, LIMBS
    if TRUNK is None:
        TRUNK = LimbIndex(shape.STRANDS, cell=6.)
        LIMBS = LimbIndex(shape.LIMBS)
    return TRUNK, LIMBS


def flesh(p, n):
    m = vnoise(p[0]*.16, p[1]*.16, p[2]*.16)+.5*vnoise(p[0]*.5, p[1]*.5, p[2]*.5)
    c = mix(DEEP, PURPLE, clamp(.5+1.2*m))
    # Raised, branching veins: ridged noise lines, lighter on top of the flesh.
    # Each vein gets a dark bruised bed either side of its raised magenta core.
    for scale_, width, salt in ((.23, .034, 0.), (.55, .026, 7.), (1.1, .02, 13.)):
        v = abs(vnoise(p[0]*scale_+salt, p[1]*scale_, p[2]*scale_*1.4))
        c = mix(c, VEIN_EDGE, .55*smooth((2.4*width-v)/(1.4*width))*(1-smooth((width-v)/width)))
        c = mix(c, VEIN, .85*smooth((width-v)/width))
    # Fine pores and wrinkles break up any plastic smoothness.
    c = scale(c, .86+.28*(vnoise(p[0]*2.3, p[1]*2.3, p[2]*2.3)+.5)*.5+.1*vnoise(p[0]*5, p[1]*5, p[2]*5))
    blot, h = worley(p, 2.4, 41)
    if blot < .3 and h > .45:
        c = mix(c, BRUISE, .5*smooth((.3-blot)/.2))
    return c


def strand_paint(p, n):
    trunk, _ = indices()
    best = second = None
    for index, row in _near(trunk, p):
        d = math.dist(p, row['c'])-row['r']
        if best is None or d < best[0]:
            best, second = (d, row), best
        elif second is None or d < second[0]:
            second = (d, row)
    c = flesh(p, n)
    # Twisted muscle bands along each strand, crowned with mauve.
    if best is not None:
        arc = best[1]['arc']
        band = .5+.5*math.cos(arc*TAU/3.2)
        c = mix(c, MAUVE, .35*band**3*clamp(.4+.6*n[2]+.3))
    groove = 0.
    if best is not None and second is not None and second[1] is not best[1]:
        groove = math.exp(-((second[0]-best[0])/1.4)**2)
    return c, 1-.8*groove


def _near(index, p):
    key = tuple(int(math.floor(c/index.cell)) for c in p)
    out = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                out += index.grid.get((key[0]+dx, key[1]+dy, key[2]+dz), ())
    return out


def limb_paint(p, n, q):
    limb, row = q['limb'], q['row']
    cosv = q['cosv']
    ventral = smooth((cosv-.1)/.42)
    arc, s = row['arc'], row['s']
    back = flesh(p, n)
    ring = .5+.5*math.cos(arc*TAU/1.3)
    back = scale(back, 1-.22*ring**5*(1-ventral))
    back = mix(back, MAUVE, .28*smooth((.2-abs(q['sinl']))/.2)*(1-ventral))   # dorsal ridge highlight
    belly = mix(PINK_SH, PINK, clamp(.5+.5*cosv+.4*vnoise(p[0]*.8, p[1]*.8, p[2]*.8)))
    belly = scale(belly, 1-.18*(.5+.5*math.cos(arc*TAU/(1.1*max(.5, row['r'])))))
    c = mix(back, belly, ventral)
    c = mix(c, BRUISE, .6*math.exp(-((cosv-.08)/.08)**2))
    c = mix(c, BRUISE, .3*smooth((s-.8)/.2)*(1-ventral))
    occ = 1-.5*(1-smooth((arc-limb.exit)/4.))
    return c, occ


def head_paint(p, n):
    c = flesh(p, n)
    top = clamp(.5+.8*n[2])
    c = mix(c, MAUVE, .3*top*smooth(vnoise(p[0]*.3+2, p[1]*.3, p[2]*.3)+.2))
    d = math.dist(p, shape.MAW)
    c = mix(c, LIP, .8*smooth((6.8-d)/1.6))
    c = mix(c, BRUISE, .55*math.exp(-((d-7.3)/.7)**2))
    return c


def pigment(p, n):
    trunk, limbs = indices()
    q = limbs.query(p)
    hq = trunk.query(p)
    head = ((p[0]-shape.HEAD_C[0])/shape.HEAD_R[0])**2+((p[1]-shape.HEAD_C[1])/shape.HEAD_R[1])**2 \
        + ((p[2]-shape.HEAD_C[2])/shape.HEAD_R[2])**2
    trunk_sdf = hq['sdf'] if hq else 99.
    occ = 1.
    vent = 0.
    if q is not None and q['sdf'] < min(trunk_sdf, 1.2 if p[2] > 56 else 99.)+.3:
        c, occ = limb_paint(p, n, q)
        vent = smooth((q['cosv']-.1)/.42)
    elif p[2] > 55 or head < 1.35:
        c = head_paint(p, n)
        occ = 1-.35*smooth((58-p[2])/4)
    else:
        c, occ = strand_paint(p, n)
        occ *= 1-.45*smooth((16-p[2])/14)
    under = smooth((-n[2]-.3)/.5)
    occ *= 1-.35*under*(1-.8*vent)
    # Heavy roots: the lowest flesh sinks into bruised darkness.
    occ *= 1-.35*smooth((9-p[2])/8)*(1-.6*vent)
    # Wet sheen only on surfaces facing up; flanks and undersides stay matte flesh.
    sheen = 1.25*smooth((n[2]-.05)/.7)
    return finish(c, n, occ, gloss=sheen, top=.40*(1-.6*vent))


def strip_color(y, u):
    if abs(y-600) <= 30:   # sucker cup: dark pit, raw pink lip, pale rim, pink skirt
        keys = ((0, (40, 8, 30)), (.3, (110, 34, 80)), (.52, (214, 120, 160)), (.78, (246, 214, 226)), (1, (214, 140, 172)))
    elif abs(y-680) <= 30:   # hook teeth: ivory to a translucent yellowed tip
        keys = ((0, (150, 110, 120)), (.35, (232, 222, 200)), (1, (252, 246, 220)))
    else:
        return None
    for (u0, a), (u1, b) in zip(keys, keys[1:]):
        if u <= u1:
            return mix(a, b, (u-u0)/(u1-u0))
    return keys[-1][1]


def maw_color(dx, dy):
    r = math.hypot(dx, dy)
    if r > 1:
        return (70, 14, 40)
    angle = math.atan2(dy, dx)
    # Wet crimson throat: concentric muscular folds darkening to a black pit.
    fold = .5+.5*math.cos(r*TAU*4.5+.8*math.sin(angle*7))
    c = mix((10, 2, 8), (150, 32, 70), smooth((r-.08)/.7))
    c = scale(c, .72+.28*fold)
    c = mix(c, (190, 70, 110), .5*math.exp(-((r-.9)/.08)**2))
    for gx, gy, gr in ((-.35, -.45, .07), (.2, -.62, .04)):
        if math.hypot(dx-gx, dy-gy) < gr:
            c = (250, 214, 228)
    return c


def accessory_pixels(size=1024):
    pixels = bytearray(size*size*3)
    for y in range(size):
        for x in range(size):
            if x < 512 and y < 512:
                c = maw_color((x-256)/238, (y-256)/238)
            else:
                c = strip_color(y, clamp((x/1024-.02)/.96))
            if c is not None:
                o = (y*size+x)*3
                pixels[o:o+3] = bytes(max(0, min(255, round(v))) for v in c)
    return pixels


def connected_atlas(parts, pixels=False):
    return _atlas(parts, pixels, pigment, accessory_pixels)
