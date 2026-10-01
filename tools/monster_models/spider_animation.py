"""Original connected spider cuticle and eight cosmetic IK leg chains."""
import hashlib
import json
import math
from . import iqm, spider_materials as materials
from .creatures import Sculpt
from .rat import ROOT, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips

SKIN=materials.SKIN
SPECS=[('root',None,(0,0,0)),('body','root',(3,0,12)),('abdomen','body',(-10,0,13))]
for i in range(4):
    x=9-i*3.5
    for side,sign in (('L',1),('R',-1)):
        points=[(x,sign*5.3,11.5),(x+(9-6*i),sign*(16.5+1.4*math.sin(i)),17),
                (x+(13-8*i),sign*(24.5-abs(i-1.5)),.55)]
        parent='body'
        for joint,point in zip(('upper','lower','end'),points):
            name=f'leg_{i}_{side}_{joint}';SPECS.append((name,parent,point));parent=name
for side,sign in (('L',1),('R',-1)):
    SPECS.append((f'fang_{side}','body',(12,sign*2.7,9.5)))
    SPECS.append((f'palp_{side}','body',(10.5,sign*4.5,10)))
RIG=Rig.from_world(SPECS)
BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('scuttle',28,35,True),('bite',20,35,False),
       ('threaten',24,35,False),('recoil',12,35,False),('death',32,35,False)]

def build_parts():
    s=Sculpt()
    # One closed continuous cuticle: abdomen, constricted pedicel, cephalothorax.
    p=s.strand('body_cuticle',[(-22,0,13,.2),(-19,0,13,5),(-12,0,13,9),
          (-5,0,12,6.5),(-2,0,11.5,2.1),(2,0,12,5.8),(7,0,12,6.8),
          (11,0,11.5,4.5),(13,0,11,.2)],'body',32,7)
    p.vertices=[(x,y,12+(z-12)*.72) for x,y,z in p.vertices]
    # Fine abdominal chevrons follow the surface, never floating effects.
    for i in range(5):
        x=-16+i*2.1
        for side,sign in (('L',1),('R',-1)):
            s.strand(f'abdomen_mark_{i}_{side}',[(x-1.2,sign*.3,19.1,.12),
                (x,sign*2.5,18.8,.13),(x+1.2,sign*4.4,18.0,.07)],'cloth',7,3)
    s.oval('mouth',(12,0,9),(1.0,2.8,.8),'dark',16,10)
    for i in range(4):
        for side,sign in (('L',1),('R',-1)):
            prefix=f'leg_{i}_{side}'
            hip,knee,foot=[REST[IDS[prefix+'_'+j]] for j in ('upper','lower','end')]
            s.strand(prefix,[(*hip,1.35),(*knee,.84),(*foot,.24)],'accent',12,6)
            s.oval(f'joint_{i}_{side}',knee,(.9,.9,.9),'dark',12,8)
            s.oval(f'coxa_{i}_{side}',hip,(1.4,1.6,1.25),'body',14,8)
            s.strand(f'claw_{i}_{side}',[(*foot,.24),(foot[0]+.5,foot[1]-sign*.25,.22,.035)],'bone',7,2)
            # A few short bristles sit on the upper cuticle and follow that bone.
            for j in range(3):
                t=.25+j*.2;c=add(hip,mul(sub(knee,hip),t))
                s.strand(f'bristle_{i}_{side}_{j}',[(c[0],c[1],c[2]+.85,.095),
                     (c[0]-.6,c[1]+sign*.45,c[2]+1.65,.015)],'cloth',5,1)
    for side,sign in (('L',1),('R',-1)):
        for j in range(4):
            y=sign*(1.2+j*1.12);x=11.6-j*.46;z=14.1+(1 if j in (1,2) else 0)
            r=.78 if j==0 else .55
            s.oval(f'socket_{side}_{j}',(x,y,z),(r*.72,r*1.17,r*1.1),'dark',16,10)
            s.oval(f'eye_{side}_{j}',(x+.35,y,z),(r*.55,r*.85,r*.84),'glow',16,10)
        s.strand(f'chelicera_{side}',[(11.7,sign*2.7,10,1.4),(14.0,sign*2.6,8.4,1.2),
                      (14.9,sign*2.3,7.3,.65)],'accent',16,5)
        s.strand(f'fang_{side}',[(14.4,sign*2.5,7.8,.62),(15.6,sign*2.2,6.4,.46),
                      (15.1,sign*.95,5.8,.035)],'bone',12,5)
        s.strand(f'palp_{side}',[(10.5,sign*4.5,10,.8),(14,sign*6.0,8.4,.62),
                      (17,sign*5.6,6.9,.43),(17.3,sign*4.7,6.3,.12)],'accent',12,5)
        s.strand(f'spinneret_{side}',[(-20,sign*1.3,10,.5),(-22.3,sign*1.6,9.8,.15)],'cloth',9,3)
    return materials.repack(s.parts)

