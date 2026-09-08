"""Launch an extracted validation package and restore the real bloodwort run."""
import argparse
import json
import hashlib
from pathlib import Path
import os
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--backend',type=int,choices=(0,1),required=True)
    parser.add_argument('--depth-return',action='store_true')
    args=parser.parse_args()
    out=ROOT/'artifacts/bloodwort/packaged'/(str(args.backend)+('-revisit' if args.depth_return else ''))
    out.mkdir(parents=True,exist_ok=True)
    archive=ROOT/'artifacts/release/0.1.0-bloodwort-validation/ProjectBroom-Windows-x64-0.1.0-bloodwort-validation.zip'
    extracted=ROOT/'artifacts/bloodwort'/('extracted-'+hashlib.sha256(archive.read_bytes()).hexdigest()[:12])
    if not extracted.exists():
        with zipfile.ZipFile(archive) as z: z.extractall(extracted)
    package=next(extracted.glob('*/release-manifest.json')).parent
    saved=out/'input.broguesave'
    shutil.copy2(ROOT/'artifacts/bloodwort/save'/('bloodwort-depth2.broguesave' if args.depth_return else 'bloodwort-turn31.broguesave'),saved)
    probe=subprocess.run([str(package/'ProjectBroom.exe'),'--probe-save',str(saved)],
                         cwd=out,capture_output=True,text=True,timeout=30)
    (out/'launcher-probe.log').write_text(probe.stdout+probe.stderr)
    if probe.returncode: raise RuntimeError('Packaged launcher rejected native save')
    # UZDoom's console wait is cosmetic time, with one explicit native WAIT.
    config=out/'restore.cfg'
    if args.depth_return:
        level=json.loads((ROOT/'artifacts/bloodwort/save/depth2.json').read_text())['levels'][0]
        player=next(c for c in level['cells'] if c['flags']&4)
        delta=(level['upStairs']['x']-player['x'],level['upStairs']['y']-player['y'])
        action={(0,-1):'N',(1,0):'E',(0,1):'S',(-1,0):'W'}[delta]
        transition=f'brg_actions {action}; wait 200; '
    else: transition=''
    config.write_text('wait 350; '+transition+'screenshot bloodwort-restored.png; brg_wait; wait 100; screenshot bloodwort-continued.png; quit\n')
    command=[str(package/'runtime/engine/uzdoom.exe'),'-iwad',str(package/'runtime/iwad/freedoom2.wad'),
             '-file',str(package/'game/ProjectBroom.pk3'),str(ROOT/'generated/seed-1/ProjectBroom-seed-1.pk3'),
             '-config',str(out/'uzdoom.ini'),'-noautoload','-nosound','-window',
             '+set','vid_preferbackend',str(args.backend),'+set','i_pauseinbackground','false',
             '+screenblocks','12','+set','brg_debug','true','+set','brg_seed','1',
             '+set','brg_map_compiler',str(package/'runtime/compiler/ProjectBroomMapCompiler.exe'),
             '+set','brg_load_path',str(saved),'+set','brg_save_root',str(out/'saves'),
             '+set','screenshot_dir',out.as_posix(),'+exec',str(config),'+menu_main']
    environment={('Path' if k.upper()=='PATH' else k):v for k,v in os.environ.items()}
    with (out/'process.log').open('w') as log:
        run=subprocess.run(command,cwd=out,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=100)
    log=(out/'process.log').read_text(errors='replace')
    if run.returncode or f'SAVE_COMPLETE turn={63 if args.depth_return else 32}' not in log or not (out/'bloodwort-restored.png').exists():
        raise RuntimeError(f'Packaged restoration failed: {out}')
    print(f'BLOODWORT package restore/WAIT/save passed: {out}')


if __name__=='__main__': main()
