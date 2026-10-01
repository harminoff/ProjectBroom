"""Original vampire paint: bloodless skin, oxblood coat, lace and a leathery cloak.

Presentation-only. Brogue gives the vampire a white glyph and red blood
(`DF_RED_BLOOD`); the bluish, bloodless skin with dark veins, the red-rimmed
eyes, the blood at the mouth and on the lace, the oxblood frock coat, black
breeches and boots, and the leathery bat-wing cloak with a crimson lining are
artistic interpretation, not new powers. Nothing emits light: the red irises
are ordinary paint. The engine's flat light hides sculpted form, so value
contrast is painted: pale head, hands and jabot against dark cloth, a warm
brown sheen and paler ribs so the black cloak separates from the grey walls,
fold occlusion and specular pools on boots and silver.

Islands and baking reuse the revenant's per-triangle Morton atlas (read-only).
"""
import math
from .revenant_materials import bake, vnoise, mix, smooth, GRID, SIZE  # noqa: F401

COAT_ROWS = [(24.5, -.2, 4.4, 5.4), (29, -.2, 4.2, 5.2), (34, -.4, 3.7, 4.6), (39, -.6, 3.9, 5.2),
             (44, -.6, 4.3, 6.2), (48, -.4, 4.0, 6.6), (50.5, -.1, 3.0, 4.6), (52.2, .5, 1.7, 2.0)]
CLOAK_ROWS = [(9.5, -4.2, 8.6, 12.6), (18, -3.6, 8.0, 12.0), (28, -3.0, 7.2, 11.4), (38, -2.4, 6.6, 11.0),
              (45, -1.9, 6.2, 11.0), (49.5, -1.4, 5.4, 9.8), (52.3, -.9, 3.8, 6.6)]
WRISTS = {'L': (2.6, 10.0, 27.4), 'R': (2.6, -10.0, 27.4)}
OXBLOOD = (98, 18, 30)
OX_SHADE = (34, 6, 12)
VELVET = (22, 18, 24)
SKIN = (182, 184, 196)
SKIN_SHADE = (92, 82, 112)
BLOOD = (120, 8, 12)
CLOAK = (58, 44, 42)
CLOAK_SHADE = (12, 9, 10)
LINING = (62, 22, 26)
SILVER = (190, 194, 204)


CLOAK_A = (98, 262)
CLOAK_SCALLOPS = 6


def cloak_hem(u):
    """Deep bat-wing scallops: the hem rises high between hanging rib points."""
    return 8.6*abs(math.sin(math.pi*u*CLOAK_SCALLOPS))**.85


def _interp(rows, z, k):
    if z <= rows[0][0]:
        return rows[0][k]
    for a, b in zip(rows, rows[1:]):
        if a[0] <= z <= b[0]:
            return a[k]+(b[k]-a[k])*(z-a[0])/(b[0]-a[0])
    return rows[-1][k]


def light(normal):
    return .72+.36*max(-.6, normal[2]*.7+normal[0]*.3)


def finish(c, normal, cav, floor=.25, occ=3.2):
    c = tuple(v*light(normal) for v in c)
    edge = max(0.0, -cav)*1.2
    occl = max(0.0, cav)*occ+.35*smooth(0, -.9, normal[2])
    return tuple(min(255, v*max(floor, 1-occl)*(1+edge)) for v in c)


def folds(point, k=9, depth=.8):
    x, y, z = point
    ang = math.atan2(y, x+1)
    warp = 1.8*vnoise(ang*1.4, z*.06, 5.1)
    f = math.sin(ang*k+warp+z*.03)+.4*math.sin(ang*19+1.4*warp)
    return max(-1, min(1, f*depth))


def sheen(normal, c, lit, power=5, amount=.45):
    spec = max(0.0, normal[2]*.55+normal[0]*.55)**power
    return mix(c, lit, amount*spec)


def coat(point, normal, cav):
    x, y, z = point
    cx, rx, ry = (_interp(COAT_ROWS, z, k) for k in (1, 2, 3))
    ang = math.degrees(math.atan2(y/ry, (x-cx)/rx))
    c = mix(OX_SHADE, OXBLOOD, .7+.3*folds(point, 7, .6))
    # Black velvet lapels in a deep V down to the waist; a dark placket.
    lapel = 12+22*smooth(36, 49, z)
    if z > 34 and abs(ang) < lapel:
        c = VELVET if abs(ang) > 6 else mix(VELVET, (60, 10, 16), .5)
    elif abs(ang) < 5 and z <= 34:
        c = mix(c, VELVET, .6)
    # Faint brocade diaper in the oxblood cloth.
    elif (math.sin(ang*.45)*math.sin(z*1.3)) > .82:
        c = mix(c, (150, 44, 44), .35)
    c = sheen(normal, c, (170, 70, 70), 6, .3)
    return finish(c, normal, cav)


