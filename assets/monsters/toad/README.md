# Toad — BRG-M13

Original Project Broom artwork, CC-BY-SA-4.0. No imported meshes or textures.
Brogue prose and rules retain upstream licensing and remain authoritative.

- Master: `tools/monster_models/toad_animation.py` and `toad_materials.py`.
- `connected-skin.json.gz`: reproducible closed skin bake, required by builds.
- `toad-animated.blend`: editable source with packed diffuse, 17-bone rig and
  six Actions. The studio material approximates the runtime wet surface;
  Blender lighting does not establish in-game appearance.
- `animation.json`: dimensions, geometry counts, clip bounds and asset hashes,
  including the runtime normal/specular maps.
- Runtime: `models/monsters/13_toad.iqm`, `graphics/BRGTOAD.png`,
  `graphics/BRGTOAD_N.png`, `graphics/BRGTOAD_S.png` inside the static mod.

After changing anatomy/weights, bake with isolated Blender and one thread:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python tools/monster_models/blender_skin.py -- toad
python -m tools.monster_models.toad_animation
python -m tools.monster_models.generate
python -m tools.monster_models.bestiary
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_TOAD
```

The six roles are idle, crawl, slime, slam, recoil and death. Only idle/crawl
loop. Their names describe cosmetic poses, not extra gameplay actions or an
exact attack-verb signal. Slime has no particles, world light, projectile or
damage. Runtime highlights use existing lights. See the
[verification report](../../../docs/toad-animation.md) for actual evidence.
