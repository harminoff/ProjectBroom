# Flame turret model and animation

Presentation-only BRG-M44 / MK_FLAME_TURRET. Brogue CE remains authoritative.

## Source facts and planned proof

Brogue describes the flame turret as "This infernal contraption spits blasts of flame at intruders." Its catalog row (`Globals.c` L1112) gives glyph `G_TURRET`, `lavaForeColor` (20/20/20, a dark grey glyph cue), 40 hit points, 0 defense, 150 accuracy, damage {1, 2, 1}, 100 movement and 250 attack duration, `LAVA_LIGHT`, the single bolt `BOLT_FIRE` and the flag `MONST_TURRET` (immobile, inanimate, attackable through walls). Its strings are "incinerating"/"Incinerating" and the attack verb "pricks". Horde rows are `GlobalsBrogue.c` L791 (ordinary, depths 14-24, spawns in WALL, `HORDE_NO_PERIODIC_SPAWN`) and L884 (machine, 17-24, `TURRET_DORMANT`, `HORDE_MACHINE_TURRET`). The fire bolt, ignition, burning, targeting, dormant activation, light, turn timing, damage, RNG and every outcome remain Brogue-owned. No gameplay, AI, collision, damage, spawn, visibility, light, terrain or bridge ABI change.

Planned art interpretation (written before implementation):

- A heavy wall-mounted furnace mechanism, clearly unlike the timber crossbow of the arrow turret and the round sigil plaque/blue crystal of the spark turret. A tall convex shield-shaped cast-iron backplate carries six hex anchor bolts and a riveted border.
- A riveted soot-black firebox cantilevered from the plate on two iron gusset brackets. Its front is a cast "infernal" furnace mask (an art reading of "infernal", like historical beast-mouthed cannon): angry brow ridges, sunken eye sockets, a snout ridge, curled ribbed horns and a fanged mouth ring from which the nozzle projects.
- A long heat-tempered nozzle (straw/bronze/purple/blue temper bands darkening to a soot-black flared bell mouth), brass bands and radial cooling fins, a hinged mouth damper and a small copper pilot line ending at the lower lip.
- Two banded fuel canisters with valve wheels flank the firebox, feeding it through copper pipes; one carries a pressure dial with a moving needle. A leather bellows with hinged iron boards sits on top of the firebox. Fuel, bellows, dial and ornament are art interpretation, not Brogue facts.
- The only emission is mesh-local, in a dedicated atlas column read by a new GLDEFS material shader: a small pilot flame at the nozzle lip, two ember eye lenses behind half-closed iron eyelids, and an attached nozzle blast tongue that exists only during the attack clips. No world light, particles, projectile, detached geometry, additive whole-body style or persistent effect. The body keeps Normal render style.
- Six roles: `idle` (loop; pilot flame flickers, dial needle trembles, everything structural fixed), `rest` (unused move role, exact rest, loop), `spit` (attack: bellows compress, lids flare open, nozzle recoils and the blast tongue is fully extended at the middle frame), `gout` (alternate: nozzle dips, shorter tongue at the middle frame), `jolt` (hit: firebox knocked back, lids squeeze, damper rattles, pilot gutters) and `extinguish` (death: firebox tears from the plate at the top, nozzle droops, damper slams shut, lids close, bellows slump and every emissive volume collapses to zero area). Only idle/rest loop.

Planned proof:

- fixed backplate, anchors, gussets, canisters and valves in every frame; unit bone scales; at most four quantised normalised influences;
- every frame inside the centred -32..32 X/Y limits; the rear plane defines `wallMountBack`;
- zero projected area for every emissive triangle in the final death frame, and nonzero pilot/eye emission in idle; blast tongue collapsed outside attack clips;
- action recovery to rest, key pose on each action clip's middle frame;
- deterministic IQM, atlas, manifest, shader and GLDEFS bytes across two cold builds;
- fresh Blender 5.2 reopen with 18 sampled poses, packed skin, no linked libraries;
- native compile and fingerprint; packaged Vulkan and OpenGL 34-view 1920x1080 galleries; the established solid-pillar wall fixture on both backends with cardinal and corner approaches;
- preservation audit against the immediate raw-byte baseline.

Natural encounter: the unchanged all-kind 1-2000 census and bounded searches reached at most depth 9, while the ordinary flame turret rows start at depth 14. That search is not repeated; the gate is expected to remain open.

