"""Original large club-bearing brute. All motion is cosmetic presentation."""
import hashlib
import json
import math
from . import iqm, ogre_materials
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips

SKIN='graphics/BRGOGRE.png'
SPECS=[('root',None,(0,0,0)),('pelvis','root',(-1,0,29)),
       ('spine','pelvis',(-3,0,47)),('neck','spine',(-1,0,61)),
       ('head','neck',(2,0,68)),('jaw','head',(7,0,63))]
for side,sign in (('L',1),('R',-1)):
    for limb,parent,points in (
        ('arm','spine',[(-2,sign*13,53),(0,sign*17,41),(6,sign*17,33)]),
        ('leg','pelvis',[(-1,sign*7,29),(6,sign*9,16),(1,sign*9,3)])):
        for joint,point in zip(('upper','lower','end'),points):
            name=f'{limb}_{side}_{joint}';SPECS.append((name,parent,point));parent=name
SPECS.append(('club','arm_R_end',(6,-17,33)))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('lumber',32,35,True),('cudgel',26,35,False),
       ('batter',28,35,False),('recoil',14,35,False),('collapse',36,35,False)]

def ring_surface(name,rings,segments=40,face=False):
    p=Part(name)
    for j,(z,cx,depth,width) in enumerate(rings):
        for i in range(segments):
            a=math.tau*i/segments;y=width*math.sin(a);f=max(0,math.cos(a))
            x=cx+depth*math.cos(a)
            if face:
                socket=math.exp(-((abs(y)-3.0)/1.05)**2-((z-68.5)/1.0)**2)
                brow=math.exp(-((abs(y)-2.8)/2.2)**2-((z-70)/.7)**2)
                nose=math.exp(-(y/1.25)**2-((z-66.8)/2.0)**2)
                cheek=math.exp(-((abs(y)-4.1)/1.2)**2-((z-65.7)/1.2)**2)
                x+=f*(-1.3*socket+1.4*brow+2.1*nose+.8*cheek)
            else:
                x+=f*(1.2*math.exp(-((z-51)/4)**2-((abs(y)-5.2)/3.6)**2)
                      -.5*math.exp(-(y/.8)**2-((z-50)/5)**2))
            p.vertex((x,y,z),'fur',i/segments,j/(len(rings)-1))
    for j in range(len(rings)-1):
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments;p.faces.append((a,b,b+segments,a+segments))
    p.faces.extend((tuple(reversed(range(segments))),tuple((len(rings)-1)*segments+i for i in range(segments))))
    return p

