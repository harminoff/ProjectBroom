"""Original segmented centipede; anatomy and cosmetic IK, never game logic."""
import hashlib
import json
import math
from . import iqm, centipede_materials as materials
from .creatures import Sculpt
from .rat import ROOT, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips

SKIN=materials.SKIN
SEGMENTS=15
SPECS=[('root',None,(0,0,0)),('head','root',(17,0,6.3))]
for i in range(SEGMENTS):
    x=12-2.25*i
    SPECS.append((f'segment_{i}','root',(x,0,5.5)))
    width=4.2*(.76+.24*math.sin(math.pi*(i+1)/16))
    for side,sign in (('L',1),('R',-1)):
        prefix=f'leg_{i}_{side}'
        points=[(x,sign*width,5.1),(x-(3.5 if i==14 else 1.1),sign*(width+4.0),6.3),
                (x-(7 if i==14 else 2.4),sign*(width+8.2),.38)]
        parent=f'segment_{i}'
        for joint,point in zip(('upper','lower','end'),points):
            name=prefix+'_'+joint;SPECS.append((name,parent,point));parent=name
for side,sign in (('L',1),('R',-1)):
    parent='head'
    for i,point in enumerate(((20,sign*2.8,7.4),(24,sign*5.2,9.2),(28,sign*7.4,10.6))):
        name=f'antenna_{side}_{i}';SPECS.append((name,parent,point));parent=name
    SPECS.append((f'forcipule_{side}','head',(17.9,sign*3.5,4.8)))
RIG=Rig.from_world(SPECS)
BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CHAIN=[IDS['head']]+[IDS[f'segment_{i}'] for i in range(SEGMENTS)]
CLIPS=[('idle',40,20,True),('scuttle',28,35,True),('prick',18,35,False),
       ('sting',22,35,False),('recoil',12,35,False),('death',30,35,False)]


