# Generalized targeting preview (API v16)

Contribution category: bridge parity. Gameplay declaration: Brogue CE remains
authoritative; no new gameplay, commands, assets, or bolt animations.

## Contract

`brogue_bridge_preview_target(request, result)` accepts API version 16,
`expectedRevision` (zero means current), `THROW_ITEM`, `USE_STAFF`, or `USE_WAND`,
a carried stable item ID, and Brogue target coordinates. Wrong versions,
unsupported commands, wrong device categories, missing/non-carried items,
stale revisions, and inactive/ended sessions fail without executing anything.
The native frontend always supplies its displayed revision.

The copied result includes the echoed request, revision, depth, player origin,
structural cell validity, ordered guide cells, selected-cell reach, optional
maximum range (`hasRange`, with legacy `maxDistance = -1` when absent), guide
termination, eligible creature IDs/coordinates, the next cycling target,
confirmation requirement, certain-death refusal, and Brogue's warning text.

Structural validity means an in-map cell other than the player. Automatic
eligibility, manual aiming, guide reach, and execution acceptance are distinct.
An excluded reflector can still be manually aimed at. A guide stopped by terrain
is not an execution rejection. No impacts, reflections, hidden effects, or
charge depletion are predicted.

Termination is selected cell, range, map edge, unexplored area, terrain, or
creature. Devices can continue beyond the selected cell; `reachesTarget` is
independent of the final termination reason. The first unexplored cell is not
included in the reachable guide, matching Brogue's terminal cursor emphasis.

Arrays retain the 1024-creature and 128-path-cell capacities, copied counts,
and explicit truncation flags. Results are zero-initialized. Creature identity
lookup never allocates or marks an identity seen; a missing identity is omitted
and reported through target truncation. The request and result ABI sizes are
asserted at compile time in both consumers (32 and 17760 bytes).

All three old functions remain deprecated wrappers. The DLL export, native
loader, harness, monster catalog, and registry use v16 together. A v15 DLL
lacks the required new export; version checks also reject mixed components.

## Brogue implementation and UI

`Items.c::collectTargetCreatures()` calls `canAutoTargetMonster()` without
refreshing the sidebar. It orders direct vision before sensing, then squared
proximity, then x/y coordinates, with no duplicate cell or terminal row limit.
Standalone sidebar behavior is unchanged.

`calculateTrajectory()` supplies both `hiliteTrajectory()` (used by
`chooseTarget()`) and `previewItemTarget()` / `previewDeviceTarget()`. Drawing
is separate. Throws and unknown devices begin with `BOLT_NONE`; known devices
use only the definition Brogue permits. Throw range, known blinking range,
tunneling, fiery terrain, and pass-through rules remain Brogue's own.

`blinkingHazard()` is pure and shared with execution. It preserves
“that would be certain death!” and “Blink across lava with unknown range?”.
Only execution prints or requests approval. `itemThrowConfirmationPrompt()`
formats the exact standalone throw prompt from an item value copy, without
changing inventory quantity or inspecting hidden curse state.

Execution remains `throwItemAtTarget()` or `applyDeviceAtTarget()` ->
`useStaffOrWand()` -> existing effect/turn processing. Preview never calls
`zap()`, submits a command, refreshes the sidebar, changes targeting history,
or consumes RNG/turns/revisions.

UZDoom retains the five-cell camera-facing initial cursor, movement, Tab,
confirm/cancel controls, display location, held-device models, and noninteracting
markers. All three actions use shared cycling and copied guides. Text reports
range/obstruction/unexplored continuation; warnings use the existing wrapped
midprint and confirmation display. All submissions start with `confirmed = 0`.
The existing approval overlay retries the same item, target, and revision.
Targeting/approvals are cleared on cancellation, item loss, reset, or depth
change, and displayed guides refresh when the state revision changes.

## Automated evidence (2026-09-05)

- Canonical bridge and source frontend/exporter builds succeeded. Launcher
  restore required network access; the successful canonical retry is recorded
  in `artifacts/target-source-build-release.log`.
- `powershell -ExecutionPolicy Bypass -File scripts/test.ps1`: 106 main tests
  and 6 engine-source tests passed (`artifacts/target-tests-final.log`).
- `--target-smoke`: 21 preview fixtures plus 8 staff/throw standalone-input
  differential cases, repeated on seeds 1, 2, 42, 12345, 99999. Existing wand
  differential tests remain in the full suite. Preview cases compare repeated
  zero-filled output, inventory and targeting state, both RNG continuations,
  and an identical WAIT continuation. Capacity clipping is exercised on the
  collector with a one-entry destination; normal public bounds are asserted.
