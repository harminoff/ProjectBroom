# Sequential creature authoring handoff

> **Superseded workflow (2026-09-28):** the remaining queue uses the v2
> pipeline in [creature-pipeline.md](creature-pipeline.md). Authoring agents
> now work in parallel on creature-local files and a pending profile row. They
> review with `review_skeletal --preview` and stop. The coordinator integrates
> and gates batches with `creature_pipeline.py`. Steps 1–8 below (baselines,
> card restores, per-agent determinism/evidence/audit scripts) no longer apply
> to authoring agents. The boundaries and the "Lessons" section still apply;
> read the lessons for your creature's family.

The user explicitly authorized completing all remaining 57 models with a fresh
agent for each, sequentially. Work only on the one assigned creature. Report
back and let the coordinator review and dispatch the next. The durable queue
is `docs/creature-creation-queue.json` and `.md`; only the coordinator edits it.

After 15 verified models the platform refused another spawn with `agent thread
limit reached`. The user was informed. Continue one model at a time using focused
disk handoffs to idle existing agents when fresh agents cannot be allocated.
Reused agents retain prior context; do not describe them as fresh. Take a new
immediate baseline and finish only the newly assigned creature.

After the eighteenth verified model, fresh allocation became available again;
naga was successfully dispatched to a fresh agent. Prefer the user's requested
fresh-agent workflow when capacity permits, falling back transparently only
when the platform refuses allocation.

## Required context and boundaries

Read root `AGENTS.md`, relevant runtime architecture and parity TODO, your
individual `docs/creatures/NN_name.md`, `docs/skeletal-enemy-workflow.md`, and
the relevant earlier reports/generators. The toad report is the newest complete
example: `docs/toad-animation.md`. The source roster, prose and horde references
are in `assets/monsters/bestiary-index.json` and pinned Brogue source.

This is presentation-only. No new gameplay, AI, collisions, health, turns,
RNG, spawn rules, status behavior or bridge ABI changes. Do not infer invented
powers from colors. Do not use a broad generic shape and call it detailed art.
Reuse family tooling where it fits while preserving each creature's anatomy,
signature features and actual source description. Immobile objects must not
gain a locomotion fiction; unused shared animation roles can settle at rest.

For turrets, Brogue's `MONST_TURRET` includes attackable-through-walls and the
ordinary horde terrain is WALL. Check actual wall placement, not only a floor
gallery. The existing `MonsterWorldPosition` centers most kinds in their cell;
an enclosed wall can conceal the mesh. If a projection fix is necessary, keep
it presentation-only, use copied known terrain/visibility and displayed identity,
and prove that gameplay collision/coordinates and Brogue outcomes stay unchanged.
Never cut authoritative walls or reveal hidden creatures to expose a model.
The arrow-turret pass now supplies `wallMountBack` profile metadata and
`wall_mount.h`: known exposed cardinal faces face the copied player cell,
with stable corner ties. Attack-facing yaw is guarded for mounted proxies.
Reuse and test that capability for later turrets rather than adding another
placement path. See `docs/arrow-turret-animation.md`; its isolated wall fixture
must wait two engine tics after spawn before setting sampled poses, otherwise
Spawn silently overrides the requested clip. The native seed26-depth6 turret
encounter is verified on both backends, but natural firing/death remains open.

The checkout contains extensive pre-existing tracked/untracked work. Inventory
and hash a narrow baseline before edits; preserve all unrelated files and prior
verification. Do not reset/clean/commit/publish. Save evidence in a new named
`artifacts/creature-queue/<work-id>/` directory. Use separate background Blender
processes; never clear or replace a user's live Blender document.

## Implementation and verification

1. Write expected appearance, source facts versus art decisions, and planned
   proof in your creature report before implementation.
2. Author detailed geometry, original textures, sensible scale and animation.
   Use connected skin for organic anatomy; separate accessories where real
   anatomy requires it. Existing shared solver assumes unit bone scales.
3. Register in `skeletal_profiles.json`; use the existing deterministic IQM
   exporter and generated native table/MODELDEF/ZScript. Preserve static
   references and existing gameplay-inert proxy classes. Six roles are idle,
   move, attack, alternate attack, hit and death; only idle/move loop.
