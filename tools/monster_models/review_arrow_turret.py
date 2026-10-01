"""Reproduce a natural seed-26 arrow turret encounter using ordinary Brogue intents.

The route helper reads snapshots to find a route; Brogue validates every move.
The observer only aims a camera at a directly visible existing proxy. It never
reveals, spawns or repositions a creature, or changes health/status/RNG.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from .rat import ROOT
from .review_campaign import missing_depth_mapinfo


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--backend',choices=('0','1'),required=True)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    env={k.upper():v for k,v in os.environ.items()}
    env['PATH']=str(ROOT/'src/brogue-mapgen/bin')+';'+env['PATH']
    exe=out/'route.exe'
    subprocess.run(['g++','-std=c++17','-static',str(ROOT/'tools/monster_models/bloat_encounter.cpp'),
                    str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.dll'),'-o',str(exe)],check=True)
    route=[str(exe),'26','15','0','--visible','1100','8']
    first=subprocess.check_output(route,cwd=out,env=env,text=True)
    assert first==subprocess.check_output(route,cwd=out,env=env,text=True)
    expected='ab31c1c06bb8a76a'
    assert 'hash='+expected in first and 'CREATURE kind=15 id=94' in first
    (out/'bridge-route.log').write_text(first)
    actions=first.splitlines()[-1].split()
    observer=out/'observer';observer.mkdir(exist_ok=True)
    # The small seed-26 startup campaign only declares depths 1-4. The native
    # bridge reconstructs depth 6 from Brogue; declare its presentation identity
    # so the engine can attach that snapshot (without changing any map cells).
    campaign=ROOT/'generated/seed-26/startup/ProjectBroom-seed-26.pk3'
    target_depth=int(first.split('depth=',1)[1].split()[0])
    (observer/'MAPINFO').write_text('GameInfo { AddEventHandlers="ArrowTurretReview" }\n'
        + missing_depth_mapinfo(campaign, target_depth))
    (observer/'ZSCRIPT').write_text('''version "5.0"
class ArrowTurretCamera : Actor {
 Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; }
 States { Spawn: TNT1 A -1; Stop; }
}
class ArrowTurretReview : EventHandler {
 Actor camera; bool seen;
 override void WorldTick() {
  let pawn=players[consoleplayer].mo;if(!pawn) return;
  let it=ThinkerIterator.Create("BrogueMonsterK15");Actor candidate;Actor subject;double best=100000;
  while(candidate=Actor(it.Next())) {
   double d=(candidate.pos-pawn.pos).Length();
   if(!candidate.bINVISIBLE && candidate.alpha>=1 && d<best) {best=d;subject=candidate;}
  }
  if(!subject) return;
  vector3 eye=(pawn.pos.x,pawn.pos.y,players[consoleplayer].viewz);
  if(!camera) camera=Actor.Spawn("ArrowTurretCamera",eye);
  camera.SetOrigin(eye,false);
  vector3 delta=subject.pos+(0,0,26)-eye;
  camera.angle=VectorAngle(delta.x,delta.y);
  camera.pitch=atan2(-delta.z,sqrt(delta.x*delta.x+delta.y*delta.y));
  players[consoleplayer].camera=camera;pawn.bINVISIBLE=true;
  if(!seen) {Console.Printf("ARROW_TURRET_NATURAL_VISIBLE distance=%.2f alpha=%.2f",best,subject.alpha);seen=true;}
 }
}
''')
    cfg=['vid_setsize 1920 1080','brg_debug true','screenblocks 12','con_notifytime 0',
         'brg_monster_omniscience false','brg_enemy_walk_tics 5','brg_rat_walk_tics 5','wait 100',
         'brg_actions '+' '.join(actions),'wait 3700','brg_monsters','screenshot encounter.png',
         'brg_actions WAIT','wait 80','brg_monsters','screenshot active.png',
         'brg_actions WAIT','wait 80','brg_monsters','screenshot resolved.png','quit']
    (out/'capture.cfg').write_text('; '.join(cfg)+'\n')
    cmd=[str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),'-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),
         '-file',str(args.package.resolve()),str(ROOT/'generated/seed-26/startup/ProjectBroom-seed-26.pk3'),str(observer),
         '-config',str(out/'test.ini'),'-noautoload','-nosound','-window','-width','1920','-height','1080',
         '+set','vid_fullscreen','false',
         '+set','vid_preferbackend',args.backend,'+set','i_pauseinbackground','false',
         '+set','brg_save_root',str(out/'saves'),'+set','brg_map_compiler',sys.executable,
         '+set','brg_map_compiler_root',str(ROOT),'+set','brg_seed','26',
         '+set','screenshot_dir',str(out),'+map','BRG01','+exec',str(out/'capture.cfg')]
    logpath=out/'runtime.log'
    with logpath.open('w') as log:
        proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT)
        deadline=time.monotonic()+240
        timed_out=False
        while proc.poll() is None:
            text=logpath.read_text(errors='replace')
            if time.monotonic()>deadline or any(e in text for e in ('Script error','VM execution aborted')):
                timed_out=time.monotonic()>deadline
                proc.kill();proc.wait();break
            time.sleep(.25)
    text=logpath.read_text(errors='replace')
    (out/'process-result.json').write_text(json.dumps(dict(returncode=proc.returncode,
        timedOut=timed_out,backend=args.backend,expectedHash=expected,
        reachedEncounter='ARROW_TURRET_NATURAL_VISIBLE' in text,
        lastCommands=[line for line in text.splitlines() if 'Brogue command=' in line][-3:]),indent=2)+'\n')
    assert proc.returncode==0 and 'ARROW_TURRET_NATURAL_VISIBLE' in text,text[-3000:]
    assert 'hash='+format(int(expected,16),'016x') in text,text[-3000:]
    assert 'class=BrogueMonsterK15' in text,text[-3000:]
    assert 'Selecting '+('Vulkan' if args.backend=='1' else 'OpenGL')+' backend' in text
    assert all((out/(name+'.png')).exists() for name in ('encounter','active','resolved'))
    print('Natural seed-26 arrow turret encounter passed:',out)


if __name__=='__main__':main()
