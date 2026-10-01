# Wraith model and animation

Presentation-only BRG-M24 / MK_WRAITH. Brogue CE remains authoritative.

## Source facts, art and planned proof

Pinned Brogue prose describes an emaciated frame, hollow eye sockets and long bloodstained nails that grope ceaselessly. Its existing verbs are clutches, claws and bites. Its large flag and olive glyph are identity cues, not anatomical measurements. The source has no flight flag: this is a grounded corporeal figure, without a hood, ghost sheet, magical emission or invented power.

Original art will emphasize a drawn narrow abdomen, raised rib cage and clavicles, bony knees and elbows, bald skull with deep black sockets and cheekbones, thin lips and exposed uneven teeth, ten extended stained nails and sinewy hands. Ash-olive skin, old dark red nail stains, proportions and ragged waist covering are artistic decisions. Geometry and textures are original Project Broom work, CC-BY-SA-4.0. Six cosmetic roles are searching idle, shuffling advance, claw rake, clutch/bite, recoil and collapse. Only idle and move loop.

Planned proof: closed connected anatomy, continuous pigment, normalized weights, grounded supports and centered bounds; two cold bakes/runtime builds; isolated background editable Blender source and fresh-open 18-pose verification; scoped regressions/native build/fingerprint; early actual engine art review before final 34-view 1920x1080 packaged Vulkan/OpenGL galleries. The existing ordinary-intent search through seeds 1-2000 found no kind24 encounter; do not repeat unchanged search or substitute synthetic gallery poses for natural behavior.

No gameplay, AI, combat, health, visibility, movement acceptance, RNG, turns, flight, collision or ABI changes. Natural encounter and individual user art approval remain open.

## Delivered source and appearance

Master sources: `tools/monster_models/wraith_animation.py` and `wraith_materials.py`.
Editable source: `assets/monsters/wraith/wraith-animated.blend`; the deterministic connected cage and animation manifest are beside it. Runtime: `mod/BrogueDoom/models/monsters/24_wraith.iqm` and `mod/BrogueDoom/graphics/BRGWRAIT.png`. Static OBJ, original skin and static Blender source remain unchanged.

The model contains 17 bones, 35 parts, 20,047 runtime vertices and 11,464 triangles. The closed fused organic cage has 5,600 triangles. Separate hollow socket interiors, teeth, ten curved nails and ragged waist strips preserve material/anatomical boundaries. Continuous rest-position pigment fills the 2048-square original atlas without source-part color seams. Nothing emits light or uses transparency. Dark red nail coloration represents an artistic victim-blood stain, not a change to Brogue's green-blood token.

Rest dimensions are 18.3375 / 20.1193 / 60.6976 map units. Every sampled animation frame stays within centered X -14.2298 to 22.2379, Y -11.8225 to 13.1413; minimum Z is 0.2984 and maximum Z is 60.9961. These are presentation dimensions, never collision or movement rules. The two-link leg solver keeps at least one support foot on the floor during advance and both feet supported through the collapsed kneel. All bone scales are one and automatic floor compensation is zero.

Six clips are idle, advance, rake, clutch, recoil and fall; only the first two loop. A searching head and arms, small shuffling gait, asymmetric rake and two-handed clutch provide cosmetic interpretations of Brogue's existing verbs. The mouth is visibly toothed; no independent bite damage, target selection, combat, AI, status or turn behavior exists. Death ends in a bowed, limp kneel, not a prone corpse.

Early actual-engine review found the mouth recessed and one death wrist raised. Final art exposes the mouth and uneven teeth, relaxes the hands, curves and tapers the ribs with slight asymmetry, and adds cooler continuous mottling. Coordinator technical art review accepted this frozen version before final proof. Individual user art approval is open. Close polygon banding and simplified facial forms remain visible; exhaustive self-intersection acceptance is not claimed.

## Reproduction and verification

Evidence root: `artifacts/creature-queue/BRG-M24/`. Early and refined galleries are superseded by `final-vulkan` and `final-opengl`.

```powershell
python -m tools.monster_models.wraith_animation
python -m tools.monster_models.skeletal_registry
python -m tools.monster_models.generate
python -m tools.monster_models.bestiary
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_WRAITH
python -m tools.monster_models.review_skeletal --symbol MK_WRAITH --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M24/reproduction-vulkan
```

Use backend 0 and a fresh directory for OpenGL. Before regenerating cards, back up their raw bytes and restore unrelated generator normalization from that immediate backup, not Git HEAD.

