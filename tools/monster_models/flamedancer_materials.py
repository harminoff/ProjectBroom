"""Original flamedancer atlas: an infernal being of white-hot fire (presentation only).

Brogue's flamedancer is drawn as a white 'F', carries the flamedancerCoronaColor
light, is fiery and immune to fire, keeps its distance and casts fire; its text calls
it "an elemental creature from another plane of existence" that "burns with such
intensity that [it] is painful to behold". This atlas paints fire only: a white-hot
core and head with dark eye slits, ribbon tongues that cool from yellow to deep red at
their tips, and small ember sparks. The runtime shader (shaders/flamedancer-fire.fp)
draws every texel fullbright with a view-angle rim and a slow rising shimmer, so
value carries the form. Original Project Broom art; no imported artwork.
"""
import math
from .toad_materials import png
from .flame_turret_materials import noise, mix, ramp

SIZE=512
RECTS={'flame':(8,8,264,504),'core':(280,8,376,248),'head':(392,8,504,248),
       'spark':(280,264,376,360),'ember':(392,264,504,504),'rim':(280,376,376,504)}


def uv(role,a,b):
    x0,y0,x1,y1=RECTS[role]
    a=min(1,max(0,a));b=min(1,max(0,b))
    return ((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE)


WHITE=(255,250,226);YELLOW=(255,214,84);ORANGE=(255,140,26);RED=(224,64,14);DEEP=(140,22,8);BLACKRED=(72,8,4)


def pigment(role,a,b,px,py):
    n=noise(px*.55,py*.55,21);f=noise(px*.35,py*1.7,22);g=noise(px*1.3,py*.4,23)
    if role=='flame':
        # a: root 0 to tip 1; b: around the ribbon, 0 and .5 are its broad edges.
        edge=abs(math.cos(b*math.tau))
        core=1-edge**1.6
        heat=(1-a)*.78+core*.34+(f-.5)*.36-(1-core)*.10
        c=ramp([(0,BLACKRED),(.16,DEEP),(.34,RED),(.52,ORANGE),(.74,YELLOW),(1,WHITE)],heat)
        # Licks of hotter fire streaming along the tongue.
        streak=max(0,math.sin(b*math.tau*2+a*9+g*6))**5
        return mix(c,YELLOW,streak*.35*(1-a))
    if role=='core':
        c=ramp([(0,RED),(.3,ORANGE),(.55,YELLOW),(.8,ORANGE),(1,RED)],a+(n-.5)*.3)
        return c
    if role=='head':
        # a: around the head (.5 faces +X), b: top 0 to bottom 1.
        u=a-.5;v=b-.5
        c=ramp([(0,WHITE),(.22,WHITE),(.5,YELLOW),(.8,ORANGE),(1,RED)],abs(u)*1.9+max(0,v+.05)*1.1+(n-.5)*.25)
        for side in (-1,1):
            # Slanted dark eye slit, outer ends raised: the only dark note on the white-hot face.
            ex=u-side*.085;ey=v+.02+side*ex*1.25
            d=(ex/.085)**2+(ey/.04)**2
            if d<1:return mix(BLACKRED,(150,26,6),d**2)
            if d<2.4:c=mix(c,ORANGE,(2.4-d)*.6)
        return c
    if role=='spark':
        return mix(WHITE,YELLOW,abs(a-.5)+abs(b-.5))
    if role=='ember':
        return mix(YELLOW,ORANGE,b*.8+(n-.5)*.3)
    if role=='rim':
        return mix(ORANGE,RED,a)
    raise KeyError(role)


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                if not (0<=x<SIZE and 0<=y<SIZE):continue
                rgb=pigment(name,max(0,min(1,(x-x0)/(x1-x0))),max(0,min(1,(y-y0)/(y1-y0))),x,y)
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c))) for c in rgb)
    return png(pixels,SIZE,SIZE)
