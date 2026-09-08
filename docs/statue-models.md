# Statue presentation

Original presentation assets, CC0-1.0. Brogue CE remains authoritative.

The pinned `Globals.c` describes ordinary statues as weathered marble, cracking
statues with deep spreading cracks, broken doorway statues as crumbled beyond
recognition, and demonic statues as leering obsidian figures. The robed figure,
folded hands, hood, plinth and proportions are original artistic interpretation.

`tools/statue_models.py`, invoked by `tools/terrain_assets.py`, generates four
OBJ forms and four shaded stone texture atlases. The intact figure is about
71 units tall on a 36-unit-wide base; the horned obsidian form reaches 81 units.
All parts meet or intersect as solid sculptural masses. End caps are explicitly
triangulated because UZDoom's OBJ loader supports triangles and quads only.
The OBJ files can be imported into Blender; procedural source remains canonical.

`terrain_presentation.json` maps inert, dormant, instant-crack and dormant
doorway states to the identical marble model. Cracking and broken states have
separate forms; the obsidian form is only selected for `DEMONIC_STATUE`.
The existing copied-appearance rules control knowledge and visibility. No raw
hidden terrain is consulted by the models. Actors are noninteractive and use
existing reconciler ownership; Brogue continues to decide movement obstruction.

Visible statue replacements shed short existing stone fragments at Enhanced
and Cinematic settings. Basic settles immediately. A replaced statue is removed
instead of following the outgoing-door animation. Initial attachment, remembered
terrain and duplicate snapshots retain existing settle/retarget rules.

## Verification

- Canonical source engine and launcher build passed.
- 39 resource, terrain-geometry and animation tests passed, including identical
  regeneration, face validity, renderer-compatible polygons, dimensions and
  identical dormant/inert bindings.
- `python -m tools.test_terrain_renderer --backend 1 --statues --quality 1 --run-label final`
  and the same command with backend 0 passed. Before/during/after captures of
  intact, dormant, cracking, broken, cleared floor and obsidian forms are under
  `artifacts/statues/{vulkan,opengl}/1/final/`.
- Basic and Cinematic Vulkan runs also passed (`--quality 0` / `--quality 2`),
  with immediate Basic settling and bounded Enhanced/Cinematic fragments.
- Renderer probes verify correct proxy replacement, no obsolete outgoing actor,
  no fragments surviving their transition, duplicate-snapshot stability and
  unchanged native Brogue turn 0/hash `c92268ff6250781b`.

These are synthetic copied-appearance renderer fixtures, not natural statue
activation or gameplay-parity recordings. An attempted natural first-floor route
required a Brogue confirmation, so that route did not produce a completed natural
capture. Full release ZIP assembly and standalone side-by-side play were not run.
Recorded frame timings include screenshot overhead and are not a controlled
before/after performance benchmark. No dynamic-terrain backlog gates are newly
checked off by this asset change.
