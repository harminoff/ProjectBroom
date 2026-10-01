# Creature queue pipeline (v2)

This page supersedes the per-agent integration steps in
[creature-agent-handoff.md](creature-agent-handoff.md) for the remaining queue.
That document's authority rules and family lessons still apply; read its
"Lessons" section for your creature's family. Root `AGENTS.md` is mandatory.

Why v2 exists: the first 26 queue models took 41–154 agent-minutes each. The
machine steps took about 15 minutes; the rest was agents rewriting identical
baseline, card-restore, determinism, Blender, evidence and audit scripts, plus
full-gate reruns after art rejection. v2 splits the work:

| Phase | Who | Parallel? | Touches shared files? |
| --- | --- | --- | --- |
| 1. Author + preview | authoring agent, one creature family | yes, up to 4 agents | **never** |
| 2. Art review of preview | coordinator | — | no |
| 3. Integrate + gate a batch | coordinator, one command each | no (serial) | yes, generated only |
| 4. Final review + archive + queue | coordinator | — | queue files only |

## Phase 1: authoring agent

Work only in creature-local files:

- `tools/monster_models/<slug>_animation.py` (the master generator, exposing
  the standard `BONES`, `REST`, `CLIPS`, `geometry()`, `animation_data()`,
  `deform()`, `build()` API), `<slug>_materials.py`, `test_<slug>.py`;
- `assets/monsters/<slug>/` (manifest, `connected-skin.json.gz`, `.blend`);
- new, collision-checked runtime files: `mod/BrogueDoom/models/monsters/NN_<slug>.iqm`,
  `mod/BrogueDoom/graphics/<LUMP>.png` (+ `_N`/`_S` maps), optional new shader;
- `docs/<slug-with-dashes>-animation.md` (your report);
- **pending profile row** `assets/monsters/skeletal_pending/MK_<NAME>.json`.
  Copy a registered row from `assets/monsters/skeletal_profiles.json` as the
  template. Add `"report": "docs/<...>-animation.md"` and a `"traits": [...]`
  list, which the generated card and bestiary use. Add `"ownedFiles": [...]` for
  any extra runtime file, such as a shader. Wall turrets need `wallMountBack`;
- optional **pending GLDEFS snippet** `assets/monsters/skeletal_pending/MK_<NAME>.gldefs`
  (the preview loads it; integration appends it to `mod/BrogueDoom/GLDEFS`).

Connected-skin configuration belongs in your module, not in shared files:
define `CONNECTED_SKIN = lambda name: ...` (part selection), and optionally
`SKIN_VOXEL_SIZE` and `SKIN_FACE_BUDGET`. Do not edit `connected_skin.py`,
`blender_skin.py`, `bestiary.py`, `skeletal_profiles.json`, generated files,
cards, the queue, GLDEFS or native code.

### Phase 1 runs in two hand-backs: blockout, then final

Almost every rework in rounds C and D was a design call that the first
front-camera screenshot already showed: wrong Brogue colour, cute face, balloon
anatomy, wings reading as arms, an unfortunate head shape, a too-short
wingspan. Show the design before investing in detail.

1. **Blockout hand-back, after about 15–20 minutes.** Build the silhouette,
   proportions, face and colour blocking, plus the idle, attack-key and death
   poses. Painting can be flat or rough. Capture only the key views:

   ```powershell
   python -m tools.monster_models.<slug>_animation
   python -m tools.monster_models.review_skeletal --symbol MK_<NAME> --backend 1 --preview --views key --width 1920 --height 1080 --output artifacts/creature-queue/BRG-Mkk/blockout
   ```

   Hand back the six captures (oblique idle, attack key and death end; front
   idle and attack key; front idle at 128 units). Include the Brogue colour you
   looked up (`monsterCatalog` in `src/brogue-mapgen/src/brogue/Globals.c`
   and its `const color`) and your palette plan, then **stop**. The
   coordinator approves or redirects in minutes.
2. **Final hand-back, after approval.** Paint, detail, write tests. Iterate
   with the fast loop only:

   ```powershell
   python -m tools.monster_models.<slug>_animation                      # export
   & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --threads 1 --factory-startup --disable-autoexec --python-exit-code 1 --python tools/monster_models/blender_skin.py -- <slug>   # cage bake, only if you have a connected skin and changed it
   python -m tools.monster_models.review_skeletal --symbol MK_<NAME> --backend 1 --preview --views key --width 1920 --height 1080 --output artifacts/creature-queue/BRG-Mkk/iterate
   ```

   Once, at the end:
   - a second cold `--threads 1` cage bake, whose hashes must match the first;
   - one full Vulkan gallery (`--all-angles --distances`) into `preview-vulkan`
     with its contact sheet
     (`python -m tools.monster_models.creature_pipeline contact artifacts/creature-queue/BRG-Mkk/preview-vulkan`);
   - the precheck (below).

   Do **not** run the Blender build/reopen or the OpenGL gallery. The gate does
   both, and its per-creature cache makes a late failure cheap to fix.

