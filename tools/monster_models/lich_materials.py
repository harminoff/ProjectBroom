"""Original lich paint: royal cope, gold regalia, mummified skin and a green gem.

Presentation-only. Brogue gives the lich a white glyph and the same green lich
light as its phylactery (`lichLightColor`); the royal blue cope, crimson lining,
tarnished gold, ash-dusted hem and leathery skin are artistic interpretation,
not new powers. Only texels inside the glow key (``glow_key``; matched by
``shaders/lich-phylactery.fp``) render fullbright: the faceted phylactery gem
and two eye pinpoints. The faint green cast on the face, beard, hand and chest
around the gem is ordinary paint. The engine's flat light hides sculpted form,
so value contrast is painted: top light, fold occlusion, cavity darkening and
specular pools on gold.

Islands and baking reuse the revenant's per-triangle Morton atlas (read-only).
"""
import math
from .revenant_materials import bake, vnoise, mix, smooth, GRID, SIZE  # noqa: F401

ROBE_ROWS = [(.6, -2.2, 10.2, 11.2), (4, -1.8, 9.2, 10.2), (12, -1.3, 7.6, 8.8), (20, -1.0, 6.5, 7.8),
             (28, -.8, 5.8, 7.3), (34, -.8, 5.5, 7.1), (40, -.8, 5.3, 7.7), (46, -.6, 5.0, 8.6),
             (49.5, -.3, 4.0, 7.2), (51.5, 0, 2.4, 3.4), (52.6, .2, 1.4, 2.0)]
COPE_ROWS = [(38.5, -1.2, 7.4, 13.0), (42, -1.1, 7.6, 14.0), (45.5, -1.0, 7.4, 14.2), (48.5, -.9, 6.6, 12.6),
             (50.8, -.7, 5.0, 9.4), (52.4, -.4, 3.2, 5.2)]
GEM = (6.0, 0.0, 40.8)
GOLD_DARK = (92, 62, 22)
GOLD = (176, 132, 56)
GOLD_LIT = (236, 200, 118)
ROYAL = (40, 50, 118)
ROYAL_SHADE = (8, 10, 30)
MIDNIGHT = (27, 27, 58)
LINING = (112, 20, 30)
LEATHER = (98, 72, 48)
LICHLIGHT = (70, 170, 120)
GLOW = (120, 255, 182)
GLOW_DARK = (18, 128, 80)


def cope_hem(u):
    """Hem lift of the cope's lowest row: five hanging points plus ragged,
    irregular tatters on alternate hem vertices (shared with the geometry)."""
    base = 3.2*abs(math.sin(math.pi*u*5))**1.5
    k = max(0.0, min(1.0, u))*44
    i = math.floor(k)
    f = k-i

    def rag(j):
        return 2.2*((j*7+3) % 5)/4*(j % 2)
    return base+rag(i)*(1-f)+rag(i+1)*f


DUSTY = (76, 82, 104)
INDIGO = (30, 34, 70)
TROUGH = (7, 7, 22)


def faded(point, normal, k=11):
    """Aged cope cloth: dark indigo fold troughs, faded dusty blue on lit planes."""
    f = folds(point, k, .95)
    c = mix(INDIGO, TROUGH, (-f)**.8) if f < 0 else mix(INDIGO, DUSTY, f**1.3)
    c = mix(c, (100, 100, 108), .3*max(0.0, normal[2]))
    return tuple(v*(.62+.38*(f+1)/2) for v in c)


def glow_key(rgb):
    """True where the shader renders fullbright (kept in sync with the .fp)."""
    r, g, b = (c/255 for c in rgb)
    return r < .6 and g > .86 and .35 < b < .85


def _interp(rows, z, k):
    if z <= rows[0][0]:
        return rows[0][k]
    for a, b in zip(rows, rows[1:]):
        if a[0] <= z <= b[0]:
            return a[k]+(b[k]-a[k])*(z-a[0])/(b[0]-a[0])
    return rows[-1][k]


def light(normal):
    return .72+.36*max(-.6, normal[2]*.7+normal[0]*.3)


def lichlight(point, c, strength=.42):
    """Painted green cast from the gem on nearby surfaces (not emissive)."""
    d2 = sum((a-b)**2 for a, b in zip(point, GEM))
    return mix(c, LICHLIGHT, strength*math.exp(-d2/30))


def finish(c, normal, cav, floor=.25, occ=3.2):
    c = tuple(v*light(normal) for v in c)
    edge = max(0.0, -cav)*1.2
    occl = max(0.0, cav)*occ+.35*smooth(0, -.9, normal[2])
    return tuple(min(255, v*max(floor, 1-occl)*(1+edge)) for v in c)


