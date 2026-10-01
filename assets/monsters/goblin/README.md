# Goblin — BRG-M08

Original Project Broom cave-dwelling primate humanoid, stone spear, diffuse texture and six
skeletal clips, CC-BY-SA-4.0. Created through Blender MCP with a connected skin
cage, 19 bones and hand-parented spear. No third-party artwork imported.

Redesigned with continuous angular facial anatomy, recessed slanted eyes, swept
ears, sparse hair, dirty brown skin and a plain ragged waist wrap. The longer
stone spear has modeled cord bindings. Nine deterministic diffuse regions are
authored in `tools/monster_models/goblin_materials.py`. Ear shape and clothing
are art choices, not claims about Brogue lore; see the design research report.

`goblin-animated.blend` is editable with packed skin and six Actions.
`connected-skin.json.gz` is the deterministic connected-body bake.

The latest pass used Higgsfield's local background Blender integration for
facial/chest shaping, skin refinement and folded wrap details. The existing rig,
clips and spear attachment remain intact. See the
[Higgsfield refinement report](../../../docs/goblin-higgsfield-refinement.md)
for actual tool use, captures, hashes and verification limits.

Rebuild with `python -m tools.monster_models.goblin_animation`. After changing
body blockout or weights, run isolated Blender `blender_skin.py -- goblin`
before rebuilding. Use `blender_skeletal.py -- MK_GOBLIN --render` to rebuild
the editable source and sampled pose evidence. Reconcile manual Blender edits
with the procedural master first.

See [verification and remaining acceptance](../../../docs/goblin-animation.md).
