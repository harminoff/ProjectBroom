# Tentacle horror model and animation

Presentation-only BRG-M48 / `MK_TENTACLE_HORROR` (kind 48, `BrogueMonsterK48`),
authored in the v2 creature pipeline, phase 1. Brogue CE remains authoritative.
This is a pending profile row, not an integrated or gated model. User art
approval is open.

## Source facts and art decisions

Pinned Brogue (`Globals.c`): "This seething, towering nightmare of fleshy
tentacles slinks through the bowels of the world. The tentacle horror's
incredible strength and regeneration make $HIMHER one of the most fearsome
creatures of the dungeon." It is large and bleeds purple (`DF_PURPLE_BLOOD`);
its verbs are "slaps", "batters", "crushes", "sucking on" and "Consuming".
Glyph colour (75, 25, 85) is an identity cue only. Strength and regeneration
are Brogue-owned and have no visual effect here.

Art interpretation (not source facts): a land-based tower, deliberately not a
recoloured kraken. It is vertical and purple, and it has no mantle, eyes or beak.

- **Trunk:** four thick tentacles braided into a twisting column.
- **Crown:** eyeless and knotted, with a round sucking maw ringed by 23 pale
  hooks (drawn from the source's "sucking on" verb).
- **Crown tentacles:** nine, of clearly different length, thickness and curl.
  Some writhe forward over the maw, some droop down the back, and one towers.
- **Other limbs:** four heavy mid-trunk arms, four hanging curls, seven splayed
  root tentacles and four thin tendrils.
- **Flesh:** deep bruised aubergine with raised magenta veins set in dark vein
  beds, plus pores and wrinkles. Braid grooves and roots are near-black. A wet
  sheen appears only on upward-facing surfaces, and the sucker undersides are raw pink.

Review round 1 (coordinator) found three problems with the first pass:

- The symmetric crown read as bunny ears at 128 and 192 units.
- The flesh read as glossy toy purple.
- The batter and crush attacks looked alike.

This pass replaces the six identical crown tentacles with nine varied ones. It
widens the painted value range: dark bruised grooves and roots, sheen only on
top, and veins with dark beds. Crush is now a low wrap around a floor-level
target, with the whole column bent forward over it.

No collision, AI, RNG, emission, regeneration effect, grabbing logic, bridge,
native or ABI change.

## Construction

- **Skin:** one connected, closed, voxel-fused skin with 12,000 cage faces
  (`SKIN_FACE_BUDGET = 12000`, `SKIN_VOXEL_SIZE = .24`). It fuses four braid
  strands, a core, the crown and lumps, ten lip lobes and 28 limbs. It is painted
  per triangle with the kraken's atlas code, and the braid grooves are darkened
  from the gap between the two nearest strands.
- **Accessories:** a maw throat disc, 23 hook teeth on a `maw` bone that thrusts,
  and 482 sucker cups, seated with interpolated skin weights in the same way as the kraken's.
- **Rig:** 218 bones: a six-bone trunk spine, head, maw and 28 limb chains.
  Scales are 1, and weights are quantised with `math.fsum`. The toolkit is reused
  read-only from `kraken_animation`.
- **Runtime:** 46,268 vertices, 28,328 triangles, rest 55.88 x 56.32 x 80.95. It
  stands taller than the kraken (50.5).

| Role | Clip | Frames | Middle-frame key pose |
| --- | --- | --- | --- |
| idle | `idle` | 48 @20 | rest pose; the trunk twists and every limb writhes |
| walk | `slink` | 32 @35 | rest pose; the roots ripple and the column sways |
| attack | `batter` | 27 | the trunk and crown pitch forward. The whole crown streams at the target at head height, and the heavy arms hammer down at x 28-29 |
| alt attack | `crush` | 31 | the column bows forward over a floor-level target with the maw turned down. The crown pours down over the target, and the arms wrap it near the floor (tips at about z 9) |
| hit | `flinch` | 15 | the column recoils and twists; limbs are flung out |
| death | `collapse` | 41 | the column shortens and buckles forward into a heap; limbs slide into slack floor coils |

All frames stay inside the centred cell: X -29.15..29.88, Y -27.98..29.14,
minimum Z 0.504, with no automatic floor compensation. Idle frame 0 equals the rest pose.

## Files

- `tools/monster_models/tentacle_horror_animation.py`, `tentacle_horror_materials.py`,
  `test_tentacle_horror.py`.
- `assets/monsters/tentacle_horror/` (`connected-skin.json.gz`, `animation.json`,
  `tentacle-horror-animated.blend`).
- `mod/BrogueDoom/models/monsters/48_tentacle_horror.iqm`,
  `mod/BrogueDoom/graphics/BRGTHOR.png` (2048 square; names checked). No shader
  or GLDEFS snippet.

## Phase-1 evidence

In `artifacts/creature-queue/BRG-M48/`:

- Two cold `--threads 1` cage bakes. Both hashes are
  `ff9cf8549f0cd7381f287db010f1375fc53d8e3152923ab0ff91a98a36e137cd`.
- `blender-build.log`: `SKELETAL_SOURCE_OK`, 218 bones, fresh reopen true.
- `preview-vulkan-contact.jpg` and `preview-opengl-contact.jpg` (1920x1080, 34
  views). Each has 26 distinct images, and the only duplicates are the expected
  ones (see `preview-*-distinct.txt`).
- `tests.log`: `python -m unittest tools.monster_models.test_tentacle_horror`, 10 tests OK.

## Known limitations

- The asset is heavy: 218 bones and about 28.3k triangles, most of them sucker
  cups. The first two Vulkan preview launches after a new IQM captured frozen
  frames (9 and 17 distinct images), and the third attempt was clean. Frame time
  was not measured.
- The front of the trunk is very dark. Its silhouette carries it, but surface
  detail there is subtle.
- A few triangles stretch at the crown and arm roots during large sweeps, and in
  the compressed death heap, which uses bone translation with scales of 1.
- There is no natural encounter, packaged gallery, native build or user art approval.

## Coordinator package archive

The coordinator returned the first delivery (a symmetric crown reading as bunny ears, glossy candy-purple flesh, look-alike attacks) and accepted the irregular writhing crown, darker veined flesh and distinct forward-bent crush. Round B was integrated and gated as pipeline batch `B` with the kraken, phantom, imp, fury, revenant, golem and tentacle horror (`artifacts/creature-queue/batches/B/gate-summary.json`: 118 tests OK, preservation audit with zero unexpected changes). Both final review packages (`0251f56fe4c6ab6b4bc3932db7e23556a749ae907edfdb6a8faec5b77bbb771c`, 1,216 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M48/final-vulkan/ProjectBroom-review.pk3.archive.json
```
