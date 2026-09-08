# Camera-visible enemy movement

Presentation-only update, 2026-09-06. Brogue CE still resolves each intent and
returns authoritative positions before any presentation runs. No bridge ABI,
monster AI, collision, damage, RNG or simulation timing changed.

## Behavior

All enemy proxies share visible tile travel. Rat, kobold, jackal and monkey use
their existing registered skeletal walk clips. Static enemies receive the same
position interpolation; this change does not create skeletal rigs for the rest
of the roster. Rat retains two scurry cycles per tile; other rigs use one cycle.

An ordinary step animates only when the creature was and remains directly visible
in Brogue and either end of the step intersects the camera view. The projection
uses camera yaw, pitch, FOV and aspect, with conservative body bounds to include
partially visible creatures at screen edges. Brogue visibility supplies the
knowledge/line-of-sight restriction; this is not a renderer pixel-occlusion query.
Newly observed creatures, sensed-only creatures, unknown creatures and teleports
settle immediately. Turning away during travel snaps to the latest Brogue target
and clears the remaining movement hold. Off-camera pulse/death holds also clear.
Idle and cosmetic action/death tails do not become new input gates.

Default travel is 28 engine tics per cardinal tile (about 0.8 seconds), and 40 for
a diagonal. `brg_enemy_walk_tics` controls the shared setting, clamped to 5–70;
`brg_rat_walk_tics` retains the existing rat preference. The historical
`brg_monster_anim_tics` CVar remains accepted but no longer selects enemy travel.

A small gold circle fills clockwise at the top center while the existing enemy
movement/pulse/death input hold is active. It uses those same remaining timers,
including the longest concurrent hold, and disappears when movement input is
available. No new wait timer was added. Camera movement remains responsive, and
the existing one-command movement buffer remains intact. Cosmetic clips can
continue after the circle disappears because those clips do not hold input.

## Implementation

- `src/gzdoom-bridge/enemy_movement.h`: camera-bounds predicate, duration and
  progress math without any simulation access.
- Native frontend: shared movement selection, camera check on each presentation
  tick, immediate off-camera settling and a procedural HUD circle.
- Existing registry, meshes and clips are reused unchanged. No new art or licenses.
- `tools/test_enemy_movement.py` / `enemy_movement_test.cpp`: front/back/vertical
  and edge visibility, cardinal/diagonal/teleport timing, clamping and progress.
- Engine build receipt now includes the new header, including its tamper test.

## Evidence and limits

Evidence lives in `artifacts/enemy-movement/`, outside release content.

- Canonical source build and launcher build passed. The final diagnostic-only
  log addition was incrementally compiled and its build receipt refreshed.
- `scripts/test.ps1`: 159 tests passed. The seed-1 long run ends naturally at
  turn 195, killed by a rat; it is not a completed 300-action survival run.
- Packaged UZDoom Vulkan and OpenGL seed-2 encounters reproduce freeing hash
  `891359fb198ed00f` and next-action hash `aed1b77be1e3f7e6`.
- Runtime logs include visible rat and kobold cardinal travel at 28 tics, monkey
  diagonal travel at 40 tics, and off-camera travel at zero tics.
- A camera-turn fixture cancels monkey travel with six tics remaining; the same
  authoritative result is retained. No scene reload or simulation action is used
  to settle it. The fixture camera is local test content, not a gameplay camera change.
- Existing 48-command kobold/Vulkan and jackal/OpenGL scenarios retain their
  previous final hashes: `69afa7433350e1b6` and `6bfdb2d8cf5d78be`. Those routes
  exercise off-camera movement; the visible travel samples come from seed 2.
- Captures show the top circle during movement and absent after settling. Timing
  captures use a 35-FPS fixture cap for repeatable visual sampling; it is not a
  performance benchmark and does not change the shipped graphics preferences.

No new standalone graphical side-by-side session or frame-time benchmark was
performed for this presentation change. Existing bridge, save, resource and map
regressions passed. The conservative camera bounds are intentional; occlusion
by detailed frontend props is not tested per pixel. Unrigged enemies still need
individual modeling work for anatomical gait animations.
