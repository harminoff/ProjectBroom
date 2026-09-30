# Goblin totem model and animation

Presentation-only BRG-M11 / `MK_GOBLIN_TOTEM` work.

## Source facts and intended proof

Brogue describes a makeshift goblin totem imbued with shamanistic power.
`MONST_IMMOBILE` and `MONST_INANIMATE` establish a planted object, not a
walking goblin. Haste and spark remain Brogue-owned bolts; this asset does
not emit independent projectiles, auras, lights, or gameplay effects.

The art interpretation is a crooked split timber post with pegged crosspieces,
a broad carved wooden mask, chipped bone crown, hemp lashings, dangling bone
charms, ragged ochre cloth and an uneven stone footing. Layered wood grain,
split edges, drilled bone holes and irregular cord coils distinguish it from
the living goblin/conjurer silhouette. Dimensions, pigments and ornaments are
art decisions, not new Brogue facts. The mask is an object, not a living face.

Six cosmetic roles are idle, rest, rattle, shudder, recoil and collapse. The
unused move role rests; the footing stays planted throughout live poses.
Only hanging objects move gently at idle. The existing event selector owns
when an action pose is shown; rattle/shudder are not a claim of bolt-specific
cast synchronization. No gameplay, ABI, topology, AI or timing changes.

Planned proof: fixed footing, rigid accessories, normalized unit-scale rig,
loop/recovery and noninverting geometry, 64-unit clearance, deterministic IQM
and textures, packed/freshly reopened Blender source and sampled deformation,
native table compilation, inspected packaged Vulkan/OpenGL before/after,
poses/angles/distances, and a bounded ordinary-intent natural encounter search.
Evidence root: `artifacts/creature-queue/BRG-M11/`. User art approval remains open.

## Delivered model

- 89 named assembled parts, 5,709 runtime vertices, 9,678 triangles, nine bones
  and six clips. All parts are rigidly weighted to their physical hinge or
  timber member. Separate pieces are intentional joinery; this inanimate
  structure has no organic skin cage. Unit bone scales are preserved.
- Rest extents are 17.8834 / 30.2326 / 49.9077 map units. The full authored
  sequence fits X -20.524 to 19.300 and Y -15.135 to 16.139, within one 64-unit
  cell. Footing stones remain at exactly the same coordinates in every frame;
  live stump timber also remains fixed. Floor clearance is 0.12 and the final
  broken assembly is 14.965 units high. These are art bounds, never collision.
- Original 1024-square diffuse has padded timber, carved-mask, bone, hemp,
  ochre-cloth, stone, recess and cut-end regions. It reuses the goblin family's
  palette/shading helpers. There is no emissive material, normal-map dependency,
  world light, aura or projectile. Deep carved sockets are dark wood recesses.
- `assets/monsters/goblin_totem/goblin-totem-animated.blend` is the editable
  source. Deterministic masters are `goblin_totem_animation.py` and
  `goblin_totem_materials.py` under `tools/monster_models/`. Runtime output is
  `mod/BrogueDoom/models/monsters/11_goblin_totem.iqm`, with `BRGTOTEM.png`.
  Existing static OBJ/texture/Blend references remain untouched.

## Verification, 2026-09-26

1. **56 tests passed**:
   `python -m unittest tools.monster_models.test_goblin_totem tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
   The seven focused checks cover distinctive construction, rigid weights,
   exact unused move rest, fixed support, floor/corridor bounds, six roles,
   action recovery, unit scale, triangle area at every frame, outward carved
   surfaces, and complete exported IQM/atlas bytes. A first test exposed a
   concave cloth notch triangulated by a polygon fan. Ear clipping corrected
   the actual geometry; the passing final suite uses that result.
2. Native compilation passed with
   `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
   `python tools/engine_source.py --root . --record-build .build/uzdoom/Release`
   refreshed the fingerprint only after success. The generated K11 profile row
   is the sole native integration delta; no frontend behavior or ABI changed.
3. Isolated background Blender 5.2.1 rebuilt and freshly reopened the final
   `.blend`: six Actions, nine bones, packed diffuse and no linked libraries.
   Eighteen sampled source poses matched the shared runtime solver with maximum
   vertex error 0.000008849 units. No live desktop document was modified. The
   existing extension-cache permission warning was nonfatal and global settings
   were unchanged. Blender file byte determinism is not claimed.
4. Three runtime builds reproduced IQM, diffuse and manifest bytes exactly.
   `determinism.json` contains all three complete hash sets. This assembled
   construct needs no remesh cache or supplemental material maps.
5. Both Vulkan and OpenGL launched the actual deterministic packed resources
   and each captured 34 views at 1920x1080: static before, three samples of each
   clip, front/side/rear, and distances 64/128/192. All subjects log `blocking=0`.
   Both final contact sheets and representative full images were inspected.
   The mask, crown, hanging charms and rigid post remain identifiable, including
   from behind; the collapse settles on the unchanged stone footing. Both PK3s
   match byte-for-byte and their IQM, diffuse, MODELDEF and ZScript match source.
   Existing minimap/menu warnings remain; no new model or texture errors appear.
6. The existing seed-26 startup map passed the topology/package verifier:
   `python tools/mapcompiler/verify.py --input generated/seed-26/brogue-dungeon.json --package generated/seed-26/startup/ProjectBroom-seed-26.pk3 --startup`.
   No map generation or terrain code changed.

Final hashes:

