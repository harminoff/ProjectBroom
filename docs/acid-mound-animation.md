# Acid mound model and animation

Presentation-only BRG-M16 / MK_ACID_MOUND.

## Source facts and intended proof

Brogue describes an acid mound squelching across the ground and a trail of
hissing goo. Liquefying/Feeding and slimes/douses/drenches are existing prose.
Armor corrosion, weapon corrosion, acid blood, turns and all outcomes remain
source-owned. No trail actor, damage, spawn, RNG, AI or bridge ABI is added.

Art interpretation: a low asymmetrical spreading mass with an off-center folded
shoulder, long rear skirt, shallow collapsed pockets and green acid film over
dark olive gel. The silhouette is flatter and more oblong than the pink jelly;
there are no eyes, mouth or limbs. Six cosmetic roles: idle, squelch, slime,
douse, recoil and collapse. Only idle/move loop. Original CC-BY-SA-4.0 artwork.

Proof planned: connected closed manifold and every-frame surface integrity,
floor/64-unit corridor envelope, normalized deformation and seams, deterministic
IQM/three maps, editable Blender fresh reopen, native table compile, actual
1920x1080 packaged Vulkan/OpenGL clip/angle/distance galleries, and ordinary
seed 26 depth 6 encounter replay with copied-state hashes. User art approval,
manual play and exhaustive corrosion/death coverage remain separate gates.

## Delivered model and verification

The runtime mesh has one closed connected surface, 4,561 vertices, 9,024
triangles, 18 bones and six clips. No remesh bake is needed: deterministic
parameterized geometry carries folds, pockets and skirt in one manifold. Rest
extents are 51.8415 / 38.9553 / 21.8001 units. Every sampled frame fits the
64-unit envelope; X ranges -29.162 to 25.754 and Y -20.636 to 21.586. The floor
contact stays about 0.12 units up; settled collapse height is 2.736 units.
These are art dimensions, never collision or movement authority.

Editable source: `assets/monsters/acid_mound/acid-mound-animated.blend`.
Runtime: `mod/BrogueDoom/models/monsters/16_acid_mound.iqm` with original
1024-square diffuse/specular maps and a flat normal map preserving sculpted
normals. The final v2 skin strengthens olive channels and yellow-green film
after close inspection found the first material too uniformly green. No
emission, fullbright, detached droplets or damaging trail was introduced.

Evidence root: `artifacts/creature-queue/BRG-M16/`.

