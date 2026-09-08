# Water shorelines

Presentation-only implementation of [the shoreline research](water-shoreline-research.md).
Water now fades through a narrow, stationary irregular mask at known banks,
revealing the existing recessed bed. Earth, moss, flagstone and timber keep
their original diffuse detail with material-specific wet-edge widths. Small
contact highlights move within the water-side band. No sector geometry,
entity support height, collision, terrain category, turn or Brogue RNG changes.

`shoreline.h` reads only copied terrain appearance. It distinguishes ordinary
ground-level banks, wall contacts, raised floods, bridge decks, ice, holes and
other liquid types. Unknown neighbors cannot supply a bank; remembered water
uses a static material. Eight-neighbor masks normalize to 47 unique distance
shapes, including isolated corners. A changed cell invalidates its complete
3x3 shoreline neighborhood independently of the geometry reconciler.

`tools/shoreline_assets.py` creates eight binary texels for each mask plus
material aliases for the existing textures. The 376 aliases share six shader
programs: masks are additional texture bindings, and the still-water variants
use zero shader speed. The pinned engine deduplicates identical shader/define
combinations and reuses single-patch image sources. No full-resolution diffuse
artwork is regenerated. Original mask/shader provenance is in
[SHORELINE-LICENSE.md](../assets/terrain/SHORELINE-LICENSE.md).

The water shader reproduces the existing wave scale/pace while dimming its
highlights near contact. Shallow and deep water have different core opacity;
water remains apparent at cell centers. Earth/moss/stone/timber wet bands use
6/7/4/3 units respectively, within the unchanged 64-unit cells.

Persistent water materials use at most alpha 254 on their attached 3D floor,
keeping `FF_TRANSLUCENT` and the recessed bed in the correct clipping path.
Per-pixel alpha supplies the actual gradient. This is separate from the
existing flood/recede animation tween, which continues to settle normally.
The same owner lifecycle handles initial attachment, snapshots, quality
changes, freezing, melting and level rebinding. Basic effects retain static
wet borders and water shading; contact motion is disabled.

`brg_shorelines false` restores the original materials for development
comparison; the default is true and the switch is not archived. It does not
change the simulation. No public bridge ABI or compiler geometry version changed.
The new resource files participate in the compiler's resource hash, and native
source receipts now cover the shoreline implementation and fixture.

Verification commands:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-source-bridge.ps1 -SkipTests
python -m unittest tools.test_shoreline
python -m tools.test_shoreline_renderer --backend 0
python -m tools.test_shoreline_renderer --backend 1
python -m tools.test_shoreline_renderer --backend 1 --quality 0
python -m tools.test_shoreline_renderer --backend 0 --benchmark
python -m tools.test_shoreline_renderer --backend 1 --benchmark
```

The explicit developer fixture produces 11 captures: original/updated earth,
a grazing view, moss, flagstone, a wooden deck, ice, melting back to water,
raised flooding, unknown neighbors and remembered water. Flagstone is a
material-only fixture override; the pinned catalog's existing floor aliases
are unchanged. The fixture edits copied presentation state, never Brogue's
map. Its completion checks the native state hash and turn, and rejects solid
or swimmable liquid/deck floors. Unit tests exercise all 256 neighborhood
combinations, distance-preserving normalization, privacy, heights, deck/hole
exceptions, neighborhood invalidation and byte-identical data generation.

Evidence lives under `artifacts/shoreline/`. Capture runs and screenshot-free
timing runs are separate. These are presentation checks, not a claim of
standalone gameplay parity for the synthetic scene. Raised water cliffs and
waterfalls retain their separate existing presentation; the horizontal wet
band is not painted onto a floor below a raised water surface. Sector-grid
silhouettes remain unchanged: irregularity comes from the material transition,
not a new sloping bank mesh or a terrain/topology rewrite.
