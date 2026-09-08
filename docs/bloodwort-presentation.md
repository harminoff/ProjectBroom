# Bloodwort presentation and verification

Status: implemented with automated native, renderer and package evidence.
**Physical-input standalone comparison remains unverified.** This does not close
the wider dynamic-terrain backlog. Contribution categories: presentation and
parity verification. Brogue CE remains authoritative; no gameplay rules, public
ABI v20, save format or map format changed. The existing dirty workspace was
preserved.

## Native behavior and proof

The pinned catalog in `Globals.c` defines a blocking, flammable stalk, a blocking
pod that promotes on player entry, and dark-red `HEALING_CLOUD`. The expected
interaction is a turn-consuming bump that leaves the player in place, followed
by entry on a later move. `Movement.c::playerMoves()` emits the catalog's exact
pod text, calls `promoteTile()`, calls `playerTurnEnded()` and returns before
moving the player. No frontend implementation of that rule was added.

`Time.c::updateEnvironment()` schedules stalk promotions using the native RNG.
`promoteTile()` calls `spawnDungeonFeature()` with the catalog's pod-growth or
burst feature. `exposeTileToFire()` selects the existing fire promotion, while
`updateVolumetricMedia()` spreads/dissipates gas. The scheduler reaches
`applyGradualTileEffectsToCreature()`: eligible creatures heal; inanimate and
submerged creatures are excluded. All synthetic setup lives in
`tools/bridge-bloodwort-smoke.h` under the native harness directory.

`python -m unittest tools.test_bloodwort` repeats seeds 1, 2, 42, 12345 and 99999
twice. Each run compares native `executeKeystroke()` against bridge dispatch:

| Scenario | Assertions |
|---|---|
| 0: stalk bump | Rejected, no turn, unchanged coordinates |
| 1: pod bump then entry | Accepted, one turn each; first remains in place, second enters |
| 2: fire | Native `exposeTileToFire(..., true)` bursts the pod and creates healing gas |
| 3: controlled lifecycle | 300 completed actions, repeated pod bumps, native stalk regrowth and cloud spread |
| 4: healing | Injured eligible player gains HP |
| 5: inanimate | No spore healing |
| 6: submerged | No spore healing |

Every step compares normalized bridge state hashes, copied message bytes and a
subsequent substantive RNG sample. Acceptance/turn flags and positions are
checked directly where applicable. The controlled fixture removes monsters,
sets health/nutrition and prepares pods every 30 actions; eight native stalks
grow independently. It is not a natural survival run. Gas diffusion and removal
are exercised through native environment ticks; a dedicated assertion advances
the native environment until no healing cloud remains (13 ticks for seed 1).

Logs: `artifacts/bloodwort/native-{seed}.log` and
`bloodwort-tests-final.log`. Seed 1's controlled 300-action terminal hash is
`d6d6e71c54260cc0`, subsequent RNG sample 28922. The canonical natural 300-action
request ends at turn 195, killed by a rat, hash `36b2a00b6543c40a`; it is recorded
separately and is not counted as completed endurance.

## Original assets and ownership

