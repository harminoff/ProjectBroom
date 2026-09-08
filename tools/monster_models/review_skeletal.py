"""Opt-in real renderer clip review: --symbol MK_KOBOLD --backend 0|1.
Presentation-only ART01 fixture; produces static-before and sampled-pose captures.
"""
import argparse, os, subprocess, time
from pathlib import Path
from .skeletal_registry import ROOT, profiles
from tools.mapcompiler.compile import make_wad

def main():
 p=argparse.ArgumentParser();p.add_argument('--symbol',default='MK_KOBOLD');p.add_argument('--backend',choices=['0','1'],required=True)
 p.add_argument('--all-angles',action='store_true');p.add_argument('--before-iqm',type=Path)
 p.add_argument('--captivity',action='store_true')
 p.add_argument('--output',type=Path);a=p.parse_args()
 row=next(r for r in profiles() if r['symbol']==a.symbol)
 out=a.output or ROOT/'artifacts/skeletal-review'/a.symbol/('vulkan' if a.backend=='1' else 'opengl');out=out.resolve();out.mkdir(parents=True,exist_ok=True)
 fixture=out/'fixture';(fixture/'maps').mkdir(parents=True,exist_ok=True)
 text='namespace="ZDoom";\n'
 for x,y in ((-128,-128),(-128,128),(128,128),(128,-128)):text+=f'vertex {{ x={x}; y={y}; }}\n'
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
 (fixture/'MODELDEF').write_text(f'Model SkeletalBefore {{ Path "models/monsters" Model 0 "{obj}" Skin 0 "{before_skin}" Scale 1 1 1 FrameIndex BRM0 A 0 0 {baseframe} }}\n')
 stages=[('before',0,0)]+[(clip,frame,role) for role,clip in enumerate(row['clips']) for frame in (0, int(__import__('json').loads((ROOT/row['manifest']).read_text())['clips'][role]['frameCount']*.5),int(__import__('json').loads((ROOT/row['manifest']).read_text())['clips'][role]['frameCount'])-1)]
 # Keep every clip sample at the oblique view, then add front, side and rear
 # attachment checks. Sparse angles keep the review below the runtime timeout.
 if a.all_angles:
  stages += [(clip,frame,role) for angle in range(3) for clip,frame,role in [('before',0,0),(row['clips'][0],0,0),(row['clips'][2],9,2),(row['clips'][1],8,1)]]
 if a.captivity:
  captivity=row['captivity']
  stages=[(captivity['idle'],f,0) for f in (0,20,39)]+[(captivity['release'],f,0) for f in (0,10,20)]+[(row['clips'][0],0,0)]
 switches='\n'.join(f'case {i}: subject.SetAnimation("{clip}",0,{frame},-1,-1,0,SAF_INSTANT); break;' for i,(clip,frame,role) in enumerate(stages) if clip!='before')
 (fixture/'ZSCRIPT').write_text('''version "5.0"
 class SkeletalBefore : BrogueMonsterProxyBase { States { Spawn: BRM0 A -1; Stop; } }
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
 if(stage>=19) { int view=(stage-19)/4; camera.SetOrigin(view==0 ? (92,0,35) : view==1 ? (0,92,35) : (-92,0,35),false); camera.angle=view==0 ? 180 : view==1 ? 270 : 0; camera.pitch=atan2(16,92); }
 
 Console.Printf("SKELETAL_REVIEW stage=%d z=%.2f blocking=%d",stage,subject.pos.z,subject.bSOLID);
 }
 if(tick==2) { switch(stage) { SWITCHES } }
 }
 }
 '''.replace('ACTOR_SELECTION',('stage<3 ? "'+row['captivity']['class']+'" : "'+row['class']+'"') if a.captivity else '"'+row['class']+'"').replace('STAGE_MAX',str(len(stages)-1)).replace('SWITCHES',switches).replace('IS_BEFORE',' || '.join(f'stage=={i}' for i,(clip,_,_) in enumerate(stages) if clip=='before') or 'false'))
 lines=['brg_fx_quality 0','wait 112']
 for i,(clip,frame,_) in enumerate(stages):
  filename=f'{i:02d}-{clip}-{frame}.png';(out/filename).unlink(missing_ok=True);lines+=['screenshot '+filename,'wait 20']
 lines+=['quit'];(out/'capture.cfg').write_text('; '.join(lines)+'\n')
 cmd=[str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),'-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),'-file',str(ROOT/'mod/BrogueDoom'),str(fixture),'-config',str(out/'test.ini'),'-noautoload','-nosound','-window','+set','vid_preferbackend',a.backend,'+set','i_pauseinbackground','false','+set','screenshot_dir',str(out),'+set','con_notifytime','0','+set','screenblocks','12','+map','ART01','+exec',str(out/'capture.cfg')]
 env={('Path' if k.upper()=='PATH' else k):v for k,v in os.environ.items()}
 with (out/'runtime.log').open('w') as log:
  proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT);deadline=time.monotonic()+60
  while proc.poll() is None:
   text=(out/'runtime.log').read_text(errors='replace')
   if any(e in text for e in ('Script error','VM execution aborted')) or time.monotonic()>deadline:
    proc.kill();proc.wait();raise RuntimeError(text[-3000:])
   time.sleep(.25)
 text=(out/'runtime.log').read_text(errors='replace')
 assert proc.returncode==0 and text.count('blocking=0')==len(stages),text[-3000:]
 assert ('Selecting '+('Vulkan' if a.backend=='1' else 'OpenGL')+' backend') in text
 assert all((out/f'{i:02d}-{clip}-{frame}.png').exists() for i,(clip,frame,_) in enumerate(stages))
 print('Captured',len(stages),'poses:',out)
if __name__=='__main__':main()
