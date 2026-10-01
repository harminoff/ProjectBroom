# Dart turret model and animation

Presentation-only BRG-M38 / MK_DART_TURRET. Brogue CE remains authoritative.

## Source facts and planned proof

Brogue describes the dart turret as "This spring-loaded contraption fires darts that are imbued with a strength-sapping poison." Its catalog row (`Globals.c` L1100-1101) gives glyph `G_TURRET`, `centipedeColor` (75/25/85, a violet glyph cue), 20 hit points, 0 defense, 140 accuracy, damage {1, 2, 1}, 100 movement and 250 attack duration, no light, the single bolt `BOLT_POISON_DART`, the flag `MONST_TURRET` (immobile, inanimate, attackable through walls) and the ability `MA_CAUSES_WEAKNESS`. Its strings are "gazing at"/"Gazing" and the attack verb "pricks". The bolt row (`GlobalsBrogue.c` L87) is "poisoned dart", "fires a dart", "fires strength-sapping darts", glyph `G_WEAPON` in `centipedeColor_Brogue`. Horde rows are `GlobalsBrogue.c` L789 (ordinary, depths 15-22, spawns in WALL, `HORDE_NO_PERIODIC_SPAWN`) and L883 (machine, 15-22, `TURRET_DORMANT`, `HORDE_MACHINE_TURRET`). The dart bolt, poison, weakness, targeting, dormant activation, turn timing, damage, RNG and every outcome remain Brogue-owned. No gameplay, AI, collision, damage, spawn, visibility, light, terrain or bridge ABI change.

Planned art interpretation (written before implementation):

- A compact wall-mounted spring gun, clearly unlike the timber crossbow of the arrow turret, the octagonal sigil plaque and blue crystal of the spark turret, and the bronze furnace mask of the flame turret. Its fixed mount is a diamond (lozenge) blackened-iron plate with a riveted border, four anchor bolts, two forged yoke brackets holding trunnion pins and a braced under-shelf.
- A violet-enamelled launcher (an art reading of the violet glyph and bolt colour, not a literal Brogue material) pivots on the trunnion: a breech block, two guide rods, a sliding steel crosshead with a central striker rod, a short receiver and a short open-topped launching channel ending in a brass muzzle collar.
- Two large exposed polished-steel tension coil springs run from the crosshead to front posts on the channel sides. They are the signature "spring-loaded" feature and change length with real coil spacing: stretched while cocked, contracted after release.
- A visible dart feed: a slatted magazine hopper above the channel shows stacked steel darts with violet-painted poison tips and dark flights; the tips poke out of the front of the hopper as a column of needle points aimed at the viewer. The chamber dart lies in the channel below it.
- Poison is painted and mesh-local only: a violet glass poison vial with a brass collar sits on the hopper and feeds a drip spout above the muzzle, where a small violet bead hangs. No light, particles, emission, shader, projectile or persistent effect; the body keeps Normal render style and the ordinary opaque proxy class.
- A side ratchet wheel with a ticking pawl and a cocking lever that re-cocks the crosshead after release; a small sear under the receiver trips at release.
- Six roles: `idle` (loop; the pawl ticks and the poison bead swells slightly; all structure fixed), `rest` (unused move role, exact rest, loop), `loose` (attack: sear trips, crosshead slams forward, springs contract, the chamber dart is driven so its poisoned tip projects from the muzzle at the middle frame; it then shrinks to a point at the muzzle without translating, re-forms hidden inside the hopper throat and drops into the channel while the lever re-cocks), `snap` (alternate: the launcher dips on its trunnion and makes a shorter release at the middle frame, recovering the same way), `jar` (hit: the launcher is knocked on its trunnion, the springs shudder and the lever rattles) and `jam` (death: the left spring hook breaks free and the spring sags, the launcher droops nose-down on its trunnion, the chamber dart jams crooked half out of the muzzle, the lever flops, the hopper lid springs open). Only idle/rest loop.
- The chamber dart always stays attached to the launcher through an affine corner cage (unit bone scales). It is not a projectile, not the Brogue bolt and not a claim about a hit, poison or weakness.