Captures from every agent and the gate are serialized by a machine-wide lock,
so queueing for a minute is normal. Frozen or timed-out captures are retried
automatically (`--attempts`, default 3), so there is no need to hand-check
hashes. Delete the `blockout` and `iterate` folders before the final hand-back.

**Self-review before each hand-back.** Look at your own front-camera captures
at 128 and 192 units and answer each question:
- Is the base colour Brogue's catalog colour?
- Does the face read as a threat rather than a mascot: no bulging eyeball
  domes, a brow over small eyes, visible teeth where the creature has them?
- Are bodies fused or shaped forms, rather than stacked spheres or capsules?
- Do wings, heads and tails read unambiguously? Wings need feathered or
  membrane leading edges, not bare arms. Heads must not read as a dome from
  behind.
- Does the attack key pose change the silhouette strongly, and is it on the
  middle frame?
- Does the death end limp on the floor?
- Does the creature separate from grey walls and a brown floor by value?

Fix anything that fails before handing back.

Before the final hand-back, run the fast precheck. It takes seconds to a few
minutes and works on your pending row:

```powershell
python -m tools.monster_models.creature_pipeline precheck MK_<NAME>
```

It re-encodes your IQM from the generator and compares the bytes. The mesh
label must be `Project_Broom_<symbol without MK_, lowercase>`. It also checks
the manifest hash, clip names, 35 Hz durations and the absence of
`visualScale`, then runs your creature test module. The gate runs the same
precheck first, so anything it catches fails the gate within minutes.

`--preview` spawns a fixture-local actor bound to your exported IQM/skin, so no
registry, native build or regeneration is needed. On the dart turret it
produced pixels identical to the accepted packaged gallery. Put each action
clip's key pose on its **middle frame**: galleries sample first/middle/last.

Final hand-back (then stop) with:
- the Vulkan preview contact sheet path;
- the front idle, attack and death capture paths;
- cage-bake hashes from two cold bakes;
- the precheck result;
- your art decisions and candid flaws. **Do not** run the shared suites, regenerate,
build native code, take baselines or write final evidence. The coordinator
does that once per batch.

## Phase 3: coordinator integration and gate

```powershell
python -m tools.monster_models.creature_pipeline baseline  --batch B01
python -m tools.monster_models.creature_pipeline integrate --batch B01 MK_A MK_B MK_C
python -m tools.monster_models.creature_pipeline gate      --batch B01 MK_A MK_B MK_C [--extra-tests tools.monster_models.test_<family> ...]
# after visually accepting artifacts/creature-queue/BRG-Mkk/final-*-contact.jpg:
python -m tools.monster_models.creature_pipeline archive   MK_A MK_B MK_C
```

- `baseline`: hashes ~1,670 integration-surface files and keeps raw copies of
  shared/generated files. It refuses to overwrite.
- `integrate`: promotes pending rows (exact registry format), appends pending
  GLDEFS, regenerates, and checks each card is skeletal and links its report.
- `gate`: runs, per creature, two fresh-process exports (byte determinism), the
  Blender build and a separate fresh-process reopen check, then one native
  build and fingerprint (skipped if up to date). It then captures both
  packaged 34-view galleries plus the wall fixture for wall-mounted rows,
  verifies every package entry against source, and builds contact sheets. Once
  per batch it runs the creature tests plus the shared suites, writes
  verification records, checks that a second regeneration leaves them
  unchanged, and runs the preservation audit. That audit fails on any
  unexpected changed or new file, or on any shared-registry entry changed
  outside the batch. Output goes to `artifacts/creature-queue/batches/<batch>/`
  and per-creature `BRG-Mkk/`.
- Speed (since 2026-09-29):
  - The gate runs the precheck first.
  - Determinism and Blender run in parallel (`--jobs`, default 4).
    Galleries run serially, because they share one GPU.
  - Test modules run in parallel processes. Creature tests that passed in the
    precheck are not re-run.
  - Each creature's determinism, Blender and gallery results are cached in
    `BRG-Mkk/gate-cache.json`, keyed by input hashes. A re-run after a partial
    failure therefore redoes only what changed. `--force` ignores the cache.
  - A frozen or timed-out capture is retried up to three times automatically.
    A freeze is any identical pair across a camera or distance change.
  - `test_skeletal` caches full verification in `.build/skeletal-verified.json`,
    keyed by generator sources, profile row and model bytes. Set
    `BROOM_SKELETAL_FULL=1` to force a full check.
  - Batch C (12 creatures) took about 67 minutes with an empty cache; the old
    pipeline took about 100 minutes per pass.
- The gate regenerates before writing verification records. Without this, a
  re-export after `integrate` left stale art hashes in the index, and
  regeneration then marked the records stale.
- Pass `--declare-change PATH=REASON` for an intended maintenance edit to a
  baselined file, such as a pipeline or docs change. It is recorded under
  `declaredMaintenance` in `preservation.json` instead of failing the audit.
