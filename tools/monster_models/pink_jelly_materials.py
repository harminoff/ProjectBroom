"""Original seamless rose/coral gel skin and wetness, with no emission."""
import math
from .toad_materials import png

SKIN='graphics/BRGPINKJ.png'
SIZE=1024
POCKETS=[((i*.381966+.08)%1,.24+.61*((i*7)%17)/16,
          .014+.010*((i*3)%7)/6,.022+.022*((i*5)%9)/8)
         for i in range(18)]


def pigment(u,v):
    angle=math.tau*u
    # Periodic angular functions meet exactly at the UV meridian. Polar
    # attenuation avoids pinwheel artifacts at the surface's welded poles.
    cap=math.sin(math.pi*v)**.65
    fold=math.sin(angle*5+v*13+1.2*math.sin(angle*2-v*7))
    cloud=math.sin(angle*3+v*17)*math.sin(angle*7-v*9)
    filament=abs(math.sin(angle*7+v*31+.9*math.sin(angle*3-v*17)))
    vein=math.exp(-(filament/.16)**2)*cap
    # Soft inclusions vary in size. They are pigmentation, not separate organs.
    inclusion=max(0,math.sin(angle*17+v*53)*math.sin(angle*11-v*37)-.45)**2*cap
    grain=math.sin(angle*71+v*187)*math.sin(angle*43-v*211)*cap
    # Wide cloudy density gradients remain legible at dungeon distance. The
    # warm upper skin and wine-dark folds suggest thick gel without emission.
    light=-18+42*v+cap*(25*cloud+12*fold+2*grain)
    dark=vein*8+inclusion*90
    pocket_light=0
    for pu,pv,ru,rv in POCKETS:
        du=((u-pu+.5)%1-.5)/ru;dv=(v-pv)/rv
        radius=math.hypot(du,dv)
        if radius<2.2:
            dark+=22*math.exp(-radius*radius*2)
            pocket_light+=22*math.exp(-((radius-.9)/.23)**2)*max(.1,min(1,(dv-du+1)/2))
    light+=pocket_light
    base=(179,66,95)
    return tuple(max(0,min(255,round(c+light-dark*d)))
                 for c,d in zip(base,(.66,1.0,.82)))


def texture_bytes():
    pixels=bytearray()
    for y in range(SIZE):
        v=1-y/(SIZE-1)
        for x in range(SIZE):pixels.extend(pigment(x/(SIZE-1),v))
    return png(pixels,SIZE,SIZE)


def surface_maps():
    pixels=bytearray()
    for y in range(SIZE):
        v=1-y/(SIZE-1)
        for x in range(SIZE):
            a=math.tau*x/(SIZE-1)
            level=round(113+20*math.sin(math.pi*v)+13*math.sin(a*5+v*17)*math.sin(math.pi*v))
            pixels.extend((level,)*3)
    return {'graphics/BRGPINKJ_N.png':png(bytes((128,128,255))*16,4,4),
            'graphics/BRGPINKJ_S.png':png(pixels,SIZE,SIZE)}
