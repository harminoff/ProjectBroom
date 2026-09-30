"""Original ifrit atlas: desaturated-violet storm-djinn, worn gold, dark-spined steel, smoke and embers.

Brogue's ifrit ("A whirling desert storm given human shape, the ifrit's twin scimitars
flicker in the darkness and [its] eyes burn with otherworldly zeal") is drawn in
ifritColor, a deep violet-blue. The body is painted with a baked-light ramp: every skin
vertex gets its lighting (key, fill, crevice occlusion and an ember under-glow on
downward-facing surfaces) computed from the geometry in `ifrit_animation.geometry()`, and
the 'skin' tile is only a 2-D ramp addressed by (under-glow, shade). Near-black indigo
sits in the crevices, desaturated violet in the mid-tones, lavender only on the top
highlights, and a warm ember tint on undersides, so form comes from value, not from a
glossy saturated fill. Smoke, gold, horn, hair, cloth, ivory and steel have their own
tiles. Texels inside the ember key (shaders/ifrit-embers.fp, `ember_key()` here) render
fullbright: eyes, the ember-forged edge strips, the crown flame, burst flecks and the
storm's ember sparks. Everything else stays lit. Original Project Broom art.
"""
import math
from .toad_materials import png
from .flame_turret_materials import noise, mix, ramp

SIZE=512
RECTS={'skin':(4,4,260,260),'smoke':(268,4,468,260),'steel':(4,268,132,460),'gold':(140,268,204,396),
       'horn':(212,268,276,396),'hair':(284,268,348,396),'cloth':(356,268,420,396),'ivory':(428,268,492,396),
       'core':(140,404,204,500),'fire':(212,404,340,500)}


def uv(role,a,b):
    x0,y0,x1,y1=RECTS[role]
    a=min(1,max(0,a));b=min(1,max(0,b))
    return ((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE)


def ember_key(rgb):
    """Same soft key as the shader: hot orange/yellow with low blue."""
    r,g,b=(c/255 for c in rgb)
    def sm(e0,e1,x):
        q=min(1,max(0,(x-e0)/(e1-e0)));return q*q*(3-2*q)
    return sm(.80,.90,r)*sm(.22,.30,g)*(1-sm(.80,.90,g))*(1-sm(.30,.40,b))


EMBER=(255,142,26);EMBER_HOT=(255,206,58);WARM=(158,66,36)
SKIN_STOPS=[(0,(7,4,16)),(.16,(24,15,42)),(.36,(52,40,76)),(.58,(70,57,92)),(.8,(100,85,124)),(1,(140,126,162))]


def _hash(i,j,seed=5):
    h=(i*374761393+j*668265263+seed*1442695041)&0xffffffff
    h=((h^(h>>13))*1274126177)&0xffffffff
    return ((h^(h>>16))&0xffff)/65535.0


def pigment(role,a,b,px,py):
    n=noise(px*.3,py*.3,31);f=noise(px*.12,py*1.1,32);g=noise(px*1.1,py*.15,33)
    if role=='skin':
        # a: ember under-glow 0..1, b: baked shade 0 (occluded) .. 1 (lit). Coarse mottling only.
        shade=b+(n-.5)*.05
        col=ramp(SKIN_STOPS,shade)
        glow=a*(1-.55*shade)
        return mix(col,WARM,min(1,glow*.62))
    if role=='smoke':
        # a: around a thin ribbon (0 and .5 are its broad edges), b: waist 0 to wisp tip 1.
        rim=abs(math.cos(math.tau*a))
        streak=noise(px*.35,py*.06,35)
        core=(1-rim)**1.2
        col=ramp([(0,(16,10,30)),(.35,(38,29,60)),(.65,(68,56,96)),(1,(122,106,152))],rim*.22+b*.5+streak*.5-core*.3)
        col=mix(col,(18,12,32),max(0,.28-b)*1.5*core)
        cell=_hash(int(px*.5),int(py*.5),36)
        if cell>.94 and b>.05:                      # sparse ember sparks in the eddies
            col=mix(col,EMBER,min(1,(cell-.94)*40))
        return col
    if role=='core':
        col=mix((10,6,22),(30,20,52),g*.9)
        if _hash(int(px*.5),int(py*.5),37)>.955:col=mix(col,EMBER,.95)
        return col
    if role=='steel':
        # a: 0 = cutting edge, .5 = darker spine; b: hilt 0 to tip 1. Blued spine, bright polished edge bevel.
        w=abs(a-.5)*2
        col=ramp([(0,(36,38,56)),(.35,(70,74,98)),(.7,(150,158,182)),(.92,(206,214,232)),(1,(232,238,248))],w+(n-.5)*.10)
        col=mix(col,(24,26,40),max(0,1-abs(a-.5)/.1)*.65)                          # dark spine
        col=mix(col,(30,32,50),max(0,1-abs(a-.3)/.045)*.55)                        # fuller groove
        col=mix(col,(190,120,64),max(0,1-min(a,1-a)/.05)*.45*b)                   # heat-tint along the edge, not keyed
        return col
    if role=='gold':
        c=math.cos(math.tau*a);s=.5+.5*c
        col=ramp([(0,(44,26,6)),(.4,(116,80,18)),(.75,(176,132,34)),(1,(198,168,76))],s*.85+(n-.5)*.25)
        return mix(col,(40,24,6),max(0,1-abs(b-.5)/.05)*.5)
    if role=='horn':
        c=math.cos(math.tau*a)
        return ramp([(0,(22,16,30)),(.5,(64,54,62)),(.85,(148,134,116)),(1,(198,186,160))],b*.9+(n-.5)*.15+(c-.5)*.06)
    if role=='hair':
        return mix((8,5,18),(58,46,90),max(0,math.cos(math.tau*a))*.5+g*.35+b*.1)
    if role=='cloth':
        fold=.5+.5*math.sin(math.tau*(a*2+g*.5))
        col=ramp([(0,(58,8,22)),(.5,(116,22,40)),(1,(170,50,62))],fold*.7+(n-.5)*.2+.1*math.cos(math.tau*a))
        return mix(col,(196,160,110),max(0,b-.9)*8)
    if role=='ivory':
        return ramp([(0,(120,104,86)),(.6,(196,184,158)),(1,(222,214,192))],.15+b*.85+(n-.5)*.1)
    if role=='fire':
        return ramp([(0,(255,116,16)),(.5,EMBER),(1,EMBER_HOT)],b*.9+(n-.5)*.2)
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