def gold(point, normal, cav, tarnish=.35):
    x, y, z = point
    spec = max(0.0, normal[2]*.55+normal[0]*.55)**4
    c = mix(GOLD, GOLD_DARK, tarnish*vnoise(x*.9, y*.9, z*.9))
    c = mix(c, GOLD_LIT, .75*spec)
    # Centuries of tarnish: verdigris creeping into recesses and blotches.
    verd = max(smooth(.62, .8, vnoise(x*1.3+7, y*1.3, z*1.3)), min(1.0, max(0.0, cav)*4))
    c = mix(c, (58, 104, 86), .45*verd)
    c = tuple(v*(.78+.3*max(0.0, normal[2]*.6+normal[0]*.4)) for v in c)
    occl = max(0.0, cav)*3.5+.3*smooth(0, -.9, normal[2])
    return tuple(min(236, v*max(.35, 1-occl)) for v in c)


def folds(point, k=9, depth=.8):
    x, y, z = point
    ang = math.atan2(y, x+1)
    warp = 1.8*vnoise(ang*1.4, z*.06, 2.3)
    f = math.sin(ang*k+warp+z*.03)+.4*math.sin(ang*19+1.4*warp)
    return max(-1, min(1, f*depth))


def age(point, c, hem_z=10.0):
    """Faded, dusty, moth-eaten cloth: pale dust blooms and dark holes."""
    x, y, z = point
    c = mix(c, (78, 74, 80), .3*smooth(.45, .8, vnoise(x*.22, y*.22, z*.16)))
    c = mix(c, (64, 60, 58), .6*smooth(hem_z, .5, z))
    n = .6*vnoise(x*.5+2, y*.5, z*.35)+.4*vnoise(x*2.1, y*2.1, z*2.1)
    hole = smooth(.76, .8, n)
    return mix(c, (6, 5, 8), .85*hole)


def robe(point, normal, cav):
    x, y, z = point
    # Same aged cloth as the cope, a shade deeper: indigo troughs, dusty lit folds.
    c = tuple(v*.82 for v in faded(point, normal, 9))
    # Gold hem band with a dark meander, ash dusting toward the floor.
    if 1.2 < z < 3.8:
        c = gold(point, normal, cav, .5)
        if abs(math.sin(math.atan2(y, x+2)*28)) > .8 and 2.0 < z < 3.0:
            c = mix(c, (50, 30, 14), .7)
        return c
    c = age(point, c)
    c = lichlight(point, c, .3)
    return finish(c, normal, cav)


def sleeve(point, normal, cav):
    x, y, z = point
    if z < 26.2:
        # Worn gold cuff, frayed into dark tatters toward its edge.
        c = gold(point, normal, cav, .7)
        tear = smooth(.5, .62, vnoise(math.atan2(y, x)*9, z*2.5, 7.7))*smooth(25.6, 24.2, z)
        return mix(c, (18, 15, 22), .85*tear)
    c = faded((x, y*.3, z), normal, 5)
    # Embroidered gold bands above the cuff and at the elbow.
    if 26.2 <= z < 27.0 or 36.5 < z < 37.3:
        c = mix(c, GOLD_DARK, .8)
    return finish(age(point, c, 0), normal, cav)


def cope(point, normal, cav):
    x, y, z = point
    cx, rx, ry = (_interp(COPE_ROWS, z, k) for k in (1, 2, 3))
    radial = ((x-cx)/rx**2, y/ry**2, 0)
    ln = math.hypot(radial[0], radial[1]) or 1
    outward = (normal[0]*radial[0]+normal[1]*radial[1])/ln
    deg = math.degrees(math.atan2(y/ry, (x-cx)/rx)) % 360
    u = (deg-44)/272
    hem = COPE_ROWS[0][0]+cope_hem(max(0, min(1, u)))
    x_, y_, z_ = point
    if outward < -.2:
        # Crimson silk lining, deep in shadow.
        c = mix((40, 6, 12), LINING, .5+.4*folds(point, 7, .7))
        return finish(c, normal, cav, .3)
    # Gold orphrey along the open front and the pointed hem.
    if z < hem+.7:
        # Frayed hem edge: dark, ragged threads.
        c = mix((52, 46, 44), (14, 12, 18), smooth(.35, .6, vnoise(u*120, z*3, 1.3)))
        return finish(c, normal, cav, .3)
    if u < .05 or u > .95 or z < hem+1.8 or z > 52.0:
        c = gold(point, normal, cav, .7)
        # The worn orphrey is torn through in places.
        return mix(c, (26, 24, 30), .8*smooth(.62, .7, vnoise(u*60, z*1.6, 4.4)))
    c = faded(point, normal)
    # Scattered embroidered gold sigils: small crowns of dots and bars.
    gu, gz = u*24, (z-hem)/3.2
    cu, cz = gu-math.floor(gu)-.5, gz-math.floor(gz)-.5
    if (math.floor(gu)+math.floor(gz)) % 2 == 0 and cu*cu+cz*cz < .06:
        c = mix(c, GOLD_DARK, .8)
    # A second thin gold line inside the border.
    if hem+2.5 < z < hem+2.9 or .075 < u < .085 or .915 < u < .925:
        c = mix(c, GOLD_DARK, .7)
    return finish(age(point, c, 0), normal, cav)


