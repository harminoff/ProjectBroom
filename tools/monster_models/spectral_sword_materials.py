"""Original spectral sword atlas: a crimson projected image of a broadsword.

The runtime draws this skin additively and fullbright (`shaders/spectral-sword-glow.fp`),
so value is opacity. The main image has pink-white edges, a dark see-through fuller
with one bright engraved line, and fine horizontal projection scanlines that mark
it as an image rather than steel (the spectral blade uses runes instead). The two
echo images reuse the same paint at 55% and 34% value, so they read as fainter
after-images. Colours interpret Brogue's `spectralImageColor` (13, 0, 0 with a
dancing red component) and its crimson weapon-image light; identity cues only.
Original Project Broom art; no imported artwork.
"""
import math
from .toad_materials import png
from .flame_turret_materials import noise, mix, ramp

SIZE=512
RECTS={'blade':(8,8,136,504),'guard':(152,8,248,120),'grip':(152,136,248,248),'pommel':(152,264,248,376),
       'gem':(152,392,248,504),'e1_blade':(264,8,328,504),'e1_hilt':(344,8,376,504),
       'e2_blade':(392,8,456,504),'e2_hilt':(472,8,504,504)}
ECHO={'e1':.55,'e2':.34}


def uv(role,a,b):
    """Local (a, b) in [0,1] (b downwards in the image) to IQM/Blender UV."""
    x0,y0,x1,y1=RECTS[role]
    a=min(1,max(0,a));b=min(1,max(0,b))
    return ((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE)


def _smooth(e0,e1,x):
    q=min(1,max(0,(x-e0)/(e1-e0)));return q*q*(3-2*q)


def scan(b,lines):
    """Projection scanlines: the image is made of faint horizontal bands."""
    return .84+.16*math.cos(b*lines*math.tau)


def blade(a,b,n):
    d=abs(a-.5)*2
    c=ramp([(0,(150,16,42)),(.05,(84,6,24)),(.2,(92,8,28)),(.3,(226,52,76)),(.55,(206,36,62)),
            (.78,(244,104,118)),(.92,(255,178,182)),(1,(255,232,228))],d)
    c=mix(c,(255,168,176),max(0,1-d/.035)*.85)        # engraved centre line
    c=mix(c,(255,236,232),_smooth(.86,.99,b)*.75)      # bright point
    c=mix(c,(255,140,150),_smooth(.06,0,b)*.5)         # glow where it leaves the guard
    c=tuple(x*scan(b,64) for x in c)
    return mix(c,(120,10,34),max(0,.34-n)*.35)


def hilt(role,a,b,n):
    # a: along the piece, b: painted shade (0 faces the viewer's key, 1 turned away).
    if role=='gem':
        return mix((255,236,236),(214,24,70),min(1,math.hypot(a-.35,b-.3)*2.2))
    if role=='grip':
        wrap=.5+.5*math.cos(a*math.tau*9)
        c=mix((68,4,20),(196,38,62),wrap**.7)
    else:
        c=ramp([(0,(255,176,180)),(.35,(232,72,94)),(.7,(150,18,44)),(1,(84,6,26))],b+(n-.5)*.12)
    return tuple(x*scan(a,18) for x in c)


def pigment(role,a,b,px,py):
    n=noise(px*.6,py*.6,21)
    if role=='blade':return blade(a,b,n)
    if role in ('guard','grip','pommel','gem'):return hilt(role,a,b,n)
    k=ECHO[role[:2]]
    if role.endswith('blade'):return tuple(x*k for x in blade(a,b,n))
    return tuple(x*k for x in hilt('guard',a,b,n))


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                rgb=pigment(name,max(0,min(1,(x-x0)/(x1-x0))),max(0,min(1,(y-y0)/(y1-y0))),x,y)
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c))) for c in rgb)
    return png(pixels,SIZE,SIZE)
