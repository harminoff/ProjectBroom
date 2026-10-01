# Spider model and animation

The coordinator losslessly archived the review packages after verification.
Restore a final package before replaying it:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M21/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding `final-opengl` manifest for OpenGL. All screenshots, logs
and archive segments remain available; restoration reproduces exact bytes.

Presentation-only BRG-M21 / MK_SPIDER. Brogue CE remains authoritative.

Pinned source describes red eyes, projectile webs and deadly poison; the
catalog supplies BOLT_SPIDERWEB and MA_POISONS. Ordinary horde depth is 9–16.
Neither these powers nor spawn rules, damage, collision, turns, RNG or visibility
are changed. The model is an original dark umber spider with eight long articulated
legs, a narrow pedicel connecting a broad abdomen and compact cephalothorax,
eight red ocelli, paired chelicerae/fangs and short pedipalps. Anatomy details,
colors beyond red eyes and dimensions are artistic interpretation.

Six cosmetic roles are idle, scuttle, bite, threaten, recoil and death. No
independent projectile or web effect is spawned. The death pose rolls the body onto its back
and curls the legs inward and upward. Existing native events choose cosmetic attack alternatives;
these do not assert that a specific Brogue verb or spell was identified.

Planned proof: closed connected body and appendage surfaces, eight reachable
IK chains with distributed support, normalized weights, loop closure and every
frame's centered ±32 bounds. Repeat deterministic assets, isolated editable
Blender fresh-open with 18 pose comparisons, native compile, canonical build,
actual packaged 1920×1080 Vulkan/OpenGL galleries and a bounded ordinary-intent
natural search. User art approval, manual input, standalone comparison, frame-time
benchmark and release installer remain separate gates. Original artwork is
CC-BY-SA-4.0; no external assets are imported.


## Delivered artwork and verification

Master modules are `tools/monster_models/spider_animation.py` and
`spider_materials.py`; runtime is `models/monsters/21_spider.iqm` with original
1024-square diffuse/specular maps and a flat normal map. Editable source is
`assets/monsters/spider/spider-animated.blend`, with `animation.json` beside it.
31 bones, 92 anatomical parts, 9,782 runtime vertices and 17,892 triangles.
Rest extents are 44.8453 / 48.4549 / 19.0259 units. All animation frames stay
within X -23.5968 to +24.5223 and Y -25.5888 to +24.2275; the rolling transition
reaches 43.3738 units high. Dimensions are artistic, never collision extents.

One analytically closed cuticle contains abdomen, pedicel and cephalothorax;
each segmented leg is a continuous closed tube. Separate sockets, claws,
chelicerae, fangs, eyes, pedipalps and bristles reflect arthropod anatomy.
This uses no voxel cage; an unnecessary cage bake is not claimed. The eight
IK chains are reachable and maintain at least four distributed planted feet
through the scuttle cycle. Only idle/scuttle loop. Living poses need no root
floor adjustment. The authored death roll explicitly tracks its lowest mesh
surface at 0.1 units; exported frames need no additional automatic floor lift.
This deterministic cosmetic root transform never changes the Brogue cell.

The early lowered death still resembled a living crouch. The final corpse rolls
174 degrees with all eight tarsi above their hips. Coordinator inspected the
revised idle/front, bite, rolled death and 192-unit view before final proof.
Red ocelli remain visible at three cells in the isolated review lighting.
These are diffuse red surfaces with existing-light material highlights, not
emission or new lights. Fine close-up material banding and stylized leg joints
remain visible; no exhaustive self-intersection or user art approval is claimed.

Evidence is `artifacts/creature-queue/BRG-M21/`.

- **54 tests passed in 130.823s**: `python -m unittest tools.monster_models.test_spider tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
  Five spider tests cover signature anatomy, closed manifold body/leg surfaces,
  normalized influences, exact IK targets/support, loop closure, every-frame
  centered bounds, grounded inverted corpse, UV regions and material bytes.
- Native Release compilation passed with `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`; the successful fingerprint was refreshed
  with `python tools/engine_source.py --root . --record-build .build/uzdoom/Release`.
  Integration is the generated K21 presentation-table row only.
- Two cold single-thread background Blender 5.2.1 builds freshly reopened the
  editable file with six Actions, packed skin and zero linked libraries.
  Eighteen source/runtime sample poses agree within 0.000011256 units.
  Existing user documents/settings remain untouched; the extension-cache
  permission warning is nonfatal. Blend-file byte determinism is not claimed.
- Two runtime/material/manifest builds and repeated analytic geometry are
  byte-identical (`determinism.json`). No third-party runtime dependency added.

## Natural encounter and open gates

The separate diagonal route uses copied state to select ordinary bridge intents;
Brogue resolves every action. Searches used seeds 1849, 24, 27 and 501–550, each
bounded at 1500 steps/depth 16. No directly visible spider was reached. Seed 1849
ended depth 8 after 401 intents with HP 0; seed 24 stopped depth 8 after 380 intents
with HP 27; seed 27 stopped depth 7 after 279 intents with HP 13. Full outputs and
`natural-search/results.json` preserve the negative attempt. This differs from
the earlier conservative cardinal search; no identical search was repeated.
No health, spawn, visibility or RNG was overridden. No natural renderer
encounter is claimed, and gallery actors are explicitly synthetic subjects.
Natural hostile locomotion, web casting, poison, hit and death remain open.
Physical keyboard acceptance, standalone side-by-side comparison, controlled
frame-time benchmark, release-installer packaging and user art approval are
also open. No gameplay or public ABI behavior changed.


## Final package and preservation

Canonical `python -m tools.monster_models.skeletal_registry --build` passed.
Both final backends captured **34 actual 1920×1080 views**, including static
before, six roles, front/side/rear, and 64/128/192-unit distances. Both contact
sheets and representative full-size action/death/distance images were inspected.
All 34 subjects per backend log `blocking=0`; engine exit codes are zero. Existing
menu/minimap warnings remain; no missing spider model or material was reported.
Both final PK3s are byte-identical and all **1,146 entries** match source bytes.
Final gallery paths are `final-vulkan/` and `final-opengl/`; early/revised captures
are development evidence. See `package-verification.json`.

```text
IQM b826971c5ea0a278b73bf752796d8a57c838d567ea3e8526c4994fa48635e004
PNG 2b42814b507054cb702de810335271deea786bf70ee6cddfd653466aec354691
PK3 0088c1808e63bd474d01a518b485a926cd5ee6db7579f821caf2544c644a38bf
```

The immediate narrow inventory has 1,348 files: 1,341 unchanged, seven intended
shared changes and zero missing. All 19 prior skeletal profiles, all 67 other
bestiary entries and all 67 other creature cards remain intact. Cards were
restored from immediate byte copies, including mixed-newline goblin conjurer.
The native frontend/pending-map barrier and `wall_mount.h` are unchanged.
The generated native table also adds only K21, outside that narrow inventory.
Shared edits are the skeletal/bestiary/monster registries, K21 card, bestiary
trait generator, MODELDEF, ZScript, native table and GLDEFS. No queue changes,
reset, clean, commit or publication occurred. Prior static spider assets remain.

Reproduce gallery checks with:

```powershell
python -m tools.monster_models.review_skeletal --symbol MK_SPIDER --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M21/reproduction-vulkan
```

Use backend 0 and a fresh output directory for OpenGL. The coordinator owns
package archival and the next sequential creature; this agent stops here.