4. Build/fresh-open the editable Blender source. Verify sampled source/runtime
   deformation, packed textures and no missing linked resources. Use current
   local Blender 5.2: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.
   Connected cages use `--threads 1` for cold-bake repeatability. The existing
   extension-cache permission warning is nonfatal; do not change global settings.
5. Run meaningful creature-specific checks plus existing skeletal/resource
   regression suites. Verify two builds byte-for-byte, including connected
   cages and all supplemental maps. Run native compile for generated-table
   additions with `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
   Refresh the build fingerprint with `python tools/engine_source.py --root . --record-build .build/uzdoom/Release`
   only after successful compilation.
   Finish native linking before launching its review executable: Windows locks
   a running UZDoom binary, so overlapping the link and capture causes LNK1104.
   For an asset-only addition, scope verification to its generator/family,
   skeletal/resource suites and this native build. Regenerate the required
   registries/bindings. A full `build-source-bridge.ps1` run with every bridge
   and parity suite is not required for each individual model; broader checks
   belong to relevant shared-code changes or the coordinator's batch validation.
6. Use `review_skeletal --symbol MK_NAME --backend 1` and backend 0 with
   `--packaged --all-angles --distances --width 1920 --height 1080 --output <new evidence directory>`.
   Inspect actual before/after, clip, angle and distance images. Models must
   load without new resource errors and remain nonblocking. Both deterministic
   packages should match source. Adapt the review room only if anatomy needs
   special framing, keeping it explicitly separate from gameplay.
   Send early idle/front, attack and final-death captures to the coordinator
   before repeating the full final evidence run. Finish art corrections first;
   final package, Blender and deterministic proofs must use the accepted bytes.
   The explicit size sets windowed mode and `vid_setsize` in the isolated
   review configuration; startup width/height alone are ignored by this build.
   For natural observers, use the same explicit command before the capture
   waits. Keep screenshots, logs and verification manifests. After acceptance,
   the coordinator losslessly archives only review PK3s with `review_archive`:
   unchanged ZIP segments are stored once under the queue evidence root, and
   every package can be restored byte-for-byte. Do not delete these blobs or
   manifests. This avoids exhausting disk space across all 57 models.
7. Seek a natural fixed-seed encounter using existing bridge commands and
   copied-state route helpers. Never inject health, spawn or reveal creatures
   to claim a natural encounter. Late/rare creatures may require more work;
   state unresolved gates precisely. Coordinator candidate routes and bounded
   search results are in `artifacts/creature-queue/encounter-preparation/`;
   these are headless preparation only, not renderer proof. Acid mound has
   seed26/depth6 and goblin mystic seed27/depth5 candidates. Reproduce and
   validate them with your actual package. Existing `review_toad.py` demonstrates
   an eye-level observer. Native hashes use padded hex; compare numerically.
   `bloat_encounter.cpp` accepts optional limits after the existing arguments:
   `route.exe <seed> <kind> <waits> --visible <maxSteps> <maxDepth>`.
   Omitted limits remain 450/4; later creatures can use larger bounded searches.
   This route uses copied snapshots and ordinary intents, with no health or
   spawn overrides. Greater limits do not guarantee survival or an encounter.
   Old seed startup packages may declare only depths 1-4. Use
   `review_campaign.missing_depth_mapinfo(package, targetDepth)` in the
   observer overlay to add absent MAPINFO declarations within Brogue's 1-40
   range. It changes no geometry or simulation and preserves the package.
   The shared native transition lifetime repair is documented in
   `docs/creature-queue-transition-crash.md`; preserve its pending-map barrier.
   A hung process titled `UZDoom Very Fatal Error` is a crash dialog, not a
   traversal timeout: record that evidence before bounded cleanup.
8. Update only your creature's bestiary verification and report, preserving
   every other entry. Regeneration normalizes previously hand-refined creature
   cards (notably goblin conjurer); restore only your own unwanted generator
   delta from the immediate pre-task copy, never from git HEAD.
   Back these files up as bytes, not decoded text: existing mixed line endings
   must survive unchanged. Verify restored SHA256 against the immediate baseline.
   The assigned row in generated `docs/creature-model-index.md` should update
   with the final asset metadata. Preserve every other row. This generated
   model index is distinct from coordinator-owned `REVIEW.md` and the queue.

## Lessons from completed queue entries

- A gallery-spawned actor may miss native proxy synchronization. Wisp review
  caught `ApplyMonsterVisibility` replacing its additive material with opaque
  defaults. The repaired path restores the displayed actor class's render style
  and alpha for direct visibility; hidden and sensed rules remain unchanged.
  Preserve this behavior, including hallucinated displayed identity. The isolated
  `brg_monster_visibility_smoke` fixture exercises real native transitions for
  wisp and rat only in ART01 with no active Brogue session; it is synthetic proof.
  See `docs/wisp-animation.md`. New native include files also need build-source
  fingerprint coverage in `tools/engine_source.py`.
- Validate natural captures against copied turn, health and entity flags. A
  short screenshot delay can precede a queued action. Captive visibility is
  not hostile combat proof. A later attack in the same exchange may replace
  recoil; report the actual displayed clip rather than its screenshot filename.
- For articulated legs, verify reachable IK targets and planted support feet.
  Fix geometry or gait when checks fail; do not loosen checks to accept sliding.
  Centipede's final gait uses zero automatic floor compensation.
  Inspect the final death pose for a visibly limp or collapsed silhouette;
  lower height alone can still read as a living combat crouch with a raised weapon.
- Inspect silhouette and material depth from several engine angles before
  accepting deterministic exports. A correct export can still have weak anatomy
  or indistinct materials. Keep source color cues separate from literal paint.
  Fused organic skin needs continuous pigment coordinates: independently shaded
  source-part UVs can leave conspicuous triangular colour patches after remeshing.
  Ventral markings need surface-aware placement: naga's initial Z/Y projection
  put its pale underside on the dorsal head and back. Coiled bodies also need
  longitudinal coordinates along the body centerline; height alone stretches
  scales into streaks. Inspect both oblique and rear views before freezing maps.
- Check centred cell clearance using minimum and maximum X/Y coordinates for
  every animation frame. A total width below 64 does not prove that an off-centre
  pose stays within the cell's -32 to +32 limits.
- Keep separate limbs apart in an organic rest cage: troll palms touching its
  thighs caused unwanted remesh fusion and mixed deformation weights. Move the
  actual anatomy and rig together. For small skin-attached details, seat anchors
  on the supporting cage and reuse its normalized weights; do not widen an
  attachment tolerance to hide drift during animation.
- Preserve the legacy static recipe/traits while adding skeletal metadata.
  Salamander's trait change altered the old OBJ generator's expected output;
  restoring the immediate baseline fixed that regression without changing the
  new skeletal assets. Use distinct log names for retries so failed evidence
  cannot be overwritten. Check raw and exported root positions: automatic floor
  correction can disguise a floating collapse even when exported bounds pass.
- Prepared ogre encounter: seed 169, depth 5, target ID 99, 247 intents,
  hash `06838c74a89fe52e`, in `encounter-preparation/ogre-route.txt`.
  This is headless preparation only; inspect captive/allied flags in runtime.
  Bog monster searches through seed 2000 and spider through seed 500 found no
  encounter with the conservative route. Avoid repeating identical searches.
- Ogre shaman: Python 3.12 float `sum()` rounding differs between system Python
  and Blender's Python for tube-based parts; round authored coordinates to 1e-6
  for identical bake fingerprints. A held prop longer than about 62 units cannot
  lie flat inside the cell, so plan death poses around it. Drop duplicated ring
  seam vertices before measuring tube centroids. `blender_skin.py` accepts an
  optional per-creature face budget (default 5,600); raise it only for your own
  creature so other bakes stay byte-identical.
- Centaur: check a new texture lump name against existing graphics first (its
  first build overwrote the centipede's `BRGCENT.png`). A skin needing more than
  8,192 faces can place extra per-triangle patches in the spare bottom-right
  atlas quadrant. Quantize skin weights to 1e-6 (last weight takes the exact
  remainder) so Blender's and system Python agree. Near-black eye-socket shells
  read as a stare; use lids and a lash line. Held-prop overhang, not body length,
  limits draw poses: tilt props until the extreme frame to stay in the cell.
- Acidic jelly: the gallery samples each action clip only at its first, middle
  and last frame, so put the key pose at the middle frame or the clip will look
  like idle. The engine's flat bright light hides sculpted form: paint value
  contrast, occlusion, fake-subsurface cores and specular pools. Judge the
  silhouette from the actual gameplay camera at 128 and 192 units. The
  coordinator rejected a first pass that read as a round fruit.
- Pixie: never re-run a baseline script after edits begin; make it refuse to
  overwrite. The shared Blender exporter needs the first clip named `idle`. Lay
  per-triangle skin islands out in spatial (Morton) order to avoid mipmap
  speckle. Small creatures need a creature-specific finer voxel size. A shared
  carry pose blended into every action avoids pops out of idle. Orientation
  tests must compare with bone-rotated rest normals once the whole body turns.
- Flame turret: a solid mask plate hides anything recessed behind it, so raise
  ports and nozzles in front. A hinged cover must close through free space;
  check it per frame in barrel space. Affine corner cages give exact emissive
  extinction with unit bone scales and allow attack-only attached fire without
  extra actors. Mesh builders must triangulate collapsed pole rows (no
  zero-area triangles). `review_flame_turret_wall.py` is the newest wall
  fixture to copy for turrets.
- Keep only evidence the final report cites. Delete your own superseded
  intermediates (duplicate packages, retry galleries, scratch renders); keep at
  most one early-review contact sheet documenting a meaningful art correction.
- Pipeline round A (dar priestess/battlemage, goblin warlord, black jelly,
  unicorn): every first delivery was returned for the same reasons. Attack
  key poses changed the silhouette too little to read at 128/192 units, and a
  bent-over but still-standing death read as a living crouch. Exaggerate the
  middle-frame action silhouette (full lunge, overhead raise, a wave at 1.6-2x
  rest height) and end deaths on the floor. Near-white and near-black creatures
  need a deliberately wide painted value range (the unicorn's lavender
  underside, the black jelly's specular bands and shader rim). Bare skin needs
  painted anatomy or it reads as cloth.
- Creature tests must look up their profile with `skeletal_registry.find(symbol)`,
  never by reading `skeletal_pending/MK_X.json` directly: integration consumes
  the pending row and GLDEFS snippet. A GLDEFS check should fall back to
  `mod/BrogueDoom/GLDEFS`. Hard-coded pending paths failed the round A gate.
- Parallel preview runs under load sometimes capture stale, repeated frames.
  Hash the gallery and retry when a key middle frame equals another capture.
  Expected duplicates are only each action clip's first/last frame and idle
  frame 0.
- A generator's `__main__` must re-import itself by package name, or
  `connected_skin` cannot find its `CONNECTED_SKIN` hook under `python -m`.
  Sum weights with `math.fsum` (or quantize) so Blender's and system Python agree.
- Pipeline round B (kraken, phantom, imp, fury, revenant, golem, tentacle
  horror): profile `durations` are engine tics at 35 Hz, not frame counts.
  Set each action role to at least ceil(frames x 35 / fps); shorter values cut
  the clip off in-engine and fail `test_skeletal`. Size a creature in its own
  exported geometry rather than with registry `visualScale`: the shared
  MODELDEF scale count test (only the kobold is scaled) would otherwise need a
  shared edit that fails the preservation audit.
- The gameplay camera faces the creature's +X front: put faces, eyes and beaks
  there (the first kraken showed only its mantle from the front). Watch
  unintended reads at 128/192 units (symmetric crown tentacles read as bunny
  ears, arms under eyes as a moustache, stock hooded skulls as a monk, a block
  head as a brick). Separate stone and grey creatures from the grey cobblestone
  walls with a warmer or lighter palette and strong per-block value gradients.
  The oblique gallery camera crops above about 72 units, so make key poses low
  and wide rather than overhead.
- Frozen preview/gate captures recur under load (fury and revenant OpenGL froze
  from capture 26 on the first round-B gate). Hash every final gallery before
  archiving; a rerun of the gate recaptures them.
- Pipeline rounds C and D: **use Brogue's catalog colour as the creature's base
  identity.** Look up the monster's colour in `monsterCatalog`
  (`src/brogue-mapgen/src/brogue/Globals.c`) and its `const color` definition
  before choosing a palette. Five first passes were rejected for ignoring it:
  - the dragon was painted crimson, but `dragonColor` is green;
  - the underworm was salmon pink, but `wormColor` is tan-brown;
  - the winged guardian was white, but Brogue uses `&blue`;
  - the guardian spirit was amber, but `spectralImageColor` is the spectral
    sword's crimson.
  Creatures that share a Brogue colour should share a look (the guardian
  spirit reuses the accepted spectral sword recipe). Keep enough value contrast
  against the grey walls and brown floor; push value, not hue.
- Rounds C and D art rejections that recurred:
  - **Separate rigid ellipsoids read as balloons or toys.** Fuse bodies with a
    `CONNECTED_SKIN` cage (ifrit, like the ogre, troll and golem), and shape
    muscles as elongated, overlapping forms rather than spheres.
  - **Smooth domed heads can read as phallic** from rear views (underworm).
    Make heads widest at the mouth and armour or cap the back.
  - **Cute faces undercut threat.** Bulging eyeball domes and soft muzzles
    read as mascots. Use a heavy brow over small sunk slit eyes, a wedge snout
    and visible fangs.
  - **Wing silhouettes need feathered leading edges.** A bare wing arm with a
    knuckle knob reads as raised arms. Folded wings must still show from the
    front camera without reading as extra horns.
  - **Additive overlap of many plates is busy.** Fewer, continuous shells plus
    back-face rejection and a rim-dominant shader read cleanly. An opaque
    "ghost" reads as a wooden mannequin.
  - **Short breath or cast effects vanish at 192 units.** Use layered
    fullbright cones (dragon, via a pending `.gldefs` plus a region shader) or
    a separate fireball cage (flamedancer), and park hidden effect bones where
    no other clip can reveal them.
- Process notes from rounds C and D:
  - Agents share one session scratchpad. Keep helpers in a per-creature
    subfolder, and never move or delete another creature's
    `artifacts/<name>-animation/` or `BRG-*` files.
  - A generator can drift from its exported IQM when shared kit code changes
    after export (stone guardian arm poses). Re-export and re-preview; the
    gate's fresh-process export is the source of truth.
  - The IQM mesh label must be `Project_Broom_` plus the lowercase symbol
    without `MK_` (for example `Project_Broom_spectral_image`,
    `Project_Broom_charm_guardian`), not the creature slug. The shared
    `test_skeletal` registry/binary check rebuilds the bytes from the symbol.
    The round C gate failed on three creatures for this. Run
    `python -m unittest tools.monster_models.test_skeletal` locally before
    handing back; it reads pending rows only after integration, so also check
    the label by eye.
  - unittest collects a shared test base class as its own case. Make it a
    mixin, or `del` it after subclassing.
  - Authoring for the next round can run while the coordinator reviews and
    while a batch gates: the audit and package checks set aside creatures
    that still have a pending row (see creature-pipeline.md). Never touch the
    gating batch's creatures or shared tools.
- Process notes from rounds D and E:
  - Part names must be unique within a creature. Blender renames a duplicate
    (`ring` to `ring.001`), so the gate's fresh-process reopen check looked up
    the same object twice and failed with a 52-unit error (the ifrit's two
    arm bands). The IQM was unaffected, so only the gate catches this.
  - Unintended reads recur at close range after the silhouette is fixed:
    ash lumps as skulls (phoenix), chest glow cracks as a cat face and then a
    spider (Warden). Check a 2x crop of glowing or clustered details.

## Handoff format

Return a compact report with:

- Assigned symbol and delivered source/runtime/report/evidence paths.
- Distinctive art decisions, rig/clip counts and authoritative boundaries.
- Exact passing test totals, compile result, deterministic hashes, package
  result and inspected Vulkan/OpenGL captures.
- Natural encounter seed/depth/actions/hashes, or the exact remaining obstacle.
- Any failed, missing or still-open acceptance gates and related next action.
- Shared files changed, baseline-preservation result, and reusable family lessons.

Do not mark user art approval complete. Do not stop at a scaffold or a build
without attempting the actual renderer checks. Do not spawn the next agent.
