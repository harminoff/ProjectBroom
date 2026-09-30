# Pink jelly model and animation

Presentation-only BRG-M12 / `MK_PINK_JELLY` work.

## Source facts and intended proof

Brogue describes a mass of caustic pink goo slipping across the ground in search
of a warm meal. Its existing strings include absorbing, Feeding, smears, slimes
and drenches. `MA_CLONE_SELF_ON_DEFEND`, `MONST_NEVER_SLEEPS` and purple blood
remain Brogue behavior. The ordinary horde range is depth 4–13. A large flag is
not a numerical size specification.

The art interpretation is an asymmetric, connected, low gelatinous mass with
a broad lobed contact skirt, sagging folds, shallow hollows, trapped-looking
inclusions and coral/rose/burgundy marbling. It has no invented eyes, mouth,
limbs, aura, projectile or independent splitting action. Opaque wet material
keeps the surface readable; existing scene lights provide its specular sheen.
The authored dimensions, folds and pigments are artistic decisions.

Six cosmetic roles are idle, flow, smear, drench, recoil and collapse. Idle and
flow loop. Existing copied state/events select clips; attack variants do not
claim the bridge distinguishes Brogue's verbs. New daughter creatures, when
Brogue creates them, use the existing stable-ID synchronization. No ABI,
combat, collision, RNG, topology or timing rule changes are intended.

Planned proof: connected topology and identical seams, floor/corridor and
animation bounds, cyclic flow, attack recovery and death settling, deterministic
IQM/maps, Blender fresh reopen and sampled deformation, native table compilation,
packaged Vulkan/OpenGL before/after/clip/angle/distance inspection, and an
ordinary-intent natural encounter attempt. Evidence belongs in
`artifacts/creature-queue/BRG-M12/`. Individual art approval remains the user's.

## Delivered model

- One closed connected analytic skin: 4,561 runtime vertices, 9,024 triangles,
  18 bones and six clips. Organic folds and blisters belong to the skin itself;
  there are no overlapping body balls or detached details. No remesh cage or
  extra bake dependency is needed.
- Rest extents are 51.3996 / 44.4528 / 30.8001 units. Across all authored frames,
  X stays within -26.271 to 27.799 and Y within -22.764 to 24.169. The contact
  skirt stays about 0.12 above the floor. Settled death height is 3.816 units.
  These bounds are artistic presentation bounds, never gameplay collision.
- Original 1024-square diffuse and specular maps plus a flat normal map retain
  the sculpted normals. Broad density mottling, wine-dark folds and rounded
  pockets replaced an initially uniform fine-line texture after engine review.
  The opaque material has no fullbright or emission. Specular highlights depend
  on scene lights; the unlit gallery does not establish a glass-like surface.
- Editable source is `assets/monsters/pink_jelly/pink-jelly-animated.blend`.
  Runtime IQM is `mod/BrogueDoom/models/monsters/12_pink_jelly.iqm`. Python
  anatomy/material modules remain the deterministic master. All prior static
  reference files remain untouched. Artwork is original CC-BY-SA-4.0.

## Verification, 2026-09-26

Evidence root: `artifacts/creature-queue/BRG-M12/`.

1. Native compilation passed with
   `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
   The build fingerprint was refreshed only after success. The generated K12
   presentation row is the only native integration change for this model.
2. **55 tests passed** with
   `python -m unittest tools.monster_models.test_pink_jelly tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
   The six jelly checks cover manifold closure, one connected component, Euler
   characteristic, positive triangle area/orientation at every authored frame,
   floor/64-unit envelope, exact seams, looping/recovery, normalized unit-scale
   weights and all runtime bytes. A first pass caught crown pinching and tiny
   seam differences; shared crown/floor controls and canonical angle wrapping
   fixed them before the passing suite.
3. Isolated background Blender 5.2.1 freshly reopened the saved source with six
   Actions, packed diffuse and no linked libraries. Eighteen sampled poses
   matched the runtime solver with maximum vertex error 0.000003433 units.
   No existing desktop document was changed. The known extension-cache write
   warning is nonfatal. Source-file byte determinism is not claimed.
4. Three runtime builds reproduced IQM, diffuse, normal, specular and manifest
   bytes exactly. `determinism.json` records complete hashes. The connected
   surface comes directly from the analytic generator rather than remeshing.
5. Both Vulkan and OpenGL launched the actual deterministic packed resources.
   Each gallery captured 34 stages: static before, three samples of every clip,
   front/side/rear views, and 64/128/192-unit distances. All subjects reported
   `blocking=0`. Both contact sheets and representative full-resolution images
   were inspected, including collapse and distance views. No new missing model
   or texture errors appeared; existing menu/minimap warnings remain. Both
   PK3s are byte-identical; IQM, three maps, MODELDEF, ZScript and GLDEFS match
   source (`package-verification.json`).
