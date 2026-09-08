"""Capture fixed hand poses in the actual UZDoom renderer.

Presentation-only MODELDEF overrides hold each pose on the starting dagger;
no inventory, Brogue action, or gameplay fixture is needed.
"""
import argparse
import os
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
POSES = {
    'dagger': ('weapons/weapon_00.md3', 0),
    'broadsword': ('weapons/weapon_02.md3', 0),
    'spear': ('weapons/weapon_08.md3', 0),
    'dart': ('weapons/weapon_12.md3', 0),
    'release': ('weapons/weapon_12.md3', 12),
    'staff': ('devices/staff.md3', 0),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=(0, 1), type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline-archive', type=Path)
    parser.add_argument('--pose', choices=tuple(POSES))
    args = parser.parse_args()
    environment = {('Path' if k.upper() == 'PATH' else k): v for k, v in os.environ.items()}
    for name, (model, frame) in POSES.items():
        if args.pose and name != args.pose:
            continue
        output = args.output.resolve() / str(args.backend) / name
        output.mkdir(parents=True, exist_ok=True)
        overlay = output / 'poses.pk3'
        with zipfile.ZipFile(overlay, 'w') as archive:
            if args.baseline_archive:
                with zipfile.ZipFile(args.baseline_archive) as baseline:
                    for entry in sorted(baseline.namelist()):
                        prefix = 'mod/BrogueDoom/models/'
                        if entry.startswith(prefix):
                            archive.writestr(zipfile.ZipInfo(entry.removeprefix('mod/BrogueDoom/')), baseline.read(entry))
            definition = ('Model BrogueViewWeaponK00\n{\n Path "models"\n'
                          f' Model 0 "{model}"\n Skin 0 "graphics/BRGHANDS.png"\n'
                          ' Scale 1 1 1\n ScaleWeaponFOV\n')
            definition += '\n'.join(f' FrameIndex BW00 {chr(65+i)} 0 {frame}' for i in range(16))+'\n}\n'
            archive.writestr(zipfile.ZipInfo('MODELDEF'), definition)
        config = output / 'capture.cfg'
        config.write_text('wait 100; screenshot view.png; wait 5; quit\n')
        capture = output / 'view.png'
        capture.unlink(missing_ok=True)
        command = [str(ROOT/'.build/uzdoom/Release/uzdoom.exe'),
                   '-iwad', str(ROOT/'.deps/freedoom-0.13.0/freedoom2.wad'),
                   '-file', str(ROOT/'mod/BrogueDoom'),
                   str(ROOT/'generated/seed-1/ProjectBroom-seed-1.pk3'), str(overlay),
                   '-config', str(output/'test.ini'), '-noautoload', '-nosound', '-window',
                   '+set', 'vid_preferbackend', str(args.backend),
                   '+set', 'i_pauseinbackground', 'false', '+set', 'brg_seed', '1',
                   '+set', 'brg_save_root', str(output/'saves'),
                   '+set', 'screenshot_dir', str(output), '+set', 'con_notifytime', '0',
                   '+set', 'screenblocks', '12', '+map', 'BRG01', '+exec', str(config)]
        log_path = output/'runtime.log'
        with log_path.open('w') as log:
            subprocess.run(command, cwd=output, env=environment, stdout=log,
                           stderr=subprocess.STDOUT, timeout=50, check=True)
        backend = 'Vulkan' if args.backend else 'OpenGL'
        text = log_path.read_text(errors='replace')
        if not capture.is_file() or f'Selecting {backend} backend' not in text or 'Script error' in text:
            raise RuntimeError(f'Hand capture failed: {log_path}')
        print(f'{backend}: {name}: {capture}', flush=True)


if __name__ == '__main__':
    main()
