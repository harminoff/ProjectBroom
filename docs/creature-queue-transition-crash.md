# Native queued level-transition repair

Contribution category: maintenance protecting Brogue parity. No gameplay
outcomes, bridge ABI, RNG, creature assets, or map geometry were changed.

## Failure and cause

The seed-26 ordinary-intent route used for the goblin totem review crashed on
entry to BRG02 on both Vulkan and OpenGL. The retained Vulkan fatal report is
an access violation reading `0000002800000027`, at executable RVA `0x65f3d3`.
There is no Release PDB, so this report alone does not name the faulting symbol.

The runtime log and source establish the presentation lifetime defect:

1. The bridge resolves the stair action at revision 36 and requests BRG02.
2. `DetachLevelPresentation()` discards the old raw actor pointers.
3. UZDoom's `ChangeLevel()` queues the engine transition; it does not load it
   synchronously inside the bridge command.
4. Before BRG02 loads, another `brg_actions` intent executes at revision 37,
   recreating 7 monster proxies and 13 floor-item proxies in the source level.
5. UZDoom destroys those actors while replacing the level. `primaryLevel`
   points at the reused global `FLevelLocals`, so pointer equality cannot detect
   that the proxy storage belongs to the previous level.

The original log fails the new transition-order regression at step 4. This is
separate from the older stale Doom hub-snapshot defect documented in
`depth-return-crash-investigation.md`.

## Correction

`brogue_bridge_frontend.cpp` keeps an explicit pending presentation barrier
from the moment a successful map reconstruction queues the engine change until
the engine's live depth matches Brogue's destination. The barrier covers stair
and deferred fall/retry changes, commands, queued actions/waits, comparison and
held input, scene attachment, and weapon projection. Escape and the existing
native save/exit path remain available. Shutdown clears the barrier.

Pending intent queues are retained, including when an earlier input source
requests a map change during the same input tic. No destination actor pointers
are repopulated while the engine still owns the source level. Existing native
load finalization and fall departure/arrival phases remain in place.

Brogue still resolves every intent through the unchanged bridge command path,
including `playerMoves()` / `playerTurnEnded()` / `startLevel()` as applicable.
Only projection and input-dispatch timing are delayed.

## Fixture correction

The seed-26 startup campaign defines MAPINFO for depths 1-4 only. Once the
crash was removed, BRG05 loaded as `Unnamed` without the expected level number,
and correctly remained behind the presentation barrier. That diagnostic run
was stopped and retained under `transition-crash/fixed-vulkan`.

`tools.monster_models.review_campaign.missing_depth_mapinfo()` now produces
review-only MAPINFO for undeclared depths through the headless route's target
depth, bounded to Brogue's 1-40 campaign. The natural totem observer includes
this metadata. The original startup PK3 remains byte-for-byte unchanged; no
map cells, entities, health, or gameplay state are injected. Later natural
reviews can reuse the helper. This does not change the production campaign
packaging contract.

## Verification

- Canonical Release compilation passed:
  `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
  The engine build fingerprint was refreshed and validated.
- 81 tests passed:
  `python -m unittest tools.test_brogue_bridge tools.test_broguedoom_resources tools.mapcompiler.test_compile`.
- 11 focused tests passed:
  `python -m unittest tools.test_level_transition tools.test_engine_source`.
- Vulkan and OpenGL native natural replays passed, including normal process exit and all
  three encounter captures. The regression checks every queued intent in order
  and rejects commands or proxy attachment between each level request and load.
- The 292-intent route reaches depth 5, cell 58,17, absolute turn 288, HP 20/30,
  hash `2dcb11e9c4d62ec5`, matching two headless route runs. Native revision 294
  includes recording setup; the headless route revision is 293. Two follow-up
  waits reach hashes `f216cb965c1fbb21` and `66b6f3a2ec52154d`.
- Pink-jelly OpenGL replay passed with normal exit, five captures, all 222 route
  intents plus three east intents in order, and final hash `a07209e57c20cd6d`.
  Brogue's real split IDs 75/76 and recoil/smear/drench animation logs were
  verified. Evidence: `artifacts/creature-queue/BRG-M12/after-transition-opengl`.
- Existing seed-1 Vulkan fall regression passed, including cancellation,
  departure/arrival, landing, and native save-on-exit. The final hash remains
  `16b7f15d918ac047` at absolute turn 28 / persistence turn 29, depth 2. An
  evidence-only copy of `tools/test_chasm_transition.py` changed only ROOT/output
  paths to preserve its earlier captures. Command:
  `python artifacts/creature-queue/transition-crash/fall-regression.py --backend 1`.
  Evidence: `fall-vulkan` and `replay-fall-vulkan.log`.

Reproduce each renderer with `python -m tools.test_level_transition --backend 1`
(or `0`), `--package artifacts/creature-queue/BRG-M11/final-vulkan-v2/ProjectBroom-review.pk3`,
and a fresh `--output` directory. Audit existing output with `--check DIR`.

Evidence lives under `artifacts/creature-queue/transition-crash/`: the immediate
dirty baseline, pre-change source/hash/log/fatal report, build and test logs,
and `verified-vulkan` / `verified-opengl` runtime evidence. The Vulkan encounter
capture was inspected: depth-5 scene, goblins and totem, health and authoritative
messages are visible. This repair does not claim new creature-art approval.

No full release packaging, physical keyboard acceptance, native save-load/revisit
rerun, standalone graphical side-by-side run, or exhaustive lifetime audit was performed for this narrow
fix. Exact repeated headless state hashes and actual native queues provide the
parity evidence here. No new third-party assets or licensing changes.
