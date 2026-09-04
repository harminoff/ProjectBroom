# Project Broom semantic prop sprites

These transparent PNGs were generated with the built-in OpenAI image-generation
tool for the Project Broom presentation layer. They are original project assets,
not extracted from CC4. GZDoom virtual sprite definitions and offsets live in
`../TEXTURES.txt`.

Generation prompts, normalized for the three committed assets:

- `BRGGRASS.png`: low-resolution hand-painted Doom-style subterranean grass
  tuft; olive and moss-green blades, brown roots, compact irregular grounded
  silhouette, transparent background, no floor, shadow, cutoff edge, or vines.
- `BRGFUNG.png`: low-resolution hand-painted Doom-style cave mushroom cluster;
  gray-brown caps, muted teal undersides, varied short heights, compact grounded
  silhouette, transparent background, no floor, shadow, or cutoff edge.
- `BRGFOLIA.png`: low-resolution hand-painted Doom-style subterranean broad-leaf
  and fern mound; desaturated greens and brown stems, uneven grounded silhouette,
  transparent background, no floor, shadow, tree, vines, or cutoff edge.
- `BRGVEG0.png`: seamless top-down cave-floor tile; damp earth and weathered
  stone with fine moss and roots, uniform detail density, diffuse lighting,
  no perspective, large objects, border, vignette, or obvious grid.
- `BRGROCK.png`: seamless charcoal-and-slate natural cave wall and ceiling.
- `BRGDIRT.png`: seamless top-down compacted cave earth and small pebbles.
- `BRGSTONE.png`: seamless weathered basalt masonry for worked structures.
- `BRGBRIDGE.png`: seamless weathered timber-and-iron deck for Brogue bridge cells.
- `BRGWATER.png`: seamless midnight-blue underground water, warped at runtime.
- `BRGLAVA.png`: seamless dark basalt crust and molten orange fissures, warped
- `BRGLAVA_BM.png`: deterministic emissive mask derived from `BRGLAVA.png`; only
  the molten fissures contribute to the GZDoom brightmap
  at runtime.

Generated on 2026-09-02 using the built-in image-generation mode. The original
1536x1024 RGBA outputs are preserved so the engine can downscale them cleanly.