Planned proof:

- fixed plate, anchors, brackets and trunnion pins in every frame; unit bone scales; at most four quantised normalised influences;
- spring coil length follows the crosshead exactly (blended weights, translation only) and every spring vertex stays attached;
- the chamber dart is inside the channel at rest, projects past the muzzle at the attack middle frame, and never has a large one-frame translation while visible (no streak);
- every frame inside the centred -32..32 X/Y limits; the rear plane defines `wallMountBack`;
- action recovery to rest, key pose on each action clip's middle frame, a visibly broken/jammed death;
- deterministic IQM, atlas and manifest bytes across two cold builds;
- fresh Blender 5.2 reopen with 18 sampled poses, packed skin, no linked libraries;
- native compile and fingerprint; packaged Vulkan and OpenGL 34-view 1920x1080 galleries; the established solid-pillar wall fixture on both backends with cardinal and corner approaches;
- preservation audit against the immediate raw-byte baseline.

Natural encounter: the unchanged all-kind 1-2000 census and bounded searches reached at most depth 9, while the dart turret rows start at depth 15. That search is not repeated; the gate is expected to remain open.

All new art is original Project Broom content under CC-BY-SA-4.0. No third-party artwork is imported.

## Delivered artwork and rendering

The final spring gun has **133 named parts, 9,429 runtime vertices, 13,378 triangles, 24 bones and six clips**. Rest extents are 35.71 / 33.00 / 38.00 map units. Across every frame of every clip the envelope is X -10.0..28.0, Y -16.5..16.5, Z 5.0..43.31. The plate's rear plane stays at X = -10 in every frame, so `wallMountBack` is 10 and the native mount offset is 32 + 10 + 0.3 = 42.3. These are presentation dimensions, not Brogue collision, size or targeting rules.

Deviations from the pre-implementation plan: the drip spout and bead hang at the front of the hopper lid over the uppermost stacked needle, not directly over the muzzle (the muzzle collar occupies that space); the separate sear under the receiver was not built, because the release reads from the crosshead, springs and dart alone.

### Construction

- **Fixed mount (root bone, never moves):** a diamond (lozenge) blackened wrought-iron plate with clipped points, a stepped deep-aubergine enamel panel, border rivets and four hex anchor bolts with washers at its points. Two forged yoke brackets with rivets carry brass trunnion bosses; a braced strut and steel cradle pad sit under the breech. The ratchet pawl rides on a root stud. 2,380 root-only vertices are verified exactly stationary in every frame.
- **Launcher (head bone, pivots only on the trunnion axis):** a violet-enamelled breech block with brass straps, steel trunnion pins, a brass trunnion cap, a 12-tooth brass ratchet wheel and two steel guide rods. A test proves the head origin never leaves the trunnion axis.
- **Crosshead and springs:** a sliding steel crosshead carries the striker rod and brass hook eyes. Two polished-steel tension coil springs (16 turns each, swept wire) run from the hook eyes to channel lugs with knurled brass tension knobs. Spring weights blend linearly from the hook to the fixed front post, so the coils stretch exactly with the crosshead (verified vertex by vertex against the analytic stretch) and remain attached at both ends.
- **Launching channel:** a short open-topped gun-steel U channel with a brass breech ring and a brass muzzle collar carrying a crown of six steel spurs.
- **Visible dart feed:** a slatted hopper with a closed enamel throat, brass corner posts, steel slats and front bars. Three stacked steel darts (brass ferrules, violet-painted barbed heads, dark violet flights) are visible through the slats; their tips project through the front bars, so from the front the hopper reads as a column of needle points above the muzzle. The chamber dart lies in the channel below.
- **Poison (painted and mesh-local only):** a violet glass vial with a brass collar, stopper and wire guard (four ribs and an equator hoop) stands on the hinged hopper lid. A brass drip line runs forward to a spout, where a violet bead hangs. Nothing is emissive; there is no shader, light, particle, projectile or GLDEFS entry, and the actor keeps the ordinary opaque `BrogueMonsterProxyBase` class with Normal style.
- **Cocking lever:** a steel lever with a hardwood grip and brass knob on the outboard trunnion end.
- **Caged parts:** the chamber dart sits in an 8-corner affine cage (parent: head) and the poison bead in an 8-corner cage (parent: lid). Weights are Freudenthal simplex weights with at most four influences, quantised to 1e-6. With unit bone scales the cages let the dart shrink onto its own tip and re-form, and let the bead swell or dry up. No other part uses cage bones.

