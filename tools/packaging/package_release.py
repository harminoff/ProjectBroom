#!/usr/bin/env python3
"""Assemble deterministic Project Broom runtime and corresponding-source ZIPs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import zipfile
from pathlib import Path

ZIP_TIME = (2026, 1, 1, 0, 0, 0)
PUBLIC_ROOT_FILES = {
    ".editorconfig", ".gitattributes", ".gitignore", "AGENTS.md",
    "ASSETS-LICENSE.md", "CODE_OF_CONDUCT.md", "CONTRIBUTING.md",
    "dependencies.lock.json", "LICENSE", "README.md", "SECURITY.md",
    "SUPPORT.md", "THIRD_PARTY_NOTICES.md",
}
PUBLIC_ROOTS = {".github", "assets", "docs", "mod", "patches", "scripts", "src", "tools"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def excluded(relative: str) -> bool:
    parts = relative.replace("\\", "/").split("/")
    if any(part in {".git", ".deps", ".build", "artifacts", "generated", "tooling", "crash-analysis", "obj", "__pycache__"} for part in parts):
        return True
    lower = relative.lower().replace("\\", "/")
    if lower.startswith("docs/cc4-") or lower == "assets/terrain/cc4_cave_registry.json":
        return True
    if lower.startswith("tools/broguedoomlauncher/bin/"):
        return True
    if lower.startswith("tools/") and any(token in Path(lower).name for token in ("cc4", "reference_wads")):
        return True
    if lower.startswith("src/brogue-mapgen/bin/") and not lower.startswith("src/brogue-mapgen/bin/assets/"):
        return True
    if lower.startswith("src/brogue-mapgen/vars/"):
        return True
    if Path(lower).suffix in {".exe", ".dll", ".pdb", ".ilk", ".lib", ".exp", ".o", ".a", ".pyc", ".zip", ".7z", ".wad"}:
        return True
    return False


def public_source_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts[0] not in PUBLIC_ROOTS and relative.as_posix() not in PUBLIC_ROOT_FILES:
            continue
        if not excluded(relative.as_posix()):
            yield path, relative


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def zip_tree(root: Path, output: Path, prefix: str = "") -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            name = Path(prefix) / path.relative_to(root)
            info = zipfile.ZipInfo(name.as_posix(), ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = path.stat().st_mode
            info.external_attr = ((stat.S_IFREG | (0o755 if mode & stat.S_IXUSR else 0o644)) << 16)
            archive.writestr(info, path.read_bytes())


def locate(engine_dir: Path, name: str, fallback_dir: Path | None = None) -> Path:
    candidates = [engine_dir / name, engine_dir / "Release" / name]
    if fallback_dir is not None:
        candidates.append(fallback_dir / name)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"missing engine runtime file: {name}")


def assemble(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    root = args.root.resolve()
    output = args.output.resolve()
    stage = output / "stage" / f"ProjectBroom-{args.version}"
    source_stage = output / "source-stage" / f"ProjectBroom-Source-{args.version}"
    if stage.exists():
        shutil.rmtree(stage)
    if source_stage.exists():
        shutil.rmtree(source_stage)
    stage.mkdir(parents=True)
    source_stage.mkdir(parents=True)

    copy_file(args.launcher.resolve(), stage / "ProjectBroom.exe")
    engine_target = stage / "runtime" / "engine"
    engine_runtime = root / ".deps" / "gzdoom-runtime-4.14.2"
    for name in ("gzdoom.exe", "gzdoom.pk3", "game_support.pk3", "game_widescreen_gfx.pk3", "brightmaps.pk3", "lights.pk3", "openal32.dll", "zmusic.dll", "sndfile.dll"):
        copy_file(locate(args.engine_dir.resolve(), name, engine_runtime), engine_target / name)
    copy_file(root / "src" / "brogue-mapgen" / "bin" / "brogue.exe", stage / "runtime" / "brogue" / "brogue.exe")
    copy_file(root / "src" / "brogue-mapgen" / "bin" / "brogue-bridge.dll", engine_target / "brogue-bridge.dll")
    copy_file(args.mapcompiler.resolve(), stage / "runtime" / "compiler" / "ProjectBroomMapCompiler.exe")
    copy_file(root / ".deps" / "freedoom-0.13.0" / "freedoom2.wad", stage / "runtime" / "iwad" / "freedoom2.wad")

    static_pk3 = stage / "game" / "ProjectBroom.pk3"
    zip_tree(root / "mod" / "BrogueDoom", static_pk3)

    for name in ("LICENSE", "ASSETS-LICENSE.md", "THIRD_PARTY_NOTICES.md", "README.md"):
        copy_file(root / name, stage / "licenses" / name)
    copy_file(root / "src" / "brogue-mapgen" / "LICENSE.txt", stage / "licenses" / "BrogueCE-AGPL-3.0.txt")
    copy_file(root / ".deps" / "gzdoom-source" / "LICENSE", stage / "licenses" / "GZDoom-GPL-3.0.txt")
    copy_file(engine_runtime / "licenses.zip", stage / "licenses" / "GZDoom-runtime-licenses.zip")
    for name in ("COPYING.txt", "CREDITS.txt", "CREDITS-MUSIC.txt"):
        copy_file(root / ".deps" / "freedoom-0.13.0" / name, stage / "licenses" / "Freedoom" / name)
    copy_file(root / "mod" / "BrogueDoom" / "ULTIMATECLASSICMINIMAP-LICENSE.txt", stage / "licenses" / "UltimateClassicMinimap-MIT.txt")

    lock = json.loads((root / "dependencies.lock.json").read_text(encoding="utf-8"))
    files = []
    for path in sorted(p for p in stage.rglob("*") if p.is_file()):
        relative = path.relative_to(stage).as_posix()
        files.append({"path": relative, "size": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "schemaVersion": 1,
        "product": "Project Broom",
        "version": args.version,
        "platform": "win-x64",
        "dataRoot": "%LOCALAPPDATA%/ProjectBroom",
        "paths": {
            "engine": "runtime/engine/gzdoom.exe",
            "bridge": "runtime/engine/brogue-bridge.dll",
            "exporter": "runtime/brogue/brogue.exe",
            "compiler": "runtime/compiler/ProjectBroomMapCompiler.exe",
            "iwad": "runtime/iwad/freedoom2.wad",
            "staticMod": "game/ProjectBroom.pk3",
        },
        "components": lock["components"],
        "files": files,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (stage / "release-manifest.json").write_bytes(manifest_bytes)
    (output / "release-manifest.json").write_bytes(manifest_bytes)

    for path, relative in public_source_files(root):
        copy_file(path, source_stage / relative)
    gzdoom_source = root / ".deps" / "gzdoom-source"
    for path in sorted(p for p in gzdoom_source.rglob("*") if p.is_file()):
        relative = path.relative_to(gzdoom_source)
        if ".git" in relative.parts or any(part.startswith("build") for part in relative.parts):
            continue
        copy_file(path, source_stage / "third_party_source" / "gzdoom-g4.14.2" / relative)
    for checkout_name, archive_name in (
        ("zmusic-source", "ZMusic-1.1.14"),
        ("libsndfile-source", "libsndfile-1.2.2"),
        ("openal-soft-source", "openal-soft-1.23.1"),
    ):
        checkout = root / ".deps" / checkout_name
        for path in sorted(p for p in checkout.rglob("*") if p.is_file()):
            relative = path.relative_to(checkout)
            if ".git" in relative.parts or any(part.startswith("build") for part in relative.parts):
                continue
            copy_file(path, source_stage / "third_party_source" / archive_name / relative)

    runtime_zip = output / f"ProjectBroom-Windows-x64-{args.version}.zip"
    source_zip = output / f"ProjectBroom-Source-{args.version}.zip"
    zip_tree(stage, runtime_zip, stage.name)
    zip_tree(source_stage, source_zip, source_stage.name)
    checksums = f"{sha256(runtime_zip)}  {runtime_zip.name}\n{sha256(source_zip)}  {source_zip.name}\n"
    checksum_path = output / "SHA256SUMS.txt"
    checksum_path.write_text(checksums, encoding="ascii", newline="\n")
    return runtime_zip, source_zip, checksum_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--engine-dir", required=True, type=Path)
    parser.add_argument("--launcher", required=True, type=Path)
    parser.add_argument("--mapcompiler", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    for path in assemble(args):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
