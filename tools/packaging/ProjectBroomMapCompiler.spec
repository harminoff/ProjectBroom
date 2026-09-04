# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_root = Path(SPECPATH).parents[1]
datas = [
    (str(project_root / "assets" / "terrain" / "broguedoom_cave_registry.json"), "assets/terrain"),
    (str(project_root / "mod" / "BrogueDoom"), "mod/BrogueDoom"),
    (str(project_root / "tools" / "mapcompiler" / "terrain_render_map.json"), "tools/mapcompiler"),
]

a = Analysis(
    [str(project_root / "tools" / "mapcompiler" / "cli.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=["tools.mapcompiler.compile", "tools.mapcompiler.verify"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ProjectBroomMapCompiler",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