### Materials

`tools/monster_models/dart_turret_materials.py` paints an original 1024-square atlas, `mod/BrogueDoom/graphics/BRGDTUR.png`. The lump name was checked against all existing mod files before the first write. Its regions are:
- plate iron with plum-brown oxide blooms;
- aubergine panel enamel and chipped plum stove enamel;
- aged brass, dark steel, oiled gun-steel channel and bolt steel;
- polished spring steel;
- dart (steel shaft, brass ferrule, violet poison coating with a ragged dip line) and dark violet flights;
- vial glass (violet liquid, bright meniscus, smoky glass), violet poison bead, hardwood and soot.

UZDoom lights models flatly, so each region paints its own shading. The horizontal axis carries the pattern (for darts and the vial it follows the lathe profile); the vertical axis is a top-light ramp from a specular highlight down to occlusion. Each vertex samples that ramp from its rest normal, plus a contact-darkening term near the plate. The violet enamel and poison are an art reading of Brogue's violet glyph and bolt colour (`centipedeColor`), not literal Brogue materials.

### Clips

| Role | Clip | Frames / fps | Key pose (middle frame) |
| --- | --- | --- | --- |
| idle | `idle` (loop) | 40 / 20 | The pawl clicks over a ratchet tooth twice per loop and the poison bead slowly swells; all structure is exactly at rest |
| move | `rest` (loop) | 20 / 20 | Exact rest; a wall turret has no locomotion |
| attack | `loose` | 24 / 35 | Crosshead released 7.2 units, springs contracted and buzzing, launcher recoiled 2.6 degrees nose-up, chamber dart driven so its poisoned tip stands at x = 28 beyond the muzzle spurs |
| alternate | `snap` | 28 / 35 | Launcher dipped 7.5 degrees on its trunnion, a shorter 5.6-unit release |
| hit | `jar` | 14 / 35 | Launcher knocked 5 degrees on the trunnion, springs shuddering, lever and lid rattling, pawl jumping |
| death | `jam` | 36 / 35 | The left spring's hook tears free and the spring sags, the crosshead jams half-released, the chamber dart jams crooked half out of the muzzle, the launcher droops 24 degrees nose-down, the lever flops forward, the pawl lifts off the ratchet, the lid springs open and the bead dries away |

- Only idle/rest loop. Loose, snap and jar start and end exactly at rest.
- **Dart reload without a streak:** after the key pose the dart shrinks onto its fixed needle tip at the muzzle (it does not translate), stays collapsed for a frame, jumps only while it has zero area, re-forms entirely inside the closed hopper throat out of sight, and then drops 3.1 units into the channel while the lever re-cocks the crosshead. A test checks every consecutive frame pair: a per-frame change above 3.2 units is allowed only for the forward striker stroke along the launch axis, a uniform contraction onto the tip, or a collapsed or hidden dart.
- Every raw pose stays above Z = 5, and every exported root transform equals its raw transform (zero automatic floor lift).

### Review iterations