All new art is original Project Broom content under CC-BY-SA-4.0. No third-party artwork is imported.

## Delivered artwork and rendering

The final mechanism has **195 named parts, 13,064 runtime vertices, 18,760 triangles, 33 bones and six clips**. Rest extents are 42.11 / 35.24 / 42.90 map units (X includes the rest pilot flame). Across every frame of every clip the envelope is X -11.0..31.045, Y -17.62..17.62, Z 2.739..46.566. The backplate's rear plane stays at X = -11 in every frame, so `wallMountBack` is 11 and the native mount offset is 32 + 11 + 0.3 = 43.3. These are presentation dimensions, not Brogue collision, size or targeting rules.

The planned single top-hinged damper was replaced during review by twin side shutters; see "Review iterations".

### Construction

- **Fixed mount (root bone, never moves):** a convex shield-shaped cast-iron backplate with a stepped inner panel, 34 border rivets, six hex anchor bolts with washers, two riveted gusset brackets and a support shelf. Two banded fuel canisters carry straps, valve stems and spoked valve wheels, and the left canister has a brass-bezelled pressure dial. Over 4,000 root-only vertices are verified exactly stationary in every frame.
- **Firebox and infernal mask (body bone):** a chamfered riveted firebox with iron straps and side louvres. Its front is a cast heat-blackened bronze furnace mask with:
  - angry brow ridges, a snout crest, cheek bosses and cheek ridges;
  - a fanged mouth ring (eight fangs) around the nozzle;
  - two raised eye ports (bezel rim, soot well, ember lens);
  - two ribbed horns curling up and outward.

  Copper feed pipes from both canisters blend from root to body weights, so they flex rather than tear when the firebox moves.
- **Nozzle (barrel bone):** a lathed barrel with an open soot-black bore and a flared, rolled bell mouth. It has three brass bands, five heat-blued cooling fins and a copper pilot line along the underside ending in a brass pilot jet inside the lower lip. The paint follows a heat-temper gradient toward the mouth: oxidised iron, straw, bronze, purple, blue, then soot.
- **Twin mouth shutters (damper_L/R):** half-disc iron shutters on vertical side hinges, with brass ribs, rivets and pull knobs. At rest they stand open forward and outward, flanking the mouth like jaws; at death they swing shut through the free space in front of the bell. A test maps every shutter vertex into barrel space in every frame and proves it never enters the barrel or bell envelope.
- **Eyelids (lid_L/R):** hinged iron visors. At rest (-80 degrees) they form heavy brow shelves over the upper eye. Spit flares them wide, jolt squints them and death closes them flat.
- **Bellows (bellows bone):** a fixed lower board, a hinged upper board with a brass handle, and an eleven-ring pleated oxblood leather accordion blended between body and bellows by hinge angle.
- **Emission (the only emissive surfaces):**
  - a curled pilot flame (core plus two licks) at the pilot jet;
  - two ember eye lenses with painted vertical slit pupils;
  - a blast plume (core plus seven ragged outward tongues).

  Each sits inside an affine corner cage: 8-corner cages for the pilot and blast, bilinear 4-corner cages for each eye. Weights are Freudenthal simplex weights with at most four influences, quantised to 1e-6. With unit bone scales, moving a cage's corners to one point collapses its volume. Outside the attack clips the blast is collapsed to a point inside the bell mouth; it exists only in `spit` and `gout`. It stays attached to the nozzle and is not a projectile, the Brogue bolt, or a claim about ignition.

### Materials and emission

`tools/monster_models/flame_turret_materials.py` paints an original 1024-square atlas, `mod/BrogueDoom/graphics/BRGFTUR.png`. The lump name was checked against all existing graphics first. Its opaque regions are:
- plate iron, firebox iron, canister iron, dark steel, bolt steel and heat-blued fin iron;
- mask bronze, nozzle temper, brass and copper (with verdigris);
- leather, soot, horn and the dial face.

UZDoom lights models flatly, so each region paints its own shading. The horizontal axis carries the surface pattern. The vertical axis is a top-light ramp from a specular highlight down to occlusion. Each vertex samples that ramp from its rest normal, plus a contact-darkening term near the plate. The rightmost atlas column (u >= 0.875) holds only the flame and ember regions.

