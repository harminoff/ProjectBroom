# Zombie model and animation

Presentation-only BRG-M25 / MK_ZOMBIE. Brogue CE remains authoritative.

Source describes ritual-created undeath and decaying flesh hanging from bones in shreds. Rot gas, flammability, nausea, hits/bites, health, visibility, movement, AI and turns are existing Brogue behavior. This model adds none of those systems.

Art plan: a broad, asymmetrically wasted torso rather than the wraith's narrow skeletal build; ochre-grey mottled tissue, exposed ivory ribs on one side, a ruptured shoulder and shin, thick dangling red-brown tissue shreds, slack open jaw and uneven teeth, milky eyes, cropped blunt fingers and ragged waist cloth. Geometry and pigment are original Project Broom artwork under CC-BY-SA-4.0. Body anatomy will be fused; torn flaps, exposed bones, eyes, teeth and cloth stay separate for their real material boundaries. Six cosmetic roles are idle, shamble, hit, bite, recoil and collapse. Only idle/shamble loop.

Proof planned: closed connected skin and continuous pigment; flesh-flap attachment and normalized weights; grounded support IK, every-frame centered bounds and no automatic floor compensation; repeated cold cage/runtime builds; background editable Blender and fresh-process eighteen-pose agreement with packed skin; native generated-table build/fingerprint; early real engine front/attack/final-death review followed by frozen-art packaged Vulkan/OpenGL 34-view 1920x1080 galleries. Previous ordinary-intent routes seeds1-2000 reached at most depth9 versus ordinary zombie11-18; do not repeat unchanged routes or substitute injected encounters. User art approval and natural encounter remain open.

## Delivered model and source

The zombie has **70 parts, 21,758 runtime vertices, 14,576 triangles and 18 bones**.
A fused 5,600-triangle body cage carries connected torso, skull, neck, limbs,
hands and feet. Eighteen thick closed tissue ribbons hang from chest, abdomen,
shoulder, face, shin, forearm and back. Five exposed rib arcs, clavicle and limb
bones emerge from dark wound inserts. Seven upper and five lower teeth frame
the visible mouth; the lower jaw has its own bone. Milky eyes, uneven ears,
short blunt fingers and ragged cloth distinguish it from the wraith.

Masters: `tools/monster_models/zombie_animation.py` and `zombie_materials.py`.
Editable source/cage/manifest: `assets/monsters/zombie/`. Runtime:
`mod/BrogueDoom/models/monsters/25_zombie.iqm` and
`mod/BrogueDoom/graphics/BRGZOMB.png`. The original 2048-square diffuse uses
continuous rest-position pigment across the body and separate padded regions
for flesh ribbons, exposed ivory, cavities and cloth. No emission, alpha,
light, particle/gas emitter or custom native material override is introduced.
Original static OBJ, skin and Blender reference remain intact.

Rest extents are 15.005 / 19.9326 / 60.9856 units; the complete animated envelope
is X -14.706497..18.640116, Y -11.483777..12.435673, Z 0.272759..61.258370.
These are art dimensions, never Brogue collision sizes. The grounded two-link
leg solver preserves at least one support foot in shamble and both feet in the
collapse. Every frame needs zero automatic floor correction and unit bone scales.

Clips are idle, shamble, strike, bite, recoil and fall. Only idle/shamble loop.
The jaw articulates during bite, while the final fall bows the torso and head,
lower arms hanging limp in a supported kneel. It is a slumped collapse, not a
prone corpse. Ribbons remain attached to their named bones and add no independent
physics or effects. These cosmetic variants do not claim exact Brogue hit/bite
verb selection. Brogue still supplies every event and authoritative outcome.

## Frozen-art verification

Evidence root: `artifacts/creature-queue/BRG-M25/`. The coordinator inspected
early front, bite and final fall, requested no revisions, and accepted this
technical pass before final proofs. Individual user art approval remains open.
Close polygon banding and the simplified layered wound/ribbon geometry remain
visible; exhaustive self-intersection acceptance is not claimed.

