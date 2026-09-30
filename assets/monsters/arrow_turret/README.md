# Arrow turret source

Original Project Broom BRG-M15 geometry, 1024-square diffuse and six animations,
licensed CC-BY-SA-4.0. No third-party art imported. Brogue text retains its
upstream licensing. Python definitions are the deterministic master.

Rebuild runtime: `python -m tools.monster_models.arrow_turret_animation`.
Rebuild editable source with the shared background `blender_skeletal.py` exporter.
The saved `arrow-turret-animated.blend` contains 103 named meshes, eight bones,
six Actions and its packed texture. No linked dependencies are required.

The plate, anchors, magazine and support remain fixed; the unused move and idle
roles rest. Bow limbs, weighted string, sled, drums and sear move cosmetically.
Brogue alone fires arrows and decides targets, visibility, damage and turns.
See [verification and wall projection](../../../docs/arrow-turret-animation.md).
