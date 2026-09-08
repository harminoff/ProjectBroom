# Hand model refinement

Presentation-only change, researched and verified on 2026-09-06. Brogue CE
remains authoritative. No bridge, input, action timing, collision or RNG code
changes are part of this work.

## Research and diagnosis

[Proko's hand construction lesson](https://www.proko.com/course-lesson/how-to-draw-hand-bones-anatomy-for-artists)
explains the planar palm, curved knuckle arrangement, unequal finger lengths,
tapering phalanges and separate thumb structure.
[His surface-form lesson](https://www.proko.com/course-lesson/how-to-draw-hands-details-for-realistic-hands)
distinguishes softer finger pads from the joint structure. These inform the
original glove geometry; no reference mesh, image or texture was imported.

The previous generator used an oval palm, four equal tube paths, oversized
separate knuckle pads and identical anatomy for both hands. Release moved the
finger paths sideways rather than extending their joints. The target is a
readable gloved grip: flattened palm, distinct fingers, opposing thumb, mirrored
left hand and smooth release, with existing sleeves and held objects preserved.

## Implementation

`tools/weapon_models/viewmodel.py` now builds a bevelled palm loft, staggered
finger roots with individual lengths and taper, a smaller thumb web, and a
joint-based extended pose. The palm and glove digits remain overlapping closed
parts, not a welded bare-hand mesh. Left-hand geometry and winding are mirrored
before the existing HUD axis conversion. Wrist roots still meet the existing
cuffs. The atlas, sleeves, cuffs, weapon meshes, placements and timing are
unchanged.

`python -m tools.weapon_models.generate` updates all 15 weapon and both device
MD3/OBJ pairs. The existing Blender generator also recreated
`assets/weapons/hero-weapons.blend` with the revised editable hands and poses.
Original Project Broom art remains CC-BY-SA-4.0, attributed to Project Broom
contributors under `ASSETS-LICENSE.md`. Research references are not asset sources.

## Verification

- `python -m unittest tools.weapon_models.test_viewmodel tools.test_broguedoom_resources`:
  40 tests passed, including exact runtime MD3/OBJ reproduction for weapons and
  devices, all pose layouts, triangle integrity and left-hand winding.
- Baseline geometry hashes prove every non-hand vertex, face, UV and material
  matches across all 240 weapon poses. A regression test retains those hashes.
- One hand decreases from 1,362 to 1,328 triangles; the number of named surfaces
  also decreases. This is a geometry count, not a frame-time measurement.
- The original seed-1 dagger was captured with ordinary runtime assets. Further
  captures hold dagger, broadsword, spear, dart, release and staff poses through
  a temporary MODELDEF override of the starting dagger. These are actual UZDoom
  framebuffers, not Blender renders or evidence of Brogue equipping those items.
- All 24 fixed-pose captures completed on the requested Vulkan/OpenGL backends.
- Live `scripts/test-staff-ui.ps1 -Throw` checks passed on both renderers:
  cancellation preserved the copied state and throwing advanced one revision
  and one turn. Captures/logs are in `live-throw-vulkan` and `live-throw-opengl`.
- Before/after captures and renderer logs are under `artifacts/hand-model/`.
  The baseline archive preserves the previous assets and dirty worktree inventory.

Reproduce the fixed-pose captures with the built local UZDoom and seed-1 campaign:

```powershell
python -m tools.weapon_models.capture --backend 1 --output artifacts/hand-model/after
python -m tools.weapon_models.capture --backend 0 --output artifacts/hand-model/after
```

The capture tool also accepts `--baseline-archive artifacts/hand-model/baseline.zip`.
Backend 1 is Vulkan, 0 is OpenGL. Captures isolate settings and save paths.

View the [primary comparison](../artifacts/hand-model/hand-before-after.png),
[Vulkan matrix](../artifacts/hand-model/comparison-vulkan.jpg), and
[OpenGL matrix](../artifacts/hand-model/comparison-opengl.jpg).

## Limits

This preserves the existing stylized leather gloves, atlas and first-person arm
poses. It is not a new full-body skeleton or a photorealistic hand sculpt. The
shared palm dimensions still serve every handle size. This asset-only change
did not rebuild the native engine or create a new packaged release. Frame-time
benchmarking and a standalone gameplay comparison were not run for this change.
