# Kraken model and animation

Presentation-only BRG-M39 / `MK_KRAKEN` (kind 39, `BrogueMonsterK39`), authored
in the v2 creature pipeline, phase 1. Brogue CE remains authoritative. This is
a pending profile row (`assets/monsters/skeletal_pending/MK_KRAKEN.json`), not an
integrated or gated model. User art approval is open.

## Source facts and art decisions

Pinned Brogue (`Globals.c`) says: "This tentacled nightmare will emerge from the
subterranean waters to ensnare and devour any creature foolish enough to set
foot into $HISHER lake." It is large; tokens `MA_SEIZES`, `MONST_SUBMERGES`,
`MONST_RESTRICTED_TO_LIQUID`, `MONST_IMMUNE_TO_WATER`, `MONST_FLITS`,
`MONST_FLEES_NEAR_DEATH`, `MONST_NEVER_SLEEPS`; attack verbs "slaps", "smites",
"batters"; eating verb "devouring". Hordes use `DEEP_WATER` and one mud machine.
Glyph colour (100, 55, 55) is an identity cue only.

Art interpretation (not source facts): a squat, rearing cephalopod whose face
looks at the player (+X). Two large golden eyes with horizontal bar pupils,
heavy lids and dark painted rings sit on the front corners of the head, above a
heavy dark parrot beak in a ring of fleshy lips at the centre of the arm crown.
The mottled mantle sits low behind and above the head and leans well back.

It has eight arms and two clubbed feeding tentacles:

- two rising arms flank the face, never crossing it, and curl forward at the tips;
- the two clubs arch up at the flanks;
- six thick, strongly tapering floor arms sprawl and coil in S-curves around the body.

Every arm has a continuous pale sucker band and raised sucker cups. The rising
arms turn their suckers toward the head, so from the front they show dark maroon
backs with a pale inner edge. Sizes, limb count and colours are art choices. The
design is deliberately unlike the bog monster's six pale featureless arms.

Review round 1 (coordinator) found three problems with the first pass:

- It faced the wrong way: the eyes showed only from the side.
- It stood high on thin straight arms, like a stilt-walker.
- Its slap arm read as a straight bar.

This pass turns the face forward and lowers the body from 68 to 50.5 units. The
floor arms are thicker and coil, and the slap arm whips out with a hooked tip.

Seizing, submersion, surfacing, liquid restriction, fleeing, movement, attack
outcomes and visibility are Brogue-owned. There is no collision, AI, RNG,
emission, grabbing logic, bridge, native or ABI change.

## Deep water

`MonsterWorldPosition()` lifts only the eel (kind 4) to the water surface. Every
other visible creature, including this one, stands on the deep bed, 24 units
below an opaque render-only surface. Above that line are the eyes (bottoms at
z 26.7), the upper head, the mantle, both rising arms and both clubs. The beak
and arm crown (about z 14-22) are now below it. As the coordinator directed,
readability at 128 and 192 units in dry and mud views takes priority over how
much shows above the water. No synthetic water fixture was run in this phase.

## Construction

- **Skin:** one connected, closed, voxel-fused skin with 11,014 cage faces
  (`SKIN_FACE_BUDGET = 11000`, `SKIN_VOXEL_SIZE = .2`). It fuses the head, eye
  bulges and lids, buccal mass, eight lip lobes, mantle and ten swept limbs. It
  is painted per triangle from rest positions and a limb-centreline index.
- **Accessories:** these sit in the atlas's top-right quadrant. They are the
  eyeballs, an enlarged upper and lower beak (the lower beak has its own `beak`
  bone) and 347 sucker cups.
- **Cup seating:** each cup sits on the closest skin triangle driven by its own
  limb segment. It takes that triangle's weights interpolated at the closest
  point, keeps the top four influences and quantises them. The neighbouring turn
  of a coiled tip is never used. Cups more than 0.3 from the baked surface
  (buried in the fused root web) are dropped.
