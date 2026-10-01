# Runtime wall-top fade

The compiler's depth-2+ fade was lost during `ReconcileTerrain`: the runtime
clears the two-sided middle texture and selects an ordinary rock upper texture.
The older compiler-only repair therefore did not survive initial reconciliation.

The runtime now selects BRGCVUP, BRGWTUP or BRGMSUP for the corresponding cave,
wet-rock or masonry upper tier on lower floors. `ML_DONTPEGTOP` anchors texture
row zero to the open ceiling; otherwise the default upper-tier bottom pegging
places the fade above the rendered wall. Lower cliff textures remain independent.
Depth 1 keeps its existing ceiling and materials.

This is presentation-only: no bridge ABI, topology, collision, Brogue terrain,
actions, RNG or fall timing changes. The existing original fade images are reused.

## Reproduction and verification

`python -m tools.capture_terrain_overlays --label wall-fall-vulkan --fall --backend 1`
uses seed 1 and submits the established Brogue movement sequence, confirms the
fall, waits for floor 2, looks west/up from the landing, captures, submits WAIT,
then captures again. `--backend 0` repeats on OpenGL.

`--walls` instead exercises a synthetic copied depth-2 presentation and dirties
every appearance for a second full reconciliation. It checks that Brogue's hash
and turn remain unchanged. This fixture is not evidence of a gameplay descent.

The native Release build and 60 resource/map-compiler tests passed. Runtime
captures live under `artifacts/terrain-overlays/wall-fall-*`. The local engine is
rebuilt; no release ZIP or online download is updated by this repair.
