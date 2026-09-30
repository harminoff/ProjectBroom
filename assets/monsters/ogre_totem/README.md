# Ogre totem source

Original Project Broom BRG-M20 mesh, diffuse and animation artwork, licensed
CC-BY-SA-4.0. No third-party artwork was imported. Upstream Brogue text keeps
its existing license and notices.

`ogre-totem-animated.blend` contains eight bones, 105 named assembled mesh parts,
six Actions and the packed 1024-square diffuse. Python is the deterministic
master: `tools.monster_models.ogre_totem_animation` and `ogre_totem_materials`.
The shared Blender exporter rebuilds the editable source in an isolated process.

Fixed masonry and buried stumps support three heavy uprights and a bone crown.
The greenstone tablet and scored tallies have modeled bronze rings and staples;
the tablet ring meets a crown suspension pin through all live poses. The unused
move role is rest. The broken crown falls into a low heap on death while the
footing remains fixed. No organic cage is needed for these rigid assembled
members. All bone scales are one.

Healing, slowing, health, visibility, damage, death and all turn decisions remain
entirely Brogue-owned. The asset emits no light, particles or independent effect.
See [the report](../../../docs/ogre-totem-animation.md) for technical proof and
the unresolved natural encounter and user art approval gates.
