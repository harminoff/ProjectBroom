# Mangrove dryad animation (BRG-M67, MK_ANCIENT_SPIRIT)

Presentation only. Brogue CE owns the dryad's melee, the vines bolt, movement and
timing; this model only draws the displayed creature. No gameplay data, RNG,
collision or bridge contract changed.

## Source facts (pinned Brogue CE, `Globals.c`)

- Glyph `G_ANCIENT_SPIRIT`, name "mangrove dryad", colour `tanColor` {80,67,15}.
- 70 HP, defense 60, accuracy 175, damage 2-8, bolt `BOLT_ANCIENT_SPIRIT_VINES`,
  blood `DF_ASH_BLOOD`, no light; flags `IMMUNE_TO_WEBS | ALWAYS_USE_ABILITY |
  MAINTAINS_DISTANCE | NO_POLYMORPH | MALE | FEMALE`. Attack verbs: whips, lashes,
  thrashes, lacerates.
- Text: "This mangrove dryad is as old as the earth, and its gnarled figure houses an
  ancient power. When angered, it can call upon the forces of nature to bind its
  foes and tear them to shreds."

## Art decisions

- **Brogue colour is the base identity.** Weathered khaki bark: a baked-light ramp
  from near-black brown fissures (16,11,4) through khaki mid-tones (126,102,52) to
  pale straw ridges (224,206,152). Moss, olive leaves, dark-khaki vines and amber eye
  glow are small accents only. Value, not hue, separates it from grey walls and the
  brown floor.
- **Fused connected skin** (`CONNECTED_SKIN` hook, `blender_skin.py`, voxel .3, face
  budget 16000; cage 8025 vertices, 16046 faces): a spirally fluted trunk with burls
  and a chest knot hollow, asymmetric shoulders (one big burl), long thin gnarled
  arms with knotted joints and twig fingers, and eight prop roots.
- **Prop roots are the identity.** Each is a quarter-ellipse arch that leaves the
  trunk horizontally at its own height (z 27-44), bows out and lands vertically at a
  radius of 20-26, leaving open gaps beneath; six fork once. Irregular heights,
  spacing and thickness, with a clear gap in front. Roots stay pinned to their planted
  world footing while the trunk moves (`pin_roots`).
- **Rigid parts:** head (heavy angled brow over deep sunken slit eyes, ridged nose,
  splintered mouth, knotted chin), asymmetric crown of six bare branches with small
  forks, a few leaves and a trailing moss strand, one broken stub on the big-burl
  shoulder, two thorned khaki vine lashes, and nine bark shards hidden inside the trunk.
- **Bark paint** is baked per vertex from geometry (`bake_skin`): occlusion, concavity,
  analytic rib troughs (dark) and crests (pale) on the trunk and roots, vertical grain,
  knot holes, brow creases and dark undersides. The 'skin' tile is a 2-D ramp: the
  first coordinate is a grain streak (or moss above 0.9), the second the baked shade.
- Gender-ambiguous: no beard, no breasts; a bark face.

## Rig and clips (51 bones, 35 Hz durations)

| Role | Clip | Frames @ fps | Profile duration |
| --- | --- | --- | --- |
| idle | `idle` | 48 @ 24 (loop) | 0 |
| walk | `stride` | 32 @ 35 (loop) | 0 |
| attack | `lash` | 26 @ 35 | 26 |
| attack_alt | `vines` (vines bolt cast) | 28 @ 35 | 28 |
| hit | `recoil` | 14 @ 35 | 14 |
| death | `collapse` | 40 @ 35 | 40 |

- **`lash`:** the key pose is on the middle frame. The right arm and vine sweep
  laterally to the right at shoulder height, reaching the cell edge with a shallow S
  and the tip curled forward. The torso leans and twists into it, the crown tilts,
  and the left arm is flung up and back. The face stays clear.
- **`vines`:** both arms thrust forward and down with the vines slamming the floor,
  while the front roots rear up.
- **`collapse`:** the trunk pitches forward into a low heap, the roots pull in flat and
  pinned, three roots (1, 4, 6) snap flat outward, the arms and vines flop behind, and
  the hidden bark shards are thrown out onto the floor. It ends on the floor.
- Every frame of every clip stays inside +/-32 in X and Y (checked per frame in
  `test_mangrove_dryad.py`). No `visualScale`.

## Files

- `tools/monster_models/mangrove_dryad_animation.py` (generator),
  `mangrove_dryad_materials.py`, `test_mangrove_dryad.py`
- `assets/monsters/mangrove_dryad/` (`animation.json`, `connected-skin.json.gz`)
- `mod/BrogueDoom/models/monsters/67_mangrove_dryad.iqm` (mesh label
  `Project_Broom_ancient_spirit`), `mod/BrogueDoom/graphics/BRGDRYAD.png`
- Pending profile row `assets/monsters/skeletal_pending/MK_ANCIENT_SPIRIT.json`
  (class `BrogueMonsterK67`). The legacy static art `67_ancient_spirit.obj` and
  `BRGM67.png` are untouched.

## Verification (authoring pass)

- `python -m unittest tools.monster_models.test_mangrove_dryad`: 11 tests, OK.
- Two cold `--threads 1` cage bakes: identical cage hash
  `e0cd9ab4764f0c132fba66df19388c8b055f91788b2ffd6a960d08f6bd7e8e05` and identical
  bake file sha256 `d40c73e004e09486148f059dbbee5baef577459c0bc5d69b4b64b9260a0d188e`.
- IQM sha256 `6f916ac7488e6ae47d123c183a3c051813033c014c9ec9371a8acba6d78a80bb`,
  skin sha256 `ab44006da943c4cf8db5e437df661d71a6003c19a44e075322b27dbb1558157c`.
- Gallery and precheck results are in the final hand-back; the Blender build, OpenGL
  gallery and gate run at integration.

## Known limitations

- The lash's vine cannot extend toward the camera inside the +/-32 cell, so it
  sweeps sideways instead.
- The collapse reads as a slumped heap rather than a fully limp pile; the three
  snapped roots are only mildly visible.
- The bark relief comes from vertex-baked paint on a 16k-face cage, so fine grain is
  soft at close range.
