# Imp model and animation

Presentation-only BRG-M45 / MK_IMP (queue #30). Brogue CE remains authoritative.
This is a Phase-1 authoring deliverable under
[creature-pipeline.md](creature-pipeline.md). Integration, shared suites,
packaged galleries and final evidence belong to the coordinator's Phase 3.

## Source facts

- **Catalog row** (`Globals.c` L1114):
  - glyph `G_IMP` and colour `pink`;
  - `DF_GREEN_BLOOD` and `IMP_LIGHT`;
  - the bolt `BOLT_BLINKING` and the ability `MA_HIT_STEAL_FLEE`.
- **Prose** (L1314): "This trickster demon moves with astonishing speed and
  delights in stealing from $HISHER enemies and blinking away". The action
  string is "dissecting", and the attack verbs are "slices" and "cuts".
- **Horde rows** (`GlobalsBrogue.c` L797, L837, L899, L913, L921) include
  captive, kennel, vampire-fodder and thief-machine appearances.

Everything that happens in play stays Brogue-owned:

- speed, theft, fleeing and blinking;
- the light and the blood;
- targets, damage, turns and every outcome.

There is no gameplay, AI, collision, RNG, bridge, native, light or
render-style change. No clip moves the imp off its cell or fakes a blink, and
the `snatch` clip does not claim that an item was stolen.

## Art interpretation (coordinator rework)

The first pass read as a cute cartoon gremlin: wide eyes, a zipper grin, hands
clasped at the chest and a flat hot-pink body. The rework pushes it toward a
cunning, dangerous thief-demon. Horns, spurs, colours and proportions are art
choices, not Brogue facts.

### Face

- Narrow eyes slanted up at the outer corners, under heavy maroon upper lids
  with a dark lash line and small lower lids.
- Gold irises with vertical slit pupils.
- A hard V brow pinched low toward the nose, painted sockets, lit cheekbones
  and hollow cheeks.
- A sly smirk curled up at the imp's left corner, with lips parted there over
  three modelled sharp teeth and one fang on the other side.
- The ear span is cut from about 20 to about 16 units.
- The horns are sharper and swept hard back.

### Silhouette and pose

- The idle is a predatory crouch:
  - the pelvis is lowered 2.7 units with the knees bent;
  - the torso pitches forward and the head stays level and watching;
  - the long arms hang low and forward below the pelvis, with the claws spread
    and ready;
  - the tail curls up behind in an S.
- Ivory shoulder and elbow spurs and a ridge of seven spikes down the spine
  make the outline angular and spiky.

### Scale

The imp is posed and weighted at design scale. Export then bakes a uniform
`SCALE = 1.15` into the geometry, the rest skeleton and every clip translation,
keeping unit bone scales, so the runtime IQM itself is 46.4 units tall.

- The profile carries no `visualScale`, and MODELDEF binds the imp at
  `Scale 1.0`. An earlier `visualScale: 1.15` broke the shared registry test,
  which allows only the kobold to be scaled.
- The connected-skin bake stays in design units. Its fingerprint and cage are
  unchanged by the scale bake.
- Clearance and the presented size are identical to the accepted version.

### Paint (flat engine light)

- **Body:** deep rose-crimson (the pink glyph cue) with a strong value range:
  - lighter lit planes;
  - a subtle specular sheen;
  - painted anatomy (pectorals, sternum, abdominals, ribs, collarbones, spine
    and shoulder blades);
  - painted occlusion.
- **Extremities:** hands, feet, the tail tip and spade, and the horn and spur
  bases grade to near-black maroon.
- **Legs:** dark goat fur carries a lighter rose rim on the thigh and shin
  fronts, so the legs separate from dark floors.
- No emission, GLDEFS material, brightmap or light is added.

## Construction

- **Masters:** `tools/monster_models/imp_animation.py` and `imp_materials.py`.
  - `imp_materials.bake_atlas` is a generic island baker. The fury reuses it
    read-only.
  - Primitives are imported read-only from `pixie_animation`.
- **Runtime files:** `mod/BrogueDoom/models/monsters/45_imp.iqm` and
  `mod/BrogueDoom/graphics/BRGIMP.png` (2048 square). Both names were checked
  for collisions first.
- **Assets:** `assets/monsters/imp/animation.json`, `connected-skin.json.gz`
  and `imp-animated.blend`.
- **Profile:** now promoted to the registry by the coordinator, who is removing
  `visualScale` and setting the durations in engine tics at 35 Hz, as
  `ceil(frames*35/fps)`: `[0, 0, 28, 28, 14, 38]`. There is no GLDEFS snippet.
- **Mesh:** 29 bones and 46 runtime parts (one connected skin plus 45
  accessories), with 28,721 vertices, 17,052 triangles and six clips.
- **Connected skin:** a 3,952-vertex cage with 7,900 faces and one component.
  - It joins the cranium, face, chin, nose, brows, ears, neck, torso,
    shoulders, arms, palms, legs, feet, tail and spade.
  - The module sets `SKIN_VOXEL_SIZE = .11` and `SKIN_FACE_BUDGET = 7900`.
  - Weights are quantised to 1e-6, and the last influence takes the
    `math.fsum` complement.
- **Accessories:** closed and rigid on their bones. They are the horns, eyes,
  lids, teeth, fingers, claws, toe claws, shoulder and elbow spurs, and spine
  spikes.
- **Rest extents (exported):** 23.4 x 18.9 x 46.4 units.
- **Clearance:** every frame of every clip stays within X -29.74..30.03 and
  Y -15.35..23.07. Minimum Z is 0.214, and no automatic floor lift is used.

## Clips

Every action starts and ends in the shared predatory crouch, and each action's
key pose is on its sampled middle frame.

- **idle** (48 frames at 24 fps, loop): the crouch, with sly head scanning,
  claws flexing, an ear twitch and a flicking tail tip. Both feet stay planted
  exactly through two-bone digitigrade IK.
- **walk** (24 frames at 30 fps, loop): a pitched-forward scamper with a
  4.2-unit stride. One foot is always planted, and the swing foot lifts more
  than 3.5 units.
- **slice** (24 frames, attack, "slices"): the right claw cocks back at the
  shoulder, then the imp lunges. At the middle frame:
  - the right foot has stepped far forward and the left leg is stretched
    behind;
  - the right arm is flung out with the claws splayed (claw bone X above 14);
  - the tail is raised.
- **snatch** (24 frames, alternate): the imp coils low, then dives into a
  stretched two-handed grab. Both claws reach past X 11 below chest height,
  and the clip finishes with a clutch. This is cosmetic only.
- **recoil** (12 frames, hit): the head snaps back, the arms go up to guard,
  the ears flatten and the tail bristles. The feet stay planted.
- **death** (32 frames):
  1. A jolt.
  2. A forward topple over the planted feet. At the middle frame the pelvis and
     head are still above 6 units.
  3. A prone landing with a small bounce.
  4. The final pose is limp:
     - the head rests on one cheek with the ears flopped;
     - one arm is flung forward and the other lies back;
     - the legs are splayed;
     - the tail lies in a curve.

  Only one rigid horn stands clear of a body lying within 10 units of the
  floor. A pose-level ground guard lifts the body only while it is falling,
  and it fades to zero before the settled frames.

## Verification (Phase 1)

- **Cold bakes:** two cold `--threads 1` connected-skin bakes
  (`cold-bake-0.log`, `cold-bake-1.log`), re-run after the scale bake, both
  produced cage 3952/7900. Their byte-identical output hashes to
  `7a61683bb241ab8b2b7a6d1fe06d27f3e8cc0bae98b4867afc041f6a176293d5`. This is
  unchanged, because the skin is baked at design scale.
- **Runtime hashes:**
  - IQM `c8bf120aae54a3ff9bb803d77dfda44cf8bcc0e0db6adc3fd7b9359a0145b130`
    (scale baked in)
  - PNG `442eb81d7b7956b1e516a43ec8f4ababa70354fd91f01e343936a55b75570c3c`
- **Blender:** Blender 5.2.1 built the source with
  `blender_skeletal.py -- MK_IMP` (`blender-build.log`) at unit rig scale.
  - The registry row still carried `visualScale` until the coordinator's
    update, so the build and previews ran through a scratch wrapper that drops
    that key from the looked-up row. No shared file was edited.
  - The preview fixture confirmed that the imp is bound at `Scale 1.0`.
- **Tests:** `python -m unittest tools.monster_models.test_imp` ran 10 tests.
  They pass against the registry row once the coordinator removes
  `visualScale` and sets the formula durations. Before that, the `visualScale`
  and duration assertions fail by design. They cover:
  - a closed single-component skin with seam-consistent, normalised weights of
    at most four influences;
  - the signature anatomy: horns, eyes, lids, smirk teeth, claws, spurs and
    seven spine spikes;
  - an exported height of 45.5 to 48.5 units, no profile `visualScale`, and
    the exported rest equal to SCALE times the design rest;
  - the profile, read via `skeletal_registry.find`, including the rule
    `durations[role] >= ceil(frames*35/fps)`;
  - per-frame clearance within ±32 in exported units, no floor compensation,
    unit scales and loop closure;
  - planted idle and recoil feet, and the alternating walk stance;
  - the predatory crouch: hands below the pelvis and forward, torso pitched,
    tail raised;
  - middle-frame key-pose travel of at least 80% of the clip peak;
  - the limp death on the floor;
  - no degenerate triangles, atlas isolation, and exact IQM and PNG bytes.
- **Galleries:** `--preview --all-angles --distances` at 1920x1080 on Vulkan
  (`preview-vulkan/`) and OpenGL (`preview-opengl/`), 34 captures each, with
  contact sheets. They were re-captured after the scale bake and match the
  accepted look. Every gallery was hashed. The only duplicates are each
  action clip's first and last frames. Superseded galleries were deleted.

Evidence: `artifacts/creature-queue/BRG-M45/`.

## Candid flaws

- **Size at distance:** at 192 units the imp reads as a horned, spiked crimson
  figure with a gold eye glint, but the smirk and lids do not resolve.
- **Leg rim:** from straight ahead, the lighter rim makes the goat legs read
  plum rather than near-black. This is a deliberate trade for floor
  separation.
- **Slice middle frame:** the rake arm is a thin line at distance. The lunge
  and stretched rear leg carry most of that silhouette.
- **Death horn:** the prone death leaves one horn standing about 17 units high,
  which is plausible for the head's orientation.
- **Eyes:** the lids do not blink, so the fallen imp still looks out
  (mostly face-down).
- **Not proven by these galleries:** natural speed, theft, blink, captive or
  thief-machine presentation, and native event timing. User art approval
  remains open.

## Coordinator package archive

The coordinator returned the first delivery (a goofy cartoon gremlin: wide eyes, painted zipper grin, steepled hands, flat hot pink, too small at 192 units) and accepted the sly slit-eyed, spurred, predatory-crouch rework. At gate time the 1.15 enlargement moved from the registry `visualScale` into the exported geometry, so the shared MODELDEF scale count stays intact, and action durations were corrected to engine tics (ceil(frames x 35 / 30 fps)). Round B was integrated and gated as pipeline batch `B` with the kraken, phantom, imp, fury, revenant, golem and tentacle horror (`artifacts/creature-queue/batches/B/gate-summary.json`: 118 tests OK, preservation audit with zero unexpected changes). Both final review packages (`0251f56fe4c6ab6b4bc3932db7e23556a749ae907edfdb6a8faec5b77bbb771c`, 1,216 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M45/final-vulkan/ProjectBroom-review.pk3.archive.json
```
