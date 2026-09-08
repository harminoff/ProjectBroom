# Water-to-floor transition research

Research date: September 8, 2026. Scope: presentation-only recommendations.
This pass reviewed the supplied screenshot, current Project Broom source,
the pinned UZDoom source, and primary graphics references. No rendering or
gameplay code was changed, and no proposed effect has been runtime-tested.

**Recommendation**

Use a narrow, irregular shoreline transition combining a damp land border,
partially transparent water near the bank, and restrained contact ripples.
Build its placement from Brogue's copied, knowledge-safe terrain appearance.
Use the existing separate liquid surface and stable cell geometry.

The intended visual progression is:

    existing dry material -> damp material -> visible submerged bank -> open water

The width, tint and edge shape should depend on the adjoining material. A
dirt shore should look different from water against flagstones or a wooden
bridge. Bright foam around every boundary would be a poor default for the
quiet, dark cave shown in the screenshot.

**What the screenshot and current source establish**

The screenshot shows straight edges and a pointed ground corner surrounded
by water. The blue water pattern ends immediately against brown ground, with
no visible band connecting their colors or surface qualities. Its strong
highlights continue up to the edge. These observations explain why the ground
reads like a cutout laid over water. The screenshot alone does not identify
the seed, cell coordinates, water class or executable version.

The current development source is consistent with that appearance:

- [ApplyTerrainCell](../src/gzdoom-bridge/brogue_terrain_frontend.inc) puts
  ordinary water at Z=0. Dry ground also normally sits at Z=0. Shallow/deep
  water beds are recessed to -8/-24. Flood surfaces instead rise to 8/24.
- [PrepareTerrainAnimation and TerrainAnimatedPlane](../src/gzdoom-bridge/brogue_terrain_animation.inc)
  target liquid alpha 1 when water exists. Alpha changes over time during a
  terrain transition; there is no spatial fade toward a shore here. The
  settled surface therefore conceals the bed.
- [The terrain registry](../assets/terrain/terrain_presentation.json) selects
  BRGWATR for shallow and deep water. [ANIMDEFS](../mod/BrogueDoom/ANIMDEFS)
  gives it texture warp, which supplies motion but no neighboring-floor mask.
- [The compiler](../tools/mapcompiler/compile.py) uses 64-unit cells and
  preserves normal traversable-to-traversable portal edges on the grid.
  Existing solid-wall recesses and chasm lips do not provide general shores.
- [The animation notes](terrain-animation-research.md) explicitly leave
  continuous shoreline meshes and waterfall transition detail unimplemented.

The first useful fix is therefore spatial treatment of the boundary. Making
the whole water surface more transparent would expose the bed everywhere but
would not by itself resolve the hard perimeter or provide material variation.

**Techniques worth using**

| Technique | Contribution | Fit for this scene |
| --- | --- | --- |
| Damp ground band | Changes the dry material gradually before it meets water | High priority; keep the original soil/stone detail visible |
| Shore-distance opacity and color mask | Reveals the submerged edge, then blends into deeper-looking water | High priority; a controlled fit for the existing grid and liquid planes |
| Joined edge/corner strips | Breaks the ruler-straight appearance and joins inside/outside corners | High priority; cosmetic geometry or masked surfaces only |
| Small contact ripples or sparse foam | Adds motion where water touches a bank | Secondary; subdued gray-blue highlights, with foam concentrated at turbulent contacts |
| Screen-depth intersection fade | Automatically softens intersections with rendered scene geometry | Useful later; needs verified scene-depth plumbing in this engine |
| Sloped cosmetic bank skirt | Makes a softened surface look supported from a low viewing angle | Add only if the first prototype exposes an obvious vertical ledge |
| Refraction, large waves, screen-space reflections | Improves broader water appearance | Lower priority for this specific seam |

