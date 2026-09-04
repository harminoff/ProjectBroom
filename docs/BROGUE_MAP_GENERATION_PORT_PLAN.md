# Brogue-to-GZDoom Procedural Map Pipeline

This document records the implementation contract for the first Brogue-to-Doom
milestone. Brogue CE is authoritative for deterministic seeds, generation order,
terrain layers, machines, and stair placement. GZDoom is the downstream renderer
and will later host the turn-based presentation and gameplay consumers.

## Milestone boundary

The pipeline is an external pre-launch compiler. It does not require a GZDoom
fork and does not duplicate Brogue's `Architect.c` logic in ZScript. It targets
GZDoom 4.14.2 with Freedoom Phase 2 during development and produces a 40-depth
campaign using the Brogue 79x29 tactical grid. Items, monsters, combat, field of
view, lighting parity, and save interoperability remain later milestones.

The source of truth is the pinned Brogue CE snapshot at commit
`7f52dd93b7fa553dd6e354ccd44229a3c22d8a76`. The untouched upstream reference is
`tooling/source/BrogueCE`; the tracked exporter snapshot is
`src/brogue-mapgen`. Its provenance and local changes are recorded in
`src/brogue-mapgen/UPSTREAM.md`.

## Repository layout

- `src/brogue-mapgen/`: tracked Brogue CE snapshot plus the JSON exporter.
- `tooling/source/BrogueCE/`: untouched upstream reference checkout.
- `tools/mapcompiler/`: standard-library Python 3.11 JSON-to-UDMF/WAD/PK3 compiler.
- `mod/BrogueDoom/`: static ZScript, DoomEdNums, and runtime support.
- `generated/seed-<seed>/`: disposable JSON, PK3, manifest, and GZDoom log.
- `scripts/build-mapgen.ps1`: rebuilds the pinned headless exporter.
- `scripts/launch-seed.ps1`: validates tools, generates, compiles, and launches.

The pre-existing deleted root `.gitignore` is intentionally not restored or
modified by this milestone.

## Exporter contract

Build the headless exporter with:

```text
pwsh -File scripts/build-mapgen.ps1
```

Its public command is:

```text
brogue.exe --export-dungeon-json <output.json> --seed <positive-seed> --depths <1-40>
```

The exporter selects normal Brogue, calls `initializeRogue(seed)` once, then
generates depths sequentially with the normal `startLevel()` traversal. It does
not reseed or independently generate a depth, because Brogue's cross-depth
state and metered distributions depend on generation order. It writes a
temporary/incomplete output only while exporting and removes it after failure.

The version-one JSON contains:

- schema/source metadata, including the pinned commit and compiled Brogue version;
- decimal-string seed and level seeds, preserving 64-bit values exactly;
- the 79x29 dimensions and a deterministic terrain catalog;
- dungeon, liquid, gas, and surface layer IDs and symbols for every cell;
- permanent cell flags, resolved terrain/mechanical flags, volume, machine, and
  fire-exposure state;
- exact upstairs/downstairs coordinates; and
- reserved empty entity arrays for a future schema version.

Arrays and fields used for hashing are deterministic. Timestamps, absolute
paths, and machine-specific data are excluded.

## UDMF compiler contract

Compile an exported dungeon with:

```text
python tools/mapcompiler/compile.py \
  --input generated/seed-1/brogue-dungeon.json \
  --output generated/seed-1/ProjectBroom-seed-1.pk3
```

The compiler emits `BRG01.wad` through `BRG40.wad` under `/maps/`, root
`MAPINFO`, and `brogue-manifest.json`. Each WAD contains only its map marker,
`TEXTMAP`, and `ENDMAP`; GZDoom builds nodes on load initially.

Geometry is one independently addressable 64x64-unit sector per Brogue cell.
The coordinate conversion is `doom_x = x*64` and
`doom_y = (28-y)*64` for cell centers. Every map uses a shared 80x30 vertex
lattice and therefore has these exact counts:

