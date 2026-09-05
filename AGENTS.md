# Project Broom Agent and Contribution Guide

This file is mandatory reading for every human contributor and every coding
agent before planning, editing, generating assets, or opening a pull request.
Instructions in a more deeply nested `AGENTS.md` may add local constraints but
must not weaken the authority and parity rules in this file.

## What Project Broom is

Project Broom runs Brogue CE as the game and uses UZDoom as its 3D
presentation and input frontend.

```text
player input
    -> UZDoom translates intent
    -> stable Brogue bridge command
    -> Brogue CE validates and resolves it
    -> Brogue advances its authoritative simulation
    -> copied state and events cross the bridge
    -> UZDoom updates presentation
```

Brogue CE owns all gameplay truth:

- dungeon generation and topology;
- random-number generation;
- player and creature positions;
- movement legality and diagonal restrictions;
- turns, timing, monsters, combat, items, statuses, and equipment;
- terrain promotion, traps, doors, liquids, fire, gas, and machines;
- visibility, discovery, messages, stairs, saving, and recordings.

UZDoom owns only presentation and input translation:

- 3D geometry and rendering;
- camera control and visual interpolation;
- models, textures, sprites, particles, lighting, and sound;
- menus, overlays, accessibility, and controller/keyboard mapping;
- frontend actors that mirror bridge entity IDs.

The governing rule is:

> UZDoom asks Brogue what happens. UZDoom never decides what happens.

The project is not a Brogue-inspired Doom mod and is not a reimplementation of
Brogue rules in UZDoom.

## Product and technical names

- The player-facing product name is **Project Broom**.
- **Brogue CE** names the authoritative upstream game and simulation.
- **UZDoom** names the frontend engine.
- Some internal paths, APIs, classes, CVars, and test modules retain historical
  `BrogueDoom`, `Brogue`, or `brg_` names. Do not mass-rename these. Change an
  internal identifier only when the PR is specifically scoped to a safe,
  fully tested migration.

## Allowed contribution categories

Every PR must fit at least one category below.

### 1. Presentation-only work

Examples:

- original or redistributable models, textures, sprites, animations, sounds,
  music, particles, brightmaps, lighting, and visual effects;
- visual interpolation and frontend actor synchronization;
- HUD, menus, readability, accessibility, input mapping, and settings;
- performance improvements that do not alter simulation timing or outcomes;
- presentation tooling, asset validation, documentation, and tests.

Presentation code may read authoritative state. It may not create gameplay
state, block movement, deal damage, run monster AI, consume turns, select
targets, or alter Brogue RNG. Cosmetic randomness must use an isolated
presentation-only RNG stream and must never feed data back into Brogue.

### 2. Brogue parity and bridge work

Examples:

- exposing an existing Brogue command through a semantic bridge action;
- exporting additional copied state needed to present existing Brogue behavior;
- forwarding Brogue prompts, targeting, save/load, recordings, or messages;
- fixing stable-ID, event, revision, determinism, or synchronization defects;
- making UZDoom mirror an existing Brogue terrain or entity transition;
- differential, deterministic, long-run, and comparison-mode tests.

Bridge work must call Brogue's existing action and turn-processing paths. If
standalone Brogue already implements a rule, the bridge must adapt that rule;
it must not create a parallel version.

### 3. Maintenance that protects parity

Examples include build fixes, packaging, diagnostics, CI, licensing, dependency
updates, code cleanup, and documentation when they preserve the behavior and
authority boundary above.

## Contributions that will not be accepted

Do not add or change gameplay. In particular, do not add:

- new monsters, items, weapons, spells, statuses, terrain types, traps, rooms,
  levels, biomes, quests, or encounters;
- new abilities, attacks, movement rules, crafting, progression, inventory
  rules, currencies, or game modes;
- balance changes to damage, accuracy, health, nutrition, stealth, spawn rates,
  item frequency, AI, status durations, or dungeon generation;
