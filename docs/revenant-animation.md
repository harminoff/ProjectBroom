# Revenant model and animation

Presentation-only BRG-M47 / MK_REVENANT. Brogue CE remains authoritative.

## Source facts and art decisions

Pinned Brogue prose (`Globals.c` L1320): "This unholy specter stalks the deep places
of the earth without fear, impervious to conventional attacks." Its only flag is
`MONST_IMMUNE_TO_WEAPONS`; it has no flight flag and a 200 movement duration (slow).
Colour is `ectoplasmColor`. Immunity, speed, attacks and outcomes stay in Brogue;
nothing here signals or changes them.

Revised after coordinator review (the first pass read as a stock grim-reaper monk):

- **Silhouette:** a stooped, looming predator. The cowled head sits low and forward
  of the shoulders (neck/head bones moved forward and down) beneath a broad mantle
  hump that rises behind it; the stalk adds extra stoop.
- **Unnatural lower body:** the cloth cage now ends above the knees. Below it, two
  rings of 36 torn, tapering strips hang at irregular lengths, end 1.4-6.9 units above
  the floor and are painted to fade into near-black toward their tips. Feet were
  removed, so there are no visible feet or legs. Everything stays opaque; no shader
  was added (fade and taper are painted and modelled).
- **Grave-shroud cloth:** a torn over-layer with ragged edge, four binding strips
  wound diagonally across the torso, noise-warped irregular folds with strong
  painted value contrast, rot blotches, dull ectoplasm stains, grave earth darkening
  toward the hem and lit frayed edges. The monk rope belt was dropped.
- **Head and hands:** a skull deep in a near-black cowl under a projecting brim,
  darker grey-brown aged bone with the cowl's shadow across the brow and crown,
  thin wandering cracks, a longer jaw with long teeth, and faint cold painted
  pinpoints in the sockets (not emissive). Hands are darker aged bone with long,
  hooked dark talons.

Six cosmetic roles: `idle` (heavy breathing, slow head sweep), `stalk` (slow,
stooped plod; two-link leg IK under the strips), `smash` (middle frame: both fists
raised above the cowl, silhouette to Z 75; elbows fold through the slam to stay in
the cell), `rend` (middle frame: hunched low, claws raking forward), `recoil` and
`fall` (middle frame: the legs give way under the shroud; ends seated and folded
face-down with the strips spilling on the floor, max Z 27.8 of 62).

## Delivered files

- Master: `tools/monster_models/revenant_animation.py`, `revenant_materials.py`;
  tests `tools/monster_models/test_revenant.py`.
- Runtime: `mod/BrogueDoom/models/monsters/47_revenant.iqm`,
  `mod/BrogueDoom/graphics/BRGREVNT.png` (2048 atlas; name collision-checked).
- Editable: `assets/monsters/revenant/revenant-animated.blend`, `animation.json`,
  `connected-skin.json.gz`.
- Pending: `assets/monsters/skeletal_pending/MK_REVENANT.json`. No shader or GLDEFS.

19 bones, 95 source parts. The fused cloth cage (shroud, torn over-layer, mantle,
open cowl, sleeves) has 6,404 faces (`SKIN_FACE_BUDGET` 6400). Runtime: 45,576
vertices and 15,192 triangles in per-triangle Morton-ordered islands painted per
texel (budget freed by removing the feet, cord and knuckle geometry). Skirt weights
drape the front over the thighs and hang the back from pelvis to heels. Every
sampled frame stays inside X -28.02..31.93, Y -28.0..28.0, min Z 0.75; both feet
stay planted except the stalk swing foot; all bone scales one; no floor
compensation.

## Verification (Phase 1)

- Two cold `--threads 1` Blender 5.2.1 bakes of the final cage: both
  `33e2ca68ab60d39b085f56f27585c87b7986266f1952f87fd79e27f95558fae1`.
- `python -m unittest tools.monster_models.test_revenant`: 10 tests OK (136 s).
- `blender_skeletal.py -- MK_REVENANT` built the .blend (exit 0).
- Preview galleries (34 captures each, 1920x1080; one stale OpenGL capture run was
  detected by hash and retried): `artifacts/creature-queue/BRG-M47/preview-vulkan`
  and `preview-opengl`, contact sheets `preview-vulkan-contact.jpg` /
  `preview-opengl-contact.jpg`.

| Asset | SHA256 |
| --- | --- |
| IQM | `239b99b0c8a3b9f54ceb2e12b7391d514b7d13ad34c98cd8455374ad529331ad` |
| Diffuse | `58459a4786574059c6854e82a2200c59ec523cafec65b0be7704197469971a2c` |

Integration, shared suites, native build, packaged galleries, natural encounter and
user art approval remain open. Original art, CC-BY-SA-4.0; no imports.

## Coordinator package archive

The coordinator returned the first delivery (a stock grim-reaper/monk: smooth purple robe, rope belt, clean skull, upright) and accepted the hunched grave-shroud specter with a shredded fading hem, bindings, rot staining and a cowl-shadowed cracked skull. The first gate's frozen OpenGL gallery was recaptured. Round B was integrated and gated as pipeline batch `B` with the kraken, phantom, imp, fury, revenant, golem and tentacle horror (`artifacts/creature-queue/batches/B/gate-summary.json`: 118 tests OK, preservation audit with zero unexpected changes). Both final review packages (`0251f56fe4c6ab6b4bc3932db7e23556a749ae907edfdb6a8faec5b77bbb771c`, 1,216 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M47/final-vulkan/ProjectBroom-review.pk3.archive.json
```
