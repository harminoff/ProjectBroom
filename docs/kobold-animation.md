# Kobold skeletal implementation and evidence

The later [reptilian skin pass](kobold-skin.md) replaces the initial diffuse
atlas. Hashes and screenshots below describe the original animation delivery.

The kobold now uses an original 24-bone IQM model with idle, walk, two club
attacks, hit reaction and collapse clips. Its lizardlike face, teeth, clawed feet,
segmented tail and gripping hand follow the pinned creature description and
club/bash attack prose. The existing diffuse atlas and static reference remain.
This is presentation-only work; Brogue CE remains authoritative.

The reusable foundation consists of `skeletal.py` (hierarchy, quaternion math,
skinning, chain weights and sampling), `skeletal_registry.py` (validated clip
roles and generated native lookup), the parameterized IQM writer, and
`blender_skeletal.py` (armature/Action generation and independent deformation
checks). The rat now consumes the shared math without changing its IQM bytes.
See [the authoring workflow](skeletal-enemy-workflow.md) for adding another enemy.

Existing snapshot/entity IDs, event cues and visibility handling select the
clips. Native presentation owns the club and corpse visually, never through
Doom attacks, damage or solidity. Walk clips follow the existing five-tic generic
interpolation; the rat's slower special pacing is unchanged. Rapid actions may
retarget a pose before it finishes. Clip durations do not create an input gate.

## Recorded evidence

- Runtime: pinned UZDoom 5.0.0, commit
  `292cf4203ebd3ced951cb67f6819180f588c1d44`.
- Both Vulkan and OpenGL: 19 gallery captures each (static before, and first,
  middle, last frame of all six clips), plus 55 captures each from a normal
  seed-one dungeon encounter. Gallery logs assert every proxy is non-solid.
- The normal encounter uses `N` x3, `W` x25, `N`, `W`, `WAIT` x2,
  `W` x4, `E` x12. All 48 native action results match headless Brogue for
  acceptance, turn, coordinates and normalized hash. Native revisions have
  a constant +1 session-attachment offset. Headless output repeats byte-identically;
  Vulkan and OpenGL action logs are identical. The final hash is
  `69afa7433350e1b6`. The final six east intents are blocked, consuming no turn.
- Kobold entity 10 receives walk, attack, alternate attack, hit and death cues
  from those real Brogue events. The gallery independently covers complete clips;
  fast successive dungeon actions can interrupt them.
- Background Blender 5.2.1 source creation compares sampled evaluated vertices
  with the shared solver, then reopens the saved source and verifies 24 bones,
  six Actions and a packed texture. See `blender-verification.json` in the evidence.
- The new runtime model has 6,959 vertices and 75 parts. Its bind extents are
  approximately 22.49 x 18.82 x 40.65 map units, including the raised club.
  The settled collapse is below 20 units high; all sampled poses stay above
  the floor. These are artistic dimensions, never collision facts.
- Rat IQM remains
  `87512b1684f200d69a64e71697988a5f4f96b7c32852ebb8fd6f14c22b7779b7`.
  Re-encoding both models in the regression suite checks deterministic bytes.

Local captures and logs: `artifacts/skeletal-review/MK_KOBOLD/` and
`artifacts/kobold-animation/`. The contact sheets show sampled frames, not
real-time video. `kobold.pk3` and its repeat are byte-identical mod packages;
OpenGL's real encounter loads that package.

## Limits

Final user art approval, a dense multi-enemy stress benchmark and standalone
side-by-side visual captures remain open. The recorded headless comparison uses
the real Brogue bridge action path; it is not an independent standalone renderer
comparison. This pass retains existing diffuse shading and does not add PBR
materials. No gameplay, bridge ABI, terrain or weapon behavior was changed.
The editable Blender file is checked for structure and deformation, not promised
byte-identical across saves. Original art licensing and provenance are recorded
in [the kobold README](../assets/monsters/kobold/README.md).

## Fixed-scene timing

Single actor, identical ART01 camera at (62,62,35), vsync off, Basic / Enhanced /
Cinematic in that order. Each `bench` sample follows stabilization; no other game
instance runs concurrently. These are lightweight smoke measurements, not a
dense-scene performance guarantee. Engine `All` is its reported render timing;
it is not interchangeable with total frame interval.

| Backend | Model | FPS (B/E/C) | Engine All ms (B/E/C) |
|---|---|---|---|
| Vulkan | before | 980 / 984 / 977 | 0.348 / 0.363 / 0.385 |
| Vulkan | after | 986 / 983 / 982 | 0.345 / 0.37 / 0.37 |
| OpenGL | before | 991 / 984 / 987 | 0.312 / 0.345 / 0.393 |
| OpenGL | after | 988 / 992 / 986 | 0.302 / 0.329 / 0.286 |

The near-1000 FPS ceiling and sample noise prevent a meaningful speedup claim.
Both static and skeletal versions remained responsive in this fixed scene.

## Build and regression gates

`scripts/test.ps1` passed all 143 tests, including the shared skeletal, rat,
creature, bridge, saves, resource, map, interaction and terrain suites. The
300-action seed-one long-run attempt ended naturally at turn 195: killed by a
rat, final normalized hash `36b2a00b6543c40a`. This is not a completed 300-action
survival run. The corrupt-recording tests intentionally emit a playback-panic
message; the test process still reports success.

The source build compiled the native engine and passed its full Quick suite.
Its launcher restore initially hit sandbox network restrictions (`NU1301`);
retrying the existing launcher packaging command with network access succeeded.
The final canonical source build was rerun with `-SkipTests` after the separate
complete test script passed. Build logs retain each distinct gate.

The deterministic mod package SHA-256 is
`654afc11fb0393137694029ae70cb8214e598e930e1f732d32d7719b7a19d4a0`.
The final package is identical to the one used by the captured OpenGL encounter.
The packaged mod was launched in UZDoom; a fresh installer distribution and an
interactive launcher/restored-run walkthrough were not part of this asset pass.

Final build result: `scripts/build-source-bridge.ps1 -SkipTests` completed
successfully, including engine copy, build manifest and self-contained launcher.
Repeated canonical builds also exposed intermittent Windows errors reopening
unchanged weapon MD3s. Their generator now skips writing an identical payload;
all 11 focused weapon tests pass, and the final mod package still matches the
previously tested SHA-256 exactly. No hand or weapon asset bytes changed.
