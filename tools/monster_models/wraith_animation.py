"""Original gaunt wraith with hollow sockets and stained groping nails. Cosmetic only."""
import hashlib,json,math
from . import iqm,wraith_materials
from .creatures import Sculpt
from .rat import ROOT,Part,add,sub,mul,unit
from .skeletal import Rig,axis,between,inverse,qmul,assemble,sample_clips
SKIN='graphics/BRGWRAIT.png'
SPECS=[('root',None,(0,0,0)),('pelvis','root',(0,0,28)),('spine','pelvis',(-.5,0,40)),
       ('neck','spine',(0,0,49)),('head','neck',(.2,0,55))]
for side,sign in (('L',1),('R',-1)):
 for limb,parent,points in (
  ('arm','spine',[(0,sign*6.3,45.5),(1,sign*8.2,36.5),(6,sign*8.3,31)]),
  ('leg','pelvis',[(0,sign*3.6,28),(2,sign*4.4,15),(0,sign*5.1,2.4)])):
  for joint,point in zip(('upper','lower','end'),points):
   name=f'{limb}_{side}_{joint}';SPECS.append((name,parent,point));parent=name

RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('advance',32,35,True),('rake',24,35,False),('clutch',26,35,False),('recoil',14,35,False),('fall',36,35,False)]

def rings(name,rows,sides=32):
 p=Part(name)
 for j,(z,cx,rx,ry) in enumerate(rows):
  for i in range(sides):
   a=math.tau*i/sides;x=cx+rx*math.cos(a);y=ry*math.sin(a)
   if name=='head_cranium':
    f=max(0,math.cos(a))
    x+=f*(.9*math.exp(-(y/.65)**2-((z-54.6)/1.35)**2)
       -.65*math.exp(-((abs(y)-1.55)/.65)**2-((z-55.7)/.65)**2)
       +.45*math.exp(-((abs(y)-2)/.6)**2-((z-54.2)/.8)**2))
   p.vertex((x,y,z),'fur',i/sides,j/(len(rows)-1))
 for j in range(len(rows)-1):
  for i in range(sides):
   a=j*sides+i;b=j*sides+(i+1)%sides;p.faces.append((a,b,b+sides,a+sides))
 p.faces.extend((tuple(reversed(range(sides))),tuple((len(rows)-1)*sides+i for i in range(sides))))
 return p