- Doom AI, Doom combat, Doom pickups, Doom physics, or Doom RNG as substitutes
  for Brogue behavior;
- frontend collision or line-of-sight rules that determine whether a Brogue
  action succeeds;
- networking, multiplayer, or simulation-affecting asynchronous execution;
- guessed behavior intended to resemble Brogue when the real source path can
  be called;
- copied map geometry or unlicensed assets from reference WADs or other games.

Do not describe a new feature as “optional,” “quality of life,” or “disabled by
default” to bypass these constraints. If it changes an authoritative outcome,
it is outside Project Broom's scope unless that behavior already exists in the
pinned Brogue CE version and the PR is exposing it faithfully.

When uncertain whether a change affects gameplay, stop and ask a maintainer
before implementing it.

## Authority-preserving engineering rules

1. Inputs crossing the bridge represent player intent, never raw keyboard scan
   codes or a position that UZDoom has already chosen.
2. UZDoom must not move the authoritative player first. It submits an action,
   waits for Brogue, and projects the returned coordinates.
3. Brogue decides acceptance and whether time was consumed. A requested action
   is not automatically an accepted action or a consumed turn.
4. Never expose Brogue pointers or internal structure layouts in the public
   API. Use fixed-width integers, enums, copied strings, copied arrays, and
   bridge-owned records.
5. Never use pointer values as public entity IDs. Preserve a stable bridge ID
   for each creature and item throughout that entity's lifetime.
6. Keep the public contract frontend-neutral. Do not add sectors, actors,
   textures, key codes, or other Doom concepts to `BrogueBridge.h`.
7. One active Brogue session is the supported design. Do not create unsafe
   pseudo-multisession support around Brogue's globals.
8. Do not introduce gameplay threads. Correct synchronous behavior and
   determinism are more important than reducing a small bridge-call cost.
9. State revisions must never move backward. Stale snapshots must not overwrite
   newer frontend state.
10. Events are an efficient change description, not the final source of truth.
    The latest complete Brogue snapshot resolves synchronization uncertainty.
11. No frontend actor may run independent gameplay AI. Creature actors are
    visual proxies keyed by stable bridge IDs.
12. Preserve the standalone Brogue build where practical. Bridge-specific
    hooks should remain narrow and isolated.

## Repository map

Start with these locations:

- `src/brogue-mapgen/` — pinned Brogue CE source, exporter, bridge adapter, and
  headless bridge harness.
- `src/brogue-mapgen/src/brogue/BrogueBridge.h` — public copied-data contract.
- `src/brogue-mapgen/src/brogue/BrogueBridge.c` — Brogue-facing adapter,
  state extraction, stable identities, events, commands, and hashing.
- `src/gzdoom-bridge/brogue_bridge_frontend.cpp` — native UZDoom bridge
  service, input interception, state synchronization, HUD, and frontend actors.
- `mod/BrogueDoom/` — static runtime resources, ZScript, models, textures,
  effects, menus, and definitions. This historical internal path remains valid
  even though the product is Project Broom.
- `tools/mapcompiler/` — deterministic Brogue-cell to UDMF/PK3 compiler and
  verification tests.
- `assets/` — semantic material, monster, pickup, and weapon registries.
- `scripts/` — canonical Windows build, test, launch, and comparison workflows.
- `docs/brogue-gzdoom-runtime-bridge.md` — current architectural details.
- `docs/brogue-1to1-parity-todo.md` — prioritized parity backlog.
- `docs/brogue-gzdoom-comparison-mode.md` — side-by-side comparison boundary.
- `third_party/` — vendored dependencies and required attribution.
- `.deps/` and `.build/` — ignored pinned dependencies and build outputs
  prepared by `scripts/bootstrap-dev.ps1`; never commit them.
- `tooling/` — legacy local source/build/reference dependencies retained only
  in old development workspaces; it is not part of the public repository.
