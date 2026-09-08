"""Opt-in shoreline captures and fixed-scene timing in the actual engine."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from tools.mapcompiler.compile import make_map_text, make_wad
from tools.mapcompiler.terrain_geometry import verify_geometry

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--backend',type=int,choices=(0,1),required=True)
    parser.add_argument('--quality',type=int,choices=(0,1,2),default=1)
    parser.add_argument('--benchmark',action='store_true')
    parser.add_argument('--label',default='final')
    parser.add_argument('--package',type=Path,help='Extracted package root; use its shipped engine and material PK3')
    args=parser.parse_args()
    output=ROOT/'artifacts/shoreline'/args.label/('vulkan' if args.backend else 'opengl')/str(args.quality)
    if args.benchmark: output=output/'benchmark'
    output.mkdir(parents=True,exist_ok=True)
    captures=[] if args.benchmark else [output/f'shore-{i:02d}.png' for i in range(11)]
    for path in captures: path.unlink(missing_ok=True)
    model=json.loads((ROOT/'generated/seed-1/brogue-dungeon.json').read_text())
    text,_,metadata=make_map_text(model['levels'][0],79,29,game_seed='1',addressable=True)
    metadata['geometryVerification']=verify_geometry(model['levels'][0],text)
    wad=output/'BRG01.wad';wad.write_bytes(make_wad('BRG01',text))
    (output/'compiler.json').write_text(json.dumps(metadata,indent=2))
    package=args.package.resolve() if args.package else None
    engine=package/'runtime/engine/uzdoom.exe' if package else ROOT/'.build/uzdoom/Release/uzdoom.exe'
    iwad=package/'runtime/iwad/freedoom2.wad' if package else ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'
    resources=package/'game/ProjectBroom.pk3' if package else ROOT/'mod/BrogueDoom'
    command=[str(engine),'-iwad',str(iwad),
        '-file',str(resources),str(ROOT/'generated/seed-1/ProjectBroom-seed-1.pk3'),str(wad),
        '-config',str(output/'uzdoom.ini'),'-noautoload','-nosound','-width','1280','-height','800','-window',
        '+set','vid_preferbackend',str(args.backend),'+set','i_pauseinbackground','false',
        '+set','vid_fullscreen','false',
        '+set','brg_fx_quality',str(args.quality),'+set','brg_seed','1','+set','brg_debug','true',
        '+set','brg_save_root',(output/'saves').as_posix(),'+set','screenshot_dir',output.as_posix(),
        '+set','screenblocks','12','+set','con_notifytime','0','+set','ucm_drawmap','false',
        '+set','vid_vsync','false','+set','cl_capfps','false',
        '+brg_shoreline_benchmark' if args.benchmark else '+brg_shoreline_smoke','+map','BRG01']
    environment={('Path' if k.upper()=='PATH' else k):v for k,v in os.environ.items()}
    with (output/'process.log').open('w') as log:
        run=subprocess.Popen(command,cwd=output,env=environment,stdout=log,stderr=subprocess.STDOUT)
        deadline=time.monotonic()+180
        while run.poll() is None:
            current=(output/'process.log').read_text(errors='replace')
            if time.monotonic()>deadline or any(s in current for s in ('Script error,','Failed to compile','SHADER compilation failed')):
                run.kill();run.wait();raise RuntimeError(f'Renderer failure: {output}')
            time.sleep(.25)
    log=(output/'process.log').read_text(errors='replace')
    assert run.returncode==0 and 'SHORELINE passed' in log, str(output)
    assert f"Selecting {'Vulkan' if args.backend else 'OpenGL'} backend" in log, str(output)
    assert all(path.is_file() for path in captures), str(output)
    print(f'Shoreline renderer passed: {output}')

if __name__=='__main__':main()