| UDMF object | Count |
| --- | ---: |
| vertices | 2,400 |
| linedefs | 4,690 |
| sectors | 2,291 |
| sidedefs | 9,164 |

Walkable cells use floor 0 and ceiling 128. Solid cells and closed doors use
floor 0 and ceiling 0 while remaining separate sectors for future tactical
control. Chasms and liquids receive distinct presentation heights/materials;
gas and surface effects remain metadata until their gameplay consumers exist.

Every sector stores the Brogue coordinate and source state in
`user_brogue_x`, `user_brogue_y`, `user_brogue_depth`,
`user_brogue_dungeon`, `user_brogue_liquid`, `user_brogue_gas`,
`user_brogue_surface`, `user_brogue_cell_flags`,
`user_brogue_terrain_flags`, `user_brogue_tm_flags`,
`user_brogue_machine`, and `user_brogue_volume`.

Terrain rendering is keyed by the Brogue enum symbol. Unknown symbols must fail
compilation rather than silently becoming a generic floor. The current mapping
is intentionally placeholder-oriented and can be expanded as the material set
and visual parity work mature.

The package writer fixes ZIP timestamps, entry order, and compression settings,
so identical JSON input produces byte-identical PK3 output.

## GZDoom runtime integration

`mod/BrogueDoom` supplies `BrogueWorldHandler`, `BrogueStair`, and
`BrogueTravelState`, plus fixed stair DoomEdNums 15000 and 15001. On
`WorldLoaded`, the handler reads the UDMF sector metadata, requires exactly one
sector for each coordinate, rejects missing/duplicate/out-of-range cells, and
builds a coordinate-to-sector lookup. A travelling player is placed at the
matching destination stair and the transient travel token is removed.

Entering a stair cell computes the destination from `Level.levelnum +/- 1`,
refuses depths outside 1..40, records whether the destination landing is
upstairs or downstairs, and changes level without an intermission. Arrival
temporarily disarms the landing cell to prevent immediate return travel.
Generated MAPINFO puts all `BRG01`-`BRG40` maps in one hub cluster with level
numbers 1-40. Presentation uses a wall-height ladder for ascent and a
stone-rimmed dark pit with an inset ladder for descent.

## Canonical workflow

```text
pwsh -File scripts/launch-seed.ps1 -Seed 1
```

The launcher validates the pinned exporter, Python 3.11, GZDoom, and
`freedoom2.wad`; exports all 40 depths; recompiles only when the input hash is
new; then launches GZDoom with the static mod, generated PK3, and `BRG01`.
qZDL remains an optional manual launcher for an already-generated package and
is not part of generation.

## Verification gates

1. Build the exporter and preserve Brogue's existing seed-catalog regression
   output for seeds 1-25 across all 40 depths.
2. Export seed 1 twice; require byte-identical JSON and matching SHA-256 values.
3. Validate 40 levels, 2,291 unique cells per level, valid layer IDs, and valid
   stair coordinates.
4. Parse every generated TEXTMAP back into a grid; prove coordinates,
   passability boundaries, and stairs match the JSON.
5. Compile seed 1 twice; require byte-identical PK3 files and the exact geometry
   counts above.
6. Launch `BRG01`, `BRG02`, `BRG26`, and `BRG40` in GZDoom 4.14.2 without
   ZScript, UDMF, missing-texture, or node-builder errors.
7. Verify travel `BRG01->BRG02->BRG01`, `BRG25<->BRG26`, and `BRG39<->BRG40`.
8. Verify a spawned object on BRG01 survives a round trip through the hub.
9. Record export time, package size, and per-map load time. Correctness is the
   gate; node prebuilding can be added later if load measurements justify ZDBSP.

## Deferred work and distribution

Future consumers will use the exported Brogue state for item placement, monster
placement, turn scheduling, combat, inventory, status effects, terrain
evolution, field of view, and presentation parity. Brogue C remains the planned
authority for those rules and RNG decisions.

Modified Brogue CE source and distribution notices remain under AGPL-3.0.
Freedoom licensing must be preserved when its IWAD is redistributed. This is
project hygiene, not legal advice.
