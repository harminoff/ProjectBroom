# Troll model and animation

Presentation-only BRG-M26 / MK_TROLL. Brogue CE remains authoritative.

## Source facts, art and planned proof

Pinned Brogue describes an enormous disfigured creature covered in phlegm and warts, with misshapen hands, astonishing strength and rapid regeneration. Existing attack verbs are cudgels, clubs, bludgeons, pummels and batters. No wielded club is stated. Regeneration, HP, combat, AI, timing, RNG, visibility and collision remain entirely Brogue-owned; this model adds no healing glow, gas, particles or automatic effect.

Original art interpretation: a broad hunched torso with an uneven shoulder mound, low forward head, swollen asymmetric brow and lower face, flattened nose, small sunken eyes, thick bowed legs, huge unequal palms with bent knobby digits, irregular skin-seated warts and thick dull yellow-green mucus strands at the mouth and chest. Mottled gray-olive skin and wet surface highlights respond only to existing scene lights. These proportions and colors are art choices, not new Brogue facts. Original Project Broom geometry/textures, CC-BY-SA-4.0; no imported art.

Six cosmetic roles: idle, lumber, pummel, batter, recoil and collapse. Only idle/move loop. Planned proof: one closed organic cage, surface-attached warts, normalized weights, grounded support and centered 64-unit bounds; repeated cold deterministic cage/runtime builds; editable background Blender and fresh-open 18-pose checks; scoped regression/native compile/fingerprint; early engine front/attack/death review before frozen final 34-view 1920x1080 packaged Vulkan/OpenGL galleries. Natural encounter and user art approval remain separate open gates.

## Delivered art and motion

Master sources are `tools/monster_models/troll_animation.py` and `troll_materials.py`. Runtime resources are `mod/BrogueDoom/models/monsters/26_troll.iqm` and `graphics/BRGTROLL.png`, with `_N` and `_S` normal/specular maps. Editable source, deterministic connected cage and manifest live in `assets/monsters/troll/`. Static OBJ/skin/Blend references remain unchanged.

The troll has 18 bones, 137 parts, 25,106 runtime vertices and 20,288 triangles. The closed organic cage contains 5,596 triangles. A raised unequal shoulder, broad hunched back, swollen low face, crooked brow, tiny non-emissive eyes and enormous uneven hands distinguish it from the club-bearing ogre. Eight bent fingers and two thumbs remain part of the connected skin. Teeth, short nails, cloth remnants and attached phlegm are separate material surfaces. Ninety-six irregular warts are seated on cage vertices with exactly the supporting normalized weights.

The original 2048-square diffuse atlas uses continuous rest-position mottling and sculpt shading over the fused skin. A flat normal map retains the actual modeled relief; the specular map distinguishes dull skin, warts, eyes and wetter mucus. Native highlights use existing lights only, with no emission, dynamic light, shader, particles, healing animation or gameplay substance. The Blender preview uses packed diffuse and fixed roughness; it does not claim pixel-identical native specular lighting.

Rest dimensions are 28.8988 / 51.2658 / 70.2376 map units. Across every exported frame X stays -17.9334 to 30.9653 and Y -28.3891 to 27.0674. Minimum floor height is 0.29221, maximum height 71.1648. Numerical scale is artistic interpretation; no collision is widened. The lumber gait uses 60% stance / 40% recovery and keeps at least one support foot planted. Both feet remain supported through collapse, with bowed head and limp hands. Final height is 54.6624; this is a deeply slumped crouch, not a prone corpse. All bone scales stay one and automatic floor compensation is zero.

Early tests caught palms touching the thighs in the rest blockout, causing unintended fusion and mixed skin weights, and fingertips below the floor during collapse. The final body moves palms and matching arm endpoints outward, leaving a clear gap, and reduces the collapse drop. One armpit wart still differed from the nearest folded skin when using triangle-average weights; exact supporting cage-vertex weights fix that attachment. Maximum sampled wart-center/support distance is 0.10098 units; the original 2.2-unit regression tolerance was not widened. Initial failed evidence remains as superseded logs.

Coordinator reviewed actual front, attack and final-death captures before freezing this geometry and material. Individual user art approval remains open. Close views retain polygon banding, simplified facial contours and sharply outlined mucus strands; no exhaustive self-intersection proof is claimed.

## Reproduction and technical verification

```powershell
python -m tools.monster_models.troll_animation
python -m tools.monster_models.skeletal_registry
python -m tools.monster_models.generate
python -m tools.monster_models.bestiary
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_TROLL
python -m tools.monster_models.review_skeletal --symbol MK_TROLL --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M26/reproduction-vulkan
```

Use backend 0 and a fresh directory for OpenGL. Before generating cards, preserve their immediate raw bytes and restore unrelated normalization from those backups rather than Git HEAD.

