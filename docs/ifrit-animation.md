# Ifrit animation (BRG-M64, MK_IFRIT)

Presentation only. Brogue CE owns flight, speed, melee, the discord bolt, health
and timing; this model only draws the displayed creature. No gameplay data, RNG,
collision or bridge contract changed.

## Source facts (pinned Brogue CE, `Globals.c`)

- Glyph `G_IFRIT`, colour `ifritColor` {50,10,100} (deep violet-blue), light
  `IFRIT_LIGHT`.
- 40 HP, 50-tick movement (fast), `{5,13,2}` melee, bolt `BOLT_DISCORD`; flags
  `MONST_IMMUNE_TO_FIRE | MONST_FLIES | MONST_MALE`.
- Text: "A whirling desert storm given human shape, the ifrit's twin scimitars
  flicker in the darkness and [its] eyes burn with otherworldly zeal."

## Art decisions (after the round-1 rejection)

- Heavy silhouette, the opposite of the flamedancer's thin fire column: a very
  broad inverted-triangle torso, huge deltoids, swept-back horns, gold collar,
  armlets and bracers, twin scimitars raised in a wide V, and no legs.
- Anatomy by form: torso, neck, shoulders, arms and fists are ONE connected skin
  (`CONNECTED_SKIN` hook in the module plus `blender_skin.py`, like ogre/troll).
  The blockout is overlapping elongated, flattened masses that the voxel remesh
  fuses: fan-shaped pecs flowing into elongated deltoids, sloping traps, lats, a
  flat abdominal plate over a V-taper to the waist, long tapering biceps, triceps
  and brachioradialis, and forearms that taper from 6.8 to 3.8. Voxel size .26,
  face budget 11000 (cage 5510 vertices, 11016 faces). Head, horns, jewellery,
  blades, crown flame, flecks and the vortex are rigid attachments.
- Anatomy by paint, baked from geometry after the fusion: `bake_skin()` computes
  per-vertex key and fill light, occlusion (other parts nearby, the fused
  surface's own concavity so creases fall where muscles meet, and shallow
  abdominal grooves) and an ember under-glow on downward faces. Shading is a
  function of position only, so UV-split vertices of the fused skin shade
  identically (no seam patches). The ramp is one step darker than round 2. The `skin` tile is only a 2-D ramp addressed by
  (under-glow, shade): near-black indigo crevices, desaturated violet mid-tones,
  lavender only on the top highlights, warm ember tint on undersides. There is no
  specular or normal map, so nothing reads as glossy plastic.
- Face: a skull enlarged 1.26x as a group, heavy brow ridge, cheekbones, jaw, dark
  open mouth with 12 teeth and four fangs, slit ember eyes under the brow, a
  moustache with volume (two strands per side), goatee and beard tuft, gold
  earrings, thicker swept-back horns with a dark-to-ivory value gradient, and the
  small crown flame.
- Tail: the coiled rings are gone. A dark vortex core (near-black with ember
  sparks) is wrapped by nine ragged, twisting smoke sheets and six thinner outward
  wisps that narrow to a point at the floor; the smoke tile is charcoal violet
  with lighter ragged tips and sparse ember sparks.
- Blades: real sabre curve (tip sweeps 17 units toward +X), widest near the tip,
  dark blued spine and polished edge bevel. The glowing edge is a separate thin
  strip on its own bone; on the corpse the strip sinks into the blade, so the
  collapse ends with dull steel.
- Fullbright only where painted with the ember key (`shaders/ifrit-embers.fp`,
  `ember_key()`): eyes, edge strips, crown flame, burst flecks and smoke sparks.
- Skinning: 36 bones. The fused skin uses transferred, relaxed, 4-influence
  weights over spine, chest, neck, shoulders, elbows and wrists; attachments are
  rigid or chain-weighted; 16 burst-fleck bones and two edge-strip bones.
