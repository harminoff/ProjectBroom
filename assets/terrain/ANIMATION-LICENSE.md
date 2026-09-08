# Original terrain animation assets

Author: Project Broom contributors (procedurally authored for this project).
License: CC0-1.0, https://creativecommons.org/publicdomain/zero/1.0/

`tools/terrain_assets.py` deterministically creates eight OBJ models under
`mod/BrogueDoom/models/terrain` and `graphics/BRGICE.png`, `BRGTFLAM.png`, and `BRGTCLOUD.png`. No reference-game
geometry, external artwork or downloaded meshes are used. Existing BRGBRIDGE,
BRGROCK and BRGSEARCH skins retain their existing provenance and licensing.
Generated MODELDEF entries are original configuration under the same dedication.

`tools/statue_models.py` additionally authors four original robed statue meshes
(`statue_marble.obj`, `statue_cracked.obj`, `statue_broken.obj`, `statue_demon.obj`)
and four deterministic shaded stone atlases (`BRGSTMAR`, `BRGSTCRK`,
`BRGSTBRK`, `BRGSTOBS`).
These are CC0-1.0 under the same dedication. All geometry and marble veins are
procedural original work; no downloaded sculpture, scan or texture is used.
The OBJ files are editable/importable in Blender; the Python source is the
canonical deterministic asset source. Dimensions and sculptural clothing are
presentation choices, not new Brogue lore or gameplay properties.
# Wall torches

`tools/torch_models.py` generates original Project Broom iron brackets, wooden
shafts and flame sheets, plus BRGTORCH, BRGTORFL and BRGTHAFL textures. These
assets are dedicated to the public domain under CC0-1.0. No imported meshes or
textures are used. Brogue's existing terrain catalog supplies the identities.

## Iron manacles

`tools/manacle_models.py`, its four generated terrain OBJ files, and `BRGIRON.png`
are original Project Broom assets dedicated under CC0-1.0. No imported art is used.
The skeletal monkey restraints retain the monkey asset CC-BY-SA-4.0 license.

## Bloodwort

`tools/bloodwort_models.py`, `bloodwort_*.obj`, and BRGBWST, BRGBWPD,
BRGBWSH, BRGBWSP textures are original procedural Project Broom work,
dedicated under CC0-1.0. No imported artwork or reference geometry is used.
