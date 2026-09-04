#!/usr/bin/env python3
"""Generate one Brogue depth, compile it as MAP01, and optionally launch GZDoom."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

# Direct script execution puts ``tools/`` on sys.path rather than the project
# root. Add the root explicitly so package imports work from any cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.mapcompiler.compile import COMPILER_VERSION, compile_package, sha256_file
from tools.mapcompiler.debug import write_level_artifacts
from tools.mapcompiler.verify import verify_package, wad_textmap


def project_root() -> Path:
    return PROJECT_ROOT


def export_model(exporter: Path, output_path: Path, seed: int, depth: int) -> dict:
    command = [str(exporter), "--export-dungeon-json", str(output_path), "--seed", str(seed), "--depths", str(depth)]
    success = False
    try:
        result = subprocess.run(command, cwd=project_root(), check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Brogue exporter failed with exit code {result.returncode}")
        model = json.loads(output_path.read_text(encoding="utf-8"))
        success = True
        return model
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"exporter did not produce valid JSON: {error}") from error
    finally:
        # The exporter writes atomically, but remove any incomplete staging
        # file if the process or JSON validation fails.
        if not success:
            output_path.unlink(missing_ok=True)


def launch_gzdoom(package_path: Path) -> int:
    root = project_root()
    gzdoom = root / "tooling" / "GZDoom" / "gzdoom.exe"
    iwad = root / "tooling" / "GZDoom" / "freedoom2.wad"
    mod = root / "mod" / "BrogueDoom"
    for required in (gzdoom, iwad, mod):
        if not required.exists():
            raise RuntimeError(f"required launch path is missing: {required}")
    process = subprocess.Popen(
        [str(gzdoom), "-nosound", "-width", "1280", "-height", "720", "-iwad", str(iwad), "-file", str(mod), str(package_path), "+ucm_mapshowall", "true", "+map", "MAP01"],
        cwd=root,
    )
    return process.pid


def package_matches(input_path: Path, package_path: Path, depth: int) -> bool:
    if not package_path.exists():
        return False
    try:
        with zipfile.ZipFile(package_path) as archive:
            manifest = json.loads(archive.read("brogue-manifest.json"))
        maps = manifest.get("maps")
        return (
            manifest.get("compilerVersion") == COMPILER_VERSION
            and manifest.get("inputSha256") == sha256_file(input_path)
            and isinstance(maps, list)
            and len(maps) == 1
            and maps[0].get("name") == "MAP01"
            and maps[0].get("depth") == depth
        )
    except (OSError, KeyError, TypeError, ValueError, zipfile.BadZipFile):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--depth", required=True, type=int)
    parser.add_argument("--output", type=Path, default=Path("generated"))
    parser.add_argument("--no-launch", action="store_true")
    args = parser.parse_args(argv)
    if args.seed <= 0:
        parser.error("--seed must be positive")
    if args.depth < 1 or args.depth > 40:
        parser.error("--depth must be in the Brogue CE range 1..40")

    root = project_root()
    output_root = args.output if args.output.is_absolute() else root / args.output
    seed_root = output_root / f"seed-{args.seed}"
    seed_root.mkdir(parents=True, exist_ok=True)
    combined_path = seed_root / "brogue-dungeon.json"
    pending_path = seed_root / "brogue-dungeon.pending.json"
    package_path = seed_root / f"ProjectBroom-seed-{args.seed}-depth-{args.depth}.pk3"
    exporter = root / "src" / "brogue-mapgen" / "bin" / "brogue.exe"

    if not exporter.exists():
        raise RuntimeError(f"pinned Brogue exporter is missing: {exporter}")
    model = export_model(exporter, pending_path, args.seed, args.depth)
    pending_path.replace(combined_path)
    level_json, level_txt = write_level_artifacts(model, args.depth, seed_root)
    if not package_matches(combined_path, package_path, args.depth):
        compile_package(combined_path, package_path, depth=args.depth, map_name="MAP01")
    verify_package(combined_path, package_path, depth=args.depth, map_name="MAP01")

    with zipfile.ZipFile(package_path) as archive:
        textmap = wad_textmap(archive.read("maps/map01.wad"), "MAP01")
    textmap_path = seed_root / f"depth-{args.depth}" / "TEXTMAP.txt"
    textmap_path.write_text(textmap, encoding="utf-8")

    print(json.dumps({
        "seed": args.seed,
        "depth": args.depth,
        "levelJson": str(level_json),
        "levelTxt": str(level_txt),
        "textmap": str(textmap_path),
        "package": str(package_path),
        "launched": not args.no_launch,
        "pid": launch_gzdoom(package_path) if not args.no_launch else None,
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"brogue-gzmap: {error}", file=sys.stderr)
        raise SystemExit(2)
