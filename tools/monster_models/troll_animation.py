"""Original asymmetric warty troll with huge misshapen hands. Cosmetic only."""
import hashlib
import json
import math
from . import iqm, troll_materials
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips

SKIN='graphics/BRGTROLL.png'
SPECS=[('root',None,(0,0,0)),('pelvis','root',(-1,0,27)),
       ('spine','pelvis',(-3,0,44)),('neck','spine',(0,0,55)),
       ('head','neck',(5,0,62)),('jaw','head',(11,0,57))]
for side,sign in (('L',1),('R',-1)):
    for limb,parent,points in (
        ('arm','spine',[(-2,sign*12,55 if side=='L' else 51),(1,sign*19,37),(8,sign*21,24)]),
        ('leg','pelvis',[(-1,sign*7,27),(6,sign*8.5,15),(1,sign*9,3.3)])):
        for joint,point in zip(('upper','lower','end'),points):
            name=f'{limb}_{side}_{joint}';SPECS.append((name,parent,point));parent=name
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('lumber',32,35,True),('pummel',26,35,False),
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
    s.oval('pelvis',(-1,0,27),(7.4,10,7))
    s.parts.append(ring_surface('torso',[(25,-1,6.8,9),(30,0,9.0,10.6),(35,-.2,10.2,12),
        (40,-1.4,10.8,13.4),(45,-2.8,11.2,14.1),(50,-3.5,10.8,14.5),
        (55,-3.5,9.1,12.3),(59,-3,7.3,9.2),(62,-2,4.7,5),(64,-1,2.7,3)]))
    s.oval('torso_hump',(-8,4,55),(6.5,8,10),'body',30,18)
    # Squashed asymmetrical head carried in front of the shoulders.
    s.parts.append(ring_surface('head_cranium',[(54,6.5,3.8,4.3),(56,7,5.5,6.4),(59,6,5.9,7),
        (62,4.8,6.6,7.5),(65,3.3,6.6,7.0),(68,2.1,5.1,5.5),(70,1.5,2.8,3),(70.4,1.5,.15,.2)]))
    s.oval('head_nose',(11.5,.8,61),(2.5,3.0,2.2),'body',24,14)
    s.oval('head_cheek_L',(9,4.8,59),(3.2,3.1,3.8),'body',24,14)
    s.oval('head_cheek_R',(8.8,-4.9,59.5),(2.6,2.7,3),'body',24,14)
    s.oval('head_chin',(10,-.6,55.8),(3.4,5.4,2.8),'body',24,14)
    s.strand('jaw_mouth',[(12,-4,58.1,.34),(13.7,-1.5,57.5,.38),(13.8,1.6,57.8,.4),(12,4.3,58.8,.3)],'dark',14,4)
    for i in range(5):
        s.oval(f'jaw_tooth_{i}',(13.9,(i-2)*.9,57.65),(.23,.34,.5 if i%2 else .3),'bone',12,8)
    for sign in (-1,1):
        z=64+.65*sign
        s.oval(f'detail_socket_{sign}',(10,sign*3.6,z),(.26,1.2,.65),'dark',20,12)
        s.oval(f'detail_iris_{sign}',(10.25,sign*3.6,z),(.09,.48,.35),'accent',18,10)
        s.oval(f'detail_pupil_{sign}',(10.34,sign*3.6,z),(.04,.18,.27),'dark',14,8)
        s.strand(f'head_brow_{sign}',[(11.3,sign*1.6,z+.9,1),(9.8,sign*3.8,z+1.0,1.3 if sign==1 else .8),(7.6,sign*6,z+.4,.6)],'body',16,4)
        s.strand(f'head_ear_{sign}',[(2,sign*6.5,63.5,1.2),(1,sign*8.8,62.8,1.6),(.6,sign*9.6,59.5,.4)],'body',14,4)
        s.oval(f'detail_nostril_{sign}',(13.8,.7+sign*1.2,60.5),(.16,.55,.36),'dark',16,10)
    for side,sign in (('L',1),('R',-1)):
        s.oval(f'shoulder_{side}',(-2,sign*11.5,54 if side=='L' else 51),(6.4,6.3,8 if side=='L' else 5.7),'body',26,16)
        for limb in ('arm','leg'):
            points=[REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
            radii=(5.6 if side=='L' else 4.8,4.1,3.0) if limb=='arm' else (6,4.2,3)
            s.strand(f'{limb}_{side}',[(*p,r) for p,r in zip(points,radii)],sides=22,samples=5)
        s.oval(f'foot_{side}',(3,sign*9,2.1),(6,4.3,1.8),'body',26,14)
        for i in range(4):s.oval(f'foot_{side}_toe{i}',(8,sign*9+(i-1.5)*1.6,1.7),(1.9,1,1.3),'body',14,8)
        s.oval(f'hand_{side}_palm',(8.7,sign*16.5,23.5),(4.1,4.7 if side=='L' else 4.1,4.4),'body',26,16)
        for i in range(4):
            y=sign*(13.4+i*1.85);z=22.6+(.45 if i%2 else -.45)
            length=(3.6,5.2,4.5,3.0)[i]+(.8 if side=='L' else 0)
            s.strand(f'hand_{side}_finger{i}',[(9.2,y,z,1.18),(11.4,y+sign*.4,z-length*.6,1.35),(11,y+sign*.45,z-length,1.05),(9.8,y,z-length+.2,.8)],'body',14,4)
            s.oval(f'nail_{side}_{i}',(10.1,y,z-length+.5),(.42,.62,.7),'bone',12,8)
        s.strand(f'hand_{side}_thumb',[(6.5,sign*13,24.5,1.4),(8.7,sign*11.7,22,1.2),(10.3,sign*12.1,20.7,.75)],'body',14,4)
    # No held weapon: the source's misshapen hands deliver its existing attacks.
    for i in range(11):
        a=math.tau*i/11
        s.strand(f'wrap_strip_{i}',[(-1+8*math.cos(a),10.8*math.sin(a),29,.95),(-1+8.5*math.cos(a),11*math.sin(a),26,1.2),(-1+8.8*math.cos(a),11.3*math.sin(a),22+(i%3),.12)],'cloth',12,3)
    # Static attached mucus ropes: no droplets are spawned, no hazard exists.
    for i,(y,end) in enumerate([(-2.7,50),(-.5,47.5),(2.0,52)]):
        s.strand(f'phlegm_head_{i}',[(13.3,y,57.3,.32),(13.5,y+.2,55,.39),(12.2,y+.4,end,.16)],'accent',12,4)
        s.oval(f'phlegm_head_bead_{i}',(12.2,y+.4,end),(.32,.35,.62),'accent',14,10)
    s.strand('phlegm_chest',[(7.7,1.5,49,.48),(8.5,2.1,44,.72),(9,1.8,40,.25)],'accent',14,4)
    for p in s.parts:
        if p.name.startswith(('hand_','nail_')):
            sign=1 if p.name.split('_')[1]=='L' else -1
            p.vertices=[(x,y+sign*4.5,z) for x,y,z in p.vertices]
    return troll_materials.repack(s.parts)

def weights(part,v,uv):
    n=part.name
    if n.startswith('nail_'):return [(IDS[f"arm_{n.split('_')[1]}_end"],1)]
    if n.startswith('phlegm_head'):return [(IDS['head'],1)]
    if n.startswith('phlegm_chest'):return [(IDS['spine'],1)]
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
    if not abs(a-b)<distance<a+b:raise ValueError(('unreachable troll foot',side,target,distance,a+b))
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
    elif name in ('pummel','batter'):
        wind=math.sin(math.pi*min(1,t/.4))**2
        hit=math.sin(math.pi*max(0,(t-.25)/.75))**2
        turn('arm_R_upper',(0,1,0),12*wind-28*hit)
        turn('arm_R_lower',(0,1,0),-12*wind-8*hit)
        turn('spine',(0,0,1),(4 if name=='pummel' else -7)*hit)
        turn('arm_L_upper',(0,1,0),(-10 if name=='pummel' else -28)*hit)
        turn('head',(0,1,0),4*hit);turn('jaw',(0,1,0),6*hit)
    elif name=='recoil':
        turn('spine',(0,1,0),-7*pulse);turn('head',(0,0,1),-7*pulse)
    elif name=='collapse':
        s=min(1,t/.85);s=s*s*(3-2*s)
        shift[IDS['pelvis']]=(-5*s,0,-10*s)
        for side in ('L','R'):
            # Solve against the translated pelvis, preserving both planted feet.
            target=add(REST[IDS[f'leg_{side}_end']],(5*s,0,10*s))
            solve_leg(side,target,rot)
        turn('spine',(0,1,0),42*s);turn('neck',(0,1,0),12*s);turn('head',(0,1,0),35*s)
        turn('arm_R_end',(0,1,0),12*s)
        turn('arm_R_upper',(0,1,0),-20*s);turn('arm_L_upper',(0,1,0),-24*s)
        turn('jaw',(0,1,0),10*s)
    return [(*add(local,shift[i]),*rot[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]

def surface_warts(body):
    """Seat each wart on a baked cage vertex with exactly its skin weights.

    Geometry detail moves with the skin, including at the shoulders. The fixed
    spatial selection is an authoring pattern, not simulation randomness.
    """
    candidates = []
    normals = body.normals()
    seen=set()
    for i,(center,normal) in enumerate(zip(body.vertices,normals)):
        if tuple(center) in seen:continue
        seen.add(tuple(center));x,y,z=center
        if z<18 or normal[2]<-.5 or (z>54 and x>6):continue
        candidates.append((tuple(center),unit(normal),(i,)))
    # Irregular golden-ratio ordering avoids horizontal rows of identical beads.
    candidates.sort(key=lambda c: ((c[0][0]*.754877666+c[0][1]*.569840296)%1,c[0]))
    chosen = []; parts = []
    for center,normal,face in candidates:
        if any(math.dist(center,c)<2.0 for c in chosen): continue
        chosen.append(center)
        radius = .6+.65*((center[0]*1.71+center[1]*2.39)%1)
        s = Sculpt()
        p = s.oval(f'wart_{len(parts):02d}',(0,0,0),(radius,radius*.85,radius*.43),
                   'accent',8,5)
        troll_materials.repack(s.parts)
        tangent = unit((normal[2],0,-normal[0]))
        bitangent = (normal[1]*tangent[2],normal[2]*tangent[0]-normal[0]*tangent[2],-normal[1]*tangent[0])
        # The lower half intersects the skin; no detached bead or floating disc.
        p.vertices = [add(center,add(mul(tangent,x),add(mul(bitangent,y),mul(normal,z))))
                      for x,y,z in p.vertices]
        blend = {}
        for i in face:
            for bone,w in body.skin_weights[i]: blend[bone] = blend.get(bone,0)+w/len(face)
        keep = sorted(blend.items(),key=lambda row:(-row[1],row[0]))[:4]
        total = sum(w for _,w in keep)
        p.skin_weights = [[(b,w/total) for b,w in keep] for _ in p.vertices]
        parts.append(p)
        if len(parts)>=96: break
    return parts


def geometry():
    from .connected_skin import attach
    parts=attach('troll',build_parts(),weights)
    return assemble(troll_materials.connected_atlas(parts+surface_warts(parts[0])),weights)
def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():
    from .connected_skin import attach
    return troll_materials.connected_atlas(attach('troll',build_parts(),weights),True)
def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    supplemental={}
    for name,data in troll_materials.surface_maps().items():
        (ROOT/'mod/BrogueDoom'/name).write_bytes(data);supplemental[name]=hashlib.sha256(data).hexdigest()
    parts,v,n,uv,tr,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,tr,w,BONES,clips,bounds,mesh_label='Project_Broom_troll',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/26_troll.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M26',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        supplementalMaps=supplemental,parts=len(parts),vertices=len(v),triangles=len(tr),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/troll/troll-animated.blend')
    out=ROOT/'assets/monsters/troll';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':print(build()['sha256'])
