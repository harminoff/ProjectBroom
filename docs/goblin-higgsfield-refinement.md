# Goblin refinement through Higgsfield Blender

September 13, 2026. Contribution category: presentation only.

The goblin now has a firmer chin and jaw, a shorter nose, hollow lower cheeks,
more legible mouth, and subtle chest/sternum shaping. Its diffuse atlas has
darker brown skin, irregular pores and creases in place of repeated horizontal
stripes. The ragged wrap has folds, a rolled edge and short ties. These are
original art refinements of the existing Brogue creature, not new equipment,
armor or gameplay abilities.

The 19 bones, six clip roles, axes, scale, spear grip and rest extents remain
unchanged. The connected body remains a closed 2,805-vertex / 5,606-face cage.
The complete runtime mesh has 6,770 vertices and 10,982 triangles, up from
6,349 vertices and 10,274 triangles. Much of the added geometry is the rolled
cloth edge and ties. The atlas remains a single 1024px diffuse texture.

## Actual Higgsfield usage

The installed cloud plugin supplied `/use-blender` and its installation and
verification references. Its local integration is a separate package:
`fnf-blender-mcp@0.2.0`, installed under
`C:/Users/harmi/AppData/Local/Higgsfield/blender-mcp`.
It ran with the bundled Node 24.19.0 and local Blender 5.2.1 LTS.
No cloud generation job or subscription was used for this refinement.

This task used a local stdio MCP client in
`artifacts/goblin-higgsfield/mcp_client.py` to call the actual Higgsfield server.
It is not registered as a new global Codex MCP server. The server returned
`higgsfield-use-blender` version 0.2.0; `bl_health` verified its own background
Blender process. `bl_open_project`, `bl_get_scene_summary`, and `bl_get_object`
inspected the existing source. The `blender-scene`, modeling, materials, and
lighting-camera guidance was read. `bl_execute` ran the canonical procedural
refinement and connected-skin rebuild; `bl_save_project` saved a review copy,
and `bl_render` produced the inspected before/after and turnaround images.

The procedural Python remains the reproducible master. Editable source and
runtime export therefore agree; this is not an unexported manual Blender edit.
Existing desktop Blender windows and unsaved scenes were not used or replaced.
No third-party geometry or textures were imported. Original assets retain
CC-BY-SA-4.0; the locally installed tool retains its own MIT license.

## Evidence and verification

All pass-specific evidence is under `artifacts/goblin-higgsfield/`.
The `before/` directory preserves the input source, model, texture, bake,
generator code and documents. `before/front-matched.png` and `front.png` use
the same camera and lighting. `side.png` and `back.png` provide form checks;
the studio side view clips the far spear tip, whose complete bounds and
appearance are checked in the engine gallery.

- The saved source was reopened and checked for 19 bones, six Actions,
  packed texture and no linked libraries. Eighteen sampled Blender poses
  matched the runtime solver within 0.000012 map units.
- A second fresh Higgsfield Blender process reproduced the connected bake,
  IQM and PNG byte for byte. See `determinism-results.json`.
- `python -m unittest tools.monster_models.test_goblin tools.monster_models.test_skeletal tools.test_broguedoom_resources tools.monster_models.test_connected_skin tools.monster_models.test_creatures`
  passed all 52 tests, checking the goblin, rig, resources, connected cages
  and roster consistency.
  The first run exposed stale generic cage-test assumptions: it incorrectly
  included eel/bloat surfaces and expected quadruped limb names for goblins.
  That test now scopes itself to the five baked-cage species and checks the
  goblin's actual arm/leg chains. The goblin's recorded art hashes were refreshed.
- `python -m tools.monster_models.review_skeletal --symbol MK_GOBLIN --backend 1 --all-angles --distances --packaged --output artifacts/goblin-higgsfield/vulkan`
  and the corresponding backend `0` / `opengl` command each captured 34
  actual UZDoom poses and 64/128/192-unit views. Packed model, skin and bindings
  match source bytes. Representative front, attack, death and distance views
  were inspected. All gallery subjects report nonblocking presentation.
- `python -m tools.monster_models.review_goblin --backend 1 --package artifacts/goblin-higgsfield/vulkan/ProjectBroom-review.pk3 --output artifacts/goblin-higgsfield/encounter-vulkan`
  exercises the established ordinary seed-27 route. The helper now accepts
  explicit package/output paths so prior review evidence is preserved.
  This command and its backend `0` / `opengl` counterpart both passed:
  two goblins are naturally visible, with movement and Brogue-resolved attacks.
  Repeated headless output and each renderer's final state agree at turn 74,
  depth 3, hash `cc14f9d0bbb31e67`. This is the unchanged preceding baseline.

Current SHA-256 values:

```text
IQM  c76c757262d4746855a123550c1939e3bdd9819ae24d6361cd8310903e39a5fb
PNG  332f47a0d7720a4c7ca53bc5cd04181829145ce60c92794423be39c11a6135d1
Cage d5b5f53391d8c1fbc761560ba1469bb5b9b3e5ef9772f17799579a3ddd9883a1
```

## Authority and remaining acceptance

Gameplay outcomes cannot change through these edits. Brogue still owns all
movement, attacks, targeting, damage, visibility, turns and RNG. No bridge,
native frontend, actor bindings, collision or simulation code changed.

The existing native engine binary was reused; native compilation was not
repeated for this asset-only update. Verification includes review packaging
and real launches, not a new full release distribution. Individual art
approval, physical-input acceptance, standalone comparison, exhaustive natural
death/penetrating-attack coverage and comparative performance measurements
remain unperformed. Close-up UV/material boundaries inherited from the
connected-cage workflow remain visible in places.
