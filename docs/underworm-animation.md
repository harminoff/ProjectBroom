# Underworm model and animation

Presentation-only BRG-M36 / MK_UNDERWORM. Brogue CE remains authoritative. No gameplay, AI, collision, RNG, timing or ABI change.

## Source facts (pinned Globals.c)

Large earth-dwelling creature "larger than an ogre but capable of squeezing through tiny openings" that burrows behind cavern walls and lies dormant until it feels prey. 80 HP, defense 40, damage 18-22, move 150 / attack 200 (slow), never sleeps, bleeds brown worm viscera (wormColor 80/60/40). Verbs: slams, bites, tail-whips. Slowness, burrowing and dormancy are Brogue-owned and have no visual logic here.

## Art decisions (rework 1, current)

- Palette follows wormColor (80, 60, 40): dark umber back, dusty tan/ochre flanks, pale sandy-cream belly, near-black grooves, a restrained wet sheen. Maw interior is dark maroon with ivory teeth; the lip ring is dark fleshy brown-red.
- Body: legless annulated worm, about thirty ridge-and-groove segments, flat low-oval section. Coil of 1.44 turns spans y -28.5..+26.7 (previously only to +20.6); lateral radius grows from 1.2 at the tail tip to 7.8 at the coil end and 10.4 at the raised front.
- Head: a flattened, ridged, flared head (widest at the mouth, none of the earlier smooth dome) with a funnel mouth, three overlapping chitin collar plates behind it, ten small funnel teeth, and four thick hinged jaw petals (bones `petal_0..3`) each carrying three teeth. Petals open outward from about 48 degrees at rest to 64 in the lunge; opening angle drives all four with small per-petal variation.
- Rest head height is about 49 (top about 61, under the ~72 oblique crop). Whole design sits 2.5 units back so the open petals stay in the cell.
- Clips: idle (40 f, loop; a lift wave travels through the coil), crawl (28 f), lunge (25 f: rears up and back, then a low forward strike with petals flung open on the middle frame), slam (29 f: rears higher, crashes head down and to the left), recoil (15 f), collapse (37 f: neck slumps along the floor and runs north beside the coil, head lies turned to the side with petals splayed slack). Durations equal frame counts at 35 fps.
- Cell fit: every frame stays inside x -31.4..31.4, y -30.4..31.3.

## Rework history

1. First delivery: salmon-pink palette, smooth bulbous head with jaw, rest head 40 high, coil to y +20.6. Rejected: wrong palette (authority: wormColor), head read phallic from the rear, body too small, standing head in death.
2. Rework 1: repaint to umber/tan/sand; head rebuilt as a flared ridged funnel with collar plates and four hinged petals; body thickened, coil enlarged, head raised; death re-posed lying flat. Preview `--backend` 1 and 0 galleries regenerated (old galleries deleted).

## Files

`tools/monster_models/underworm_animation.py`, `underworm_materials.py`, `test_underworm.py`; `assets/monsters/underworm/` (manifest, connected skin, blend); `mod/BrogueDoom/models/monsters/36_underworm.iqm`, `mod/BrogueDoom/graphics/BRGWORM.png`; pending row `assets/monsters/skeletal_pending/MK_UNDERWORM.json`. No new GLDEFS snippet. Original artwork, CC-BY-SA-4.0.

## Verification (phase 1 only)

See the hand-back message for the two cold cage-bake hashes, test result, runtime SHA-256 values, and both backends' galleries and contact sheets in `artifacts/creature-queue/BRG-M36/`. Shared suites, native build, packaging and natural-encounter gates are not run (coordinator phase 3).

3. Rework 2 (polish): petal knobs replaced by three sharp hooked, inward-curling ivory teeth with a dark root per petal; petals thinned to a sharp plated edge with a raised ridge line; three overlapping convex chitin cap plates close the back of the head; collapse now turns the head over (yaw 85, tipped down) so it lies on its side, petals slack and about 22 degrees open, the maw facing sideways.

## Known flaws

- The dead head still stands about 20-25 units (flattened head, open petals); the oval body cannot be flattened further without bone scale. Head roll was not used because the head is wider than tall.
- From directly behind, the head is a domed chitin cap inside a collar ring with a dark value gradient; it reads as armour but a slight bell shape remains.
- Dead head still stands about 28 units tall (rear caps rise when tipped); the maw faces sideways rather than fully to the floor.
- Open petals reach within about 1 unit of the +X cell limit at strike and slam peaks.
- The peristaltic bulge is a travelling lift wave (idle envelope), not a radius change; the mesh is rigid otherwise.
- No dedicated tail-whip clip.
