# Phoenix model and animation

Presentation-only BRG-M65 / `MK_PHOENIX` (queue #55, round D, birds). Brogue CE stays authoritative for flight, fire immunity, PHOENIX_LIGHT, the egg it leaves, damage, turns and RNG. The model adds no gameplay, actors, light or collision. The phoenix egg is a separate creature (`phoenix_egg_animation.py`) and is not modelled here.

## Source facts and art decisions

Pinned Brogue (`Globals.c`): glyph colour `phoenixColor` = {100,0,0, 0,100,0, 0,true} (red with a large random green part, so red to orange to yellow); flags immune to fire, flies, no polymorph; light `PHOENIX_LIGHT`; blood `DF_ASH_BLOOD`; verbs pecks / scratches / claws; text: "shines with a brilliant light, its wings crackle and pop like embers ... an egg will form and a newborn phoenix will rise from its ashes".

Colour identity follows the catalogue colour: crimson roots through scarlet and orange to gold and pale-yellow tips (same palette family as the egg's ember-red membrane and gold-white cracks). Flame parts are fullbright (atlas column u >= 0.75, `shaders/phoenix-fire.fp`); body plumage, horn, talons and ash are lit with a wide warm value range.

Anatomy (original, reworked after the first pass was rejected as a scarecrow with chick eyes): hawk body pitched about 38 degrees; a larger head with a heavy, deeply tapered hooked beak (gold cere with a small ridge darkening to a near-black bronze tip whose hook shows below the jaw), flat angular crimson-brown brow wedges sloping down toward the beak in a V-scowl and set behind the eye plane, and narrow slanted glowing slit eyes in sunk dark sockets; cheek and neck ruff, 100+ overlapping plumage feathers, scaled tarsi with four hooked talons per foot, a crest of five flame plumes, seven long flame plumes for the tail plus short lit rump feathers. Each wing is full size (primaries reach about +-30 Y in idle): a thin buried arm rising out and back, 12 overlapping marginal feathers along the leading edge with four flame licks, scapulars, six inner secondaries, six outer trailing feathers hanging forward-down, three coverts bands, nine fullbright flame primaries on three flexible tongue bones and three embers. The fan plane leans back and its feathers curl forward for a cupped spread.

Clips (key pose on each action clip's middle frame):

- `idle` (36 f @ 24, loop): raised, cupped wing beat (roll -12 to +4, forward pitch), body bob, tail and crest flicker, tongues sway.
- `fly` (24 f @ 30, loop, movement role): full wingbeat with lagging elbow/wrist/hand, body counter-bob, flowing tail.
- `claw` (attack, 18 f @ 30): wings mantled wide and low, body lunges and pitches, talons thrust forward, beak open wide.
- `peck` (alternate, 20 f @ 30): neck and head strike forward and down, beak snaps open, wings half-mantled.
- `recoil` (hit, 12 f @ 30): body thrown back, wings flared up, head back, tongues snap.
- `death` (30 f @ 30): flare (wings thrown up, beak wide), then the bird collapses prone: torso flat, head laid forward, crest and tail flat, legs folded back, wings swept back and lying flat along the body. Three hidden spreaders (a tiny disc or dome in the torso at rest, skinned between a centre bone and eight ring bones, so only bone translations change and no bone scale is needed) grow into a large ash pool (about 31 x 23) under the husk and two ember-cracked mounds, one in front beside the head and one behind the tail beyond the wing silhouette, plus 30 hidden ash/ember lumps that land on the mounds and husk as ember glints. Final frame rests on the floor (bird minimum z 0.10, no automatic compensation).

Durations (engine tics): `[0, 0, 21, 24, 14, 35]`. No `visualScale`; size lives in the geometry.

## Construction

- `tools/monster_models/phoenix_animation.py`, `phoenix_materials.py`, `test_phoenix.py`; runtime `mod/BrogueDoom/models/monsters/65_phoenix.iqm`, `graphics/BRGPHNX.png`, `shaders/phoenix-fire.fp`; `assets/monsters/phoenix/` (manifest, `.blend`); pending row and GLDEFS snippet `assets/monsters/skeletal_pending/MK_PHOENIX.*`.
- Rigid pieces plus smoothly weighted flame ribbons (chain weights along tail, crest and tongue bones) and the ash spreaders. No connected skin, so no cage bake. About 337 parts, 27.6k vertices, 52.8k triangles.
- Clearance across every frame: |Y| <= 31.6, X -30.2..29.9, Z 0.10..65.5; constant hover lift of 3.4 on non-death clips. The longer wings reach radius about 32 from the shoulder, so claw, peck and fly add forward sweep and the death sweeps the wings back so no frame overshoots the cell.
- Shader is static: no time, world light, simulation input or RNG.

## Verification (phase 1 only)

See the hand-back message for hashes and capture paths. Not run: integration, shared suites, native build, packaged galleries, baselines, natural encounter.

## Candid flaws

- The death heap is still low; the pool is partly hidden under the folded wings and only the two mounds and the rims show from the oblique camera. Fullbright embers cannot be dimmed per frame.
- Fully spread wings are dense at 128 units; wing feather detail only shows at close range.
- Fan planes face forward, so from a pure side view the wings read thin.
- Body feather rows are somewhat coarse ("pineapple") from above.
