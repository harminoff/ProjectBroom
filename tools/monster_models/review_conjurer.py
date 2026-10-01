"""Natural seed-8 conjurer and Brogue-summoned blades; no spawned creatures."""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from .rat import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--backend',choices=('0','1'),required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--package',type=Path)
    args=parser.parse_args();out=(args.output or ROOT/'artifacts/conjurer-encounter'/args.backend).resolve();out.mkdir(parents=True,exist_ok=True)
    env={k.upper():v for k,v in os.environ.items()};env['PATH']=str(ROOT/'src/brogue-mapgen/bin')+';'+env['PATH']
    exe=out/'route.exe'
    subprocess.run(['g++','-std=c++17','-static',str(ROOT/'tools/monster_models/bloat_encounter.cpp'),
        str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.dll'),'-o',str(exe)],check=True)
    cmd=[str(exe),'8','9','8','--visible'];first=subprocess.check_output(cmd,cwd=out,env=env,text=True)
    assert first==subprocess.check_output(cmd,cwd=out,env=env,text=True)
    expected='e2e87855fd32531d';assert 'hash='+expected in first
    (out/'bridge-route.log').write_text(first);actions=first.splitlines()[-1].split()
    observer=out/'observer';observer.mkdir(exist_ok=True)
    (observer/'MAPINFO').write_text('GameInfo { AddEventHandlers="ConjurerReview" }\n')
    (observer/'ZSCRIPT').write_text('''version "5.0"
class ConjurerCamera : Actor { Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; } States { Spawn: TNT1 A -1; Stop; } }
class ConjurerReview : EventHandler {
 Actor camera; bool seen;
 override void WorldTick() {
  let pawn=players[consoleplayer].mo;if(!pawn) return;
  let it=ThinkerIterator.Create("BrogueMonsterK09");Actor candidate;Actor subject;double best=100000;
  while(candidate=Actor(it.Next())) {
   double d=(candidate.pos-pawn.pos).Length();
   if(!candidate.bINVISIBLE && candidate.alpha>=1 && d<best) {best=d;subject=candidate;}
  }
  if(!subject) return;
  vector3 eye=(pawn.pos.x,pawn.pos.y,players[consoleplayer].viewz);
  if(!camera) camera=Actor.Spawn("ConjurerCamera",eye);
  camera.SetOrigin(eye,false);
  vector3 delta=subject.pos+(0,0,24)-eye;
  camera.angle=VectorAngle(delta.x,delta.y);camera.pitch=atan2(-delta.z,sqrt(delta.x*delta.x+delta.y*delta.y));
  players[consoleplayer].camera=camera;pawn.bINVISIBLE=true;
  if(!seen) {Console.Printf("CONJURER_NATURAL_VISIBLE distance=%.2f alpha=%.2f",best,subject.alpha);seen=true;}
 }
}
''')
    cfg=['brg_debug true','screenblocks 12','con_notifytime 0','brg_enemy_walk_tics 5','brg_rat_walk_tics 5','wait 100',
         'brg_actions '+' '.join(actions[:-6]),'wait 1800','brg_monsters','screenshot encounter.png',
         'brg_actions '+' '.join(actions[-6:-1]),'wait 100','screenshot blades.png',
         'brg_actions '+actions[-1],'wait 12','screenshot pulse-early.png','wait 10','screenshot pulse-later.png',
         'wait 80','screenshot settled.png','brg_monsters','quit']
    (out/'capture.cfg').write_text('; '.join(cfg)+'\n')
    package=(args.package or ROOT/'artifacts/conjurer-higgsfield'/('vulkan' if args.backend=='1' else 'opengl')/'ProjectBroom-review.pk3').resolve()
    cmd=[str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),'-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),
        '-file',str(package),str(ROOT/'generated/seed-8/startup/ProjectBroom-seed-8.pk3'),str(observer),
        '-config',str(out/'test.ini'),'-noautoload','-nosound','-window',
        '+set','vid_preferbackend',args.backend,'+set','i_pauseinbackground','false',
        '+set','brg_save_root',str(out/'saves'),'+set','brg_map_compiler',sys.executable,
        '+set','brg_map_compiler_root',str(ROOT),'+set','brg_seed','8',
        '+set','screenshot_dir',str(out),'+map','BRG01','+exec',str(out/'capture.cfg')]
    logpath=out/'runtime.log'
    with logpath.open('w') as log:
        proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT);deadline=time.monotonic()+120
        while proc.poll() is None:
            text=logpath.read_text(errors='replace')
            if time.monotonic()>deadline or any(s in text for s in ('Script error','VM execution aborted')):
                proc.kill();proc.wait();raise RuntimeError(text[-3000:])
            time.sleep(.25)
    text=logpath.read_text(errors='replace')
    assert proc.returncode==0 and 'CONJURER_NATURAL_VISIBLE' in text,text[-3000:]
    assert 'hash='+expected in text,text[-3000:]
    assert 'CREATURE kind=55' in first,first
    assert 'class=BrogueMonsterK55' in text,text[-3000:]
    assert all((out/(n+'.png')).exists() for n in ('encounter','blades','pulse-early','pulse-later','settled'))
    print('Natural seed-8 conjurer encounter passed:',out)


if __name__=='__main__':main()
