"""Original brown primate and stone spear; cosmetic skeletal presentation only."""
import hashlib
import json
import math
from . import iqm, goblin_materials
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips

SKIN='graphics/BRGGOB.png'
SPECS=[('root',None,(0,0,0)),('pelvis','root',(0,0,18)),
       ('spine','pelvis',(-1.5,0,27)),('neck','spine',(1,0,32)),
       ('head','neck',(3,0,35)),('jaw','head',(5,0,32.5))]
for side,sign in (('L',1),('R',-1)):
    for limb,parent,points in (
        ('arm','spine',[(0,sign*6,28),(2,sign*8,23),(4,sign*8,20 if side=='R' else 17)]),
        ('leg','pelvis',[(0,sign*3,18),(4.3,sign*3.5,10),(2,sign*4,2)])):
        for joint,point in zip(('upper','lower','end'),points):
            name=f'{limb}_{side}_{joint}';SPECS.append((name,parent,point));parent=name
SPECS.append(('spear','arm_R_end',(4,-8,20)))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('walk',20,35,True),('thrust',18,35,False),
       ('cut',20,35,False),('recoil',10,35,False),('death',26,35,False)]


def sculpted_head():
    """Continuous craniofacial surface with recessed orbits, not a muzzle stack.

    Rings describe skull planes; smooth local displacements carve the sockets
    and build the nose/brow. X is forward, Y lateral, Z up.
    """
    p=Part('head_cranium');segments=48
    rings=[(31.5,3.4,.7,1.15),(32,3.3,1.35,1.9),(32.7,3.05,2,2.3),
           (33.4,2.65,2.4,2.7),(34.2,2.35,2.8,3.55),(35,2.1,3.15,3.6),
           (35.7,2.1,3.25,3.65),(36.4,1.9,3.5,3.6),(37.1,1.5,3.5,3.3),
           (37.8,1.1,3.1,2.8),(38.4,.9,2.3,2.1),(38.8,.8,.1,.1)]
    for j,(z,cx,depth,width) in enumerate(rings):
        for i in range(segments):
            a=math.tau*i/segments;y=width*math.sin(a);front=max(0,math.cos(a))
            x=cx+depth*math.cos(a)
            socket=math.exp(-((abs(y)-1.65)/.85)**2-((z-35.55)/.68)**2)
            brow=math.exp(-((abs(y)-1.7)/1.5)**2-((z-36.4-abs(y)*.12)/.45)**2)
            nose=math.exp(-(y/.65)**2-((z-34.55)/1.45)**2)
            cheek=math.exp(-((abs(y)-2.55)/.7)**2-((z-34)/.6)**2)
            # Hollow the lower cheeks and define the upper lip/chin planes.
            hollow=math.exp(-((abs(y)-2.0)/.65)**2-((z-33.3)/.65)**2)
            lip=math.exp(-(y/1.35)**4-((z-32.9)/.35)**2)
            x+=front*(-1.0*socket+.85*brow+1.75*nose+.7*cheek-.5*hollow+.35*lip)
            p.vertex((x,y,z),'paw',i/segments,j/(len(rings)-1))
    for j in range(len(rings)-1):
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments
            p.faces.append((a,b,b+segments,a+segments))
    p.faces.extend((tuple(reversed(range(segments))),tuple((len(rings)-1)*segments+i for i in range(segments))))
    return p


