# Golem model and animation

Presentation-only BRG-M49 / MK_GOLEM. Brogue CE remains authoritative.

## Source facts, art and planned proof

Pinned Brogue (`Globals.c` catalog and prose) describes a statue animated by ancient, tireless magic. It does not regenerate and attacks with only moderate strength, but its stone form withstands incredible damage before collapsing into rubble. Catalog tokens are `DF_RUBBLE_BLOOD`, `MONST_REFLECT_50` and `MONST_DIES_IF_NEGATED`. The glyph colour is gray (50, 50, 50), the large flag is set, and the source attack verbs are backhands, punches and kicks. Reflection, negation death, non-regeneration, health, dormant-statue and sacrifice machine rows, timing, AI, RNG, visibility and collision all remain Brogue-owned. This model adds no glow, particles, debris actors or collision.

The art is an original interpretation: a top-heavy carved gray statue built from separate, hewn stone masses. It has a forward-leaning wedge chest with pillowed pectoral slabs, boulder pauldrons with stacked caps, a small sunk head carved as a stern statue face (a chamfered cranium, a heavy overhanging brow with a receding forehead, two separated deep-shadow eye sockets painted without glow, a lit wedge nose ridge between them, a lit squared jaw and no drawn mouth), long arms, and huge knuckled fists that hang to knee height. Short, thick pillar legs stand on slab feet. Dark basalt ball joints show in the gaps between segments. Incised, non-emissive glyph bands (waist drum, collar and wrist bands) and chisel rings are decorative carving on an ancient statue, not a stated Brogue fact or power. All dimensions and colours are artistic interpretation. The geometry and textures are original Project Broom work (CC-BY-SA-4.0); no imported art.