def build_parts():
    s=Sculpt()
    # Closed continuous soft cuticle, tapering at both ends. Plates are real
    # separate exoskeletal parts rather than disconnected surrogate body balls.
    points=[(-22,0,5.5,.35),(-19.5,0,5.5,3.45),(-10,0,5.5,4.0),
            (2,0,5.5,4.25),(12,0,5.5,4.0),(17,0,6.3,3.6),(20.8,0,6.3,.3)]
    p=s.strand('flexible_body',points,'cloth',24,5)
    p.vertices=[(x,y,5.5+(z-5.5)*.55) for x,y,z in p.vertices]
    for i in range(SEGMENTS):
        x=12-2.25*i;w=4.5*(.76+.24*math.sin(math.pi*(i+1)/16))
        s.oval(f'plate_{i}',(x,0,6.1),(1.68,w,2.25),'body',20,10)
        # Curved copper edge of the tergite; modeled narrow raised cuticle.
        rim=[(x-.75,w*.96*math.cos(a),6.0+2.13*math.sin(a),.14)
             for a in [math.pi*j/16 for j in range(17)]]
        s.strand(f'rim_{i}',rim,'accent',6,1)
        # Subtle median groove and two lateral spiracles per segment.
        s.strand(f'groove_{i}',[(x-1.1,0,8.1,.065),(x+.9,0,8.15,.065)],'dark',5,2)
        for side,sign in (('L',1),('R',-1)):
            prefix=f'leg_{i}_{side}'
            hip,knee,foot=[REST[IDS[prefix+'_'+j]] for j in ('upper','lower','end')]
            s.strand(prefix,[(*hip,.65),(*knee,.48),(*foot,.17)],'accent',10,4)
            s.oval(f'coxa_{i}_{side}',hip,(.7,.9,.65),'body',12,7)
            s.oval(f'joint_{i}_{side}',knee,(.47,.5,.46),'dark',10,6)
            s.strand(f'claw_{i}_{side}',[(*foot,.19),(foot[0]-.48,foot[1]+sign*.3,.18,.025)],'bone',6,2)
            s.oval(f'spiracle_{i}_{side}',(x,sign*w*.98,6.1),(.42,.10,.23),'dark',10,6)
    s.oval('head_shield',(17,0,6.3),(4.7,4.5,2.7),'body',28,16)
    s.oval('head_clypeus',(20.3,0,5.7),(1.35,2.75,1.0),'accent',20,10)
    s.strand('head_suture',[(13.3,0,8.0,.075),(16,0,9.03,.075),(19.5,0,8.13,.07)],'dark',6,3)
    s.strand('head_mouth',[(20.8,-1.6,4.85,.15),(21.35,0,4.6,.18),(20.8,1.6,4.85,.15)],'dark',8,3)
    for side,sign in (('L',1),('R',-1)):
        # Grouped simple eyes, inset into the lateral cephalic shield; no glow.
        for j in range(4):
            x=17.6+(j%2)*.65;z=7.15+(j//2)*.49
            s.oval(f'head_ocellus_{side}_{j}',(x,sign*3.98,z),(.37,.24,.32),'dark',12,8)
        points=[REST[IDS[f'antenna_{side}_{j}']] for j in range(3)]
        s.strand(f'antenna_{side}',[(*p,r) for p,r in zip(points,(.43,.25,.04))],'accent',10,7,ribbed=True)
        # Each sickle is a continuous tapered jaw appendage curved inward.
        s.strand(f'forcipule_{side}',[(17.9,sign*3.5,4.8,.9),(20.9,sign*4.0,3.9,.8),
                     (23.0,sign*2.7,3.8,.44),(22.9,sign*.7,4.1,.04)],'bone',12,5)
        s.strand('head_palp_'+side,[(20.6,sign*1.5,4.7,.3),(22,sign*1.6,4.3,.22),
                                  (22.5,sign*.9,4.45,.035)],'accent',8,3)
    return materials.repack(s.parts)


def weights(part,v,uv):
    n=part.name
    if n=='flexible_body':return RIG.chain_weights(v,CHAIN)
    if n.startswith('head'):return [(IDS['head'],1)]
    if n.startswith('antenna'):return RIG.chain_weights(v,[IDS[n+'_'+str(i)] for i in range(3)])
    if n.startswith('forcipule'):return [(IDS[n],1)]
    bits=n.split('_');i=int(bits[1])
    if bits[0]=='leg':return RIG.chain_weights(v,[IDS[n+'_'+j] for j in ('upper','lower','end')])
    if bits[0] in ('claw','joint'):
        return [(IDS[f'leg_{i}_{bits[2]}_'+('end' if bits[0]=='claw' else 'lower')],1)]
    return [(IDS[f'segment_{i}'],1)]


def geometry():return assemble(build_parts(),weights)


def solve_leg(prefix,target,rotations):
    ids=[IDS[prefix+'_'+j] for j in ('upper','lower','end')]
    hip,knee,foot=[REST[i] for i in ids]
    a,b=math.dist(hip,knee),math.dist(knee,foot)
    direction=unit(sub(target,hip));distance=min(a+b-.001,max(abs(a-b)+.001,math.dist(target,hip)))
    along=(a*a-b*b+distance*distance)/(2*distance)
    pole=sub(knee,hip);bend=unit(sub(pole,mul(direction,sum(x*y for x,y in zip(pole,direction)))))
    newknee=add(hip,add(mul(direction,along),mul(bend,math.sqrt(max(0,a*a-along*along)))))
    upper=between(sub(knee,hip),sub(newknee,hip));lower=between(sub(foot,knee),sub(target,newknee))
    rotations[ids[0]]=upper;rotations[ids[1]]=qmul(inverse(upper),lower);rotations[ids[2]]=inverse(lower)


def gait(i,side,t):
    phase=(t-i*.12+(0 if side=='L' else .5))%1
    # 65% stance with constant backward foot speed, 35% lifted recovery.
    if phase<.65:return (1.65-3.3*phase/.65,0,0)
    u=(phase-.65)/.35
    return (-1.65+3.3*(u*u*(3-2*u)),0,1.7*math.sin(math.pi*u)**2)


def pose(name,t):
    rotations=[(0,0,0,1) for _ in BONES];shifts=[(0,0,0) for _ in BONES]
    phase=math.tau*t;pulse=math.sin(math.pi*t)**2
    death=min(1,t/.85);death=death*death*(3-2*death) if name=='death' else 0
    for i in range(SEGMENTS):
        wave=math.sin(phase-i*.7)
        shift=(0,.28*wave if name=='scuttle' else 0,0)
        if name in ('prick','sting','recoil'):
            lead=math.exp(-i*.27)
            shift=((1.5 if name=='prick' else 2.2 if name=='sting' else -1)*pulse*lead,0,0)
        if death:shift=(0,2.3*math.sin(i*.2)*death,-2.65*death)
        shifts[IDS[f'segment_{i}']]=shift
        for side,sign in (('L',1),('R',-1)):
            prefix=f'leg_{i}_{side}';foot=REST[IDS[prefix+'_end']]
            offset=gait(i,side,t) if name=='scuttle' else (0,sign*.85*death,0)
            # Segment-local target cancels body translation to plant support feet.
            solve_leg(prefix,sub(add(foot,offset),shift),rotations)
    headshift=(0,0,0)
    if name=='idle':rotations[IDS['head']]=axis((0,1,0),math.radians(.45*math.sin(phase)))
    elif name=='scuttle':headshift=(0,.25*math.sin(phase+.6),0)
    elif name in ('prick','sting'):
        headshift=((2 if name=='prick' else 3.0)*pulse,0,(.6 if name=='prick' else 1.4)*pulse)
        rotations[IDS['head']]=axis((0,1,0),math.radians((5 if name=='prick' else -7)*pulse))
    elif name=='recoil':headshift=(-1.3*pulse,0,.4*pulse)
    elif name=='death':headshift=(0,0,-2.7*death)
    elif name!='idle':raise ValueError(name)
    shifts[IDS['head']]=headshift
    for side,sign in (('L',1),('R',-1)):
        for j in range(3):
            degrees=(3.4*math.sin(phase+j*.5+sign) if name in ('idle','scuttle') else 5*pulse)*sign
            rotations[IDS[f'antenna_{side}_{j}']]=axis((0,0,1),math.radians(degrees))
        rotations[IDS[f'forcipule_{side}']]=axis((0,0,1),math.radians(sign*(17*pulse if name in ('prick','sting') else 1.0*math.sin(phase) if name=='idle' else 0)))
    return [(*add(local,shifts[i]),*rotations[i],1,1,1) for i,(_,_,local) in enumerate(BONES)]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)


def build():
    skin=materials.texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    supplemental={}
    for name,data in materials.surface_maps().items():
        (ROOT/'mod/BrogueDoom'/name).write_bytes(data);supplemental[name]=hashlib.sha256(data).hexdigest()
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_centipede',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/17_centipede.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M17',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),surfaceMapSha256=supplemental,
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/centipede/centipede-animated.blend')
    out=ROOT/'assets/monsters/centipede';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest

if __name__=='__main__':print(json.dumps(build(),indent=2))