- `generated/`, `artifacts/`, and `crash-analysis/` — local outputs and evidence,
  not normal source contributions.

Map generation is an established subsystem. Do not rewrite it as part of an
unrelated bridge or presentation PR. Preserve Brogue coordinates, connectivity,
stairs, semantic metadata, and every `user_brogue_*` UDMF field.

## Required workflow for coding agents

### Before editing

1. Read this file completely.
2. Read the relevant architecture document and the parity TODO.
3. Inspect the current worktree and preserve unrelated tracked and untracked
   changes. Never reset, clean, or replace another contributor's work.
4. Identify the contribution category from the allowed list above.
5. For bridge work, trace the actual standalone Brogue call chain before
   selecting an entry point. Useful starting files include `RogueMain.c`,
   `IO.c`, `Movement.c`, `Time.c`, `Monsters.c`, `Combat.c`, `Items.c`, and
   `Recordings.c`.
6. Write down the expected Brogue behavior and how it will be proven before
   changing code.

### While editing

- Keep changes narrow and avoid opportunistic rewrites.
- Prefer an adapter around existing Brogue functions over changes to Brogue
  rules or structures.
- If the public bridge ABI changes, increment
  `BROGUE_BRIDGE_API_VERSION`, update both consumers, and add ABI-sensitive
  tests.
- Keep all generated output deterministic. Sort by stable IDs or coordinates;
  never hash addresses or container iteration order.
- Preserve exact Brogue text when a user-facing message, prompt, or item detail
  already exists in Brogue.
- Keep presentation actors non-blocking and non-damaging unless their collision
  is merely mirroring an authoritative Brogue cell, and then derive it only
  from the returned cell state.
- Update relevant documentation and tests in the same PR.

### Before claiming completion

Treat these as separate gates:

1. source compilation;
2. unit/regression tests;
3. deterministic bridge or map verification;
4. packaging;
5. an actual UZDoom launch;
6. interactive or captured runtime evidence for visual changes;
7. standalone/side-by-side comparison when gameplay parity is involved.

A passing compiler is not runtime proof. A screenshot is not gameplay-parity
proof. Report any gate that was not run and why.

## Canonical Windows commands

Run commands from the repository root using Windows PowerShell. `pwsh` is not
required.

Build the Brogue bridge and harness:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-bridge.ps1
```

Run the primary bridge, resource, and map-compiler suites:

```powershell
python -m unittest tools.test_brogue_bridge tools.test_broguedoom_resources tools.mapcompiler.test_compile
```

Run a deterministic command sequence:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-bridge-test.ps1 -Seed 1 -Actions "WAIT,N,E,SE,WAIT,W"
```

Run a long bridge simulation:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-bridge-test.ps1 -Seed 1 -LongRun 300 -VerboseOutput
```

Build the complete source bridge and modified UZDoom frontend:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-source-bridge.ps1
```

Launch a reproducible development game:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\launch-source-bridge.ps1 -Seed 1
```

Launch the player-facing executable with a reproducible seed:

```powershell
.\ProjectBroom.exe --seed 1
```

Launch the pinned standalone Brogue and Project Broom side by side:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\launch-comparison.ps1 -Seed 1
```

Some complete builds require the repository's configured MinGW, Python,
CMake, Visual Studio/MSBuild, and .NET toolchains. If a dependency is missing,
report the exact missing program and the tests that could still be run; do not
replace the build system in an unrelated PR.

## Verification expectations by contribution type

### Presentation-only PR

- Run `tools.test_broguedoom_resources` and relevant generator tests.
- Verify generated assets are deterministic when a generator is involved.
- Launch at least one fixed seed and inspect the result in UZDoom.
- Provide before/after captures for visible changes.
- Confirm that the effect has no collision, damage, AI, turn, or gameplay-RNG
  behavior.
- For performance-sensitive effects, compare frame timing or frame rate in the
  same fixed scene and graphics settings.

### Bridge/API PR

