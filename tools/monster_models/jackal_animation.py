"""Original powerful-jawed jackal on Project Broom's shared skeletal pipeline."""
import hashlib,json,math
from . import iqm,jackal_materials
from .creatures import Sculpt
from .rat import ROOT,add,sub,mul,unit,loft
from .skeletal import Rig,axis,between,inverse,qmul,assemble,sample_clips
SPECS=[('root',None,(0,0,0)),('pelvis','root',(-10,0,18)),('spine','pelvis',(0,0,19)),('neck','spine',(9,0,22)),('head','neck',(15,0,24)),('jaw','head',(17,0,21))]
for side,sign in (('L',1),('R',-1)):
 SPECS.append(('ear_'+side,'head',(12,sign*3,27)))
 for limb,parent,points in [('fore','spine',[(8,sign*4,20),(6,sign*4,10),(9,sign*4,1.4)]),('hind','pelvis',[(-11,sign*4,18),(-7,sign*4,10),(-12,sign*4,1.4)])]:
  for joint,p in zip(('upper','lower','end'),points):
   name=f'{limb}_{side}_{joint}';SPECS.append((name,parent,p));parent=name
parent='pelvis'
for i,p in enumerate([(-15,0,20),(-20,0,18),(-24,0,15),(-27,0,14),(-29,0,16)]):
 name=f'tail_{i}';SPECS.append((name,parent,p));parent=name
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest;IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('prowl',20,35,True),('bite',18,35,False),('maul',22,35,False),('recoil',10,35,False),('death',26,35,False)]

