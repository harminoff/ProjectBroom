# Brogue CE → GZDoom map-generation research

This prototype keeps Brogue CE authoritative for dungeon topology and terrain.
The converter consumes a generated snapshot; it does not reimplement rooms,
corridors, lakes, machines, bridges, doors, or RNG in Python or ZScript.

## Local source basis

The untouched reference is `tooling/source/BrogueCE`. The modified, pinned
exporter is `src/brogue-mapgen`, based on commit
`7f52dd93b7fa553dd6e354ccd44229a3c22d8a76`. The current local source tree
contains the Brogue source and the GZDoom 4.14.2 binary/runtime package, but it
does not contain a GZDoom `src/maploader`, `specs`, or `wadsrc` source checkout.
The runtime package is therefore treated as a black-box compatibility target;
the generated UDMF is restricted to standard `ZDoom` entities and properties.

## Brogue generation flow

The relevant local functions are:

- `src/brogue/RogueMain.c:initializeRogue()` initializes the selected variant,
  game seed, metered state, and every `levels[i].levelSeed` in sequence.
- `src/brogue/RogueMain.c:startLevel()` is the canonical level-entry path. It
  seeds the substantive RNG from `levels[rogue.depthLevel - 1].levelSeed`, calls
  the level generator, places stairs, performs Brogue's initialization and
  environment simulation, and restores the caller RNG state.
- `src/brogue/Architect.c:digDungeon()` is the master terrain generator. The
  local implementation runs `clearLevel`, `carveDungeon`, `addLoops`, converts
  the carved grid to floor/door terrain, `finishWalls(false)`, designs and
  fills lakes, runs non-machine autogenerators, removes diagonal openings, adds
  machines, runs machine autogenerators, cleans lake boundaries, builds bridges,
  finishes doors, and runs `finishWalls(true)`.
- `src/brogue/Architect.c:placeStairs()` chooses qualifying positions using
  Brogue's own maps and flags, writes the up/down stair terrain, and carries the
  next level's connecting stair location forward.
- `src/brogue/RogueMain.c:initializeLevel()` populates the normal level and the
  current exporter invokes it through `startLevel`; item/monster data is not
  serialized. This is retained because the local level-entry path includes
  terrain-affecting cleanup and the 50-turn environment simulation. The next
  extraction refinement can isolate those calls after an A/B snapshot proves
  identical pmap terrain.

The exporter calls `initializeGameVariant()` once, then
`initializeRogue(gameSeed)` once, and advances from depth 1 through the
requested depth with `startLevel()`. It never derives a depth seed itself and
never calls `digDungeon()` independently for a requested depth.

## Brogue data captured

The source `Rogue.h` defines `pcell` as four terrain layers (`DUNGEON`,
`LIQUID`, `GAS`, `SURFACE`), permanent cell flags, gas volume, machine number,
remembered display/item/terrain state, and fire exposure. The exporter keeps
all of those fields in JSON, plus the resolved `terrainFlags()` and
`terrainMechFlags()` values from `Globals.c`.

Each cell also has a derived semantic record calculated from Brogue's actual
catalog flags and layer values: solid/walkable/pathing-blocked, vision and
diagonal blockers, door/secret, liquid/deep water/lava/chasm/bridge, stairs,
and machine terrain. Raw IDs and symbols remain alongside these semantics.

Important flag meanings come directly from `Rogue.h`, including
`T_OBSTRUCTS_PASSABILITY`, `T_OBSTRUCTS_VISION`,
`T_OBSTRUCTS_DIAGONAL_MOVEMENT`, `T_PATHING_BLOCKER`, `T_AUTO_DESCENT`,
`T_LAVA_INSTA_DEATH`, `T_IS_DEEP_WATER`, `T_CAN_BE_BRIDGED`, and `TM_IS_SECRET`.

## Snapshot and debug artifacts

The C interface is the existing CLI contract:

```text
brogue.exe --export-dungeon-json <output.json> --seed <game-seed> --depths <N>
```

The development wrapper is:

```text
python tools/brogue_gzmap.py --seed 12345 --depth 8
```

It exports sequentially through depth 8, writes the combined source snapshot,
then creates:

```text
generated/seed-12345/
    brogue-dungeon.json
    brogue-manifest.json
    depth-8/
        level.json
        level.txt
        TEXTMAP.txt
    ProjectBroom-seed-12345-depth-8.pk3
```

`level.txt` is an ASCII diagnostic projection of the final snapshot. Its
symbols are selected from raw layer symbols and the C-derived semantic record:
`#` wall, `.` floor, `+` door, `<`/`>` stairs, `~` liquid, `^` lava, `_` chasm,
`=` bridge, and `,` surface vegetation.

## GZDoom format and package

The compiler emits UDMF using `namespace = "ZDoom";`. A generated map WAD has
exactly this lump sequence:

```text
MAP01
TEXTMAP
ENDMAP
```

The standalone prototype package is:

```text
ProjectBroom-seed-12345-depth-8.pk3
    MAPINFO
    brogue-manifest.json
    maps/map01.wad
```

The existing campaign compiler also supports the 40-map package with
`maps/BRG01.wad` through `maps/BRG40.wad`. ZIP timestamps, entry order, and
compression are fixed for reproducible packages.

## Geometry decisions

The current implementation uses 64×64 world cells and a shared 80×30 vertex
lattice. The Y transform is
`worldY = (height - gridY) * 64`; cell centers use the corresponding inverted
row. The JSON retains all 2,291 Brogue cells, while the UDMF map emits one
physical sector for each traversable cell and one-sided perimeter walls beside
solid cells. This is the first prototype's practical interpretation of “one
sector per relevant traversable cell”.

Open/open cardinal neighbors share a two-sided portal. A solid/open, door/open,
or outer boundary is a blocking one-sided wall face on the traversable side.
For seed 1 depth 8, the emitted map has 2,400 lattice vertices, 952 physical
sectors, 2,283 unique grid edges, and 3,808 sidedefs. Counts vary with the
source map's passable-cell count. The static handler accepts this
traversable-sector subset and leaves solid cells represented by null entries in
its future coordinate lookup.

Corner safety follows from sealing every solid/open cardinal edge with a full
wall face. The verifier checks every emitted line's blocking flag against the
source semantic classification; focused tests cover malformed references,
determinism, unique grid edges, and solid-boundary output. Full 2×2 diagonal
movement parity is a planned expansion of the verifier.

## Runtime boundary

`mod/BrogueDoom` is limited to map validation, sector metadata lookup, stairs,
and placeholder materials. It does not add combat, monsters, items, inventory,
turn scheduling, UI, sound, spells, or progression. The one-command wrapper
launches GZDoom directly into `MAP01`; the static campaign launcher continues
to use `BRG01`–`BRG40`.

## Known limitations

- The local GZDoom source/spec directories requested by the original research
  brief are not present, so loader behavior is validated against the installed
  GZDoom 4.14.2 executable.
- The current C exporter uses canonical `startLevel()` for source fidelity and
  discards generated entity lists. A future source-backed extraction seam may
  skip entity population only after proving identical final terrain.
- The first prototype uses placeholder Freedoom materials and ordinary Doom
  movement. It is a geometry inspection build, not a Brogue gameplay port.
- A true GZDoom screenshot is runtime evidence and is not synthesized by the
  compiler; capture it after the launched `MAP01` window is visible.
- Reintroducing every solid cell as a physical zero-height sector remains
  deferred until a prebuilt-node path is available and measured; the compact
  traversable-sector path is the current runtime-compatible representation.
