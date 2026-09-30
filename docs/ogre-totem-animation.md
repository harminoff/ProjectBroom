# Ogre totem model and animation

Presentation-only BRG-M20 / `MK_OGRE_TOTEM`. Brogue CE remains authoritative.

## Source facts, art interpretation and proof boundary

Pinned Brogue describes a totem assembled by ancient ogres versed in eldritch
arts and imbued with occult power. `MONST_IMMOBILE` and `MONST_INANIMATE` define
an object with no locomotion. `BOLT_HEALING` and `BOLT_SLOW_2` remain Brogue-owned;
green glyph color is an identity cue, not a requirement for glowing green paint.
The nominal ordinary horde range is depths 12–19. Size and physical materials
are artistic choices rather than authoritative dimensions or new lore.

The original art design is a substantial open shrine built from three dark,
deeply split timber uprights on a fractured stone footing. Thick curved bone
ribs enclose a hanging, weathered greenstone tablet in a heavy circular crown.
Broad aged bronze straps, worn hide bindings, scored timber and uneven drilled
bone tally plaques suggest long use. Its open circular upper silhouette and
three-legged timber frame distinguish it from the goblin totem's carved mask
on a narrow single post. There is no living face, head, eye, limb or weapon.
Nothing emits light, particles or an independent spell effect.

Six cosmetic roles are idle, rest, toll, tremor, recoil and collapse. Idle sways
only suspended pieces; the unused move role is literal rest. Structural support
is fixed in every live pose. Death breaks the upper assembly into a low heap,
while the stone foundation remains fixed. Generic action cues are not claims
that the current bridge distinguishes healing from slowing.

Proof covers rigid physical assembly and attachments, fixed footing and zero
automatic floor lift, correct triangles at all frames, centered 64-unit bounds,
loop closure and recovery, distinct early front/action/death engine views,
deterministic runtime bytes, fresh Blender reopen/deformation/packed skin,
scoped regression/native compilation/fingerprint, and both packaged 34-view
1920x1080 galleries. The existing 2,000-seed census contains no kind20 encounter;
the unchanged conservative route will not be repeated. Natural lifecycle and
individual user art approval remain separate open gates.

Evidence belongs in `artifacts/creature-queue/BRG-M20/`. This assignment reuses an
idle agent after the platform's fresh-agent allocation was exhausted; it is a
focused reassignment with a fresh disk baseline, not a fresh context.

## Delivered source and runtime

- [Editable source](../assets/monsters/ogre_totem/ogre-totem-animated.blend)
  contains 105 named assembled mesh parts, eight bones, six Actions and one
  packed 1024-square diffuse image. It has no linked libraries.
- [Geometry and animation](../tools/monster_models/ogre_totem_animation.py) and
  [original materials](../tools/monster_models/ogre_totem_materials.py) are the
  deterministic master. They reuse shared rigid rig, mesh and noise helpers;
  the ogre shrine's geometry, proportions, marks and material treatment are new.
- [IQM v2](../mod/BrogueDoom/models/monsters/20_ogre_totem.iqm),
  [diffuse](../mod/BrogueDoom/graphics/BRGOGTOT.png) and
  [animation manifest](../assets/monsters/ogre_totem/animation.json) contain
  6,511 vertices and 10,948 triangles. Rest dimensions are
  26.4058 / 44 / 64.45 map units; one unit is one map unit and a cell is 64.
- [Provenance](../assets/monsters/ogre_totem/README.md): original Project Broom
  artwork, CC-BY-SA-4.0. No third-party art was imported. Existing upstream text
  and notices retain their licenses.

The atlas separates split timber, endgrain, worn bone, aged bronze, hide,
fractured stone, greenstone and dark incisions. Modeled rings, staples and a
crown pin give the tablet and bone tallies visible support. The engraved marks
are original geometric shapes, with no asserted alphabet or new lore. No extra
emission or material effect was added, and `GLDEFS` remains byte-identical.

Rigid separate pieces are intentional construction joints. Each triangle stays
on one bone; an organic remesh cage would be inappropriate for this object.
The rig is `root`, `column_L`, `column_R`, `rear_beam`, `crown`, `tablet`,
`tally_L`, `tally_R`. All scales are one. Five footing stones and buried support
stumps stay fixed at every frame, including death. The three main uprights stay
fixed throughout live clips. Small crown recoil is a cosmetic impact cue.