- Clips: `idle` (48 @ 24), `fly` (32 @ 35, forward lean, tail streaming, blades
  swept back), `slash` (26, key pose on frame 13: blades chop down into a low
  wide V), `discord` (28, key pose on frame 14: the torso rears back, the head
  drops, the blades are flung out level into a wide T, and sixteen ember flecks
  that hid inside the chest spiral out around the body in a rising column),
  `recoil` (14), `collapse` (40: staggers, topples face-down to the floor with
  arms and blades laid under and beside the body; the eye, crown-flame and edge
  bones sink so no ember burns on the corpse).
- Profile durations (35 Hz tics): 0, 0, 26, 28, 14, 40. No `visualScale`.
- Every frame stays inside the -32..+32 cell (X -31.3..28.6, Y -31.1..31.1,
  height <= 69.3, floor contact only at the end of `collapse`).

## Rework history

- Round 1 (rejected): smooth saturated ellipsoids, flat lavender, three dust
  bands that read as a coiled spring, small face. Kept for comparison in
  `artifacts/creature-queue/BRG-M64/rejected-v1-contact.jpg`.
- Round 2 (this delivery): the items above. Notable fixes found on the way: the
  first ember burst placed flecks below the floor (bone rest positions are
  parent-relative), which lifted the whole model; the collapse body was 70 units
  long and needed the hips shifted, the blades crossed under the body and the head
  bowed to fit the cell.

- Round 3 (this delivery), coordinator: "every muscle is a separate rigid
  ellipsoid ... reads as an inflatable toy". Moved torso, neck, shoulders and arms
  onto the connected skin and reshaped every mass as an elongated flattened form;
  slightly bulkier arms after the first bake looked thin; darkened the ramp.
  The skin, cage and bake are new: `assets/monsters/ifrit/connected-skin.json.gz`.

## Files

- `tools/monster_models/ifrit_animation.py`, `ifrit_materials.py`, `test_ifrit.py`
- `assets/monsters/ifrit/connected-skin.json.gz` (cage bake; rebuild with `blender_skin.py -- ifrit`)
- `mod/BrogueDoom/models/monsters/64_ifrit.iqm`,
  `mod/BrogueDoom/graphics/BRGIFRIT.png`, `mod/BrogueDoom/shaders/ifrit-embers.fp`
- `assets/monsters/ifrit/` (manifest, `.blend`), pending row and GLDEFS snippet
  in `assets/monsters/skeletal_pending/`

## Verification (phase 1)

- `python -m unittest tools.monster_models.test_ifrit`: 15 tests pass (one closed connected skin spanning torso to wrists, sculpted
  legless anatomy, layered ragged vortex, baked skin range and desaturation, fanged
  +X face, curved dark-spined blades, weights, rest reconstruction and loops,
  per-frame clearance, middle-frame poses, slash V, discord rear/wide/burst,
  collapse with embers out, ember key, profile durations, exact bytes, inert proxy).
- Two cold `--threads 1` cage bakes are byte identical (same four CAGE_HASH lines,
  same `connected-skin.json.gz`), and two cold exports are byte identical. Blender
  5.2 build and fresh reopen pass (36 bones, 95 parts, six actions).
- Vulkan and OpenGL 34-capture preview galleries in
  `artifacts/creature-queue/BRG-M64/`; no repeated captures.

## Known limitations

- Skin lighting is baked at the rest pose; poses do not re-light it.
- The fusion smooths fine detail: abdominal grooves are painted occlusion, not
  geometry, and gold armlets/bracers sit on a slightly different surface than
  the blockout (seated by radius, not re-fitted).
- Eyes read as orange slit bars under the brow rather than fine eyes; teeth show
  only in close front views. The vortex is still a coiled read at 192 units.
- The discord silhouette is limited by the 32-unit cell: the wide T spans about
  60 units and is subtler from the front camera than from the oblique gallery.
- Gameplay outcomes: cannot change; Brogue CE remains authoritative.
