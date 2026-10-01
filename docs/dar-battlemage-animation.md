# Dar battlemage model and animation

Presentation-only BRG-M33 / MK_DAR_BATTLEMAGE. Brogue CE remains authoritative.

## Source facts and boundaries

Pinned `Globals.c` (catalog L1090, text L1274): "The dar battlemage's eyes glow
like embers and $HISHER hands radiate an occult heat." Male or female; bolts
fire, slow and discord; maintains distance; attack verb "cuts"; glyph colour
`darMageColor` (50, 50, 0). Fire, slowing, discord, targeting, drops, turns and
outcomes stay in Brogue. No native, bridge, ABI, collision, AI or RNG change.

## Art

Original art on the dar family anatomy (blademaster face sculpt reused
read-only), deliberately unlike the blademaster and priestess:

- Olive quilted battle coat (glyph cue) with oxblood placket and brass studs,
  a swallow-tailed skirt open at the front and lined in oxblood, and a tall
  flared standing collar (widened flare and brighter, wider brass edge trim
  for the 192-unit read; body volume unchanged). Bare forearms with leather bracers and brass rings.
- Asymmetric guard: three layered blackened-steel pauldrons with brass rims on
  the left, one smaller plate on the right; painted highlight pools.
- Belt with brass buckle and a chained red grimoire (original tooled sigil)
  on the right hip, on its own sway bone.
- Shaved scalp sides, swept near-black crest into a brass-bound topknot and a
  long tail on its own sway bone; heavy scowling brow, soot around the eyes.
- Source cues: ember irises and open, tense casting hands of charred skin
  crazed with ember veins, fully ember at the fingertips. Localized emission
  only: `shaders/dar-battlemage-embers.fp` makes texels inside a painted colour
  key fullbright (`ember_key()` in the materials module uses the same numbers).
  No world light, no time input, nothing changes at death.

## Rig, clips and bounds

19 bones (dar body, tome, topknot). Clips: `idle` (40, loop, caster guard with
right palm raised), `advance` (32, loop), `cut` (24: cocked back, then on the middle frame a
raking lunge onto the left foot with the right ember hand raised far forward,
fingers clawed down, left arm thrown back, torso twisted into it; the arm is
kept out of the 3/4 camera's line so it is not foreshortened), `conjure` (26, both palms thrust forward,
"transmuting"), `recoil` (14), `fall` (36). Key poses on the middle frame.
`fall` is a full collapse: knees buckle, then the body pitches face-down onto
the floor, laid on the cell diagonal (root yaw 38 degrees, pitch 88 degrees)
so its length fits the cell; head turned to the side, arms limp at the sides
with the ember hands low by the floor. Settled height 15.2 (was a crouch). Cage uses `SKIN_VOXEL_SIZE = .2` and `SKIN_FACE_BUDGET = 7000` (module
local) so the open fingers survive fusion.

Runtime: 27,478 vertices, 18,688 triangles; fused cage 3,522 vertices / 7,056
faces. Every frame within X -27.58..27.69, Y -21.63..21.32, min Z 0.166; no
floor compensation, unit bone scales.

## Files

`tools/monster_models/dar_battlemage_animation.py`, `dar_battlemage_materials.py`,
`test_dar_battlemage.py`; `assets/monsters/dar_battlemage/`;
`mod/BrogueDoom/models/monsters/33_dar_battlemage.iqm`;
`mod/BrogueDoom/graphics/BRGDBMG.png` (new lump, collision-checked);
`mod/BrogueDoom/shaders/dar-battlemage-embers.fp` (listed in `ownedFiles`);
pending row `assets/monsters/skeletal_pending/MK_DAR_BATTLEMAGE.json` and
GLDEFS snippet `MK_DAR_BATTLEMAGE.gldefs`.

## Verification (phase 1)

- Two cold `--threads 1` cage bakes: identical
  `f2f789f8311c31c5d782017ff59f0e7f67ceff1c842d32ef7310ba8d4ccf9f00`.
- `python -m unittest tools.monster_models.test_dar_battlemage`: 6 tests OK
  (ember-key confinement and shader threshold parity; planted rear foot in the
  lunge; prone death with head below 16 and settled height below 18).
- `blender_skeletal.py -- MK_DAR_BATTLEMAGE`: fresh reopen OK.
- Preview galleries: `artifacts/creature-queue/BRG-M33/preview-vulkan/` and
  `preview-opengl/` with contact sheets.

Integration, shared suites, native build and packaged galleries are the
coordinator's phase 3. User art approval is not claimed.

Original generated mesh/skin/shader: CC-BY-SA-4.0. No third-party artwork.

## Coordinator package archive

The coordinator returned the first delivery (idle-like chest-height cut, a still-standing bent-over death that read as a living crouch, thin silhouette at 192 units) and accepted the raking lunge, full face-down collapse and broadened collar/pauldron read. Round A was integrated and gated as pipeline batch `A` with the dar priestess, dar battlemage, goblin warlord, black jelly and unicorn (`artifacts/creature-queue/batches/A/gate-summary.json`: 87 tests OK, preservation audit with zero unexpected changes). Both final review packages (`761572a54dbd32a91407ca9cc82a4a7f5c6007f9919d70a01de10d5acc193dba`, 1,199 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M33/final-vulkan/ProjectBroom-review.pk3.archive.json
```
