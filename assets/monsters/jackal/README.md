# Jackal — MK_JACKAL / BrogueMonsterK03

Original Project Broom canine, following Brogue's powerful-jaw description,
brown catalog identity and bite/maul attack prose. Lean proportions, pointed
ears, a darker back, amber eyes and pale paws are artistic interpretation.

- `jackal-animated.blend`: 25-bone rig, weights, six Actions and packed diffuse.
- `animation.json`: deterministic runtime hash, hierarchy, bounds and clip data.
- Runtime: `models/monsters/03_jackal.iqm`, skin `graphics/BRGJACK.png`.
- Rebuild: `python -m tools.monster_models.jackal_animation`, then regenerate
  roster bindings and the bestiary. The canonical build includes registration.
- Blender: `--background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_JACKAL`.
- [Shared workflow](../../../docs/skeletal-enemy-workflow.md).

The static `03_jackal.obj`, `sources/03_jackal.blend` and `BRGM03.png` remain the
reference. Python anatomy and clip definitions are the reproducible master;
reconcile manual Blender edits before regenerating. Brogue retains all gameplay.

Original mesh, texture, rig and animations by Project Broom contributors with
Codex-assisted procedural modeling and Blender, under
[CC-BY-SA-4.0](../../../ASSETS-LICENSE.md). No external artwork was imported.
Brogue prose and catalog data retain their upstream notices. User art approval
remains pending. See [implementation and evidence](../../../docs/jackal-animation.md).

Connected body cage: `connected-skin.json.gz`, rebuilt with the shared Blender
`blender_skin.py` authoring step. It has the same original Project Broom
CC-BY-SA-4.0 provenance as this model. See
[anatomy repair](../../../docs/enemy-anatomy-repair.md) for connectivity, scale
and runtime verification.