6. Natural Vulkan encounter: seed 26, depth 4, 222 ordinary intents reach
   player 66,14 and jelly ID62 at 68,14, hash `fd84c26107328c93`. Three further
   `E` intents approach and hit twice. Brogue creates daughter ID75 at 68,15,
   then ID76 at 67,15. Original HP changes 50 → 23 → 10; player remains alive
   at 11/30. Copied events select recoil, smear and drench. Final hash is
   `a07209e57c20cd6d`; repeated headless replay agrees. The captured close and
   resolved views show the real daughters and normal scene lighting. The
   observer stays at the real player eye and does not spawn/reveal/reposition
   creatures or modify health. Diagnostic routing may use copied hidden map
   knowledge to choose intents; Brogue still validates every action.
7. The existing seed-26 startup package passed the map/topology verifier with
   `python tools/mapcompiler/verify.py --input generated/seed-26/brogue-dungeon.json --package generated/seed-26/startup/ProjectBroom-seed-26.pk3 --startup`.
   No map generation or terrain behavior changed.

The initial natural OpenGL route was attempted twice with a bounded 160-second process
deadline. Both stalled before the jelly encounter during the depth-2 transition.
The first ended at revision 37, hash `89db5fb58f622db8`; the retry ended at
revision 38, hash `5324bdffa4f57252`. Neither produced a script error or reached
the jelly. Logs remain under `natural-opengl/` and `natural-opengl-retry/`, with
the retry exception in `natural-opengl-retry-result.log`. The coordinator later
identified the shared native level-transition lifetime defect and verified a
[narrow repair](creature-queue-transition-crash.md). OpenGL then completed the
222-intent route plus three ordinary E intents, reproduced real daughter IDs
75/76 and final hash `a07209e57c20cd6d`, captured all five views and exited normally.
The coordinator inspected the resolved image. Evidence and intent-order checks
are in `artifacts/creature-queue/BRG-M12/after-transition-opengl`. This replay used
the later totem review package with the same jelly asset bytes; its package hash
is `c0163c08048130ee3e8d61b4d94a33781a803c0896a418c0686a796cfe80e72e`.

Final hashes:

```text
IQM a0f1ea8a1fdc3f85501c3e40714b640548e758c979842f56b24181154939baa8
PNG e11f9d6986aa0f4fb96f48f08cffc9dc677c209c5915d8195ef3c54d816d2c20
PK3 454fde2a7cb3e581058c3743989763f7fd7b2b65aaf02ac7df4e9a53c8d36f9f
```

Reproduce gallery captures with:

```powershell
python -m tools.monster_models.review_skeletal --symbol MK_PINK_JELLY --backend 1 --all-angles --packaged --distances --output artifacts/creature-queue/BRG-M12/final-vulkan
python -m tools.monster_models.review_skeletal --symbol MK_PINK_JELLY --backend 0 --all-angles --packaged --distances --output artifacts/creature-queue/BRG-M12/final-opengl
python -m tools.monster_models.review_pink_jelly --backend 1 --package artifacts/creature-queue/BRG-M12/final-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M12/natural-vulkan
```

## Preservation and reusable lessons

The narrow pre-edit inventory contains 347 hashes and immediate backups of
shared generated files/cards. The final comparison preserves 337 unrelated
files, all 67 other bestiary entries and every other creature card. The known
goblin-conjurer card normalization was restored from the immediate backup,
never from HEAD. Coordinator-owned queue, handoff and route-limit changes are
outside this model's edits. No commits, publishing or global cleanup occurred.

Shared changes are the profile/registry/bestiary entry and traits, generated
MODELDEF/ZScript/native row, creature index/card and the dedicated GLDEFS
material. Geometry, materials, tests and encounter runner are separate jelly
modules. The bridge ABI and simulation source remain unchanged.

For later gel-family work, a continuous parameterized surface provides closed
organic anatomy without remeshing. Use shared pole controls: angularly varying
controls converging onto one pole can invert the last triangle ring in recoil.
Wrap both the geometry angle and diffuse meridian identically. Separate low
contact skirt motion from upper mass inertia and use translations instead of
unsupported scale. Verify every frame's triangle orientation and the final
flattened surface, not just positive rest topology. Broad tonal patches remain
more useful than fine wrinkles at 128–192 units. Real cloning is proven by
authoritative stable IDs and matching hashes, not by manually spawning a pair.

[Engine before/after](../artifacts/creature-queue/BRG-M12/before-after.png),
[Vulkan contact sheet](../artifacts/creature-queue/BRG-M12/final-vulkan-contact-sheet.png),
[OpenGL contact sheet](../artifacts/creature-queue/BRG-M12/final-opengl-contact-sheet.png),
[natural split](../artifacts/creature-queue/BRG-M12/natural-vulkan/close.png).

The coordinator losslessly archived the three review PK3 files to shared ZIP
segments after acceptance. Their `.pk3.archive.json` manifests and all capture
evidence remain in place. An exact restoration of the final package was checked
against the recorded SHA-256. To restore a package before replaying a natural
capture, run `python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M12/final-vulkan/ProjectBroom-review.pk3.archive.json`.
The shared `artifacts/creature-queue/.review-package-blobs` directory is required;
do not delete it. See `package-archive-verification.json` for the three records.

Natural encounter verification now passes on both renderers. Individual art approval, manual input acceptance,
natural death, standalone side-by-side comparison, controlled frame-time
benchmarking and release-installer packaging also remain open. The gallery death clip is verified; this does not claim
a natural death capture or exhaustive cloning/combat parity coverage.
