# Explosive bloat membrane and animation

The coordinator losslessly archived the review packages after verification.
Restore a final package before replaying it:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M30/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding `final-opengl` manifest for OpenGL. Screenshots, logs and
archive segments remain available; restoration reproduces exact package bytes.

BRG-M30 / MK_EXPLOSIVE_BLOAT is presentation-only. The pinned catalog describes
a rare bloat subspecies: a thin membrane surrounding highly explosive gases,
orange glyph RGB 100/50/0, flying/flitting, kamikaze and DF_BLOAT_EXPLOSION on
death. No eyes, limbs, weapons or magical organs are inferred.

The original art reuses the existing continuous seven-bone bloat-family
membrane, with amber-orange pigment, darker fine vessels and pale taut pressure
areas. Six cosmetic roles show breathing, drift, two bumps, recoil and a rapid
asymmetric deflation into a low spent membrane. These colors, dimensions and
motions are art choices. No independent fire, damage, gas or terrain is spawned.
Combat.c's existing MA_KAMIKAZE -> killCreature and MA_DF_ON_DEATH ->
spawnDungeonFeature(DF_BLOAT_EXPLOSION) remain the sole gameplay authority.

All new art is original Project Broom work under CC-BY-SA-4.0. No third-party
artwork is imported; prior bloat and pit-bloat sources and bytes are preserved.

## Delivered art and authority

The continuous family mesh has 1,521 vertices, 2,976 triangles and seven bones.
Rest dimensions are 28 x 26.3268 x 32 map units, with a 16-unit hover gap.
The six clips contain 118 frames in total: idle, drift, bump, bump_alt, recoil
and collapse. Only idle/drift loop. Collapse briefly swells then folds the crown
off-center and settles into a low cupped membrane. Its final height is 9.3120
units, with maximum Z 12.7689. Across every sampled frame, X lies within
[-16.4229,20.2889], Y within [-14.8329,15.3181], and Z remains above 3.4568.
These are centered cell-clearance measurements, not just total width checks.

The dedicated 512-square RGB diffuse has periodic longitude, orange/amber
pigment, dark fine vessels and paler taut areas. It has no alpha, emission,
brightmap, supplemental material map, new light or spawned effect. The apparent
pressure areas are painted pigment; they do not reveal hidden creatures.
The analytical mesh is already one closed membrane and needs no voxel bake.
The shared bloat and pit-bloat generators, textures, rigs and models are intact.

The profile uses the existing BrogueMonsterProxyBase and generated native clip
table, MODELDEF and ZScript. There are no changes to gameplay, ABI, health, AI,
collision, turns, visibility, RNG, pending-map transition handling or wall mount
code. Existing Brogue death logic also retains its administrative-death and
falling exclusions; the model does not emulate or broaden DF_BLOAT_EXPLOSION.

Runtime IQM SHA-256:
`bc9ee8782d9a8bc18043f370f2fea09c18cb7cd062bc3162bcd90a958ca7d0b3`.

## Verification

Evidence root: `artifacts/creature-queue/BRG-M30/`.

- `python -m unittest tools.monster_models.test_explosive_bloat tools.monster_models.test_bloat tools.monster_models.test_pit_bloat tools.monster_models.test_skeletal tools.test_broguedoom_resources`
  passed 49 tests. This includes closed manifold seams, all-frame centered
  clearance, hover/loop continuity, orange RGB and UV seam equality, distinct
  final deflation, deterministic geometry/IQM/all material bytes and shared
  resource integration. `tools.test_engine_source` separately passed 6 tests.
- Two direct builds have identical IQM, skin and manifest SHA-256 values;
  geometry tuples are identical too (`determinism.json`). There are no omitted
  supplemental material maps. All old bestiary entries and profiles are checked
  separately from the new creature.
- Isolated Blender 5.2.1 rebuilt and reopened
  `assets/monsters/explosive_bloat/explosive-bloat-animated.blend`: seven bones,
  six Actions, packed diffuse, no linked libraries and 18 sampled poses match
  the runtime solver. A second fresh process verifies all 18 poses from the
  saved file and exact packed skin bytes (`blender-fresh-verification.json`).
  See also `blender-verification.json`. The existing extension
  cache permission warning was nonfatal; no global setting was changed.
