"""Original ritual corpse with hanging flesh shreds, exposed bones and a slack jaw. Cosmetic only."""
import hashlib,json,math
from . import iqm,zombie_materials
from .creatures import Sculpt
from .rat import ROOT,Part,add,sub,mul,unit
from .skeletal import Rig,axis,between,inverse,qmul,assemble,sample_clips
SKIN='graphics/BRGZOMB.png'
SPECS=[('root',None,(0,0,0)),('pelvis','root',(0,0,28)),('spine','pelvis',(-.5,0,40)),
       ('neck','spine',(0,0,49)),('head','neck',(.2,0,55)),('jaw','head',(3,0,52.6))]
for side,sign in (('L',1),('R',-1)):
 for limb,parent,points in (
  ('arm','spine',[(0,sign*6.3,45.5),(1,sign*8.2,36.5),(6,sign*8.3,31)]),
  ('leg','pelvis',[(0,sign*3.6,28),(2,sign*4.4,15),(0,sign*5.1,2.4)])):
  for joint,point in zip(('upper','lower','end'),points):
   name=f'{limb}_{side}_{joint}';SPECS.append((name,parent,point));parent=name

RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('shamble',32,35,True),('strike',24,35,False),('bite',26,35,False),('recoil',14,35,False),('fall',36,35,False)]

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
 s.oval('pelvis',(0,0,28),(3.4,5.1,4.1))
 s.parts.append(rings('torso',[(27,0,3.1,4.8),(31,.2,3.2,4.6),(35,0,3.9,5.2),(39,-.4,4.1,6.2),(43,-.6,4.2,6.7),(46,-.2,3.5,6.4),(48,.2,1.7,2),(52,.6,1.5,1.9)]))
 s.parts.append(rings('head_cranium',[(50.5,1.2,1.4,1.8),(52,1.2,2.2,2.7),(54,.7,3,3.3),(56,.4,3.3,3.4),(58.7,0,2.9,3.1),(60.8,-.1,1.8,2),(61.3,0,.15,.2)]))
 for sign in (-1,1):
  s.oval(f'detail_socket_{sign}',(3.48,sign*1.55,56.1),(.34,.93,.83),'dark',20,12)
  s.oval(f'detail_eye_{sign}',(3.77,sign*1.55,56.1),(.3,.5,.43),'dark',20,12)
  s.strand(f'head_brow_{sign}',[(3.25,sign*.5,57,.4),(3.5,sign*1.4,57.1,.45),(2.4,sign*2.8,56.8,.32)],'body',14,4)
  s.strand(f'head_cheek_{sign}',[(2.7,sign*2.7,55.2,.6),(3.5,sign*2.1,54.4,.5),(3.7,sign*.9,53.5,.22)],'body',14,4)
  if sign==1:s.oval('head_ear_L',(-.3,3.3,55.3),(.7,.8,1.05),'body',18,12)
  else:s.oval('head_ear_stump_R',(-.2,-3.2,55),(.65,.48,.5),'body',18,12)
  s.strand(f'detail_nostril_{sign}',[(4.15,sign*.35,54.6,.25),(3.9,sign*.55,54.3,.13)],'dark',10)
 s.strand('head_nose_stump',[(3.3,0,56.1,.4),(4.05,0,54.7,.45)],'body',14)
 # A projecting open mouth, hinged jaw and visible asymmetric teeth.
 s.oval('detail_mouth',(4.1,0,52.9),(.4,1.55,1),'dark',24,12)
 s.oval('jaw_lower',(3.5,0,51.75),(1,1.9,.62),'body',24,12)
 for i in range(7):
  y=(i-3)*.4
  s.strand(f'detail_tooth_{i}',[(4.45,y,53.65,.17),(4.48,y,53.0+(.2 if i%3 else 0),.10)],'bone',8)
 for i in range(5):
  y=(i-2)*.5
  s.strand(f'jaw_tooth_{i}',[(4.4,y,52,.18),(4.48,y,52.6-(.2 if i%2 else 0),.09)],'bone',8)
 # Ragged dark recess with individual rib arcs on the right front of the chest.
 s.oval('wound_chest',(3.9,-2.1,40.4),(.65,2.65,4.15),'dark',24,14)
 for j in range(5):
  z=37.4+j*1.35
  s.strand('bone_rib_'+str(j),[(4.45,-.4,z,.28),(4.6,-1.6,z-.25,.33),(4.1,-3.4,z-.75,.28),(2.6,-5.5,z-1,.16)],'bone',12,3)
 s.strand('bone_clavicle',[ (3.3,.5,46.4,.4),(3.35,3.5,46.7,.5),(1.5,5.6,46,.3)],'bone',12,3)
 for side,sign in (('L',1),('R',-1)):
  s.oval(f'shoulder_{side}',(0,sign*5.9,45),(2.2,2.4,2.6))
  for limb in ('arm','leg'):
   points=[REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
   rs=((1.85,1.45,1.05) if side=='L' else (1.65,1.25,.94)) if limb=='arm' else ((2.45,1.65,1) if side=='L' else (2.1,1.45,.9))
   s.strand(f'{limb}_{side}',[(*pt,r) for pt,r in zip(points,rs)],sides=20,samples=5)
   s.oval(f'{limb}_{side}_joint',points[1],(rs[1]*1.05,rs[1]*1.08,rs[1]*1.12),'body',18,12)
  s.oval(f'foot_{side}',(1.7,sign*5.1,1.55),(3.5,1.6,1.3),'body',24,12)
  s.oval(f'hand_{side}_palm',(6.4,sign*8.3,31),(1.5,1.6,1),'body',20,12)
  for i in range(4):
   y=sign*(7.1+i*.8);reach=9.9-abs(i-1.5)*.45
   s.strand(f'hand_{side}_finger{i}',[(6.7,y,31,.43),(8.3,y+sign*.1,31,.38),(reach,y+sign*.2,30.2,.27)],'body',10,4)
   s.oval(f'nail_{side}_{i}',(reach-.1,y+sign*.2,30.45),(.48,.28,.12),'bone',10,6)
  s.strand(f'hand_{side}_thumb',[(5.8,sign*7.4,31,.6),(6.9,sign*6.4,30.7,.4),(7.9,sign*6.1,30,.29)],'body',12,4)
  s.oval(f'nail_{side}_thumb',(7.7,sign*6.1,30.2),(.42,.3,.12),'bone',10,6)
 # Exposed forearm and shin bone are accessories emerging from dark ragged wounds.
 for name,bone,pts in [('forearm','arm_R_lower',[(2.3,-9,35,.42),(4.7,-9,32,.34)]),('shin','leg_L_lower',[(3.2,4.5,15,.45),(1.7,5.1,6,.35)])]:
  s.strand('wound_'+name,[(*q[:3],q[3]+.45) for q in pts],'dark',12,4);s.parts[-1].anchor=bone
  s.strand('bone_'+name,pts,'bone',12,4);s.parts[-1].anchor=bone
 # Thick closed tapering tissue ribbons: rooted in the skin, hanging under gravity.
 def flap(name,root,tip,width,bone):
  a=root;b=((root[0]+tip[0])*.5+.7,(root[1]+tip[1])*.5,(root[2]+tip[2])*.5)
  p=Part('flesh_'+name)
  for j,(c,w) in enumerate(((a,width),(b,width*.78),(tip,width*.06))):
   for dx,dy in ((-.15,-w),(.15,-w),(.15,w),(-.15,w)):
    p.vertex((c[0]+dx,c[1]+dy,c[2]),'fur',.05 if dx<0 else .95,j/2)
  p.faces=[(3,2,1,0),(8,9,10,11)]
  for j in range(2):
   for i in range(4):p.faces.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
  p.anchor=bone;s.parts.append(p)
 for j in range(5):flap('chest_'+str(j),(4.3,-.4-j*.75,44.4-j*.15),(5.3,-.8-j*.85,35.5+(j%3)),.38+(j%2)*.2,'spine')
 for j in range(3):flap('abdomen_'+str(j),(3.7,-1.5+j*1.5,34.5),(4.6,-2+j*1.6,28.5+(j%2)),.58,'pelvis')
 for j in range(3):flap('shoulder_'+str(j),(1.3,5.9+j*.6,45.8),(2.5,6.3+j*.8,38.5+j),.5,'arm_L_upper')
 flap('cheek',(3.7,-2.2,54.6),(4.6,-2.4,49.5),.42,'head')
 flap('jaw',(3.9,1.3,52.4),(4.3,1.6,49.2),.4,'jaw')
 flap('forearm',(2.1,-8.5,36),(4.5,-9.2,30),.5,'arm_R_lower')
 flap('shin',(3.1,4.7,14.8),(3.2,5.3,7.2),.65,'leg_L_lower')
 for j in range(3):flap('back_'+str(j),(-4,-2+j*2,43),(-4.8,-2.5+j*2.1,36+j),.65,'spine')
 for i in range(10):
  a=math.tau*i/10
  s.strand(f'cloth_strip_{i}',[(3.5*math.cos(a),5.25*math.sin(a),29.7,.7),(3.65*math.cos(a),5.35*math.sin(a),26.5,.75),(3.9*math.cos(a),5.6*math.sin(a),23+i%3,.07)],'cloth',10,3)
 return zombie_materials.repack(s.parts)

def weights(part,v,uv):
 n=part.name
 if hasattr(part,'anchor'):return [(IDS[part.anchor],1)]
 if n.startswith('jaw'):return [(IDS['jaw'],1)]
 if n.startswith(('wound_chest','bone_rib','bone_clavicle')):return [(IDS['spine'],1)]
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
 if not abs(a-b)<distance<a+b:raise ValueError(('unreachable zombie foot',side,target,distance,a+b))
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
 elif name=='shamble':
  for side,offset in (('L',0),('R',.5)):
   q=(t+offset)%1
   if q<.6:dx=2-4*q/.6;lift=0
   else:u=(q-.6)/.4;dx=-2+4*u;lift=2*math.sin(math.pi*u)
   solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(dx,0,lift)),rot)
   turn(f'arm_{side}_upper',(0,1,0),4*math.cos(phase+offset*math.tau))
  turn('spine',(0,0,1),2*math.sin(phase))
 elif name in ('strike','bite'):
  wind=math.sin(math.pi*min(1,t/.4))**2;hit=math.sin(math.pi*max(0,(t-.22)/.78))**2
  turn('arm_R_upper',(0,1,0),-18*wind-48*hit)
  turn('arm_R_lower',(0,1,0),-8*wind-20*hit)
  turn('arm_R_end',(0,1,0),(15*wind+25*hit) if name=='strike' else 35*hit)
  turn('spine',(0,0,1),(10 if name=='strike' else -5)*hit)
  turn('arm_L_upper',(0,1,0),(-24 if name=='strike' else -48)*hit);turn('head',(0,1,0),(5 if name=='strike' else 25)*hit)
  if name=='bite':turn('jaw',(0,1,0),28*hit)
 elif name=='recoil':
  turn('spine',(0,1,0),-11*pulse);turn('head',(0,0,1),-10*pulse);turn('arm_R_lower',(0,1,0),-12*pulse)
 elif name=='fall':
  s=min(1,t/.88);s=s*s*(3-2*s)
  shift[IDS['pelvis']]=(-4*s,0,-15*s)
  for side in ('L','R'):solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(4*s,0,15*s)),rot)
  turn('spine',(0,1,0),73*s);turn('neck',(0,1,0),12*s);turn('head',(0,1,0),35*s)
  turn('arm_R_upper',(0,1,0),-60*s);turn('arm_R_lower',(0,1,0),-25*s);turn('arm_R_end',(0,1,0),12*s)
  turn('arm_L_upper',(0,1,0),-45*s);turn('arm_L_lower',(0,1,0),-15*s);turn('arm_L_end',(0,1,0),12*s)
 if name=='fall':turn('jaw',(0,1,0),18*s)
 if name not in ('shamble','fall'):
  shift[IDS['pelvis']]=(-.3,0,-.8)
  for side,dx in (('L',1.8),('R',-1.8)):
   solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(dx+.3,0,.8)),rot)
 return [(*add(local,shift[i]),*rot[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]

def geometry():
 from .connected_skin import attach
 return assemble(zombie_materials.connected_atlas(attach('zombie',build_parts(),weights)),weights)
def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():
 from .connected_skin import attach
 return zombie_materials.connected_atlas(attach('zombie',build_parts(),weights),True)
def build():
 skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
 parts,v,n,uv,tr,w=geometry();clips,bounds=animation_data(v,w)
 data=iqm.encode(v,n,uv,tr,w,BONES,clips,bounds,mesh_label='Project_Broom_zombie',material_path=SKIN)
 path=ROOT/'mod/BrogueDoom/models/monsters/25_zombie.iqm';path.write_bytes(data)
 manifest=dict(schemaVersion=1,workId='BRG-M25',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],parts=len(parts),vertices=len(v),triangles=len(tr),boneCount=len(BONES),bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],poseBounds=bounds,authoringSource='assets/monsters/zombie/zombie-animated.blend')
 out=ROOT/'assets/monsters/zombie';out.mkdir(exist_ok=True);(out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':print(build()['sha256'])


