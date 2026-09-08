"""Extract the validation ZIP, verify shipped masks, restore and play real Brogue."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile
from tools.shoreline_assets import MASKS

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--backend',type=int,choices=(0,1),required=True)
    args=parser.parse_args()
    archive=ROOT/'artifacts/release/0.1.0-shoreline-validation/ProjectBroom-Windows-x64-0.1.0-shoreline-validation.zip'
    signature=hashlib.sha256(archive.read_bytes()).hexdigest()
    extracted=ROOT/'artifacts/shoreline'/('extracted-'+signature[:12])
    if not extracted.exists():
        with zipfile.ZipFile(archive) as z:z.extractall(extracted)
    package=next(extracted.glob('*/release-manifest.json')).parent
    output=ROOT/'artifacts/shoreline/packaged'/str(args.backend)
    output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(package/'game/ProjectBroom.pk3') as z:
        names=['shaders/shoreline.fp','shaders/shoreline/textures.txt','shaders/shoreline/gldefs.txt']
        names += [f'shaders/shoreline/mask-{mask:02x}.png' for mask in MASKS]
        for name in names:
            assert z.read(name)==(ROOT/'mod/BrogueDoom'/name).read_bytes(),name
    source=next((ROOT/'artifacts/shoreline/final/vulkan/1/saves/saves').glob('*.broguesave'))
    save=output/'input.broguesave';shutil.copy2(source,save)
    environment={('Path' if k.upper()=='PATH' else k):v for k,v in os.environ.items()}
    probe=subprocess.run([str(package/'ProjectBroom.exe'),'--probe-save',str(save)],cwd=output,env=environment,capture_output=True,text=True,timeout=30)
    (output/'launcher.log').write_text(probe.stdout+probe.stderr)
    assert probe.returncode==0,probe.stdout+probe.stderr
    config=output/'restore.cfg'
    config.write_text('wait 350; brg_shorelines false; wait 35; screenshot real-before.png; '
        'brg_shorelines true; wait 35; screenshot real-after.png; '
        'brg_actions N; wait 70; screenshot real-move.png; brg_wait; wait 70; screenshot real-wait.png; quit\n')
    command=[str(package/'runtime/engine/uzdoom.exe'),'-iwad',str(package/'runtime/iwad/freedoom2.wad'),
        '-file',str(package/'game/ProjectBroom.pk3'),str(ROOT/'generated/seed-1/ProjectBroom-seed-1.pk3'),
        '-config',str(output/'uzdoom.ini'),'-noautoload','-nosound','-window','-width','1280','-height','800',
        '+set','vid_preferbackend',str(args.backend),'+set','vid_fullscreen','false','+set','i_pauseinbackground','false',
        '+set','screenblocks','12','+set','con_notifytime','0','+set','brg_debug','true','+set','brg_seed','1',
        '+set','brg_map_compiler',str(package/'runtime/compiler/ProjectBroomMapCompiler.exe'),
        '+set','brg_load_path',str(save),'+set','brg_save_root',str(output/'saves'),
        '+set','screenshot_dir',output.as_posix(),'+exec',str(config),'+menu_main']
    with (output/'process.log').open('w') as log:
        run=subprocess.run(command,cwd=output,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=120)
    log=(output/'process.log').read_text(errors='replace')
    assert run.returncode==0 and 'SAVE_COMPLETE turn=2' in log, str(output)
    assert 'accepted=true' in log and 'TERRAIN commit' in log, str(output)
    assert f"Selecting {'Vulkan' if args.backend else 'OpenGL'} backend" in log, str(output)
    for name in ('real-before.png','real-after.png','real-move.png','real-wait.png'):
        assert (output/name).is_file(),name
    (output/'verification.json').write_text(json.dumps({'archiveSha256':signature,'package':str(package),
        'shippedShorelineFiles':len(names),'restoredSeed':1,'continuedTurn':2,'backend':args.backend},indent=2))
    print(f'SHORELINE packaged restore, movement, WAIT, save passed: {output}')

if __name__=='__main__':main()
