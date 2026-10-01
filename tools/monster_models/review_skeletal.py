"""Opt-in real renderer clip review: --symbol MK_KOBOLD --backend 0|1.
Presentation-only ART01 fixture; produces static-before and sampled-pose captures.

`--views key` captures only six decisive shots (oblique idle / attack key / death
end, front idle / attack key, front idle at 128 units) for fast authoring
iterations; the full 34-view gallery stays the hand-back and gate evidence.
Captures from every process on the machine are serialized by a lock file (parallel
GPU captures froze under load), and a capture whose image does not change across a
camera or distance change is treated as frozen and retried.
"""
import argparse, hashlib, json, os, subprocess, time, zipfile
from pathlib import Path
from .skeletal_registry import ROOT, find, PENDING
from tools.mapcompiler.compile import make_wad

LOCK=Path(os.environ.get('TEMP') or ROOT/'.build')/'broom-review-capture.lock'


class capture_lock:
 """Machine-wide exclusive lock so only one engine capture runs at a time."""
 def __init__(self,timeout=3600):self.timeout=timeout
 def __enter__(self):
  import msvcrt
  LOCK.parent.mkdir(parents=True,exist_ok=True);self.fd=os.open(LOCK,os.O_RDWR|os.O_CREAT);start=time.monotonic()
  while True:
   try:msvcrt.locking(self.fd,msvcrt.LK_NBLCK,1);return self
   except OSError:
    if time.monotonic()-start>self.timeout:raise TimeoutError(f'capture lock busy for {self.timeout}s: {LOCK}')
    time.sleep(1)
 def __exit__(self,*exc):
  import msvcrt
  os.lseek(self.fd,0,0);msvcrt.locking(self.fd,msvcrt.LK_UNLCK,1);os.close(self.fd)


def frozen(out,stages,views):
 """Consecutive captures that must differ (camera/distance change) but are byte-identical."""
 h=[hashlib.sha256((out/f'{i:02d}-{c}-{f}.png').read_bytes()).hexdigest() for i,(c,f,_) in enumerate(stages)]
 return [i for i in range(1,len(stages)) if views[i]!=views[i-1] and h[i]==h[i-1]]

