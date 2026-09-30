# Centipede model and animation

Presentation-only BRG-M17 / `MK_CENTIPEDE`. Brogue CE remains authoritative.

## Source facts and original art

The pinned description specifies monstrous centipede incisors and venom; the
catalog uses `MA_CAUSES_WEAKNESS` and `DF_GREEN_BLOOD`. Source attack strings are
"pricks" and "stings". See `Globals.c` catalog line 1059 and prose line 1223.
The ordinary horde row in `GlobalsBrogue.c:769` is depth 7–14; it does not forbid
out-of-depth selection. No toxin, damage, weakness, AI, spawn, turn, collision,
RNG or public ABI behavior changed.

Original anatomy comprises a low, continuous closed flexible cuticle beneath
fifteen overlapping violet-brown tergites, narrow copper rims, thirty continuous
articulated leg meshes, longer terminal legs, a broad cephalic shield, paired
three-bone tapering antennae, eight grouped lateral ocelli, thirty spiracles,
small palps and inward-curved forcipules. Colors beyond Brogue's glyph cue,
segment counts, anatomy detail and all dimensions are artistic interpretation.
Separate shell plates, sockets and appendages represent arthropod anatomy.
The body and each leg are closed connected surfaces, tested after UV seam welding;
no external connected-cage bake is needed for these directly authored tubes.

Six roles are `idle`, `scuttle`, `prick`, `sting`, `recoil` and `death`. Only the
first two loop. The two attack variants communicate existing native attack
events, not a claim that the bridge identifies a specific attack verb. Locomotion
uses a traveling leg-phase wave: 65% stance, 35% lifted recovery, at least 18
planted feet distributed along the body. IK compensates cosmetic body motion;
Brogue alone moves the authoritative entity. Death lowers the body and splays
its feet. The source-guided weakness behavior remains entirely in Brogue.

## Delivered assets

- `tools/monster_models/centipede_animation.py` and `centipede_materials.py`.
- `assets/monsters/centipede/centipede-animated.blend` and `animation.json`.
- `mod/BrogueDoom/models/monsters/17_centipede.iqm` plus 1024-square diffuse and
  specular maps, and a flat normal map preserving the sculpted vertex normals.
- 115 bones, six clips, 214 anatomical parts, 17,669 runtime vertices and
  31,530 triangles. The original static OBJ/skin/source remain unchanged.
- Rest dimensions 55.0156 / 25.4424 / 10.4787 map units. All sampled poses remain
  within 56.9586 length / 27.1231 width, below a 64-unit corridor envelope.
  These extents never determine gameplay collision.
- Existing-light chitin sheen, no emissive effect or moving venom particles.

## Verification

Evidence root: `artifacts/creature-queue/BRG-M17/`.

1. Native compile passed with
   `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`;
   build fingerprint refreshed with
   `python tools/engine_source.py --root . --record-build .build/uzdoom/Release`.
   Only the generated K17 presentation-table row changes native integration.
   The pending-map lifetime barrier and wall-mount frontend remain byte-identical
   to the immediate pre-task baseline.
