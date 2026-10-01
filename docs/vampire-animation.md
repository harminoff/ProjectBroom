# Vampire model and animation

Presentation-only BRG-M53 / MK_VAMPIRE. Brogue CE remains authoritative.

## Source facts and boundaries

Pinned `Globals.c` (catalog L1131, text L1341): "This vampire lives a solitary life
deep underground, consuming any warm-blooded creature unfortunate enough to venture
near $HISHER lair." Male; glyph colour white; `DF_RED_BLOOD`, death
`DF_BLOOD_EXPLOSION`; `BOLT_BLINKING`, `BOLT_DISCORD`; `MA_TRANSFERENCE`,
`MA_CAST_SUMMON` (vampire bats, `GlobalsBrogue.c` L815), `MA_ENTER_SUMMONS`,
`MONST_FLEES_NEAR_DEATH`. Attack verbs "grazes", "bites", "buries $HISHER fangs in";
summon text "spreads his cloak and bursts into a cloud of bats!"; a machine-boss lair
with a coffin (L849, L258). Draining, blinking, discord, bat transformation, fleeing,
the blood burst, drops, turns and outcomes stay in Brogue. No native, bridge, ABI,
collision, AI or RNG change.

## Art

An aristocratic underground predator rather than the stock Dracula: no tall
stand-up opera collar, no red silk lining, no medallion and no slicked hair. It
is distinct from the lich (upright, crowned, blue/gold) and the dar, wraith and
revenant:

- **Silhouette:** a gaunt, stooped figure with the head thrust forward and long
  arms. The bald skull is elongated, with a thin, sharp nose, sharp cheek ridges
  and long swept bat ears (flattened, cupped blades); long black-nailed claws
  are held half-curled. Legs are thick, with the hips, knees, feet and tall black
  riding boots set outward.
- **Aristocrat:** a tailored oxblood frock coat with black velvet lapels, a
  faint brocade diaper and silver buttons. The tails are split front and back,
  lined in black. A low turned-down velvet collar, a frilled ivory lace jabot
  flecked with blood, velvet cuffs with lace edges, and black breeches.
- **Predator (source cues):** two long fangs, fresh blood at the lips and
  running from the chin, blood on the claws, and bloodless blue-white skin with
  violet hollows and dark veins. Painted head: blue-grey temples, jaw and back of
  skull, hollow cheeks under a lit cheekbone ridge, deep shadowed sockets, and
  veins on the temples and jaw. The red irises are plain paint (no emission).
- **The cloak is the bat form:** a leathery, low-collared cloak held by a silver
  clasp chain. Its hem is cut into six bat-wing scallops (8.6 units deep,
  `cloak_hem`, shared with the paint) between five thin dark ribs (the edge ribs
  were dropped), painted as membrane (strongly mottled, veined, leathery
  warm-brown sheen) with a dark wine-brown inner membrane. A crimson rim is
  painted along the side edges and scalloped hem, outer and inner, so the cloak
  holds its outline at distance. The side edges are weighted to the arm chains,
  so `spread` opens it like a pair of wings.
- Flat-light painting: the pale head, hands and jabot sit against the dark
  cloth, and a warm sheen and paler ribs separate the cloak from the grey walls.

## Rig, clips and bounds

19 bones: root, pelvis, spine, chest, neck, head, jaw, and two three-bone arms
and legs, with two-link leg IK. Clips: `idle` (40, loop, predatory stoop
`STOOP = (14, 10, 14, 26, 8, -4, -100, 70, 36)`: shoulders and head forward, claws
half-raised in front at the waist, wrists Z > 30 and X > 5 in every frame, head
sweeping), `prowl` (32, loop, fixed forward/outward IK knee pole and a slight foot
splay; knees stay at |Y| > 3.5 in every frame), `bite` (24: wind-up, then on the middle frame a
low lunge, head dropped below Z 52, jaw wide, claws seizing forward), `spread`
(26: middle frame, arms thrown wide and low, cloak opened as wings to Y ±29,
head thrust forward hissing), `recoil` (14) and `collapse` (36: middle frame,
knees giving way; it ends face-down on its knees under the spread cloak, max Z
31 of 61). Durations are `[0, 0, 24, 26, 14, 36]` tics. No `visualScale`.

Fused cage (coat, pelvis, sleeves, legs and boots, `SKIN_FACE_BUDGET` 5200):
2,957 vertices and 5,192 faces. Runtime: 43,992 vertices and 14,664 triangles in
per-triangle Morton islands painted per texel (the revenant's atlas baker is
reused read-only). Every sampled frame stays inside X -25.53..26.80, Y
-29.19..29.19, min Z 0.274. There is no floor compensation, and all bone scales
are one.

## Files

`tools/monster_models/vampire_animation.py`, `vampire_materials.py`,
`test_vampire.py`; `assets/monsters/vampire/` (`animation.json`,
`connected-skin.json.gz`, `vampire-animated.blend`);
`mod/BrogueDoom/models/monsters/53_vampire.iqm`;
`mod/BrogueDoom/graphics/BRGVAMP.png` (new lump, collision-checked); pending row
`assets/monsters/skeletal_pending/MK_VAMPIRE.json`. No shader or GLDEFS.

## Rework history

The coordinator's first review asked for four changes, all done in the rework
pass:

1. **Head form.** Elongated cranium, thinner and sharper nose, sharper cheek
   ridges; painted blue-grey temples, jaw and skull, hollow cheeks, deep sockets
   and veins.
2. **Predatory idle, thicker legs, no knee knock.** The hanging idle became the
   `STOOP` pose with half-raised, half-curled claws. Leg radii are 2.8/2.4/2.05/
   2.3/1.8, the hips, knees, feet and boots moved outward, and the IK uses a fixed
   forward/outward knee pole.
3. **Rear "striped barrel" cloak.** Seven ribs became five thin dark ribs, with
   stronger mottling, a leathery sheen and scallops deepened to 8.6 units.
4. **Cloak lost at distance (192).** A crimson rim was painted on the cloak's
   side edges and scalloped hem, outer and inner membrane.

## Verification (rework pass)

- Two cold `--threads 1` Blender 5.2.1 cage bakes, both
  `9c68649cc31da0420018b605460b9c27c2e2e7ceeb4376b966b2b4041fef966f`.
- `blender_skeletal.py -- MK_VAMPIRE` built the .blend (exit 0).
- `python -m unittest tools.monster_models.test_lich tools.monster_models.test_vampire`: 24 tests OK (12 vampire, 12 lich). New vampire tests cover the predatory idle and outboard knees, the head form and the cloak rim.
- Preview galleries (34 captures each, 1920x1080, hash-checked; one frozen OpenGL run was retried; only expected first/last duplicates remain):
  `artifacts/creature-queue/BRG-M53/preview-vulkan`, `preview-opengl`, contact sheets
  `preview-vulkan-contact.jpg` / `preview-opengl-contact.jpg`.

| Asset | SHA256 |
| --- | --- |
| IQM | `8bb4244eafb8905dc5410f938ae07e809d4408a992d8bedd93d00c70913b2fe9` |
| Diffuse | `a08c400c38cc323c907406da3727cdbecf0859671775952d2f92f111fbdf6735` |

Integration, the shared suites, the native build, packaged galleries, natural
encounters and user art approval are still open. Original art, CC-BY-SA-4.0,
with no imported assets.
