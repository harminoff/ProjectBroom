"""Reproduce a natural seed-26 pink jelly encounter using ordinary Brogue intents.

The route helper reads snapshots to find a route; Brogue validates every move.
The observer only aims a camera at a directly visible existing proxy. It never
reveals, spawns or repositions a creature, or changes health/status/RNG.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from .rat import ROOT


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
    route=[str(exe),'26','12','0','--visible']
    first=subprocess.check_output(route,cwd=out,env=env,text=True)
    assert first==subprocess.check_output(route,cwd=out,env=env,text=True)
    expected='fd84c26107328c93'
    assert 'hash='+expected in first and 'CREATURE kind=12 id=62' in first
    (out/'bridge-route.log').write_text(first)
    actions=first.splitlines()[-1].split()
    observer=out/'observer';observer.mkdir(exist_ok=True)
    (observer/'MAPINFO').write_text('GameInfo { AddEventHandlers="PinkJellyReview" }\n')
    (observer/'ZSCRIPT').write_text('''version "5.0"
class PinkJellyCamera : Actor {
 Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; }
 States { Spawn: TNT1 A -1; Stop; }
}
class PinkJellyReview : EventHandler {
 Actor camera; bool seen;
 override void WorldTick() {
  let pawn=players[consoleplayer].mo;if(!pawn) return;
  let it=ThinkerIterator.Create("BrogueMonsterK12");Actor candidate;Actor subject;double best=100000;
  while(candidate=Actor(it.Next())) {
   double d=(candidate.pos-pawn.pos).Length();
   if(!candidate.bINVISIBLE && candidate.alpha>=1 && d<best) {best=d;subject=candidate;}
  }
  if(!subject) return;
  vector3 eye=(pawn.pos.x,pawn.pos.y,players[consoleplayer].viewz);
  if(!camera) camera=Actor.Spawn("PinkJellyCamera",eye);
  camera.SetOrigin(eye,false);
  vector3 delta=subject.pos+(0,0,14)-eye;
  camera.angle=VectorAngle(delta.x,delta.y);
  camera.pitch=atan2(-delta.z,sqrt(delta.x*delta.x+delta.y*delta.y));
  players[consoleplayer].camera=camera;pawn.bINVISIBLE=true;
  if(!seen) {Console.Printf("PINK_JELLY_NATURAL_VISIBLE distance=%.2f alpha=%.2f",best,subject.alpha);seen=true;}
 }
}
''')
    cfg=['brg_debug true','screenblocks 12','con_notifytime 0','brg_monster_omniscience false',
         'brg_enemy_walk_tics 5','brg_rat_walk_tics 5','wait 100',
         'brg_actions '+' '.join(actions),'wait 2400','brg_monsters','screenshot encounter.png',
         'brg_actions E','wait 80','brg_monsters','screenshot approach.png',
         'brg_actions E','wait 80','brg_monsters','screenshot close.png',
         'brg_actions E','wait 12','screenshot hit.png',
         'wait 80','brg_monsters','screenshot resolved.png','quit']
    (out/'capture.cfg').write_text('; '.join(cfg)+'\n')
    cmd=[str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),'-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),
         '-file',str(args.package.resolve()),str(ROOT/'generated/seed-26/startup/ProjectBroom-seed-26.pk3'),str(observer),
         '-config',str(out/'test.ini'),'-noautoload','-nosound','-window',
         '+set','vid_preferbackend',args.backend,'+set','i_pauseinbackground','false',
         '+set','brg_save_root',str(out/'saves'),'+set','brg_map_compiler',sys.executable,
         '+set','brg_map_compiler_root',str(ROOT),'+set','brg_seed','26',
         '+set','screenshot_dir',str(out),'+map','BRG01','+exec',str(out/'capture.cfg')]
    logpath=out/'runtime.log'
    with logpath.open('w') as log:
        proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT)
        deadline=time.monotonic()+160
        while proc.poll() is None:
            text=logpath.read_text(errors='replace')
            if time.monotonic()>deadline or any(e in text for e in ('Script error','VM execution aborted')):
                proc.kill();proc.wait();raise RuntimeError(text[-3000:])
            time.sleep(.25)
    text=logpath.read_text(errors='replace')
    assert proc.returncode==0 and 'PINK_JELLY_NATURAL_VISIBLE' in text,text[-3000:]
    assert 'hash='+format(int(expected,16),'016x') in text,text[-3000:]
    assert 'class=BrogueMonsterK12' in text,text[-3000:]
    # Two defended hits cause Brogue's real cloning path. These are copied
    # stable IDs, not fixtures spawned by the presentation observer.
    assert 'hash=a07209e57c20cd6d' in text,text[-3000:]
    assert 'id=75 kind=12' in text and 'id=76 kind=12' in text,text[-3000:]
    for clip in ('recoil','smear','drench'):
        assert 'class=BrogueMonsterK12 clip='+clip in text,text[-3000:]
    assert 'Selecting '+('Vulkan' if args.backend=='1' else 'OpenGL')+' backend' in text
    assert all((out/(name+'.png')).exists() for name in ('encounter','approach','close','hit','resolved'))
    print('Natural seed-26 pink jelly encounter passed:',out)


if __name__=='__main__':main()