def build_parts():
 s=Sculpt()
 s.oval('pelvis',(0,0,28),(2.6,4.3,3.6))
 s.parts.append(rings('torso',[(27,0,2.5,4),(31,0,2.1,3.2),(35,-.5,1.9,3.4),(39,-.7,3,5.1),(43,-.7,3.7,6.1),(46,-.2,2.8,5.4),(48,.2,1.3,1.65),(52,.5,1.2,1.5)]))
 s.parts.append(rings('head_cranium',[(50.2,1.4,.9,1.1),(51.2,1.7,1.8,1.9),(53,1.2,2.4,2.6),(54.8,.5,2.6,3),(56.5,.3,2.8,3),(59,.1,2.6,2.6),(60.6,0,1.6,1.8),(61,0,.12,.15)]))
 for sign in (-1,1):
  s.oval(f'detail_socket_{sign}',(2.96,sign*1.5,56.1),(.23,.86,.78),'dark',24,14)
  s.strand(f'head_brow_{sign}',[(3.05,sign*.55,56.9,.32),(3.05,sign*1.4,57.1,.40),(2.25,sign*2.45,56.85,.25)],'body',14,4)
  s.strand(f'head_cheek_{sign}',[(2.4,sign*2.3,55.2,.42),(3.15,sign*1.9,54.5,.40),(3.1,sign*.9,53.3,.19)],'body',14,4)
  s.oval(f'head_ear_{sign}',(-.1,sign*2.85,55.4),(.7,.7,1.1),'body',18,12)
  s.strand(f'detail_nostril_{sign}',[(3.8,sign*.3,54.6,.17),(3.5,sign*.5,54.3,.10)],'dark',10)
  # Ribs and clavicles are skin-covered ridges fused into the body.
  for i in range(6):
   z=37.2+i*1.35;ry=4.7+(z-37)*.17;rx=2.8+(z-37)*.13
   s.strand(f'torso_rib_{sign}_{i}',[(rx*math.cos(a)-.5,sign*ry*math.sin(a),z-1.1*math.sin(a)+.16*sign*math.sin(i),.19+.10*math.cos(a)) for a in [j*1.45/10 for j in range(11)]],'body',10,2)
  s.strand(f'torso_clavicle_{sign}',[(2.6,0,46,.33),(2.6,sign*2.8,46.4,.4),(.4,sign*5.7,45.8,.45)],'body',12,3)
 s.strand('head_nose',[(2.9,0,56.2,.34),(3.7,0,54.65,.45),(3.5,0,54.3,.3)],'body',14)
 s.oval('detail_mouth',(3.85,0,52.6),(.26,1.35,.52),'dark',24,12)
 for i in range(7):
  y=(i-3)*.34
  s.strand(f'detail_tooth_{i}',[(4.09,y,52.9,.15),(4.10,y,52.35+(.16 if i%2 else 0),.08)],'bone',8)
 for i in range(7):s.oval(f'torso_spine_{i}',(-2.1-.11*i,0,32+i*2),( .38,.5,.53),'body',12,8)
 for side,sign in (('L',1),('R',-1)):
  s.oval(f'shoulder_{side}',(0,sign*5.8,45),(1.9,2,2.3))
  for limb in ('arm','leg'):
   points=[REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
   rs=(1.35,1.05,.72) if limb=='arm' else (1.9,1.3,.8)
   s.strand(f'{limb}_{side}',[(*p,r) for p,r in zip(points,rs)],sides=18,samples=5)
   s.oval(f'{limb}_{side}_joint',points[1],(rs[1]*1.15,rs[1]*1.2,rs[1]*1.3),'body',18,12)
  s.oval(f'foot_{side}',(1.7,sign*5.1,1.6),(3.5,1.35,1.35),'body',24,12)
  s.oval(f'hand_{side}_palm',(6.5,sign*8.3,31),(1.7,1.5,.8),'body',20,12)
  for i in range(4):
   y=sign*(7.15+i*.76);reach=11.5-(abs(i-1.5)*.65)
   s.strand(f'hand_{side}_finger{i}',[(6.7,y,31,.36),(8.5,y+sign*.18,31.5,.30),(reach,y+sign*.32,30.8,.22)],'body',10,4)
   s.strand(f'nail_{side}_{i}',[(reach-.2,y+sign*.32,30.85,.25),(reach+1.7,y+sign*.45,30.3,.18),(reach+2.8,y+sign*.5,29.4,.025)],'bone',10,4)
  s.strand(f'hand_{side}_thumb',[(5.8,sign*7.4,31,.5),(7,sign*6.2,31.1,.36),(8.4,sign*5.8,30.4,.23)],'body',12,4)
  s.strand(f'nail_{side}_thumb',[(8.3,sign*5.8,30.4,.23),(10,sign*5.5,29.8,.17),(10.7,sign*5.7,28.9,.025)],'bone',10,4)
 # Small ragged wrap avoids a generic robe silhouette; legs and pelvis remain legible.
 for i in range(12):
  a=math.tau*i/12
  s.strand(f'cloth_strip_{i}',[(2.65*math.cos(a),4.45*math.sin(a),29.8,.63),(2.85*math.cos(a),4.6*math.sin(a),27,.7),(3*math.cos(a),4.7*math.sin(a),24+(i%3),.06)],'cloth',10,3)
 return wraith_materials.repack(s.parts)

def weights(part,v,uv):
 n=part.name
 if n.startswith('nail_'):return [(IDS[f"arm_{n.split('_')[1]}_end"],1)]
 if n.startswith('cloth'):return [(IDS['pelvis'],1)]
 if n.startswith(('head','detail','hair')):return [(IDS['head'],1)]
 if n.startswith('shoulder_'):
  t=max(0,min(1,(abs(v[1])-4)/3));return [(IDS['spine'],1-t),(IDS[f'arm_{n[-1]}_upper'],t)]
 if n.startswith(('hand_','foot_')):return [(IDS[f'{"arm" if n.startswith("hand") else "leg"}_{n.split("_")[1]}_end'],1)]
 if n.startswith(('arm_','leg_')):return RIG.chain_weights(v,[IDS['_'.join(n.split('_')[:2])+'_'+j] for j in ('upper','lower','end')])
 if n=='pelvis':return [(IDS['pelvis'],1)]
 if n.startswith('torso'):
  if v[2]<35:return RIG.chain_weights(v,[IDS['pelvis'],IDS['spine']])
  t=max(0,min(1,(v[2]-46)/6));return [(IDS['spine'],1-t),(IDS['neck'],t)]
 return RIG.chain_weights(v,[IDS[b] for b in ('pelvis','spine','neck','head')])

def solve_leg(side,target,rotations):
 ids=[IDS[f'leg_{side}_{j}'] for j in ('upper','lower','end')]
 hip,knee,foot=[REST[i] for i in ids];a=math.dist(hip,knee);b=math.dist(knee,foot);distance=math.dist(target,hip)
 if not abs(a-b)<distance<a+b:raise ValueError(('unreachable wraith foot',side,target,distance,a+b))
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
  turn('spine',(0,1,0),.45*math.sin(phase));turn('head',(0,0,1),3*math.sin(phase));turn('arm_L_lower',(0,1,0),3*math.sin(phase))
 elif name=='advance':
  for side,offset in (('L',0),('R',.5)):
   q=(t+offset)%1
   if q<.6:dx=2-4*q/.6;lift=0
   else:u=(q-.6)/.4;dx=-2+4*u;lift=2*math.sin(math.pi*u)
   solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(dx,0,lift)),rot)
   turn(f'arm_{side}_upper',(0,1,0),4*math.cos(phase+offset*math.tau))
  turn('spine',(0,0,1),2*math.sin(phase))
 elif name in ('rake','clutch'):
  wind=math.sin(math.pi*min(1,t/.4))**2;hit=math.sin(math.pi*max(0,(t-.22)/.78))**2
  turn('arm_R_upper',(0,1,0),-18*wind-48*hit)
  turn('arm_R_lower',(0,1,0),-8*wind-20*hit)
  turn('arm_R_end',(0,1,0),(15*wind+25*hit) if name=='rake' else 35*hit)
  turn('spine',(0,0,1),(10 if name=='rake' else -5)*hit)
  turn('arm_L_upper',(0,1,0),(-24 if name=='rake' else -48)*hit);turn('head',(0,1,0),(5 if name=='rake' else 25)*hit)
 elif name=='recoil':
  turn('spine',(0,1,0),-11*pulse);turn('head',(0,0,1),-10*pulse);turn('arm_R_lower',(0,1,0),-12*pulse)
 elif name=='fall':
  s=min(1,t/.88);s=s*s*(3-2*s)
  shift[IDS['pelvis']]=(-4*s,0,-15*s)
  for side in ('L','R'):solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(4*s,0,15*s)),rot)
  turn('spine',(0,1,0),70*s);turn('neck',(0,1,0),12*s);turn('head',(0,1,0),35*s)
  turn('arm_R_upper',(0,1,0),-60*s);turn('arm_R_lower',(0,1,0),-25*s);turn('arm_R_end',(0,1,0),12*s)
  turn('arm_L_upper',(0,1,0),-45*s);turn('arm_L_lower',(0,1,0),-15*s);turn('arm_L_end',(0,1,0),12*s)
 if name not in ('advance','fall'):
  shift[IDS['pelvis']]=(-.3,0,-.8)
  for side,dx in (('L',1.8),('R',-1.8)):
   solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(dx+.3,0,.8)),rot)
 return [(*add(local,shift[i]),*rot[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]

def geometry():
 from .connected_skin import attach
 return assemble(wraith_materials.connected_atlas(attach('wraith',build_parts(),weights)),weights)
def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():
 from .connected_skin import attach
 return wraith_materials.connected_atlas(attach('wraith',build_parts(),weights),True)
def build():
 skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
 parts,v,n,uv,tr,w=geometry();clips,bounds=animation_data(v,w)
 data=iqm.encode(v,n,uv,tr,w,BONES,clips,bounds,mesh_label='Project_Broom_wraith',material_path=SKIN)
 path=ROOT/'mod/BrogueDoom/models/monsters/24_wraith.iqm';path.write_bytes(data)
 manifest=dict(schemaVersion=1,workId='BRG-M24',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],parts=len(parts),vertices=len(v),triangles=len(tr),boneCount=len(BONES),bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],poseBounds=bounds,authoringSource='assets/monsters/wraith/wraith-animated.blend')
 out=ROOT/'assets/monsters/wraith';out.mkdir(exist_ok=True);(out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':print(build()['sha256'])

