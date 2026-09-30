# Pink jelly — BRG-M12

Original Project Broom model and textures, CC-BY-SA-4.0. No imported artwork.
Brogue prose and behavior remain under their existing upstream licensing.

- Master: `tools/monster_models/pink_jelly_animation.py` and
  `pink_jelly_materials.py`.
- `pink-jelly-animated.blend`: editable connected mesh, packed diffuse,
  18-bone rig, six Actions; fresh-open and sampled deformation verified.
- `animation.json`: runtime geometry, bounds, clip and material hashes.
- Runtime: `models/monsters/12_pink_jelly.iqm` and `graphics/BRGPINKJ*.png`.

The skin is a single analytic closed surface. No Blender remesh cache is
required. Original static OBJ/source/skin remain untouched. Rebuild with:

```powershell
python -m tools.monster_models.pink_jelly_animation
python -m tools.monster_models.generate
python -m tools.monster_models.bestiary
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_PINK_JELLY
```

Only idle/flow loop. Smear, drench, recoil and collapse are presentation clips.
Brogue owns caustic attacks, cloning, damage and death. The opaque surface has
no fullbright, emission or transparency sorting; its specular material uses
existing scene lights. Blender's studio material approximates this sheen.

See the [model report](../../../docs/pink-jelly-animation.md) for actual
renderer, encounter, deterministic and preservation evidence and limitations.
