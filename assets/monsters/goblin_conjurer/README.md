# Goblin conjurer — BRG-M09

Original Project Broom connected goblin anatomy, open hands, ash-brown skin,
ragged wrap, six skin-conforming violet sigils and six skeletal clips.
CC-BY-SA-4.0; no third-party meshes, textures or symbols imported.

Authored through Higgsfield's local background Blender integration, with no
cloud generation credits. The procedural definitions remain the reproducible
master; reconcile any manual Blender edits before regenerating.

- `goblin-conjurer-animated.blend`: editable source, packed RGBA atlas, 18 bones,
  six Actions and emissive sigil preview material.
- `connected-skin.json.gz`: deterministic closed, connected animation cage.
- `animation.json`: exported model/skin hashes, bounds and clip manifest.
- `tools/monster_models/goblin_conjurer_animation.py`: anatomy, skin-conforming
  markings, original atlas and IQM exporter.
- `mod/BrogueDoom/shaders/conjurer-sigils.fp`: runtime material-only pulse.

Rebuild in this order after anatomy changes:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/monster_models/blender_skin.py -- goblin_conjurer
python -m tools.monster_models.goblin_conjurer_animation
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_GOBLIN_CONJURER
python -m tools.monster_models.generate
```

These are the same canonical builders invoked through Higgsfield MCP during
authoring. Normal Python rebuilds consume the checked-in cage without Blender.
The original static OBJ/skin/source remain available for comparison.

The pulse is not a spell timer. Summoning, spectral blades, movement, damage,
visibility and turns remain Brogue-owned. See the
[verification report](../../../docs/goblin-conjurer-animation.md).
