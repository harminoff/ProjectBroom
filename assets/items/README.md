# Project Broom pickup art

Start with the [indexed pickup roster](../../docs/pickup-model-index.md) and
[refresh report](../../docs/pickup-model-refresh.md). The set covers 100 item
kinds and five unidentified forms. `pickups.blend` contains 105 origin-centered
scenes with named editable parts, a packed diffuse texture, and a shared
preview-only 64-unit floor. Select a scene by the registry's runtime class.

Original Project Broom procedural geometry and texture: CC-BY-SA-4.0 under
[ASSETS-LICENSE.md](../../ASSETS-LICENSE.md). Floor weapons reuse original
`tools/weapon_models/viewmodel.py` components, without arms or poses. No external
models, textures or reference-game resources were imported. Exact Brogue prose
in the index is extracted from the pinned upstream source, whose license remains
unchanged. Numeric sizes, ornamental strokes and colors are artistic inference.

The five hidden-identity categories retain a single generic model each. Known
effect ornaments are not randomized Brogue flavor names, potion colors, wood
species or gems. The existing bridge alone selects the safe known/generic class.
Glass and crystal are opaque diffuse approximations, not transparent/PBR assets.

Rebuild runtime art and index:

```powershell
python -m tools.pickup_models.generate
python -m tools.pickup_models.index
```

Rebuild the editable source in an isolated process (never clears live Blender):

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/pickup_models/blender_source.py -- --render
```

The Python definitions are the reproducible master. Reconcile manual Blender
changes before regeneration. Export only the scene's ASSET collection, never
its stage. OBJ is `(X, Z, -Y)` from Blender; the single runtime skin is
`graphics/BRGPICKS.png`. Legacy `BRGITEMS.png` stays intact for weapon UI markers.
