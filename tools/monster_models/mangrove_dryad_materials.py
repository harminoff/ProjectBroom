"""Original mangrove dryad atlas: pale tan bark (Brogue's tanColor), khaki vines, sparse olive leaves.

Brogue's mangrove dryad is drawn in tanColor {80,67,15}. The body is one baked-light bark ramp:
`mangrove_dryad_animation.bake_skin` computes a per-vertex shade (key, fill, crevice occlusion,
bark grain, knot holes and fissures) and a small moss amount; the 'skin' tile is a 2-D ramp
addressed by (moss, shade). Near-black brown sits in the fissures, weathered khaki in the
mid-tones and pale straw on the ridges, so the figure separates from grey walls and a brown floor
by value while staying tan. Vines, leaves, moss, splinters, eye glow and the dark mouth/socket
tiles are separate. Original Project Broom art.
"""
import math
from .toad_materials import png
from .flame_turret_materials import noise, mix, ramp

SIZE=512
RECTS={'skin':(4,4,260,260),'vine':(268,4,396,260),'leaf':(404,4,500,132),'moss':(404,140,500,268),
       'splinter':(4,268,68,396),'dark':(76,268,140,396),'glow':(148,268,212,396)}


def uv(role,a,b):
    x0,y0,x1,y1=RECTS[role]
    a=min(1,max(0,a));b=min(1,max(0,b))
    return ((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE)


BARK_STOPS=[(0,(16,11,4)),(.14,(40,29,11)),(.32,(80,61,26)),(.52,(126,102,52)),(.74,(170,144,88)),(.9,(200,178,122)),(1,(224,206,152))]
MOSS=(84,92,34)


def pigment(role,a,b,px,py):
    n=noise(px*.3,py*.3,51);g=noise(px*1.3,py*.16,52)
    if role=='skin':
        # a: 0..0.88 bark streak coordinate (bands of pale plates and dark cracks), above 0.9 moss; b: baked shade 0..1
        if a>.9:
            return mix(ramp(BARK_STOPS,b*.8),MOSS,.35+.6*min(1,(a-.9)*10))
        s1=noise(a*22,.5,82);s2=noise(a*80,1.5,83);streak=.55*s1+.45*s2
        crack=max(0,1-abs(s1-.5)/.05)
        v=b*(.72+.95*streak)*(1-.55*crack*min(1,b*1.6))
        return ramp(BARK_STOPS,v+(n-.5)*.03)
    if role=='vine':
        # a around the vine, b along it (base 0 to tip 1): fibrous khaki cords with dark twist lines.
        c=.5+.5*math.cos(math.tau*a*2)
        col=ramp([(0,(30,24,8)),(.4,(74,62,24)),(.75,(112,98,44)),(1,(150,134,72))],c*.7+g*.35+(1-b)*.06)
        return mix(col,(30,24,8),max(0,1-abs(math.sin(math.tau*(a*3+b*4)))*7)*.4)
    if role=='leaf':
        vein=max(0,1-abs(a-.5)/.06)
        col=ramp([(0,(48,60,18)),(.5,(94,110,38)),(1,(146,152,70))],b*.6+g*.3+.1)
        return mix(col,(170,164,96),vein*.6)
    if role=='moss':
        return ramp([(0,(44,54,16)),(.5,(80,92,32)),(1,(124,132,58))],n*.8+(1-b)*.2)
    if role=='splinter':
        return ramp([(0,(120,100,64)),(.6,(206,188,140)),(1,(238,224,178))],.2+b*.8+(n-.5)*.1)
    if role=='dark':
        return mix((6,4,2),(30,20,9),g*.8)
    if role=='glow':
        return ramp([(0,(255,150,24)),(.5,(255,196,60)),(1,(255,232,140))],.3+g*.5)
    raise KeyError(role)


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-4,y1+4):
            for x in range(x0-4,x1+4):
                if not (0<=x<SIZE and 0<=y<SIZE):continue
                rgb=pigment(name,max(0,min(1,(x-x0)/(x1-x0))),max(0,min(1,(y-y0)/(y1-y0))),x,y)
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c))) for c in rgb)
    return png(pixels,SIZE,SIZE)
