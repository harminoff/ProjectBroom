"""Opt-in full-size terrain geometry renderer probe (not a gameplay test).

Run: python -m tools.test_terrain_renderer --backend 1
UZDoom backend 0 is OpenGL; 1 is Vulkan. Artifacts use isolated configs.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from tools.mapcompiler.compile import make_map_text, make_wad
from tools.mapcompiler.terrain_geometry import verify_geometry

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', type=int, choices=(0, 1), required=True)
    parser.add_argument('--settled', action='store_true')
    parser.add_argument('--animations', action='store_true')
    parser.add_argument('--statues', action='store_true')
    parser.add_argument('--torches', action='store_true')
    parser.add_argument('--bloodwort', action='store_true')
    parser.add_argument('--run-label', default='', help='Separate evidence/config/save directory for a repeat capture')
    parser.add_argument('--benchmark', action='store_true')
    parser.add_argument('--input', action='store_true')
    parser.add_argument('--quality', type=int, choices=(0,1,2), default=1)
    parser.add_argument('--resource-overlay', type=Path, help='Optional preserved asset baseline for visual/timing comparisons')
    parser.add_argument('--package', type=Path, help='Extracted release root; use shipped engine, IWAD and resources')
    args = parser.parse_args()
    if args.benchmark: args.animations=True
    if args.statues or args.torches or args.bloodwort: args.animations=True
    output = ROOT / 'artifacts' / ('terrain-sync' if args.settled else 'terrain-foundation') / ('vulkan' if args.backend == 1 else 'opengl')
    if args.animations:
        output = ROOT/'artifacts/terrain-animation'/('vulkan' if args.backend else 'opengl')/str(args.quality)
    if args.input:
        output=ROOT/'artifacts/terrain-animation'/('vulkan' if args.backend else 'opengl')/'input'
    if args.benchmark: output=output/'benchmark'
    if args.statues: output=ROOT/'artifacts/statues'/('vulkan' if args.backend else 'opengl')/str(args.quality)
    if args.torches: output=ROOT/'artifacts/torches'/('vulkan' if args.backend else 'opengl')/str(args.quality)
    if args.bloodwort: output=ROOT/'artifacts/bloodwort'/('vulkan' if args.backend else 'opengl')/str(args.quality)
    if args.bloodwort and args.benchmark: output=output/'benchmark'
    if args.run_label: output=output/args.run_label
    output.mkdir(parents=True, exist_ok=True)
    captures = ['terrain-initial.png','terrain-door-before.png','terrain-door-after.png'] if args.settled else [f'terrain-{phase:02d}.png' for phase in range(9)]
    if args.animations:
        captures = [f'animation-{stage:02d}-{phase}.png' for stage in range(23) for phase in ('before','during','after')]
    if args.statues:
        captures = [f'animation-{stage:02d}-{phase}.png' for stage in range(23,29) for phase in ('before','during','after')]
    if args.torches:
        captures = [f'animation-{stage:02d}-{phase}.png' for stage in range(29,37) for phase in ('before','during','after')]
    if args.bloodwort:
        captures = [f'animation-{stage:02d}-{phase}.png' for stage in range(37,48) for phase in ('before','during','after')]
    if args.input:
        captures=['terrain-initial.png','terrain-door-before.png','terrain-door-during.png','terrain-door-after.png']
    if args.benchmark: captures=[]
    for capture in captures:
        (output / capture).unlink(missing_ok=True)
    model = json.loads((ROOT / 'generated/seed-1/brogue-dungeon.json').read_text())
    text, _, metadata = make_map_text(model['levels'][0], 79, 29, game_seed='1', addressable=True)
    metadata['geometryVerification'] = verify_geometry(model['levels'][0], text)
    wad = output / 'BRG01.wad'
    wad.write_bytes(make_wad('BRG01', text))
    (output / 'compiler.json').write_text(json.dumps(metadata, indent=2))
    engine = ROOT / '.build/uzdoom/Release/uzdoom.exe'
    iwad = ROOT / '.deps/freedoom-0.13.0/freedoom2.wad'
    resources = ROOT / 'mod/BrogueDoom'
    if args.package:
        package = args.package.resolve()
        engine, iwad, resources = package/'runtime/engine/uzdoom.exe', package/'runtime/iwad/freedoom2.wad', package/'game/ProjectBroom.pk3'
    command = [str(engine), '-iwad', str(iwad),
               '-file', str(resources), str(ROOT / 'generated/seed-1/ProjectBroom-seed-1.pk3'), str(wad),
               '-config', str(output / 'uzdoom.ini'), '-noautoload', '-nosound',
               '-width', '960', '-height', '640', '-window',
               '+set', 'vid_preferbackend', str(args.backend),
               '+set', 'i_pauseinbackground', 'false',
               '+set', 'brg_fx_quality', str(args.quality),
               '+set', 'brg_seed', '1', '+set', 'brg_debug', 'true',
               '+set', 'brg_save_root', (output / 'saves').as_posix(),
               '+set', 'screenshot_dir', output.as_posix(),
               '+set', 'screenblocks', '12', '+set', 'con_notifytime', '0',
               '+set', 'ucm_drawmap', 'false',
               '+brg_bloodwort_benchmark' if args.bloodwort and args.benchmark else '+brg_bloodwort_smoke' if args.bloodwort else '+brg_torch_smoke' if args.torches else '+brg_statue_smoke' if args.statues else '+brg_terrain_animation_benchmark' if args.benchmark else '+brg_terrain_animation_input' if args.input else '+brg_terrain_animation_smoke' if args.animations else '+brg_terrain_sync_smoke' if args.settled else '+brg_terrain_geometry_fixture', '+map', 'BRG01']
    environment = {('Path' if k.upper() == 'PATH' else k): v for k, v in os.environ.items()}
    if args.resource_overlay:
        command.insert(command.index('-config'), str(args.resource_overlay.resolve()))
    with (output / 'process.log').open('w') as log:
        run = subprocess.Popen(command, cwd=output, env=environment, stdout=log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 90
        while run.poll() is None:
            current = (output / 'process.log').read_text(errors='replace')
            if time.monotonic() >= deadline or 'Script error,' in current or 'unknown actor property' in current or 'Unknown render style' in current:
                run.kill()
                run.wait()
                raise RuntimeError(f'Renderer startup or timeout failure: {output}')
            time.sleep(0.25)
    engine_log = (output / 'process.log').read_text(errors='replace')
    success = 'TERRAIN_SYNC passed' if args.settled else 'TERRAIN foundation complete unchangedHash=true'
    if args.animations: success = 'TERRAIN_ANIMATION passed'
    if args.input: success = 'TERRAIN_INPUT passed'
    if run.returncode or success not in engine_log:
        raise RuntimeError(f'Renderer foundation failed; inspect {output}')
    expected_backend = 'Vulkan' if args.backend == 1 else 'OpenGL'
    if f'Selecting {expected_backend} backend' not in engine_log:
        raise RuntimeError(f'Requested renderer was not selected: {output}')
    if any(not (output / capture).is_file() for capture in captures):
        raise RuntimeError(f'Renderer captures incomplete: {output}')
    print(f'Renderer probe passed: {output}')


if __name__ == '__main__':
    main()
