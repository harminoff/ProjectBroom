# Jackal skeletal presentation

The jackal now uses the shared skeletal pipeline: 25 bones, 5,102 vertices,
9,368 triangles and six clips (idle, prowl, bite, maul, recoil and death).
Brogue's powerful-jaw description, brown catalog color and bite/maul prose are
the source constraints. Lean canine anatomy, pointed ears, a darker back,
short fur strokes, pale paws and amber eyes are artistic interpretations.
No Brogue monster properties, turn processing or RNG behavior changed.

The new anatomy module and dedicated skin use the existing rig math, skinning,
IQM writer, native clip registry and Blender exporter. Registering `MK_JACKAL`
adds its generated native table row and MODELDEF/ZScript binding; no hand-written
jackal-specific C++ or gameplay code was added. The original OBJ, PNG and static
Blender source remain available. See [shared authoring](skeletal-enemy-workflow.md)
and [source and licensing](../assets/monsters/jackal/README.md).

The jaw carries its lower teeth and mouth, ears have independent joints, feet
use two-joint pose solves and the tail has five joints. A death clip retains only
a non-interacting visual proxy. Existing generic movement interpolation and
input timing remain unchanged. Rapid returned actions can retarget clips;
animations never queue new gameplay outcomes.

## Verification

- `scripts/build-source-bridge.ps1 -SkipTests` completes native compilation,
  engine copy/build manifest and self-contained launcher packaging.
- `scripts/test.ps1` passes all 149 tests. Its requested 300-action seed-one
  endurance attempt ends naturally at turn 195, killed by a rat; this is not a
  completed 300-action survival run. Final hash: `36b2a00b6543c40a`.
- The final fur-only refinement passes the three focused jackal tests again.
  Shared skeletal tests check binary regeneration, bounds, weights and clips;
  jackal-specific checks cover jaw/ear ownership, grounded gait and death pose.
- Blender 5.2.1 creates and reopens the editable file, checks its packed texture,
  25 bones and six Actions, and compares sampled deformed vertices against the
  shared solver. Python definitions remain the reproducible master.
- A local fixture chooses routes from copied snapshots and submits only normal
  bridge movement actions. Seeds 1, 2, 12345 and 99999 reach and kill a jackal in
  48, 30, 36 and 16 actions respectively. Seed 42 has no initial jackal. Repeating
  every fixture produces identical output. This read-only route planning is test
  tooling, not a new in-game auto-navigation feature.

Local logs, route lists, package hashes and captures are in
`artifacts/jackal-animation/`. The renderer gallery is in
`artifacts/skeletal-review/MK_JACKAL/`. Runtime captures demonstrate presentation;
headless action comparisons separately check the authoritative outcomes.

## Scope and limits

This is original Project Broom art under CC-BY-SA-4.0, without imported images,
meshes or game assets. Fur is a diffuse texture, not simulated hair. No new
shader or extra lighting pass was added. User art approval, dense-pack stress
coverage, an installer distribution, an interactive restored-run walkthrough
and standalone side-by-side visual captures remain separate from this pass.

Final renderer evidence: Vulkan and OpenGL each capture 19 gallery views and
55 normal seed-one dungeon frames. All 48 native results match repeated headless
Brogue results for acceptance, turns, coordinates and hashes. Native revisions
have the expected +1 session-attachment offset. Both backends end at normalized
hash `6bfdb2d8cf5d78be`. Real events exercise bite, maul, recoil and death; the
complete prowl cycle is independently checked in the gallery. Gallery views
sample clips rather than constitute real-time video.

The packaged mod is generated twice with identical bytes and is loaded by the
captured OpenGL run. Package SHA-256: `7cbae5f53e2e505114e7960bc4e87db7b80b7ea055a755220daeab4a5b7b81dc`.
Rat and kobold model/skin hashes match the incoming baseline.

## Fixed-scene timing

Vulkan, one actor, identical ART01 camera, vsync off, Basic / Enhanced /
Cinematic in that order. Engine `All` measures its reported renderer work, not
total frame interval. The near-1000 FPS ceiling and sample noise prevent a
meaningful speedup claim; this is not dense-pack or OpenGL timing coverage.

| Model | FPS (B/E/C) | Engine All ms (B/E/C) |
|---|---|---|
| before | 984 / 985 / 985 | 0.436 / 0.345 / 0.338 |
| after | 985 / 982 / 988 | 0.371 / 0.334 / 0.347 |
