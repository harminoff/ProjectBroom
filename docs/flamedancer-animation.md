# Flamedancer animation (BRG-M54, MK_FLAMEDANCER)

Presentation only. Brogue CE owns spawning, flight, distance keeping, the fire
bolt, burning hits, health and timing; this model only draws the displayed
creature. No gameplay data, RNG, collision or bridge contract changed.

## Source facts (pinned Brogue CE, `Globals.c`)

- Glyph `G_FLAMEDANCER` (white `F`), light `FLAMEDANCER_LIGHT` with the
  `flamedancerCoronaColor` corona and `DF_FLAMEDANCER_CORONA`.
- Flags `MONST_MAINTAINS_DISTANCE | MONST_IMMUNE_TO_FIRE | MONST_FIERY`,
  ability `MA_HIT_BURN`, bolt `BOLT_FIRE`; hits are "singes / burns / immolates".
- Text: "An elemental creature from another plane of existence, the infernal
  flamedancer burns with such intensity that [it] is painful to behold."

## Art decisions

- It is a being of fire, not a figure in an orange robe: a spiral column of
  twelve unequal flame tongues around a hot core, eleven short side licks so the
  outline bristles, eight swirling skirt tongues, a bright head with dark angry
  eye slits on the +X front, two ribbon arms that end in finger-flames (one
  raised, one flung wide), and eight drifting sparks.
- Value carries form. Every texel is fullbright; `shaders/flamedancer-fire.fp`
  darkens by view angle, reddens the rim and runs a slow shimmer up the body.
  **The shimmer is driven by renderer time**, so a gallery hash check cannot prove
  a capture is not frozen; key frames were checked by eye on both backends
  (Vulkan and OpenGL match). Palette: white-hot head, yellow core, orange
  bodies, deep red tips. Distinct from the wisp (blue, additive, translucent).
- Skinning: one 4x4x9 free-form lattice of 144 bones (the wisp / flame-turret
  affine-cage technique) with exact Freudenthal weights, quantized to 1e-6. All
  bones keep unit scale, so the death collapses the cage to a point: complete
  extinction. A second 2x2x2 cage of 8 bones carries the cast fireball: it is a
  point (invisible) in every clip except `bolt`, where it opens to 1.5x its rest
  size in front of the body. No connected skin, no Blender cage bake.
- Clips: `idle` (48 @ 24, sway and twist), `dance` (32 @ 35, stronger leaning
  whirl), `sear` (24, melee: winds back then lunges forward and low with both
  arms reaching, key pose on frame 12), `bolt` (26, fire cast, key pose on frame
  13: the column flares to about 1.5x its width and leans toward +X, both ribbon
  arms thrust forward and inward together, the skirt spreads, and a bright
  yellow fireball with radiating licks forms out in front between the hands),
  `recoil` (14), `gutter` (36, flares, sags into a low puddle of flame at the
  middle frame, then collapses to a single point).
- Profile durations (35 Hz tics): 0, 0, 24, 26, 14, 36. No `visualScale`, no
  `emissive`/`additiveFlame`; a painted fullbright shader is used instead.
- Every frame stays inside the -32..+32 cell (measured X -25.5..31.2, Y
  -29.7..29.8, height <= 72.3).

## Rework history

- Round 1 review: the `bolt` middle frame was almost indistinguishable from
  idle at gallery distance. Rework: 1.5x column flare, forward lean, arms thrust
  together, plus the fireball cage above (new part `fireball` + six licks, eight
  extra bones). `dance` got a larger forward lean (still inside the cell). A
  first attempt to carry the ball with the main lattice was rejected: the ball
  and column share nodes, so it stayed buried in the flames; a separate cage
  fixed that. The collapsed cage point sits at the floor centre so the death
  ends fully extinguished.

## Files

- `tools/monster_models/flamedancer_animation.py`, `flamedancer_materials.py`,
  `test_flamedancer.py`
- `mod/BrogueDoom/models/monsters/54_flamedancer.iqm`,
  `mod/BrogueDoom/graphics/BRGFDANC.png`,
  `mod/BrogueDoom/shaders/flamedancer-fire.fp`
- `assets/monsters/flamedancer/` (manifest, `.blend`),
  pending row and GLDEFS snippet in `assets/monsters/skeletal_pending/`

## Verification (phase 1)

- `python -m unittest tools.monster_models.test_flamedancer`: 10 tests pass
  (closed parts, weights and rest reconstruction, loops, clearance, middle-frame
  key poses, bolt flare width and fireball only during `bolt`, sag then
  extinction, +X face, profile durations, exact bytes, inert proxy).
- Two cold generator runs are byte identical. Blender 5.2 build and fresh reopen
  pass (153 bones, 61 parts, six actions).
- Vulkan and OpenGL 34-capture preview galleries in
  `artifacts/creature-queue/BRG-M54/`; no repeated captures.

## Known limitations

- Head reads as a bright mask; body is flame ribbons rather than volumetric
  flame. `dance` is a stronger lean and twist of the idle sway.
- Death ends with no geometry (fully extinguished), as the wisp does.
- Gameplay outcomes: cannot change; Brogue CE remains authoritative.
