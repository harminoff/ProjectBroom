# Dragon (MK_DRAGON, BRG-M50) animation report

Presentation only. Brogue CE owns the dragon's stats, speed, dragonfire bolt, burning, targeting and every outcome.
The dragon is 150 HP, immune to fire, carries an item and attacks all adjacent creatures. This model only draws poses.

## Source cues (pinned Brogue CE, `Globals.c`)
- "An ancient serpent of the world's deepest places ... an undying furnace of white-hot flames burns within its scaly
  hide"; attack verbs claws / tail-whips / bites; bolt `BOLT_DRAGONFIRE`; glyph colour green (20,80,15).
- Palette follows Brogue: emerald/forest green (rework 1; the first crimson pass was rejected as an authority issue).

## Design
- Compact winged quadruped that fits the 64-unit cell (rest 55 long, ~44 high incl. wing peaks, +X front): barrel chest,
  S-curved neck, horned head with hinged lower jaw, digitigrade hind legs, coiled tail with a blade, 22 dorsal spines.
- Skin (fused, 8,000 faces, `SKIN_FACE_BUDGET` set in the module): body, neck, head, legs, tail. Accessories: horns,
  teeth, jaw, tongue, claws, wing bones and fingers, six membrane panels, spines, tail blade, flame parts.
- Wings: bone arm plus three two-jointed fingers per side; membranes are thin closed shells between adjacent fingers
  (last panel to the flank) with a scalloped trailing edge, weighted between the two bordering finger chains.
- Fire: three teardrop pieces plus six tongues parked inside the skull. Only `breathe` slides them out of the mouth
  (bone translation, no bone scale); tests prove they are hidden in every other clip.
- Rig: 47 bones. Clips (role order): idle 48f loop, stalk 32f loop (lateral-sequence gait, one paw swings at a time),
  breathe 30f, lash 28f, recoil 14f, death 40f. Durations (35 Hz tics): 0,0,35,33,17,47.
- Key poses on the middle frame: breathe = hunkered low and back, wings mantled, neck thrust, jaw open, flame out;
  lash = body yawed hard toward the camera side, forepaw raked off the floor, jaw snapping, tail swung out;
  recoil = rears up, head thrown back, roar; death = reel and roar, then collapse onto the belly with legs splayed,
  neck laid sideways and wings draped, static for the last quarter.
- Paint: directional overlapping scale rows (larger on the back, tiny on head and limbs, lit free edge, shadowed base),
  dark green dorsal band, brighter flanks, pale yellow-ochre belly plates, ivory horns/claws/teeth, amber slit-pupil eyes,
  light olive/jade veined membranes, orange fire.

## Files
- `tools/monster_models/dragon_animation.py`, `dragon_materials.py`, `test_dragon.py`
- `assets/monsters/dragon/` (`animation.json`, `connected-skin.json.gz`, `dragon-animated.blend`)
- `mod/BrogueDoom/models/monsters/50_dragon.iqm`, `mod/BrogueDoom/graphics/BRGDRGN.png` (names collision-checked)
- `assets/monsters/skeletal_pending/MK_DRAGON.json` (class `BrogueMonsterK50`, no `visualScale`)

## Verification (phase 1 only)
- Two cold `--threads 1` cage bakes: identical CAGE_HASH lines, final `f9dec909d13905a3c6a622a1a406484ceb60f276263b9bfe5144a4c7f960e8a8`;
  identical `connected-skin.json.gz` SHA-256 `44f0f607bce073ca08c1d8a7e4a7b467cd8bd8b722e628bc5a579254a9d1d208`.
- `python -m unittest tools.monster_models.test_dragon`: 12 tests OK (every frame of every clip inside -32..+32 in X/Y
  measured from deformed skin; idle paws planted exactly; walk has at most one paw airborne; flames hidden outside breathe).
- Vulkan and OpenGL galleries (34 captures each) in `artifacts/creature-queue/BRG-M50/`; hashed, only expected
  duplicates (action first/last frames equal idle-derived rest).
- Not run (phase 3 duties): shared suites, regeneration, native build, packaged galleries, natural encounter.

## Rework 1 (coordinator review)
1. Colour: crimson repainted emerald (dragonColor 20/80/15, green blood); amber eyes; olive/jade membranes; fire stays orange.
2. Scale paint: the crackle network is gone; scales are now rows along the body axis (arc coordinate around it), with
   sizes by region and light-edge / dark-base shading.
3. Presence: the head rides a taller S-neck (`HEAD_DZ` 13): idle head/horn tops reach about 50; horns sweep back and down;
   folded wing arms angle back and outward beside the shoulders (fingers trail down beside the flanks). Breathe hunkers
   low (neck folds 100+ degrees, body pulled 10 back) and stays low and wide.
4. Fire: flame pieces slide out 4-16 units with eight tongues fanned sideways (about 12-13 beyond the snout); the flame
   atlas cells are fullbright via `mod/BrogueDoom/shaders/dragon-flame.fp` and pending `MK_DRAGON.gldefs`
   (region key checked against `RECTS` in tests).
5. Floor: planted paws roll level and rise off the floor by any dip (palm/claw probes), the tail guard keeps a bake margin,
   and a test asserts no idle/stalk/breathe/lash/recoil frame needs the exporter's root lift (death mid-fall may lift under 0.6).
New tests: head height, no root lift, green palette, fullbright region match. Tests: 15 OK.
Cage bakes (two cold): CAGE_HASH d5df47d4aee4f5cf69c384148a9d0047c1656153e8f08363fb07576b775a578c; skin gz SHA-256 582489fb...97c1.
Superseded first-pass galleries were overwritten in place (same 34 file names).

## Rework 2 (final polish)
1. Head menace: heavy bony brow tubes overhang small flush amber eye slits (no eyeball dome, flat lid plate); long
   flat-topped wedge snout (lofted superellipse sections) with nostril pads and ridges; lipless jaw line with six long
   upper teeth per side (two fangs each) overlapping the lower jaw; eight brow spines, six flaring jaw spikes, smaller
   cheeks; head top painted darker green. Eyes are fullbright with the flame cells (same shader, second region).
2. Flame: 23 layered tongues in four layers (white-yellow root, orange, deep red tip) plus six sparks form a cone with
   streak tongues reaching about 15 units past the mouth, fanned sideways and up. The pieces now park inside the
   chest/belly (bones parented to the chest, not the skull), so long tongues stay hidden; breathe slides each layer to the
   jaws, oriented with the head, growing out of the mouth. The breath key pose retracts the head (snout about x 17) so the
   jet ends inside the cell (max X 29.9).
Tests: 16 OK (new: predatory face, flames parked in the chest, long fanned cone, eye fullbright region).
Cage bakes (two cold): CAGE_HASH 3ea476e42f805b5db0b5c7b2096e922d464ac7590e024ebf77589afa8b6d02ee; skin gz acaa8fc6...84fd.
Galleries overwritten in place; contact sheets regenerated.

## Candid flaws
- Breath cell margins are thin (min X -31.7 from the wings, max X 29.9); the neck folds sharply to keep snout plus jet inside the cell.
- From the front camera the jet is foreshortened; at 21-breathe-9 (mid wind-up) fire has not left the mouth yet.
- Eye slits are small and mostly seen at close range; at 192 units the face reads through brow, fangs and horns.
- Flame tongues are rigid leaf shapes, so the flicker is only whole-layer motion.
- Death mid-fall frames may lift the root up to about 0.5; final corpse rests within 0.3 of the floor.
- Neck belly plates show slight aliasing; legs read slightly thin from the front.