Early Vulkan galleries ([early contact sheet](../artifacts/creature-queue/BRG-M38/early-vulkan-contact.jpg)) drove these corrections:
- **Enamel and glass saturation:** the first pass read as toy-like magenta. The launcher enamel became aged plum with chips, the panel darker aubergine, and the vial liquid a deeper violet.
- **Springs:** the first spring steel read as white rolls at 64 units. It was darkened with a stronger underside so the coils separate.
- **Vial:** it was reduced and given a brass wire guard, so it reads as a mechanical reservoir rather than a potion bottle.
- **Drip bead:** it was moved forward of the lid's brass rim band, which had hidden it.

Final art uses only the accepted bytes below.

Residual flaws:
- From the front at gameplay height the violet bead sits against the violet lid and is hard to see; the idle bead swell is a very small effect.
- The chamber dart is mostly hidden under the hopper at rest; only its tip shows in the muzzle bore. The attack reads mainly from the springs contracting and the poisoned tip projecting past the spurs, which is strongly foreshortened from the front.
- The breech block, crosshead and hopper are chamfered boxes; the form is mechanical and clean but less sculpted than the flame turret's cast mask.
- The launcher's plum enamel and the panel's aubergine enamel are close in hue; brass trim and bright springs carry the separation at 192 units.
- At death the opened lid hinges at its rear edge while the launcher droops, so the lid can look detached from the hopper front in a single still.
- The drip line, bead and poison-coated tips are an art reading of "imbued with a strength-sapping poison", not a Brogue fact about how darts are poisoned.

Source and runtime files:
- Editable packed source: `assets/monsters/dart_turret/dart-turret-animated.blend`, built by the shared isolated `blender_skeletal.py` (no emission preview is needed).
- Master geometry and poses: `tools/monster_models/dart_turret_animation.py`.
- Manifest: `assets/monsters/dart_turret/animation.json`.
- Runtime model: `mod/BrogueDoom/models/monsters/38_dart_turret.iqm`.

The legacy static `38_dart_turret.obj`, `BRGM38.png` and `assets/monsters/sources/38_dart_turret.blend` are byte-identical to baseline and remain the gallery's "before" reference.

## Tests

**86 tests passed in 512.644 seconds** (`artifacts/creature-queue/BRG-M38/tests.log`):

```powershell
python -m unittest tools.monster_models.test_dart_turret tools.monster_models.test_flame_turret tools.monster_models.test_arrow_turret tools.monster_models.test_spark_turret tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources
```

The ten new dart turret tests cover:
- signature construction and part counts (six muzzle spurs, four anchors, three stacked darts, four chamber-dart flights, 24 bones, six clips);
- the fixed plate, brackets, bosses, strut, pad and pawl stud in every frame, and the launcher origin never leaving the trunnion axis;
- weights: quantised, normalised, at most four influences, with dart and bead cage bones isolated to the chamber dart and the bead;
- exact rest/idle structure (only the pawl and bead move in idle), exact action recovery, loop flags and unit scales;
- springs: at the loose middle frame every coil vertex matches the analytic linear stretch from hook to fixed post, and the front ends stay put;
- the chamber dart: inside the channel at rest, past the muzzle at the loose/snap middle frames, and no reload streak between any consecutive frames;
- middle-frame key poses and a broken death (launcher drooped over 20 degrees, lid open, lever flopped, left hook torn more than 5 units, right hook attached, crooked protruding dart, dried bead);
- geometry limits: the -10 rear plane, centred ±32 bounds, Z > 2.5, zero root lift and nondegenerate solid triangles;
- exact IQM and atlas bytes, no GLDEFS entry, the opaque ZScript class, the generated native row with `wallMountBack` 10, and the retained legacy static files;
- a compiled check of the shared `wall_mount.h` selector.

The existing arrow, spark and flame turret suites pass unchanged, including their wall-mount selector, copied-knowledge and attack-yaw guard tests.

## Frozen-byte verification

Evidence root: `artifacts/creature-queue/BRG-M38/`.