- Native compilation passed using `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`,
  then the source/build fingerprint was refreshed. The first link attempt ran
  while the early gallery held the executable open and reported LNK1104;
  sequential retry after gallery exit passed (`native-build-retry.log`).
- `powershell -ExecutionPolicy Bypass -File scripts/build-source-bridge.ps1`
  completed regeneration, the 1,854-file public-source audit, all 204 configured
  tests in nine suites, and native engine compilation/fingerprinting. The full
  command **failed** at the subsequent launcher NuGet restore: NU1301, access to
  `api.nuget.org:443` forbidden by the environment. This is not a successful
  full canonical/launcher build. No launcher or network settings were changed;
  final galleries use the successfully compiled native engine.
- Final packaged Vulkan and OpenGL each captured 34 images at 1920x1080:
  preserved static reference, three samples of each clip, front/side/rear views
  and 64/128/192-unit distances. Both complete contact sheets and representative
  full-size before, idle, attack, collapse and distance captures were inspected.
  Each log confirms 34 nonblocking subjects with no new resource/script errors.
  All 1,148 package entries match source bytes; both packages have SHA-256
  `c39dc0e3c8a5fd0c714114247931d678b75441498388414b6cd41d9c4cc5c3cc`.
  See `package-verification.json`, `final-vulkan/` and `final-opengl/`.
  Early engine idle/front/attack/death captures were reviewed before freezing
  the art. Technical review does not substitute for user art approval.

## Preservation

The immediate baseline covers 1,472 files: 1,464 are byte-identical, eight have
intended shared changes, and none are missing (`preservation.json`). All 20 prior
profiles, 67 other bestiary entries and 67 other creature cards are preserved.
The mixed-newline goblin-conjurer card was restored from its immediate raw-byte
backup and its exact SHA checked. Shared changes are the skeletal, monster and
bestiary registries, bestiary traits/report link, K30 card, generated native table,
MODELDEF and ZScript. The generated creature-model index also updates outside
that narrow inventory. No queue, native transition barrier, wall-mount helper,
prior family design or gameplay code was edited. No reset, cleanup, commit or
publication was performed. Review packages remain for coordinator archiving.

## Natural encounter and remaining acceptance

The coordinator's standard ordinary copied-snapshot route searched seeds
1–2000 with 1,500 actions/depth 15 limits and found no kind 30. The pinned
ordinary horde row is nominally depth 10–26; route failure is not proof of
absence. The strongest standard candidate, seed 1849, reached depth 9 before
death. Those search files remain under `encounter-preparation/`.

A distinct bounded attempt selected the 24 deepest-reaching standard-route
seeds and used the existing eight-direction route with ordinary confirmation
retries. It also found no kind 30; seed 1849 reached depth 8 with HP 0 after
401 intents. See `natural-diagonal-search.json` and its log. No health, spawn,
reveal or simulation override was used. Blocked topology, normal death and
insufficient depth remain the obstacles. These are headless negative searches,
not normal renderer encounter proof.

Natural locomotion, attack, damage, death/explosion-event synchronization and
normal dungeon lighting for this creature remain unverified. Gallery fixtures
prove only cosmetic asset presentation. User art approval, physical keyboard
play, standalone side-by-side comparison, controlled frame-time measurement and
full release distribution are also open.

## Reproduction

Run `python -m tools.monster_models.explosive_bloat_animation`, regenerate the
skeletal registry, model bindings and bestiary, preserving unrelated card bytes.
Use the shared background Blender exporter with `-- MK_EXPLOSIVE_BLOAT`.
For the packaged gallery use `python -m tools.monster_models.review_skeletal --symbol MK_EXPLOSIVE_BLOAT --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M30/reproduction-vulkan`.
Use backend 0 and a separate output directory for OpenGL. Keep package evidence
for the coordinator's lossless archive step.
