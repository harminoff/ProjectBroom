# Vampire bat model and animation

Presentation-only BRG-M14 / MK_VAMPIRE_BAT. Source describes pack-hunting bats with leathery wings and keen senses; flags MONST_FLIES, MONST_FLITS and MA_TRANSFERENCE remain entirely Brogue-owned. Combat.c retains health transfer. No simulation or ABI changes are planned.

Art plan: compact charcoal fur torso, broad cupped ears with tragus folds, short muzzle and paired incisors/fangs, muscular upper arms, long articulated hand digits carrying scalloped leathery wing membranes, hind toes and a short tail. Numerical size, ear shape and warm gray/brown skin colors are artistic choices. One connected organic cage joins torso, head, ears, limbs and membranes; eyes, mouth creases, fangs and claws remain anatomically separate.

Six presentation roles: hovering idle, flight, nip, feeding bite, recoil and grounded folded-wing death. Only idle/flight loop. Feeding is cosmetic and does not assert that a health-transfer event was observed. Proof: source anatomy and closed topology, normalized seamless weights, loop continuity, bounded clips, deterministic cold cage/IQM/skin, fresh Blender reopen and sampled deformation, native compilation, packaged 1920x1080 Vulkan/OpenGL galleries and a bounded natural encounter search. User art approval remains open.

## Delivered model

The final V3 model has 5,974 runtime vertices, 9,404 triangles, 23 runtime parts,
14 bones and six clips. Its single closed organic cage has 2,804 topological
vertices and 5,604 triangles; UV seams share identical positions and weights.
The cage joins the charcoal torso, compact broad muzzle, swept ears, muscular
arms, four long wing digits per side, connected scalloped membranes, hind limbs,
five toes per foot and a short tail. Separate eyes, inner ear cups, mouth seams,
fangs and claws are anatomical details. The broad nose pad and tragi are art
interpretations; Brogue specifies leathery wings and keen senses, not these
numerical measurements or a particular real-world bat species.

Initial renderer review identified overly regular fur marks and a rodent-like
head. Two refinements softened the fur texture, shortened and widened the muzzle,
flattened the nose pad, swept/shortened the ears, and enlarged/darkened the long
digits against the warmer membranes. V3 is the final reviewed revision. Earlier
packages/captures remain evidence of iteration, not final acceptance.

Rest mesh dimensions are 27.0483 / 55.7391 / 15.9853 units, with authored hover
clearance built into the geometry. All sampled poses fit X -16.023..16.153,
Y -31.736..31.750, Z 0.07..36.495. Death settles to the floor while folding the
wings. These dimensions do not change gameplay collision. Only idle and fly loop;
nip, feed and recoil recover; death stays settled. All transforms use unit scale.
The 1024-square original diffuse provides charcoal fur, warm leather and pale
teeth/claws without emission, new lights or imported artwork. New art is
CC-BY-SA-4.0, like the existing original creature assets.

- Masters: `tools/monster_models/vampire_bat_animation.py` and `vampire_bat_materials.py`.
- Editable source: `assets/monsters/vampire_bat/vampire-bat-animated.blend`.
- Connected bake and manifest: `assets/monsters/vampire_bat/`.
- Runtime: `mod/BrogueDoom/models/monsters/14_vampire_bat.iqm`, `graphics/BRGBAT.png`.
- Observer/test: `review_vampire_bat.py` and `test_vampire_bat.py` beside the masters.

## Verification

Evidence root: `artifacts/creature-queue/BRG-M14/`.

1. Release native compilation passed with
   `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
   The generated skeletal table is the sole native-source change. The build
   fingerprint was refreshed only after compilation and subsequently validated.
   Existing wall mounting and the pending-map transition barrier are untouched.
2. **56 tests passed** with
   `python -m unittest tools.monster_models.test_vampire_bat tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
   Tests cover bat digits/toes/signature parts, closed connected skin and seam
   weights, bone coverage, loop/recovery behavior, unit scale, normalized weights,
   flight clearance, corridor bounds, every frame's positive triangle area,
   runtime hashes, roster and resources. An intermediate run correctly caught
   stale generated dimensions/skin hashes after a visual refinement; regeneration
   resolved both failures before the final V3 passing suite.
3. Isolated single-thread Blender 5.2.1 saved and freshly reopened the source,
   verifying six Actions, 14 bones, a packed diffuse and no linked libraries.
   Eighteen sampled source poses agree with runtime deformation within 0.00001
   units. No live document or global preference changed. The known extension
   cache permission warning remains nonfatal.
4. A second cold bake and build reproduced the final connected cage, IQM,
   diffuse and manifest byte for byte (`determinism-v3.json`). Blender document
   byte determinism is not claimed.
