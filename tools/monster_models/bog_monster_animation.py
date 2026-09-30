"""Original pale swamp tentacles. All motion is presentation-only."""
import hashlib,json,math,struct,zlib
from . import iqm,connected_skin
from .rat import ROOT,Part,add,sub,mul,unit,cross,ellipsoid
from .skeletal import Rig,axis,assemble,sample_clips
SKIN='graphics/BRGBOG.png'
# Presentation-only centered-cell clearance; rig and skin use the same units.
ANATOMY_SCALE=.93
CLIPS=[('idle',40,20,True),('drift',28,35,True),('squeeze',22,35,False),('coil',26,35,False),('recoil',14,35,False),('collapse',32,35,False)]

def center(arm,t):
    angle=math.tau*arm/6+.20+(0.7 if arm%2 else -.55)*t*t
    radial=5+21*math.sin(t*math.pi*.93)
    height=(25,17,22,15,24,19)[arm]
    return (radial*math.cos(angle),radial*math.sin(angle),5+height*math.sin(t*math.pi*.79)**2)

SPECS=[('root',None,(0,0,0)),('mantle','root',(0,0,5))]
for arm in range(6):
    for j in range(6):SPECS.append((f'arm_{arm}_{j}','mantle' if j==0 else f'arm_{arm}_{j-1}',center(arm,j/5)))
RIG=Rig.from_world([(n,p,mul(c,ANATOMY_SCALE)) for n,p,c in SPECS]);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}

def build_parts():
    mantle=ellipsoid('mantle',(0,0,4.8),(11,10,4.7),segments=32,rings=16)
    mantle.uv=[(.03+.14*u,v) for u,v in mantle.uv]
    parts=[mantle]
    for arm in range(6):
        p=Part(f'tentacle_{arm}');rings=65;sides=20
        for i in range(rings):
            t=i/(rings-1);c=center(arm,t)
            tangent=unit(sub(center(arm,min(1,t+.001)),center(arm,max(0,t-.001))))
            side=unit(cross(tangent,(0,0,1)));other=unit(cross(tangent,side))
            radius=.40+3.7*(1-t)**.85
            for j in range(sides+1):
                a=math.tau*(j%sides)/sides
                # Continuous fleshy underside corrugation, not detached suction beads.
                rib=.55*math.sin(t*math.tau*18)**2*max(0,-math.sin(a))**4*math.sin(math.pi*t)
                r=radius+rib
                point=add(c,add(mul(side,math.cos(a)*r),mul(other,math.sin(a)*r*.98)))
                p.vertices.append(point);p.uv.append((.02+.96*t,.02+.96*j/sides))
        for i in range(rings-1):
            for j in range(sides):
                a=i*(sides+1)+j;p.faces.append((a,a+1,a+sides+2,a+sides+1))
        for end,reverse in ((0,True),(rings-1,False)):
            index=len(p.vertices);p.vertices.append(center(arm,end/(rings-1)));p.uv.append((.02+.96*end/(rings-1),.5))
            for j in range(sides):
                a=end*(sides+1)+j;p.faces.append((index,a+1,a) if reverse else (index,a,a+1))
        parts.append(p)
    for p in parts:p.vertices=[mul(v,ANATOMY_SCALE) for v in p.vertices]
    return parts

def weights(part,v,u):
    if part.name=='mantle':return [(IDS['mantle'],1)]
    arm=int(part.name.split('_')[1]);return RIG.chain_weights(v,[IDS[f'arm_{arm}_{j}'] for j in range(6)])

def geometry():
    parts=connected_skin.attach('bog_monster',build_parts(),weights)
    # A rest-height pigment coordinate runs continuously through the fused
    # mantle/arm junction; source-part UV islands cannot cut off the mud stain.
    for part in parts:
        part.uv=[(max(.01,min(.99,(v[2]-.1*ANATOMY_SCALE)/(32*ANATOMY_SCALE))),u[1]) for v,u in zip(part.vertices,part.uv)]
    return assemble(parts,weights)

def pose(name,t):
    rot=[(0,0,0,1) for _ in BONES];shift=[(0,0,0) for _ in BONES]
    pulse=math.sin(math.pi*t)**2
    settle=min(1,t/.85);settle=settle*settle*(3-2*settle)
    for arm in range(6):
        a=math.tau*arm/6+.2
        for j in range(6):
            phase=math.tau*t-arm*.85-j*.5
            bend=(1.5 if name=='idle' else 3)*math.sin(phase) if name in ('idle','drift') else 0
            if name in ('squeeze','coil'):bend=(7 if name=='squeeze' else 10)*pulse*(.4+j/6)
            if name=='recoil':bend=-5*pulse
            if name=='collapse':bend=8*settle
            rot[IDS[f'arm_{arm}_{j}']]=axis((-math.sin(a),math.cos(a),0),math.radians(bend))
    if name=='recoil':shift[IDS['mantle']]=(-.6*pulse,0,0)
    return [(*add(local,shift[i]),*rot[i],1,1,1) for i,(_,_,local) in enumerate(BONES)]
def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)

def texture_bytes():
    size=1024;pixels=bytearray()
    for y in range(size):
        pixels.append(0)
        for x in range(size):
            t=x/(size-1);v=y/(size-1);mud=max(0,1-t/.45)**1.0
            underside=max(0,-math.sin(v*math.tau))**3
            vein=math.exp(-((math.sin(t*38+math.sin(v*21)*2))/.08)**2)*8
            grain=3*math.sin(x*1.73+y*.37)*math.sin(y*1.21-x*.53)
            mottling=13*math.sin(t*53+math.sin(v*37))*math.sin(v*59)
            crease=underside*8*math.sin(t*math.tau*18)**8
            base=(210-129*mud,191-126*mud-27*underside,176-127*mud-19*underside)
            tissue=13*math.cos(v*math.tau)+6*math.cos(v*math.tau*3+t*19)
            pixels.extend(max(0,min(255,round(c+grain+mottling-vein-crease+tissue))) for c in base)
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(pixels),9))+chunk(b'IEND',b'')

def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_bog_monster',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/19_bog_monster.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M19',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],poseBounds=bounds,authoringSource='assets/monsters/bog_monster/bog-monster-animated.blend')
    out=ROOT/'assets/monsters/bog_monster';out.mkdir(exist_ok=True);(out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':print(json.dumps(build(),indent=2))
