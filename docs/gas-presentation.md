# Soft gas presentation

Gas previously used three faceted, diamond-shaped volumes with nonzero alpha
at every texture edge, exposing straight boundaries even at low density.

The replacement uses nine overlapping cloud cards with smooth, irregular
alpha that reaches zero at every edge. The existing `Stencil` property
(mapped by the pinned engine to `STYLE_TranslucentStencil`) preserves the
copied Brogue gas color while honoring density and dissipation. The cards
face several directions so they remain visible from above and at eye level.
Per-cell orientation and bounded sinusoidal drift break up repetition without
using randomness. Basic quality retains the soft clouds with motion disabled.
Healing gas retains its dedicated specks inside the same feathered cloud form.

This is presentation-only. The existing knowledge-safe snapshot determines
gas identity, volume, color, creation, replacement, and removal. No Brogue
rules, RNG, bridge ABI, collision, or map geometry are changed. All cloud
vertices remain within their cell even at maximum scale and drift. The
existing short density tween is preserved, and visibility loss removes gas.

Original procedural assets in `tools/gas_assets.py` are dedicated under
CC0-1.0, as are the existing generated terrain assets. No external textures
were imported.

Validation commands:

```powershell
python -m unittest tools.test_gas_assets tools.test_bloodwort tools.test_terrain_animation tools.test_broguedoom_resources
python -m tools.test_terrain_renderer --animations --backend 0 --run-label gas-after
python -m tools.test_terrain_renderer --animations --backend 1 --run-label gas-after
python -m tools.test_terrain_renderer --bloodwort --backend 1 --run-label gas-after
```

The renderer fixtures change only copied frontend state and verify the native
state hash is unchanged. They are visual and lifecycle checks, not independent
standalone gameplay parity proof. Local results are recorded under
`artifacts/gas/` and the labeled terrain/bloodwort capture directories.