def build_parts():
 s=Sculpt();s.parts.append(loft('coat',[(-16,18,.5,1),(-12,18,4.2,5),(-5,19,4.1,5.7),(3,20,5.2,7),(8,21,4.8,6),(11,23,2,3)],sides=24,samples=3))
 s.strand('neck',[(7,0,20,4.5),(11,0,23,4),(14,0,25,3.2)],sides=20)
 s.oval('head_skull',(14,0,25),(4.7,3.6,4),seg=24,rings=14)
 s.oval('head_cheek',(16,0,22.8),(3.8,3.4,2.9))
 s.strand('head_muzzle',[(16,0,23,2.5),(20,0,22.2,2),(24,0,21.8,1.15)],sides=18,samples=3)
 s.oval('head_nose',(24,0,22),(1,1.4,.9),'dark',16,10)
 s.oval('jaw_mouth',(20,0,20.8),(4,2.2,.38),'dark')
 s.oval('jaw_lower',(19.7,0,20.2),(4.4,2.1,.85),'cloth')
 for side,sign in (('L',1),('R',-1)):
  s.oval('head_eye_'+side,(16,sign*3.05,25.5),(1,.55,.85),'glow',16,10)
  s.oval('head_pupil_'+side,(16.4,sign*3.5,25.5),(.43,.15,.5),'dark',12,8)
  s.oval('head_brow_'+side,(15.9,sign*3.1,26.3),(1.4,.65,.55))
  outline=[(9.5,sign*3,26.5),(11,sign*4.3,34),(14.7,sign*3.2,27)]
  s.plate('ear_'+side,outline,1.2,'body')
  s.plate('ear_'+side+'_inner',[(10.2,sign*3+sign*.7,27),(11.2,sign*4.3+sign*.65,32.5),(13.8,sign*3.2+sign*.7,27.4)],.12,'accent')
  for i in range(5):
   x=18+i*1.05
   s.strand('head_tooth_'+side+str(i),[(x,sign*1.7,21.7,.24),(x+.25,sign*1.65,20.3 if i in (0,3) else 20.9,.025)],'bone',6,1)
   s.strand('jaw_tooth_'+side+str(i),[(x,sign*1.5,20.5,.17),(x+.15,sign*1.45,21.1,.025)],'bone',6,1)
  for limb in ('fore','hind'):
   points=[REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
   s.strand(f'{limb}_{side}',[(*p,r) for p,r in zip(points,(2.8 if limb=='hind' else 2.4,1.45,.9))],sides=14,samples=4)
   foot=points[-1];s.oval(f'paw_{limb}_{side}',add(foot,(1,0,-.1)),(2.4,1.45,1.3),'cloth')
   for i in range(3):
    c=add(foot,(2.6,(i-1)*.65,-.55))
    s.strand(f'paw_{limb}_{side}_claw{i}',[(*c,.19),(*add(c,(.85,0,-.1)),.025)],'bone',6,1)
 s.strand('tail',[(*REST[IDS[f'tail_{i}']],radius) for i,radius in enumerate((2.4,2.3,1.8,1.1,.08))],sides=14,samples=4)
 return s.parts

def weights(part,v,uv):
 n=part.name
 if n.startswith('head'):return [(IDS['head'],1)]
 if n.startswith('jaw'):return [(IDS['jaw'],1)]
 if n.startswith('ear'):return [(IDS['_'.join(n.split('_')[:2])],1)]
 if n.startswith('paw'):
  _,limb,side,*_=n.split('_');return [(IDS[f'{limb}_{side}_end'],1)]
 if n.startswith(('fore','hind')):return RIG.chain_weights(v,[IDS[n+'_'+j] for j in ('upper','lower','end')])
 if n=='tail':return RIG.chain_weights(v,[IDS[f'tail_{i}'] for i in range(5)])
 return RIG.chain_weights(v,[IDS[n] for n in ('pelvis','spine','neck','head')])

def leg(prefix,target,rotations):
 ids=[IDS[prefix+'_'+j] for j in ('upper','lower','end')];hip,knee,foot=[REST[i] for i in ids]
 a,b=math.dist(hip,knee),math.dist(knee,foot);direction=unit(sub(target,hip));distance=min(a+b-.001,max(abs(a-b)+.001,math.dist(target,hip)))
 along=(a*a-b*b+distance*distance)/(2*distance);pole=sub(knee,hip)
 bend=unit(sub(pole,mul(direction,sum(x*y for x,y in zip(pole,direction)))))
 new=add(hip,add(mul(direction,along),mul(bend,math.sqrt(max(0,a*a-along*along)))))
 upper=between(sub(knee,hip),sub(new,hip));lower=between(sub(foot,knee),sub(target,new))
 rotations[ids[0]]=upper;rotations[ids[1]]=qmul(inverse(upper),lower);rotations[ids[2]]=inverse(lower)

def pose(name,t):
 rot=[(0,0,0,1) for _ in BONES];shift=[(0,0,0) for _ in BONES];phase=t*math.tau
 def turn(n,a,d):rot[IDS[n]]=axis(a,math.radians(d))
 if name=='idle':
  turn('neck',(0,1,0),1.3*math.sin(phase));turn('head',(0,0,1),2*math.sin(phase));turn('jaw',(0,1,0),3*max(0,math.sin(phase*2)))
  for side,offset in [('L',0),('R',1.6)]:turn('ear_'+side,(1,0,0),8*max(0,math.sin(phase+offset))**10)
 elif name=='prowl':
  for limb,offset in [('fore',0),('hind',math.pi)]:
   for side,extra in [('L',0),('R',math.pi)]:
    p=phase+offset+extra;foot=REST[IDS[f'{limb}_{side}_end']]
    leg(f'{limb}_{side}',add(foot,(-3.5*math.cos(p),0,2.3*max(0,math.sin(p)))),rot)
  turn('head',(0,1,0),2*math.sin(phase*2));turn('neck',(0,0,1),2*math.sin(phase))
 elif name in ('bite','maul'):
  p=math.sin(math.pi*t)**2;turn('neck',(0,1,0),-12*p);turn('head',(0,1,0),22*p)
  turn('jaw',(0,1,0),32*max(0,math.sin(math.pi*min(1,t/.7))))
  if name=='maul':turn('head',(0,0,1),22*math.sin(t*math.tau*2)*p)
  for side in ('L','R'):turn('ear_'+side,(0,1,0),-18*p)
 elif name=='recoil':
  p=math.sin(math.pi*t)**2;turn('neck',(0,1,0),-15*p);turn('head',(0,0,1),-19*p);turn('jaw',(0,1,0),10*p)
 elif name=='death':
  s=min(1,t/.8);s=s*s*(3-2*s);turn('root',(1,0,0),90*s);shift[0]=(0,18*s,0)
  turn('head',(0,0,1),-16*s);turn('jaw',(0,1,0),16*s)
  for limb in ('fore','hind'):
   for side in ('L','R'):turn(f'{limb}_{side}_lower',(0,1,0),35*s)
 for i in range(5):turn(f'tail_{i}',(0,0,1),(2*math.sin(phase-i*.6) if name in ('idle','prowl') else 2*math.sin(math.pi*t)))
 return [(*add(local,shift[i]),*rot[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]

def geometry():
 from .connected_skin import attach
 return assemble(attach('jackal',build_parts(),weights),weights)
def matrices(frame):return RIG.matrices(frame)
def deform(vertices,influences,frame):return RIG.deform(vertices,influences,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def build():
 skin=jackal_materials.texture_bytes();(ROOT/'mod/BrogueDoom'/jackal_materials.SKIN).write_bytes(skin)
 parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
 data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_jackal',material_path=jackal_materials.SKIN)
 path=ROOT/'mod/BrogueDoom/models/monsters/03_jackal.iqm';path.write_bytes(data)
 manifest={'schemaVersion':1,'workId':'BRG-M03','format':'IQM v2','runtimeModel':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'skin':jackal_materials.SKIN,'skinSha256':hashlib.sha256(skin).hexdigest(),'dimensions':[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],'parts':len(parts),'vertices':len(v),'triangles':len(t),'boneCount':len(BONES),'bones':[{'name':n,'parent':p,'local':v} for n,p,v in BONES],'clips':[{k:v for k,v in c.items() if k!='frames'}|{'frameCount':len(c['frames'])} for c in clips],'poseBounds':bounds,'authoringSource':'assets/monsters/jackal/jackal-animated.blend'}
 out=ROOT/'assets/monsters/jackal';out.mkdir(exist_ok=True);(out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Jackal:',len(v),'vertices,',len(BONES),'bones');return manifest
if __name__=='__main__':build()