def swept_ear(name,sign,inner=False):
    p=Part(name)
    points=[(1.7,3.15,36.2),(-1.2,7.1,37.8),(.2,5.45,34.6),(2,3.3,34.5),
            (1.65,4.45,35.9),(.75,4.25,35.8)]
    if inner:
        points=[(1.82,3.5,36.1),(-.65,6.3,37.25),(.65,5.1,35.25),(1.95,3.7,35.1),
                (1.92,4.45,35.9),(1.7,4.25,35.8)]
    for i,(x,y,z) in enumerate(points):p.vertex((x,sign*y,z),'paw',(i%3)/2,(i//3))
    for i in range(4):
        j=(i+1)%4;p.faces.extend(((4,i,j),(5,j,i)))
    if sign<0:p.faces=[tuple(reversed(f)) for f in p.faces]
    return p


def build_parts():
    s=Sculpt()
    s.oval('pelvis',(0,0,18),(3.6,4.5,3.5))
    # One elliptical trunk-to-neck surface avoids the capped-tube collar ridge.
    torso=Part('torso');segments=32
    trunk=[(17,-.2,2.8,3.8),(19,-.6,2.65,3.8),(21,-1,2.5,3.1),
           (23,-1.4,2.6,3.25),(25,-1.8,2.9,4.2),(27,-2,3.25,5.3),
           (29,-1.6,3.1,5.25),(30.3,-.6,2.7,4.1),(31.5,.5,2.25,2.9),
           (33,1.3,2,2.4)]
    for row,(z,cx,depth,width) in enumerate(trunk):
        for i in range(segments):
            a=math.tau*i/segments
            y=width*math.sin(a);front=max(0,math.cos(a))
            chest=.55*math.exp(-((z-27)/2.4)**2-((abs(y)-2.2)/1.5)**2)
            sternum=-.23*math.exp(-(y/.6)**2-((z-26)/3)**2)
            torso.vertex((cx+depth*math.cos(a)+front*(chest+sternum),y,z),'fur',i/segments,row/(len(trunk)-1))
    for row in range(len(trunk)-1):
        for i in range(segments):
            a=row*segments+i;b=row*segments+(i+1)%segments
            torso.faces.append((a,b,b+segments,a+segments))
    torso.faces.extend((tuple(reversed(range(segments))),tuple((len(trunk)-1)*segments+i for i in range(segments))))
    s.parts.append(torso)
    s.parts.append(sculpted_head())
    s.strand('jaw_mouth',[(4.75,-1.65,32.8,.1),(5.28,-.65,32.7,.11),(5.28,.65,32.7,.11),(4.75,1.65,32.8,.1)],'dark',8)
    s.oval('jaw_lower',(4.35,0,32.2),(.85,1.55,.38),'cloth',16,8)
    # Sparse scalp tufts replace the smooth full-fur cap of the rejected model.
    for i in range(5):
        y=(i-2)*.65
        s.strand(f'head_hair_{i}',[(-.5,y,37.7,.65),(-1.7,y,38.65+(i%2)*.2,.4),
                                  (-3,y-.25,38.3,.035)],'body',8)
    for sign in (-1,1):
        s.parts.extend((swept_ear(f'head_ear_{sign}',sign),swept_ear(f'head_ear_inner_{sign}',sign,True)))
        s.oval(f'head_eye_socket_{sign}',(4.6,sign*1.65,35.55),(.17,.7,.25),'dark',16,10)
        s.oval(f'head_eye_iris_{sign}',(4.755,sign*1.65,35.56),(.06,.24,.145),'accent',16,10)
        s.oval(f'head_eye_pupil_{sign}',(4.805,sign*1.65,35.56),(.025,.09,.13),'dark',12,8)
        for p in s.parts[-3:]:p.vertices=[(x,y,z+(abs(y)-1.65)*.32) for x,y,z in p.vertices]
        s.strand(f'head_brow_{sign}',[(5.7,sign*.65,36,.42),(5.15,sign*1.65,36.25,.42),(4.25,sign*2.65,36.55,.3)],'cloth',10)
        s.oval(f'head_nostril_{sign}',(6.45,sign*.43,34.05),(.1,.17,.11),'dark',10,6)
        for i in range(2):
            x=-3+i*1.3;y=sign*(3.8+i*.65)
            s.strand(f'coat_shoulder_{sign}_{i}',[(x,y,28.6,.8),(x-.8,y+sign*.6,28,.6),(x-1.4,y+sign,26.9,.08)],sides=8)
    for side,sign in (('L',1),('R',-1)):
        s.oval(f'shoulder_{side}',(-.5,sign*5,28),(2.4,2.7,2.7))
        for limb in ('arm','leg'):
            points=[REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
            radii=(2.05,1.5,1.1) if limb=='arm' else (2.4,1.7,1.1)
            s.strand(f'{limb}_{side}',[(*p,r) for p,r in zip(points,radii)],sides=16,samples=4)
        s.oval(f'foot_{side}',(3,sign*4,1.2),(3,1.85,1.2),'cloth')
        for i in range(4):
            s.oval(f'foot_{side}_toe{i}',(5.3,sign*4+(i-1.5)*.8,.9),(.8,.45,.65),'cloth',12,8)
        if side=='L':
            s.oval('hand_L_palm',(4,8,17),(1.2,1.4,1.6),'cloth')
            for i in range(4):
                y=7.1+i*.6
                s.strand(f'hand_L_finger{i}',[(4.2,y,16.5,.4),(5,y,15,.36),(5.7,y,14.4,.23)],'cloth',8)
            s.strand('hand_L_thumb',[(4,9,17,.5),(5.5,9.4,16.8,.4),(5.8,8.8,16,.25)],'cloth',8)
            continue
        s.oval(f'hand_{side}_palm',(4,sign*8,20),(1.2,1.4,2.1),'cloth')
        # Curled fingers surround the right-hand shaft rather than float nearby.
        for i in range(4):
            x=3+(i*.65)
            s.strand(f'hand_{side}_finger{i}',[(x,sign*8-1,20.6,.4),(x+.7,sign*8-1,19.8,.4),
                         (x+.8,sign*8,19.5,.35),(x+.3,sign*8+.8,19.9,.28)],'cloth',8,3)
        s.strand(f'hand_{side}_thumb',[(3,sign*8+1,21,.5),(4.3,sign*8+1,21.6,.45),(5,sign*8,20.7,.25)],'cloth',8)
    # Plain ragged hide wrap: cosmetic clothing, no armor or cultural symbols.
    wrap=Part('wrap_ragged');n=32
    for row in range(4):
        for i in range(n):
            a=math.tau*i/n;z=18.8 if row in (0,3) else 14.7+.7*math.sin(i*2.3)+.35*math.sin(i*4.1)
            inset=.12 if row>=2 else 0
            fold=(.12 if row in (0,3) else .38)*math.cos(a*8+.3)
            wrap.vertex(((4.1-inset+fold)*math.cos(a),(5.05-inset+fold)*math.sin(a),z),'paw',i/n,float(row in (1,2)))
    for row in range(4):
        nextrow=(row+1)%4
        for i in range(n):
            j=(i+1)%n;wrap.faces.append((row*n+i,nextrow*n+i,nextrow*n+j,row*n+j))
    # Closed thin clothing shares pelvis motion, not collision.
    s.parts.append(wrap)
    # A plain rolled edge and short tie make the wrap read as worn clothing.
    belt=[(4.22*math.cos(a),5.17*math.sin(a),18.65+.12*math.sin(2*a),.16)
          for a in [i*math.tau/48 for i in range(49)]]
    s.strand('wrap_edge',belt,'cloth',6,1)
    for sign in (-1,1):
        s.strand(f'wrap_tie_{sign}',[(4.32,1,18.65,.16),(4.5,1+sign*.35,17.8,.14),
                                    (4.55,1+sign*.5,16.8,.09)],'cloth',6,2)
    # A narrow, irregular shaft and a knapped leaf point, not a gem-shaped club.
    s.strand('spear_shaft',[(-18,-8,12.2,.43),(-7,-8.25,16,.5),(4,-8,20,.55),
                            (15,-7.85,24,.46),(24,-8,27.1,.38)],'wood',12,3)
    stone=Part('spear_stone')
    outline=[(22,26.45),(23,28),(24.1,28.1),(24.6,29),(26,29.05),(27,29.75),
             (33,30.45),(29.2,27.3),(27.6,26.75),(26.8,26.3),(25.1,26.45),(23.6,25.9)]
    for x,z in outline:stone.vertex((x,-8,z),'claw',(x-22)/11,(z-25.9)/4.55)
    stone.vertex((26.6,-8.7,28.05),'claw',.45,.5)
    stone.vertex((26.6,-7.3,28.05),'claw',.45,.5)
    for i in range(len(outline)):
        j=(i+1)%len(outline);stone.faces.extend(((12,i,j),(13,j,i)))
    s.parts.append(stone)
    for i in range(7):
        # A continuous wrapping loop around the shaft, not stacked cylinders.
        x=21+i*.4;z=26.05+i*.145
        points=[(x+.19*math.cos(a),-8+.58*math.sin(a),z+.55*math.cos(a),.13)
                for a in [j*math.tau/16 for j in range(17)]]
        s.strand(f'spear_lashing{i}',points,'accent',6,1)
    # Angle the spear outward so the shaft reads from the player's frontal view.
    angle=math.radians(-27)
    for part in s.parts:
        if part.name.startswith('spear'):
            part.vertices=[(4+(x-4)*math.cos(angle)-(y+8)*math.sin(angle),
                            -8+(x-4)*math.sin(angle)+(y+8)*math.cos(angle),z) for x,y,z in part.vertices]
    return goblin_materials.repack(s.parts)


def weights(part,v,uv):
    name=part.name
    if name.startswith('wrap'):return [(IDS['pelvis'],1)]
    if name.startswith('spear'):return [(IDS['spear'],1)]
    if name.startswith('head'):return [(IDS['head'],1)]
    if name.startswith('jaw'):return [(IDS['jaw'],1)]
    if name.startswith('shoulder_'):
        t=max(0,min(1,(abs(v[1])-2)/4))
        return [(IDS['spine'],1-t),(IDS['arm_'+name[-1]+'_upper'],t)]
    if name.startswith(('hand_','foot_')):
        limb='arm' if name.startswith('hand') else 'leg'
        return [(IDS[f'{limb}_{name.split("_")[1]}_end'],1)]
    if name.startswith(('arm_','leg_')):return RIG.chain_weights(v,[IDS[name+'_'+j] for j in ('upper','lower','end')])
    if name=='pelvis':return [(IDS['pelvis'],1)]
    return RIG.chain_weights(v,[IDS[n] for n in ('pelvis','spine','neck','head')])


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
    def turn(b,d,degrees):rotations[IDS[b]]=axis(d,math.radians(degrees))
    phase=math.tau*t;pulse=math.sin(math.pi*t)**2
    if name=='idle':
        turn('spine',(0,1,0),.8*math.sin(phase));turn('head',(0,0,1),3*math.sin(phase))
    elif name=='walk':
        for side,offset in (('L',0),('R',math.pi)):
            p=phase+offset
            solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(-3.5*math.cos(p),0,2.6*max(0,math.sin(p)))),rotations)
            turn(f'arm_{side}_upper',(0,1,0),5*math.cos(p))
        turn('head',(0,0,1),2*math.sin(phase))
    elif name in ('thrust','cut'):
        wind=math.sin(math.pi*min(1,t/.35))**2
        strike=math.sin(math.pi*max(0,(t-.2)/.8))**2
        shift[IDS['arm_R_upper']]=(-2*wind+7*strike,0,0)
        turn('arm_R_upper',(0,1,0),8*wind-10*strike)
        turn('spine',(0,0,1),(-6 if name=='thrust' else 22)*strike)
        turn('head',(0,1,0),4*strike);turn('jaw',(0,1,0),8*strike)
        turn('arm_L_upper',(0,1,0),-20*strike)
    elif name=='recoil':
        turn('spine',(0,1,0),-12*pulse);turn('head',(0,0,1),-12*pulse)
    elif name=='death':
        s=min(1,t/.8);s=s*s*(3-2*s)
        turn('root',(1,0,0),90*s);shift[0]=(0,18*s,10*s)
        # Settle the outward-pointing spear alongside the fallen body.
        turn('spear',(0,0,1),27*s)
        turn('jaw',(0,1,0),18*s)
        for side in ('L','R'):
            turn(f'leg_{side}_lower',(0,1,0),30*s)
            turn(f'arm_{side}_lower',(0,1,0),25*s)
    return [(*add(local,shift[i]),*rotations[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]


def geometry():
    from .connected_skin import attach
    return assemble(attach('goblin',build_parts(),weights),weights)
def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():
    return goblin_materials.texture_bytes()


def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_goblin',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/08_goblin.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M08',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/goblin/goblin-animated.blend')
    out=ROOT/'assets/monsters/goblin';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':print(build()['sha256'])