- Authoring for the next round may continue while a batch gates. The audit
  reports creatures with a pending row outside the batch under
  `inProgressOtherCreatures` rather than as failures, and the capture lock
  queues their previews behind the gate's galleries. The gallery and
  `archive` package checks skip the runtime files of those pending rows
  (recorded as `inProgressSkipped`) and compare the two backends by
  `checkedSha256`, a digest of the compared entries only. Before 2026-09-29
  they compared every entry, so a next-round re-export failed batch D's gate
  and later its archive. Two things must not happen during a batch: an agent
  touching that batch's creatures or shared kits, and anyone editing the
  shared tools.
- Regeneration is now a full no-op on an unchanged tree. Hand-refined cards
  (`HAND_MAINTAINED_CARDS` in `bestiary.py`) are never overwritten, so no
  card-restore step exists anymore.
- Do not dispatch a new authoring round while a gate's native build is linking
  (Windows locks a running `uzdoom.exe`, LNK1104). Run gates between rounds.
- Natural-encounter gates are recorded as **deferred** to one later deeper-route
  census for all deep creatures; agents do not re-derive them.

Pipeline self-test (dart turret, isolated evidence root, no record writes):
`python -m tools.monster_models.creature_pipeline --evidence-root <dir> gate --batch <name> MK_DART_TURRET --no-record`.
Unit tests: `python -m unittest tools.monster_models.test_creature_pipeline`.

## Remaining queue grouped for parallel authoring

Queue order is production priority, not encounter order; groups trade strict
order for shared kits. Suggested rounds (one agent per line):

| Round | Agent group | Creatures (queue #) | Start from |
| --- | --- | --- | --- |
| A | dar kit | dar priestess (27), dar battlemage (31) | dar blademaster |
| A | goblin | goblin warlord (41) | goblin, goblin conjurer |
| A | jelly | black jelly (42) | acid jelly, pink jelly |
| A | equine | unicorn (53) | centaur horse body |
| B | specters | phantom (29), revenant (33) | wraith |
| B | tentacles | kraken (28), tentacle horror (35) | bog monster, naga |
| B | demons | imp (30), fury (32) | pixie scale, vampire bat wings |
| B | stone | golem (34) | ogre, troll |
| C | blades | spectral blade (45), spectral sword (46) | flame-turret affine cages |
| C | guardians | stone guardian (47), winged guardian (48), guardian spirit (49), sentinel (39) | golem (round B) |
| C | objects | phylactery (36), eldritch totem (51), mirrored totem (52), phoenix egg (56) | goblin/ogre totem |
| C | undead nobles | lich (40), vampire (43) | dar blademaster, wraith |
| D | fire | flamedancer (44), ifrit (54) | salamander flame atlas, wisp |
| D | dragon | dragon (37) | new |
| D | worm | underworm (38) | naga coil, centipede |
| D | birds | phoenix (55) | vampire bat, flame atlas |
| E | unique | Warden of Yendor (50), mangrove dryad (57) | new |

Coordinator review bar, unchanged: reject art that reads generic, blocky, or
unreadable from the gameplay camera at 64/128/192 units. Rejection now costs
only a phase-1 rework, not a full gate.

## Authoring agent prompt template

Coordinators dispatch authoring agents (Sonnet 5.5) with this skeleton. Fill in
the angle brackets. Use Brogue's creature facts and colour, never guesses.

```text
You are a phase-1 AUTHORING agent for Project Broom's creature queue, repo <repository root>.
Creature: <name> (<MK_SYMBOL>, work id <BRG-Mkk>), round <R>.

Read first: AGENTS.md, docs/creature-pipeline.md (phase 1: blockout hand-back, then final hand-back),
and the Lessons section of docs/creature-agent-handoff.md.
Look up the creature in src/brogue-mapgen/src/brogue/Globals.c: monsterCatalog row, its const color,
flags, abilities, bolts and description. Presentation only.

Brogue colour: <colour name = values>. Make it the base identity.
Start from: <existing kits/modules>.
Design intent: <silhouette, key features, attack key pose, death>.

Rules:
- Touch only creature-local files plus assets/monsters/skeletal_pending/<MK_SYMBOL>.json (+ .gldefs).
- Mesh label: Project_Broom_<symbol without MK_, lowercase>.
- Durations are 35 Hz tics. No visualScale. Tests use skeletal_registry.find.
- Key poses go on middle frames. Stay within -32..+32. Face +X. Death ends on the floor.
- Iterate with `review_skeletal --preview --views key`.
- Do not run the Blender build, the OpenGL gallery, the shared suites, a regeneration, a baseline or the gate.
- Keep scratch in your own scratchpad subfolder. Never touch other creatures' files.
- Keep artifacts lean.
- STOP at the blockout hand-back: six key captures plus the Brogue colour and palette plan.
- After approval, finish and run the self-review checklist.
- Run `creature_pipeline precheck <MK_SYMBOL>`, then STOP with the final hand-back.
```