- Fixtures cover open/obstructed throws, throw range, unknown staff/wand,
  blinking warning/refusal, tunneling, fiery terrain, pass-through, manual
  reflectors, hidden/submerged/telepathic/hallucinated creatures, hostile-device
  ally exclusion, healing ally inclusion/self exclusion, zero/one/multiple candidates, duplicates, and an empty sidebar.
- Standalone differential routes call real `apply()` or `throwCommand()` with
  terminal target/cancel input; command routes test approval and rejection.
  The same WAIT follows both, comparing hashes, turns, and substantive RNG use.
- The canonical `WAIT,N,E,SE,WAIT,W` and `-LongRun 300` commands were each
  repeated twice on all five seeds with byte-identical output. Long runs end
  at natural Brogue deaths, not 300 surviving actions.

| Seed | Six-action state hash | Long-run final hash | Final turn |
|---|---|---|---:|
| 1 | 88d61247fcf73d76 | 605cf66657aa5f8e | 195 |
| 2 | 44446bcb3332d995 | 4b8100449d7d2a85 | 43 |
| 42 | 30bf48bdc0c2d672 | 8d13a463dae3e192 | 72 |
| 12345 | 85d551f12cd43aa8 | 93b34275cf604e88 | 145 |
| 99999 | a7686a9591f6421c | 5c7264608578c3cc | 109 |

Runtime smoke uses naturally carried staff seed 14, wand seed 19, and starting
weapon seed 1. `scripts/test-staff-ui.ps1` now accepts `-Throw` and retains
separate evidence directories for each renderer and HUD scale. Vulkan/OpenGL
at HUD scales 1–3 passed for all three actions (18 runs). Captures and logs are
under `artifacts/{staff,wand,throw}-ui-{Vulkan,OpenGL}-{1,2,3}`. Throw frames
include the actual confirmation, unchanged cancellation, and one approved use;
staff/wand checks include held-device restoration. These are engine-driven
input-handler tests, not physical keyboard/mouse acceptance.

The local package is produced by `scripts/package-release.ps1 -Version
0.1.0-target-preview-v16 -SkipBuild`; archive/manifest verification is separate
from runtime verification. It contains matching v16 bridge and native components,
plus corresponding source. Package evidence and extracted-runtime results are
recorded under `artifacts/release/0.1.0-target-preview-v16` and
`artifacts/*-ui-packaged-*`. The final extracted package passed all 18 renderer/
HUD-scale/device combinations as well. `artifacts/target-acceptance.json` records
all 36 source/package runtime checks and their actual 3440x1440 capture size.
The extracted DLL's inactive-session, v15, stale-revision, and missing-item
rejections are recorded in `artifacts/target-packaged-abi.json`.

Final engine SHA-256: `7839973de3db8a431d7ceeb70101e765899dbf12bd93e183e968c5d14309cd11`.
Final bridge DLL SHA-256: `97d4ab5ada05e7f0a46e8b789afd590c0c06e3f8b38ce0f5880fbcaea41aa550`.
Both were verified byte-identical between the build and extracted package.

Representative captures:

- Historical staff baseline: `artifacts/staff-ui/Screenshot_Doom_20260905_122655.png`.
- New staff guide: `artifacts/staff-ui-OpenGL-1/Screenshot_Doom_20260905_160652.png`.
- Final packaged throw confirmation, scale 3:
  `artifacts/throw-ui-packaged-OpenGL-3/Screenshot_Doom_20260905_162625.png`.

## Remaining acceptance and limits

- Physical keyboard/mouse testing and a live standalone visual targeting
  comparison are separate, unclaimed acceptance gates.
- Existing pre-change staff/wand captures are retained in `artifacts/staff-ui`
  and `artifacts/wand-ui`; they are historical evidence, not newly captured
  controlled before/after pairs. No pre-change throw-confirmation frame exists.
- Public 1024-candidate overflow, every beneficial-device ally combination,
  and every map-edge/range boundary combination are not exhaustively exercised
  by the controlled fixtures. The pure collector and existing Brogue predicates
  remain the source of these policies.
- Preview tests do not claim an independent complete serialization of all
  private Brogue globals. Direct nonmutation comparisons, continuation tests,
  and the read-only implementation collectively cover the stated boundary.
- The generalized interaction state machine, additional semantic commands,
  bolt animations, and UZDoom migration acceptance backlog remain separate.

The initial modified `.gitignore` and untracked project baseline were retained;
no reset, clean, commit, or PR operation was performed.
