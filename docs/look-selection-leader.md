# Look selection leader

Look mode (L) connects its detail panel to the selected Brogue cell with a
gold line, black outline, and hollow diamond. Tab and wheel cycling reuse the
existing Look selection handler. The panel docks on the opposite side of the
screen to keep the selected location easier to see. Targets outside the view
receive an edge endpoint labelled OFF-SCREEN. The line is hidden on the full
map and disappears when Look closes.

The line and diamond render in a dedicated 2D drawer at the end of the world
pass, before the first-person weapon models. Hands and weapons therefore
occlude the leader using their actual silhouettes. The detail panel and
off-screen text remain in the final HUD pass. The hook is in the pinned
UZDoom patch's `HWDrawInfo::EndDrawScene`; it does not run for camera textures.
The viewport, viewpoint binding, and depth state are restored before weapons.

This is presentation-only: projection reads the copied cursor coordinates
and the rendered camera, including field of view, pitch, and pixel stretch.
It does not search hidden entities, change selection eligibility, consume
turns, or modify Brogue simulation or RNG. The endpoint identifies a cell
just above its floor, rather than tracing a particular mesh's outline.

For repeatable engine captures, `brg_look` and `brg_look_next` dispatch through
the same handlers as L and Tab. Seed 1 captures under
`artifacts/look-leader/` exercise gold selection, sword selection outside the
view, and closing Look on Vulkan and OpenGL; the displayed turn remains zero.
The native Release build and `python -m unittest tools.test_broguedoom_resources`
pass. These are engine-driven captures, not physical keyboard acceptance or
a standalone Brogue comparison. No release ZIP or online upload is included.

Weapon-occlusion follow-up: seed 1 Vulkan/OpenGL captures in
`artifacts/look-leader/behind/` show the gold leader interrupted by the dagger,
with selection cycling and close captures retained. The Release build,
pinned patch validation, and 38 resource/engine-source tests pass. The local
runtime is refreshed; no new distribution archive is created.
