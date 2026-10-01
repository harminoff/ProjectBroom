"""Natural bloat death or pit-bloat fall: normal intents and player-eye camera."""
import argparse
import os
import subprocess
import sys
import time
from .rat import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--backend',choices=('0','1'),required=True)
    parser.add_argument('--pit',action='store_true')
    args=parser.parse_args()
    seed,kind,expected=(27,7,'51456a766cb43c62') if args.pit else (4,6,'464a4af7a0c08c6b')
    symbol='MK_PIT_BLOAT' if args.pit else 'MK_BLOAT'
    out=ROOT/('artifacts/pit-bloat-encounter' if args.pit else 'artifacts/bloat-encounter')/args.backend;out.mkdir(parents=True,exist_ok=True)
    exe=out/'route.exe'
    subprocess.run(['g++','-std=c++17','-static',str(ROOT/'tools/monster_models/bloat_encounter.cpp'),str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.dll'),'-o',str(exe)],check=True)
    env={k.upper():v for k,v in os.environ.items()};env['PATH']=str(ROOT/'src/brogue-mapgen/bin')+';'+env['PATH']
    route_command=[str(exe),str(seed),str(kind)]
    first=subprocess.check_output(route_command,cwd=out,env=env,text=True)
    assert first==subprocess.check_output(route_command,cwd=out,env=env,text=True)
    assert 'SUCCESS' in first and 'hash='+expected in first,first
    if args.pit: assert 'PIT_CREATED' in first or 'PIT_FALL' in first,first
    (out/'bridge-route.log').write_text(first)
    actions=first.splitlines()[-1].split()
    observer=out/'observer';observer.mkdir(exist_ok=True)
    (observer/'MAPINFO').write_text('GameInfo { AddEventHandlers="BloatEncounterReview" }\n')
    (observer/'ZSCRIPT').write_text('''version "5.0"
class BloatReviewCamera : Actor { Default { +NOINTERACTION; +NOBLOCKMAP; +NOGRAVITY; RenderStyle "None"; CameraHeight 0; } States { Spawn: TNT1 A -1; Stop; } }
class BloatEncounterReview : EventHandler {
 Actor camera; bool seen;
 override void WorldTick() {
  let pawn=players[consoleplayer].mo;if(!pawn) return;
  let it=ThinkerIterator.Create("BrogueMonsterK06");Actor candidate;Actor subject;double best=100000;
  while(candidate=Actor(it.Next())) {
   double d=(candidate.pos-pawn.pos).Length();
   if(!candidate.bINVISIBLE && candidate.alpha>=1 && d<best) {best=d;subject=candidate;}
  }
  if(!subject) return;
  vector3 eye=(pawn.pos.x,pawn.pos.y,players[consoleplayer].viewz);
  if(!camera) camera=Actor.Spawn("BloatReviewCamera",eye);
  camera.SetOrigin(eye,false);
  vector3 delta=subject.pos+(0,0,32)-eye;
  camera.angle=VectorAngle(delta.x,delta.y);camera.pitch=atan2(-delta.z,sqrt(delta.x*delta.x+delta.y*delta.y));
  players[consoleplayer].camera=camera;pawn.bINVISIBLE=true;
  if(!seen) {Console.Printf("BLOAT_NATURAL_VISIBLE distance=%.2f alpha=%.2f",best,subject.alpha);seen=true;}
 }
}
'''.replace('BrogueMonsterK06',f'BrogueMonsterK{kind:02d}'))
    cfg=['brg_debug true','screenblocks 12','con_notifytime 0','brg_enemy_walk_tics 5','brg_rat_walk_tics 5','wait 100',
         'brg_actions '+' '.join(actions[:-1]),'wait 900','brg_monsters','screenshot before-burst.png',
         'brg_actions '+actions[-1],'wait 12','screenshot burst-early.png','wait 10','screenshot collapse.png',
         'wait 80','screenshot gas.png','brg_monsters','quit']
    (out/'capture.cfg').write_text('; '.join(cfg)+'\n')
    package=ROOT/'artifacts/skeletal-review'/symbol/('vulkan' if args.backend=='1' else 'opengl')/'ProjectBroom-review.pk3'
    cmd=[str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),'-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),
        '-file',str(package),str(ROOT/f'generated/seed-{seed}/startup/ProjectBroom-seed-{seed}.pk3'),str(observer),
        '-config',str(out/'test.ini'),'-noautoload','-nosound','-window',
        '+set','vid_preferbackend',args.backend,'+set','i_pauseinbackground','false',
        '+set','brg_save_root',str(out/'saves'),'+set','brg_map_compiler',sys.executable,
        '+set','brg_map_compiler_root',str(ROOT),'+set','brg_seed',str(seed),
        '+set','screenshot_dir',str(out),'+map','BRG01','+exec',str(out/'capture.cfg')]
    logpath=out/'runtime.log'
    with logpath.open('w') as log:
        proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT);deadline=time.monotonic()+100
        while proc.poll() is None:
            text=logpath.read_text(errors='replace')
            if time.monotonic()>deadline or any(s in text for s in ('Script error','VM execution aborted')):
                proc.kill();proc.wait();raise RuntimeError(text[-3000:])
            time.sleep(.25)
    text=logpath.read_text(errors='replace')
    assert proc.returncode==0 and 'BLOAT_NATURAL_VISIBLE' in text,text[-3000:]
    if not args.pit:
        assert f'class=BrogueMonsterK{kind:02d} clip=collapse' in text,text[-3000:]
    else:
        assert 'Brogue fall transition: departing.' in text
        assert 'Brogue fall transition: arriving.' in text
        assert f'Brogue fall transition: complete turn=69 hash={expected}' in text
    assert 'hash='+expected in text,text[-3000:]
    assert all((out/(n+'.png')).exists() for n in ('before-burst','burst-early','collapse','gas'))
    print(f'Natural seed-{seed} {symbol} encounter passed:',out)


if __name__=='__main__':main()