def build_parts():
    s=Sculpt()
    s.oval('pelvis',(-1,0,29),(7.8,9.5,7))
    s.parts.append(ring_surface('torso',[(26,-1,7,9),(30,-.5,8,9.6),(35,.3,9.8,10.8),
        (40,-.3,10.3,11.5),(45,-2.2,9.4,12.5),(50,-3,8.4,13),(54,-2.8,7.6,12.7),
        (57,-2.3,7,10.8),(60,-1,6,7),(64,1,5.3,5.5),(66,1.5,4.7,5.0)]))
    s.parts.append(ring_surface('head_cranium',[(62,3.3,4.3,4.5),(64,3.1,5,5.4),(66,2.4,5.1,5.9),
        (68,1.4,5.3,6.2),(70,.4,5.6,6.1),(72,-.5,5.2,5.5),(74,-1.1,4.1,4.2),(75,-1.2,2.4,2.7),
        (75.6,-1.2,.1,.1)],face=True))
    s.oval('head_chin',(6,0,62.9),(2.7,4.3,2.1),'body',24,12)
    s.strand('jaw_mouth',[(8.1,-3.4,64,.14),(8.8,-1.5,63.65,.17),(8.85,1.5,63.65,.17),(8.1,3.4,64,.14)],'dark',10)
    for i in range(6):
        y=(i-2.5)*.8
        s.oval(f'jaw_tooth_{i}',(8.6,y,63.6),(.24,.32,.47 if i%3 else .35),'bone',10,8)
    for sign in (-1,1):
        s.oval(f'head_ear_{sign}',(-1.0,sign*6.0,68),(1.7,1.8,2.65),'body')
        s.oval(f'detail_ear_inner_{sign}',(.33,sign*6.25,68),(.25,1.15,1.7),'accent')
        s.oval(f'detail_eye_socket_{sign}',(6.06,sign*3,68.5),(.22,.95,.42),'dark',18,10)
        s.oval(f'detail_eye_iris_{sign}',(6.25,sign*3,68.48),(.08,.36,.26),'accent',16,8)
        s.oval(f'detail_eye_pupil_{sign}',(6.31,sign*3,68.49),(.035,.13,.22),'dark',12,8)
        s.strand(f'head_brow_{sign}',[(7.3,sign*1.1,69.6,.75),(6.5,sign*2.9,70,.85),(4.9,sign*4.8,70.2,.65)],'body',12)
        s.oval(f'detail_nostril_{sign}',(9.3,sign*.9,66.15),(.16,.38,.25),'dark',12,8)
    for side,sign in (('L',1),('R',-1)):
        s.oval(f'shoulder_{side}',(-2,sign*11.5,52.5),(6.2,5.7,6.2))
        for limb in ('arm','leg'):
            points=[REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
            radii=(5.0,3.8,2.5) if limb=='arm' else (6.0,4.2,2.7)
            s.strand(f'{limb}_{side}',[(*p,r) for p,r in zip(points,radii)],sides=20,samples=5)
        s.oval(f'foot_{side}',(3,sign*9,2.0),(5.2,3.9,1.9),'body',24,12)
        for i in range(4):
            s.oval(f'foot_{side}_toe{i}',(7,sign*9+(i-1.5)*1.4,1.6),(1.7,.85,1.3),'body',12,8)
        s.oval(f'hand_{side}_palm',(6,sign*17,33),(2.7,3,3.2),'body')
        if side=='R':
            for i in range(4):
                z=31.1+i*1.25
                s.strand(f'hand_R_finger{i}',[(5,-19,z,.78),(7.5,-19,z,.75),(8,-17,z,.7),
                    (7,-15.5,z,.65),(5.7,-16,z,.52)],'body',10,3)
            s.strand('hand_R_thumb',[(4,-15,35.5,.95),(6,-14.5,35.8,.8),(7.5,-16,34.6,.65)],'body',12)
        else:
            for i in range(4):
                y=15+i*1.3
                s.strand(f'hand_L_finger{i}',[(6,y,32,.8),(7,y,29,.72),(8,y,27.7,.5)],'body',10,3)
            s.strand('hand_L_thumb',[(4.5,19,33,.95),(6.5,20,32,.8),(7.5,19,30.5,.6)],'body',10)
    # Thick plain hide kilt, uneven worn hem and rolled top. No armor claim.
    p=Part('wrap_hide');n=40
    for row in range(4):
        for i in range(n):
            a=math.tau*i/n;bottom=23+1.1*math.sin(i*2.1)+.6*math.sin(i*3.7)
            z=31.6 if row in (0,3) else bottom;inset=.22 if row>=2 else 0
            fold=(.18 if row in (0,3) else .55)*math.cos(10*a)
            p.vertex((-1+(8.6+fold-inset)*math.cos(a),(10.25+fold-inset)*math.sin(a),z),'paw',i/n,float(row in (1,2)))
    for row in range(4):
        for i in range(n):p.faces.append((row*n+i,((row+1)%4)*n+i,((row+1)%4)*n+(i+1)%n,row*n+(i+1)%n))
    s.parts.append(p)
    s.strand('wrap_belt',[(-1+8.8*math.cos(a),10.5*math.sin(a),31.4,.34) for a in [math.tau*i/60 for i in range(61)]],'cloth',8,1)
    s.strand('wrap_tie',[(7.8,0,31.4,.35),(8.2,1,29,.32),(8.7,1.2,26,.18)],'cloth',8)
    # One continuous irregular timber, thick crown and narrowed hand grip.
    s.strand('club_timber',[(6.4,-17,22,1.3),(6,-17,29,1.5),(6,-17,36,1.5),(5,-17.5,44,2.6),
        (3.5,-18,54,4.6),(2,-18.6,64,5.6),(1.5,-18.4,71,5.3),(2,-18,74,4.5)],'wood',24,4)
    for i in range(5):
        z=56+i*3.5;a=i*2.3
        s.oval(f'club_knot_{i}',(3+4.4*math.cos(a),-18+4.4*math.sin(a),z),(1.3,1.3,2),'wood',12,8)
    for i in range(8):
        z=27+i*1.05
        s.strand(f'club_binding_{i}',[(6+1.58*math.cos(a),-17+1.58*math.sin(a),z+.2*math.sin(a),.19)
                     for a in [math.tau*j/20 for j in range(21)]],'cloth',6,1)
    # Blunt lower face instead of a projecting primate muzzle; shallow eyes
    # sit beneath the existing brow. Deform the complete head consistently.
    for p in s.parts:
        if p.name.startswith(('head','detail','jaw')):
            p.vertices=[(x-1.7*max(0,min(1,(68-z)/4)),y*1.08,z) for x,y,z in p.vertices]
        if p.name.startswith('detail_eye'):
            center=(6.18,3.24 if '_1' in p.name else -3.24,68.5)
            p.vertices=[(x,center[1]+(y-center[1])*1.3,center[2]+(z-center[2])*1.35) for x,y,z in p.vertices]
        if p.name=='club_timber':
            p.vertices=[(x+(.6*math.sin(z*.37) if z>45 else 0),y,
                         z+(max(0,(z-68)/6))*(.85*math.sin(x*1.7+y*.8)+.5*math.sin(y*2.1))) for x,y,z in p.vertices]
    return ogre_materials.repack(s.parts)

def weights(part,v,uv):
    n=part.name
    if n.startswith('club'):return [(IDS['club'],1)]
    if n.startswith('wrap'):return [(IDS['pelvis'],1)]
    if n.startswith(('head','detail')):return [(IDS['head'],1)]
    if n.startswith('jaw'):return [(IDS['jaw'],1)]
    if n.startswith('shoulder_'):
        t=max(0,min(1,(abs(v[1])-7)/7));return [(IDS['spine'],1-t),(IDS[f'arm_{n[-1]}_upper'],t)]
    if n.startswith(('hand_','foot_')):
        return [(IDS[f'{"arm" if n.startswith("hand") else "leg"}_{n.split("_")[1]}_end'],1)]
    if n.startswith(('arm_','leg_')):return RIG.chain_weights(v,[IDS[n+'_'+j] for j in ('upper','lower','end')])
    if n=='pelvis':return [(IDS['pelvis'],1)]
    return RIG.chain_weights(v,[IDS[b] for b in ('pelvis','spine','neck','head')])

def solve_leg(side,target,rotations):
    ids=[IDS[f'leg_{side}_{j}'] for j in ('upper','lower','end')]
    hip,knee,foot=[REST[i] for i in ids];a=math.dist(hip,knee);b=math.dist(knee,foot)
    distance=math.dist(target,hip)
    if not abs(a-b)<distance<a+b:raise ValueError(('unreachable ogre foot',side,target,distance,a+b))
    direction=unit(sub(target,hip));along=(a*a-b*b+distance*distance)/(2*distance);pole=sub(knee,hip)
    bend=unit(sub(pole,mul(direction,sum(x*y for x,y in zip(pole,direction)))))
    nk=add(hip,add(mul(direction,along),mul(bend,math.sqrt(max(0,a*a-along*along)))))
    upper=between(sub(knee,hip),sub(nk,hip));lower=between(sub(foot,knee),sub(target,nk))
    rotations[ids[0]]=upper;rotations[ids[1]]=qmul(inverse(upper),lower);rotations[ids[2]]=inverse(lower)

def pose(name,t):
    rot=[(0,0,0,1) for _ in BONES];shift=[(0,0,0) for _ in BONES]
    def turn(b,d,v):rot[IDS[b]]=axis(d,math.radians(v))
    phase=math.tau*t;pulse=math.sin(math.pi*t)**2
    if name=='idle':
        turn('spine',(0,1,0),.55*math.sin(phase));turn('head',(0,0,1),1.8*math.sin(phase))
    elif name=='lumber':
        for side,offset in (('L',0),('R',.5)):
            q=(t+offset)%1
            if q<.6:dx=3.0-6.0*q/.6;lift=0
            else:
                u=(q-.6)/.4;dx=-3+6*u;lift=2.8*math.sin(math.pi*u)
            solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(dx,0,lift)),rot)
            turn(f'arm_{side}_upper',(0,1,0),2.5*math.cos(phase+offset*math.tau))
        turn('spine',(1,0,0),1.3*math.sin(phase))
    elif name in ('cudgel','batter'):
        wind=math.sin(math.pi*min(1,t/.4))**2
        hit=math.sin(math.pi*max(0,(t-.25)/.75))**2
        turn('arm_R_upper',(0,1,0),-14*wind+22*hit)
        turn('arm_R_lower',(0,1,0),-8*wind+4*hit)
        turn('spine',(0,0,1),(4 if name=='cudgel' else -7)*hit)
        turn('arm_L_upper',(0,1,0),-14*hit)
        turn('head',(0,1,0),4*hit);turn('jaw',(0,1,0),6*hit)
    elif name=='recoil':
        turn('spine',(0,1,0),-7*pulse);turn('head',(0,0,1),-7*pulse)
    elif name=='collapse':
        s=min(1,t/.85);s=s*s*(3-2*s)
        shift[IDS['pelvis']]=(-5*s,0,-12*s)
        for side in ('L','R'):
            # Solve against the translated pelvis, preserving both planted feet.
            target=add(REST[IDS[f'leg_{side}_end']],(5*s,0,12*s))
            solve_leg(side,target,rot)
        turn('spine',(0,1,0),42*s);turn('neck',(0,1,0),12*s);turn('head',(0,1,0),35*s)
        turn('arm_R_end',(0,1,0),-45*s)
        turn('arm_R_upper',(0,1,0),-31*s);turn('arm_L_upper',(0,1,0),-15*s)
        turn('jaw',(0,1,0),10*s)
    return [(*add(local,shift[i]),*rot[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]

def geometry():
    from .connected_skin import attach
    parts=attach('ogre',build_parts(),weights)
    return assemble(ogre_materials.connected_atlas(parts),weights)
def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():
    from .connected_skin import attach
    return ogre_materials.connected_atlas(attach('ogre',build_parts(),weights),True)
def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,tr,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,tr,w,BONES,clips,bounds,mesh_label='Project_Broom_ogre',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/18_ogre.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M18',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(tr),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/ogre/ogre-animated.blend')
    out=ROOT/'assets/monsters/ogre';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':print(build()['sha256'])
