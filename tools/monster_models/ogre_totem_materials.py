"""Original weathered timber, old bone, greenstone, leather and bronze atlas."""
import math
from .rat import TILES
from .toad_materials import png
from .goblin_materials import noise

SIZE=1024
ROLES=('timber','bone','bronze','leather','stone','tablet','incision','endgrain')
RECTS={name:(i%4*256+8,i//4*512+8,i%4*256+248,i//4*512+504) for i,name in enumerate(ROLES)}


def pigment(name,u,v):
    n=noise(int(u*479),int(v*983))
    if name=='timber':
        bend=u+.022*math.sin(v*13)+.015*math.sin(v*31+u*9)
        grain=5*math.sin(bend*190)+3*math.sin(bend*371)
        split=-26*max(0,1-abs(math.sin(bend*79+v*2))*16)
        erosion=10*math.sin(u*19+v*8)*math.sin(v*14)
        delta=grain+split+erosion+n*12
        base=(77,67,49)
    elif name=='bone':
        delta=10*math.sin(u*17+v*9)+3*math.sin(u*160+v*17)+n*10
        delta-=21*max(0,1-abs(math.sin(u*47+v*3))*14)
        delta-=13*(math.sin(v*8+u*4)**2)
        base=(171,156,117)
    elif name=='bronze':
        patina=max(0,math.sin(u*23+math.sin(v*29))*math.sin(v*41))
        delta=n*17+8*math.sin(u*97+v*51)
        base=(116-49*patina,90-9*patina,45+17*patina)
    elif name=='leather':
        delta=n*13+4*math.sin(u*151)*math.sin(v*311)-12*math.sin(v*9)**2
        base=(81,47,25)
        delta+=12*(abs(u-.5)*2)**8
    elif name=='tablet':
        vein=math.sin(u*21+2*math.sin(v*13))+math.sin(u*49-v*17)*.3
        delta=12*math.sin(u*13+v*11)*math.sin(v*21)+n*8
        delta+=18*max(0,1-abs(vein)*13)
        base=(66,100,81)
        if min(u,1-u,v,1-v)<.05:delta+=11
    elif name=='stone':
        delta=12*math.sin(u*23)*math.sin(v*19)+noise(int(u*37),int(v*49))*15+n*12
        base=(97,91,72)
    elif name=='endgrain':
        rings=math.hypot((u-.47)*1.3,v-.54)
        delta=9*math.sin(rings*130)+n*13
        base=(108,84,51)
    else:base=(20,27,22);delta=n*5
    return tuple(max(0,min(255,round(c+delta))) for c in base)


def repack(part,role,swap=False):
    x0,y0,x1,y1=RECTS[role];uv=[]
    for u,v in part.uv:
        x,y=u*1024,(1-v)*1024
        r=next(r for r in TILES.values() if r[0]-.01<=x<=r[2]+.01 and r[1]-.01<=y<=r[3]+.01)
        a,b=(x-r[0])/(r[2]-r[0]),(y-r[1])/(r[3]-r[1])
        if swap:a,b=b,a
        uv.append(((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE))
    part.uv=uv;return part


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(pigment(name,max(0,min(1,(x-x0)/(x1-x0))),max(0,min(1,(y-y0)/(y1-y0)))))
    return png(pixels,SIZE,SIZE)