2. **54 tests passed**:
   `python -m unittest tools.monster_models.test_centipede tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
   Five creature tests cover anatomy counts, closed connected body/leg surfaces,
   reachable exact foot targets, distributed support, loop seams, 64-unit bounds,
   death settling, UV isolation and deterministic material bytes. An initial
   low-knee pose failed reach/settle tests; raising the actual knee bend fixed
   the rig without weakening tolerances. The final sampled clips require **zero**
   floor correction; the highest point settles from 10.6383 to 7.9383 units.
3. Isolated background Blender 5.2.1 built and freshly reopened the editable
   source with six Actions, a packed skin and no linked resources. Eighteen
   sampled source/runtime poses agree within 0.000006371 map units. The user's
   live Blender document and global settings were untouched. The extension-cache
   permission warning is nonfatal. See `blender-source/blender-verification.json`.
4. Two independent runtime builds produce byte-identical IQM, diffuse, normal
   and specular maps. No procedural randomness is involved. Blender file bytes
   themselves are not promised deterministic. See `determinism.json`.
5. Actual **Vulkan and OpenGL** launches each captured **34 packaged views** at
   1920×1080: static before, all six roles, front/side/rear and 64/128/192-unit
   distances. All 34 subjects per backend log `blocking=0`. Rear leg chains,
   gait phases, incisors, antennae and the settled death were inspected in the
   captures. Both packages are byte-identical; model, three maps, MODELDEF,
   ZScript and GLDEFS match source. See `package-verification.json` and the
   `vulkan-pose-inspection.png` / `opengl-pose-inspection.png` contact sheets.
6. Seed-1525 depth-1 startup package was generated by the pinned exporter with
   five exported depths, then the existing compiler `--startup` and package/
   topology verifier passed. `missing_depth_mapinfo` declares depths 2–5 only
   in the observer overlay; Brogue/native reconstruction owns actual maps.
7. The prepared seed-1525 route reproduces byte-identical headless output and
   reaches depth 5, player 32,24, living centipede ID76 at 29,27 after **303
   intents / 299 consumed turns**, hash `6b8b00dc21a05674`. Copied state explicitly
   reports **isCaptive=0, isAlly=0, direct=1**. This is a natural hostile
   out-of-nominal-range encounter, not an injected spawn or a captive showcase.
   The first image is partly occluded by a corner. Two attempted southwest
   diagnostic moves were rejected without changing the hash; they are not part
   of the final route. Legal `W S S` moves reach player 31,26, centipede 30,26,
   player HP14 and centipede HP20 at hash `a0c1d7ec113cfcac`. The adjacent image
   clearly shows the animal, with ordinary grass partly covering its middle.
   Existing Brogue text and the HUD show its attack and weakness onset.
8. A further ordinary `W` attacks the centipede: player HP13, centipede HP18,
   hash `9d98854b42ace1e1` after **307 intents / 303 consumed turns**. Native logs
   prove movement, attack and damage event selection. The damage event schedules
   recoil, then the centipede's attack in that same exchange selects `prick`;
   therefore **pure active recoil is not proved in the natural capture**.
   Gallery poses separately prove recoil deformation. An initial four-tic
   screenshot was too early to show updated HUD state; final damage-response
   and settled captures replace that misleading label. The observer reads proxy
   health and direct visibility and only aims a camera from the player's eye;
   it never changes creature placement, health, visibility or simulation.
   Both renderer replays use the same package and match all three hashes.
   The copied-snapshot route may use hidden map knowledge for diagnostic path
   planning; it is not an in-game autopilot. Full logs and five 1920×1080
   screenshots per backend remain under `natural-vulkan/` and `natural-opengl/`.

## Reproduction

```powershell
python -m tools.monster_models.centipede_animation
python -m tools.monster_models.skeletal_registry
python -m tools.monster_models.generate
python -m tools.monster_models.bestiary
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_CENTIPEDE --render
python -m tools.monster_models.review_skeletal --symbol MK_CENTIPEDE --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M17/final-vulkan
python -m tools.monster_models.review_skeletal --symbol MK_CENTIPEDE --backend 0 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M17/final-opengl
python -m tools.monster_models.review_centipede --backend 1 --package artifacts/creature-queue/BRG-M17/final-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M17/natural-vulkan
python -m tools.monster_models.review_centipede --backend 0 --package artifacts/creature-queue/BRG-M17/final-opengl/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M17/natural-opengl
```

The natural runner uses
`generated/seed-1525/startup/ProjectBroom-seed-1525.pk3`, generated by:

```powershell
src/brogue-mapgen/bin/brogue.exe --export-dungeon-json generated/seed-1525/dungeon.json --seed 1525 --depths 5
python tools/mapcompiler/compile.py --input generated/seed-1525/dungeon.json --output generated/seed-1525/startup/ProjectBroom-seed-1525.pk3 --startup
python tools/mapcompiler/verify.py --input generated/seed-1525/dungeon.json --package generated/seed-1525/startup/ProjectBroom-seed-1525.pk3 --startup
```

Preserve immediate pre-task card copies when regenerating: the shared generator
normalizes other hand-refined cards. This pass restores those unrelated card
bytes from its own saved baseline, never from Git HEAD.

## Final hashes and boundaries

```text
IQM 17000596ee0e154fdc4ab25923e3c84367d9129e05b343f56ed465b48fbafa68
PNG 559a7aa023c26545ac05e896e272f4558f5d545cf0a34e7d8a7a55d6c8f16412
PK3 926fa39ab817f1b43ba624aa23a1bb28cc79ab58917791a64582ce723b262859
```

Shared changes: one registry row, generated MODELDEF/ZScript/native-table/index
bindings, centipede-only bestiary traits/report link and a GLDEFS material.
Other bestiary entries, all other creature cards, earlier IQMs and all prior
skeletal profiles are preserved against the saved baseline. No queue or
coordinator files were edited. See `baseline-preservation.json`.

[Actual engine before/after](../artifacts/creature-queue/BRG-M17/before-after.png),
[editable-source studio view](../artifacts/creature-queue/BRG-M17/blender-source/studio-idle-20.png),
and [natural adjacent Vulkan view](../artifacts/creature-queue/BRG-M17/natural-vulkan/adjacent.png)
provide compact review points; full-resolution galleries and logs remain alongside.

Individual user art approval, manual input acceptance, exhaustive encounter/pose
coverage, a controlled frame-time benchmark, standalone comparison and release-
installer packaging remain open. Natural death and the complete weakness
lifecycle are not claimed; weakness onset is visible in the encounter HUD.
Existing menu/minimap texture and signedness
warnings are recorded in engine logs; no new missing centipede resource occurred.
All artwork is original Project Broom work under CC-BY-SA-4.0. No third-party
art was imported; upstream Brogue prose retains its existing license.

## Coordinator archive note

Both final gallery PK3s were losslessly archived after review. Their `.pk3.archive.json` manifests preserve the exact package bytes; screenshots and logs remain. Restore before replaying:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M17/final-vulkan/ProjectBroom-review.pk3.archive.json
```
