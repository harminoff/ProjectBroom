# Warden of Yendor (MK_WARDEN_OF_YENDOR) skeletal model

Work id BRG-M60, queue round E. Presentation only: Brogue CE owns the Warden's
1000 health, 12-17 damage, `NEVER_SLEEPS | ALWAYS_HUNTING | INVULNERABLE |
NO_POLYMORPH` flags, its endless hunt, `DF_RUBBLE` blood, `YENDOR_LIGHT` radius,
timing and every "strikes" outcome. Nothing here feeds data back to the
simulation, and no rubble, mantle or light plate collides or blocks anything.

Source text: "An immortal presence stalks through the dungeon, implacably hunting
that which was taken... and the one who took it."

## Brogue colour and palette

`monsterCatalog` uses `&yendorLightColor = {50, -100, 30, 0, 0, 0, 0, true}`: red
50, green -100, blue 30, a deep violet-magenta that dances. That is the base
identity.

- Armour: near-black aubergine to violet. Mid violet on the breast facets
  (86,60,120); a step lighter on arms, gauntlets and shoulder lames (112,82,152 and
  140,106,184); darker on legs and tassets (60,42,84) and darker still on
  greaves, helm and fauld lames (40,27,56). Pale lilac edge highlights everywhere.
- Light: hot magenta (255,70,216) reserved for four thin plate groups, each on its
  own bone: a single continuous lightning-crack fissure (zigzag on the breast facet through a
  brighter core widening, then down the plackart to its tip, with two short side
  branches leaving the line away from the core; nothing radiates from the core), the V visor slit, and a seam across each knuckle guard.
- `shaders/warden-yendor-light.fp` renders exactly that colour key fullbright
  (`glow_key()` in `warden_of_yendor_materials.py` is its Python twin) with a slow
  dancing pulse from renderer time. All armour keeps ordinary lighting.
- Death sinks the four plate groups into the armour, so the light goes out with
  the clip. No painted glow remains on the armour.

## Design

Rigid carved-plate kit (`guardian_kit`, read-only import); no connected skin, so
there is no cage bake. 129 rigid parts, 39 bones (root, pelvis, waist, chest, head, two pauldrons,
12 limb bones, 4 light, 16 mantle), exported at scale 0.745. Idle stands 69.4 units.

- Cuirass: two breast facets meet in a central ridge and taper to a pointed
  two-facet plackart over a narrow waist, with three overlapping curved fauld
  lames. Every plate carries a ridge or bevelled facet so lighting breaks across it.
- Pauldrons: three curved, downward-overlapping lames per side and a swept spike,
  20% smaller than the first blockout, on their own bones.
- Helm: tall tapering great-helm with a blank tapered mask, a narrow V visor slit
  and a swept-back crown of five blade points. No forward antennae, no hood, no chin block.
- Arms: tapered vambraces and taloned gauntlets (back-of-hand plate, knuckle guard,
  four articulated finger plates ending in pointed claws, thumb claw).
- Mantle: eight long tapering strips, each a two-bone chain, hanging from the
  shoulders and upper back to about knee height in uneven lengths with pointed
  tips and a lighter lilac edge. From the front only the outer strips show.

## Clips (35 Hz tics)

| Role | Clip | Frames @ fps | Loop | Tics |
| --- | --- | --- | --- | --- |
| idle | `idle` | 56 @ 16 | yes | 0 |
| move | `stride` | 44 @ 30 | yes | 0 (walkFrames 44) |
| attack | `strike` | 33 @ 30 | no | 39 |
| alternate | `sweep` | 31 @ 30 | no | 37 |
| hit | `recoil` | 15 @ 30 | no | 18 |
| death | `collapse` | 51 @ 30 | no | 60 |

Key poses sit on the middle frame. `strike` ("strikes"): the right gauntlet is
hauled high behind the crest around t=.25; the middle frame drives it forward,
down and wide at full extension in a long lunge with the torso twisted, the left
arm flung back and the mantle flaring out. `sweep` is a wide backhand.
`collapse`: the armour kneels, then falls into a low, wide heap; the helm lies on
its side on the floor beside it with the visor dark; the strips drape across the
pile and trail onto the floor; the glow is buried.

Pose bounds are inside +/-32 in X and Y for every frame, no frame touches below
z 0.07, and the death clip ends on the floor (top of the heap below 24 units).

## Files

- `tools/monster_models/warden_of_yendor_animation.py`, `warden_of_yendor_materials.py`,
  `test_warden_of_yendor.py`
- `mod/BrogueDoom/models/monsters/60_warden_of_yendor.iqm` (new name; the legacy
  `60_warden_of_yendor.obj` and `graphics/BRGM60.png` are untouched reference)
- `mod/BrogueDoom/graphics/BRGWRDN.png` (new lump, checked against existing graphics)
- `mod/BrogueDoom/shaders/warden-yendor-light.fp`
- `assets/monsters/warden_of_yendor/animation.json`
- pending row and GLDEFS snippet in `assets/monsters/skeletal_pending/`

## Known limits

- The mantle is rigid strips on two-bone chains, not cloth simulation; at rest it
  is a hint at 128 units and reads mainly in the strike and stride.
- The cuirass front is a flat triangle from straight on; the ridge reads better in
  oblique views.
- Plate is intentionally dark; the striking arm separates by a lifted mid tone and
  lilac edges, not by a large value gap.
- No natural-encounter proof: deferred to the deep-route census with the other deep creatures.