The new `mod/BrogueDoom/shaders/flame-turret-fire.fp` is attached by an appended GLDEFS `material "graphics/BRGFTUR.png"` block. It sets `Bright` only for u >= 0.875 and adds a renderer-time brightness flicker to those texels. The actor keeps the ordinary opaque `BrogueMonsterProxyBase` with Normal style: no `additiveFlame` and no RenderStyle. There is no light, particle, trail, projectile or GLDEFS light binding, and the displayed-class visibility restoration is untouched. Blender shows the same threshold as an emission preview; it does not reproduce the engine material pixel-for-pixel.

### Clips

| Role | Clip | Frames / fps | Key pose (middle frame) |
| --- | --- | --- | --- |
| idle | `idle` (loop) | 40 / 20 | Pilot flame sways through its top cage corners and the dial needle trembles; everything structural is exactly at rest |
| move | `rest` (loop) | 20 / 20 | Exact rest; a wall turret has no locomotion |
| attack | `spit` | 24 / 35 | Bellows compressed, lids flared, nozzle recoiled, blast plume fully extended to x ~31 |
| alternate | `gout` | 28 / 35 | Bellows pumped then pressed, nozzle dipped 7 degrees, shorter plume with a trailing puff |
| hit | `jolt` | 14 / 35 | Firebox knocked back 4.5 degrees, lids squinting, shutters rattling, pilot guttering |
| death | `extinguish` | 36 / 35 | Pilot and eyes collapse, lids close, shutters slam, the firebox tears 7 degrees off the plate at the top, the nozzle droops a further 18 degrees, the bellows slump and the needle drops to its stop |

- Only idle/rest loop. Spit, gout and jolt start and end exactly at rest.
- At the final death frame the total emissive area is below 1e-3 square units, versus over 12 in idle. The remainder is weight-quantisation residue, far below one texel. Lids and shutters are exactly closed.
- Every raw pose stays above Z = 2.7, and every exported root transform equals its raw transform (zero automatic floor lift).

### Review iterations

Blender previews and one early packaged Vulkan gallery ([early contact sheet](../artifacts/creature-queue/BRG-M44/early-vulkan-contact.jpg)) drove these corrections:
- **Eye ports:** the first eye sockets sat behind the solid mask plate and never showed. They became raised eye ports with the lenses in front of the plate.
- **Eyelids:** the first half-lidded visor (-58 degrees) hid the eyes from the gameplay camera, so it became a -80 degree brow shelf.
- **Shutters:** a single top-hinged damper flap covered the face and would have swept through the bell while closing. It was replaced by twin side shutters that close through free space.
- **Blast shape:** a twisting blast read as a candy-striped flower, so it became a widening plume with ragged forward tongues.
- **Fins:** they were reduced so the mouth ring and fangs read from the front.
- **Mask paint:** in the early engine gallery the mask read like brown wood. It was repainted as heat-blackened bronze with brighter worn ridges, and the nozzle temper colours were desaturated.

Final art uses only the accepted bytes below.

Residual flaws:
- From the front the nozzle is strongly foreshortened, so the attack plume reads as a spiky orange disc in the mouth. Its shape shows in the side and oblique views.
- The `gout` middle-frame plume is small at gallery distance.
- At 45-degree oblique angles the near shutter hides part of the pilot flame.
- The fangs are too small to read beyond close range.
- Plate and firebox iron are intentionally dark, matching the dark grey glyph, and can merge at 192 units. The eyes, mouth fire and brass bands carry the silhouette there.
- The horns are an ornamental reading of "infernal", not a Brogue fact.

Source and runtime files:
- Editable packed source: `assets/monsters/flame_turret/flame-turret-animated.blend`. It is built by `tools/monster_models/blender_flame_turret.py`, which runs the shared isolated `blender_skeletal.build()` and adds the atlas-local emission preview.
- Master geometry and poses: `tools/monster_models/flame_turret_animation.py`.
- Manifest: `assets/monsters/flame_turret/animation.json`.
- Runtime model: `mod/BrogueDoom/models/monsters/44_flame_turret.iqm`.

The legacy static `44_flame_turret.obj`, `BRGM44.png` and `assets/monsters/sources/44_flame_turret.blend` are byte-identical to baseline and remain the gallery's "before" reference.

## Tests

**76 tests passed in 475.290 seconds** (`artifacts/creature-queue/BRG-M44/tests.log`):