def main():
 p=argparse.ArgumentParser();p.add_argument('--symbol',default='MK_KOBOLD');p.add_argument('--backend',choices=['0','1'],required=True)
 p.add_argument('--all-angles',action='store_true');p.add_argument('--before-iqm',type=Path)
 p.add_argument('--captivity',action='store_true')
 p.add_argument('--packaged',action='store_true')
 p.add_argument('--distances',action='store_true')
 p.add_argument('--width',type=int);p.add_argument('--height',type=int)
 p.add_argument('--output',type=Path)
 # --preview reviews a creature still being authored: a fixture-local actor and
 # MODELDEF bind its exported IQM/skin, so no shared registry, MODELDEF, ZScript
 # or native row is needed and parallel authoring agents cannot collide.
 p.add_argument('--preview',action='store_true')
 p.add_argument('--views',choices=['full','key'],default='full',help='key: six decisive shots for fast iteration')
 p.add_argument('--attempts',type=int,default=3,help='retries for a timed-out or frozen capture');a=p.parse_args()
 if a.views=='key' and (a.captivity or a.packaged or a.all_angles or a.distances):
  p.error('--views key replaces --all-angles/--distances and is for unpackaged previews')
 if (a.width is None)!=(a.height is None) or (a.width is not None and min(a.width,a.height)<320):
  p.error('--width and --height must both be supplied and at least 320')
 if a.preview and (a.captivity or a.packaged):p.error('--preview supports ordinary unpackaged galleries only')
 row=find(a.symbol)
 out=a.output or ROOT/'artifacts/skeletal-review'/a.symbol/('vulkan' if a.backend=='1' else 'opengl');out=out.resolve();out.mkdir(parents=True,exist_ok=True)
 fixture=out/'fixture';(fixture/'maps').mkdir(parents=True,exist_ok=True)
 text='namespace="ZDoom";\n'
 extent=256 if a.distances or a.views=='key' else 128
 for x,y in ((-extent,-extent),(-extent,extent),(extent,extent),(extent,-extent)):text+=f'vertex {{ x={x}; y={y}; }}\n'
 text+='sector { heightfloor=0; heightceiling=160; texturefloor="BRGDIRT"; textureceiling="BRGROCK"; lightlevel=208; }\n'
 for n in range(4):text+=f'sidedef {{ sector=0; texturemiddle="BRGROCK"; }}\nlinedef {{ v1={n}; v2={(n+1)%4}; sidefront={n}; blocking=true; }}\n'
 text+='thing { x=64; y=-64; type=1; angle=135; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; }\n'
 (fixture/'maps/ART01.wad').write_bytes(make_wad('ART01',text))
 (fixture/'MAPINFO').write_text('GameInfo { AddEventHandlers="SkeletalReview" }\nmap ART01 "Skeletal presentation review" {}\n')
 # Original OBJ is a distinct review-only actor, preserving its authored reference.
 obj=Path(row['model']).with_suffix('.obj').name
 before_skin=row.get('referenceSkin',row['skin']);baseframe=''
 if a.before_iqm:
  (fixture/'models/monsters').mkdir(parents=True,exist_ok=True)
  obj='anatomy-before.iqm';(fixture/'models/monsters'/obj).write_bytes(a.before_iqm.read_bytes())
  before_skin=row['skin'];baseframe='BaseFrame'
 modeldef=f'Model SkeletalBefore {{ Path "models/monsters" Model 0 "{obj}" Skin 0 "{before_skin}" Scale 1 1 1 FrameIndex BRM0 A 0 0 {baseframe} }}\n'
 preview_class=''
 if a.preview:
  scale=row.get('visualScale',1.0)
  modeldef+=f'Model SkeletalPreview {{ Path "models/monsters" Model 0 "{row["model"]}" Skin 0 "{row["skin"]}" Scale {scale} {scale} {scale} FrameIndex BRM0 A 0 0 BaseFrame }}\n'
  style=' RenderStyle "Add"; Alpha 0.65;' if row.get('additiveFlame') else ''
  preview_class=('class SkeletalPreview : BrogueMonsterProxyBase { Default { +DECOUPLEDANIMATIONS;'+style+' }'
                 ' States { Spawn: BRM0 A 0; BRM0 A -1 A_SetAnimation("'+row['clips'][0]+'", -1, -1, -1, -1, 1, SAF_LOOP); Stop; } }\n')
  snippet=PENDING/(a.symbol+'.gldefs')
  if snippet.is_file():(fixture/'GLDEFS').write_bytes(snippet.read_bytes())
 (fixture/'MODELDEF').write_text(modeldef)
 counts=[c['frameCount'] for c in json.loads((ROOT/row['manifest']).read_text())['clips']]
 stages=[('before',0,0)]+[(clip,frame,role) for role,clip in enumerate(row['clips']) for frame in (0,int(counts[role]*.5),counts[role]-1)]
 # Keep every clip sample at the oblique view, then add front, side and rear
 # attachment checks. Sparse angles keep the review below the runtime timeout.
 if a.all_angles:
  stages += [(clip,frame,role) for angle in range(3) for clip,frame,role in [('before',0,0),(row['clips'][0],0,0),(row['clips'][2],9,2),(row['clips'][1],8,1)]]
 if a.captivity:
  captivity=row['captivity']
  stages=[(captivity['idle'],f,0) for f in (0,20,39)]+[(captivity['release'],f,0) for f in (0,10,20)]+[(row['clips'][0],0,0)]
 distance_start=len(stages)
 if a.distances:stages += [(row['clips'][0],0,0)]*3
 # Camera per stage: 'o' oblique, 'f' front, 's' side, 'r' rear, 'dN' front at N*64 units.
 views=(['o']*19+['fsr'[(i-19)//4] for i in range(19,distance_start)]) if a.all_angles else ['o']*distance_start
 views=views[:distance_start]+[f'd{k+1}' for k in range(len(stages)-distance_start)]
 if a.views=='key':
  idle,attack,death=row['clips'][0],row['clips'][2],row['clips'][5]
  stages=[(idle,0,0),(attack,int(counts[2]*.5),2),(death,counts[5]-1,5),(idle,0,0),(attack,int(counts[2]*.5),2),(idle,0,0)]
  views=['o','o','o','f','f','d2']
 target=row.get('previewTarget',[0,0,19])[2]
 def camera_code(v):
  if v=='o':return 'camera.SetOrigin((62,62,35),false); camera.angle=VectorAngle(-62,-62); camera.pitch=atan2(16,87.7);'
  if v in ('f','s','r'):return {'f':'camera.SetOrigin((92,0,35),false); camera.angle=180;','s':'camera.SetOrigin((0,92,35),false); camera.angle=270;','r':'camera.SetOrigin((-92,0,35),false); camera.angle=0;'}[v]+' camera.pitch=atan2(16,92);'
  d=64*int(v[1:]);return f'camera.SetOrigin(({d},0,41),false); camera.angle=180; camera.pitch=atan2(41-{target},{d});'
 if a.views=='key':
  cameras='switch(stage) { '+' '.join(f'case {i}: {camera_code(v)} break;' for i,v in enumerate(views))+' }'
 else:  # unchanged original camera schedule, so full galleries stay comparable with accepted evidence
  cameras=(' if(stage>=19 && stage<DISTANCE_START) { int view=(stage-19)/4; camera.SetOrigin(view==0 ? (92,0,35) : view==1 ? (0,92,35) : (-92,0,35),false); camera.angle=view==0 ? 180 : view==1 ? 270 : 0; camera.pitch=atan2(16,92); }\n'
           ' if(stage>=DISTANCE_START) { double distance=64*(stage-DISTANCE_START+1); camera.SetOrigin((distance,0,41),false); camera.angle=180;camera.pitch=atan2(41-TARGET_Z,distance); }'
           ).replace('DISTANCE_START',str(distance_start)).replace('TARGET_Z',str(target))
 switches='\n'.join(f'case {i}: subject.SetAnimation("{clip}",0,{frame},-1,-1,0,SAF_INSTANT); break;' for i,(clip,frame,role) in enumerate(stages) if clip!='before')
 (fixture/'ZSCRIPT').write_text('''version "5.0"
 class SkeletalBefore : BrogueMonsterProxyBase { States { Spawn: BRM0 A -1; Stop; } }
 PREVIEW_CLASS
 class SkeletalCamera : Actor { Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; } States { Spawn: TNT1 A -1; Stop; } }
 class SkeletalReview : EventHandler {
 Actor subject; Actor camera; int counter;
 override void WorldTick() {
 counter++; if(counter<100) return;
 if(!camera) { camera=Actor.Spawn("SkeletalCamera",(62,62,35)); camera.angle=VectorAngle(-62,-62); camera.pitch=atan2(16,87.7); }
 players[consoleplayer].camera=camera;
 if(players[consoleplayer].mo) players[consoleplayer].mo.bINVISIBLE=true;
 int stage=(counter-100)/20; int tick=(counter-100)%20;
 if(stage>STAGE_MAX) return;
 if(tick==0) {
 if(subject) subject.Destroy();
 subject=Actor.Spawn(IS_BEFORE ? "SkeletalBefore" : ACTOR_SELECTION,(0,0,0)); subject.angle=0;
 CAMERAS
 
 Console.Printf("SKELETAL_REVIEW stage=%d z=%.2f blocking=%d",stage,subject.pos.z,subject.bSOLID);
 }
 if(tick==2) { switch(stage) { SWITCHES } }
 }
 }
 '''.replace('PREVIEW_CLASS',preview_class).replace('CAMERAS',cameras).replace('ACTOR_SELECTION',('stage<3 ? "'+row['captivity']['class']+'" : "'+row['class']+'"') if a.captivity else '"SkeletalPreview"' if a.preview else '"'+row['class']+'"').replace('STAGE_MAX',str(len(stages)-1)).replace('SWITCHES',switches).replace('IS_BEFORE',' || '.join(f'stage=={i}' for i,(clip,_,_) in enumerate(stages) if clip=='before') or 'false'))
 lines=['brg_fx_quality 0','wait 112']
 if a.width is not None:lines.insert(0,f'vid_setsize {a.width} {a.height}')
 for i,(clip,frame,_) in enumerate(stages):
  filename=f'{i:02d}-{clip}-{frame}.png';(out/filename).unlink(missing_ok=True);lines+=['screenshot '+filename,'wait 20']
 lines+=['quit'];(out/'capture.cfg').write_text('; '.join(lines)+'\n')
 resource=ROOT/'mod/BrogueDoom'
 if a.packaged:
  resource=out/'ProjectBroom-review.pk3'
  with zipfile.ZipFile(resource,'w',compression=zipfile.ZIP_DEFLATED) as archive:
   for path in sorted((ROOT/'mod/BrogueDoom').rglob('*')):
    if path.is_file():
     entry=zipfile.ZipInfo(path.relative_to(ROOT/'mod/BrogueDoom').as_posix(),(2020,1,1,0,0,0))
     entry.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(entry,path.read_bytes())
  with zipfile.ZipFile(resource) as archive:
   for path in ('models/monsters/'+row['model'],row['skin'],'models/monsters/MODELDEF.txt','brogue_monsters.zs'):
    assert archive.read(path)==(ROOT/'mod/BrogueDoom'/path).read_bytes()
 cmd=[str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),'-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),'-file',str(resource),str(fixture),'-config',str(out/'test.ini'),'-noautoload','-nosound','-window','+set','vid_preferbackend',a.backend,'+set','i_pauseinbackground','false','+set','screenshot_dir',str(out),'+set','con_notifytime','0','+set','screenblocks','12','+map','ART01','+exec',str(out/'capture.cfg')]
 if a.width is not None:cmd[1:1]=['-width',str(a.width),'-height',str(a.height),'+set','vid_fullscreen','false']
 env={('Path' if k.upper()=='PATH' else k):v for k,v in os.environ.items()}
 problems=[]
 for attempt in range(1,a.attempts+1):
  for i,(clip,frame,_) in enumerate(stages):(out/f'{i:02d}-{clip}-{frame}.png').unlink(missing_ok=True)
  failure=None
  with capture_lock(),(out/'runtime.log').open('w') as log:
   proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT);deadline=time.monotonic()+60+2*len(stages)
   while proc.poll() is None:
    text=(out/'runtime.log').read_text(errors='replace')
    if any(e in text for e in ('Script error','VM execution aborted')):proc.kill();proc.wait();raise RuntimeError(text[-3000:])
    if time.monotonic()>deadline:proc.kill();proc.wait();failure='timed out';break
    time.sleep(.25)
  text=(out/'runtime.log').read_text(errors='replace')
  if failure is None and not all((out/f'{i:02d}-{c}-{f}.png').exists() for i,(c,f,_) in enumerate(stages)):failure='missing captures'
  if failure is None and frozen(out,stages,views):failure='frozen at stages '+str(frozen(out,stages,views))
  if failure is None:break
  problems.append(f'attempt {attempt}: {failure}');print('RETRY',problems[-1],flush=True)
 else:
  raise RuntimeError('capture failed: '+'; '.join(problems)+'\n'+text[-2000:])
 assert proc.returncode==0 and text.count('blocking=0')==len(stages),text[-3000:]
 assert ('Selecting '+('Vulkan' if a.backend=='1' else 'OpenGL')+' backend') in text
 assert all((out/f'{i:02d}-{clip}-{frame}.png').exists() for i,(clip,frame,_) in enumerate(stages))
 if a.width is not None:
  import struct
  for i,(clip,frame,_) in enumerate(stages):
   capture=out/f'{i:02d}-{clip}-{frame}.png'
   assert struct.unpack('>II',capture.read_bytes()[16:24])==(a.width,a.height),str(capture)
 print('Captured',len(stages),'poses:',out)
if __name__=='__main__':main()