def sleeve(point, normal, cav):
    x, y, z = point
    side = 'L' if y > 0 else 'R'
    d = math.dist(point, WRISTS[side])
    if d < 2.4:
        # Turned-back velvet cuff with a lace edge.
        c = (230, 226, 216) if d > 2.0 or z < 27.9 else VELVET
        return finish(c, normal, cav)
    c = mix(OX_SHADE, OXBLOOD, .7+.3*folds((x, y*.3, z), 5, .6))
    return finish(sheen(normal, c, (170, 70, 70), 6, .3), normal, cav)


def legs(point, normal, cav):
    x, y, z = point
    if z < 13.5:
        # Tall black riding boots with a folded top and hard highlights.
        c = (20, 17, 18) if z < 12.2 else (48, 36, 30)
        c = sheen(normal, c, (170, 160, 160), 8, .7)
        return finish(c, normal, cav, .4, 2.5)
    c = mix((18, 16, 20), (44, 40, 48), .5+.5*folds(point, 4, .5))
    return finish(c, normal, cav)


def skin(point, normal, cav, name):
    x, y, z = point
    c = SKIN
    # Bloodless blue-white skin, violet hollows, a web of dark veins.
    c = mix(c, (140, 146, 168), .5*vnoise(x*.9, y*.9, z*.9))
    vein = smooth(.955, .995, 1-abs(math.sin(x*1.7+z*2.3+1.6*math.sin(y*2.9+z*.7))))*smooth(.35, .6, vnoise(x*.6, y*.6, z*.6))
    c = mix(c, (70, 70, 120), .5*vein)
    if name.startswith(('head', 'jaw', 'neck')):
        # Gaunt modelling painted for flat light: a pale lit dome and brow,
        # blue-grey temples, jaw and back of the skull, hollow cheeks under a
        # lit cheekbone ridge, and deep shadowed sockets round the eyes.
        c = mix(c, (112, 118, 146), .55*smooth(3.0, -1.5, x)+.25*smooth(58, 61.5, z)*smooth(1.5, 3, abs(y)))
        temple = math.exp(-((abs(y)-2.2)/.9)**2-((z-58.2)/1.6)**2)
        c = mix(c, (104, 110, 140), .6*temple)
        c = mix(c, (60, 62, 118), .75*vein*(temple+smooth(55, 53, z)))
        c = mix(c, (116, 118, 144), .55*smooth(55.6, 53.4, z)*smooth(1.0, 2.0, abs(y)))
        hollow = math.exp(-((abs(y)-1.75)/.7)**2-((z-55.25)/.8)**2)*smooth(2.5, 4.0, x)
        c = mix(c, (72, 64, 94), .8*hollow)
        ridge = math.exp(-((abs(y)-1.95)/.8)**2-((z-56.45)/.35)**2)
        c = mix(c, (226, 228, 236), .55*ridge)
        eyes = math.exp(-((abs(y)-1.05)/1.0)**2-((z-57.05)/.9)**2)*smooth(3.6, 5.0, x)
        c = mix(c, (34, 18, 30), .88*eyes)
        if name.startswith(('head_brow', 'head_cheek', 'head_nose')):
            c = mix(c, (228, 230, 238), .45*max(0.0, normal[2]*.7+normal[0]*.5))
        # Fresh blood at the lips and running from the chin.
        run = math.exp(-((y-.3)/.8)**2)*smooth(55.3, 53.2, z)*smooth(4.2, 5.2, x)
        lips = math.exp(-(y/1.2)**2-((z-54.95)/.45)**2)*smooth(4.8, 5.5, x)
        c = mix(c, BLOOD, max(.85*lips, .75*run))
        if name.startswith('head_ear'):
            c = mix(c, (190, 150, 170), .35*smooth(0, -2, x))
    elif name.startswith('hand'):
        knuckle = abs(math.sin(z*2.1))**6
        c = mix(c, (150, 130, 160), .35*knuckle)
        c = mix(c, BLOOD, .6*smooth(.72, .82, vnoise(x*1.5, y*1.5, z*1.5)))
    spec = max(0.0, normal[2]*.6+normal[0]*.5)**6
    c = mix(tuple(v*light(normal) for v in c), (230, 230, 240), .2*spec)
    occl = max(0.0, cav)*3.2+.3*smooth(.1, -.8, normal[2])
    return tuple(min(255, v*max(.3, 1-occl)) for v in c)