```powershell
python -m unittest tools.monster_models.test_flame_turret tools.monster_models.test_arrow_turret tools.monster_models.test_spark_turret tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources
```

The eleven new flame turret tests cover:
- signature construction and part counts;
- the fixed backplate, supports and canisters in every frame;
- weights: quantised, normalised, at most four influences, with cage bones isolated to their emissive parts;
- exact rest/idle structure, action recovery, loop flags and unit scales;
- an emissive atlas column containing exactly the fire parts;
- fire behaviour: visible idle pilot and eyes, the blast only in attack clips, the middle-frame plume beyond x = 30, and complete extinction at death;
- middle-frame key poses, with lids and shutters closed at death;
- shutters never entering the bell in any frame;
- geometry limits: the -11 rear plane, centred ±32 bounds, Z > 2.5, zero root lift and nondegenerate solid triangles;
- exact IQM and atlas bytes, the shader threshold, a GLDEFS material without a light, the opaque ZScript class, the generated native row with `wallMountBack` 11, and the retained legacy static files;
- a compiled check of the shared `wall_mount.h` selector.

The existing arrow and spark turret suites pass unchanged. They include the wall-mount selector, copied-knowledge and attack-yaw guard tests.

## Frozen-byte verification

Evidence root: `artifacts/creature-queue/BRG-M44/`.

- **Determinism:** two separate fresh-process exports reproduced the IQM, atlas, manifest, shader and GLDEFS byte-for-byte (`determinism.json`). This rigid mechanism has no connected-skin cage. Blend-file byte determinism is not claimed.
- **Blender:** isolated Blender 5.2.1 (`--background --factory-startup`) built and reopened the source (`blender-build.log`, `blender-build-verification.json`). A separate fresh process reopened the saved file and verified (`blender-verification.json`):
  - 33 bones and six Actions;
  - **18 sampled poses**, maximum vertex error **0.00000665 units**;
  - exact packed skin bytes and no linked libraries;
  - the emission preview threshold.

  The known extension-cache warning was nonfatal. No global preferences or live documents were touched.
- **Native:** `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4` passed with exit 0 (`native-build.log`). The generated header row was the only native input change. `python tools/engine_source.py --root . --record-build .build/uzdoom/Release` then recorded the fingerprint, and `validate_build()` passed.
- **Galleries:** packaged Vulkan (backend 1) and OpenGL (backend 0) galleries each captured **34 views at 1920x1080**: the static before model, three samples per role, front/side/rear, and 64/128/192-unit distances.
  - Both contact sheets and the full-size front idle, attack and death frames were inspected.
  - All 34 subjects per renderer log `blocking=0`.
  - Both packages are byte-identical (`071b92e5…`), and all 1,183 entries match source (`package-verification.json`).
  - The logs contain only the existing menu-texture and three minimap script warnings, with no shader, model or resource errors.
- **Wall fixture:** `tools/monster_models/review_flame_turret_wall.py` is the established isolated solid-pillar ART02 fixture with the flame turret's class, 43.3 offset and clips.
  - It compiles the unchanged shared `wall_mount.h` selector for four cardinal and two corner approaches.
  - It spawns the actor, waits two tics, then applies idle, spit frame 12 and extinguish frame 35.
  - Both backends captured **18 nonblocking 1920x1080 views** (`wall-vulkan`, `wall-opengl`).
  - On every face the backplate sits on the unchanged pillar face and the mechanism projects into the open cell; no wall is cut.
  - This is synthetic, not a natural encounter.

```text
IQM 66122cb977bd551b2afccf41c613daa39e949667b01bb31973354c9a62d6d3f5
PNG 0f739ab92dad5aff6c971f67af8c987e99cae1f0f9240310842cf5ed3ad9cc72
PK3 071b92e559ce61aaa97d6717850f178c6e8225b993f23a3ec643aad73ac9c3c6
```

[Final Vulkan gallery](../artifacts/creature-queue/BRG-M44/final-vulkan-contact.jpg), [final OpenGL gallery](../artifacts/creature-queue/BRG-M44/final-opengl-contact.jpg), [Vulkan wall fixture](../artifacts/creature-queue/BRG-M44/wall-vulkan-contact.jpg), [OpenGL wall fixture](../artifacts/creature-queue/BRG-M44/wall-opengl-contact.jpg).

## Remaining acceptance