def weights(part,v,uv):
    n=part.name
    if n=='body_cuticle':return RIG.chain_weights(v,[IDS['abdomen'],IDS['body']])
    if n.startswith(('abdomen','spinneret')):return [(IDS['abdomen'],1)]
    if n.startswith(('fang','chelicera')):return [(IDS['fang_'+n.split('_')[1]],1)]
    if n.startswith('palp'):return [(IDS[n],1)]
    if n.startswith('leg_'):return RIG.chain_weights(v,[IDS[n+'_'+j] for j in ('upper','lower','end')])
    if n.startswith(('joint','claw','bristle')):
        bits=n.split('_');joint={'joint':'lower','claw':'end','bristle':'upper'}[bits[0]]
        return [(IDS[f'leg_{bits[1]}_{bits[2]}_{joint}'],1)]
    return [(IDS['body'],1)]

def geometry():return assemble(build_parts(),weights)

def solve_leg(prefix,target,rotations):
    ids=[IDS[prefix+'_'+j] for j in ('upper','lower','end')]
    hip,knee,foot=[REST[i] for i in ids];a,b=math.dist(hip,knee),math.dist(knee,foot)
    direction=unit(sub(target,hip));distance=math.dist(target,hip)
    if not abs(a-b)<distance<a+b:raise ValueError(('unreachable',prefix,target,distance,a,b))
    along=(a*a-b*b+distance*distance)/(2*distance)
    pole=sub(knee,hip);bend=unit(sub(pole,mul(direction,sum(x*y for x,y in zip(pole,direction)))))
    newknee=add(hip,add(mul(direction,along),mul(bend,math.sqrt(max(0,a*a-along*along)))))
    upper=between(sub(knee,hip),sub(newknee,hip));lower=between(sub(foot,knee),sub(target,newknee))
    rotations[ids[0]]=upper;rotations[ids[1]]=qmul(inverse(upper),lower);rotations[ids[2]]=inverse(lower)

def gait(i,side,t):
    phase=(t+(i%2)*.5+(0 if side=='L' else .5))%1
    if phase<.65:return (2-4*phase/.65,0,0)
    u=(phase-.65)/.35
    return (-2+4*u*u*(3-2*u),0,2.8*math.sin(math.pi*u)**2)

_CONTACT_GEOMETRY=None

def pose(name,t):
    rotations=[(0,0,0,1) for _ in BONES];shifts=[(0,0,0) for _ in BONES]
    pulse=math.sin(math.pi*t)**2;phase=math.tau*t
    d=min(1,t/.88);d=d*d*(3-2*d) if name=='death' else 0
    shift=(0,0,.12*math.sin(phase)) if name=='idle' else (0,.25*math.sin(phase),0) if name=='scuttle' else (0,0,-2*d) if d else ((2.2 if name=='bite' else -1.3 if name=='recoil' else .5)*pulse,0,(1.6 if name=='threaten' else .4)*pulse)
    shifts[IDS['body']]=shift
    rotations[IDS['abdomen']]=axis((1,0,0),math.radians(8*d if d else .6*math.sin(phase) if name=='idle' else 0))
    for i in range(4):
        for side,sign in (('L',1),('R',-1)):
            prefix=f'leg_{i}_{side}';foot=REST[IDS[prefix+'_end']]
            offset=gait(i,side,t) if name=='scuttle' else (-foot[0]*.22*d,-sign*6*d,2*d)
            solve_leg(prefix,sub(add(foot,offset),shift),rotations)
    for side,sign in (('L',1),('R',-1)):
        rotations[IDS['fang_'+side]]=axis((0,1,0),math.radians(22*pulse if name=='bite' else 13*d))
        rotations[IDS['palp_'+side]]=axis((0,0,1),math.radians(sign*(14*pulse if name=='threaten' else -22*d if d else 2*math.sin(phase))))
    frame=[(*add(local,shifts[i]),*rotations[i],1,1,1) for i,(_,_,local) in enumerate(BONES)]
    if d:
        # A dead spider rolls onto its dorsal cuticle, legs curled above it.
        # Ground contact follows the rolling surface, not gameplay collision.
        frame[0]=(0,0,0,*axis((1,0,0),math.radians(174*d)),1,1,1)
        global _CONTACT_GEOMETRY
        if _CONTACT_GEOMETRY is None:
            _,vv,_,_,_,ww=geometry();_CONTACT_GEOMETRY=(vv,ww)
        points=RIG.deform(*_CONTACT_GEOMETRY,frame)
        row=list(frame[0]);row[2]=.1-min(v[2] for v in points);frame[0]=tuple(row)
    return frame

def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)

def build():
    skin=materials.texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    supplemental={}
    for name,data in materials.surface_maps().items():
        (ROOT/'mod/BrogueDoom'/name).write_bytes(data);supplemental[name]=hashlib.sha256(data).hexdigest()
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_spider',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/21_spider.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M21',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),surfaceMapSha256=supplemental,
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/spider/spider-animated.blend')
    out=ROOT/'assets/monsters/spider';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest

if __name__=='__main__':print(json.dumps(build(),indent=2))
