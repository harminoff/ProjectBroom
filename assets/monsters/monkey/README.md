# Monkey — MK_MONKEY / BrogueMonsterK05

Original reddish-brown monkey with a bare face, long arms, fingers, rounded ears,
short legs and a curling tail. Brogue describes a mischievous thief of shiny
trinkets; its catalog color is reddish brown. Species and roughly 33-unit standing
height are presentation choices, not a measurement specified by Brogue.

- `monkey-animated.blend`: connected body, 23-bone rig, eight Actions, packed skin.
- `monkey-animated-captive.blend`: the same body and rig with wrist ropes.
- `connected-skin.json.gz`: deterministic closed skin cage and transferred weights.
- `animation.json`: both IQM hashes, bounds, bones and clip metadata.
- Runtime models: `05_monkey.iqm`, `05_monkey_captive.iqm`.
- Original skin: `graphics/BRGMONKY.png`.

Clips: idle, walk, bite, snatch, recoil, death, captive and released. The captive
loop hunches forward with the wrists bound. Release removes the iron cuff and chain model and
stands up over 21 engine tics. A new authoritative movement can interrupt it.
Initial attachment and unseen releases settle without replaying that transition.
Cages belong to terrain; open-floor captives do not receive an invented cage.

Rebuild with `python -m tools.monster_models.monkey_animation`, then
`python -m tools.monster_models.generate`. Blender authoring uses
`tools/monster_models/blender_skeletal.py -- MK_MONKEY` and adds `--captive` for
the second source. See the [shared workflow](../../../docs/skeletal-enemy-workflow.md).
Python anatomy and clip definitions plus the baked cage are the reproducible master;
reconcile manual Blender edits before regeneration. Static OBJ/source and BRGM05
remain reference assets.

Original mesh, skin, rig, iron restraints and animations by Project Broom contributors with
Codex-assisted procedural modeling and Blender, under
[CC-BY-SA-4.0](../../../ASSETS-LICENSE.md). No external artwork was imported.
Brogue text retains upstream notices. User art approval remains pending.
See [implementation evidence](../../../docs/monkey-animation.md).
