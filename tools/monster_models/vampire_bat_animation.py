"""Original connected vampire bat, six purely cosmetic skeletal roles."""
import math,hashlib,json
from . import iqm, vampire_bat_materials as materials
from .creatures import Sculpt
from .rat import ROOT,Part,add,sub
from .skeletal import Rig,axis,assemble,sample_clips
SKIN=materials.SKIN
SPECS=[('root',None,(0,0,0)),('torso','root',(-2,0,23)),('head','torso',(5,0,25)),('jaw','head',(7,0,23))]
for side,s in [('L',1),('R',-1)]:
 SPECS += [(f'ear_{side}','head',(4,s*3,28)),(f'arm_{side}','torso',(0,s*4,23)),(f'hand_{side}',f'arm_{side}',(5,s*13,23)),(f'fingers_{side}',f'hand_{side}',(1,s*21,21)),(f'leg_{side}','torso',(-7,s*3,20))]
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
CLIPS=[('idle',32,28,True),('fly',24,35,True),('nip',18,35,False),('feed',24,35,False),('recoil',12,35,False),('death',30,35,False)]

def membrane(s,side,sign):
 # A closed, thickened scalloped membrane joins the muscular arm and hind ankle.
 outline=[(1,3,23),(5,13,23),(13,28,22),(3,24,21),(-2,28,20),(-5,21,20),(-12,21,19),(-8,12,19),(-10,6,18),(-7,3,20)]
 center=(0,11,21);p=Part('wing_'+side);n=len(outline);rings=7
 for top in (-1,1):
  for i in range(rings):
   t=(i+1)/rings
   for j,b in enumerate(outline):
    x=center[0]*(1-t)+b[0]*t;y=center[1]*(1-t)+b[1]*t
    z=center[2]*(1-t)+b[2]*t+top*.36+(.32*math.sin(t*math.pi))
    p.vertex((x,sign*y,z),'ear',.08+.84*(x+11)/22,.08+.84*y/30)
  p.vertex((center[0],sign*center[1],center[2]+top*.36),'ear',.5,.5)
 stride=rings*n+1
 for k in range(2):
  base=k*stride
  for j in range(n):
   p.faces.append((base+rings*n,base+(j+1)%n,base+j) if k==0 else (base+rings*n,base+j,base+(j+1)%n))
  for i in range(rings-1):
   for j in range(n):
    a=base+i*n+j;b=base+i*n+(j+1)%n;c=b+n;d=a+n
    p.faces.append((a,d,c,b) if k==0 else (a,b,c,d))
 for j in range(n):
  a=(rings-1)*n+j;b=(rings-1)*n+(j+1)%n;p.faces.append((a,b,b+stride,a+stride))
 if sign<0:p.faces=[tuple(reversed(f)) for f in p.faces]
 s.parts.append(p)

def build_parts():
 s=Sculpt();s.oval('body',(-3,0,23),(8,4.4,4.8),seg=28,rings=18)
 s.oval('chest',(1,0,24),(5.5,5,5),seg=28,rings=18)
 s.oval('head',(5.4,0,25.5),(3.7,4.5,3.5),seg=28,rings=18)
 s.oval('muzzle',(7.9,0,24.6),(1.6,3.25,1.55),seg=24,rings=14)
 s.oval('jaw',(7.8,0,23.1),(1.5,2.8,.75),seg=24,rings=12)
 s.oval('nose',(9.0,0,25.1),(.58,2.4,1.05),'accent',20,12)
 s.strand('tail',[(-9,0,22,1),(-13,0,20,.6),(-14,0,19,.08)],'accent',12,4)
 for side,sign in [('L',1),('R',-1)]:
  s.oval('ear_'+side,(3.8,sign*4.0,29.3),(1.55,3.1,3.25),seg=24,rings=16)
  s.oval('ear_inner_'+side,(5.28,sign*4.0,29.5),(.15,2.2,2.5),'accent',24,16)
  s.strand('ear_tragus_'+side,[(5.4,sign*2.4,27,.72),(5.75,sign*2.8,28.8,.6),(5.5,sign*3.3,30,.10)],'accent',10,3)
  s.oval('eye_'+side,(8.0,sign*3.35,26.4),(.42,.60,.55),'dark',20,12)
  s.oval('nostril_'+side,(9.56,sign*1.25,25.2),(.10,.55,.3),'dark',12,8)
  s.strand('mouth_'+side,[(9.15,sign*.3,23.45,.14),(9.0,sign*1.7,23.45,.16),(7.9,sign*2.85,23.65,.12)],'dark',8,3)
  s.strand('fang_'+side,[(9.0,sign*1.7,23.5,.40),(9.15,sign*1.7,22.3,.22),(8.95,sign*1.7,21.8,.025)],'bone',12,3)
  s.strand('arm_'+side,[(0,sign*3,23,1.8),(0,sign*8,24,1.5),(5,sign*13,23,1.1)],sides=16,samples=4)
  membrane(s,side,sign)
  for i,end in enumerate([(13,28,22),(-2,28,20),(-12,21,19),(-10,6,18)]):
   x,y,z=end
   s.strand(f'digit_{side}_{i}',[(5,sign*13,23,.92),((5+x)*.5,sign*(13+y)*.5,(23+z)*.5+.45,.65),(x,sign*y,z,.27)],'accent',10,4)
  s.strand('thumb_'+side,[(5,sign*13,23,.7),(8,sign*12.3,24,.5),(9,sign*11.6,24.5,.25)],'accent',10,3)
  s.strand('claw_thumb_'+side,[(9,sign*11.6,24.5,.27),(10,sign*11.4,24.2,.14),(10.3,sign*11.7,23.8,.015)],'bone',8,3)
  s.strand('leg_'+side,[(-7,sign*2.7,21,1.4),(-9,sign*4.6,18.5,.9),(-10,sign*6,18,.65)],'accent',12,4)
  for i in range(5):
   y=sign*(5.1+i*.4)
   s.strand(f'toe_{side}_{i}',[(-10,y,18,.26),(-11,y,17.35,.2),(-11.2,y,16.9,.10)],'accent',8,2)
   s.strand(f'claw_foot_{side}_{i}',[(-11.2,y,16.9,.12),(-10.8,y,16.5,.02)],'bone',6,2)
 for part in s.parts:
  if part.name.startswith(('ear_L','ear_R','ear_inner')):
   sign=1 if part.name.endswith('L') else -1
   part.vertices=[(x,sign*4+(y-sign*4)*(1-.45*max(0,z-29)/4)+sign*max(0,z-27)*.65,z) for x,y,z in part.vertices]
 return materials.repack(s.parts)

