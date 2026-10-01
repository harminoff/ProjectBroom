"""Original veinous gas bladder. Presentation only; Brogue owns the gas burst."""
import hashlib
import json
import math
import struct
import zlib
from . import iqm
from .rat import ROOT, add, sub, ellipsoid
from .skeletal import Rig, axis, assemble, sample_clips

SKIN = 'graphics/BRGBLOAT.png'
CENTER = (0, 0, 32)
RADII = (14, 13, 16)
DIRECTIONS = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
SPECS = [('root',None,(0,0,0))]
for name, direction in zip(('front','back','left','right','crown','base'),DIRECTIONS):
    SPECS.append((name,'root',add(CENTER,tuple(c*8 for c in direction))))
RIG=Rig.from_world(SPECS)
BONES,REST=RIG.bones,RIG.rest
CLIPS=[('idle',40,20,True),('drift',24,35,True),('bump',12,35,False),
       ('bump_alt',14,35,False),('recoil',10,35,False),('collapse',18,35,False)]


def geometry():
    body=ellipsoid('bloat_membrane',CENTER,RADII,segments=48,rings=32)
    for i,p in enumerate(body.vertices):
        x,y,z=(p[a]-CENTER[a] for a in range(3))
        theta=math.atan2(y/RADII[1],x/RADII[0])
        latitude=math.asin(max(-1,min(1,z/RADII[2])))
        # Continuous slight lobing and a pinched base, not separate body balls.
        lobes=1+.035*math.cos(theta*5+latitude)*math.cos(latitude)**2
        taper=1-.22*max(0,-z/RADII[2])**3
        body.vertices[i]=(x*lobes*taper,y*lobes*taper,z+CENTER[2])
        u=((i-1)%49)/48 if 0<i<len(body.vertices)-1 else .5
        body.uv[i]=(u,.02+.96*(latitude/math.pi+.5))
    return assemble([body],weights)


def weights(part,p,uv):
    normalized=[(p[a]-CENTER[a])/RADII[a] for a in range(3)]
    amounts=[abs(c)**2 for c in normalized]
    total=sum(amounts)
    if total<1e-12:return [(0,1)]
    return [(1+a*2+(0 if normalized[a]>=0 else 1),value/total)
            for a,value in enumerate(amounts) if value>1e-12]


def pose(name,t):
    phase=t*math.tau
    shifts=[(0,0,0) for _ in BONES]
    rotations=[(0,0,0,1) for _ in BONES]
    pulse=math.sin(math.pi*t)**2
    for i,d in enumerate(DIRECTIONS,1):
        expansion=.55*math.sin(phase+(i//2)*.35) if name in ('idle','drift') else .8*pulse
        shifts[i]=tuple(c*expansion for c in d)
    if name in ('idle','drift'):
        shifts[0]=(0,0,1.2*math.sin(phase))
        rotations[0]=axis((0,1,0),math.radians((2 if name=='idle' else 6)*math.sin(phase)))
    elif name in ('bump','bump_alt'):
        shifts[0]=(2.3*pulse,(1.4*pulse if name=='bump_alt' else 0),0)
        rotations[0]=axis((0,1,0),math.radians(5*pulse))
    elif name=='recoil':
        shifts[0]=(-1.6*pulse,0,.5*pulse)
        shifts[1]=(-2.5*pulse,0,0)
    elif name=='collapse':
        settle=max(0,min(1,(t-.12)/.72));settle=settle*settle*(3-2*settle)
        # Translate shell bones inward/down; never animate unsupported bone scale.
        for i,d in enumerate(DIRECTIONS,1):
            shifts[i]=tuple(-d[a]*(8 if a<2 else 13)*settle for a in range(3))
        shifts[0]=(0,0,-23*settle)
        rotations[0]=axis((0,0,1),math.radians(15*settle))
    return [(*add(local,shifts[i]),*rotations[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)


def texture_bytes():
    size=512;pixels=bytearray()
    for y in range(size):
        pixels.append(0)
        v=max(0,min(1,(1-y/(size-1)-.02)/.96))
        for x in range(size):
            u=x/(size-1);theta=math.tau*u
            mottling=7*math.sin(theta*9+v*23)*math.sin(theta*4-v*37)
            mottling+=4*math.sin(theta*23+v*91)
            trunk=abs(math.sin(theta*6+.55*math.sin(v*19)+.20*math.sin(theta*3+v*27)))
            branch=abs(math.sin(theta*13+v*29+.65*math.sin(theta*5-v*13)))
            cap=math.sin(math.pi*v)**.5
            vein=max(math.exp(-(trunk/.055)**2),.58*math.exp(-(branch/.04)**2))*cap
            halo=max(math.exp(-(trunk/.14)**2),.25*math.exp(-(branch/.10)**2))*cap
            light=13*math.sin(math.pi*v)+6*math.cos(theta*2)
            base=(166+light+mottling,96+light+mottling,174+light+mottling)
            color=[c-halo*12-vein*dark for c,dark in zip(base,(56,52,45))]
            pixels.extend(max(0,min(255,round(c))) for c in color)
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(pixels),9))+chunk(b'IEND',b'')


def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_bloat',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/06_bloat.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M06',format='IQM v2',
        runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),
        skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/bloat/bloat-animated.blend')
    out=ROOT/'assets/monsters/bloat';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    result=build();print({k:result[k] for k in ('sha256','dimensions','vertices','triangles')})
