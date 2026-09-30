"""Opt-in seed-one renderer gallery; synthetic copied state, never gameplay edits."""
import argparse
import os
from pathlib import Path
import subprocess
import json
import sys
from tools.mapcompiler.compile import make_map_text, make_wad
from tools.mapcompiler.terrain_geometry import verify_geometry

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--label',required=True)
    parser.add_argument('--backend',default=1,type=int)
    parser.add_argument('--resources',type=Path,default=ROOT/'mod/BrogueDoom')
    parser.add_argument('--debris',action='store_true')
    parser.add_argument('--walls',action='store_true')
    parser.add_argument('--fall',action='store_true')
    parser.add_argument('--potions',action='store_true')
    parser.add_argument('--flavors',action='store_true')
    args=parser.parse_args()
    out=ROOT/'artifacts/terrain-overlays'/args.label; out.mkdir(parents=True,exist_ok=True)
    captures=[f'overlay-{i:02d}.png' for i in range(9 if args.debris else 13)]
    if args.walls or args.fall: captures=['wall-fade-initial.png','wall-fade-reconciled.png']
    if args.potions: captures=[f'potion-colors-{i}.png' for i in range(3)]
    if args.flavors: captures=[f'flavors-{i:02d}.png' for i in range(21)]
    model=json.loads((ROOT/'generated/seed-1/brogue-dungeon.json').read_text())
    text,_,metadata=make_map_text(model['levels'][0],79,29,game_seed='1',addressable=True)
    metadata['geometryVerification']=verify_geometry(model['levels'][0],text)
    wad=out/'BRG01.wad'; wad.write_bytes(make_wad('BRG01',text))
    (out/'compiler.json').write_text(json.dumps(metadata,indent=2))
    engine=ROOT/'.build/uzdoom/Release/uzdoom.exe'
    cmd=[str(engine),'-iwad',str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),'-file',str(args.resources.resolve()),str(ROOT/'generated/seed-1/ProjectBroom-seed-1.pk3'),str(wad),
         '-config',str(out/'uzdoom.ini'),'-noautoload','-nosound','-width','960','-height','640','-window',
         '+set','vid_preferbackend',str(args.backend),'+set','i_pauseinbackground','false',
         '+set','brg_seed','1','+set','brg_debug','true','+set','brg_save_root',str(out/'saves'),
         '+set','brg_map_compiler',sys.executable,'+set','brg_map_compiler_root',str(ROOT),
         '+set','screenblocks','12','+set','con_notifytime','0','+set','screenshot_dir',out.as_posix(),'+brg_potion_color_smoke' if args.potions else '+brg_wall_fall_smoke' if args.fall else '+brg_wall_fade_smoke' if args.walls else '+brg_debris_smoke' if args.debris else '+brg_overlay_smoke','+map','BRG01']
    env={('Path' if k.upper()=='PATH' else k):v for k,v in os.environ.items()}
    if args.flavors: cmd[cmd.index('+brg_overlay_smoke')]='+brg_flavor_smoke'
    with (out/'process.log').open('w') as log:
        run=subprocess.run(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180 if args.fall else 75)
    text=(out/'process.log').read_text(errors='replace')
    marker='authoritativeFall=1' if args.fall else 'unchangedHash=true'
    if run.returncode or any(not (out/c).exists() for c in captures) or marker not in text:
        raise RuntimeError(f'Gallery failed: {out}')
    print(f'Captured {len(captures)} views: {out}')

if __name__=='__main__': main()