5. Final `v3-vulkan/` and `v3-opengl/` packages are byte-identical. Each actual
   engine launch captured 34 nonblocking 1920x1080 views: static before, all six
   clip roles, front/side/rear, and 64/128/192-unit distances. Both contact sheets
   and representative full-resolution images were inspected. IQM, skin, MODELDEF
   and ZScript inside each package exactly match source. Existing menu/minimap
   warnings remain; no new bat model/resource error appeared.
6. Seed-317 startup generation, map compilation and topology/package verification
   passed. No map generation or terrain behavior changed.

```text
IQM  74209dcde269fb146b77b32a856e3271355c6a0eb1c459e2eaa1c32dd5c5f18e
PNG  248bda199a33db347107b8ab05b51da53361cf7888c0fe1ee578b3373fca8749
Cage a4281d3a9b8a9d654783ae06e8b6ff95d2361e0b556aaddb488a7a9d341c16a4
PK3  1281a01644ce5b364af4a3a688e75da96db917c9eb28ca46efd4c88f09c7d68a
```

## Natural encounter scope

The initial bounded seeds 1–100 search found no visible bat. The coordinator
extended that search and found seed 317, depth 5, after 231 ordinary intents.
This is an out-of-depth encounter relative to the nominal 6–13 table; no spawn
rule was changed. Repeated headless routes match hash `7b94665d3beee4fb`.
Bat ID104 is at 26,8, the player at 25,8. The observer stays at the real player
eye and aims only at an already directly visible proxy. It does not move,
spawn or reveal a creature, modify health, or change visibility. Routing may
use copied hidden map knowledge; every submitted intent is validated by Brogue.

One additional E intent makes both sides miss and selects the cosmetic `feed`
variant, hash `8372975ce8582670`. A WAIT produces Brogue's "The vampire bat bites
you" message and selects `nip`, hash `1a4d8730ab05844e`. The copied bat health
changes from 18/18 to 23/18 and player health reaches 8/30. These are unchanged
Brogue results, not frontend health logic. Clip names are cosmetic alternatives:
`feed` is not a claim that that specific missed swing transferred health.
Both final Vulkan and OpenGL processes exited 0 and produced encounter, active
and resolved screenshots. All 233 action/hash pairs (231 route intents plus E
and WAIT) match each other and the intermediate native replay; see
`runtime-verification.json`. Both final natural captures were inspected.
The active/resolved screenshots are taken eight engine tics after the ordinary
follow-up command, while its selected action pose is still playing.

User art approval, manual input acceptance, natural death/hit/recoil coverage,
standalone side-by-side comparison, a controlled frame-time benchmark and a full
release-installer package remain open. Gallery death/recoil poses are verified;
this does not claim exhaustive gameplay parity or a natural death capture.

## Reproduction and preservation

```powershell
python -m tools.monster_models.review_skeletal --symbol MK_VAMPIRE_BAT --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M14/v3-vulkan
python -m tools.monster_models.review_vampire_bat --backend 1 --package artifacts/creature-queue/BRG-M14/v3-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M14/natural-v3-vulkan
```

Use backend 0 and fresh paths for OpenGL. The natural observer expects the
seed-317 startup package generated with the pinned `brogue.exe` exporter,
`tools/mapcompiler/compile.py --startup` and verified with `verify.py --startup`.
It defensively adds missing MAPINFO depth declarations through the existing
helper; geometry remains Brogue-derived. If packages are later archived, restore
their exact archive manifests before replaying.

The 1,086-file immediate baseline retains 1,076 byte-identical files, ten
intended shared-file changes and no missing files.
All 13 prior skeletal profiles and all 67 other bestiary entries remain equal
to the immediate pre-task baseline. The static bat OBJ/skin/Blend references,
other model/texture bytes and native authority paths remain unchanged.
Regeneration normalized the conjurer and totem cards; both were restored from
copies verified against their exact pre-task SHA-256, never from git HEAD.
Shared edits are profile/registry/bestiary/card/index generation, connected-skin
selection and generated MODELDEF/ZScript/native row. No commits, publishing,
queue edits, global cleanup or previous-evidence removal occurred.

[Before/after](../artifacts/creature-queue/BRG-M14/before-after.png),
[Vulkan gallery](../artifacts/creature-queue/BRG-M14/v3-vulkan-contact.jpg),
[OpenGL gallery](../artifacts/creature-queue/BRG-M14/v3-opengl-contact.jpg),
[natural bite](../artifacts/creature-queue/BRG-M14/natural-v3-vulkan/resolved.png).

## Coordinator archive note

All five review gallery PK3s were losslessly archived after review; their `.pk3.archive.json` manifests retain exact original package bytes. Screenshots, logs and source files remain in place. Restore the final package before replay:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M14/v3-vulkan/ProjectBroom-review.pk3.archive.json
```
