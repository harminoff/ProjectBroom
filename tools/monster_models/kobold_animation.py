"""Original lizardlike kobold rig and clips, using the shared skeletal pipeline."""
import hashlib
import json
import math
from . import iqm, kobold_materials
from .creatures import Sculpt
from .rat import ROOT, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips

SPECS=[('root',None,(0,0,0)),('pelvis','root',(0,0,16)),
       ('spine','pelvis',(0,0,24)),('neck','spine',(0,0,30)),
       ('head','neck',(1,0,33)),('jaw','head',(3,0,31))]
for side,sign in (('L',1),('R',-1)):
    for limb,parent,points in (
        ('arm','spine',[(0,sign*5,26),(2,sign*7,21),(4,sign*7,17)]),
        ('leg','pelvis',[(0,sign*3,16),(2.8,sign*3,9),(2,sign*3,2)])):
        for joint,point in zip(('upper','lower','end'),points):
            name=f'{limb}_{side}_{joint}';SPECS.append((name,parent,point));parent=name
parent='pelvis'
for i,point in enumerate(((-3,0,16),(-8,0,12),(-12,1,12),(-14,3,15),(-13,4,18))):
    name=f'tail_{i}';SPECS.append((name,parent,point));parent=name
SPECS.append(('club','arm_R_end',(4,-7,17)))
RIG=Rig.from_world(SPECS); BONES,REST=RIG.bones,RIG.rest
IDS={name:i for i,(name,p,point) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('walk',16,35,True),('attack',18,35,False),
       ('attack_alt',20,35,False),('hit',10,35,False),('death',26,35,False)]


