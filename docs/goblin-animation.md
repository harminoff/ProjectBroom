# Goblin model and animation

The latest [Higgsfield Blender refinement](goblin-higgsfield-refinement.md)
adds firmer facial anatomy, chest shaping, revised skin texture and a folded,
tied waist wrap. Its evidence and current hashes are recorded in that report;
the redesign verification below documents the preceding asset revision.

BRG-M08 / MK_GOBLIN now uses an original animated primate carrying a makeshift
stone spear, following the pinned Brogue description. Normal goblin encounters
begin at depth 3; machines, captivity and out-of-depth selection are separate.
The redesigned form uses dirty brown skin, sparse hair, an angular face,
recessed slanted eyes, swept ears and a rough stone spear to distinguish it
from the lizardlike kobold and tailed monkey. A plain ragged waist wrap is an
artistic clothing choice, not armor. No magic, extra organs or attacks were added.
See [source review, research and skill usage](goblin-design-research.md).

The 19-bone rig has idle, walk, thrust, cut, recoil and death clips. The organic
body is one closed connected cage, not detached primitive limbs. UV copies have
identical positions and weights. Eyes, jaw and held equipment remain separate
where appropriate. The spear is parented to the gripping hand; leg posing uses
two-link inverse kinematics. Thrust/cut are cosmetic alternatives and do not
claim to identify the exact attack verb selected by Brogue.

The redesign replaces the stacked monkey muzzle with a continuous craniofacial
surface and recessed sockets. A continuous elliptical chest-to-neck surface
removes the old collar-like ridge. Nine atlas regions separate body, hair,
face, hands, wood, chipped stone, cord, dark details and hide. The longer spear
angles outward for frontal readability, with seven modeled binding loops and
a chipped leaf-shaped stone point. Its death pose turns back along the floor.
This revision's before captures and source backups are in
`artifacts/goblin-redesign/before/`; earlier backups remain untouched.

Rest extents including the spear are 45.6812 x 30.8421 x 39.2134 map units, at
runtime scale 1. These are art choices, not Brogue physical measurements. The
runtime mesh has 6,770 vertices and 10,982 triangles; the body cage has 2,805
topological vertices and 5,606 faces. Original static references remain intact.

## Authority and scope

Presentation only. The shared skeletal registry supplies the existing MODELDEF,
proxy bindings and native clip table. No handwritten species-specific native
logic, simulation source, public ABI, damage, collision, AI, turns or Brogue RNG
changes. `MA_ATTACKS_PENETRATE` and `MA_AVOID_CORRIDORS` remain Brogue-owned.
No front-end spear collision or extra target selection is introduced. Hidden,
sensed, hallucinated and captive state retain the current shared presentation;
a dedicated bound goblin variant is not part of this update.

## Verification — September 13, 2026

- Blender MCP created the rig and reopened its saved file. The clean isolated
  rebuild verified six Actions, packed skin and 18 sampled deformations against
  the runtime solver. Evidence: `artifacts/goblin-animation/`.
- The redesign was built in a new live Blender MCP scene, preserving the
  existing scenes. Fixed front/side/rear views drove additional eye, mouth and
  torso corrections. Additional views: `artifacts/goblin-redesign/`.
- Two cold `blender_skin.py -- goblin` builds produced identical bake bytes.
- `python -m unittest tools.monster_models.test_goblin tools.monster_models.test_skeletal tools.test_broguedoom_resources`
  passed 41 tests, including closed connected skin, seam weights, all limb
  chains, spear attachment throughout the clips, loop continuity, finite poses,
  corridor-width bounds, material UV boundaries, spear visibility, lashings,
  final death-pose floor clearance, shallow eye sockets, closed ear/cloth/stone
  surfaces and deterministic IQM/skin bytes.
- `python -m unittest tools.monster_models.test_creatures` passed another nine
  tests (50 total across the two suites). The additional run found stale goblin
  registry dimensions and a pre-existing static-eel test fixture. Canonical
  regeneration updated only the goblin registry entry, without changing any
  runtime resource bytes. The test now selects an actual static OBJ fixture.
- `python tools/run_native.py cmake --build .build/uzdoom --config Release -j 4`
  passed for the initial goblin integration; this asset-only refinement reuses
  that binary and changes no native code or clip bindings.
- `python -m tools.monster_models.review_skeletal --symbol MK_GOBLIN --backend 1 --all-angles --distances --packaged`
  and backend `0` capture 34 frames each, including old static reference,
  all clips, four angles and 64/128/192-unit distances. Packed model, skin and
  bindings are checked against source. Representative captures were inspected.
  Evidence: `artifacts/skeletal-review/MK_GOBLIN/{vulkan,opengl}/`.
- `python -m tools.monster_models.review_goblin --backend 1` and backend `0`
  replay seed 27 using ordinary bridge intents. After the natural pit-bloat fall
  to depth 3, two existing goblins are visible; ID 53 walks and plays thrust
  following Brogue-resolved attacks. Three ordinary waits after landing are
  replayed in the headless bridge and UZDoom. Repeated headless output and
  runtime final hash agree: `cc14f9d0bbb31e67`. Captures use an observer camera
  at the player's eye, without spawning, moving or revealing enemies. This
  proves a normal movement/attack encounter, not goblin death or all pack tactics.
  Evidence: `artifacts/goblin-encounter/{1,0}/`.

Runtime IQM SHA-256:
`33cdd0973f87f138191b24b4a8dbd8982d35ce26cbc1183ab367341e44128912`.

Diffuse SHA-256:
`fab5e1fb7640583c3a1296ef3c4940e5d43357c693fe0457d6860b21d4d3298f`.

## Remaining acceptance

Individual art approval, physical-input acceptance, standalone comparison,
full release distribution, captive refinement and comparative performance
measurements remain unperformed. A gallery death pose is not proof of every
natural death circumstance or penetrating-attack target combination.

All new mesh, texture and animation content is original Project Broom work
under CC-BY-SA-4.0. Brogue prose retains its upstream license and exact text.
