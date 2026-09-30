"""Original goblin fur, leathery skin, bark, cord and chipped stone diffuse atlas."""
import math
import struct
import zlib
from .rat import TILES as OLD_TILES

SIZE=1024
ROLES=('fur','mane','face','hand','wood','stone','cord','dark','hide')
RECTS={name:(i%4*256+8,i//4*341+8,i%4*256+248,i//4*341+333) for i,name in enumerate(ROLES)}


def role(name):
    if name.startswith('wrap'):return 'hide'
    if name.startswith('spear_lashing'):return 'cord'
    if name=='spear_stone':return 'stone'
    if name.startswith('spear'):return 'wood'
    if name.startswith('head_eye_iris'):return 'cord'
    if name.startswith(('head_eye','head_nostril','jaw_mouth')):return 'dark'
    if name.startswith(('head_face','head_muzzle','head_nose','head_ear_inner','jaw_lower')):return 'face'
    if name.startswith(('hand_','foot_')):return 'hand'
    if name.startswith(('coat_','head_hair')):return 'mane'
    if name.startswith('head_'):return 'face'
    return 'fur'


def repack(parts):
    for part in parts:
        x0,y0,x1,y1=RECTS[role(part.name)];mapped=[]
        for u,v in part.uv:
            x,y=u*1024,(1-v)*1024
            r=next(r for r in OLD_TILES.values() if r[0]-.01<=x<=r[2]+.01 and r[1]-.01<=y<=r[3]+.01)
            a,b=(x-r[0])/(r[2]-r[0]),(y-r[1])/(r[3]-r[1])
            if part.name in ('torso','neck') or part.name.startswith(('arm_','leg_','spear_shaft')):a,b=b,a
            mapped.append(((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE))
        part.uv=mapped
    return parts


def noise(x,y):return (((x*1619+y*31337)^(x*y*6971))&255)/255-.5


def shade(name,u,v):
    n=noise(int(u*240),int(v*496))
    if name=='mane':
        # Broad irregular tufts remain visible after mipmapping; fine strands
        # provide close-up texture without relying on alpha fur cards.
        bend=u+.018*math.sin(v*25)
        row=math.floor(v*34);col=math.floor(bend*27)
        strand=math.sin(bend*290+2*math.sin(v*31))
        coarse=noise(col,row)*10
        taper=math.sin(math.pi*(v*34%1))
        clump=-8*max(0,1-abs((bend*27%1)-.5)*7)*taper
        delta=coarse+clump+strand*2+n*6+4*math.sin(v*9)
        base=(48,37,25)
    elif name in ('fur','face','hand'):
        # Irregular pores and broad dirt read across mip levels without the
        # former horizontal stripe pattern following every anatomical tube.
        folds=math.sin(v*39+3*math.sin(u*19)+math.sin(u*47))
        creases=-5*max(0,1-abs(folds)*18)
        grime=-24*max(0,math.sin(u*13+math.sin(v*9))*math.sin(v*17))
        mottling=7*math.sin(u*21+math.sin(v*18))*math.sin(v*15)
        pores=-5*max(0,noise(int(u*133),int(v*179))-.3)*5
        delta=creases+grime+mottling+pores+n*7
        base=(105,88,66) if name=='face' else (88,73,52)
        if name=='face':
            # Cranial ring UV: front repeats at both U edges, Z increases V.
            facefront=abs(2*u-1)**6
            orbital=-20*math.exp(-((v-.52)/.075)**2)
            cheek=8*math.exp(-((v-.38)/.09)**2)
            delta+=facefront*(orbital+cheek)
        if name=='hand':base=(94,75,54)
    elif name=='wood':
        grain=math.sin(u*150+math.sin(v*19)*3)
        split=-21*max(0,1-abs(math.sin(u*83+math.sin(v*8)))*18)
        delta=grain*12+split+n*9;base=(93,66,35)
    elif name=='stone':
        facet=noise(math.floor(u*9),math.floor(v*13))*32
        fracture=-17*max(0,1-abs(math.sin(u*33+v*17))*22)
        delta=facet+fracture+n*10;base=(120,126,113)
    elif name=='cord':
        delta=9*math.sin(u*130+v*80)+n*8;base=(133,113,75)
    elif name=='hide':
        fold=9*math.cos(u*math.tau*8+.3)*(0.3+.7*v)
        wear=10*math.exp(-((v-.04)/.045)**2)+7*math.exp(-((v-.93)/.07)**2)
        delta=n*9+fold+wear-12*v+4*math.sin(u*43+math.sin(v*19))
        base=(66,43,26)
    else:delta=n*3;base=(16,12,8)
    return tuple(c+delta for c in base)


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                u=max(0,min(1,(x-x0)/(x1-x0)));v=max(0,min(1,(y-y0)/(y1-y0)))
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c))) for c in shade(name,u,v))
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    raw=b''.join(b'\0'+pixels[y*SIZE*3:(y+1)*SIZE*3] for y in range(SIZE))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',SIZE,SIZE,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