- **Determinism:** two separate fresh-process exports reproduced the IQM, atlas and manifest byte-for-byte (`determinism.json`). This rigid mechanism has no connected-skin cage and needs no shader or GLDEFS entry. Blend-file byte determinism is not claimed.
- **Blender:** isolated Blender 5.2.1 (`--background --factory-startup --disable-autoexec`) built the source with `blender_skeletal.py -- MK_DART_TURRET` and reopened it (`blender-build.log`, `blender-build-verification.json`). A separate fresh process reopened the saved file and verified (`blender-fresh.log`, `blender-verification.json`):
  - 24 bones and six Actions;
  - **18 sampled poses**, maximum vertex error **0.0000100 units**;
  - exact packed skin bytes and no linked libraries.

  No global preferences or live documents were touched.
- **Native:** `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4` passed with exit 0 (`native-build.log`); `brogue_bridge_frontend.cpp` recompiled against the new generated row and `uzdoom.exe` relinked. `python tools/engine_source.py --root . --record-build .build/uzdoom/Release` then recorded the fingerprint (`native-fingerprint.txt`), and `validate_build()` passed. Linking finished before any final capture.
- **Galleries:** packaged Vulkan (backend 1) and OpenGL (backend 0) galleries each captured **34 views at 1920x1080**: the static before model, three samples per role, front/side/rear, and 64/128/192-unit distances.
  - Both contact sheets and the full-size front idle, attack middle frame and final death frame were inspected.
  - All 34 subjects per renderer log `blocking=0`.
  - Both packages are byte-identical (`c6ca013f…`), and all 1,185 entries match source (`package-verification.json`).
  - The logs contain only the existing menu-texture and three minimap script warnings, with no model or resource errors.
- **Wall fixture:** `tools/monster_models/review_dart_turret_wall.py` is the established isolated solid-pillar ART02 fixture (copied from the flame turret) with the dart turret's class, 42.3 offset and clips.
  - It compiles the unchanged shared `wall_mount.h` selector for four cardinal and two corner approaches.
  - It spawns the actor, waits two tics, then applies idle, loose frame 12 and jam frame 35.
  - Both backends captured **18 nonblocking 1920x1080 views** (`wall-vulkan`, `wall-opengl`) from the final package.
  - On every face the diamond plate sits on the unchanged pillar face and the launcher projects into the open cell; no wall is cut. The drooped death pose stays in the open cell.
  - This is synthetic, not a natural encounter.

```text
IQM 4efcba62c3366ee7128faa7888a9109c8a87045e80ddc7eb365ccc2f64f06f40
PNG 158ee1ce759d872a5c13d9acaecadf041e61b3d92a151342fe73f7727fe9787b
PK3 c6ca013f12ca48b212e15b3b033db8a4d1c8dafccb59cfac43ff4e850331e85e
```

[Final Vulkan gallery](../artifacts/creature-queue/BRG-M38/final-vulkan-contact.jpg), [final OpenGL gallery](../artifacts/creature-queue/BRG-M38/final-opengl-contact.jpg), [Vulkan wall fixture](../artifacts/creature-queue/BRG-M38/wall-vulkan-contact.jpg), [OpenGL wall fixture](../artifacts/creature-queue/BRG-M38/wall-opengl-contact.jpg).

## Remaining acceptance

- **Natural encounter: unresolved** (`natural-encounter-status.json`).
  - The unchanged all-kind 1-2000 census contains no kind 38.
  - The conservative route reached at most depth 9; both dart turret rows start at depth 15.
  - The unchanged search was not repeated, and no health, spawn, reveal or terrain override was used.
  - The wall projection is proven naturally only for the arrow turret (seed 26, depth 6).
- **Not claimed:**
  - natural wall placement of kind 38;
  - synchronisation with a real `BOLT_POISON_DART` event, poison or weakness presentation, dormant activation, or natural hit/death timing;
  - hidden/sensed transitions in a live session;
  - standalone comparison, manual input and controlled frame timing;
  - individual user art approval.

## Reproduction