def build_parts():
    s=Sculpt()
    s.oval('pelvis',(0,0,16),(3.4,4.1,3.3))
    s.strand('torso',[(0,0,16,3.2),(-.4,0,21,3.3),(0,0,26,4.2),(0,0,28,3)],sides=20,samples=3)
    s.strand('neck',[(0,0,27,2.2),(1,0,32,2)],sides=16)
    s.oval('head_cranium',(1,0,33.5),(3.1,3.3,3.6),seg=24,rings=14)
    s.oval('head_muzzle',(4.3,0,32.2),(3.5,2.35,1.65),seg=24,rings=12)
    s.oval('jaw_mouth',(4.9,0,31.05),(2.65,1.8,.2),'dark')
    s.oval('jaw_lower',(4.6,0,30.7),(2.8,1.9,.65))
    for sign in (-1,1):
        s.oval(f'head_brow_{sign}',(3,sign*2.45,34.6),(1.65,.85,.55))
        s.oval(f'head_eye_{sign}',(3.7,sign*2.5,34),(1,.43,.76),'accent',16,10)
        s.oval(f'head_pupil_{sign}',(4.05,sign*2.83,34),(.18,.14,.57),'dark',12,8)
        s.oval(f'head_nostril_{sign}',(7.35,sign*1,32.6),(.2,.23,.16),'dark',10,6)
        s.strand(f'head_frill_{sign}',[(0,sign*2.7,34,1.1),(-1.4,sign*4.7,36,.08)],sides=10)
        for i in range(4):
            s.strand(f'head_tooth_{sign}_{i}',[(3.6+i*.8,sign*1.7,31.3,.16),(3.6+i*.8,sign*1.7,30.7,.03)],'bone',6,1)
    for i in range(5):
        s.oval(f'head_crest_{i}',(-1.6+i*.65,0,36.2+math.sin(i*.65)*.5),(.65,.48,.65),'accent',10,7)
    for side,sign in (('L',1),('R',-1)):
        # Deltoid volume overlaps the ribcage and upper arm before skin fusion.
        s.oval(f'shoulder_{side}',(0,sign*3.8,26),(2.4,2.6,2.4))
        for limb in ('arm','leg'):
            points=[REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
            radii=(2.0,1.45,.95) if limb=='arm' else (2.5,1.7,1.1)
            s.strand(f'{limb}_{side}',[(*p,r) for p,r in zip(points,radii)],sides=14,samples=4)
        s.oval(f'foot_{side}',(2.8,sign*3,1.2),(3,1.65,1.2))
        for i in range(3):
            s.strand(f'foot_{side}_claw{i}',[(4.8,sign*3+(i-1)*.85,.9,.3),(6.2,sign*3+(i-1)*.85,.45,.03)],'bone',6,2)
        s.oval(f'hand_{side}_palm',(2.9,sign*7,17.2),(1.15,1.2,2.0))
        for i in range(4):
            z=15.65+i*1.05
            s.strand(f'hand_{side}_finger{i}',[(3,sign*7-1.05,z,.43),(4.8,sign*7-1.1,z,.4),(5.2,sign*7,z,.35),(4.5,sign*7+.95,z,.25)],sides=8,samples=3)
        s.strand(f'hand_{side}_thumb',[(2.4,sign*7+.6,18.4,.6),(3.6,sign*7+1.4,19,.5),(4.7,sign*7+.85,18.2,.25)],sides=8)
    s.strand('tail',[( *REST[IDS[f'tail_{i}']],r) for i,r in enumerate((1.7,1.2,.85,.5,.07))],sides=12,samples=5)
    s.weapon('club',(4,-7,17),'club')
    for i in range(4):
        s.strand(f'club_binding{i}',[(3.95,-7,14+i*.9,.79),(3.95,-7,14.3+i*.9,.79)],'cloth',12,1)
    # Small geometric dorsal scales survive the existing padded diffuse atlas.
    for z in (19,22,25):
        for y in (-2,0,2):
            s.oval(f'torso_scale_{z}_{y}',(-3.05,y,z),(.42,.75,.75),'accent',8,6)
    return kobold_materials.repack(s.parts)


def weights(part,v,uv):
    name=part.name
    if name.startswith('shoulder_'):
        t=max(0,min(1,(abs(v[1])-2)/3))
        return [(IDS['spine'],1-t),(IDS['arm_'+name[-1]+'_upper'],t)]
    if name.startswith('club'): return [(IDS['club'],1)]
    if name.startswith('head'): return [(IDS['head'],1)]
    if name.startswith('jaw'): return [(IDS['jaw'],1)]
    if name.startswith('hand_'): return [(IDS['arm_'+name.split('_')[1]+'_end'],1)]
    if name.startswith('foot_'): return [(IDS['leg_'+name.split('_')[1]+'_end'],1)]
    if name.startswith(('arm_','leg_')):
        return RIG.chain_weights(v,[IDS[name+'_'+j] for j in ('upper','lower','end')])
    if name=='tail': return RIG.chain_weights(v,[IDS[f'tail_{i}'] for i in range(5)])
    if name=='neck': return RIG.chain_weights(v,[IDS['spine'],IDS['neck'],IDS['head']])
    if name=='pelvis': return [(IDS['pelvis'],1)]
    return RIG.chain_weights(v,[IDS['pelvis'],IDS['spine'],IDS['neck']])


def solve_leg(side,target,rotations):
    ids=[IDS[f'leg_{side}_{j}'] for j in ('upper','lower','end')]
    hip,knee,foot=[REST[i] for i in ids];a=math.dist(hip,knee);b=math.dist(knee,foot)
    direction=unit(sub(target,hip));distance=min(a+b-.001,max(abs(a-b)+.001,math.dist(target,hip)))
    along=(a*a-b*b+distance*distance)/(2*distance);pole=sub(knee,hip)
    bend=unit(sub(pole,mul(direction,sum(x*y for x,y in zip(pole,direction)))))
    newknee=add(hip,add(mul(direction,along),mul(bend,math.sqrt(max(0,a*a-along*along)))))
    upper=between(sub(knee,hip),sub(newknee,hip));lower=between(sub(foot,knee),sub(target,newknee))
    rotations[ids[0]]=upper;rotations[ids[1]]=qmul(inverse(upper),lower);rotations[ids[2]]=inverse(lower)


def pose(name,t):
    rotations=[(0,0,0,1) for _ in BONES];shift=[(0,0,0) for _ in BONES]
    def turn(b,direction,degrees): rotations[IDS[b]]=axis(direction,math.radians(degrees))
    phase=t*math.tau
    if name=='idle':
        turn('spine',(0,1,0),1.1*math.sin(phase));turn('head',(0,0,1),4*math.sin(phase))
        turn('jaw',(0,1,0),2*max(0,math.sin(phase*2)))
    elif name=='walk':
        for side,offset in (('L',0),('R',math.pi)):
            p=phase+offset;foot=REST[IDS[f'leg_{side}_end']]
            solve_leg(side,add(foot,(-3.5*math.cos(p),0,2.2*max(0,math.sin(p)))),rotations)
            turn(f'arm_{side}_upper',(0,1,0),9*math.cos(p))
        turn('head',(0,0,1),2*math.sin(phase))
    elif name in ('attack','attack_alt'):
        wind=max(0,math.sin(math.pi*min(1,t/.5)))
        strike=max(0,math.sin(math.pi*max(0,(t-.28)/.72)))**2
        turn('spine',(0,0,1),(-12 if name=='attack' else 14)*strike)
        turn('arm_R_upper',(0,1,0),-65*wind+75*strike)
        turn('arm_R_lower',(0,1,0),-30*wind+15*strike)
        turn('arm_R_end',(0,1,0),-10*wind+15*strike)
        turn('arm_L_upper',(0,1,0),-25*strike)
        turn('head',(0,1,0),8*strike);turn('jaw',(0,1,0),12*strike)
    elif name=='hit':
        hit=math.sin(math.pi*t)**2
        turn('spine',(0,1,0),-13*hit);turn('head',(0,0,1),-15*hit)
        turn('arm_R_upper',(0,0,1),15*hit)
    elif name=='death':
        s=min(1,t/.8);s=s*s*(3-2*s)
        turn('root',(1,0,0),90*s);shift[0]=(0,16*s,0)
        turn('head',(0,0,1),25*s);turn('jaw',(0,1,0),15*s)
        for side in ('L','R'):
            turn(f'arm_{side}_upper',(0,1,0),-30*s)
            turn(f'arm_{side}_lower',(0,1,0),45*s)
            turn(f'leg_{side}_lower',(0,1,0),35*s)
    for i in range(5):
        turn(f'tail_{i}',(0,0,1),(2*math.sin(phase-i*.7) if name in ('idle','walk') else 3*math.sin(math.pi*t)))
    return [(*add(local,shift[i]),*rotations[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]


def geometry():
    from .connected_skin import attach
    return assemble(attach('kobold',build_parts(),weights),weights)
def matrices(frame): return RIG.matrices(frame)
def deform(vertices,influences,frame): return RIG.deform(vertices,influences,frame)
def animation_data(vertices,influences): return sample_clips(RIG,CLIPS,pose,vertices,influences)


def build():
    (ROOT/'mod/BrogueDoom'/kobold_materials.SKIN).write_bytes(kobold_materials.texture_bytes())
    parts,vertices,normals,uv,triangles,influences=geometry();clips,bounds=animation_data(vertices,influences)
    payload=iqm.encode(vertices,normals,uv,triangles,influences,BONES,clips,bounds,
                       mesh_label='Project_Broom_kobold',material_path='graphics/BRGKOB.png')
    path=ROOT/'mod/BrogueDoom/models/monsters/02_kobold.iqm';path.write_bytes(payload)
    manifest={'schemaVersion':1,'workId':'BRG-M02','format':'IQM v2','runtimeModel':path.relative_to(ROOT).as_posix(),
              'sha256':hashlib.sha256(payload).hexdigest(),'skin':'graphics/BRGKOB.png',
              'skinSha256':hashlib.sha256((ROOT/'mod/BrogueDoom/graphics/BRGKOB.png').read_bytes()).hexdigest(),
              'dimensions':[round(max(v[a] for v in vertices)-min(v[a] for v in vertices),4) for a in range(3)],
              'parts':len(parts),'vertices':len(vertices),'triangles':len(triangles),'boneCount':len(BONES),
              'bones':[{'name':n,'parent':p,'local':v} for n,p,v in BONES],
              'clips':[{k:v for k,v in c.items() if k!='frames'}|{'frameCount':len(c['frames'])} for c in clips],
              'poseBounds':bounds,'authoringSource':'assets/monsters/kobold/kobold-animated.blend'}
    out=ROOT/'assets/monsters/kobold';out.mkdir(parents=True,exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Kobold:',len(vertices),'vertices,',len(BONES),'bones,',len(clips),'clips')
    return manifest


if __name__=='__main__': build()