def cloak(point, normal, cav, rib=False):
    x, y, z = point
    cx, rx, ry = (_interp(CLOAK_ROWS, z, k) for k in (1, 2, 3))
    radial = ((x-cx)/rx**2, y/ry**2)
    ln = math.hypot(*radial) or 1
    outward = (normal[0]*radial[0]+normal[1]*radial[1])/ln
    deg = math.degrees(math.atan2(y/ry, (x-cx)/rx)) % 360
    u = (deg-CLOAK_A[0])/(CLOAK_A[1]-CLOAK_A[0])
    hem = CLOAK_ROWS[0][0]+cloak_hem(max(0.0, min(1.0, u)))
    rim = max(smooth(.05, .015, u), smooth(.95, .985, u), smooth(hem+1.6, hem+.4, z))
    if rib:
        c = sheen(normal, (40, 30, 30), (110, 90, 86), 4, .35)
        return finish(c, normal, cav, .35)
    if outward < -.2:
        # Inner membrane: dark wine-brown skin with branching veins, not silk.
        c = mix((16, 8, 10), LINING, .55+.35*folds(point, 6, .7))
        vein = smooth(.96, .995, 1-abs(math.sin(y*1.1+z*.9+1.2*math.sin(z*.6+y*.5))))
        c = mix(c, (110, 30, 36), .6*vein)
        c = mix(c, (150, 34, 44), .8*rim)
        return finish(sheen(normal, c, (150, 90, 90), 5, .3), normal, cav, .3)
    # Leathery membrane: mottled, with fine branching veins and a warm sheen.
    c = mix(CLOAK_SHADE, CLOAK, .6+.35*folds(point, 6, .7))
    c = mix(c, (96, 70, 62), .5*smooth(.45, .8, vnoise(x*.4, y*.4, z*.3)))
    c = mix(c, (18, 12, 12), .45*smooth(.55, .85, vnoise(x*.9+4, y*.9, z*.7)))
    vein = smooth(.965, .995, 1-abs(math.sin(y*.9+z*1.1+1.4*math.sin(z*.5+y*.4))))
    c = mix(c, (20, 12, 12), .6*vein)
    c = sheen(normal, c, (176, 134, 120), 3, .55)
    # Crimson rim along the side edges and scalloped hem separates the cloak
    # from dark walls at distance.
    c = mix(c, (156, 36, 46), .85*rim)
    return finish(c, normal, cav, .3)


def role(name):
    for prefix, r in (('socket', 'dark'), ('mouth', 'mouth'), ('fang', 'fang'), ('nail', 'nail'), ('iris', 'iris'),
                      ('jabot', 'lace'), ('button', 'silver'), ('clasp', 'silver'), ('collar', 'velvet'),
                      ('skirt', 'skirt'), ('cloak', 'cloak'), ('rib', 'rib'),
                      ('head', 'skin'), ('jaw', 'skin'), ('neck', 'skin'), ('hand', 'skin')):
        if name.startswith(prefix):
            return r
    return 'body'


def pigment(point, normal, name, cav):
    r = role(name)
    x, y, z = point
    if r == 'body':
        ry = _interp(COAT_ROWS, z, 3)
        if z > 22 and abs(y) > ry+.6:
            return sleeve(point, normal, cav)
        if z < 24.8:
            return legs(point, normal, cav)
        return coat(point, normal, cav)
    if r == 'skirt':
        # Coat tails: oxblood outside, black silk inside.
        inward = normal[0]*x+normal[1]*y < 0
        c = (16, 12, 16) if inward else mix(OX_SHADE, OXBLOOD, .7+.3*folds(point, 7, .6))
        return finish(c, normal, cav)
    if r == 'cloak':
        return cloak(point, normal, cav)
    if r == 'rib':
        return cloak(point, normal, cav, True)
    if r == 'skin':
        return skin(point, normal, cav, name)
    if r == 'lace':
        c = mix((224, 218, 204), (150, 142, 132), .5+.5*math.sin(z*6+abs(y)*2.5))
        # Blood flecks spattered down the lace.
        c = mix(c, BLOOD, .85*smooth(.62, .72, vnoise(x*2.2, y*2.2, z*2.2))*smooth(50, 45.5, z))
        return finish(c, normal, cav, .45, 2.0)
    if r == 'silver':
        return sheen(normal, tuple(v*light(normal)*.85 for v in SILVER), (250, 250, 255), 4, .6)
    if r == 'velvet':
        return finish(VELVET, normal, cav)
    if r == 'iris':
        return (214, 24, 20)
    if r == 'dark':
        return (26, 6, 10)
    if r == 'mouth':
        return (60, 4, 8)
    if r == 'fang':
        return mix((170, 164, 140), (240, 236, 220), max(0, normal[0]))
    if r == 'nail':
        return mix((12, 10, 12), (70, 64, 70), max(0, normal[2]*.5+normal[0]*.5))
    return (255, 0, 255)