- **70 tests passed in 361.341 seconds** (`tests-final.log`):
  `python -m unittest tools.monster_models.test_zombie tools.monster_models.test_wraith tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources tools.test_level_transition tools.test_engine_source`.
  The five zombie tests cover closed connected anatomy and seams, all limb
  chains, normalized weights, eighteen closed attached tissue strips, exposed
  ribs and eyes, jaw articulation, every-frame centered bounds, zero floor
  correction, support feet, continuous atlas islands and exact runtime bytes.
  The same five passed separately before final proof (26.731 seconds); totals
  overlap and are not presented as 75 unique tests.
- Two isolated single-thread Blender cold cage bakes and runtime exports match
  cage/IQM/diffuse/manifest bytes exactly (`determinism.json`).
- Background Blender 5.2.1 built the editable file. A separate fresh process
  reopened it and verified 18 pose samples across six Actions, 18 bones, one
  exact packed skin and no linked libraries. Maximum vertex error is
  0.000010255 units (`blender-fresh-verification.json`). The known extension-cache
  warning is nonfatal; no live Blender document or global settings were changed.
- Native Release build passed using
  `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
  After linking, `python tools/engine_source.py --root . --record-build .build/uzdoom/Release`
  refreshed the fingerprint, and `validate_build()` passed.
- Packaged Vulkan and OpenGL each captured **34 views at 1920x1080**: static
  before, three samples of all roles, front/side/rear/oblique and 64/128/192-unit
  distances. Both contact sheets and full front/attack/death captures were
  inspected. Both launches exited zero, every subject logged `blocking=0`, and
  only the existing three minimap warnings appeared. No new resource errors.
- Both packages are identical; **all 1,159 archive entries** match current
  source (`package-verification.json`). Galleries prove isolated rendering,
  not a natural encounter or event synchronization.

```text
IQM ed3458e9ad2d1c50390b1516fb1814fee769d605c525d7c4069eeaf51b75b510
PNG a824854e95aa3d577505c1d1c930e84b094d7f12c53516ec3cb4a3649bbe505f
Cage 9a7c2e7395ce2f72d8596dd35c0dcf7af1ba6d5f92eca0e0e9a83f456b0eb55a
PK3 2199b34c291b615e38b2256048355f27cd3c3991ec14f6b54238d3d91bd6aee5
```

## Preservation and remaining gates

Immediate raw-byte baseline: **643 files, 633 exact, ten intended changes,
zero missing**. All 25 prior skeletal profiles, 67 unrelated bestiary and monster
registry entries, prior models/skins/Blender sources/cages and other creature
cards remain unchanged. Five cards normalized by generation were restored from
immediate byte backups, never HEAD. The generated global model index changes
only the assigned zombie row (`model-index.diff`). No queue/coordinator review
file was edited.

Shared changes: the new zombie connected-skin selector, bestiary traits/report
link, skeletal/bestiary/monster registries, generated native table/MODELDEF/
ZScript and assigned card/index row. Native frontend, wall selector, visibility
fixture and engine fingerprint helper remain byte-identical, preserving the
pending-map transition barrier and displayed-class render-style restoration.
No gameplay, ABI, global settings, cleanup, commit or publication changes.

Natural encounter and natural combat/hit/death remain unresolved. Existing
ordinary-intent routes covered seeds1–2000; the inspected 1,500-seed extension
reached maximum depth9, versus the ordinary zombie range11–18, and had 619 dead
and 881 alive failed endpoints. `natural-search-status.json` fingerprints that
source evidence. The unchanged route was not repeated. No injected health,
creature spawn, revelation or altered gameplay is presented as natural proof.

Manual input, standalone side-by-side comparison, controlled frame timing,
exhaustive animation/terrain combinations, release-installer packaging and
individual user art approval remain open. The unrelated NuGet NU1301 launcher
build was outside this asset-only scope.

[Final Vulkan gallery](../artifacts/creature-queue/BRG-M25/final-vulkan-contact.jpg)
and [final OpenGL gallery](../artifacts/creature-queue/BRG-M25/final-opengl-contact.jpg).

## Review package archive

Coordinator independently checked final model, skin and bindings against both packages and inspected the final OpenGL collapse. Review PK3s are losslessly archived with verified SHA256 manifests; captures and logs remain available. Restore with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M25/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding final-opengl manifest for OpenGL.
