# Project Broom

> Brogue CE is the game. UZDoom is the 3D frontend.

[![License: AGPL v3+](https://img.shields.io/badge/code-AGPL--3.0%2B-blue.svg)](LICENSE)
[![Assets: CC BY-SA 4.0](https://img.shields.io/badge/assets-CC%20BY--SA%204.0-green.svg)](ASSETS-LICENSE.md)

Project Broom runs a live, authoritative Brogue CE simulation and presents it
through a modified UZDoom frontend. UZDoom translates input into semantic
actions, Brogue resolves those actions and advances the turn, and UZDoom then
renders the copied result.

```text
player input -> UZDoom -> bridge action -> Brogue CE
                                            |
                       presentation <- copied state and events
```

The governing rule is simple: **UZDoom asks Brogue what happens; it never
decides what happens.**

Project Broom is pre-alpha. It is already playable, but it is not yet a
complete 1:1 presentation of every Brogue command and screen.

## What Project Broom is

- A 3D frontend for Brogue CE's real dungeon generation, RNG, movement,
  monsters, combat, items, terrain, statuses, messages, and turn system.
- A narrow copied-data bridge between Brogue C code and UZDoom C++.
- A deterministic Brogue-cell to UZDoom-map projection.
- A presentation project where models, textures, particles, lighting, sound,
  HUD, menus, and accessibility can improve without changing gameplay.

## What it is not

- It is not a Brogue-inspired Doom mod.
- It does not reimplement Brogue's rules in ZScript or Doom actors.
- It does not use Doom monster AI, damage, physics, pickups, or RNG as gameplay
  authority.
- It is not a balance mod and does not accept new monsters, items, spells,
  terrain, levels, quests, or other gameplay additions.
- It is not multiplayer or networked.

## Current status

Implemented today:

- authoritative seeded Brogue game and 40-depth dungeon generation;
- eight-way movement and wait, including blocked and diagonal behavior;
- Brogue-owned melee combat, monster turns, environmental turns, doors, HP,
  messages, chasms, warnings, and level transitions;
- copied player, creature, item, terrain, message, inventory, and game-result
  state with stable runtime IDs;
- equipping/removing, dropping, throwing, targeted staffs and wands, food, potions, scrolls, charms, and
  Brogue-owned confirmation/item-selection prompts;
- bridge-backed look mode, inventory, weapon presentation, ASCII minimap,
  game-over state, and side-by-side comparison tooling;
- deterministic map packages, original cave materials, animated liquids,
  bridges, doors, ladders, foliage, pickups, monsters, and held weapons;
- scripted bridge tests, normalized state hashes, and long-run simulations.

Important parity work still remaining:

- a generalized targeting contract;
- search, auto-rest, auto-explore, travel, and run-until-disturbed commands;
- broader save/load acceptance and Brogue recording playback;
- complete dynamic terrain synchronization, visibility behavior, status
  details, special-monster effects, and remaining Brogue information screens;
- broader turn-by-turn comparison against standalone Brogue.

The maintained checklist is [docs/brogue-1to1-parity-todo.md](docs/brogue-1to1-parity-todo.md).

## Download and play

The first supported release platform is **Windows x64**.

1. Download `ProjectBroom-Windows-x64-<version>.zip` from GitHub Releases.
2. Extract the complete archive to a normal writable folder.
3. Run `ProjectBroom.exe`.
4. Choose **Continue**, **Load / Import**, **New Game**, or **New Game with
   Seed**. A normal new game chooses a positive random Brogue seed; the seeded
   option lets you enter a specific positive seed to replay. Project Broom then
   generates the authoritative dungeon, prepares and verifies the first floor,
   and starts UZDoom.

The portable release includes the required Brogue CE simulation, modified
UZDoom runtime, Freedoom Phase 2 IWAD, Project Broom presentation package, and
map compiler. You do not need to install any of those separately.

Later floors are prepared from Brogue's current state when you enter them.
New seeds take longer on their first launch. Generated campaigns, settings,
logs, working recordings, and native saves live under `%LOCALAPPDATA%\ProjectBroom`; the
installation folder remains read-only. Run `ProjectBroom.exe --seed 1` for a
repeatable development game or `ProjectBroom.exe --clear-cache` to remove
regenerable campaign data. Saves remain intact.

Use **Saves > Save and Exit** in the game menu to suspend a run. Normal window
close also saves a live run. A successful resume consumes the managed save;
importing a `.broguesave` preserves the original file. Both paths use Brogue's
native recording format. See [save/load evidence and remaining gates](docs/save-and-load.md).

Pre-alpha releases are unsigned and may trigger Windows SmartScreen. Verify
the download against the release's `SHA256SUMS.txt` before running it.

## Default controls

| Key | Action |
| --- | --- |
| Movement keys / configured directions | Submit movement in the direction faced |
| Space | Wait one Brogue action |
| `L` | Look at authoritative terrain, items, and monsters |
| `I` | Inventory |
| `Q` | Weapons/equipment view |
| `T` | Throw using Brogue targeting |
| Escape | Pause/menu or cancel the current frontend interaction |

Input bindings and video/presentation settings can be changed in UZDoom's
options. Changing presentation settings does not change the Brogue simulation.

## Build from source

The supported contributor environment is Windows 10/11 x64 with Git, Python
3.11, .NET 8 SDK, CMake, Visual Studio 2022 C++ Build Tools, and an MSYS2
MinGW-w64 make/GCC toolchain.

```powershell
git clone <repository-url>
cd ProjectBroom
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-dev.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build-dev.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\run-dev.ps1 -Seed 1
```

The bootstrap downloads exact pinned dependencies into ignored `.deps/` and
verifies their revisions and hashes. It never downloads the CC4 or Sunlust map
WADs. See [docs/building.md](docs/building.md) for prerequisites,
troubleshooting, comparison mode, and package creation.

## Architecture and source map

- `src/brogue-mapgen/` contains the pinned Brogue CE snapshot and bridge.
- `src/gzdoom-bridge/` contains the Project Broom UZDoom integration.
- `mod/BrogueDoom/` contains runtime presentation resources. The historical
  internal name remains intentionally stable.
- `tools/mapcompiler/` projects authoritative Brogue cells into UDMF/PK3.
- `assets/` contains semantic material, monster, pickup, and weapon registries.
- `scripts/` contains canonical Windows setup, build, test, run, and packaging
  entry points.

Start with [AGENTS.md](AGENTS.md), even when contributing manually. It explains
the authority boundary, accepted contribution types, exact verification gates,
and the rules coding agents must follow. Detailed bridge architecture is in
[docs/brogue-gzdoom-runtime-bridge.md](docs/brogue-gzdoom-runtime-bridge.md).

## Contributing

Pull requests are welcome for:

- presentation-only models, textures, sprites, sound, lighting, particles,
  UI, accessibility, input, and performance work;
- faithful bridge exposure of behavior that already exists in Brogue CE;
- tests, diagnostics, build/packaging maintenance, and documentation that
  protects parity.

Gameplay additions and parallel Doom-side rules are not accepted. Read
[CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) before opening a
pull request. New assets must include author, source, license, and redistribution
provenance.

## Reporting problems

Use the matching GitHub issue form and include the Project Broom version, seed,
depth, action sequence, expected Brogue behavior, and diagnostic bundle when
available. Do not upload enormous generated dungeon JSON files unless a
maintainer requests them.

Security issues should follow [SECURITY.md](SECURITY.md), not a public issue.

## Licensing and acknowledgements

Project Broom original code is AGPL-3.0-or-later. Original Project Broom assets
are CC BY-SA 4.0. Brogue CE, UZDoom, Freedoom, UltimateClassicMinimap, and
other third-party components retain their own licenses and copyright notices.
See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Project Broom is unofficial and is not endorsed by the Brogue CE, UZDoom,
Doom, or Freedoom authors.
