# Phantom model and animation

Presentation-only BRG-M43 / MK_PHANTOM. Brogue CE remains authoritative.

## Source facts and art decisions

Pinned Brogue prose (`Globals.c` L1308) describes "a silhouette of mournful rage
against an empty backdrop" that slips through the dungeon invisibly, leaving glowing
ectoplasm droplets. Catalog flags are `MONST_INVISIBLE`, `MONST_FLITS`, `MONST_FLIES`
and `MONST_IMMUNE_TO_WEBS`; its colour is `ectoplasmColor` (45, 20, 55). Invisibility,
flight, flitting, droplets and every outcome stay in Brogue. This model only defines
how the phantom looks while the frontend chooses to display it; it adds no visibility
rule.

Art answers "silhouette against an empty backdrop" literally: an additive, fullbright
figure whose glancing edges glow (`shaders/phantom-veil.fp`) around a dim violet
interior. It hovers and is legless: a gaunt ribbed torso pours into a ragged,
fold-streaked ectoplasm tail. Rage-slanted hollow sockets and a long sagging
open mouth are painted black, so they read as holes through the glowing face. Five
hair tendrils stream back from the crown (dark at the root so they never veil the
face), long claws, torn forearm and skirt tatters, and five hanging ectoplasm droplets
supply the "trailing wisps". Violet, lilac and near-white are artistic
interpretation of the ectoplasm cue. It is clearly distinct from the grounded,
opaque, naked wraith and from the opaque, hooded revenant.

Six cosmetic roles: `idle` (hover bob, tail and hair waves), `drift` (forward lean,
tail streaming, flitting weave), `lunge` (middle frame: body stretched horizontal,
both clawed arms thrust forward, jaw wide), `wail` (middle frame: reared up, arms
flung into a wide V overhead, head thrown back), `recoil` (blown back) and
`dissipate` (a last rising wail, then the ectoplasm slumps into a low heap on the
floor: tail pooled flat, torso folded over, arms spilled sideways; final max Z 23.3).

## Delivered files

- Master: `tools/monster_models/phantom_animation.py`, `phantom_materials.py`;
  tests `tools/monster_models/test_phantom.py`.
- Runtime: `mod/BrogueDoom/models/monsters/43_phantom.iqm`,
  `mod/BrogueDoom/graphics/BRGPHANT.png` (2048 atlas),
  `mod/BrogueDoom/shaders/phantom-veil.fp` (new; names collision-checked).
- Editable: `assets/monsters/phantom/phantom-animated.blend`, `animation.json`,
  `connected-skin.json.gz`.
- Pending: `assets/monsters/skeletal_pending/MK_PHANTOM.json` (`additiveFlame`,
  `emissive`, `ownedFiles` shader) and `MK_PHANTOM.gldefs`.

21 bones (no legs), 67 source parts; the fused cage (body, neck, head, shoulders,
arms, hands) has 7,212 faces at voxel 0.2 (`SKIN_VOXEL_SIZE`, `SKIN_FACE_BUDGET`
7200). Runtime: 37,884 vertices, 12,628 triangles. Every triangle owns a padded 16px
island painted per texel from its rest position and smooth normal, laid out in Morton
order. Weights are joint-centred, capped at four, quantized to 1e-6 with `math.fsum`.
Every sampled frame stays inside X -29.87..31.61, Y -31.83..31.83, min Z 0.17; all
bone scales are one and no floor compensation occurs. Additive and fullbright are
presentation only; the shader shimmer uses renderer time, not Brogue state or RNG.

## Verification (Phase 1)

- Two cold `--threads 1` Blender 5.2.1 bakes: both
  `34dbea2243c40634be17ac08625421e2a9fdc9c28cd480a8959cdcb5f6914397`.
- `python -m unittest tools.monster_models.test_phantom`: 9 tests OK (81 s).
- `blender_skeletal.py -- MK_PHANTOM` built the .blend (exit 0).
- Preview galleries (34 captures each, 1920x1080, no stale middle frames):
  `artifacts/creature-queue/BRG-M43/preview-vulkan` and `preview-opengl`, contact
  sheets `preview-vulkan-contact.jpg` / `preview-opengl-contact.jpg`.

| Asset | SHA256 |
| --- | --- |
| IQM | `fc4788818f029f394db04240e44748ecc985f67bf00c50ddb1692cfc240314f1` |
| Diffuse | `89fb5e5cbc850cb75c316d22c343874f59ec0dea95b4a3aaae8874184d8041e5` |
| Shader | `aab7f988b8ac45227d282400262861eca809f08b1fc9a4c0b264015d9be5683a` |

Integration, shared suites, native build, packaged galleries, natural encounter and
user art approval remain open. Original art, CC-BY-SA-4.0; no imports.

## Coordinator package archive

The coordinator accepted the first delivery: the additive veil shader, screaming face, claws, ectoplasm tail, lunge and wail read at gameplay distance. Round B was integrated and gated as pipeline batch `B` with the kraken, phantom, imp, fury, revenant, golem and tentacle horror (`artifacts/creature-queue/batches/B/gate-summary.json`: 118 tests OK, preservation audit with zero unexpected changes). Both final review packages (`0251f56fe4c6ab6b4bc3932db7e23556a749ae907edfdb6a8faec5b77bbb771c`, 1,216 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M43/final-vulkan/ProjectBroom-review.pk3.archive.json
```