def weights(p,v,u):
 n=p.name
 if n.startswith('jaw'):return [(IDS['jaw'],1)]
 if n.startswith(('ear_','ear_inner','ear_tragus')):return [(IDS['ear_'+n[-1]],1)]
 if n.startswith(('head','muzzle','nose','eye','nostril','mouth','fang')):return [(IDS['head'],1)]
 for side in ('L','R'):
  if side not in n:continue
  if n.startswith(('leg','toe','claw_foot')):return [(IDS['leg_'+side],1)]
  if n.startswith(('wing','digit','arm','thumb','claw_thumb')):
   # Same spatial weights across fused membranes and supporting digits.
   return RIG.chain_weights(v,[IDS['torso'],IDS['arm_'+side],IDS['hand_'+side],IDS['fingers_'+side]])
 return [(IDS['torso'],1)]

def geometry():
 from .connected_skin import attach
 return assemble(attach('vampire_bat',build_parts(),weights),weights)

def pose(name,t):
 rot=[(0,0,0,1) for _ in BONES];shift=[(0,0,0) for _ in BONES];p=math.sin(math.pi*t)**2;ph=math.tau*t
 def turn(n,a,d):rot[IDS[n]]=axis(a,math.radians(d))
 for side,sign in [('L',1),('R',-1)]:
  flap=(16 if name=='idle' else 27)*math.sin(ph)
  if name not in ('idle','fly'):flap=8*math.sin(ph)*p
  turn('arm_'+side,(1,0,0),sign*flap)
  turn('hand_'+side,(1,0,0),sign*((7 if name=='idle' else 12)*math.sin(ph-.45) if name in ('idle','fly') else 0))
  turn('fingers_'+side,(0,0,1),sign*3*math.sin(ph)* (1 if name in ('idle','fly') else p))
  turn('ear_'+side,(1,0,0),sign*2*math.sin(ph))
 if name in ('idle','fly'):
  shift[0]=(0,0,.65*math.sin(ph-.6));turn('head',(0,1,0),2*math.sin(ph))
 elif name in ('nip','feed'):
  shift[0]=((3 if name=='nip' else 2)*p,0,-1.5*p)
  turn('head',(0,1,0),14*p);turn('jaw',(0,1,0),22*p)
  if name=='feed':turn('head',(0,0,1),7*math.sin(ph)*p)
 elif name=='recoil':
  shift[0]=(-2*p,0,1*p);turn('head',(0,1,0),-14*p)
 elif name=='death':
  q=min(1,t/.9);q=q*q*(3-2*q);shift[0]=(0,0,-18*q)
  turn('head',(0,1,0),20*q)
  for side,sign in [('L',1),('R',-1)]:
   turn('arm_'+side,(0,0,1),sign*28*q)
   turn('hand_'+side,(0,0,1),sign*34*q)
   turn('fingers_'+side,(0,0,1),sign*18*q)
   turn('ear_'+side,(0,1,0),-30*q)
 return [(*add(local,shift[i]),*rot[i],1,1,1) for i,(_,_,local) in enumerate(BONES)]
def matrices(f):return RIG.matrices(f)
def deform(v,w,f):return RIG.deform(v,w,f)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def build():
 skin=materials.texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
 parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
 data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_vampire_bat',material_path=SKIN)
 model=ROOT/'mod/BrogueDoom/models/monsters/14_vampire_bat.iqm';model.write_bytes(data)
 m=dict(schemaVersion=1,workId='BRG-M14',format='IQM v2',runtimeModel=model.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],poseBounds=bounds,authoringSource='assets/monsters/vampire_bat/vampire-bat-animated.blend')
 out=ROOT/'assets/monsters/vampire_bat';out.mkdir(exist_ok=True);(out/'animation.json').write_text(json.dumps(m,indent=2)+'\n');return m
if __name__=='__main__':print(json.dumps(build(),indent=2))