`tools/bloodwort_models.py` deterministically creates four OBJ/PNG pairs:
`bloodwort_stalk`, `bloodwort_pod`, `bloodwort_shell`, `bloodwort_spores` and
BRGBWST/BRGBWPD/BRGBWSH/BRGBWSP. All are original procedural Project Broom work,
dedicated under [CC0-1.0](../assets/terrain/ANIMATION-LICENSE.md#bloodwort).
There are no downloaded meshes or textures. Regenerate with:

```powershell
python -m tools.terrain_assets
python -m tools.terrain_presentation
python -m unittest tools.test_bloodwort tools.test_terrain_sync tools.test_terrain_animation
```

Tests check identical bytes, nondegenerate triangle/quad faces and cell-bounded
plant geometry. Model definitions use scale 1. The stalk is 65 units tall and
the pointed pod 45; source coordinates convert through the existing OBJ axis
convention. Full SHA256 values are in `artifacts/bloodwort/asset-hashes.json`.
Registry and inherited actor definitions bind the models to noninteractive,
nonblocking, gravity-free presentation actors.

`BloodwortTile()` resolves both surface and remembered structural identity.
Exactly one vegetation owner presents the plant; the mechanism owner is
suppressed for bloodwort, preventing door-panel transitions. Unknown cells
have no plant. Memory uses only Brogue's copied appearance, with no unseen
growth, burst or cloud effects.

Observed consecutive snapshots grow a new pod over 21 tics. An observed pod
removal followed by healing gas emits shell fragments; copied fire/removal
states take precedence. Missing events do not prevent reconciliation. Skipped
revisions settle the plant without inventing intermediate growth/bursts;
duplicate and stale snapshots are inert. Interrupted appearance updates keep
the current growth pose. Visibility loss, replacement, new-session binding and
teardown remove transients.

The existing gas owner uses copied identity, volume and RGB, with 12-tic
density/color transitions. Healing clouds use bounded spore geometry and faint
cloud lobes, with analytical drift that does not accumulate velocity or use RNG.
Basic settles immediately and retains readable plants/clouds. Enhanced emits
six shell fragments and Cinematic twelve, within the existing global 256-owner
fragment cap. No animation enters native save data or delays action dispatch.

## Renderer evidence

```powershell
python -m tools.test_terrain_renderer --backend 0 --bloodwort --quality 0
python -m tools.test_terrain_renderer --backend 1 --bloodwort --quality 2
```

Repeat each backend for quality 0, 1 and 2. All six runs passed, producing 198
before/during/after captures across eleven stages (37–47) in
`artifacts/bloodwort/{opengl,vulkan}/{0,1,2}/populated`. These are explicit synthetic
copied-snapshot renderer probes, not native gameplay fixtures. They leave Brogue
at turn 0, hash `c92268ff6250781b`.

The stages cover stalk, pod growth, repeated burst, interrupted growth,
visibility loss into remembered identity, unknown cells, skipped/stale/duplicate
revisions, absent events, thinning gas and gas replacement/removal. Assertions
check one plant owner, selected identity, gas cleanup, no outgoing panel and
no surviving fragments. The populated harness also checks immediate player, item and creature actor
positions against copied coordinates and settled support after every snapshot.
It projects one copied item and creature beside the plant without mutating
Brogue, and requires nonempty item/creature evidence.

Representative captures:

- [Stalk](../artifacts/bloodwort/opengl/1/populated/animation-37-after.png)
- [Pod](../artifacts/bloodwort/opengl/1/populated/animation-38-after.png)
- [Burst](../artifacts/bloodwort/opengl/1/populated/animation-39-during.png)
- [Healing spores](../artifacts/bloodwort/opengl/1/populated/animation-39-after.png)
- [Restored real game](../artifacts/bloodwort/packaged/1/bloodwort-restored.png)

Screenshot-free runs use `--bloodwort --benchmark --run-label final-isolated`; their
raw timings are in `artifacts/bloodwort/timings.json`. They hold the same healing
cloud scene for six seconds. These are frame-hook wall-clock samples, not GPU
timestamp measurements or a supported-hardware budget. The final runs are
sequential, without concurrent builds, tests, other test engines or screenshot
capture. Full mean, p95, maximum and sample counts are retained in the JSON;
compare the same `dense_frame` interval across all six runs.

## Real route, persistence and package

The seed-one export was revalidated: stalk `(64,24)`, pods `(64,23)` and
`(65,24)`. From start `(38,26)`, use `N`, 27 `E`, `N`, `N`, `WAIT`. At turn 28
the player is `(65,25)`; the bump consumes turn 29 without moving; turn 30 enters
`(65,24)`. Turn 31 has hash `7ccc0e59f870c1e4` in the headless command trace.
See `artifacts/bloodwort/real-route-headless.log`.

```powershell
python -m tools.verify_bloodwort_save
python -m tools.verify_bloodwort_package --backend 0
python -m tools.verify_bloodwort_package --backend 1
```

The save tool uses only native gameplay commands on the real generated map.
It saves at turn 31, replays the native recording, compares every cell's layers
and gas volume, and continues with WAIT to turn 32. It then travels normally to
depth 2 at turn 61 and revisits depth 1 at turn 62, verifying the stalk survives.
Exports and saves are under `artifacts/bloodwort/save`. The package runner also accepts `--depth-return`: it loads the real depth-2
save at turn 61, submits the single move onto its up stairs, captures depth 1 at
turn 62, waits and saves at turn 63. Both renderer logs are under the respective
`packaged/{0,1}-revisit` directories.

Local validation package version: `0.1.0-bloodwort-validation`, under
`artifacts/release/0.1.0-bloodwort-validation`. Archive hashes and all manifest
entries pass `scripts/verify-release.ps1`. The package runner extracts the ZIP,
uses its launcher save probe, frozen compiler, engine, bridge and static mod,
and supplies the existing seed-one campaign as regenerable level data. Both
OpenGL and Vulkan restore turn 31, accept WAIT and save at turn 32. Restored
hash `de9b6a073ba89c7c` and continuation `a462cb0d7dd9fc31` agree between
renderers. Raw pre-save/restored hash identity is not claimed. Source saves are
copied before the frontend consumes its load input.

Canonical reproduction commands:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-source-bridge.ps1 -SkipTests
powershell -ExecutionPolicy Bypass -File scripts/test.ps1
powershell -ExecutionPolicy Bypass -File scripts/package-release.ps1 -Version 0.1.0-bloodwort-validation -SkipBuild
powershell -ExecutionPolicy Bypass -File scripts/verify-release.ps1 -ReleaseDirectory artifacts/release/0.1.0-bloodwort-validation
```

`artifacts/bloodwort/complete-tests-final.log` records the canonical test script
passing 168 tests. Native and engine compilation, launcher build, renderer
launch, archive verification and extracted runtime launch are separate evidence
gates. Earlier `build.log` is a NuGet access failure; `final-build.log` records
a link attempt while a renderer still held the executable. Neither is final
build-success evidence. The later engine relink and canonical build logs record
the corrected sequence. The final populated probe compilation is recorded in
`placement-engine-build-final.log`; it normalizes the child PATH spelling and
disables MSBuild node reuse after an environment-key collision. The final native
harness build is `bridge-build-final.log`.

## Remaining acceptance

Physical-input comparison was attempted with the pinned standalone and engine.
The launch script returned both process IDs, but the computer-use service did
not list either test window; its launch/retry returned:
`launched app did not expose a targetable window`. The user-owned Brogue window
was not used. No physical movement/wait or standalone visual comparison is
claimed. Retry `scripts/launch-comparison.ps1 -Seed 1` with a working window
control connection, then use the route above (comparison numpad controls).

The outstanding physical-input and standalone visual comparison keeps the
requested full acceptance gate open despite the implemented assets and
automated checks.
