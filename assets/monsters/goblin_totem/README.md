# Goblin totem source

Original Project Broom BRG-M11 mesh, 1024-square diffuse and animation artwork,
licensed CC-BY-SA-4.0. No third-party artwork or reference mesh is imported.
Brogue's description remains under its existing upstream license.

The editable `goblin-totem-animated.blend` contains nine bones, 89 named mesh
parts, six Actions and its packed diffuse. Python is the deterministic master:

```powershell
python -m tools.monster_models.goblin_totem_animation
python -m tools.monster_models.skeletal_registry
```

Use the shared background Blender exporter to rebuild the editable file.
See [the model report](../../../docs/goblin-totem-animation.md) for exact
verification, evidence and open acceptance gates.

The split timber, wooden mask, crown, hemp, drilled bone charms and cloth are
rigid assembled objects. The root and footing remain fixed in every authored
frame. The unused move role is exact rest. Only separated hanging objects sway
at idle; no living anatomy or independent spell effect is simulated. Haste,
spark, visibility, damage, death and all turns remain Brogue-owned.