- **Rig:** 97 bones: root, head, beak, four mantle bones and ten 9-bone limbs.
  Scales are 1, and weights are quantised to 1e-6 with `math.fsum`.
- **Posing:** a direction-chain solver with per-bone floor support (radius, cup
  and rest-curve sag) and tip steering.
- **Runtime:** 41,083 vertices, 24,168 triangles, rest 54.26 x 53.09 x 50.52 units.

| Role | Clip | Frames | Middle-frame key pose |
| --- | --- | --- | --- |
| idle | `idle` | 40 @20 | rest pose; arms writhe and the mantle breathes |
| walk | `surge` | 32 @35 | rest pose; larger undulation and a body bob |
| attack | `slap` | 25 | the body lunges and the mantle pitches forward. The right arm whips out wide and cracks forward to x 30 with a hooked tip. The left arm is cocked overhead and the clubs flare |
| alt attack | `seize` | 29 | both clubs arch over and clamp in front of the open beak; the rising arms curl in |
| hit | `recoil` | 15 | the body jerks back; arms and clubs are flung up |
| death | `sink` | 37 | the body drops and tips over, the mantle lies back diagonally, and every limb slides into limp floor coils |

All sampled frames stay inside the centred cell: X -31.04..30.68,
Y -27.12..28.13, minimum Z 0.199, with no automatic floor compensation. Idle
frame 0 equals the rest pose.

## Files

- `tools/monster_models/kraken_animation.py` (generator and the tentacle toolkit),
  `kraken_materials.py`, `test_kraken.py`.
- `assets/monsters/kraken/` (`connected-skin.json.gz`, `animation.json`,
  `kraken-animated.blend`).
- `mod/BrogueDoom/models/monsters/39_kraken.iqm`, `mod/BrogueDoom/graphics/BRGKRAK.png`
  (2048 square; names checked for collisions). No shader or GLDEFS snippet.

## Phase-1 evidence

In `artifacts/creature-queue/BRG-M39/`:

- Two cold `--threads 1` cage bakes: `cold-bake-1/2.log` and `.sha256`. Both hashes are
  `7ff240d20b012d3b7ef17ddf4637647d4a6fb7c88bbccf7da8477e43835f41c8`.
- `blender-build.log`: `SKELETAL_SOURCE_OK`, 97 bones, fresh reopen true.
- Previews (`--preview --all-angles --distances`, 1920x1080):
  `preview-vulkan-contact.jpg` and `preview-opengl-contact.jpg`. Each has 27
  distinct images out of 34, and the only duplicates are the expected ones that
  equal the rest pose (`preview-*-distinct.txt`).
- `tests.log`: `python -m unittest tools.monster_models.test_kraken`, 11 tests OK.

## Known limitations

- The beak and arm crown now sit below the 24-unit deep-water surface. A
  surfaced kraken shows only its eyes, head, mantle, rising arms and clubs.
- The beak is dark on dark maroon. At 192 units it reads as a hooked shape rather
  than as detail.
- A few triangles stretch at the arm roots in the seize and death poses.
- This phase has no natural encounter, synthetic water fixture, packaged gallery,
  native build or user art approval.

## Coordinator package archive

The coordinator returned the first delivery (face visible only from the side, a stilt-walking spider stance on thin straight arms, a straight-bar slap) and accepted the forward-facing eyes and beak, squat coiling body and whipping hooked slap. Round B was integrated and gated as pipeline batch `B` with the kraken, phantom, imp, fury, revenant, golem and tentacle horror (`artifacts/creature-queue/batches/B/gate-summary.json`: 118 tests OK, preservation audit with zero unexpected changes). Both final review packages (`0251f56fe4c6ab6b4bc3932db7e23556a749ae907edfdb6a8faec5b77bbb771c`, 1,216 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M39/final-vulkan/ProjectBroom-review.pk3.archive.json
```