- **Natural encounter: unresolved** (`natural-encounter-status.json`).
  - The unchanged all-kind 1-2000 census contains no kind 44.
  - The conservative route reached at most depth 9; the ordinary row starts at depth 14 and the dormant machine row at 17.
  - The unchanged search was not repeated, and no health, spawn, reveal or terrain override was used.
  - The wall projection is proven naturally only for the arrow turret (seed 26, depth 6).
- **Not claimed:**
  - natural wall placement of kind 44;
  - synchronisation with a real `BOLT_FIRE` event, dormant activation, or natural hit/death timing;
  - hidden/sensed transitions in a live session;
  - standalone comparison, manual input and controlled frame timing;
  - individual user art approval.

## Reproduction

```powershell
python -m tools.monster_models.flame_turret_animation
python -m tools.monster_models.skeletal_registry
python -m tools.monster_models.generate
python -m tools.monster_models.bestiary
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/monster_models/blender_flame_turret.py -- MK_FLAME_TURRET
python -m tools.monster_models.review_skeletal --symbol MK_FLAME_TURRET --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output <new directory>
python -m tools.monster_models.review_flame_turret_wall --backend 1 --package <that directory>/ProjectBroom-review.pk3 --output <new directory>
```

`bestiary` normalises other creature cards. Afterwards, run `artifacts/creature-queue/BRG-M44/restore-cards.py` to restore them from the immediate baseline.

## Preservation

The immediate raw-byte baseline (`take-baseline.py`) hashes 1,654 files and keeps raw copies of 124 generated or shared files; the script refuses to overwrite an existing baseline. The final audit (`preservation.json`) found **1,644 unchanged, 10 intended changes, 0 unexpected and 0 missing**.

The ten intended changes:
- `assets/monsters/bestiary-index.json` (kind 44 only);
- `assets/monsters/brogue_monster_registry.json` (MK_FLAME_TURRET only);
- `assets/monsters/skeletal_profiles.json` (MK_FLAME_TURRET only; the other 34 profiles are identical);
- `docs/creature-model-index.md` (the kind 44 row only);
- `docs/creatures/44_flame_turret.md`;
- `mod/BrogueDoom/GLDEFS` (append-only);
- `MODELDEF.txt` and `brogue_monsters.zs` (the K44 binding only);
- `skeletal_presentation.generated.h` (the K44 row only);
- `tools/monster_models/bestiary.py` (traits and report link).

Other preservation checks:
- Regeneration normalised ten other cards (09, 10, 11, 18, 20, 21, 27, 28, 29, 35). Each was restored from the immediate raw bytes, never from HEAD, and its SHA-256 matches baseline, so every card keeps its report link.
- These are explicitly verified unchanged: the wall selector, native frontend, engine fingerprint helper and shared wall fixtures; the arrow and spark turret IQMs and skins; the salamander shader; the BRGMON atlas; and every flame turret static reference.
- The bestiary, profile and card files keep their CRLF line endings.
- There were no queue or REVIEW edits, no commits or publishing, and no cleanup of others' files.

New files:
- `tools/monster_models/`: `flame_turret_animation.py`, `flame_turret_materials.py`, `blender_flame_turret.py`, `review_flame_turret_wall.py` and `test_flame_turret.py`;
- `assets/monsters/flame_turret/`: `animation.json` and `flame-turret-animated.blend`;
- `mod/BrogueDoom/models/monsters/44_flame_turret.iqm`, `mod/BrogueDoom/graphics/BRGFTUR.png` and `mod/BrogueDoom/shaders/flame-turret-fire.fp`;
- this report.

Reusable family lessons:
- A solid prism mask hides anything recessed behind its front face; raise ports in front of it.
- A hinged cover larger than its clearance sweeps through the barrel unless it closes through free space. A per-frame barrel-space test catches this.
- Affine corner cages give exact zero-area extinction with unit bone scales, and they also allow attack-only attached fire without extra actors.
- A generic `rings()` builder must triangulate collapsed pole rows; otherwise quad halves become zero-area triangles.

## Coordinator package archive

Both final review packages (`071b92e559ce61aaa97d6717850f178c6e8225b993f23a3ec643aad73ac9c3c6`, 1,183 entries) were independently compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the gallery and wall-fixture captures. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M44/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the equivalent final-opengl manifest for that backend. Captures, logs, manifests and shared content blobs are retained.