NVIDIA's water-rendering chapter uses depth to vary opacity, reflection and
wave amplitude near shore. It also describes supplying depth as authored
vertex data, demonstrating that shoreline appearance does not inherently
require screen-space depth. The transferable idea here is a controlled edge
profile; Brogue's categorical water state is not a physical depth simulation.
[GPU Gems, Chapter 1](https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-1-effective-water-simulation-physical-models)

Sébastien Lagarde identifies darker diffuse appearance, stronger specular
response and subtle color changes as cues for wet surfaces. For this already
dark scene, use mild darkening and retained texture detail; the result needs
to remain readable under the game's existing lighting.
[Water drop 3a](https://seblagarde.wordpress.com/2013/03/19/water-drop-3a-physically-based-wet-surfaces/)

Alex Tardif demonstrates a short-distance alpha fade at water/geometry
intersections, then uses that contact information for foam broken up by
noise. He cautions that broad depth fades produce implausible fading around
more distant geometry. Apply the narrow-contact principle here; his full
water pipeline is not a drop-in UZDoom implementation.
[Water Walkthrough](https://alextardif.com/Water.html)

NVIDIA's Tabula Rasa chapter describes automatic shoreline transparency from
comparing the water fragment's depth with a previously rendered depth buffer.
This supports the technique, but does not establish its availability in
Project Broom's material interface.
[GPU Gems 3, Chapter 19, section 19.5.1](https://developer.nvidia.com/gpugems/gpugems3/part-iii-rendering/chapter-19-deferred-shading-tabula-rasa)

**How the transition should vary**

| Adjacent surface | Suggested appearance |
| --- | --- |
| Earth/mud | Uneven darkened soil, a brown-green submerged fringe, low-contrast ripples |
| Natural rock | Narrow damp rock band, broken stone silhouette, localized contact highlights |
| Moss/vegetated ground | Preserve the existing green material through the wet fringe; avoid an opaque blue outline |
| Flagstone/masonry | Preserve the constructed edge; vary wetness along stone joints and use a tighter contact line |
| Wooden bridge | Damp edge and subtle contact at the correct water height; no earthen beach border |
| Shallow-to-deep water | Gradual tint/opacity change within water, with the gameplay distinction still legible |
| Waterfall/chasm | Separate falling-water and cliff treatment; do not apply the ordinary horizontal shore profile |

Starting art parameters, to be judged in captures rather than treated as
measured physical values: approximately 4-6 units of damp ground, 6-12 units
of water-side transition, and 1-3 units of small-scale edge variation, within
the existing 64-unit cell size. Reduce widths on narrow passages and isolated
cells. Keep water apparent at every water-cell center, particularly deep water.
Use stable spatial variation; animate the ripples rather than making the
entire shoreline crawl.

**A practical Project Broom implementation path**

1. Classify eligible interfaces from copied appearance, material family,
   liquid/deck height and knowledge state. A wet neighbor alone is insufficient:
   raised floodwater, a wall, a bridge, and an ordinary ground-level bank have
   different contacts. Unknown terrain must not supply shore shapes or materials.
2. Select shared straight, convex-corner and concave-corner masks for the water
   surface. Use those masks for alpha, tint and attenuation of the current
   high-contrast water pattern. Confirm the bed and bank are actually rendered
   underneath wherever alpha decreases.
3. Add joined cosmetic land-edge strips using the adjacent ground material,
   with stable texture coordinates and a dampened appearance. Use a small
   world-space offset where necessary to avoid coplanar flicker. Do not stack
   independent translucent strips at corners: joined coverage should prevent
   dark double blends, cracks and overlapping foam.
4. Add a thin contact-ripple layer after the static transition reads correctly.
   If low-angle views expose an artificial ledge, test a small render-only
   tapered bank skirt. Preserve sector geometry and entity support heights.
5. Recompute the affected shoreline neighborhood when complete snapshots
   change. Keep initial attachment, memory, flooding, freezing, melting,
   save/load and depth-return behavior in the same ownership lifecycle.

A mask-based prototype is preferable to a depth-buffer dependency here because
the map already supplies explicit boundaries and uses stepped beds. Screen
depth alone does not guarantee a broad horizontal shore gradient where an
otherwise flat bed meets a vertical step. A surface-space distance mask gives
direct control over that width. This is an engineering recommendation based
on the inspected geometry, not a measured comparison between prototypes.

Use the existing water plane as the water-side owner. An extra translucent
foam/rim sprite drawn over the unchanged opaque water cannot reveal the bed:
the underlying water material must also participate in the transition.

**Engine feasibility and remaining uncertainties**

Context7 resolved UZDoom to `/zdoom/gzdoom`, but did not provide sufficient
documentation for the depth-input question. The checked-out UZDoom 5.0.0
source, pinned at `292cf4203ebd3ced951cb67f6819180f588c1d44`, was therefore
used to check implementation capabilities.

- [Pinned GLDEFS parser](https://github.com/UZDoom/UZDoom/blob/292cf4203ebd3ced951cb67f6819180f588c1d44/src/r_data/gldefs.cpp)
  accepts custom material shaders, additional textures and `disablealphatest`.
  The latter marks a texture translucent. This is useful groundwork, not proof
  that the entire 3D-floor blending/occlusion path needs no adjustment.
- [Current floor reveal shader](../mod/BrogueDoom/shaders/search-floor-reveal.fp)
  already uses world position and spatially varying alpha. It provides a local
  example of the shader interface, though its reveal behavior is distinct
  from a persistent water shoreline.
- The liquid animation code controls 3D-floor alpha and `FF_TRANSLUCENT`, then
  recalculates attached floors. Persistent masked shores must account for that
  code clearing the flag at full plane alpha. Verify both per-pixel blending
  and underlying bed visibility at the settled endpoint.
- The inspected default material path did not establish a ready-to-use scene
  depth input. Internal depth textures exist in postprocessing; their existence
  is not proof that a water material can sample them. Treat a depth-fade solution
  as a separate renderer feasibility task.
- [Material documentation](https://zdoom.org/w/index.php?title=GLDEFS) cautions
  about combining custom materials and legacy warp. A shoreline shader must
  deliberately preserve or reproduce water motion, not assume that simply
  adding GLDEFS will compose with BRGWATR's existing ANIMDEFS warp.
- [TerrainReconciler](../src/gzdoom-bridge/terrain_reconciler.h) currently marks
  changed cells and cardinal neighbors. If corner masks depend on diagonals,
  shoreline invalidation must include those dependencies as well.

A small shared mask set and material selection should be investigated before
adding runtime texture uploads or global shader infrastructure. Exact mask
binding and translucency behavior remain prototype questions. No bridge ABI
extension appears necessary for this proposal because the current copied
appearance already carries the relevant categories and knowledge.

**Acceptance for a later implementation**

The first visual comparison should reproduce the supplied viewpoint if its
save or seed becomes available, plus a fixed-seed island, inside corner,
outside corner, narrow channel, and each material pairing above. Capture at
normal eye level, grazing angles and top down on OpenGL and Vulkan. Confirm
that the land stays readable and no texture seams, shimmer, depth gaps,
transparent sorting errors or doubled corner bands appear.

Exercise flood/recede, freeze/melt, bridge overlap, visibility loss, restored
games and depth revisits. Static wet edges should remain at Basic quality;
ripples can scale with effects quality. Compare fixed-scene frame times with
identical settings, measuring separately from screenshot capture overhead.

Run resource and relevant terrain/compiler regressions, deterministically
regenerate any new masks/assets, and verify that cosmetic updates leave
Brogue state, turns, RNG and movement results unchanged. Build, package,
launch and runtime captures are separate acceptance gates. If compiler output
changes, preserve topology/semantic fields and invalidate cached maps correctly.

This research pass performed none of those implementation acceptance gates.
It added only this report. No third-party textures or example code were imported.