def stole(point, normal, cav):
    x, y, z = point
    c = gold(point, normal, cav, .55)
    # A column of crimson lozenges outlined in dark thread down the centre.
    half = 2.3+1.3*smooth(40, 2, z)
    d = abs(y)/(.62*half)+abs((z % 6.0)-3.0)/2.5
    c = mix(c, (44, 26, 12), .8*smooth(.16, .04, abs(d-1)))
    if d < .92:
        c = mix((96, 14, 22), (140, 30, 34), max(0.0, normal[0]*.5+normal[2]*.5))
        c = mix(c, (200, 160, 80), smooth(.3, .15, d))
    if abs(abs(y)-(2.3+1.3*smooth(40, 2, z))) < .28:
        c = mix(c, (40, 22, 10), .7)
    return c


def skin(point, normal, cav, name):
    x, y, z = point
    c = LEATHER
    # Leathery, cracked and dry: blotched, with sunken, darker hollows.
    c = mix(c, (80, 64, 50), .6*vnoise(x*.9, y*.9, z*.9))
    c = mix(c, (150, 132, 104), .35*smooth(.6, .8, vnoise(x*2.3+5, y*2.3, z*2.3)))
    if name.startswith(('head', 'jaw', 'neck')):
        # Sunken temples and cheeks, lit cheekbones and brow.
        hollow = math.exp(-((abs(y)-1.9)/.9)**2-((z-55.4)/1.3)**2)
        c = mix(c, (54, 36, 22), .75*hollow)
        temple = math.exp(-((abs(y)-2.6)/.8)**2-((z-58.0)/1.2)**2)
        c = mix(c, (62, 44, 28), .5*temple)
        # Stretched, wrinkled hide rather than clean bone.
        c = mix(c, (70, 50, 34), .4*abs(math.sin(z*5.5+math.sin(y*3)))**3)
        eyes = math.exp(-((abs(y)-1.15)/1.0)**2-((z-57.3)/1.0)**2)*smooth(2.4, 3.8, x)
        c = mix(c, (30, 22, 20), .6*eyes)
        crack = smooth(.95, .995, 1-abs(math.sin(y*2.4+z*1.3+.8*math.sin(z*3.1+y*1.7))))
        c = mix(c, (40, 30, 24), .7*crack)
    elif name.startswith('hand'):
        knuckle = abs(math.sin(z*2.2))**6
        c = mix(c, (150, 128, 98), .35*knuckle)
    spec = max(0.0, normal[2]*.6+normal[0]*.5)**6
    c = mix(tuple(v*light(normal) for v in c), (180, 160, 120), .12*spec)
    c = lichlight(point, c, .25 if name.startswith(('head', 'jaw', 'neck')) else .45)
    occl = max(0.0, cav)*3.2+.3*smooth(.1, -.8, normal[2])
    return tuple(v*max(.3, 1-occl) for v in c)


def gem(point, normal, cav):
    x, y, z = point
    # Hard facets: lit faces burn fullbright, the rest stay deep green.
    facet = math.floor((math.atan2(normal[1], normal[0])+math.pi)/(math.tau/8))+math.floor((normal[2]+1)*2)
    if (facet % 3 != 0) or normal[0] > .7:
        return mix(GLOW, (160, 255, 214), .4*max(0.0, normal[0]))
    return mix(GLOW_DARK, (40, 170, 110), max(0.0, normal[2]))


def role(name):
    for prefix, r in (('socket', 'dark'), ('cavity', 'dark'), ('tooth', 'tooth'), ('nail', 'nail'),
                      ('glow', 'glow'), ('gem', 'gem'), ('beard', 'hair'), ('crown', 'gold'), ('ring', 'gold'),
                      ('cage', 'gold'), ('chain', 'gold'), ('torc', 'gold'), ('stole', 'stole'), ('cope', 'cope'),
                      ('head', 'skin'), ('jaw', 'skin'), ('neck', 'skin'), ('hand', 'skin')):
        if name.startswith(prefix):
            return r
    return 'cloth'


def pigment(point, normal, name, cav):
    r = role(name)
    x, y, z = point
    if r == 'cloth':
        ry = _interp(ROBE_ROWS, z, 3)
        if z > 22 and abs(y) > ry+.8:
            return sleeve(point, normal, cav)
        return robe(point, normal, cav)
    if r == 'cope':
        return cope(point, normal, cav)
    if r == 'stole':
        return stole(point, normal, cav)
    if r == 'gold':
        return gold(point, normal, cav)
    if r == 'skin':
        return skin(point, normal, cav, name)
    if r == 'gem':
        return gem(point, normal, cav)
    if r == 'glow':
        return GLOW
    if r == 'dark':
        return lichlight(point, (10, 8, 8), .2)
    if r == 'tooth':
        return mix((82, 68, 42), (146, 126, 86), max(0, normal[0]))
    if r == 'nail':
        return mix((24, 18, 14), (74, 60, 48), max(0, normal[2]*.5+normal[0]*.5))
    if r == 'hair':
        c = mix((120, 116, 106), (196, 190, 176), .5+.5*math.sin(y*9+z*.5))
        return tuple(v*light(normal) for v in lichlight(point, c, .5))
    return (255, 0, 255)
