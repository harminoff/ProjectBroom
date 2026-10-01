# Goblin mystic model and animation

BRG-M10 / `MK_GOBLIN_MYSTIC` is a presentation-only family refinement.
Expected appearance: the pinned source explicitly says no weapon, golden
sparkling eyes and shielding magic protecting escorts. The model will retain
the goblin's angular primate face, swept ears, sparse scalp and shoulder fur,
connected body, articulated hands and plain folded waist wrap. Warm grey-brown
fur and a faded blue cloth are art choices. No staff, blade or conjurer sigils.

Six roles use attentive open-hand idle, walking, two unarmed gestures, recoil
and death. Existing copied events select clips; the shared interface does not
identify a shielding cast, so no cosmetic gesture is claimed as synchronized
shielding. Brogue retains all spell outcomes, AI, health, turns and RNG.

Proof planned: two cold connected-skin bakes and deterministic runtime exports;
fresh-open editable Blender source and sampled deformation; family/resource
regressions and native compile; packaged Vulkan/OpenGL galleries at 1920x1080;
seed 27 depth 5 encounter replay with explicit copied captive/ally facts.
User art approval and natural shielding/death remain separate acceptance gates.

## Delivered assets and reproduction

The runtime IQM is `mod/BrogueDoom/models/monsters/10_goblin_mystic.iqm`;
the original 1024-pixel atlas is `graphics/BRGMYST.png`. Editable source,
manifest and cold-baked cage live in `assets/monsters/goblin_mystic/`.
`tools/monster_models/goblin_mystic_animation.py` reuses the family blockout,
materials, skin weighting, two-link leg solver and death pose. It replaces the
spear grip with a mirrored open hand and removes the unused weapon bone.
The dedicated material makes only the golden iris tile fullbright; it adds no
world light, pulses, sigils, particles, shields or summoned geometry.

The rig has 18 bones, 22 mesh parts, 5,754 exported vertices and 9,218 triangles.
Its closed connected cage has 2,805 topological vertices and 5,606 faces.
Rest extents are 11.8644 / 19.342 / 39.2134 map units; these are art dimensions,
not collision bounds. All sampled animation widths stay below one 64-unit cell.
Clips are `idle`, `walk`, `palm`, `sweep`, `recoil`, `death`; only idle/walk loop.

Two isolated Blender 5.2.1 cold bakes (`--threads 1`) and two runtime exports
matched byte-for-byte:

```text
IQM  706e0135f7431fde0d783ae5e6503f8597d101f670be9efe4f6287347fb8923a
PNG  2a2634da77330f031b5876efc8c21b2d92fd6a770fffb3c2f50053d309021082
Cage e3fac2f5393099ad975c9635c53d32efc1163b5eae9ee9f6abc666ea036ee15a
```

Blender source was saved and fresh-opened with six Actions, packed texture and
no linked libraries. Eighteen sampled deformations matched the runtime solver
within 0.000012 units. Blender's pre-existing extension-cache write warning
was nonfatal; no preference or security settings were changed. The Blender
source uses the packed golden diffuse; the eye fullbright behavior is a runtime
material, not a new light in the authoring scene.

## Separate verification gates

- `python -m unittest tools.monster_models.test_goblin_mystic tools.monster_models.test_skeletal tools.test_broguedoom_resources tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.monster_models.test_goblin tools.monster_models.test_goblin_conjurer`
  passed **62 tests**. This includes connected skin, seam weights, loop
  closure, finite poses, material boundaries, all prior resources and six roles.
- `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`
  passed; the build fingerprint was refreshed afterward. Only the generated
  presentation table changes native data. No hand-written native behavior changed.
- `review_skeletal --symbol MK_GOBLIN_MYSTIC --backend 1 --packaged --all-angles --distances --width 1920 --height 1080`
  and backend `0` passed with **34 captures each**. Before, idle, unarmed action,
  rear and distance images were inspected; the gallery reports every subject
  nonblocking. Both deterministic packages hash to
  `069d8badd31d8ff282e7d5727a3f1730525e057fa73bdbc5a69015bf25d65adf`.
  IQM, atlas, shader, GLDEFS and bindings all match the source bytes in both.
  No new resource errors; the three existing UCM parser warnings remain.
- The pinned exporter regenerated seed 27 for 40 depths. Startup compiler and
  verifier passed. The observer adds only missing depth-5 MAPINFO declarations
  through `missing_depth_mapinfo`; no geometry or simulation is overridden.

## Natural captive encounter

`review_goblin_mystic` replays seed **27**, **224 submitted movement intents**,
to depth **5**, player `(8,13)`, mystic **ID105** at `(5,11)`. Repeated headless
route output is identical, ending at hash **`c9e2d2e18b8526d6`**.
`mystic_encounter_state.cpp` independently replays the same intents and checks
copied state: directly visible, alive, **isCaptive=1**, **isAlly=0**
(`bookkeepingFlags=0x400141`, pinned `MB_CAPTIVE` bit 8).

Vulkan and OpenGL packaged natural replays both exited successfully and produced
`encounter.png` and `settled.png` at 1920x1080. Both native logs end with the
same hash as the headless route. Both encounter images were inspected: the
mystic is visible at approximately 231 map units amid the naturally placed
kobolds, with no observer-spawned creature. The HUD shows 220 consumed turns;
224 is the count of submitted intents, not an assertion that all consumed time.

The natural observer remains at the player's eye and aims only at an existing
directly visible mystic. It changes no creature placement, health, status, RNG,
terrain or turns. This proves natural **captive visibility**, not a normal
hostile escort's shielding behavior. No dedicated bound/release variant was
added; the captive uses the shared mystic presentation and terrain context.

Evidence: `artifacts/creature-queue/BRG-M10/`, including native/tests logs,
determinism, source-open verification, package verification, preservation,
`vulkan/`, `opengl/`, `natural-vulkan/` and `natural-opengl/` captures and logs.

## Preservation, licensing and remaining acceptance

All previous 15 skeletal profiles and the other 67 bestiary/registry entries
remain unchanged relative to the immediate task-start baseline. All other
creature cards were restored from that baseline after canonical generation.
Previous IQMs, textures and editable sources are untouched. Static mystic
reference files remain intact. The native transition barrier and wall-mounted
projection are unchanged. No commits, resets, cleaning or publication.

Shared files changed: skeletal profiles; connected-skin family selector and
its regression coverage; bestiary trait generator/index and creature index;
generated MODELDEF, monster proxy definitions, monster registry and native
presentation table; GLDEFS. The remaining source and evidence is mystic-specific.

Original Project Broom mesh, texture, shader and animation are CC-BY-SA-4.0;
upstream Brogue text and notices are preserved. No third-party art imported.

Still open: individual user art approval, physical-input acceptance, dedicated
captivity/release art, natural hostile shielding/attack/death coverage,
standalone side-by-side comparison, comparative frame timing and full player
release distribution. Close-up atlas boundaries inherited from the family
cage remain visible. These review packages are not a full release build.

## Coordinator archive note

Both gallery PK3s were losslessly archived after review. Their `.pk3.archive.json` manifests retain exact original bytes; screenshots and logs remain. Restore before replaying the package:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M10/vulkan/ProjectBroom-review.pk3.archive.json
```