- Add a deterministic headless regression test for accepted, rejected,
  cancelled, and turn-consuming behavior as applicable.
- Run the complete Python suite and a several-hundred-action long run.
- Test at least five seeds when behavior depends on generated terrain or
  creatures.
- Prove that repeated `seed + action sequence` runs produce identical normalized
  state hashes.
- Exercise the feature through UZDoom, not only the bridge executable.
- Compare against standalone Brogue or its recording path when practical.
- Document the exact Brogue functions called and why they preserve parity.

### Map or terrain-presentation PR

- Require byte-identical output for identical seed/depth inputs.
- Run map compiler and verifier tests.
- Prove cardinal connectivity, diagonals, stairs, doors, bridges, and semantic
  counts are unchanged unless fixing a demonstrated projection defect.
- Check for missing textures, invalid sidedefs, open sectors, duplicate lines,
  corner squeezes, and stale runtime proxies.
- Compare a fixed top-down view with Brogue's authoritative map.

### Sound or third-party asset PR

- Confirm every file's source, author, and redistribution license.
- Preserve required readmes, licenses, notices, and credits.
- Do not vendor an entire WAD or asset pack when only separately licensed
  resources are allowed.
- Sound selection and pitch variation must remain cosmetic and must not affect
  Brogue RNG or action timing.

## Asset and licensing policy

- Prefer original Project Broom assets or assets with explicit redistribution
  terms compatible with the repository and intended release.
- Never assume that a downloadable asset is redistributable.
- Record provenance and license details for every imported resource.
- Do not remove or rewrite upstream copyright, license, or attribution files.
- Inspection-only reference maps and WADs may be studied but must not be copied
  into generated maps or release packages.
- Do not commit build products, caches, generated campaigns, crash dumps, or
  downloaded reference archives unless a maintainer explicitly requests a
  release or evidence artifact.

## Pull request requirements

Every PR description should include:

1. **Contribution category:** presentation, bridge parity, or maintenance.
2. **Problem:** the specific visual defect, missing Brogue behavior, bridge
   limitation, or maintenance issue being addressed.
3. **Authority analysis:** which side owns the behavior and, for bridge work,
   the exact existing Brogue entry points used.
4. **Scope:** the important files and contracts changed.
5. **Gameplay declaration:** explicitly state whether gameplay outcomes can
   change. Accepted contributions should normally say “No; Brogue CE remains
   authoritative.”
6. **Verification:** exact commands, seeds, action sequences, hashes, and
   runtime checks performed.
7. **Visual evidence:** before/after captures for visible work.
8. **Licensing:** provenance and redistribution terms for every new asset.
9. **Known limitations:** anything intentionally left incomplete.

Keep one PR focused on one coherent problem. Do not bundle new assets, bridge
ABI work, map-compiler changes, and broad refactors without a demonstrated need.

## Review rejection checklist

A maintainer or reviewing agent should request changes if any answer is “yes”:

- Does UZDoom decide whether a gameplay action succeeds?
- Does the PR duplicate a Brogue rule?
- Does it add content or alter balance rather than expose existing Brogue CE
  behavior?
- Does it use Doom AI, damage, collision, or RNG as gameplay authority?
- Does a public contract expose a Brogue pointer or internal structure layout?
- Can cosmetic frame rate, camera motion, or visual RNG change Brogue state?
- Are stable IDs replaced by pointers, array positions, or transient actor IDs?
- Does deterministic output depend on unordered iteration?
- Are generated/reference/binary files included without justification?
- Are asset provenance or redistribution rights missing?
- Are build-only results presented as runtime or parity proof?
- Were unrelated contributor changes overwritten or removed?

## Definition of a good contribution

A good Project Broom contribution makes Brogue CE easier to see, hear,
control, verify, or faithfully expose. It leaves the answer to “what happened?”
entirely with Brogue and improves only how faithfully UZDoom communicates that
answer to the player.
