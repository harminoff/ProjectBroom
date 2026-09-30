"""Original lean dar swordsman. Reusable elven anatomy; cosmetic motion only."""
import hashlib,json,math
from . import iqm,dar_materials
from .creatures import Sculpt
from .rat import ROOT,Part,add,sub,mul,unit
from .skeletal import Rig,axis,between,inverse,qmul,assemble,sample_clips
SKIN='graphics/BRGDAR.png'
SPECS=[('root',None,(0,0,0)),('pelvis','root',(0,0,28)),('spine','pelvis',(-.5,0,40)),
       ('neck','spine',(0,0,49)),('head','neck',(.2,0,55))]
for side,sign in (('L',1),('R',-1)):
 for limb,parent,points in (
  ('arm','spine',[(0,sign*6.3,45.5),(1,sign*8.2,36.5),(6,sign*8.3,31)]),
  ('leg','pelvis',[(0,sign*3.6,28),(2,sign*4.4,15),(0,sign*5.1,2.4)])):
  for joint,point in zip(('upper','lower','end'),points):
   name=f'{limb}_{side}_{joint}';SPECS.append((name,parent,point));parent=name
SPECS.append(('sword','arm_R_end',(6,-8.3,31)))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('advance',32,35,True),('slash',24,35,False),('thrust',26,35,False),('recoil',14,35,False),('fall',36,35,False)]

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
 s.oval('pelvis',(0,0,28),(3.7,5,4.5))
 s.parts.append(rings('torso',[(27,0,3.5,4.8),(31,0,3.1,4.1),(35,-.4,3.1,4.2),(40,-.5,3.6,5.4),(44,-.3,3.8,6.2),(46,0,3,5.6),(48,0,2,2.4),(52,0,1.8,1.8)]))
 s.parts.append(rings('head_cranium',[(50.4,1,1,1.4),(51.3,1,1.9,2),(52.7,.6,2.5,2.5),(54.5,.1,2.9,3.1),(56,.1,2.95,3.1),(58,-.1,2.8,2.8),(59.6,-.3,2,2.1),(60.2,-.4,.15,.2)]))
 for sign in (-1,1):
  s.strand(f'head_ear_{sign}',[(-.4,sign*2.5,55.6,1.05),(-1.2,sign*4.2,56.5,.85),(-2.8,sign*6.7,58.4,.06)],'body',14,4)
  s.strand(f'detail_ear_{sign}',[(.15,sign*3.1,55.7,.19),(-.5,sign*4.1,56.4,.23),(-2,sign*5.7,57.6,.04)],'accent',10)
  s.oval(f'detail_eye_socket_{sign}',(2.65,sign*1.6,55.8),(.17,.67,.29),'dark',18,10)
  s.oval(f'detail_eye_iris_{sign}',(2.83,sign*1.6,55.8),(.06,.23,.19),'accent',14,8)
  s.strand(f'head_brow_{sign}',[(2.9,sign*.8,56.45,.26),(2.78,sign*1.65,56.6,.32),(2.23,sign*2.4,56.7,.2)],'body',12)
  s.strand(f'detail_brow_{sign}',[(3,sign*.8,56.64,.09),(2.88,sign*1.7,56.79,.12),(2.3,sign*2.4,56.8,.07)],'dark',8)
 s.strand('detail_mouth',[(3.12,-1.05,52.9,.10),(3.48,0,52.78,.11),(3.12,1.05,52.9,.10)],'dark',10)
 # Swept strands leave the face, narrow chin and ear points readable.
 for i in range(13):
  y=(i-6)*.45; crown=(abs(y)/2.7)**2
  s.strand(f'hair_sweep_{i}',[(1.8,y,58.5-1.2*crown,.38),(.1,y*1.05,60.3-1.6*crown,.56),(-2.3,y*1.02,59.1-1.3*crown,.52),(-2.8,y*.9,54.6-.6*crown,.42),(-2.5,y*.7,51.2+1.1*crown,.06)],'dark',10,4)
 for side,sign in (('L',1),('R',-1)):
  s.oval(f'shoulder_{side}',(0,sign*5.8,45),(2.6,2.6,3))
  for limb in ('arm','leg'):
   points=[REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
   rs=(2.1,1.5,1.1) if limb=='arm' else (2.8,1.9,1.25)
   s.strand(f'{limb}_{side}',[(*p,r) for p,r in zip(points,rs)],sides=18,samples=5)
  s.oval(f'foot_{side}',(1.7,sign*5.1,1.6),(3.5,1.8,1.45),'body',24,12)
  s.oval(f'hand_{side}_palm',(6,sign*8.3,31),(1.5,1.65,1.7),'body',20,12)
  for i in range(4):
   z=29.9+i*.7
   if side=='R':pts=[(5.3,-9.3,z,.4),(6.9,-9.35,z,.42),(7.1,-8.3,z,.4),(6.7,-7.6,z,.35),(5.9,-7.7,z,.28)]
   else:pts=[(6,7.2+i*.68,30.5,.37),(6.7,7.2+i*.68,28.8,.34),(7,7.2+i*.68,28.3,.23)]
   s.strand(f'hand_{side}_finger{i}',pts,'body',10,3)
  s.strand(f'hand_{side}_thumb',[(4.8,sign*7.4,32,.5),(6.5,sign*6.8,32,.43),(7,sign*7.6,31.5,.28)],'body',10)
  s.oval(f'armor_shoulder_{side}',(-.15,sign*6.3,45.8),(2.5,2.8,1.55),'bone',24,12)
  for k in range(2):
   s.strand(f'armor_trim_shoulder_{side}_{k}',[(1.9,sign*(5+k),45.7,.12),(1.5,sign*(6.5+k),46.8,.12),(-1,sign*(7+k),46.4,.12)],'bone',8)
  # Close fitting forearm/bracer volumes remain attached to their limb.
  s.strand(f'armor_bracer_{side}',[(2.4,sign*8.2,35.2,1.6),(4.9,sign*8.3,32.3,1.3)],'bone',18,3)
 s.parts.append(rings('armor_collar',[(44.8,-.1,4.1,6.8),(46.5,0,3.55,5.3),(48.1,0,2.25,2.75)],40))
 # Shaped cuirass follows the anatomical chest, with segmented lower plates.
 for z,rx,ry in [(39,4.25,5.75),(42,4.45,6.55),(44.2,4.2,6.6)]:
  s.parts.append(rings(f'armor_chest_{z}',[(z-.8,-.25,rx,ry),(z+.8,-.25,rx,ry)],40))
  s.strand(f'armor_trim_chest_{z}',[(-.25+rx*math.cos(a),ry*math.sin(a),z-.8,.10) for a in [math.tau*j/48 for j in range(49)]],'bone',6,1)
 s.parts.append(rings('sash_waist',[(29.5,0,3.95,4.8),(32,0,3.65,4.5)],40))
 s.strand('sash_knot',[(3.85,2.2,30.7,.6),(4.3,2.4,27,.55),(4.7,3,23,.25)],'cloth',12)
 # Narrow diamond-section blade, crossguard and leather grip, upright at rest.
 s.strand('sword_grip',[(6,-8.3,28.3,.53),(6,-8.3,33.6,.53)],'wood',16)
 s.oval('sword_pommel',(6,-8.3,28.1),(.8,.75,.8),'bone',16,10)
 s.strand('sword_guard',[(6,-11.2,34,.26),(6.2,-8.3,33.8,.35),(6,-5.4,34,.26)],'bone',12)
 p=Part('sword_blade');rows=[(34,1.1),(36,1.2),(53,.83),(60,.05)]
 for j,(z,w) in enumerate(rows):
  for i,(dx,dy) in enumerate(((.22,0),(0,-w),(-.22,0),(0,w))):p.vertex((6+dx,-8.3+dy,z),'claw',i/4,j/3)
 for j in range(3):
  for i in range(4):a=j*4+i;b=j*4+(i+1)%4;p.faces.append((a,b,b+4,a+4))
 p.faces.extend(((3,2,1,0),(12,13,14,15)));s.parts.append(p)
 return dar_materials.repack(s.parts)

def weights(part,v,uv):
 n=part.name
 if n.startswith('sword'):return [(IDS['sword'],1)]
 if n.startswith('sash'):return [(IDS['pelvis'],1)]
 if n.startswith(('head','detail','hair')):return [(IDS['head'],1)]
 if n.startswith('armor_bracer'):return [(IDS[f'arm_{n[-1]}_lower'],1)]
 if n.startswith('armor'):return [(IDS['spine'],1)]
 if n.startswith('shoulder_'):
  t=max(0,min(1,(abs(v[1])-4)/3));return [(IDS['spine'],1-t),(IDS[f'arm_{n[-1]}_upper'],t)]
 if n.startswith(('hand_','foot_')):return [(IDS[f'{"arm" if n.startswith("hand") else "leg"}_{n.split("_")[1]}_end'],1)]
 if n.startswith(('arm_','leg_')):return RIG.chain_weights(v,[IDS[n+'_'+j] for j in ('upper','lower','end')])
 if n=='pelvis':return [(IDS['pelvis'],1)]
 if n=='torso':
  if v[2]<35:return RIG.chain_weights(v,[IDS['pelvis'],IDS['spine']])
  t=max(0,min(1,(v[2]-46)/6));return [(IDS['spine'],1-t),(IDS['neck'],t)]
 return RIG.chain_weights(v,[IDS[b] for b in ('pelvis','spine','neck','head')])

def solve_leg(side,target,rotations):
 ids=[IDS[f'leg_{side}_{j}'] for j in ('upper','lower','end')]
 hip,knee,foot=[REST[i] for i in ids];a=math.dist(hip,knee);b=math.dist(knee,foot);distance=math.dist(target,hip)
 if not abs(a-b)<distance<a+b:raise ValueError(('unreachable dar foot',side,target,distance,a+b))
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
 elif name in ('slash','thrust'):
  wind=math.sin(math.pi*min(1,t/.4))**2;hit=math.sin(math.pi*max(0,(t-.22)/.78))**2
  turn('arm_R_upper',(0,1,0),-15*wind+18*hit)
  turn('arm_R_lower',(0,1,0),-10*wind+10*hit)
  turn('arm_R_end',(0,1,0),(-15*wind+34*hit) if name=='slash' else 40*hit)
  turn('spine',(0,0,1),(10 if name=='slash' else -5)*hit)
  turn('arm_L_upper',(0,1,0),-18*hit);turn('head',(0,1,0),5*hit)
 elif name=='recoil':
  turn('spine',(0,1,0),-11*pulse);turn('head',(0,0,1),-10*pulse);turn('arm_R_lower',(0,1,0),-12*pulse)
 elif name=='fall':
  s=min(1,t/.88);s=s*s*(3-2*s)
  shift[IDS['pelvis']]=(-4*s,0,-15*s)
  for side in ('L','R'):solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(4*s,0,15*s)),rot)
  turn('spine',(0,1,0),70*s);turn('neck',(0,1,0),12*s);turn('head',(0,1,0),35*s)
  turn('arm_R_upper',(0,1,0),-60*s);turn('arm_R_lower',(0,1,0),-25*s);turn('arm_R_end',(0,1,0),-73*s)
  turn('arm_L_upper',(0,1,0),-45*s);turn('arm_L_lower',(0,1,0),-15*s)
 if name not in ('advance','fall'):
  shift[IDS['pelvis']]=(-.3,0,-.8)
  for side,dx in (('L',1.8),('R',-1.8)):
   solve_leg(side,add(REST[IDS[f'leg_{side}_end']],(dx+.3,0,.8)),rot)
 return [(*add(local,shift[i]),*rot[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]

def geometry():
 from .connected_skin import attach
 return assemble(dar_materials.connected_atlas(attach('dar_blademaster',build_parts(),weights)),weights)
def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():
 from .connected_skin import attach
 return dar_materials.connected_atlas(attach('dar_blademaster',build_parts(),weights),True)
def build():
 skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
 parts,v,n,uv,tr,w=geometry();clips,bounds=animation_data(v,w)
 data=iqm.encode(v,n,uv,tr,w,BONES,clips,bounds,mesh_label='Project_Broom_dar_blademaster',material_path=SKIN)
 path=ROOT/'mod/BrogueDoom/models/monsters/31_dar_blademaster.iqm';path.write_bytes(data)
 manifest=dict(schemaVersion=1,workId='BRG-M31',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],parts=len(parts),vertices=len(v),triangles=len(tr),boneCount=len(BONES),bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],poseBounds=bounds,authoringSource='assets/monsters/dar_blademaster/dar-blademaster-animated.blend')
 out=ROOT/'assets/monsters/dar_blademaster';out.mkdir(exist_ok=True);(out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':print(build()['sha256'])

