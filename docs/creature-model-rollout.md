# Creature model rollout and verification

## Delivered scope

Presentation-only, 2026-09-04. The [work index](creature-model-index.md) covers
all 68 pinned Brogue catalog kinds: player reference 0, the existing rat 1, and
66 new static creature/construct/associated-form replacements 2–67. Legendary
allies, summoned weapons, eggs and totems are indexed too; this does not add
new enemies or change their spawning. The rat and held-weapon work are preserved.

Each new kind has an original triangulated OBJ, a 1024-square diffuse PNG,
named anatomical parts, a self-contained editable Blender source and an
individual Markdown work card. There are 519,616 triangles across the 66 new
models; the largest individual model has 19,032. This is a first static-art
pass, not 66 individually approved final sculpts or skeletal animations.

The exact pinned `monsterText`, catalog flags, colors and encounter-table rows
are indexed with source references. Numerical sizes are explicitly **artistic
interpretations**, because Brogue supplies no physical measurements. Scale is
calibrated against a 64-map-unit cell, a roughly 58-unit humanoid and the
existing 15-unit-tall rat. HP is never a size formula. Full silhouette extents,
including tails/equipment, are tested; flight clearance is recorded separately.

## Authority and provenance

No bridge ABI, native frontend code, Brogue rules, damage, collision, AI, turn
processing, RNG, spawning or map-generation rules were changed. Runtime
classes/IDs and non-interacting proxy flags are preserved. Brogue remains
authoritative. Static poses keep existing whole-proxy presentation transforms.

Meshes and skins are original Project Broom procedural artwork under the
existing [asset license](../ASSETS-LICENSE.md), CC-BY-SA-4.0. No third-party
models/images or reference-WAD art were imported. Brogue text retains its
upstream attribution and licensing. Current Blender API documentation fetched
through Context7 informed mesh/UV/source-file construction; Blender 5.2.1 LTS
was verified locally. The live Blender MCP scene was inspected read-only and
preserved; source generation used an isolated background Blender process.

## Verification gates

| Gate | Actual evidence |
| --- | --- |
| Native compilation | Not rerun; no native source changes. Used the existing canonical GZDoom 4.14.2-m executable. |
| Tests | 90 tests passed: bridge, resources, rat, all-creature geometry/source/scale, verification staleness, held weapons and map compiler. |
| Determinism | All 66 OBJ files matched regeneration byte-for-byte and recorded hashes; representative atlas regeneration matched exactly. Full gallery package bytes were checked against source assets; a second complete package build was byte-identical. Rat OBJ/skin hashes match the preserved baseline. |
| Blender sources | All 66 files freshly reopened: matching mesh bounds, expected named part counts, UVs, one packed image, no linked libraries. |
| Packaging | `artifacts/creature-models/ProjectBroom-creatures.pk3` contains matching runtime OBJs/skins, not Blender sources or review geometry. This is a verified static-mod package, not a rebuilt release installer. |
| Actual engine | All 67 non-player models spawned and were captured in sequential before/after GZDoom galleries; ordered logs were checked, not just screenshot file counts. |
| Visual review | All six after-gallery contact sheets and studio sheets reviewed; fixed scale grid and height reference. These establish loading/silhouettes, not final art approval. |
| Natural floor-one encounter | Seed 1, turn 38: new kobold at cell 13,23, player 12,22. Actual Brogue combat/visibility, real player eye; capture inspected. The diagnostic camera hides only the player reference model to avoid viewing it from inside. |
| Every natural encounter / side-by-side parity | Not run. No claim of all-depth, all-species encounter acceptance or new gameplay parity proof. |
| Performance | Geometry budgets checked; no controlled FPS benchmark performed. |

The isolated `ART01` review room is not a Brogue level. Its temporary actors,
camera and reference grid exist only in ignored evidence resources. It does
not run Brogue commands, alter Brogue visibility or replace real encounters.
Runtime contact sheets use a consistent central crop; full screenshots are
retained separately. Studio lighting is not representative of GZDoom lighting.

The ordinary encounter used `brg_monster_omniscience false` and the Brogue
action sequence `N N N`, 25 `W`, `N W`, then 8 `WAIT` actions. Brogue moved the
kobold around the corner itself; the test did not teleport/reveal any creature.
See [normal encounter capture](../artifacts/creature-models/normal-visible-kobold.png)
and `artifacts/creature-models/normal.log`. This proves one kobold encounter,
not the rest of the roster. The rat remained present and unchanged.

Existing minimap signedness/menu and gallery-only `BRGBRIDGE` texture warnings
were observed; no missing new creature model/skin was reported. An initial
diagnostic camera attempt failed to compile, was corrected, and is not counted
as successful evidence. Failed test sessions were closed; live Blender work
was not closed or reset.

## Reproduce and inspect

From the repository root:

```powershell
python -m tools.monster_models.creatures
python -m tools.monster_models.generate
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools\monster_models\blender_creatures.py -- --render
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools\monster_models\verify_blender_creatures.py
python -m unittest tools.test_brogue_bridge tools.test_broguedoom_resources tools.monster_models.test_rat tools.monster_models.test_creatures tools.weapon_models.test_viewmodel tools.mapcompiler.test_compile
```

For one work item, pass `--kind 2` to the creature generator and `-- --kind 2
--render` after Blender's script argument. The procedural definitions are the
reproducible master; reconcile any manual Blender edits before regeneration.

Local evidence (ignored, not release content):

- `artifacts/creature-models/after/`: studio render per kind.
- `artifacts/creature-models/runtime-before/` and `runtime-after/`: 67 full-frame captures each.
- `artifacts/creature-models/runtime-after-sheet-1.png` through `-6.png`: indexed engine review sheets.
- `artifacts/creature-models/blender-reopen-verification.json`: fresh-open source checks.
- `artifacts/creature-models/review-verification.json`: package hash and coverage.
- `artifacts/creature-models/runtime-before.log` and `runtime-after.log`: ordered spawn/capture evidence.

The reusable `tools.monster_models.review` module prepares gallery resources
and sheets. Before captures require the preserved local `baseline/` assets.
The local `run-gallery.ps1 -Phase runtime-before` / `runtime-after` scripts run
the engine; their short console aliases capture each model then exit.
`python -m tools.monster_models.record_review` verifies ordered logs, source
package bytes and Blender reopen checks, then records evidence against asset
hashes in the JSON index. Regeneration preserves verification but marks it
stale if an asset hash changes.

After visually inspecting the fixed-seed kobold capture, pass
`--include-kobold-encounter` to `record_review` to record that narrower gate.

Verified static package SHA-256:
`67c1b14339141380be53f9e4ef22354b8731469afc9710f1fbb7aa2ac7179780`.

## Next per-creature acceptance work

Use each indexed work card, not an untracked mental list:

1. Approve its anatomy, signature Brogue features, silhouette and scale.
2. Inspect at ordinary gameplay distance, in a real encounter and corridor.
   Aquatic immersion and wall-mounted turret placement especially need this.
3. Improve material/readability where needed: the current GZDoom ambient
   lighting produces substantially flatter shading than the Blender previews.
   Mirrored facets are diffuse approximations, not real-time reflections;
   the phoenix egg is not physically transparent glass.
4. Add gait/attack/death deformation only through presentation of resolved
   Brogue events. Current meshes have no skeletal animation or mutation skins.
5. Record approval and its asset hashes under that kind's `verification` object.

The player reference remains a placeholder intentionally. Individual art
approval, full turnarounds, all-depth encounters and animation gates remain open.
