"""Original oak, wrought iron, worn brass, cord and feather atlas; no emission.

Reuses original Project Broom palette/padding helpers. No imported artwork.
"""
import math
from . import goblin_materials as family
from .toad_materials import png
from .rat import TILES

SIZE=1024
ROLES=('wood','iron','brass','cord','feather','edge','dark','cut')
RECTS={name:(i%4*256+8,i//4*512+8,i%4*256+248,i//4*512+504) for i,name in enumerate(ROLES)}


def pigment(name,u,v):
    n=family.noise(int(u*241),int(v*491))
    if name in ('wood','cord'):return family.shade(name,u,v)
    if name=='iron':
        base=(62,67,69);delta=n*17+8*math.sin(u*30+v*11)
        if abs(math.sin(u*71+v*4))<.045:delta+=24
        if .17<u<.25 and .2<v<.8:base=(90,58,36)
    elif name=='brass':base=(155,112,48);delta=n*13+10*math.sin(u*11)+18*abs(2*u-1)**7
    elif name=='feather':base=(195,183,148);delta=n*8+10*math.sin(v*180+abs(u-.5)*28)
    elif name=='edge':base=(151,159,163);delta=n*10+13*math.sin(u*18)
    elif name=='cut':base=(147,104,57);delta=15*math.sin(math.hypot(u-.5,v-.5)*130)+n*12
    else:base=(21,23,22);delta=n*6
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