```powershell
python -m tools.monster_models.dart_turret_animation
python -m tools.monster_models.skeletal_registry
python -m tools.monster_models.generate
python -m tools.monster_models.bestiary
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_DART_TURRET
python -m tools.monster_models.review_skeletal --symbol MK_DART_TURRET --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output <new directory>
python -m tools.monster_models.review_dart_turret_wall --backend 1 --package <that directory>/ProjectBroom-review.pk3 --output <new directory>
```

`bestiary` normalises other creature cards. Afterwards, run `artifacts/creature-queue/BRG-M38/restore-cards.py` to restore them from the immediate baseline. `blender_skeletal.py` writes its verification under `artifacts/dart_turret-animation/`; it was moved into the evidence root as `blender-build-verification.json`.

## Preservation

The immediate raw-byte baseline (`take-baseline.py`) hashes 1,664 files and keeps raw copies of 125 generated or shared files; the script refuses to overwrite an existing baseline (a second run was refused). The final audit (`preservation.json`) found **1,655 unchanged, 9 intended changes, 0 unexpected and 0 missing**.

The nine intended changes:
- `assets/monsters/bestiary-index.json` (kind 38 only);
- `assets/monsters/brogue_monster_registry.json` (MK_DART_TURRET only);
- `assets/monsters/skeletal_profiles.json` (MK_DART_TURRET appended; the other 35 profiles are identical);
- `docs/creature-model-index.md` (the kind 38 row only);
- `docs/creatures/38_dart_turret.md`;
- `MODELDEF.txt` and `brogue_monsters.zs` (the K38 binding only);
- `skeletal_presentation.generated.h` (the K38 row only);
- `tools/monster_models/bestiary.py` (traits and report link).

Other preservation checks:
- Regeneration normalised ten other cards (09, 10, 11, 18, 20, 21, 27, 28, 29, 35). Each was restored from the immediate raw bytes, never from HEAD, and its SHA-256 matches baseline, so every card keeps its report link.
- These are explicitly verified unchanged: the wall selector, native frontend, engine fingerprint helper and the shared, spark and flame wall fixtures; the arrow, spark and flame turret IQMs and skins; the flame turret shader and `GLDEFS`; the salamander shader; the BRGMON atlas; and every dart turret static reference.
- The bestiary, profile, registry, card and generated files keep their CRLF line endings.
- There were no queue or REVIEW edits, no commits or publishing, and no cleanup of others' files.

New files:
- `tools/monster_models/`: `dart_turret_animation.py`, `dart_turret_materials.py`, `review_dart_turret_wall.py` and `test_dart_turret.py`;
- `assets/monsters/dart_turret/`: `animation.json` and `dart-turret-animated.blend`;
- `mod/BrogueDoom/models/monsters/38_dart_turret.iqm` and `mod/BrogueDoom/graphics/BRGDTUR.png`;
- this report.

Reusable family lessons:
- A caged prop can "leave" without a streak: shrink it onto its own fixed tip, move it only while it has zero area, and re-form it inside a closed housing. A consecutive-frame test that allows only a forward stroke, a uniform contraction or a hidden jump catches regressions.
- Coil springs between two bones stretch exactly under linear blend weights when the end bone only translates in its parent's frame; test against the analytic stretch.
- A lathe about the Y axis needs a right-handed (along, cos, sin) mapping, and outboard parts on the negative side should use positive profiles, or faces invert.
- Saturated identity colours read as toy-like under flat engine light; desaturate the large enamel masses and keep the brightest value for small accents.

## Coordinator package archive

Both final review packages (`c6ca013f12ca48b212e15b3b033db8a4d1c8dafccb59cfac43ff4e850331e85e`, 1,185 entries) were independently compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review. The coordinator noted that the attack clip changes the gallery silhouette only slightly; Brogue's own bolt presentation carries the shot. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M38/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the equivalent final-opengl manifest for that backend. Captures, logs, manifests and shared content blobs are retained.
