"""Original brown reptile diffuse atlas. CC-BY-SA-4.0, Project Broom contributors.

No external images or simulation randomness. UV regions have eight-pixel gutters.
The static BRGM02 reference is deliberately separate from this skeletal skin.
"""
import math, struct, zlib
from .rat import TILES as OLD_TILES

SIZE=1024
ROLES=('scales','ventral','wood','leather','eye','dark','bone','crest')
RECTS={name:(i%4*256+8,i//4*512+8,i%4*256+248,i//4*512+504) for i,name in enumerate(ROLES)}
SKIN='graphics/BRGKOB.png'


def role(name):
    if name.startswith('club_binding'):return 'leather'
    if name.startswith('club'):return 'wood'
    if name.startswith('head_eye'):return 'eye'
    if name.startswith(('head_pupil','head_nostril','jaw_mouth')):return 'dark'
    if 'tooth' in name or 'claw' in name:return 'bone'
    if name.startswith(('head_crest','head_frill','torso_scale')):return 'crest'
    if name in ('torso','neck'):return 'ventral'
    if name=='jaw_lower':return 'bone'
    return 'scales'


def repack(parts):
    for part in parts:
        target=role(part.name);x0,y0,x1,y1=RECTS[target];mapped=[]
        for u,v in part.uv:
            x,y=u*1024,(1-v)*1024
            source=next(r for r in OLD_TILES.values() if r[0]-.01<=x<=r[2]+.01 and r[1]-.01<=y<=r[3]+.01)
            a,b=(x-source[0])/(source[2]-source[0]),(y-source[1])/(source[3]-source[1])
            if part.name in ('torso','neck') or part.name.startswith(('arm_','leg_')) or (target=='wood' and '_knot_' not in part.name):a,b=b,a
            mapped.append(((x0+a*(x1-x0))/SIZE,1-(y0+b*(y1-y0))/SIZE))
        part.uv=mapped
    return parts


def noise(x,y):return (((x*1619+y*31337)^(x*y*6971))&255)/255-.5


def shade(name,u,v):
    n=noise(int(u*240),int(v*496))
    if name in ('scales','ventral','crest'):
        row=math.floor(v*30);cx=u*18+(row%2)*.5;col=math.floor(cx)
        a,b=(cx%1-.5)*2,(v*30%1-.5)*2
        # Rounded overlapping scales with narrow dark seams and a raised lip.
        radius=math.sqrt(a*a+(b*.84)**2)
        lip=max(0,1-abs(radius-.78)*9)
        seam=max(0,min(1,(radius-.82)*5))
        delta=7*noise(col,row)+3*n+9*(1-radius)+8*lip*(.5-b)-23*seam
        base=(113,77,43) if name!='crest' else (75,43,24)
        if name=='ventral':
            blend=max(0,min(1,(.23-abs(u-.5))*18))
            scute=12*math.sin((v*20%1)*math.pi)-20*max(0,1-(v*20%1)*12)
            belly=(181+scute,143+scute,91+scute)
            return tuple((c+delta)*(1-blend)+d*blend for c,d in zip(base,belly))
        return tuple(c+delta for c in base)
    if name=='wood':
        grain=math.sin(u*160+math.sin(v*13)*2)+.4*math.sin(u*390+v*9)
        split=-16 if abs(math.sin(u*81+math.sin(v*9)))<.06 else 0
        return tuple(c+grain*7+split+n*6 for c in (83,45,22))
    if name=='leather':
        grain=n*15+3*math.sin(u*85)*math.sin(v*91)
        return tuple(c+grain for c in (57,30,18))
    if name=='eye':return (224+n*12,155+n*9,37+n*6)
    if name=='dark':return (9+n*3,7+n*2,5+n*2)
    if name=='bone':return tuple(c+8*v+n*3 for c in (199,176,125))
    raise ValueError(name)


def texture_bytes():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                u=max(0,min(1,(x-x0)/(x1-x0)));v=max(0,min(1,(y-y0)/(y1-y0)))
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(max(0,min(255,round(c))) for c in shade(name,u,v))
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    raw=b''.join(b'\0'+pixels[y*SIZE*3:(y+1)*SIZE*3] for y in range(SIZE))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',SIZE,SIZE,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
