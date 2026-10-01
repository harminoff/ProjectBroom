# Lich model and animation

Presentation-only BRG-M40 / MK_LICH. Brogue CE remains authoritative.

## Source facts and boundaries

Pinned `Globals.c` (catalog L1104, text L1295): "The desiccated form of an ancient
sorcerer, animated by dark arts and lust for power, commands the obedience of the
infernal planes. $HISHER essence is anchored to reality by a phylactery that is
always in $HISHER possession, and the lich cannot die unless $HISHER phylactery is
destroyed." Glyph colour white; intrinsic light `LICH_LIGHT` (`lichLightColor`, the
same green light as the phylactery gem, L1106 "This gem was the fulcrum of a dark
rite"); `BOLT_FIRE`, `MA_CAST_SUMMON` (phantoms and furies, `GlobalsBrogue.c`
L816-817), `MONST_MAINTAINS_DISTANCE`, `DF_ASH_BLOOD`; attack verb "touches"; summon
text "rasps a terrifying incantation!". Fire bolts, summoning, distance keeping, the
phylactery link, resurrection, drops, turns and outcomes stay in Brogue. No native,
bridge, ABI, collision, AI or RNG change.

## Art

An original sorcerer-king rather than a skeleton in a robe with a staff. It is
deliberately unlike the dar kit (no coat, pauldrons or tome), the wraith, and the
revenant (no hood, shroud or stoop):

- **Silhouette:** gaunt and upright, with a tall nine-point gold crown (front spike
  tallest) grown onto the skull and a broad, open-fronted royal cope whose hem is
  cut in points. There is no staff. The idle left claw is cupped under the gem.
- **Phylactery link:** a faceted green gem in a gold reliquary cage (four bands,
  cap and finial) hangs on a chain at the sternum, and the forked beard stops
  above it. The gem and two eye pinpoints are the only fullbright texels. Brogue
  gives the lich and the gem the same lich light, so the face, beard, guarding
  hand and chest near the gem carry a painted green cast. No light is emitted.
- **Desiccated, ancient:** leathery dark-brown hide (98, 72, 48) drawn over the
  skull, with brown cheek and temple hollows, wrinkle bands, dark sockets, a nasal
  cavity, duller bared teeth and cracks. Specular is low and the green cast on the
  head is weaker. The forked beard is thin, dry and ash-grey. The claws are long
  and dark-nailed, with gold rings on two fingers of each hand.
- **Regalia and age:** a midnight-blue robe, a royal blue cope with gold orphreys,
  embroidered sigils and a crimson lining, and a gold brocade stole with crimson
  lozenges. The cloth is deeply aged (`faded()`): indigo troughs, desaturated dusty
  lit planes and painted fold occlusion. The cope hem is ragged in geometry
  (`cope_hem` adds irregular tatters on alternate vertices) with a frayed dark
  edge; the orphrey is darker and torn, the sigils are darker gold, and the sleeves
  are faded with frayed gold cuffs. The robe uses the same aged cloth. The crown,
  stole and gem stay bright. Other aging is painted: tarnish with verdigris in the
  recesses, dust blooms, sparse moth holes, and ash dusting the gold hem band
  (`DF_ASH_BLOOD` cue only).
- Flat-light painting: top light, fold and cavity occlusion, and specular pools
  on gold. The palette keeps the lich clearly separate from the grey walls.

## Rig, clips and bounds

19 bones: root, pelvis, spine, chest, neck, head, jaw, and two three-bone arms
and legs. The legs are hidden under the robe, driven by two-link IK and draped
with revenant-style skirt weights. Clips: `idle` (40, loop, gem guarded),
`stride` (32, loop, stately stride), `touch` (24: wind-up, then on the middle
frame a deep lunge with the right claw thrust out to X 30 while the left hand
keeps the gem), `incant` (26: middle frame, torso yawed 20 degrees with a neck counter-yaw so both
arms read from the oblique and front cameras, arms flung wide and low to Y -28..30,
head thrown back and jaw agape), `recoil` (14) and `crumble` (36: middle frame,
legs giving way; it ends kneeling and pitched face-down with the crown on the
floor, max Z 25.7 of 66). Durations are `[0, 0, 24, 26, 14, 36]` tics, each
action >= ceil(frames x 35 / 35). No `visualScale`.

Fused cage (robe and bell sleeves, `SKIN_FACE_BUDGET` 5600): 3,002 vertices and
5,598 faces. Runtime: 48,042 vertices and 16,014 triangles, in per-triangle
Morton islands painted per texel (the revenant's atlas baker is reused
read-only). Every sampled frame stays inside X -19.09..29.97, Y -28.01..30.42,
min Z 0.567. There is no floor compensation, and all bone scales are one.

## Files

`tools/monster_models/lich_animation.py`, `lich_materials.py`, `test_lich.py`;
`assets/monsters/lich/` (`animation.json`, `connected-skin.json.gz`,
`lich-animated.blend`); `mod/BrogueDoom/models/monsters/40_lich.iqm`;
`mod/BrogueDoom/graphics/BRGLICH.png` (new lump, collision-checked);
`mod/BrogueDoom/shaders/lich-phylactery.fp` (listed in `ownedFiles`); pending row
`assets/monsters/skeletal_pending/MK_LICH.json` and GLDEFS snippet `MK_LICH.gldefs`.

## Rework history

The coordinator's first review asked for three changes, all done in the rework
pass (art only; rig, clip lengths, cage and shader are unchanged):

1. **`incant` readable from the oblique and front cameras, low and wide.** Torso
   yaw `INCANT_YAW = 20`, neck counter-yaw, `INCANT = (-22, 28, -30, 30)` and
   pelvis Y -3.6 to recentre; both arms now read in `11-incant-13`.
2. **Deeper, older cope.** `faded()` cloth, ragged `cope_hem` geometry (vertex
   count unchanged), darker torn orphrey, darker sigils, faded sleeves with frayed
   cuffs; crown, stole and gem stay bright.
3. **Leathery skull (optional).** Darker brown hide, brown hollows, wrinkle bands,
   less specular, weaker green cast, duller teeth.

The cage is robe and sleeves only, so its bake hash did not change.

## Verification (rework pass)

- Two cold `--threads 1` Blender 5.2.1 cage bakes, both
  `f6cb23529d8116f9975cf1dae421dd69cd4f0707b9e869a9ec704acf52baf6e1`
  (unchanged from the first pass).
- `blender_skeletal.py -- MK_LICH` built the .blend (exit 0).
- `python -m unittest tools.monster_models.test_lich tools.monster_models.test_vampire`: 24 tests OK (12 lich, 12 vampire). New lich tests cover the ragged, aged cope; the robe/gold contrast test now uses the robe's mean over its folds.
- Preview galleries (34 captures each, 1920x1080, hash-checked; only expected first/last duplicates remain):
  `artifacts/creature-queue/BRG-M40/preview-vulkan`, `preview-opengl`, contact sheets
  `preview-vulkan-contact.jpg` / `preview-opengl-contact.jpg`.

| Asset | SHA256 |
| --- | --- |
| IQM | `791ea535ab00e934683798e4174d29877660a3eb40b29cf1485bbbb537c95c40` |
| Diffuse | `bf8db1d48d9c1ae16aa5fb065aed5e716b3404c168c213dd8ed0856ecc71da04` |
| Shader | `08080aae2ce3da814937c43b13e1e0410d6918792054789b2c10d89dbfd5f9b1` |

Integration, the shared suites, the native build, packaged galleries, natural
encounters and user art approval are still open. Original art, CC-BY-SA-4.0,
with no imported assets.