| Role | Clip | Frames / FPS | Behavior |
| --- | --- | --- | --- |
| Idle | idle | 40 / 20 | Small suspended-piece sway; closes its loop |
| Move | rest | 20 / 20 | Exact rest pose, appropriate to an immobile object |
| Attack | toll | 22 / 35 | Tablet and tally motion; returns to rest |
| Alternate action | tremor | 24 / 35 | Oscillation of suspended pieces |
| Hit | recoil | 14 / 35 | Brief tablet/crown reaction, then recovery |
| Death | collapse | 34 / 35 | Structural timbers fall, crown tips and settles |

The crown turns 88 degrees and lowers 36 units during death. Final maximum
height is 21.419554, with the crown assembly below 18 units. All sampled bounds
are inside the centered 64-unit cell: X -28.608459 to 27.343076,
Y -27.576455 to 27.980508, Z 0.15 to 64.606712. Automatic floor lift is zero.
The small deliberate foundation clearance is 0.15 units. These measurements
describe art, not authoritative collision or Brogue dimensions.

## Tests, deterministic export and Blender

The following scoped suite passed **56 tests in 244.679 seconds**:

```powershell
python -m unittest tools.monster_models.test_ogre_totem tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources
```

The seven creature tests cover a distinct construct signature; real ring
topology and matching seams; the tablet ring's attachment to the crown pin
through every frame; fixed foundation and live supports; centered bounds;
visibly tipped, low death; exact unused move/rest; loop/recovery closure; unit
scales; nonzero triangle areas preserved in every frame; and exact model and
texture export bytes. The rig and attachment checks are numerical evidence,
not an exhaustive test of every possible inter-part intersection.

The native frontend compiled successfully before renderer launch:

```powershell
python tools/run_native.py cmake --build .build/uzdoom --config Release -j4
python tools/engine_source.py --root . --record-build .build/uzdoom/Release
```

`native-build.log` records the successful executable link and manifest step;
`fingerprint.log` records verification of the pinned source and integration
patch. The only native table change adds the six presentation roles for kind20.
No bridge ABI or gameplay source changed. Later attachment edits changed only
asset bytes and did not require a different native role table.

Three consecutive final export hash sets match, including the manifest:

| Artifact | SHA256 |
| --- | --- |
| IQM | `a4e9206fcf09185af79980698913ec4a94062f4760ada609241faf03642a256c` |
| Diffuse | `ac47f8dbf613b8b55695817abcceabbb4856257e5208c4ca8904766b3c84f5b9` |
| Animation manifest | `94f1706fe6c53da5d0ae10bb4264f9feda692b63859c881eb8613c6bcf9fde86` |
| Editable Blend | `27fbe5ed0d2dc89d2ce3da6ae22175e2315f730725e43fff9979a926064e3347` |

Only runtime/manifest export determinism is claimed; the Blend hash identifies
the delivered source. `python -m tools.monster_models.ogre_totem_animation`
rebuilds the deterministic runtime. Shared skeletal registration, generator
and bestiary tooling then provide bindings; unrelated hand-refined cards must
be restored from immediate raw-byte backups after bestiary regeneration.

Blender 5.2.1 generated the editable scene and 18 source renders in an isolated
background process. A separate fresh process then reopened the saved file and
ran `artifacts/creature-queue/BRG-M20/verify-fresh-blender.py`. It verified all
eight bones, six Actions, 18 sampled deformations, zero linked libraries and
packed diffuse bytes exactly matching the runtime PNG. Largest vertex error
against the deterministic rig was **0.0000084162 units**. Logs and JSON reports
are retained; a nonfatal extension-cache permission warning did not prevent
the scene save, renders or fresh-open checks.

## Inspected packaged runtime

Final Vulkan and OpenGL runs each captured **34 PNGs at 1920x1080** from the
packaged mod, including before/after, six roles, front/oblique/side/rear and
64/128/192-unit views. Both full contact sheets were inspected. Full-size
final Vulkan close front, OpenGL side and final OpenGL collapse were also
inspected. The coordinator separately inspected final Vulkan front and OpenGL
collapse, accepting the technical art direction. Individual user art approval
is still pending.

```powershell
python -m tools.monster_models.review_skeletal --symbol MK_OGRE_TOTEM --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M20/final-vulkan
python -m tools.monster_models.review_skeletal --symbol MK_OGRE_TOTEM --backend 0 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M20/final-opengl
```

