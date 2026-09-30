# Goblin mystic

Original Project Broom mesh, texture and six cosmetic animation clips,
CC-BY-SA-4.0. The connected primate anatomy and material tooling reuse the
Project Broom goblin family. No third-party art or external linked resources.

Source facts: unarmed, golden eyes, shielding magic. The faded blue wrap,
warm grey-brown coloration and palm gestures are artistic interpretation.
Existing Brogue events own outcomes; gestures do not assert a shielding cast.

Rebuild runtime: `python -m tools.monster_models.goblin_mystic_animation`.
Rebuild the cage in isolated Blender 5.2 with `--threads 1 --python
tools/monster_models/blender_skin.py -- goblin_mystic`; then export editable
source with `--python tools/monster_models/blender_skeletal.py -- MK_GOBLIN_MYSTIC`.

See [implementation and acceptance](../../../docs/goblin-mystic-animation.md).
