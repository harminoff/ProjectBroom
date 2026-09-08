# Kobold — MK_KOBOLD / BrogueMonsterK02

Original Project Broom lizardlike humanoid with a club, following pinned Brogue
prose and attack verbs. The anatomy, 24-bone rig, weights and six clips are
presentation choices. Brogue retains all combat, movement, damage and timing.

- `kobold-animated.blend`: editable armature, weighted meshes, packed dedicated
  reptilian diffuse texture and named Actions; independently checked against IQM poses.
- `animation.json`: deterministic runtime hash, hierarchy, bounds and clip data.
- Runtime: `mod/BrogueDoom/models/monsters/02_kobold.iqm`.
- Rebuild: `python -m tools.monster_models.skeletal_registry --build`.
- [Shared enemy workflow](../../../docs/skeletal-enemy-workflow.md).

The original `sources/02_kobold.blend`, static OBJ and `BRGM02.png` are preserved.
The active skin is `BRGKOB.png`; see [skin and verification](../../../docs/kobold-skin.md).
Python anatomy/clip definitions are the reproducible master; manual Blender edits
must be reconciled with those definitions before regeneration.

Mesh, rig and animation authored by Project Broom contributors with Codex-assisted
procedural modeling and Blender, under [CC-BY-SA-4.0](../../../ASSETS-LICENSE.md).
No external artwork was imported. The dedicated reptilian atlas has the same provenance and license. Blender is an authoring tool, not an artwork source. Brogue prose
retains its upstream notices. Final user art approval remains pending.

Connected body cage: `connected-skin.json.gz`, rebuilt with the shared Blender
`blender_skin.py` authoring step. It has the same original Project Broom
CC-BY-SA-4.0 provenance as this model. See
[anatomy repair](../../../docs/enemy-anatomy-repair.md) for connectivity, scale
and runtime verification.
