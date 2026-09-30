# Fury model and animation

Presentation-only BRG-M46 / MK_FURY (queue #32). Brogue CE remains authoritative.
Phase-1 authoring deliverable under [creature-pipeline.md](creature-pipeline.md);
integration, shared suites, packaged galleries and final evidence are the
coordinator's Phase 3.

## Source facts

Brogue's catalog row (`Globals.c` L1116) gives glyph `G_FURY`, colour
`darkRed`, `DF_RED_BLOOD`, no bolts, and the flags `MONST_NEVER_SLEEPS` and
`MONST_FLIES`. Its prose (L1317) is "A creature of inchoate rage made flesh,
the fury's moist wings beat loudly in the darkness", with "flagellating" and
the attack verbs "drubs", "fustigates" and "castigates". Horde rows put furies
in packs (`GlobalsBrogue.c` L799). They are also summoned by the lich and the
eldritch totem (L817, L822) and appear in captive rows (L837-L841).

Flight, sleeplessness, pack behaviour, summoning, damage, turns and every
outcome remain Brogue-owned. There is no gameplay, AI, collision, RNG, bridge,
native, light or render-style change.

## Art interpretation

Brogue gives no body plan beyond wings and rage. The avian-female avenger is
an interpretation of the classical Furies, requested by the coordinator. It is
an art choice, not a Brogue fact, and Brogue's pronoun handling is unchanged.
The model is deliberately unlike the vampire bat: it has feathered wings on
their own back bones, a humanoid torso and head, and bird legs.

- **Body:** a gaunt, ashen grey-mauve woman about 38 units from talon to crown,
  hovering with a gap of about 7.7 units below the hooked talons.
- **Head:** wild near-black hair of 22 writhing locks. Blood-dark sockets frame
  bright painted red eyes that weep blood streaks, under a pinched frowning
  brow. The mouth is an open snarl with painted teeth and two 3D fangs.
- **Plumage, not clothing (coordinator fix):** 63 overlapping mantle feathers
  in six rows run from a neck ruff down to a V point on the sternum. They
  replace the painted chest wrap, which read as a bikini top. The back rows meet
  five scapular feathers per side. Those sweep from the upper back and
  shoulder out over the wing root, weighted from the chest to the first wing
  bone along their length, so the wing grows out of the body. The old
  tube-and-knob root is gone. The painted skin under the plumage and over the
  hips is dark feather scale, not cloth.
- **Hands:** long four-fingered hands with black nails.
- **Lower body:** ragged feathered hips of six feathers per thigh and a
  five-feather tail fan. The shins are scaled ochre bird legs, and each foot has
  three forward toes and a hind toe, all with hooked black talons.
- **Wings:** each wing is a three-bone feathered limb carrying:
  - 7 primaries in a tight, broad (4.2-unit), late-tapering fan from the hand,
    so they overlap instead of reading as a comb;
  - 6 secondaries, equally broad;
  - 3 tertials;
  - 11 coverts over the roots.

  The feathers hang back and down from the wing arm, so the gameplay (front)
  view sees the wing surface, not its leading edge. This was an art correction
  found in review. The span reaches about 50 units at rest.
- **Paint ("moist wings", coordinator fix):** each feather is near-black
  crimson at the root and over its covered inner vane. Only the exposed edge
  and tip grade to lit red, and coverts, scapulars and mantle feathers stay
  darker still. Flat engine light therefore shows dark roots and coverts
  against lit edges instead of one uniform saturated red. The feathers also
  carry barb striations, sparse dark splits, and shafts that run from dark to
  pale. Painted wet specular streaks and droplets are strongest where lit. The
  red nods to the dark red glyph colour. No emission, GLDEFS material,
  brightmap or light is added.
- **Ashen skin:** mottled with violet veins, with ribs and a sternum painted on
  the bare midriff.

## Construction

- **Masters:** `tools/monster_models/fury_animation.py` and
  `fury_materials.py`. `Pose`, `sharp_chain`, `quantise` and `leaf` are imported
  read-only from `imp_animation`, the island baker from `imp_materials`, and
  the primitives from `pixie_animation`.
- **Runtime files:**
  - `mod/BrogueDoom/models/monsters/46_fury.iqm`
  - `mod/BrogueDoom/graphics/BRGFURY.png` (2048 square)
  - Both names were checked for collisions first.
- **Assets:** `assets/monsters/fury/animation.json`, `connected-skin.json.gz`
  and `fury-animated.blend`.
- **Profile:** promoted to the registry by the coordinator, who is setting the
  durations in engine tics at 35 Hz, as `ceil(frames*35/fps)`:
  `[0, 0, 28, 28, 14, 42]`. There is no GLDEFS snippet.
- **Counts:** 33 bones, 212 runtime parts (one connected skin plus 211
  accessories), 47,859 vertices, 53,774 triangles and six clips.
- **Connected skin:** 3,955-vertex cage with 7,906 faces in one component. It
  joins cranium, face, chin, nose, ears, neck, chest, breasts, belly, pelvis,
  shoulders, arms, palms, legs and feet. The module sets
  `SKIN_VOXEL_SIZE = .12` and `SKIN_FACE_BUDGET = 7900`.
- **Accessories:** feathers, hair, talons, nails and eyes are closed and rigid
  on their bones. Hair locks blend head → hair → hair2 along their length, and
  scapulars blend chest → wing1.
- **Atlas:** small role cells sit top right and four 512-pixel feather cells
  bottom right. The hair cap has its own cell so its strands run pole-ward.
- **Rest extents:** 13.0 x 50.0 x 38.8 units.
- **Clearance:** every frame of every clip stays within X -27.20..25.88 and
  Y -27.06..25.52, including the full wingspan and the forward wing whip.
  Minimum Z is 0.14, and no automatic floor lift is used.

## Clips

Every action starts and ends in a shared hovering threat: claws raised to the
shoulders, palms forward, legs tucked. Each action's key pose is on its sampled
middle frame.

- **idle (36 frames at 24 fps, loop):** two loud wing beats, with the wings
  tucking on the upstroke and a body bob against the downstroke. The head
  sways, the claws flex, the talons clench and the hair and tail fan move.
  Frame 0 (used by every turnaround and distance view) shows the wings spread.
- **fly (24 frames at 30 fps, loop):** pitched 34° forward, arms swept back,
  legs trailing, hair streaming, with two larger wing beats and a roll/yaw sway
  so the middle frame differs from the first. The talons stay above 16 units.
- **drub (24 frames, attack, "drubs"):** she rears back with the wings high and
  the legs drawn up, then dives. At the middle frame both wings stand in a tall
  V more than 10 units above the head. Both talons thrust forward (X > 6) and
  both clawed hands rake forward (nails X > 9).
- **lash (24 frames, alternate, "flagellates", "castigates"):** the wings swing
  back, then whip forward around the prey in a buffet. At the middle frame both
  wings' primaries reach X > 12 in front of the body, while the right hand
  lashes down from overhead.
- **recoil (12 frames, hit):** knocked back with the wings flung up and
  crumpled, the arms guarding the face and the legs kicked forward.
- **death (36 frames):**
  1. A spasm with the wings snapping up.
  2. The wings fail and trail upward as she drops and pitches forward. At the
     middle frame she is mid-air, with pelvis and head above 6 units.
  3. A prone landing with a small bounce.
  4. The final pose is face-down. The back arches slightly so she rests on the
     breast plumage, and the head is turned down onto the cheek. The head and
     hair angles were found by floor-contact searches. The arms are flung
     forward and aside, and the legs lie straight back with the talons up.
  5. Both wings lie splayed flat across the floor, spanning more than 40
     units, with a median feather height under 5.5.

  The pelvis and chest end below 5 units, the head bone below 6 and the face
  features below 4. The maximum height is under 12.
  A falling-only ground guard is used, as for the imp.

## Verification (Phase 1)

- **Cold bakes:** two cold `--threads 1` connected-skin bakes
  (`cold-bake-0.log`, `cold-bake-1.log`) both gave cage 3955/7906 and
  byte-identical output:
  `f9e7cbda53810c44901aecaaab15bb4027ef16927c373da912925ea5f16d084c`.
- **Runtime hashes:** re-exported after the imp rework, because the fury imports
  imp helpers.
  - IQM `d555cac3654da9ac104b66fdf5082530c39da4c9936254ae6ed40264dbfbc19b`
  - PNG `fa8f74eb373c2e6a7b67d25b2b8ffeb60242dfdff29ede5f9ea6fa7bd09918bb`
- **Blender:** Blender 5.2.1 built the source with
  `blender_skeletal.py -- MK_FURY` (`blender-build.log`).
- **Tests:** `python -m unittest tools.monster_models.test_fury` ran 9 tests.
  They pass once the registry durations follow the formula. Before that, the
  duration assertion fails by design. The fury bytes were re-verified,
  unchanged, after the imp scale bake. They cover:
  - a closed single-component skin with normalised weights;
  - feather, talon and anatomy counts, and closed rigid feathers on the correct
    wing bones;
  - at least 50 mantle feathers, no tube-and-knob root, and five
    chest-to-wing scapulars per side;
  - dark roots against lit feather edges;
  - span and wing-root seating;
  - the profile via `skeletal_registry.find`, including the rule
    `durations[role] >= ceil(frames*35/fps)`;
  - per-frame ±32 clearance, no floor compensation, unit scales and loop
    closure;
  - the hover gap in every living clip, the beat range, spread wings at
    idle frame 0, and loop middle frames that differ from frame 0;
  - the drub and lash key poses;
  - the limp grounded death with flat splayed wings;
  - no degenerate triangles;
  - atlas isolation;
  - exact IQM and PNG bytes.
- **Galleries:** Vulkan (`preview-vulkan/`) and OpenGL (`preview-opengl/`), 34
  captures each at 1920x1080, with contact sheets. Stale runs (the camera never
  engaged under parallel load) were detected by hashing and retried. The only
  remaining duplicates are each action clip's first and last frames. The
  pre-fix galleries were deleted.

Evidence: `artifacts/creature-queue/BRG-M46/`.

## Candid flaws

- **Wings:** even with dark roots, the lit edges still read strongly red under
  flat light. The primary tips remain individually visible as a feathered
  (rather than smooth) trailing edge.
- **Wing root:** the scapulars hide the root. The wing arm itself is still a
  plain tube where it shows between feathers from below.
- **Mantle:** the feather rows are regular. At 64 units they read as scaled
  plumage over a simple chest form, and the bare arms and midriff stay ashen.
- **Hair:** the locks are tubes. From behind they read as heavy dreadlocks and
  hide the wing roots.
- **Hips:** the feathers are rigid on the thighs. In extreme leg poses the
  front ones can graze the belly.
- **Death:** the talons point up and the fury remains airborne-looking until
  late in the clip.
- **Eyes:** they are painted, not emissive, so in dark areas they will not
  glow.
- **Not proven by these galleries:** natural flight, pack behaviour, summoning,
  native hit and death timing, and captive presentation. User art approval
  remains open.

## Coordinator package archive

The coordinator returned the first delivery for minor fixes (a chest wrap reading as clothing, uniformly saturated red wings, a tube-and-knob wing root) and accepted the feathered mantle, dark-rooted wings and scapular wing roots. At gate time action durations were corrected to engine tics (ceil(frames x 35 / 30 fps)); the first gate's frozen OpenGL gallery was recaptured. Round B was integrated and gated as pipeline batch `B` with the kraken, phantom, imp, fury, revenant, golem and tentacle horror (`artifacts/creature-queue/batches/B/gate-summary.json`: 118 tests OK, preservation audit with zero unexpected changes). Both final review packages (`0251f56fe4c6ab6b4bc3932db7e23556a749ae907edfdb6a8faec5b77bbb771c`, 1,216 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M46/final-vulkan/ProjectBroom-review.pk3.archive.json
```