- **54 tests passed in 205.495 seconds** (`tests-final.log`): `python -m unittest tools.monster_models.test_wraith tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`. Five wraith tests cover closed connected skin and seams, all limb chains, normalized weights, centered every-frame bounds, zero floor compensation, loop closure, support feet, ten attached nails and hollow sockets, continuous atlas islands and exact runtime bytes.
- Native Release compilation/linking passed: `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4` (`native-build.log`). The subsequent `python tools/engine_source.py --root . --record-build .build/uzdoom/Release` refreshed its fingerprint (`fingerprint.log`). Only the generated K24 table row changes native source; later art refinement leaves that contract unchanged.
- Two cold single-thread Blender cage bakes and scoped runtime builds reproduce cage, IQM, diffuse and manifest byte-for-byte (`determinism.json`). No supplemental maps are used. Blender-file byte determinism is not claimed.
- Background Blender 5.2.1 built the editable source; a separate process freshly opened it and checked 18 poses across six Actions, all 17 bones, exact packed skin bytes and zero linked libraries (`blender-fresh-verification.json`). Maximum vertex error is 0.000009478 map units. The first artifact-local verifier iterated mesh objects alphabetically and falsely mismatched geometry; ordering objects by the actual geometry parts fixes the verifier without changing model bytes. The earlier failed log remains. Blender's extension-cache warning is nonfatal; global settings and live documents were untouched.
- Both final packaged galleries contain 34 actual 1920x1080 captures: original static reference, six clips at three samples each, front/side/rear/oblique and 64/128/192-unit distance views. Contact sheets and representative full-size front, attack, death and close views were inspected. Both backends exited zero with 34 nonblocking actors; only the three existing minimap script warnings appeared. No new model/resource error occurred. These are isolated presentation galleries, not a natural encounter.
- Both final packages are byte-identical and all 1,155 entries match current source (`package-verification.json`). Coordinator independently verified critical entries (`parent-package-verification.json`).

| Asset | SHA256 |
| --- | --- |
| IQM | `254bef00302eff6be24122b640de385d6ad4f71f6620be4af3d9a1a92c7ecb07` |
| Diffuse | `a84b780a452247691b20d524e533e29043a57e76469cb949ff0ad45b962721ea` |
| Connected cage | `a7675df2fe53d8f57932ae61923ebfba07493e0346a65d2ee5fb7769a98f2434` |
| Final PK3 | `33331b3b355eaab064ac58c3de8247ba85392aafba14a10803df3fd4e2fe9c07` |

## Preservation and remaining gates

Immediate baseline: 1,038 files, 1,029 byte-identical, nine intended assigned/shared changes, zero missing (`preservation.json`). All 23 previous skeletal profiles, 67 other bestiary and monster-registry entries, and unrelated creature cards are preserved (`semantic-preservation.json`). Raw-byte card backups preserve mixed line endings. Native frontend, wall_mount.h and engine_source.py remain byte-identical, retaining wisp material visibility restoration and its synthetic probe, the pending-level presentation barrier and wall mounting. No queue/review index, gameplay, bridge ABI, global settings, cleanup, commit or publication change.

Shared changes: the wraith connected-skin selector and bestiary traits/report link; skeletal/bestiary/monster registries; generated MODELDEF/ZScript/native table; assigned creature card and generated model index. Original art and tests are otherwise wraith-local. Reusable lessons: long claws need their own attached geometry; organic rib ridges must overlap the body to stay connected; expose mouth details against the actual skull surface; verify fresh-open mesh order against geometry order; inspect final death wrists rather than assuming lowered height reads as death.

Natural encounter remains unresolved. The already completed standard copied-snapshot ordinary-intent route covered seeds 1-2000. The 1,500-run extension reached at most depth 9, below the wraith's ordinary range beginning at depth 10; 619 runs ended dead and 881 stalled alive. This pass fingerprints and analyzes that existing evidence in `natural-search-status.json`, without repeating unchanged searches. It does not prove encounters impossible. No creature spawn, reveal, health override or modified movement rule is claimed as natural evidence.

Natural combat/hit/death, physical input, standalone side-by-side comparison, controlled frame-time measurements, exhaustive animation/terrain coverage, full release launcher packaging and individual user art approval remain open. The unrelated launcher NuGet NU1301 path and full canonical bridge batch were not rerun; the authorized scope uses model/resource suites plus native compile. Brogue CE remains authoritative for all outcomes.

## Review package archive

Coordinator independently verified the final model, skin and bindings against both packages. The review PK3s are losslessly archived with verified SHA256 manifests; captures and logs remain available. Restore with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M24/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding final-opengl manifest for OpenGL.