There are six cosmetic roles: `idle` (a slow grinding weight shift), `stomp` (a heavy planted gait), `smash` (punches: a double-fist overhead raise at t=0.3 in the windup, then on the middle frame a deep forward-lunging slam with the torso pitched about 42°, knees bent and both fists driven to near floor level at the cell's +X edge), `backhand` (cocked across the chest, then on the middle frame a wide horizontal sweep: right arm out at shoulder height to the side and front, torso twisted about 46°, left shoulder pulled back and the stance widened), `recoil`, and `crumble` (the knees buckle, then the rigid pieces break away and settle on the floor as rubble). Only idle and stomp loop.

## Construction (reusable stone kit)

`tools/monster_models/golem_animation.py` is both the generator and a small kit for later statue creatures (round C guardians):

- `carved_block()`: a rounded box with bevels. It adds deterministic edge chips, pillowed faces and low-frequency hewn-plane displacement so segments read as carved masses rather than boxes. Every quad keeps its own vertices for per-quad painting, and the generator stores painting attributes (local box coordinates, edge proximity, chip depth).
- `stone_core()`: a dark ball joint that fills the gap between rigid segments.
- `layout_islands()`: area-proportional shelf packing of one padded island per quad. It finds the densest texel density that still fits in 2048Â², which is 8.7 px/unit in authoring units.
- `two_bone()` (analytic IK with an explicit bend pole and controlled twist), `frame_from_world()`, `matrix_quat()`, `slerp()` and `settle()`: world-space rigid posing, converted to the shared local frame format with unit bone scales.
- Poses are authored on `A_RIG`. The exported rig and geometry are uniformly scaled by `SCALE = 0.86`, which is exact for rigid pieces, so the whole silhouette fits the fixed gallery camera.

`tools/monster_models/golem_materials.py` paints per pixel from the interpolated rest-space position using numpy. `paint(parts, Palette)` is reusable with another palette. Painting rules:

- use a warm granite/limestone grey that separates from the blue-grey cobblestone walls, and paint strong form light for the engine's flat lighting (lit tops, much darker undersides);
- darken crevices and joints with box-distance occlusion from neighbouring segments, plus floor contact shadow. Head segments take occlusion only from the eye sockets, so the collar and pauldrons don't darken the face;
- add bevel wear highlights, pale fresh fracture inside chips, and grime toward each block's lower end;
- scatter sparse cellular cracks, plus hand-placed hero cracks across the chest and pauldron;
- add granite flecks and vertical weathering streaks;
- carve incised glyph grooves with a lit lower lip, a masonry course groove and eye sockets; tone the toes and feet down into floor grime.

Specular is low: matte stone with slightly polished worn edges. The normal map is flat, like the troll's. GLDEFS uses normal and specular only, with no shader, glow or brightmap.

The kit uses no connected skin: every segment is rigid on one bone (weight 1). This follows the handoff note that articulated stone may be separate where a sculpture plausibly hinges. No cage bake is involved, so there are no cage-bake hashes.

## Delivered assets

- The runtime model is `mod/BrogueDoom/models/monsters/49_golem.iqm`. Its skin is `graphics/BRGGOLEM.png`, with the `_N` and `_S` maps alongside. Before use, all four names were checked for collisions: they are new, and the existing static `49_golem.obj` and `BRGM49.png` are untouched.
- `assets/monsters/golem/` contains `animation.json` and `golem-animated.blend`.
- The pending row is `assets/monsters/skeletal_pending/MK_GOLEM.json` and the pending GLDEFS snippet is `MK_GOLEM.gldefs`.
- The model has 19 bones and 78 parts, with 56,968 vertices and 28,484 triangles.
- Rest dimensions are 25.46 / 50.17 / 71.22 map units.
- Across every exported frame:
  - X stays between -25.22 and 31.49 (smash fists);
  - Y stays between -29.86 (backhand fist) and 27.71;
  - the minimum height is 0.301, above the 0.07 floor-compensation threshold, so no automatic lift occurs;
  - the maximum height is 78.50, at the overhead raise.
- The final crumble frame is at most 25.76 high (rubble on the floor). Pieces stack only by authored heights: the thighs on the feet, the pelvis on the thighs, and the pauldrons leaning on the arms and chest.

## Verification (phase 1)

- Export: `python -m tools.monster_models.golem_animation`. A second export was byte-identical.

  | File | SHA256 |
  | --- | --- |
  | IQM | `85a17e7ef28149646b410bc8f373950c324f22264ad75ca22fea91b522a834ca` |
  | Diffuse | `5df541fa263af17588aa3f32ef0a7a3730f0cbf79a354d385093b14893cdd2ea` |
  | Normal | `b528931a799ed8310dd24bf4548b109311f375e9f08880b4be938e388ca9ba4d` |
  | Specular | `dead04bfff6e0550c778d3319ab3c8e32872733999db646f9632bf1a76735872` |

- Blender 5.2 background build of `blender_skeletal.py -- MK_GOLEM` built and freshly reopened the source. It checked 18 sampled poses; the maximum vertex error is 2.08e-5 units, and the packed skin is present (`artifacts/creature-queue/BRG-M49/blender-build.log`, `blender-verification.json`).
- Previews used `review_skeletal --preview --all-angles --distances --width 1920 --height 1080` on both backends (`preview-vulkan/`, `preview-opengl/`, with the `*-contact.jpg` sheets). Every stage reports nonblocking. The gallery hashes show the only duplicates are the smash/recoil/crumble rest-pose endpoints and the backhand's own first/last frames; no middle key frame is stale. Earlier runs froze partway through (once on Vulkan from stage 10, once on OpenGL from stage 26); the hash check caught both and the reruns were clean.
- `python -m unittest tools.monster_models.test_golem`: 10 tests OK (`tests.log`). They cover:
  - profile via `skeletal_registry.find`;
  - rigid single-bone weights with every bone used, and positive closed-segment volumes;
  - kit determinism;
  - per-frame centred Â±32 clearance with no floor compensation, and loop closure;
  - planted feet;
  - key poses: overhead raise at frame 9; floor slam with forward-lunging head and lowered pelvis on the middle frame; backhand with the fist out to the side, chest twist over 35° and widened planted stance on the middle frame; recoil;
  - floor rubble with the head broken away;
  - non-overlapping islands;
  - a matte, non-emissive GLDEFS block with a fallback to `mod/BrogueDoom/GLDEFS`;
  - exact IQM, diffuse and supplemental bytes, and the painted value range.
- These results are from phase 1 only. The coordinator's gate (integration, packaged galleries, native build and shared suites) has not been run. Natural encounter and user art approval remain open.

## Known limitations

- The fixed oblique gallery camera clips anything above about 72 units, so the overhead raise appears only in the front, side and rear `smash-9` samples. The middle frames are deliberately low and wide instead.
- No debris chips lift during the slam; that would need extra bones and was left out.
- The nose is a simple tapered peg, and the sockets are dark lozenges rather than sculpted orbits. Upside-down rubble pieces show their painted-dark undersides.
- Rubble pieces interpenetrate slightly where they stack; no self-intersection proof is claimed.
- Close views show hard polygonal silhouettes on the smaller blocks and pale toes, Mip-level island bleeding is limited by 2 px padding only.
- Painting takes about 60 s in pure numpy per build, so the tests take about 90 s.

## Coordinator package archive

The coordinator returned the first delivery (attacks indistinguishable from idle at the oblique camera, grey stone melting into grey walls, a cartoon face) and a second head-only pass (a dark featureless block head), then accepted the low lunging floor-slam, wide backhand, warm limestone palette and carved statue face. At gate time action durations were corrected to engine tics (ceil(frames x 35 / 30 fps)). Round B was integrated and gated as pipeline batch `B` with the kraken, phantom, imp, fury, revenant, golem and tentacle horror (`artifacts/creature-queue/batches/B/gate-summary.json`: 118 tests OK, preservation audit with zero unexpected changes). Both final review packages (`0251f56fe4c6ab6b4bc3932db7e23556a749ae907edfdb6a8faec5b77bbb771c`, 1,216 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M49/final-vulkan/ProjectBroom-review.pk3.archive.json
```