- **55 tests passed**, final run 98.750 seconds, using
  `python -m unittest tools.monster_models.test_acid_mound tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
  Tests cover connected manifold closure, every-frame triangle orientation,
  floor/corridor bounds, seam equality, loop/recovery, unit-scale normalized
  weights and exact runtime/map bytes. See `tests.log`.
- Native compilation passed with
  `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`;
  the build fingerprint was refreshed after success. Only the generated K16
  presentation row was added to native integration. See `native-compile.log`.
- Background Blender 5.2.1 freshly reopened all six Actions, packed skin and no
  linked libraries. Eighteen sampled poses matched runtime deformation with
  maximum error 0.000003087 units. Existing desktop documents were untouched.
  The known extension-cache warning was nonfatal. Source Blend byte
  determinism is not claimed. See `blender-final.log` and verification JSON.
- Repeated final IQM, diffuse, normal, specular and manifest builds match byte
  for byte (`determinism.json`). Geometry does not depend on a remesh cache.
- Final `v2-vulkan/` and `v2-opengl/` each captured 34 actual engine views at
  1920x1080: static before, all six clips, front/side/rear and 64/128/192-unit
  distances. Both contact sheets and representative full-size images were
  inspected. Each subject reports `blocking=0`. No new model/resource error
  appeared; existing menu/minimap warnings remain. Both packages are identical,
  and IQM/maps/MODELDEF/ZScript/GLDEFS match source (`package-verification.json`).
- Seed26 startup topology/package verification passed:
  `python tools/mapcompiler/verify.py --input generated/seed-26/brogue-dungeon.json --package generated/seed-26/startup/ProjectBroom-seed-26.pk3 --startup`.

```text
IQM 6c88b727f887074d4cb56e8c8c3d166314062820b7d33fb2a99d276214c04d1f
PNG d4a6f13af1c1993788819d0a6603b038edd545e1920eccab323d6647348db296
PK3 520fc40577c0636e2a035b3aa2c676abafe3ddf64e175c9492a6a8a911da03ef
```

## Natural encounter scope

The prepared seed 26 route reaches depth 6 after 323 ordinary intents, player
72,24 and directly visible mound ID96 at 69,23 with 15/15 HP. State hash is
`ab31c1c06bb8a76a`. Additional W and WAIT bring the player to 71,24, with hashes
`565a027c7b6a1a8f` and `1f734c7ddc90a483`. The mound remains at 69,23 with 15 HP;
the player has 8/30 HP after the existing turret shoots. These follow-up events
are not acid-mound attacks. Both original route and full 325-intent headless
replay were repeated with identical output. Diagnostic routing can read copied
hidden map knowledge, but Brogue validates every intent.

Both final Vulkan and OpenGL processes exited 0 and captured encounter, active
and resolved views. All 325 action/acceptance/hash triples match between renderers
and the repeated headless replay (`runtime-verification.json`). Both natural
resolved images were inspected.

The observer stays at the real player eye and aims at an already directly
visible existing proxy. It does not reveal, spawn, reposition or change any
creature or health. Missing depth 6 MAPINFO declarations are added only in its
review overlay; native geometry and simulation remain unchanged. The initial
view is partially obscured by a wall corner; W exposes the whole mound at a
normal dungeon distance. Natural evidence is direct visibility and idle
appearance only. It does not cover mound attack, movement, corrosion, recoil,
acid blood or death; those remain open natural-event cases.

User art approval, manual input/play, standalone side-by-side comparison,
controlled frame-time measurement and full release-installer packaging remain
open. Gallery poses and deterministic runtime PK3s do not close those gates.

## Reproduction and preservation

```powershell
python -m tools.monster_models.acid_mound_animation
python -m tools.monster_models.review_skeletal --symbol MK_ACID_MOUND --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M16/v2-vulkan
python -m tools.monster_models.review_acid_mound --backend 1 --package artifacts/creature-queue/BRG-M16/v2-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M16/natural-v2-vulkan
```

Use backend 0 with fresh output paths for OpenGL. Retain the prepared seed 26
startup package. Coordinator may losslessly archive review PK3s afterward.

The immediate 1,071-file baseline retains 1,061 byte-identical files, ten intended
shared changes and no missing files. All 14 prior skeletal profiles and all 67
other bestiary entries remain equal. All other creature cards were preserved;
conjurer/totem normalization was restored from immediate pre-task copies,
never HEAD. Existing static acid-mound OBJ/skin/Blend references are unchanged.
Shared changes are the new profile/registry/bestiary traits/card/index,
generated native table/MODELDEF/ZScript and dedicated GLDEFS material. No queue,
coordinator, bridge ABI, gameplay, transition-lifetime or wall-mount edits.

Reusable gel-family lesson: keep shared pole controls and canonical angular
wrapping; use broad, creature-specific pigment differences and distinctly
changed mass proportions. Every-frame topology tests catch fold inversion
that a single rest preview cannot. Scene-light specular is not proof of
transparency; this mound deliberately remains opaque.

[Before/after](../artifacts/creature-queue/BRG-M16/before-after.png),
[Vulkan gallery](../artifacts/creature-queue/BRG-M16/v2-vulkan-contact.jpg),
[OpenGL gallery](../artifacts/creature-queue/BRG-M16/v2-opengl-contact.jpg),
[natural view](../artifacts/creature-queue/BRG-M16/natural-v2-vulkan/resolved.png).

## Coordinator archive note

All four gallery PK3s were losslessly archived after acceptance. Their `.pk3.archive.json` manifests preserve exact original package bytes; screenshots and logs remain available. Restore the final package before replay:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M16/v2-vulkan/ProjectBroom-review.pk3.archive.json
```