Both packages have SHA256
`682384fca7a5702cf34663750d3d9824ff072ceae766a3748bf7b2217a9e81f4`.
All 1,165 entries matched current source bytes. The independent coordinator
check also confirmed IQM, diffuse, MODELDEF, ZScript and GLDEFS payloads.
Package hashes and checks are retained in `package-verification.json` and
`parent-package-verification.json`. The coordinator may archive these exact
reproducible packages using the shared lossless entry-blob archive.

Every captured stage logged `z=0.00 blocking=0`; image-size assertions passed.
The logs show the selected Vulkan/OpenGL backend on an RTX 3080. They contain
the existing three UCM signed/unsigned comparison warnings and missing menu
texture `>`, with no model or animation load error.

The upper opening, pale bone crown and broad fixed supports distinguish this
asset from the narrow goblin mask totem. The greenstone remains visibly
suspended rather than floating, including its side-view crown pin. The death
reads as a fallen assembly with a low crown and unchanged stone footing.
No gross floor penetration, disappearance or clipping was seen. Close timber
grain repeats visibly; thin engraving and small fittings lose detail at 192
units. Those are retained art limitations, not failures hidden by a distant
camera. Runtime captures are synthetic presentation evidence and do not prove
natural Brogue actions, physical input, or lifecycle timing.

Evidence under [BRG-M20](../artifacts/creature-queue/BRG-M20/):

- `early-vulkan/` and `early-attachment-vulkan/`: early geometry, action,
  collapse and suspension review before the final proof.
- `before-after.png`, `final-vulkan-contact-sheet.jpg`,
  `final-opengl-contact-sheet.jpg` and all full-size final PNGs.
- `studio-idle-01.png`, `studio-toll-11.png`, `studio-collapse-34.png`.
- `gallery-verification.json`, both runtime logs, test/build logs,
  `determinism.json`, Blender verification logs/JSON and `handoff.json`.

## Natural encounter and remaining gates

The completed all-kind ordinary-intent census searched seeds 1–2000 with
1,500-action and depth-15 limits. Kind20 was absent. Its maximum endpoint depth
was 9; the ogre totem's ordinary table range is 12–19. The census file hash is
`7062f8826086cf30e1e40aea8c7b8f4cd8c2956dc9dfa3eda4ec46c67ce3046f`.
`natural-search-status.json` records this reviewed evidence. Per the assignment,
the unchanged route was not repeated. This route limitation does not prove the
creature cannot spawn. No seed/depth/action candidate exists to replay here.

Natural visibility, Brogue-driven healing/slowing, hostile hit/death timing and
normal encounter lighting remain unverified. A justified route reaching the
ordinary range is the next required evidence. The earlier shared transition
crash is fixed and its repair preserved; it is not the current blocker. No
synthetic reveal, health, spawn or simulation override was used to manufacture
a natural pass. Individual user art approval, physical-input acceptance,
standalone comparison, controlled performance measurements and release-installer
testing were not performed. This asset-only task claims no gameplay-parity
change and no completion of those separate gates.

## Preservation and scope

The immediate baseline covers **665 files**. Final comparison found **656
byte-identical files, nine intended shared changes and zero missing files**.
All 67 other creature cards retain their exact prior bytes, including mixed
line endings. All 67 other bestiary/registry entries and all 27 prior skeletal
profiles are semantically identical. Shared model, ZScript, native-table and
index text outside kind20 is unchanged. Existing runtime/source assets remain
unchanged. `preservation.json` and `semantic-preservation.json` contain the
checks and protected hashes.

The nine shared changes are own-kind updates to skeletal profiles, bestiary
index, monster registry, creature model index, kind20 card, MODELDEF, monster
ZScript, generated native role table and bestiary trait/report generation.
The native pending-map barrier, wisp visibility restoration, wall mounting,
engine fingerprint helper, bridge header and GLDEFS match the immediate
baseline. Coordinator archival/index work is separate from these edits.
No queue edit, reset, cleanup, commit, publication or gameplay/ABI change was
made by this assignment.

Reusable lessons: support suspended ornaments with visible pin/ring/staple
geometry in depth as well as in front view; test that the shared attachment
stays inside its physical radii through every pose; keep fixed masonry on the
root while collapsing the timber/crown; and preserve raw card bytes during
shared bestiary regeneration. Model completion here means technically verified
source and presentation assets with explicitly open natural and user-review
gates.

## Review package restoration

The coordinator losslessly archived the review packages after technical acceptance. Restore the final Vulkan package byte-for-byte with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M20/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding `final-opengl` manifest for OpenGL. Screenshots and verification manifests remain directly available.
