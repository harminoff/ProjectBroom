"""Original crystal, iron, brass, ceramic, sigil and copper atlas; no emission.

Reuses original Project Broom palette/padding helpers. No imported artwork.
"""
import math
from . import goblin_materials as family
from .toad_materials import png
from .rat import TILES

SIZE=1024
ROLES=('crystal','iron','brass','ceramic','sigil','edge','dark','copper')
RECTS={name:(i%4*256+8,i//4*512+8,i%4*256+248,i//4*512+504) for i,name in enumerate(ROLES)}


def pigment(name,u,v):
    n=family.noise(int(u*241),int(v*491))
    if name=='crystal':base=(56,132,220);delta=n*9+30*math.sin(u*math.pi)+45*v+24*abs(2*u-1)**7
    elif name=='iron':base=(44,49,57);delta=n*15+6*math.sin(u*44+v*13)
    elif name=='brass':base=(158,119,55);delta=n*14+16*abs(2*u-1)**7
    elif name=='ceramic':base=(177,174,155);delta=n*9+12*math.sin(v*64)
    elif name=='sigil':base=(132,205,248);delta=n*5+10*math.sin(v*22)
    elif name=='edge':base=(124,142,155);delta=n*12+18*math.sin(u*9)
    elif name=='copper':base=(153,83,46);delta=n*14+14*math.sin(v*38)
    else:base=(17,24,35);delta=n*6
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