- **55 tests passed in 286.429 seconds**: `python -m unittest tools.monster_models.test_troll tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources` (`tests-final.log`). Six troll tests cover one closed connected cage and equal seams, all limb chains and normalized weights, centered bounds, no automatic floor lift, loop closure, supporting feet, fingers/thumbs and original signature features, seated wart movement, material isolation, no emission and exact IQM/diffuse/supplemental-map bytes.
- Native Release compilation/linking passed with `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4` (`native-build.log`). The subsequent `python tools/engine_source.py --root . --record-build .build/uzdoom/Release` successfully refreshed the fingerprint (`fingerprint.log`). Only the generated K26 clip-table row changes native source; art refinements leave that contract unchanged.
- Two cold single-thread Blender cage bakes and scoped runtime builds reproduce cage, IQM, diffuse, normal, specular and animation manifest byte-for-byte (`determinism.json`). Blender-file byte determinism is not claimed.

- Blender 5.2.1 built and reopened the editable source. A separate fresh process verified 18 poses across six Actions and 18 bones against the runtime solver, maximum vertex error 0.000013981 map units; packed diffuse bytes match exactly and there are no linked libraries (`blender-fresh-verification.json`). The known extension-cache warning is nonfatal. No live document or global settings changed.
- `final-vulkan` and `final-opengl` each contain 34 actual 1920x1080 screenshots: static before, six clips at three samples each, oblique/front/side/rear and 64/128/192-unit distances. Contact sheets and representative full-size front/attack/death/close images were inspected. Every subject reports nonblocking; both launches exit zero. Only existing minimap warnings remain, with no new model/material error. The tall original static reference exceeds the top of the fixed oblique view; the 64-unit close view brings the final feet to the lower image boundary. Other final views show the complete silhouette.
- Both final packages are byte-identical; all 1,163 entries match current source (`package-verification.json`). Coordinator independently verified model, all three textures, bindings and GLDEFS (`parent-package-verification.json`). These are isolated gallery launches, not natural gameplay proof.

| Asset | SHA256 |
| --- | --- |
| IQM | `61f00fec32f3667dcd15e3716c67bf3a1f18457ce69d8db06972ffc2b8702d55` |
| Diffuse | `2327021799ba2086c72c4e85933efeb507c9a07e5413c702d64d4de90592d346` |
| Connected cage | `2cdc5d915794021e834d7d9b5be98a3cf846679f22ac1a65da1ff96fe7f03fdb` |
| Normal | `b528931a799ed8310dd24bf4548b109311f375e9f08880b4be938e388ca9ba4d` |
| Specular | `94cce98c38c1b9a77c7e1c45731f149daedd78fe27730b133f0bca99a77043fd` |
| Final PK3 | `163f3a06595fa85244679ad5ad449dbf0c452bdf642d83ded00f53f2379bdd19` |

## Preservation and remaining gates

The new immediate baseline contains 1,054 files: 1,043 unchanged, 11 intended assigned/shared changes and none missing (`preservation.json`). All 26 prior skeletal profiles, 67 other bestiary/monster entries and unrelated raw-byte creature cards are preserved. The previous GLDEFS bytes remain an exact prefix (`semantic-preservation.json`). Native frontend, wall_mount.h and engine_source.py are byte-identical, preserving wisp direct-visibility restoration, the native visibility probe, pending-level transition barrier and wall placement. Coordinator edits to the shared handoff guide are separate and outside this narrow inventory.

Shared edits are the troll-only connected-skin selector and bestiary traits/report link; skeletal/bestiary/monster registries; generated MODELDEF/ZScript/native table; GLDEFS material; assigned card and generated creature-model-index row. Troll geometry, materials and tests are new local modules. No queue/REVIEW index, gameplay source, ABI, collision, AI, RNG, global settings, cleanup, commit or publication change.

The completed coordinator `visible-census-1-2000.json` observes all first nearby, alive DIRECT kinds during ordinary stairward movement with 1,500-action/depth-15 bounds. Troll kind26 was absent from its recorded kinds. This pass verifies and fingerprints those results (`natural-search-status.json`) rather than repeating the same route. Earlier late-creature searches reached at most depth9; ordinary troll hordes begin at12, with some captive-machine rows beginning at10. These route failures do not prove encounters impossible. No spawn, reveal, health, position or rules override is used to claim natural evidence.

Natural encounter, regeneration observation, hostile locomotion/attack/hit/death, physical input, standalone comparison, controlled performance measurement, exhaustive terrain/self-intersection coverage, full release launcher packaging and individual user art approval remain open. The unrelated NuGet launcher failure and full canonical bridge batch were not rerun; this asset pass uses the authorized scoped regression suites and native build. Brogue retains all gameplay authority.

Reusable lessons: oversized hands need rest-pose clearance from thighs before skin fusion; exact cage-vertex weights provide stable wart seating near folded joints; test every centered bound and raw floor height rather than accepting automatic floor lift; a slumped corpse needs relaxed hands and head, not only reduced height.

## Review package restoration

The coordinator losslessly archived the review packages after acceptance. Restore either final package byte-for-byte with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M26/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding `final-opengl` manifest for the other backend. Screenshots and verification manifests remain directly available.
