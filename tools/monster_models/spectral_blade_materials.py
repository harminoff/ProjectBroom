"""Original spectral blade atlas: indigo-to-electric-blue conjured steel of light.

The runtime draws this skin additively and fullbright (`shaders/spectral-blade-glow.fp`),
so value is opacity: near-black reads as empty air and near-white as the hottest
light. The blade paints a white-hot cutting edge, a violet spine, a see-through
fuller carrying flickering rune dashes, and a white tip. Wisps, the base knot,
motes and the attack-only slash and whirl trails use their own regions. Colours
interpret Brogue's `spectralBladeColor` (15, 15, 60 with a dancing blue component)
and its violet-blue conjured light; they are identity cues, not new game facts.
Original Project Broom art; no imported artwork.
"""
import math
from .toad_materials import png
from .flame_turret_materials import noise, mix, ramp

SIZE=512
RECTS={'blade':(8,8,200,504),'wisp':(216,8,312,504),'trail':(328,8,504,200),
       'ring':(328,216,504,344),'core':(328,360,408,504),'mote':(424,360,504,432),'aura':(424,448,504,504)}


def uv(role,a,b):
    """Local (a, b) in [0,1] (b downwards in the image) to IQM/Blender UV."""
    x0,y0,x1,y1=RECTS[role]
    a=min(1,max(0,a));b=min(1,max(0,b))
    return ((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE)


def _smooth(e0,e1,x):
    q=min(1,max(0,(x-e0)/(e1-e0)));return q*q*(3-2*q)


def _hash(i,j,seed=7):
    h=(i*374761393+j*668265263+seed*1442695041)&0xffffffff
    h=((h^(h>>13))*1274126177)&0xffffffff
    return ((h^(h>>16))&0xffff)/65535.0


DEEP=(22,30,128);ELECTRIC=(58,104,255);BRIGHT=(160,208,255);WHITE=(236,246,255);VIOLET=(112,64,236)


def rune(a,b):
    """Flickering conjured dashes along the fuller: 3x5 glyph cells from a fixed hash."""
    if not (.08<b<.84 and .15<a<.35):return 0.0
    cell=int((b-.08)/.052);v=((b-.08)/.052-cell);u=(a-.15)/.2
    if not (.12<v<.88 and .12<u<.88):return 0.0
    gx=min(2,int((u-.12)/.76*3));gy=min(4,int((v-.12)/.76*5))
    return 1.0 if _hash(cell*7+gx,gy)>.48 or gx==1 and gy in (0,4) else 0.0


def pigment(role,a,b,px,py):
    n=noise(px*.6,py*.6,11);f=noise(px*1.9,py*.35,12)
    if role=='blade':
        # a: spine (0) to cutting edge (1); b: base (0) to tip (1).
        c=ramp([(0,VIOLET),(.1,(92,84,246)),(.2,DEEP),(.36,DEEP),(.44,(120,170,255)),(.5,ELECTRIC),
                (.78,(104,160,255)),(.9,BRIGHT),(1,WHITE)],a)
        # See-through fuller: darkest where the groove bottoms out.
        c=mix(c,(10,12,58),max(0,1-abs(a-.25)/.1)*.75)
        c=mix(c,(190,226,255),rune(a,b)*(.72+.28*f))
        c=mix(c,(150,196,255),max(0,1-abs(a-.44)/.025)*.7)  # ridge line
        c=mix(c,WHITE,_smooth(.84,.99,b)*.8)                # white-hot point
        c=mix(c,BRIGHT,_smooth(.08,0,b)*.6)                 # emerging from the knot
        return mix(c,(30,40,140),max(0,.36-n)*.5)
    if role=='wisp':
        # a along (root 0 to tail 1), b around the flattened ribbon.
        core=1-min(1,abs(math.sin(b*math.pi*2))*1.1)
        c=ramp([(0,BRIGHT),(.25,ELECTRIC),(.6,(84,44,214)),(.85,(34,12,96)),(1,(6,3,20))],a+(f-.5)*.18)
        return mix(c,(200,226,255),core*.4*(1-a))
    if role=='trail':
        # a along the arc (old 0 to blade 1), b around (0/1 outer rim, .5 inner).
        rim=1-min(1,abs(b-.5)*2);outer=1-rim
        streak=.75+.25*math.sin(py*.35+f*4)
        head=_smooth(0,.9,a)**1.4
        c=ramp([(0,(4,4,24)),(.3,(34,40,170)),(.6,ELECTRIC),(.85,BRIGHT),(1,WHITE)],head*(.35+.65*outer**1.6)*streak+.02)
        return c
    if role=='ring':
        rim=abs(b-.5)*2
        streak=.72+.28*math.sin(px*.5+f*5)
        return ramp([(0,(6,8,40)),(.35,(40,56,200)),(.7,ELECTRIC),(.9,BRIGHT),(1,WHITE)],rim**1.3*streak)
    if role=='core':
        return mix(WHITE,(120,170,255),abs(b-.5)*1.4+(n-.5)*.2)
    if role=='aura':
        # Dim envelope: value is faint, the shader rim turns its outline into a halo.
        c=mix((20,30,104),(8,10,44),abs(a-.5)*1.2)
        return mix(c,(30,44,140),_smooth(.9,1,b)*.5)
    if role=='mote':
        return mix(WHITE,BRIGHT,abs(a-.5)+abs(b-.5))
    raise KeyError(role)


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                rgb=pigment(name,max(0,min(1,(x-x0)/(x1-x0))),max(0,min(1,(y-y0)/(y1-y0))),x,y)
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c))) for c in rgb)
    return png(pixels,SIZE,SIZE)
