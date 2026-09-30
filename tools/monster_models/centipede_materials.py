"""Original deterministic aubergine/copper chitin; no emissive toxin fiction."""
import math
from .rat import TILES
from .toad_materials import png, noise
SIZE=1024
SKIN='graphics/BRGCENT.png'
ROLES=('shell','membrane','copper','ivory','dark','head')
RECTS={n:(i%3*340+10,i//3*512+10,i%3*340+330,i//3*512+502) for i,n in enumerate(ROLES)}

def role(name):
    if name=='flexible_body':return 'membrane'
    if name.startswith(('head_ocellus','head_suture','head_mouth','groove','joint','spiracle')):return 'dark'
    if name.startswith(('forcipule','claw')):return 'ivory'
    if name.startswith(('antenna','rim','leg','head_palp')):return 'copper'
    if name.startswith('head'):return 'head'
    return 'shell'

def repack(parts):
    for p in parts:
        x0,y0,x1,y1=RECTS[role(p.name)];mapped=[]
        for u,v in p.uv:
            x,y=u*SIZE,(1-v)*SIZE
            old=next(r for r in TILES.values() if r[0]-.01<=x<=r[2]+.01 and r[1]-.01<=y<=r[3]+.01)
            a,b=(x-old[0])/(old[2]-old[0]),(y-old[1])/(old[3]-old[1])
            mapped.append(((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE))
        p.uv=mapped
    return parts

def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        base=dict(shell=(91,50,105),membrane=(52,35,46),copper=(151,95,56),ivory=(169,137,87),dark=(16,12,20),head=(108,53,109))[name]
        for y in range(y0-10,y1+10):
            for x in range(x0-10,x1+10):
                u=max(0,min(1,(x-x0)/(x1-x0)));v=max(0,min(1,(y-y0)/(y1-y0)))
                delta=5*noise(x,y)+4*math.sin(u*38+math.sin(v*31))*math.sin(v*21)
                if name in ('shell','head'):
                    delta+=13*math.sin(math.pi*v)**2-11*max(0,math.sin(u*170+math.sin(v*35))-.75)
                if name=='copper':delta+=6*math.sin(u*82)
                if name=='dark':delta*=.15
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c+delta))) for c in base)
    return png(pixels)

def surface_maps():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        level=92 if name in ('shell','head') else 115 if name=='dark' else 48
        for y in range(y0-10,y1+10):
            for x in range(x0-10,x1+10):
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes((round(level+8*noise(x,y)),)*3)
    return {'graphics/BRGCENT_N.png':png(bytes((128,128,255))*16,4,4),'graphics/BRGCENT_S.png':png(pixels)}
