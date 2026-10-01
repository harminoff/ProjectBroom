# Spark turret model and animation

Presentation-only BRG-M22 / MK_SPARK_TURRET. Pinned Brogue describes an electrical contraption with embedded crystals and magical sigils. MONST_TURRET is immobile, inanimate and attackable through walls; BOLT_SPARK, targeting, damage, visibility and turn timing remain entirely Brogue-owned.

Art plan: fixed octagonal dark iron mounting plaque, brass concentric sigil rings, ceramic insulated copper windings, four crystal capacitors and a forward faceted focusing crystal held in articulated prongs. Fine rivets, protective ribs and raised angular runes provide close detail. Blue-white crystals distinguish the electrical identity without painting the entire mechanism blue. Original geometry and diffuse texture are CC-BY-SA-4.0. No imported artwork. Six roles are idle, unused move at rest, discharge, recharge, impact and permanent broken-prong/core sag. All charge motion is cosmetic; no projectile, damage, light, RNG or independent target selection is added.

Proof planned: immobile/fixed wall anchors and move role; rigid mechanical pieces; bounds and unit scales; deterministic repeated IQM/atlas/manifest; isolated editable Blender with eighteen source/runtime samples; native generated-table compile and fingerprint; early actual engine front/attack/death review followed by frozen-art final packaged 34-view 1920x1080 galleries on Vulkan and OpenGL; solid wall fixture at four cardinal and two corner approaches. Reuse existing wallMountBack and guarded mounted yaw unchanged. Natural route searches 1–2000 already failed to reach the ordinary 11–18 depth range (maximum 9); those negative results cannot count as a natural encounter. User art approval remains open.

## Delivered art and animation

The final model has **91 named parts, 6,393 runtime vertices, 10,762 triangles,
six bones and six clips**. Rest dimensions are 33 / 39 / 39 units. Across all
frames its local envelope is X -12..23.187714, Y -19.5..19.5, Z 3.5..42.5.
These are presentation dimensions, not Brogue collision or targeting rules.
The central crystal and three electrodes articulate; the plate, twelve raised
sigils, four wound capacitors, eight anchors and lower braces stay fixed.
Idle and unused move (`rest`) are exactly stationary. `discharge` opens the
prongs and advances the retained crystal; `recharge` settles the mechanism;
`impact` briefly jolts it; `break` leaves its core and prongs permanently sagged.
No cosmetic crystal leaves the asset. Only idle/rest loop; all bones have unit scale.

Masters are `tools/monster_models/spark_turret_animation.py` and
`spark_turret_materials.py`. Editable source is
`assets/monsters/spark_turret/spark-turret-animated.blend`; its manifest is
`assets/monsters/spark_turret/animation.json`. Runtime uses
`mod/BrogueDoom/models/monsters/22_spark_turret.iqm` and
`mod/BrogueDoom/graphics/BRGSPARK.png`. The 1024-square original padded atlas
separates crystal blue, dark iron, worn brass, pale ceramic, sigils, metal edges
and copper. Crystals remain opaque diffuse surfaces and can look flat in frontal
lighting; no additive whole-body material, shader or light was introduced.

## Verification on 2026-09-26

Evidence root: `artifacts/creature-queue/BRG-M22/`.

- **82 tests passed in 226.624 seconds**:
  `python -m unittest tools.monster_models.test_spark_turret tools.monster_models.test_arrow_turret tools.monster_models.test_wisp tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources tools.test_level_transition tools.test_engine_source`.
  They cover signatures, fixed attachments, literal rest, action recovery,
  rigid weights, unit scales, nondegenerate geometry throughout animation,
  centered bounds, exact exports, compiled wall selection, copied-knowledge
  gates, guarded attack yaw and retained transition/fingerprint behavior.
