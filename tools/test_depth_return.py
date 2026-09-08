"""Opt-in natural first-visit/revisit regression for stale Doom hub snapshots.

Requires the canonical build and generated seed-208360664 startup campaign.
Uses ordinary Brogue movement commands; Brogue resolves doors and combat.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--backend',type=int,choices=(0,1),required=True)
    parser.add_argument('--run-label',default='fixed')
    args=parser.parse_args()
    out=ROOT/'artifacts/depth-return'/f'{args.run_label}-{args.backend}'
    out.mkdir(parents=True,exist_ok=True)
    # One queue retains every action while variable-length creature animations run.
    actions=(ROOT/'tools/fixtures/depth-return-actions.txt').read_text().split()
    bridge=[str(ROOT/'src/brogue-mapgen/bin/brogue-bridge.exe'),'--seed','208360664','--actions',','.join(actions)]
    baseline=subprocess.check_output(bridge,cwd=out,text=True)
    assert baseline==subprocess.check_output(bridge,cwd=out,text=True)
    assert 'hash=6550a30ebb2e5fb8' in baseline
    (out/'bridge.log').write_text(baseline)
    cfg=['brg_debug true','screenblocks 12','wait 100','brg_actions '+' '.join(actions),'wait 1400']
    cfg+=['wait 35','brg_monsters','screenshot returned.png','quit']
    (out/'capture.cfg').write_text('; '.join(cfg)+'\n')
    cmd=[str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),
         '-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),
         '-file',str(ROOT/'mod/BrogueDoom'),str(ROOT/'generated/seed-208360664/startup/ProjectBroom-seed-208360664.pk3'),
         '-config',str(out/'test.ini'),'-noautoload','-nosound','-window',
         '+set','vid_preferbackend',str(args.backend),'+set','i_pauseinbackground','false',
         '+set','brg_save_root',str(out/'saves'),'+set','brg_map_compiler',sys.executable,
         '+set','brg_map_compiler_root',str(ROOT),'+set','brg_seed','208360664',
         '+set','screenshot_dir',str(out),'+map','BRG01','+exec',str(out/'capture.cfg')]
    env={('Path' if k.upper()=='PATH' else k):v for k,v in os.environ.items()}
    log=out/'runtime.log'
    with log.open('w') as stream:
        proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=stream,stderr=subprocess.STDOUT)
        deadline=time.monotonic()+120
        while proc.poll() is None:
            text=log.read_text(errors='replace')
            if time.monotonic()>deadline or 'Savegame is from a different level' in text or 'VM execution aborted' in text:
                proc.kill();proc.wait();raise RuntimeError(f'Depth return failed: {out}')
            time.sleep(.25)
    text=log.read_text(errors='replace')
    assert proc.returncode==0 and 'Savegame is from a different level' not in text,text[-3000:]
    assert 'Selecting '+('Vulkan' if args.backend else 'OpenGL')+' backend' in text
    assert text.count('authoritative level change to BRG02')==1
    assert text.count('authoritative level change to BRG01')==1
    assert 'hash=6550a30ebb2e5fb8' in text
    assert (out/'returned.png').is_file()
    print('Natural depth return passed:',out)

if __name__=='__main__':main()
