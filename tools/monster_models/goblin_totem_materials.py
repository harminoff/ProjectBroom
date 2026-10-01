"""Original dry timber, chipped bone, hemp and ochre pigments; no emission.

Uses the established goblin atlas padding and wood/cord palette family, while
giving the carved mask its own large painted face. No imported artwork.
"""
import math
from . import goblin_materials as family
from .toad_materials import png
from .rat import TILES

SIZE=1024
ROLES=('wood','mask','bone','cord','cloth','stone','dark','cut')
RECTS={name:(i%4*256+8,i//4*512+8,i%4*256+248,i//4*512+504) for i,name in enumerate(ROLES)}


def pigment(name,u,v):
    n=family.noise(int(u*241),int(v*491))
    if name in ('wood','cord','stone'):
        return family.shade(name,u,v)
    if name=='mask':
        grain=7*math.sin(u*160+math.sin(v*17)*3)
        split=-30*max(0,1-abs(math.sin(u*93+math.sin(v*11)))*19)
        base=(146,89,39);delta=grain+split+n*10+9*math.sin(u*21+v*9)
        # Ochre triangles and blackened sawtooth edge: original painted wood.
        chevron=abs(abs(u-.5)-(.13+.19*(v*4%1)))<.033 and .15<v<.86
        if chevron:base=(67,38,16)
        if u<.09 or u>.91:delta-=18
    elif name=='bone':
        base=(188,168,122)
        delta=12*math.sin(u*12+v*7)+4*math.sin(u*80+v*21)+n*10
        delta-=35*max(0,1-abs(math.sin(u*27+v*8))*20)
        delta-=18*(1-v)**3
    elif name=='cloth':
        base=(155,74,24);delta=n*12+3*math.sin(u*500)+3*math.sin(v*850)
        delta+=12*math.sin(u*19)-20*v
        if abs(u-.5)<.055 or abs(abs(u-.5)-(.08+.22*(v*3%1)))<.028:delta-=52
    elif name=='cut':
        base=(164,117,62);delta=12*math.sin(math.hypot(u-.5,(v-.5)*.6)*160)+n*12
    else:base=(24,16,9);delta=n*5
    return tuple(c+delta for c in base)


def repack(part,role,swap=False):
    x0,y0,x1,y1=RECTS[role];result=[]
    for u,v in part.uv:
        x,y=u*1024,(1-v)*1024
        r=next(r for r in TILES.values() if r[0]-.01<=x<=r[2]+.01 and r[1]-.01<=y<=r[3]+.01)
        a,b=(x-r[0])/(r[2]-r[0]),(y-r[1])/(r[3]-r[1])
        if swap:a,b=b,a
        result.append(((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE))
    part.uv=result
    return part


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                rgb=pigment(name,max(0,min(1,(x-x0)/(x1-x0))),max(0,min(1,(y-y0)/(y1-y0))))
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c))) for c in rgb)
    return png(pixels,SIZE,SIZE)