- Native Release compilation passed using
  `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
  After linking, `python tools/engine_source.py --root . --record-build .build/uzdoom/Release`
  refreshed the fingerprint; `validate_build()` subsequently passed.
- Three successive IQM/PNG/manifest builds match byte-for-byte in `determinism.json`.
  A separate background Blender 5.2.1 build saved and reopened the source; a
  fresh second process sampled **18 poses**, maximum vertex error
  **0.000004391 units**, six Actions, one exact packed skin and no linked libraries.
  The known extension-cache warning was nonfatal; global preferences were not changed.
- Final packaged **Vulkan and OpenGL each captured 34 views at 1920x1080**,
  including static before, three samples per role, front/side/rear and 64/128/192
  distances. Contact sheets and representative full frames were inspected.
  All subjects log `blocking=0`; both deterministic packages and their critical
  model/skin/binding entries exactly match source. Only the three existing
  minimap warnings occur; no new model/resource errors were found.
- Separate solid-wall fixtures on both backends each captured **18 views**:
  four cardinal approaches and two corners, each at idle, discharge and final
  break. The fixture uses the same compiled `wall_mount.h` selector and waits
  two tics after Spawn before sampling a clip. With `wallMountBack=12`, the
  native offset is 44.3: the back plane sits 0.3 outside the unchanged wall.
  Both contact sheets and full corner/action/death images show the backing
  attached and the mechanism projecting outside the pillar. This synthetic
  fixture is not a natural encounter.
- The existing isolated ART01 native visibility smoke was rerun on both
  backends: eight rat/wisp transitions each, `failures=0 Brogue_session=0`.
  It verifies the retained native material/visibility regression; it does not
  claim natural spark-turret synchronization. Spark uses the ordinary opaque
  proxy material and introduces no custom material override.

```text
IQM aeafa35822ef9a0887853cd3c6eb01f14db39c782fcc8d492e51e9db15880742
PNG efb6b8f074b47509e36614772cf6d28370b05034b9f0ff18e2d40924cbe2a79e
PK3 113502000283b1450c65b56fde5189aa2438fcf518fa4d516b065a3ef05ca361
```

## Preservation and remaining acceptance

The immediate raw-byte baseline covers 529 files: **521 unchanged, eight intended
registration/binding/card/bestiary files changed, zero missing**. All 24 prior
profiles, 67 unrelated bestiary entries, other cards and existing models/skins/
Blender sources remain unchanged. Five cards normalized by regeneration were
restored from immediate byte backups, never HEAD. `runtime-verification.json`
explicitly hashes the arrow turret IQM/PNG/Blend/manifest, native frontend,
visibility fixture, wall selector and engine fingerprint helper against baseline.
The arrow IQM remains `349d7472b0cb10a2ccca5b11dc390abf44c17cacd20efaaac4eccf7178585834`.
Static spark OBJ/skin/Blend references remain intact. The initial new file
`15_spark_turret.iqm` was a naming-order mistake, moved into this evidence folder;
no arrow asset was overwritten. No queue edits, commits, publishing or cleanup.

Natural encounter, natural attack/death event synchronization, user art approval,
manual input acceptance, standalone comparison, controlled performance timing
and full release-installer packaging remain open. Prior ordinary-intent searches
of seeds 1–2000 found no spark turret; the inspected 501–2000 subset reached at
most depth 9, with 619 dead and 881 alive failed endpoints. Its ordinary and
machine horde ranges are 11–18. Repeating the same route is not further evidence;
no health, spawn, reveal or terrain overrides were used to claim an encounter.
The full launcher/NuGet build was outside this asset-only validation scope.

Shared changes are the skeletal profile, generated native table/MODELDEF/ZScript/
monster registry, bestiary generator/index and this creature card. Native
presentation logic, pending-map barrier, displayed-class visibility defaults,
wall placement and attack-yaw guard are byte-identical to the immediate baseline.

[Final Vulkan gallery](../artifacts/creature-queue/BRG-M22/final-vulkan-contact.jpg),
[final OpenGL gallery](../artifacts/creature-queue/BRG-M22/final-opengl-contact.jpg),
[Vulkan wall poses](../artifacts/creature-queue/BRG-M22/wall-vulkan-contact.jpg),
[OpenGL wall poses](../artifacts/creature-queue/BRG-M22/wall-opengl-contact.jpg).

## Review package archive

Coordinator independently verified model, skin and bindings against both final packages and inspected Vulkan/OpenGL wall fixtures. Review PK3s are losslessly archived with verified SHA256 manifests; captures and logs remain available. Restore with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M22/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding final-opengl manifest for OpenGL.