```text
IQM f2a301da77bbb62627471575a4f773a0d35badd68d42bab419bf6f644537c82c
PNG f5c2d976cbdc04d9397e31ad7ade9c409ba58035662cd58a62d27d8b8573c36b
PK3 c0163c08048130ee3e8d61b4d94a33781a803c0896a418c0686a796cfe80e72e
```

## Natural encounter and remaining acceptance

A bounded search of seeds 1–26, at most 900 ordinary intents and depth 6 per
seed, found a directly visible totem on seed 26, depth 5. Repeated route-helper
runs and an independent bridge executable replay agree after 292 intents:
revision 293, turn 288, player 58,17 at 20/30 HP, totem ID81 at 61,17, state hash
`2dcb11e9c4d62ec5`. Three natural goblins are also directly visible. The route
uses copied snapshots to select intents; Brogue validates every action. No
spawn, reveal, health, status or RNG overrides are used. This is diagnostic
headless evidence; successful renderer follow-up is recorded below.

Initially, two Vulkan attempts and one OpenGL attempt failed before the depth-5 encounter,
at the BRG01-to-BRG02 transition. The last ordinary command reaches revision 37,
turn 34, player 62,26, hash `89db5fb58f622db8`; the log ends after the depth-2
initial terrain commit. The coordinator inspected the actual fatal-error dialog
and saved `native-crash-dialog.txt`: native `C0000005` access violation reading
`0000002800000027`, instruction `00007ff64474f3d3` (RVA `0x65f3d3`). OpenGL also
showed `UZDoom Very Fatal Error` at the same transition. This is a native crash,
not slow traversal, a script error or proof of a missing totem resource. The
210-second deadline merely bounds the Vulkan retry while its fatal dialog is
open. The confirmed crashed OpenGL process (PID31992) was explicitly terminated
after recording its fatal window title and matching transition log; process
absence was verified. Computer Use did not expose that dialog as a targetable
window, so a separate exact OpenGL fault address was not extracted.
Logs, cleanup and process metadata remain in the original capture directories.
The shared [transition repair](creature-queue-transition-crash.md) subsequently
closed this blocker. Both Vulkan and OpenGL naturally reached totem ID81 on
depth five, retained every one of the 292 route intents, matched the headless
hash above, captured encounter/active/resolved views and exited normally.
Two ordinary follow-up waits matched hashes `f216cb965c1fbb21` and
`66b6f3a2ec52154d` on both renderers. The coordinator inspected the natural
Vulkan encounter and OpenGL resolved images. The fixture adds only missing
depth-five MAPINFO metadata; the original startup package remains unchanged.
Evidence is under `artifacts/creature-queue/transition-crash/verified-vulkan`
and `verified-opengl`. The observer only aims from the real player eye and
does not relocate creatures.

User art approval, manual input acceptance, natural death/exhaustive bolt-event
coverage, standalone side-by-side comparison, controlled frame-time measurement
and release-installer packaging remain open. The verified gallery collapse is
not evidence of a naturally killed totem, and the action clips do not claim
bolt-specific synchronization.

## Preservation, reproduction and lessons

The pre-edit inventory hashes 441 files and includes immediate copies of shared
records and creature cards. Final comparison preserves 431 byte-for-byte; nine
changed baseline files belong to this model and `review_skeletal.py` belongs to
the coordinator's resolution-support change. All 67 other bestiary entries,
all 11 prior profiles, other creature cards and prior model/texture outputs are
preserved. The conjurer card's generator normalization was restored from the
immediate pre-task copy, never from HEAD. No commits, publishing or cleanup.

Shared model changes are the profile, registry/bestiary entry/traits, native
table row, generated MODELDEF/ZScript bindings and creature index/card. The
coordinator owns the queue, handoff, capture resolution and archive helpers;
those are not this model's edits. All mesh/texture artwork is original Project
Broom work under CC-BY-SA-4.0. Upstream Brogue text and notices are unchanged.

For later construct models: keep stones and buried supports on a fixed root,
give the unused locomotion role literal rest, and hinge only real separated
pieces. Death may disconnect broken timber without inventing locomotion. Check
every frame's footing coordinates, not just floor-minimum bounds: the shared
exporter's automatic floor lift can otherwise raise the whole structure when
one tilted member clips the floor. Use proper concave polygon triangulation
for torn cloth. Distinct bone/rope/wood silhouettes remain useful at 192 units.

```powershell
python -m tools.monster_models.review_skeletal --symbol MK_GOBLIN_TOTEM --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M11/final-vulkan-v2
python -m tools.monster_models.review_skeletal --symbol MK_GOBLIN_TOTEM --backend 0 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M11/final-opengl
python -m tools.monster_models.review_goblin_totem --backend 1 --package artifacts/creature-queue/BRG-M11/final-vulkan-v2/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M11/natural-vulkan-retry
```

[Engine before/after](../artifacts/creature-queue/BRG-M11/before-after.png),
[final Vulkan views](../artifacts/creature-queue/BRG-M11/final-vulkan-v2-contact-sheet.jpg),
[final OpenGL views](../artifacts/creature-queue/BRG-M11/final-opengl-contact-sheet.jpg),
[editable-source studio view](../artifacts/creature-queue/BRG-M11/studio-idle.png).

The coordinator losslessly archived the three review packages after validation;
all screenshots/logs remain. Restore the exact final package before a natural
replay with `python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M11/final-vulkan-v2/ProjectBroom-review.pk3.archive.json`.
Shared ZIP segments under `artifacts/creature-queue/.review-package-blobs` and
the archive manifests are required for restoration and must be retained.
