"""Opt-in UZDoom 5.0 bone-offset renderer probe.

Run python -m tools.monster_models.review_rat_bones 1 (Vulkan) or 0 (OpenGL).
Uses an isolated non-Brogue map. The fixture owns no gameplay assertions.
"""
import sys


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('0','1'):
        raise SystemExit('Pass backend 0 (OpenGL) or 1 (Vulkan).')
    from pathlib import Path
    import subprocess, os, time
    r=Path(__file__).resolve().parents[2]; backend=sys.argv[1]; out=r/'artifacts/rat-uzdoom'/('vulkan' if backend=='1' else 'opengl'); out.mkdir(parents=True,exist_ok=True)
    for i in range(8):
        (out/f'{i}.png').unlink(missing_ok=True)
    fixture=out/'fixture'; (fixture/'maps').mkdir(parents=True,exist_ok=True)
    from tools.mapcompiler.compile import make_wad
    text='namespace="ZDoom";\n'
    for x,y in ((-128,-128),(-128,128),(128,128),(128,-128)): text+=f'vertex {{ x={x}; y={y}; }}\n'
    text+='sector { heightfloor=0; heightceiling=160; texturefloor="BRGDIRT"; textureceiling="BRGROCK"; lightlevel=208; }\n'
    for n in range(4):
     text+=f'sidedef {{ sector=0; texturemiddle="BRGROCK"; }}\nlinedef {{ v1={n}; v2={(n+1)%4}; sidefront={n}; blocking=true; }}\n'
    text+='thing { x=64; y=-64; type=1; angle=135; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; }\n'
    (fixture/'maps/ART01.wad').write_bytes(make_wad('ART01',text))
    (fixture/'MAPINFO').write_text('GameInfo { AddEventHandlers="RatBoneReview" }\nmap ART01 "UZDoom rat bone review" {}\n')
    (fixture/'ZSCRIPT').write_text('''version "5.0"
    class RatBoneCamera : Actor { Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; } States { Spawn: TNT1 A -1; Stop; } }
    class RatBoneReview : EventHandler {
     BrogueRatSkeletalProxy subject; Actor camera; int counter;
     override void WorldTick() {
      counter++; if(counter<100) return;
      if(!subject) { subject=BrogueRatSkeletalProxy(Actor.Spawn("BrogueMonsterK01",(0,0,0))); subject.angle=0; }
      if(!camera) { camera=Actor.Spawn("RatBoneCamera",(48,-64,30)); camera.angle=VectorAngle(-48,64); camera.pitch=atan2(23,80); }
      players[consoleplayer].camera=camera;
      if(players[consoleplayer].mo) players[consoleplayer].mo.bINVISIBLE=true;
      int stage=(counter-100)/40; int tick=(counter-100)%40;
      if(stage>7) return;
      if(tick==0) {
       subject.bINVISIBLE=false; subject.alpha=1; subject.angle=0;
       subject.PresentationClip = stage==4 ? 2 : stage==5 ? 5 : stage==3 ? 1 : 0;
       subject.SetAnimation(stage==4 ? 'bite' : stage==5 ? 'death' : stage==3 ? 'scurry' : 'idle',stage==3 ? 25 : 0,stage==5 ? 23 : 0,-1,-1,0,SAF_INSTANT);
       if(stage==6) subject.bINVISIBLE=true;
      }
      if(stage==3) subject.angle=sin(tick*9)*35;
      if(tick==25) {
       let [q,t,s]=subject.GetNamedBoneOffset('head');
       double magnitude=abs(q.x)+abs(q.y)+abs(q.z);
       bool disabled=stage==0 || stage>=4;
       bool valid=disabled ? magnitude<0.0001 : magnitude>0.0001;
       Console.Printf("RAT_BONES stage=%d offset=%.6f valid=%d pos=%.1f,%.1f,%.1f",stage,magnitude,valid,subject.pos.x,subject.pos.y,subject.pos.z);
      }
     }
    }
    ''')
    lines=['brg_fx_quality 0','wait 126']
    for i in range(8):
     lines+=['screenshot '+str(i)+'.png', 'brg_fx_quality '+str(2 if i==1 else 0 if i==6 else 1), 'wait 40' if i<7 else 'wait 3']
    lines+=['quit']; (out/'capture.cfg').write_text('; '.join(lines)+'\n')
    cmd=[str(r/'.build/uzdoom/Release/uzdoom.exe'),'-iwad',str(r/'.deps/freedoom-0.13.0/freedoom2.wad'),'-file',str(r/'mod/BrogueDoom'),str(fixture),'-config',str(out/'test.ini'),'-noautoload','-nosound','-window','+set','vid_preferbackend',backend,'+set','i_pauseinbackground','false','+set','screenshot_dir',str(out),'+set','con_notifytime','0','+set','screenblocks','12','+map','ART01','+exec',str(out/'capture.cfg')]
    env={('Path' if k.upper()=='PATH' else k):v for k,v in os.environ.items()}
    with (out/'runtime.log').open('w') as log:
     p=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT); deadline=time.monotonic()+50
     while p.poll() is None:
      text=(out/'runtime.log').read_text(errors='replace')
      if 'Script error' in text or 'VM execution aborted' in text or time.monotonic()>deadline:
       p.kill(); p.wait(); raise RuntimeError(text[-2000:])
      time.sleep(.25)
    text=(out/'runtime.log').read_text(errors='replace')
    assert text.count('valid=1')==8,text[-2500:]
    assert all((out/f'{i}.png').is_file() for i in range(8)), 'Missing framebuffer captures'
    assert ('Selecting '+('Vulkan' if backend=='1' else 'OpenGL')+' backend') in text
    print('Passed bone runtime stages:',backend)


if __name__ == '__main__':
    main()
