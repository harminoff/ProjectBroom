# Dar priestess model and animation

Presentation-only BRG-M32 / MK_DAR_PRIESTESS. Brogue CE remains authoritative.

## Source facts and boundaries

Pinned `Globals.c` (catalog L1088, text L1271): "The dar priestess carries a host
of religious relics that jangle as $HESHE walks." Female; bolts negation,
healing, haste and spark; maintains distance; attack verbs "cuts", "slices";
glyph colour `darPriestessColor` (0, 50, 50). Haste, healing, negation, spark,
targeting, drops, turns and all outcomes stay in Brogue. No native, bridge,
ABI, collision, AI or RNG change. Clips are cosmetic roles only.

## Art

Original Project Broom art on the dar family anatomy (blademaster face sculpt
reused read-only via `dar_blademaster_animation.rings`; no shared file edited):

- Floor-length teal A-line robe with painted fold occlusion, darkened hem and a
  gold diamond hem band; a broad teal capelet with gold rim; bell sleeves with
  gold cuffs. The teal echoes the glyph cue; it implies no power.
- Cream stole in two strips down the front carrying an original emblem (a
  crescent cradling a disc), ending in gold tassels.
- Relics physically attached: gold girdle cord with knot and tasselled ends; six
  relics (two bronze bells, a gem reliquary box, an ivory tooth, a gold icon
  disc, a teal glass vial) each on its own ribbed chain and own pivot bone so
  they swing out of phase ("jangle") in walk; necklace and chest medallion.
- Ebony relic staff with gold bands, a ring head holding a teal gem, finial and
  two hanging charms (bell and disc) on a sway bone. The staff is a root child
  that copies the left-hand transform exactly while held.
- Ritual sickle in the right hand (supports the source cut/slice verbs): a
  crescent of radius 4.3 with a painted bright inner bevel and dark spine so it
  reads at 128 units, still far smaller than and unlike the blademaster's sword.
- Face: lowered lids with lash line (serene, not a stare), teal-silver irises,
  silver brows, original teal forehead mark, long silver hair under a gold
  circlet with an original crescent crest; three separated locks break up the
  back-hair curtain and strand ends are uneven.

## Rig, clips and bounds

26 bones (dar body, staff, charms, sickle, six relic pivots). Clips: `idle`
(40, loop), `advance` (32, loop), `slice` (24), `invoke` (26), `recoil` (14),
`fall` (36). Key action poses sit on the middle frame. `slice` winds the sickle
high behind the right shoulder, then on the middle frame is a committed slash:
arm extended forward and down across the body with the blade leading, torso
twisted and leaning in, weight stepped onto the right foot (hem follows the
step). The staff hand counter-rotates so the staff stays upright. `invoke` raises the staff
and an open palm (presentation for her bolts; no spell is launched). `fall` is a
limp seated collapse: knees give, legs slide forward under the robe, torso and
head slump, arms hang; the staff slides and topples about its foot to lie flat
beside her (ring flat on the floor). Robe weights: front cloth follows the thigh
chain, back cloth hangs from pelvis to feet, so the hem never enters the floor.

Runtime: 30,182 vertices, 29,858 triangles; fused cage 2,803 vertices / 5,602
faces. Every frame stays within X -27.52..29.96, Y -15.46..19.30, min Z 0.20;
no automatic floor compensation, unit bone scales.

## Files

`tools/monster_models/dar_priestess_animation.py`, `dar_priestess_materials.py`,
`test_dar_priestess.py`; `assets/monsters/dar_priestess/` (manifest, connected
skin, `.blend`); `mod/BrogueDoom/models/monsters/32_dar_priestess.iqm`;
`mod/BrogueDoom/graphics/BRGDPRS.png` (new lump, collision-checked); pending row
`assets/monsters/skeletal_pending/MK_DAR_PRIESTESS.json`. No shader, no GLDEFS.

## Verification (phase 1)

- Two cold `--threads 1` cage bakes: identical
  `3ccd288b6c9a98106e82a121e2aa95074c1a6465e3feccbb74e5ffdfdb8f3ccf`.
- `python -m unittest tools.monster_models.test_dar_priestess`: 7 tests OK.
- `blender_skeletal.py -- MK_DAR_PRIESTESS`: SKELETAL_SOURCE_OK, fresh reopen.
- Preview galleries (34 views, 1920x1080): `artifacts/creature-queue/BRG-M32/preview-vulkan/`
  and `preview-opengl/` with contact sheets.

Integration, shared suites, native build and packaged galleries are the
coordinator's phase 3. User art approval is not claimed.

Original generated mesh/skin: CC-BY-SA-4.0. No third-party artwork.

## Coordinator package archive

The coordinator returned the first delivery because its slice middle frame read as a raised hand holding a tiny knife, then accepted the committed diagonal slash with the larger bright-edged sickle. Round A was integrated and gated as pipeline batch `A` with the dar priestess, dar battlemage, goblin warlord, black jelly and unicorn (`artifacts/creature-queue/batches/A/gate-summary.json`: 87 tests OK, preservation audit with zero unexpected changes). Both final review packages (`761572a54dbd32a91407ca9cc82a4a7f5c6007f9919d70a01de10d5acc193dba`, 1,199 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M32/final-vulkan/ProjectBroom-review.pk3.archive.json
```
